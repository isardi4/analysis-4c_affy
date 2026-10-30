"""Auditable goldfish for the bridge-count decision, not a full Magic AI.

Only the 41 fixed spells and WUBR artifact lands in reference_deck are supported.
All costs have at most one colored pip; Boulder filters a land's one mana.
The common deterministic pilot never inspects unrevealed library cards.
"""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from itertools import combinations
from math import comb, sqrt
from pathlib import Path
import argparse
import csv
import hashlib
import json
import random
import time

ROOT = Path(__file__).resolve().parents[1]
BRIDGE_COUNTS = tuple(json.loads((ROOT/'configs/structural_stages.json').read_text())['part_2']['bridge_counts'])
COLORS = 'WUBR'
LANDS = {
    'Razortide Bridge': 'WU', 'Mistvault Bridge': 'UB',
    'Drossforge Bridge': 'BR', 'Rustvale Bridge': 'WR',
    'Goldmire Bridge': 'WB', 'Silverbluff Bridge': 'UR',
    'Ancient Den': 'W', 'Seat of the Synod': 'U',
    'Vault of Whispers': 'B', 'Great Furnace': 'R',
    'Darksteel Citadel': '',
}
BRIDGES = tuple(list(LANDS)[:6])
MONOS = tuple(list(LANDS)[6:10])
BOULDER = "Giant's Boulder"
RELIC = 'Cryogen Relic'
FAMILIAR = 'Refurbished Familiar'
MONITOR = 'Utrom Monitor'
ENFORCER = 'Myr Enforcer'
HAWK = 'Glint Hawk'
FOUNTAIN = 'Blood Fountain'
BOMB = 'Nihil Spellbomb'
BARGAIN = "Reckoner's Bargain"
THOUGHT = 'Thoughtcast'
MUNITIONS = 'Makeshift Munitions'
BLAST = 'Galvanic Blast'
DISPATCH = 'Dispatch'
THREATS = {FAMILIAR, MONITOR, ENFORCER}
# generic, colored pip, artifact, creature, affinity
RULES = {
    BOULDER: (1, '', True, False, False),
    RELIC: (1, 'U', True, False, False),
    FAMILIAR: (3, 'B', True, True, True),
    MONITOR: (4, 'U', True, True, True),
    ENFORCER: (7, '', True, True, True),
    HAWK: (0, 'W', False, True, False),
    FOUNTAIN: (0, 'B', True, False, False),
    BOMB: (1, '', True, False, False),
    BARGAIN: (1, 'B', False, False, False),
    THOUGHT: (4, 'U', False, False, True),
    MUNITIONS: (1, 'R', False, False, False),
    BLAST: (0, 'R', False, False, False),
    DISPATCH: (0, 'W', False, False, False),
    'Blood token': (0, '', True, False, False),
}
PROFILES = {'balanced': ('Equilibrado', None), 'blue': ('Azul temprano', 'U'),
            'white': ('Blanco temprano', 'W'), 'black': ('Negro temprano', 'B'),
            'red': ('Rojo temprano', 'R')}
METRICS = ['all4_t2', 'all4_t3', 'all4_t4', 'boulder_t1', 'boulder_t2',
           'boulder_t3', 'relic_t2', 'threat_t3', 'curve3', 'curve4', 'curve5',
           'needed_t1_t3', 'needed_t2_t3', 'color_block_t3', 'screw_t4', 'failed_keep']
METRICS += [f'{c}_t{t}' for t in (1, 2, 3) for c in COLORS]
METRICS += [f'two_mana_{c}_t2' for c in COLORS]


def bounded(total, size):
    if size == 1:
        if 0 <= total <= 4:
            yield (total,)
        return
    for n in range(max(0, total - 4 * (size - 1)), min(4, total) + 1):
        for rest in bounded(total - n, size - 1):
            yield (n,) + rest


