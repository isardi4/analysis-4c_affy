"""3/4 Boulder and artifact hate, as conditional stress tests on visible boards."""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import combinations
from math import comb, sqrt
from pathlib import Path
import argparse
import csv
import hashlib
import json
import random
import time

from src.color_bridge_study import (ROOT, BRIDGE_COUNTS, LANDS, BRIDGES, MONOS,
    RULES, BOULDER, RELIC, FAMILIAR, MONITOR, ENFORCER, HAWK, BOMB, MUNITIONS, THREATS,
    Game, Permanent, candidates, starting_hand, wilson)

CONFIG = json.loads((ROOT/'configs/boulder_hate.json').read_text())
MEASURES = ['failed_keep','boulder_kept','boulder_by_fifth_draw','development_t2_t3','hate_resolved']
MEASURES += [f'{metric}_t{t}' for t in (2,3,4,5,6)
             for metric in ('suite','all4','boulder','mana2','development','threat')]


def with_citadels(base, count):
    if not count:
        return {**base, 'citadels':0}
    lands = base['lands']
    choices=[]
    available=[name for name in MONOS for _ in range(lands.get(name,0))]
    for removed in set(combinations(available,count)):
        new=Counter(lands)
        new.subtract(removed)
        new['Darksteel Citadel']=count
        sources=[sum(n for name,n in new.items() if c in LANDS[name]) for c in 'WUBR']
        hit=sum(1-comb(60-n,9)/comb(60,9) for n in sources)
        key=(round(hit,13),min(sources),tuple(sources),removed)
        choices.append((key,dict(new)))
    _, new=max(choices,key=lambda x:x[0])
    new={name:n for name,n in new.items() if n}
    return {**base,'id':base['id']+f'-c{count}','lands':new,'citadels':count,
            'sources':{c:sum(n for name,n in new.items() if c in LANDS[name]) for c in 'WUBR'}}


