from collections import Counter
import random
import unittest
from src.color_bridge_study import Game,Permanent,BOULDER,RELIC,BOMB,FAMILIAR,starting_hand
from src.boulder_hate import CONFIG,StressGame,spell_list,with_citadels


class HateTests(unittest.TestCase):
    def board(self,names,scenario):
        g=StressGame([],['Myr Enforcer']*40,scenario)
        g.board=[Permanent(n) for n in names];g.turn=3
        return g

    def test_destruction_protects_bridges_and_citadel(self):
        g=self.board(['Mistvault Bridge','Darksteel Citadel',BOULDER,FAMILIAR],'overload');g.attack(5)
        self.assertEqual([p.name for p in g.board],['Mistvault Bridge','Darksteel Citadel'])
        self.assertCountEqual(g.grave,[BOULDER,FAMILIAR])

    def test_exile_removes_indestructible_lands(self):
        g=self.board(['Mistvault Bridge','Darksteel Citadel'],'dust');g.attack(3)
        self.assertFalse(g.board)
        self.assertCountEqual(g.exile,['Mistvault Bridge','Darksteel Citadel'])
        self.assertFalse(g.grave)

    def test_dust_needs_two_distinct_targets(self):
        g=self.board([BOULDER],'dust');g.attack(3)
        self.assertEqual(g.count(BOULDER),1)
        self.assertFalse(g.hits[0]['targets'])

    def test_ancient_grudge_repeats_targeted_destruction_but_not_bridges(self):
        g=self.board(['Mistvault Bridge','Darksteel Citadel','Ancient Den','Seat of the Synod'],'ancient_grudge')
        g.attack(2)
        self.assertEqual(g.hits[-1]['lands_lost'],1)
        self.assertEqual(g.count('Mistvault Bridge'),1)
        self.assertEqual(g.count('Darksteel Citadel'),1)
        g.turn=4;g.attack(4)
        self.assertEqual(g.hits[-1]['lands_lost'],1)
        self.assertCountEqual([p.name for p in g.board],['Mistvault Bridge','Darksteel Citadel'])

    def test_gleeful_sabotage_destroys_two_vulnerable_artifacts(self):
        g=self.board(['Mistvault Bridge','Darksteel Citadel','Ancient Den','Seat of the Synod'],'gleeful')
        g.attack(3)
        self.assertEqual(g.hits[-1]['lands_lost'],2)
        self.assertCountEqual([p.name for p in g.board],['Mistvault Bridge','Darksteel Citadel'])

    def test_gorilla_budget_and_noncreatures(self):
        g=self.board(['Ancient Den','Seat of the Synod',BOULDER,FAMILIAR],'gorilla');g.attack(2)
        self.assertEqual(g.count(BOULDER),1)
        self.assertEqual(g.hits[-1]['lands_lost'],2)
        g.attack(3)
        self.assertEqual(g.count(BOULDER),0)
        self.assertEqual(g.count(FAMILIAR),1)
        self.assertEqual(g.mana_value(Permanent(FAMILIAR)),4)

    def test_spellbomb_exile_and_simultaneous_destruction(self):
        g=self.board(['Vault of Whispers',BOMB],'masked')
        g.lose_batch([p for p in g.board if p.name==BOMB],exile=True)
        self.assertEqual(g.draws,0)
        g=self.board(['Vault of Whispers',BOMB],'overload');g.attack(5)
        self.assertEqual(g.draws,0)

    def test_cryogen_draws_when_exiled_or_destroyed(self):
        for exile in (False,True):
            g=self.board([RELIC],'masked');g.lose_batch(g.board[:],exile=exile)
            self.assertEqual(g.draws,1)

    def test_opponent_timing(self):
        for mode,turn in [('OTD',3),('OTP',4)]:
            g=self.board(['Mistvault Bridge','Darksteel Citadel'],'dust')
            for t in range(1,turn):
                g.turn=t;g.before_turn(mode);self.assertEqual(len(g.board),2)
            g.turn=turn;g.before_turn(mode);self.assertFalse(g.board)

    def test_cutoff_uses_actual_draws(self):
        g=StressGame([],['Dispatch']*5+[BOULDER]);g.scry()
        self.assertEqual(g.draws,0)
        self.assertFalse(g.early_boulder)
        a=StressGame([],['Dispatch']*5+[BOULDER]);a.draw(6)
        b=StressGame([],['Dispatch']*4+[BOULDER]);b.draw(5)
        self.assertFalse(a.early_boulder)
        self.assertTrue(b.early_boulder)

    def test_three_four_and_replacement(self):
        a,b=Counter(spell_list(3)),Counter(spell_list(4))
        self.assertEqual(sum(a.values()),41)
        self.assertEqual(a[BOULDER],3);self.assertEqual(a[BOMB],3)
        self.assertEqual(a-b,Counter({BOMB:1}));self.assertEqual(b-a,Counter({BOULDER:1}))

    def test_citadel_control(self):
        base={'id':'test','lands':{'Razortide Bridge':4,'Mistvault Bridge':4,'Drossforge Bridge':2,'Seat of the Synod':4,'Vault of Whispers':3,'Ancient Den':2}}
        c=with_citadels(base,2)
        self.assertEqual(sum(c['lands'].values()),19)
        self.assertEqual(c['lands']['Darksteel Citadel'],2)
        self.assertEqual(sum(n for name,n in c['lands'].items() if 'Bridge' in name),10)

    def test_goldfish_matches_existing_engine(self):
        deck=['Seat of the Synod']*4+['Vault of Whispers']*4+['Razortide Bridge']*4+['Mistvault Bridge']*4+['Great Furnace']*3+spell_list(4)
        for seed in range(15):
            hand,library,_=starting_hand(deck,random.Random(seed))
            if hand:
                self.assertEqual(Game(hand,library).play('OTP'),StressGame(hand,library).play('OTP',6))

    def test_card_conservation_with_exile(self):
        deck=['Seat of the Synod']*4+['Vault of Whispers']*4+['Razortide Bridge']*4+['Mistvault Bridge']*4+['Great Furnace']*3+spell_list(4)
        for scenario in CONFIG['scenarios']:
            for seed in range(10):
                hand,library,_=starting_hand(deck,random.Random(seed))
                if hand:
                    g=StressGame(hand,library,scenario);g.play('OTD',6)
                    actual=g.hand+g.library+g.grave+g.exile+[p.name for p in g.board if p.name!='Blood token']
                    self.assertEqual(Counter(actual),Counter(deck))


if __name__=='__main__':unittest.main()