def candidates():
    """Exact surrogate search; five profiles per ratio, not full-game optimization.

    Maximize sum w_c P(at least one natural c source among 9 raw cards).
    Weight=3 for the priority color, 1 for others; balanced all 1.
    No Citadels: their indestructibility has no value without interaction.
    """
    hit = [1 - comb(60 - s, 9) / comb(60, 9) for s in range(20)]
    out = []
    for b in BRIDGE_COUNTS:
        best = {}
        untapped = list(bounded(19 - b, 4))
        for bv in bounded(b, 6):
            bs = tuple(sum(n for name, n in zip(BRIDGES, bv) if c in LANDS[name]) for c in COLORS)
            for uv in untapped:
                sources = tuple(x + y for x, y in zip(bs, uv))
                common = sum(hit[s] for s in sources)
                # Final tie-break is explicit, deterministic, never simulation-driven.
                for profile, (_, focus) in PROFILES.items():
                    score = common + (2 * hit[sources[COLORS.index(focus)]] if focus else 0)
                    key = (round(score, 13), min(sources), uv[1], uv[2], bv, uv)
                    if profile not in best or key > best[profile][0]:
                        best[profile] = (key, bv, uv, sources)
        for profile, (_, focus) in PROFILES.items():
            key, bv, uv, sources = best[profile]
            lands = {name: n for name, n in zip(BRIDGES + MONOS, bv + uv) if n}
            out.append({'id': f'{profile}-{b}', 'profile': profile,
                        'label': PROFILES[profile][0], 'bridges': b, 'lands': lands,
                        'sources': dict(zip(COLORS, sources)), 'surrogate_score': key[0]})
    return out


@dataclass
class Permanent:
    name: str
    tapped: bool = False


