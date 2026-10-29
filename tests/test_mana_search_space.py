from itertools import product
from math import comb
import unittest

from src.mana_search_space import bounded_count, bounded_vectors, domain_count, exact_profiles, land_bases
from src.opening_pilot import ROOT, read_json


class ManaSearchSpaceTests(unittest.TestCase):
    def test_counts_and_enumeration_match_independent_bruteforce(self):
        for cap in (1, 2, 4):
            for types in range(5):
                for total in range(types*cap+2):
                    expected = {v for v in product(range(cap+1), repeat=types) if sum(v) == total}
                    got = list(bounded_vectors(types, total, cap))
                    self.assertEqual(len(got), len(set(got)))
                    self.assertEqual(set(got), expected)
                    self.assertEqual(bounded_count(types, total, cap), len(expected))

    def test_partition_covers_concrete_bases_including_basic_choices(self):
        scope = {"bridges": ["B"], "ordinary_artifact_lands": ["A"],
                 "citadel": ["C"], "basics": ["Island", "Swamp"]}
        for lands in range(2, 8):
            bases = list(land_bases(scope, lands, cap=2))
            profiles = list(exact_profiles(scope, lands, cap=2))
            self.assertEqual(len(bases), domain_count(scope, lands, cap=2))
            self.assertEqual(sum(p["distinct_bases"] for p in profiles), len(bases))
            self.assertEqual(len({tuple(sorted(b.items())) for b in bases}), len(bases))
            for b in bases:
                self.assertEqual(sum(b.values()), lands)
                self.assertLessEqual(b.get("Island", 0)+b.get("Swamp", 0), 1)

    def test_unrestricted_combinatorial_controls(self):
        config = read_json(ROOT/"configs/mana_search_space.json")
        core = config["scopes"]["wubr_core"]
        self.assertEqual(bounded_count(len(core["bridges"]), 20), comb(9, 5))
        self.assertEqual(bounded_count(len(core["ordinary_artifact_lands"])+1, 20), 1)
        self.assertEqual(bounded_count(6, 20), comb(9, 5))
        self.assertEqual(bounded_count(6, 19), comb(10, 5)-6)

    def test_active_domain_count_and_profile_coverage(self):
        config = read_json(ROOT/"configs/mana_search_space.json")
        scopes = config["scopes"]
        low, high = config["bridge_range"]
        total = 0
        for lands in (19, 20):
            for name, scope in scopes.items():
                self.assertEqual(scope["basics"], [])
                count = domain_count(scope, lands, bridge_min=low, bridge_max=high)
                profiles = list(exact_profiles(scope, lands, bridge_min=low, bridge_max=high))
                self.assertEqual(sum(p["distinct_bases"] for p in profiles), count)
                self.assertTrue(all(low <= p['bridges'] <= high and p['basics'] == 0 for p in profiles))
                total += count
        self.assertEqual(total, 5417403)

    def test_bridge_filter_is_applied_during_generation(self):
        scope = {"bridges": ["B1", "B2"], "ordinary_artifact_lands": ["A"],
                 "citadel": ["C"], "basics": []}
        unrestricted = list(land_bases(scope, 5, cap=2))
        expected = {tuple(sorted(b.items())) for b in unrestricted
                    if 2 <= b.get('B1', 0)+b.get('B2', 0) <= 3}
        got = list(land_bases(scope, 5, cap=2, bridge_min=2, bridge_max=3))
        self.assertEqual({tuple(sorted(b.items())) for b in got}, expected)
        self.assertEqual(len(got), len(expected))
        self.assertEqual(len(got), domain_count(scope, 5, cap=2, bridge_min=2, bridge_max=3))
        self.assertEqual(len(got), sum(p['distinct_bases'] for p in exact_profiles(scope, 5, cap=2, bridge_min=2, bridge_max=3)))


if __name__ == "__main__":
    unittest.main()
