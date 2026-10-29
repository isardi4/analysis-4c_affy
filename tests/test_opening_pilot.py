from collections import Counter
from math import comb
import random
import unittest

from src.opening_pilot import (
    BOULDER, ROOT, bottom_seven, build_variants, exact_mulligan,
    exact_opening, hand_features, read_json, run_cell, starting_hand, validate_deck, wilson,
)


class OpeningPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = read_json(ROOT / "data/reference_deck.json")
        cls.catalog = read_json(ROOT / "data/opening_catalog.json")["cards"]
        cls.config = read_json(ROOT / "configs/opening_pilot.json")
        cls.variants = build_variants(cls.reference, cls.catalog, cls.config)
        cls.deck = [name for name, count in cls.reference["cards"].items() for _ in range(count)]

    def test_all_variants_preserve_sixty_and_copy_limits(self):
        self.assertEqual(len(self.variants), 12)
        for variant in self.variants:
            validate_deck(variant["cards"], self.catalog)
            self.assertIn(variant["inventory"]["lands"], (19, 20))
        original = next(v for v in self.variants if v["id"] == "original19_b4")
        self.assertEqual(original["inventory"]["natural_sources"], {"W": 6, "U": 10, "B": 8, "R": 5})
        self.assertEqual(original["inventory"]["artifacts"], 42)

    def test_reject_invalid_deck_and_unknown_card(self):
        with self.assertRaises(ValueError):
            validate_deck({"Darksteel Citadel": 60}, self.catalog)
        with self.assertRaises(ValueError):
            validate_deck({"unknown": 60}, self.catalog)

    def test_exact_initial_matches_independent_hypergeometric(self):
        for lands in (19, 20):
            exact = exact_opening(lands, 9, 4)
            p_lt2 = (comb(60-lands, 7) + lands*comb(60-lands, 6)) / comb(60, 7)
            self.assertAlmostEqual(exact["initial_lt2"], p_lt2)
            self.assertAlmostEqual(exact["initial_boulder"], 1-comb(56, 7)/comb(60, 7))
        exact = exact_opening(19, 9, 4)
        both = 1-comb(56, 7)/comb(60, 7)-comb(51, 7)/comb(60, 7)+comb(47, 7)/comb(60, 7)
        self.assertAlmostEqual(exact["initial_boulder_untapped"], both)
        self.assertLess(exact["initial_eligible_boulder_untapped"], both)

    def test_mulligan_exact_normalizes_and_matches_geometric(self):
        raw = exact_opening(19, 9, 4)
        for floor in (4, 3, 2):
            for policy in ("min_two", "seek_boulder_once"):
                result = exact_mulligan(raw, policy, floor)
                self.assertAlmostEqual(result["failed"] + sum(result["sizes"].values()), 1)
            simple = exact_mulligan(raw, "min_two", floor)
            self.assertAlmostEqual(simple["failed"], raw["initial_lt2"]**(8-floor))

    def test_bottom_never_turns_two_lands_into_one(self):
        seven = ["Darksteel Citadel", "Razortide Bridge", BOULDER, BOULDER,
                 "Cryogen Relic", "Utrom Monitor", "Thoughtcast"]
        for size in range(2, 8):
            kept, bottom = bottom_seven(seven, size, self.catalog)
            self.assertGreaterEqual(hand_features(kept, self.catalog)["lands"], 2)
            self.assertEqual(len(kept), size)
            self.assertEqual(Counter(kept + bottom), Counter(seven))
        self.assertIsNone(bottom_seven(["Seat of the Synod"] + [BOULDER]*6, 7, self.catalog))

    def test_original_seven_already_requires_two_lands(self):
        class FixedShuffle:
            def __init__(self, deck, order):
                self.deck, self.order = deck, order

            def shuffle(self, items):
                rest = list(self.deck)
                for name in self.order:
                    rest.remove(name)
                items[:] = self.order + rest

        order = ["Seat of the Synod", BOULDER, BOULDER, "Cryogen Relic",
                 "Utrom Monitor", "Thoughtcast", "Glint Hawk"]
        out = starting_hand(self.deck, self.catalog, "min_two", 4, FixedShuffle(self.deck, order))
        self.assertTrue(out["failed"])
        self.assertEqual(len(out["attempts"]), 4)
        self.assertTrue(all(not a["kept"] for a in out["attempts"]))

    def test_mulligan_conserves_library_and_orders_bottom(self):
        for policy in ("min_two", "seek_boulder_once"):
            for seed in range(100):
                out = starting_hand(self.deck, self.catalog, policy, 2, random.Random(seed))
                if out["failed"]:
                    continue
                self.assertGreaterEqual(hand_features(out["kept"], self.catalog)["lands"], 2)
                self.assertEqual(Counter(out["kept"] + out["library"]), Counter(self.deck))
                self.assertEqual(len(out["library"]), 60-len(out["kept"]))
                if out["bottom"]:
                    self.assertEqual(out["library"][-len(out["bottom"]):], out["bottom"])
                if policy == "seek_boulder_once" and len(out["kept"]) == 7:
                    self.assertIn(BOULDER, out["kept"])

    def test_repeatability_and_shared_initial_shuffles(self):
        variant = self.variants[0]
        a = run_cell(variant, self.catalog, "min_two", 4, 30, 42)
        repeat = run_cell(variant, self.catalog, "min_two", 4, 30, 42)
        b = run_cell(variant, self.catalog, "seek_boulder_once", 2, 30, 42)
        self.assertEqual(a, repeat)
        for metric in a["events"]:
            if metric.startswith("initial_"):
                self.assertEqual(a["events"][metric]["count"], b["events"][metric]["count"])

    def test_wilson_at_extremes_does_not_hide_small_n(self):
        low0, high0 = wilson(0, 2000)
        low1, high1 = wilson(2000, 2000)
        self.assertEqual(low0, 0)
        self.assertGreater(high0, 0)
        self.assertLess(low1, 1)
        self.assertEqual(high1, 1)


if __name__ == "__main__":
    unittest.main()