class Game:
    def __init__(self, hand, library, trace=False):
        self.hand = list(hand)
        self.library = list(library)
        self.board = []
        self.grave = []
        self.turn = 0
        self.land_used = False
        self.draws = 0
        self.extra_draws = 0
        self.cast_count = 0
        self.development_count = 0
        self.first = {}
        self.metrics = {}
        self.turns = []
        self.trace = [] if trace else None

    def log(self, action):
        if self.trace is not None:
            self.trace.append({'turn': self.turn, 'action': action, 'hand': list(self.hand),
                               'board': [p.name + (' [T]' if p.tapped else '') for p in self.board]})

    def count(self, name):
        return sum(p.name == name for p in self.board)

    def artifacts(self):
        return sum(p.name in LANDS or RULES[p.name][2] for p in self.board)

    def draw(self, count=1, extra=True):
        for _ in range(count):
            if not self.library:
                return
            card = self.library.pop(0)
            self.hand.append(card)
            self.draws += 1
            self.extra_draws += int(extra)

    def demand(self):
        return Counter(RULES[c][1] for c in self.hand if c in RULES and RULES[c][1])

    def payment(self, generic, color='', relaxed=False):
        """Return land indices + optional Boulder; never creates extra mana.

        A colored pip uses a matching land or one land + an untapped filter.
        The latter still consumes only ONE mana, not two. All supported spells
        contain at most one colored pip, so filter chains are unnecessary.
        """
        lands = [i for i, p in enumerate(self.board) if p.name in LANDS and not p.tapped]
        total = generic + bool(color)
        if len(lands) < total:
            return None
        if not total:
            return ((), None)
        demand = self.demand()
        def scarcity(i):
            return sum(1 + demand[c] for c in LANDS[self.board[i].name])
        ordered = sorted(lands, key=lambda i: (scarcity(i), i))
        if not color or relaxed:
            return (tuple(ordered[:total]), None)
        choices = []
        for i in lands:
            if color in LANDS[self.board[i].name]:
                others = [j for j in ordered if j != i][:generic]
                choices.append((sum(scarcity(j) for j in [i] + others), 0, tuple([i] + others), None))
        filters = [i for i, p in enumerate(self.board) if p.name == BOULDER and not p.tapped]
        if filters:
            paid = tuple(ordered[:total])
            choices.append((sum(scarcity(i) for i in paid), 1, paid, filters[0]))
        if not choices:
            return None
        chosen = min(choices, key=lambda x: (x[0], x[1], x[2]))
        return chosen[2], chosen[3]

    def pay(self, payment):
        assert payment is not None
        lands, boulder = payment
        for i in lands:
            assert not self.board[i].tapped
            self.board[i].tapped = True
        if boulder is not None:
            assert not self.board[boulder].tapped
            self.board[boulder].tapped = True

    def cost(self, card):
        generic, color, _, _, affinity = RULES[card]
        return max(0, generic - self.artifacts()) if affinity else generic, color

    def scry(self):
        revealed = self.library[:2]
        del self.library[:len(revealed)]
        lands = sum(p.name in LANDS for p in self.board) + sum(c in LANDS for c in self.hand)
        def value(c):
            if c in LANDS:
                return 100 if lands < 3 else (65 if lands < 4 else -10)
            if c == BOULDER:
                return 90 if not self.count(BOULDER) and BOULDER not in self.hand else -5
            return {RELIC: 70, THOUGHT: 70, FAMILIAR: 65, MONITOR: 60,
                    ENFORCER: 50, FOUNTAIN: 45, HAWK: 40, BARGAIN: 35, BOMB: 25}.get(c, 0)
        top = sorted([c for c in revealed if value(c) > 0], key=value, reverse=True)
        bottom = [c for c in revealed if value(c) <= 0]
        self.library = top + self.library + bottom

    def fodder(self):
        """Protect lands, threats and the only filter; sacrifice engine material."""
        rank = {RELIC: 0, 'Blood token': 1, BOMB: 2, FOUNTAIN: 3, BOULDER: 4}
        choices = [(rank[p.name], i) for i, p in enumerate(self.board)
                   if p.name in rank and (p.name != BOULDER or self.count(BOULDER) > 1)]
        return min(choices)[1] if choices else None

    def remove(self, index, bounce=False):
        p = self.board.pop(index)
        if p.name != 'Blood token':
            (self.hand if bounce else self.grave).append(p.name)
        if p.name == RELIC:
            self.draw()
        if p.name == BOMB and not bounce:
            payment = self.payment(0, 'B')
            if payment is not None:
                self.pay(payment)
                self.draw()
        return p.name

    def bounce_target(self):
        rank = {RELIC: 0, BOULDER: 1, BOMB: 2, FOUNTAIN: 3}
        choices = [(rank[p.name], i) for i, p in enumerate(self.board) if p.name in rank]
        return min(choices)[1] if choices else None

    def legal(self, card, relaxed=False):
        if card not in RULES or card == DISPATCH:
            return None  # No opponent creature is supplied in the goldfish.
        if card == HAWK and self.bounce_target() is None:
            return None
        if card == BARGAIN and self.fodder() is None:
            return None
        return self.payment(*self.cost(card), relaxed=relaxed)

    def cast(self, card, payment):
        self.pay(payment)
        self.hand.remove(card)
        self.cast_count += 1
        self.development_count += int(card not in (BLAST, DISPATCH))
        self.first.setdefault(card, self.turn)
        _, _, artifact, creature, _ = RULES[card]
        if artifact or creature or card == MUNITIONS:
            self.board.append(Permanent(card))
        else:
            self.grave.append(card)
        if card == BOULDER:
            self.scry()
        elif card == RELIC:
            self.draw()
        elif card == THOUGHT:
            self.draw(2)
        elif card == FOUNTAIN:
            self.board.append(Permanent('Blood token'))
        elif card == BARGAIN:
            self.remove(self.fodder())
            self.draw(2)
        elif card == HAWK:
            self.remove(self.bounce_target(), bounce=True)
        # Familiar: opponent can discard, no invented free draw in a goldfish.
        self.log('cast ' + card)

    def probe(self, local):
        available = sum(p.name in LANDS and not p.tapped for p in self.board)
        filters = any(p.name == BOULDER and not p.tapped for p in self.board)
        access = {c for p in self.board if p.name in LANDS and not p.tapped for c in LANDS[p.name]}
        if available and filters:
            access.update(COLORS)
            self.first.setdefault('operative_boulder', self.turn)
        if len(access) == 4:
            self.first.setdefault('all4', self.turn)
        for c in access:
            local[c] = True
            if available >= 2:
                local['two_' + c] = True
        colored = [c for c in set(self.hand) if c in RULES and RULES[c][1] and c != DISPATCH]
        if any(self.legal(c, relaxed=True) is not None for c in colored) and not any(self.legal(c) is not None for c in colored):
            local['blocked'] = True

    def choose_land(self):
        choices = list(dict.fromkeys(c for c in self.hand if c in LANDS))
        if not choices:
            return
        demand = self.demand()
        best = None
        for card in choices:
            self.board.append(Permanent(card, card in BRIDGES))
            legal = [c for c in set(self.hand) if c in RULES and self.legal(c) is not None]
            score = max((self.action_score(c) for c in legal), default=0)
            # Immediate useful actions dominate; idle turns prepare a bridge.
            coverage = set(c for p in self.board if p.name in LANDS for c in LANDS[p.name])
            available = sum(p.name in LANDS and not p.tapped for p in self.board)
            key = (score, available if score else int(card in BRIDGES), len(coverage),
                   sum(1 + demand[c] for c in LANDS[card]), card)
            self.board.pop()
            if best is None or key > best[0]:
                best = (key, card)
        card = best[1]
        self.hand.remove(card)
        self.board.append(Permanent(card, card in BRIDGES))
        self.land_used = True
        self.log('land ' + card)

    def action_score(self, card):
        if card == BOULDER:
            return 110 if not self.count(BOULDER) else 38
        if card == THOUGHT:
            return 96
        if card == RELIC:
            return 94
        if card in THREATS:
            return 90 - self.cost(card)[0] - bool(RULES[card][1])
        if card == FOUNTAIN:
            return 88
        if card == BOMB:
            return 62
        if card == HAWK:
            return 85 if self.count(RELIC) else 55
        if card == BARGAIN:
            return 75 if self.count(RELIC) else 45
        return {MUNITIONS: 25, BLAST: 10}.get(card, 0)

    def cash_draw(self):
        # Called only after no spell can be cast. Bomb's tap costs zero;
        # remove() pays B exactly once for its death trigger.
        for i, p in enumerate(self.board):
            if p.name == BOMB and not p.tapped and self.payment(0, 'B') is not None:
                self.remove(i)
                self.log('activate Spellbomb')
                return True
        if self.count(MUNITIONS) and self.count(RELIC):
            payment = self.payment(1)
            if payment is not None:
                self.pay(payment)
                self.remove(next(i for i, p in enumerate(self.board) if p.name == RELIC))
                self.log('Munitions sacrifice Relic')
                return True
        for i, p in enumerate(self.board):
            if p.name == RELIC:
                payment = self.payment(1, 'U')
                if payment is not None:
                    self.pay(payment)
                    self.remove(i)
                    self.log('activate Relic with zero targets')
                    return True
            if p.name == 'Blood token' and not p.tapped and self.hand:
                payment = self.payment(1)
                if payment is not None:
                    def discard_value(c):
                        if c in LANDS:
                            total = sum(q.name in LANDS for q in self.board) + sum(x in LANDS for x in self.hand)
                            return 0 if total > 4 else 100
                        return {DISPATCH: 0, BLAST: 5, MUNITIONS: 10,
                                BOULDER: 15 if self.count(BOULDER) else 90}.get(c, 60)
                    discard = min(self.hand, key=lambda c: (discard_value(c), c))
                    self.pay(payment)
                    self.hand.remove(discard)
                    self.grave.append(discard)
                    self.remove(i)
                    self.draw()
                    self.log('activate Blood; discard ' + discard)
                    return True
        if self.count(FOUNTAIN):
            creatures = [c for c in self.grave if c in RULES and RULES[c][3]][:2]
            payment = self.payment(3, 'B')
            if creatures and payment is not None:
                self.pay(payment)
                self.remove(next(i for i, p in enumerate(self.board) if p.name == FOUNTAIN))
                for card in creatures:
                    self.grave.remove(card)
                    self.hand.append(card)
                self.log('Fountain return ' + ', '.join(creatures))
                return True
        return False

    def before_turn(self, mode):
        """Extension point for an opponent turn; baseline has no interaction."""

    def end_turn(self, snapshot):
        """Extension point for current-board diagnostics, without changing play."""

    def play(self, mode, horizon=5):
        for turn in range(1, horizon + 1):
            self.turn = turn
            self.land_used = False
            self.before_turn(mode)
            for p in self.board:
                p.tapped = False
            if turn > 1 or mode == 'OTD':
                self.draw(extra=False)
            before = self.development_count
            local = {}
            self.probe(local)
            self.choose_land()
            self.probe(local)
            for _ in range(60):
                choices = [(self.action_score(c), c, self.legal(c)) for c in sorted(set(self.hand)) if c in RULES]
                choices = [c for c in choices if c[2] is not None]
                if choices:
                    _, card, payment = max(choices, key=lambda x: (x[0], x[1]))
                    self.cast(card, payment)
                elif not self.land_used and any(c in LANDS for c in self.hand):
                    self.choose_land()
                elif not self.cash_draw():
                    break
                self.probe(local)
            else:
                raise AssertionError('Action bound exceeded')
            lands = sum(p.name in LANDS for p in self.board)
            self.turns.append({'turn': turn, 'lands': lands, 'extra_draws': self.extra_draws,
                               'spells': self.development_count - before, 'local': local,
                               'artifacts': self.artifacts(), 'threats': sum(p.name in THREATS for p in self.board)})
            self.end_turn(self.turns[-1])
        f = self.first
        for t in (2, 3, 4):
            self.metrics[f'all4_t{t}'] = f.get('all4', 99) <= t
        for t in (1, 2, 3):
            self.metrics[f'boulder_t{t}'] = f.get('operative_boulder', 99) <= t
            for c in COLORS:
                self.metrics[f'{c}_t{t}'] = bool(self.turns[t-1]['local'].get(c))
        for c in COLORS:
            self.metrics[f'two_mana_{c}_t2'] = bool(self.turns[1]['local'].get('two_' + c))
        self.metrics.update(relic_t2=f.get(RELIC, 99) <= 2,
                            threat_t3=any(f.get(c, 99) <= 3 for c in THREATS),
                            needed_t1_t3=all(t['spells'] > 0 for t in self.turns[:3]),
                            needed_t2_t3=all(t['spells'] > 0 for t in self.turns[1:3]),
                            color_block_t3=any(t['local'].get('blocked', False) for t in self.turns[:3]),
                            screw_t4=self.turns[3]['lands'] <= 2, failed_keep=False)
        for t in (3, 4, 5):
            self.metrics[f'curve{t}'] = self.turns[t-1]['lands'] >= t
        return self.metrics