class StressGame(Game):
    def __init__(self, hand, library, scenario='none', trace=False):
        super().__init__(hand,library,trace)
        self.scenario=scenario
        self.exile=[]
        self.kept_boulder=BOULDER in hand
        self.early_boulder=self.kept_boulder
        self.hits=[]
        self.live={}

    def draw(self,count=1,extra=True):
        for _ in range(count):
            card=self.library[0] if self.library else None
            super().draw(1,extra)
            if card==BOULDER and self.draws<=5:
                self.early_boulder=True

    @staticmethod
    def indestructible(p):
        return p.name in BRIDGES or p.name=='Darksteel Citadel'

    def priority(self,p):
        # All information used here is public; do not inspect hand/library.
        other_colors={c for q in self.board if q is not p and q.name in LANDS for c in LANDS[q.name]}
        loss=len(set(LANDS.get(p.name,''))-other_colors)
        return (int(p.name in LANDS),loss,int(p.name==BOULDER),int(p.name in THREATS),p.name)

    def lose_batch(self,targets,exile=False):
        # Simultaneous departure first; triggers see the surviving mana sources.
        ids={id(p) for p in targets}
        self.board=[p for p in self.board if id(p) not in ids]
        for p in targets:
            if p.name!='Blood token':
                (self.exile if exile else self.grave).append(p.name)
        for p in targets:
            if p.name==RELIC:
                self.draw()
            if p.name==BOMB and not exile:
                payment=self.payment(0,'B')
                if payment is not None:
                    self.pay(payment)
                    self.draw()

    def attack(self,enemy_turn):
        artifacts=[p for p in self.board if p.name in LANDS or RULES[p.name][2]]
        targets=[]
        exile=self.scenario in ('dust','masked')
        if self.scenario=='dust' and len(artifacts)>=2:
            targets=sorted(artifacts,key=self.priority,reverse=True)[:2]
        elif self.scenario=='masked':
            eligible=artifacts+[p for p in self.board if p.name==MUNITIONS]
            if eligible:
                targets=[max(eligible,key=self.priority)]
        elif self.scenario=='vandalblast':
            vulnerable=[p for p in artifacts if not self.indestructible(p)]
            if vulnerable:
                targets=[max(vulnerable,key=self.priority)]
        elif self.scenario=='overload':
            targets=[p for p in artifacts if not self.indestructible(p)]
        elif self.scenario=='gorilla':
            budget=enemy_turn
            # Each activation resolves separately. Creature artifacts are illegal.
            while True:
                legal=[p for p in self.board if p.name in LANDS or (RULES[p.name][2] and not RULES[p.name][3])]
                legal=[p for p in legal if not self.indestructible(p) and 2*self.mana_value(p)+1<=budget]
                if not legal:
                    break
                target=max(legal,key=self.priority)
                budget-=2*self.mana_value(target)+1
                targets.append(target)
                self.lose_batch([target])
        if targets and self.scenario!='gorilla':
            self.lose_batch(targets,exile)
        self.hits.append({'opponent_turn':enemy_turn,'before_player_turn':self.turn,
                          'targets':[p.name for p in targets], 'exile':exile,
                          'lands_lost':sum(p.name in LANDS for p in targets),
                          'boulders_lost':sum(p.name==BOULDER for p in targets),
                          'artifacts_lost':sum(p.name in LANDS or RULES[p.name][2] for p in targets)})
        self.log('opponent '+self.scenario+': '+', '.join(p.name for p in targets))

    @staticmethod
    def mana_value(p):
        if p.name in LANDS or p.name=='Blood token':
            return 0
        rule=RULES[p.name]
        return rule[0]+bool(rule[1])  # Printed cost, not affinity-reduced cost.

    def before_turn(self,mode):
        enemy_turn=self.turn if mode=='OTD' else self.turn-1
        if enemy_turn in CONFIG['scenarios'][self.scenario]['opponent_turns']:
            self.attack(enemy_turn)

    def probe(self,local):
        super().probe(local)
        mana=sum(p.name in LANDS and not p.tapped for p in self.board)
        filter_ready=mana>0 and any(p.name==BOULDER and not p.tapped for p in self.board)
        colors={c for p in self.board if p.name in LANDS and not p.tapped for c in LANDS[p.name]}
        local['live_all4']=local.get('live_all4',False) or filter_ready or len(colors)==4
        local['live_boulder']=local.get('live_boulder',False) or filter_ready
        local['mana2']=local.get('mana2',False) or mana>=2
        # Independent cost probes, not spells inserted into hand or cast together:
        # Cryogen, Bargain, Hawk/Dispatch/Blast colors, and Utrom with affinity.
        if not local.get('suite'):
            costs=[(1,'U'),(1,'B'),(0,'W'),(0,'R'),(max(0,4-self.artifacts()),'U')]
            local['suite']=bool(self.artifacts()) and all(self.payment(g,c) is not None for g,c in costs)

    def end_turn(self,snapshot):
        t=snapshot['turn']
        if t<2:
            return
        local=snapshot['local']
        self.live.update({f'suite_t{t}':bool(local.get('suite')),
                          f'all4_t{t}':bool(local.get('live_all4')),
                          f'boulder_t{t}':bool(local.get('live_boulder')),
                          f'mana2_t{t}':bool(local.get('mana2')),
                          f'development_t{t}':snapshot['spells']>0,
                          f'threat_t{t}':snapshot['threats']>0})


def spell_list(boulders):
    ref=json.loads((ROOT/'data/reference_deck.json').read_text())['cards']
    counts={name:n for name,n in ref.items() if name not in LANDS}
    counts[BOULDER]=boulders
    counts[CONFIG['replacement_for_fourth_boulder']]+=4-boulders
    assert sum(counts.values())==41 and max(counts.values())<=4 and boulders in (3,4)
    return [name for name,n in counts.items() for _ in range(n)]


