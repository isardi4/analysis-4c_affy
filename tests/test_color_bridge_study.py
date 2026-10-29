"""Rule-sensitive checks for costs, hidden information and resource flow."""
from collections import Counter
import random
import unittest

from src.color_bridge_study import (
    Game, Permanent, LANDS, BOULDER, RELIC, THOUGHT, FAMILIAR, MONITOR,
    ENFORCER, HAWK, BARGAIN, BOMB, FOUNTAIN, METRICS, paired, starting_hand,
)


class ColorEngineTests(unittest.TestCase):
    def game(self, hand=(), lands=(), artifacts=(), library=None):
        g = Game(hand, library or [ENFORCER] * 40)
        g.turn = 2
        g.board = [Permanent(n) for n in (*lands, *artifacts)]
        return g

    def test_filter_is_not_ramp(self):
        g = self.game(lands=['Darksteel Citadel'], artifacts=[BOULDER])
        self.assertIsNotNone(g.payment(0, 'U'))
        self.assertIsNone(g.payment(1, 'U'))
        g.pay(g.payment(0, 'U'))
        self.assertTrue(all(p.tapped for p in g.board))

    def test_filter_pays_one_u_with_two_lands(self):
        g = self.game([RELIC], ['Great Furnace', 'Ancient Den'], [BOULDER])
        g.cast(RELIC, g.legal(RELIC))
        self.assertEqual(g.extra_draws, 1)
        self.assertTrue(all(p.tapped for p in g.board[:3]))

    def test_bridge_cannot_pay_on_entry(self):
        g = self.game(['Mistvault Bridge', BOULDER])
        g.choose_land()
        self.assertTrue(g.board[0].tapped)
        self.assertIsNone(g.legal(BOULDER))

    def test_affinity_reduces_only_generic(self):
        g = self.game([FAMILIAR, THOUGHT], ['Ancient Den'], [BOULDER, BOMB, RELIC])
        self.assertEqual(g.cost(FAMILIAR), (0, 'B'))
        self.assertEqual(g.cost(THOUGHT), (0, 'U'))
        g.board[1].tapped = True
        self.assertIsNone(g.legal(FAMILIAR))
        self.assertIsNone(g.legal(THOUGHT))

    def test_thoughtcast_draws_two(self):
        g = self.game([THOUGHT], ['Seat of the Synod'], [BOULDER, BOMB, RELIC])
        g.cast(THOUGHT, g.legal(THOUGHT))
        self.assertEqual(g.extra_draws, 2)
        self.assertEqual(g.artifacts(), 4)

    def test_hawk_relic_draws_on_leave_and_reentry(self):
        g = self.game([HAWK], ['Ancient Den', 'Seat of the Synod', 'Great Furnace'], [RELIC])
        g.cast(HAWK, g.legal(HAWK))
        self.assertIn(RELIC, g.hand)
        self.assertEqual(g.extra_draws, 1)
        g.cast(RELIC, g.legal(RELIC))
        self.assertEqual(g.extra_draws, 2)

    def test_bargain_relic_draws_three(self):
        g = self.game([BARGAIN], ['Vault of Whispers', 'Great Furnace'], [RELIC])
        g.cast(BARGAIN, g.legal(BARGAIN))
        self.assertEqual(g.extra_draws, 3)
        self.assertIn(RELIC, g.grave)
        self.assertEqual(g.count(RELIC), 0)

    def test_spellbomb_trigger_cost_paid_once(self):
        g = self.game(lands=['Vault of Whispers'], artifacts=[BOMB])
        self.assertTrue(g.cash_draw())
        self.assertEqual(g.extra_draws, 1)
        self.assertTrue(g.board[0].tapped)
        self.assertFalse(g.cash_draw())

    def test_scry_is_not_a_draw_and_conserves_cards(self):
        g = self.game(library=['Dispatch', 'Mistvault Bridge', ENFORCER, MONITOR])
        original = Counter(g.library)
        g.scry()
        self.assertEqual(g.draws, 0)
        self.assertEqual(g.library[0], 'Mistvault Bridge')
        self.assertEqual(Counter(g.library), original)

    def test_familiar_does_not_invent_empty_opponent_hand(self):
        g = self.game([FAMILIAR], ['Vault of Whispers'], [BOULDER, BOMB])
        g.cast(FAMILIAR, g.legal(FAMILIAR))
        self.assertEqual(g.extra_draws, 0)

    def test_boulder_all_four_means_individual_access(self):
        g = self.game(lands=['Darksteel Citadel'], artifacts=[BOULDER])
        local = {}
        g.probe(local)
        self.assertEqual(g.first['all4'], 2)
        self.assertTrue(all(local[c] for c in 'WUBR'))
        self.assertIsNone(g.payment(1, 'U'))

    def test_london_conservation_and_min_two(self):
        deck = ['Seat of the Synod']*4 + ['Ancient Den']*4 + ['Great Furnace']*4 + ['Vault of Whispers']*4 + ['Razortide Bridge']*3 + [BOULDER]*4 + [MONITOR]*37
        for seed in range(100):
            hand, library, m = starting_hand(deck, random.Random(seed))
            if hand is not None:
                self.assertGreaterEqual(sum(c in LANDS for c in hand), 2)
                self.assertEqual(len(hand), 7-m)
                self.assertEqual(Counter(hand+library), Counter(deck))

    def test_otp_otd_draw_difference_without_engine(self):
        hand = ['Ancient Den'] * 7
        a, b = Game(hand, ['Ancient Den']*53), Game(hand, ['Ancient Den']*53)
        a.play('OTP')
        b.play('OTD')
        self.assertEqual(a.draws, 4)
        self.assertEqual(b.draws, 5)

    def test_paired_comparison_zero_and_direction(self):
        bit = 1 << METRICS.index('all4_t3')
        self.assertEqual(paired([bit]*10, [bit]*10, 'all4_t3')['ci95'], [0, 0])
        result = paired([bit]*10, [0]*10, 'all4_t3')
        self.assertEqual(result['difference'], 1)

    def test_goldfish_card_conservation(self):
        deck = ['Seat of the Synod']*4 + ['Ancient Den']*4 + ['Vault of Whispers']*4 + ['Great Furnace']*4 + ['Razortide Bridge']*3
        deck += [BOULDER]*4 + [RELIC]*4 + [THOUGHT]*4 + [FAMILIAR]*4 + [MONITOR]*4 + [HAWK]*3 + [BARGAIN]*3 + [BOMB]*2 + [FOUNTAIN]*2 + [ENFORCER]*11
        self.assertEqual(len(deck), 60)
        for seed in range(30):
            hand, library, _ = starting_hand(deck, random.Random(seed))
            if hand is None:
                continue
            game = Game(hand, library)
            game.play('OTP' if seed % 2 else 'OTD')
            actual = Counter(game.hand + game.library + game.grave + [p.name for p in game.board if p.name != 'Blood token'])
            self.assertEqual(actual, Counter(deck))


if __name__ == '__main__':
    unittest.main()