def starting_hand(deck, rng):
    """London mulligan, original seven every time, keep >=2 lands, floor4.

    Bottom: retain three lands at sizes5–7 if possible, two at4; then the first
    Boulder, one cheap engine, and castable development. No draw-mode peek.
    """
    for m in range(4):
        shuffled = list(deck)
        rng.shuffle(shuffled)
        seven, size = shuffled[:7], 7 - m
        land_positions = [i for i, c in enumerate(seven) if c in LANDS]
        if len(land_positions) < 2:
            continue
        target = min(len(land_positions), 3 if size >= 5 else 2)
        # Enumerate small land subset to preserve colors and at least one untapped.
        def land_key(subset):
            names = [seven[i] for i in subset]
            return (int(any(c not in BRIDGES for c in names)),
                    len(set(c for n in names for c in LANDS[n])),
                    sum(c not in BRIDGES for c in names), tuple(-i for i in subset))
        keep_positions = list(max(combinations(land_positions, target), key=land_key))
        spells = [i for i, c in enumerate(seven) if c not in LANDS]
        priority = {BOULDER: 100, RELIC: 80, FOUNTAIN: 75, THOUGHT: 70,
                    BOMB: 65, FAMILIAR: 60, MONITOR: 55, HAWK: 50, ENFORCER: 40,
                    BARGAIN: 35, BLAST: 20, DISPATCH: 10, MUNITIONS: 15}
        chosen_boulder = False
        while spells and len(keep_positions) < size:
            index = max(spells, key=lambda i: (priority[seven[i]] - (80 if seven[i] == BOULDER and chosen_boulder else 0), -i))
            spells.remove(index)
            keep_positions.append(index)
            chosen_boulder |= seven[index] == BOULDER
        # A seven containing 6–7 lands is still a legal keep under user's rule.
        for i in range(7):
            if len(keep_positions) >= size:
                break
            if i not in keep_positions:
                keep_positions.append(i)
        hand = [seven[i] for i in sorted(keep_positions)]
        bottom = [seven[i] for i in range(7) if i not in keep_positions]
        return hand, shuffled[7:] + bottom, m
    return None, None, 3


