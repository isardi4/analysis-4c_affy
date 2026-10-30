from itertools import permutations
from collections import defaultdict
from math import comb
import random
import unittest

from src.opening_pilot import choose
from src.structural_stages import (
    develop_exact, develop_sample, draw_branches, kept_counts, natural_draw,
    opening_exact, play_land, sample_opening,
)


class StructuralStagesTests(unittest.TestCase):
    def test_draw_schedule_and_no_eighth_card_in_keep(self):
        self.assertEqual([natural_draw('OTP', t) for t in range(1,7)], [0,1,1,1,1,1])
        self.assertEqual([natural_draw('OTD', t) for t in range(1,7)], [1,1,1,1,1,1])
        opening = {'hand': (1,1,5), 'library': ['U','S','S','S','S','S']}
        otp = develop_sample(opening, 'OTP', 'untapped_first')
        otd = develop_sample(opening, 'OTD', 'untapped_first')
        self.assertEqual(sum(otp[0]['state'][:2]), 1)
        self.assertEqual(sum(otd[0]['state'][:2]), 2)
        self.assertEqual(otp[0]['state'][2]+otp[0]['state'][3], 1)
        self.assertEqual(otd[0]['state'][2]+otd[0]['state'][3], 1)

    def test_opening_mass_and_minimum_lands(self):
        for lands in (19,20):
            for bridges in (0,6,12):
                states, data = opening_exact(lands,bridges)
                self.assertAlmostEqual(sum(states.values())+data['failed'],1)
                self.assertAlmostEqual(sum(data['hand_sizes'].values())+data['failed'],1)
                self.assertTrue(all(s[0]+s[1]>=2 for s in states))
                self.assertAlmostEqual(data['failed'],data['initial_lt2']**4)

    def test_bottom_retains_two_and_removes_exactly_m(self):
        for b in range(8):
            for u in range(8-b):
                s=7-b-u
                for m in range(4):
                    result=kept_counts(b,u,s,m)
                    if b+u<2:
                        self.assertIsNone(result)
                    else:
                        self.assertEqual(sum(result),7-m)
                        self.assertGreaterEqual(result[0]+result[1],2)
                        self.assertTrue(all(0<=a<=z for a,z in zip(result,(b,u,s))))

    def test_tapped_land_counts_as_land_but_not_current_mana(self):
        opening={'hand':(1,1,5),'library':['S']*6}
        uf=develop_sample(opening,'OTP','untapped_first')
        bf=develop_sample(opening,'OTP','bridge_t1_then_untapped')
        self.assertEqual([x['capacity'] for x in uf[:2]],[1,1])
        self.assertEqual([x['capacity'] for x in bf[:2]],[0,2])
        self.assertTrue(uf[1]['events']['lands_on_curve'])
        self.assertFalse(uf[1]['events']['capacity_on_curve'])

    def test_stochastic_draw_matches_all_permutations(self):
        start=(2,0,0,0,1,1,1)
        distribution={start:1.0}
        for _ in range(2):
            nxt=defaultdict(float)
            for state,mass in distribution.items():
                for drawn,p in draw_branches(state,True):
                    after,_=play_land(drawn,'untapped_first')
                    nxt[after]+=mass*p
            distribution=dict(nxt)
        brute=defaultdict(float)
        for cards in permutations('BUS'):
            state=start
            for card in cards[:2]:
                a=list(state)
                if card=='B':a[0]+=1;a[4]-=1
                elif card=='U':a[1]+=1;a[5]-=1
                else:a[6]-=1
                state,_=play_land(tuple(a),'untapped_first')
            brute[state]+=1/6
        self.assertEqual(set(distribution),set(brute))
        for state in distribution:self.assertAlmostEqual(distribution[state],brute[state])

    def test_lands_curve_matches_independent_hypergeometric_after_keep(self):
        for mode in ('OTP','OTD'):
            states,_=opening_exact(19,0)
            result=develop_exact(19,0,mode,'untapped_first')
            for turn in (3,4,5):
                draws=turn-int(mode=='OTP')
                expected=0
                for state,mass in states.items():
                    held=state[0]+state[1]
                    lands_left=state[4]+state[5]
                    spells_left=state[6]
                    p=sum(choose(lands_left,k)*choose(spells_left,draws-k)/comb(53,draws)
                          for k in range(draws+1) if held+k>=turn)
                    expected+=mass*p
                got=result['turns'][turn-1]['probabilities_unconditional'].get('lands_on_curve',0)
                self.assertAlmostEqual(got,expected)

    def test_bridge_count_does_not_change_land_stock_under_common_rule(self):
        a=develop_exact(19,9,'OTP','untapped_first')
        b=develop_exact(19,14,'OTP','bridge_t1_then_untapped')
        for ta,tb in zip(a['turns'],b['turns']):
            self.assertAlmostEqual(ta['probabilities_unconditional'].get('lands_on_curve',0),
                                   tb['probabilities_unconditional'].get('lands_on_curve',0))
        self.assertAlmostEqual(a['opening']['failed'],b['opening']['failed'])

    def test_sample_conserves_deck_and_is_reproducible(self):
        for seed in range(50):
            a=sample_opening(19,10,random.Random(seed))
            b=sample_opening(19,10,random.Random(seed))
            self.assertEqual(a,b)
            if a:
                self.assertEqual(sum(a['hand'])+len(a['library']),60)
                self.assertEqual(a['hand'][0]+a['library'].count('B'),10)
                self.assertEqual(a['hand'][1]+a['library'].count('U'),9)
                self.assertGreaterEqual(a['hand'][0]+a['hand'][1],2)


if __name__=='__main__':
    unittest.main()