def run_case(base,boulders,mode,scenario,n,seed):
    deck=[name for name,k in base['lands'].items() for _ in range(k)]+spell_list(boulders)
    counts,means=Counter(),Counter()
    outcomes=[]
    traces=[]
    for trial in range(n):
        hand,library,m=starting_hand(deck,random.Random(seed+trial))
        means['mulligans']+=m
        result={'failed_keep':hand is None}
        if hand is not None:
            game=StressGame(hand,library,scenario,trace=(trial==0 and base['bridges']==10 and mode=='OTP'))
            game.play(mode,CONFIG['horizon'])
            result.update(game.live,boulder_kept=game.kept_boulder,boulder_by_fifth_draw=game.early_boulder,
                          development_t2_t3=all(s['spells']>0 for s in game.turns[1:3]),
                          hate_resolved=any(h['targets'] for h in game.hits))
            means['lands_lost']=means['lands_lost']+sum(h['lands_lost'] for h in game.hits)
            means['boulders_lost']+=sum(h['boulders_lost'] for h in game.hits)
            means['artifacts_lost']+=sum(h['artifacts_lost'] for h in game.hits)
            means['extra_draws_t6']+=game.extra_draws
            if game.trace is not None:
                traces.append({'trial':trial,'opening':hand,'events':game.trace,'hits':game.hits,'metrics':result})
        mask=0
        for i,key in enumerate(MEASURES):
            if result.get(key):
                counts[key]+=1
                mask|=1<<i
        outcomes.append(mask)
    metrics={key:{'successes':counts[key],'p':counts[key]/n,'ci95':wilson(counts[key],n)} for key in MEASURES}
    return {'bridges':base['bridges'],'citadels':base['citadels'],'boulders':boulders,'mode':mode,
            'scenario':scenario,'n':n,'metrics':metrics,
            'means':{k:means[k]/n for k in ('lands_lost','boulders_lost','artifacts_lost','mulligans','extra_draws_t6')},
            'traces':traces},outcomes


def difference(a,b,metric):
    bit=1<<MEASURES.index(metric)
    diffs=[int(bool(x&bit))-int(bool(y&bit)) for x,y in zip(a,b)]
    n=len(diffs);mean=sum(diffs)/n
    variance=max(0,(sum(d*d for d in diffs)-n*mean*mean)/(n-1))
    half=1.95996398454*sqrt(variance/n)
    return {'difference':mean,'ci95':[mean-half,mean+half],'n':n}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    began=time.perf_counter()
    balanced=[b for b in candidates() if b['profile']=='balanced']
    bases=[with_citadels(b,c) for b in balanced for c in CONFIG['citadels']]
    cells,raw=[],{}
    def key(c):return (c['bridges'],c['citadels'],c['boulders'],c['mode'],c['scenario'])
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        tasks=[pool.submit(run_case,base,b,mode,s,CONFIG['trials_per_cell'],CONFIG['seed'])
               for base in bases for b in CONFIG['boulders'] for mode in ('OTP','OTD') for s in CONFIG['scenarios']]
        for i,future in enumerate(as_completed(tasks)):
            cell,outcomes=future.result();cells.append(cell);raw[key(cell)]=outcomes
            if (i+1)%12==0 or i+1==len(tasks):
                print(f'{i+1}/{len(tasks)} cases · {time.perf_counter()-began:.1f}s',flush=True)
    cells.sort(key=key)
    comparisons=[]
    for c in cells:
        k=key(c)
        references=[]
        if c['scenario']!='none':references.append(('hate_minus_none',k[:4]+('none',)))
        if c['boulders']==4:references.append(('four_minus_three',(k[0],k[1],3,k[3],k[4])))
        if c['citadels']==2:references.append(('citadel2_minus0',(k[0],0,k[2],k[3],k[4])))
        for label,ref in references:
            for metric in ('suite_t4','suite_t6','all4_t3','development_t2_t3'):
                comparisons.append({**{x:c[x] for x in ('bridges','citadels','boulders','mode','scenario')},
                                    'comparison':label,'metric':metric,**difference(raw[k],raw[ref],metric)})
    out=ROOT/'results/boulder_hate';out.mkdir(exist_ok=True)
    paths=['src/boulder_hate.py','src/color_bridge_study.py','configs/boulder_hate.json','configs/structural_stages.json','data/reference_deck.json']
    data={'version':'1.0','date':'2026-10-29','config':CONFIG,'bridges':list(BRIDGE_COUNTS),
          'total_trials':len(cells)*CONFIG['trials_per_cell'],'cells':cells,'candidates':bases,
          'paired_comparisons':comparisons,'elapsed_seconds':round(time.perf_counter()-began,2),
          'nonlands':{str(b):dict(Counter(spell_list(b))) for b in CONFIG['boulders']},
          'source_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}}
    (out/'results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    with (out/'metrics.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['bridges','citadels','boulders','mode','scenario','n','metric','successes','p','ci95_low','ci95_high'])
        for c in cells:
            for metric,m in c['metrics'].items():
                writer.writerow([c[x] for x in ('bridges','citadels','boulders','mode','scenario','n')]+[metric,m['successes'],m['p'],*m['ci95']])
    print(f'{data["total_trials"]:,} trials; {out}',flush=True)


if __name__=='__main__':main()