def wilson(successes, n):
    p = successes / n
    z = 1.95996398454
    d = 1 + z*z/n
    midpoint = (p + z*z/(2*n))/d
    half = z*sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return [max(0, midpoint-half), min(1, midpoint+half)]


def run_cell(candidate, mode, spells, n, seed):
    deck = [name for name, count in candidate['lands'].items() for _ in range(count)] + spells
    assert len(deck) == 60
    counts = Counter()
    extras = Counter()
    outcomes = []
    traces = []
    for trial in range(n):
        rng = random.Random(seed + trial)
        hand, library, mulligans = starting_hand(deck, rng)
        counts['mulligans'] += mulligans
        if hand is None:
            result = {'failed_keep': True}
        else:
            game = Game(hand, library, trace=(trial < 1))
            result = game.play(mode)
            for t in game.turns:
                extras[f'extra_draws_t{t["turn"]}'] += t['extra_draws']
                extras[f'artifacts_t{t["turn"]}'] += t['artifacts']
                extras[f'threats_t{t["turn"]}'] += t['threats']
            if game.trace is not None:
                traces.append({'trial': trial, 'mode': mode, 'mulligans': mulligans,
                               'opening': hand, 'events': game.trace, 'metrics': result})
        mask = 0
        for i, metric in enumerate(METRICS):
            if result.get(metric):
                counts[metric] += 1
                mask |= 1 << i
        outcomes.append(mask)
    metrics = {key: {'successes': counts[key], 'p': counts[key]/n,
                     'ci95': wilson(counts[key], n)} for key in METRICS}
    means = {key: value/n for key, value in extras.items()}
    means['mulligans'] = counts['mulligans']/n
    kept = n-counts['failed_keep']
    means['screw_conditional_kept'] = counts['screw_t4']/kept if kept else 0
    return {'candidate': candidate['id'], 'profile': candidate['profile'],
            'bridges': candidate['bridges'], 'mode': mode, 'n': n,
            'metrics': metrics, 'means': means, 'traces': traces}, outcomes


def paired(a, b, metric):
    """A minus B, common shuffled indices; pointwise 95% normal CI."""
    bit = 1 << METRICS.index(metric)
    diffs = [int(bool(x & bit))-int(bool(y & bit)) for x, y in zip(a, b)]
    n = len(diffs)
    mean = sum(diffs)/n
    variance = (sum(d*d for d in diffs)-n*mean*mean)/(n-1) if n > 1 else 0
    half = 1.95996398454*sqrt(max(0, variance)/n)
    return {'difference': mean, 'ci95': [mean-half, mean+half], 'discordant': sum(d != 0 for d in diffs), 'n': n}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trials', type=int, default=2000)
    parser.add_argument('--seed', type=int, default=2026102901)
    parser.add_argument('--output', default='results/color_bridges_pilot')
    parser.add_argument('--workers', type=int, default=1)
    args = parser.parse_args()
    began = time.perf_counter()
    reference = json.loads((ROOT/'data/reference_deck.json').read_text())
    spells = [name for name, count in reference['cards'].items() if name not in LANDS for _ in range(count)]
    assert len(spells) == 41 and spells.count(BOULDER) == 4
    bases = candidates()
    cells, raw = [], {}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        tasks = [pool.submit(run_cell, candidate, mode, spells, args.trials, args.seed)
                 for candidate in bases for mode in ('OTP', 'OTD')]
        for i, future in enumerate(as_completed(tasks)):
            cell, outcomes = future.result()
            cells.append(cell)
            raw[(cell['candidate'], cell['mode'])] = outcomes
            print(f'{i+1}/{len(tasks)} {cell["candidate"]} {cell["mode"]}: {time.perf_counter()-began:.1f}s', flush=True)
    order = {c['id']: i for i, c in enumerate(bases)}
    cells.sort(key=lambda c: (order[c['candidate']], c['mode'] != 'OTP'))
    comparisons = []
    for profile in PROFILES:
        for mode in ('OTP', 'OTD'):
            for a, b in combinations(BRIDGE_COUNTS, 2):
                for metric in ('needed_t2_t3', 'threat_t3', 'all4_t3', 'relic_t2'):
                    comparisons.append({'profile': profile, 'mode': mode, 'a': a, 'b': b,
                                        'metric': metric, **paired(raw[(f'{profile}-{a}', mode)], raw[(f'{profile}-{b}', mode)], metric)})
    data = {'version': '1.0', 'date': '2026-10-29', 'seed': args.seed,
            'n_per_cell': args.trials, 'total_trials': len(cells)*args.trials,
            'config': {'lands': 19, 'boulders': 4, 'bridges': list(BRIDGE_COUNTS),
                       'horizon': 5, 'keep_min_lands': 2, 'mulligan_floor': 4,
                       'focus_weight': 3, 'other_weight': 1, 'citadels': 0,
                       'opponent': 'no interaction; Familiar opponent can discard',
                       'scope': f'{len(bases)} surrogate-selected bases, common greedy pilot; not global optimum'},
            'profiles': {k: {'label': v[0], 'focus': v[1]} for k, v in PROFILES.items()},
            'candidates': bases, 'cells': cells, 'paired_comparisons': comparisons,
            'elapsed_seconds': round(time.perf_counter()-began, 2),
            'source_hashes': {path: hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
                              for path in ('src/color_bridge_study.py', 'data/reference_deck.json', 'configs/structural_stages.json')}}
    out = ROOT/args.output
    out.mkdir(parents=True, exist_ok=True)
    (out/'results.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    with (out/'metrics.csv').open('w', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['profile', 'bridges', 'mode', 'n', 'metric', 'successes', 'p', 'ci95_low', 'ci95_high'])
        for cell in cells:
            for key, value in cell['metrics'].items():
                writer.writerow([cell['profile'], cell['bridges'], cell['mode'], cell['n'], key,
                                 value['successes'], value['p'], *value['ci95']])
    print(f'Wrote {data["total_trials"]:,} games to {out}', flush=True)


if __name__ == '__main__':
    main()
