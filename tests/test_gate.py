"""Gate tests — the documented quality check (T1 0.50, NOT a ship-gate)
and the -2 band rule.

-2 band rule (DECISIONS.md): exclude band-shaped -2 cores (cw > 120)
from the mask. Evidence (R18): May's dotted title band is 449 px
wide, ~14.5k mask px/page — a highlight, not a word; fused-letter -2
cores are <= 78 px; bands are >= 307 px; 120 sits in the 78 -> 307 gap.
SURGICAL refinement (2026-11-08): the band core is FUSED with the
title letters (one CC), so the exclusion keeps the part INSIDE word
boxes (letters) and drops only the part outside (dots). Measured:
May p1 mask shrinks by 4,845 px (the dots-only part; whole-core would
be 13,229 px), and 0 words lose ink coverage (whole-core exclusion
left 3 title words <50% covered). Checks here: the band core is found
and flagged, the mask shrinks by ~4.8k px on May p1, and no word is
lost (word count unchanged — the rule touches the mask only, never
the seg).
"""
import json
import os
import unittest

import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

from helpers import PG_AUG, PG_MAY, SP, render_bgr, requires_real_fixtures
import lse.gate as gate
from lse.segment import segment_array


class TestGateConstants(unittest.TestCase):
    def test_t1_threshold_unchanged(self):
        self.assertEqual(gate.CORE_OUT_FRAC, 0.50)
        self.assertEqual(gate.CORE_OUT_EXT, 6)

    def test_band_rule_constant(self):
        self.assertEqual(gate.BAND_CORE_MIN_W, 120)


@requires_real_fixtures
class TestMinusTwoBandRule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.img_may = render_bgr(PG_MAY, 0, dpi=300)
        cls.seg_may = json.load(open(os.path.join(SP, "seg-may-p1-300.json")))
        cls.img_aug = render_bgr(PG_AUG, 0, dpi=300)
        cls.seg_aug = json.load(open(os.path.join(SP, "seg-aug-p1-300.json")))

    def test_may_band_core_found(self):
        cores = gate.ambiguous_band_cores(self.img_may, self.seg_may)
        band = [c for c in cores if c["band"]]
        print(f"  May p1: {len(cores)} ambiguous cores, {len(band)} band-shaped")
        for c in band:
            print(f"    band core box={c['box']} area={c['area']}")
        self.assertGreaterEqual(len(band), 1, "May's dotted title band not found")
        widest = max(c["box"][2] for c in band)
        self.assertGreaterEqual(widest, 307, f"widest band core {widest}px < 307")
        fused = [c for c in cores if not c["band"]]
        if fused:
            self.assertLessEqual(max(c["box"][2] for c in fused), 120)

    def test_may_mask_shrinks_by_band(self):
        with_px, without_px, n_band = gate.mask_px_with_without_band(
            self.img_may, self.seg_may)
        print(f"  May p1 mask: with rule {with_px}px, without {without_px}px "
              f"(band contribution {without_px - with_px}px, {n_band} band cores)")
        # Dots-only part of the band (surgical rule): 4,845 px measured.
        # Whole-core exclusion would be 13,229 px — the difference
        # (8,384 px) is the title letters kept inside their word boxes.
        self.assertGreater(without_px - with_px, 3000)
        self.assertLess(without_px - with_px, 7000)

    def test_aug_mask_band_effect_small(self):
        with_px, without_px, n_band = gate.mask_px_with_without_band(
            self.img_aug, self.seg_aug)
        print(f"  Aug p1 mask: with rule {with_px}px, without {without_px}px "
              f"(band contribution {without_px - with_px}px, {n_band} band cores)")
        self.assertGreaterEqual(without_px, with_px)

    def test_no_word_lost_by_rule(self):
        """The rule touches the mask only: the seg is identical, and
        every word's ink is still covered by the ruled mask."""
        import cv2
        import numpy as np
        words_before = len(self.seg_may["words"])
        mask, info = gate.full_page_mask(self.img_may, self.seg_may,
                                         rule_exclusion=True)
        self.assertEqual(len(self.seg_may["words"]), words_before)
        gray = cv2.cvtColor(self.img_may, cv2.COLOR_BGR2GRAY)
        uncovered = 0
        for w in self.seg_may["words"]:
            x0, y0, x1, y1 = w["box"]
            ink = (gray[y0:y1, x0:x1] < 210)
            cov = (mask[y0:y1, x0:x1] > 0) & ink
            if ink.sum() and cov.sum() < 0.5 * ink.sum():
                uncovered += 1
        print(f"  May p1 words with <50% ink covered by ruled mask: {uncovered}")
        self.assertEqual(uncovered, 0)


@requires_real_fixtures
class TestGateVerdicts(unittest.TestCase):
    def test_gate_runs_on_canonical_pages(self):
        """Gate verdicts are RECORDED here, not asserted ALLOW — the
        gate is a documented quality check, not a ship-gate."""
        for label, img, segf in (
                ("Aug p1", render_bgr(PG_AUG, 0, dpi=300), "seg-aug-p1-300.json"),
                ("May p1", render_bgr(PG_MAY, 0, dpi=300), "seg-may-p1-300.json")):
            seg = json.load(open(os.path.join(SP, segf)))
            verdict, details = gate.gate(img, seg)
            print(f"  {label}: {verdict} (T1 {details['t1_flags']}, "
                  f"T2 {details['t2_flags']}, {details['n_words']} words)")
            self.assertIn(verdict, ("ALLOW", "REFUSE"))
            self.assertIn("reasons", details)

    def test_synthetic_miss_must_refuse(self):
        """Control (R17/R18): dropping one seg box must REFUSE."""
        img = render_bgr(PG_AUG, 0, dpi=300)
        seg = json.load(open(os.path.join(SP, "seg-aug-p1-300.json")))
        lot_idx = next(i for i, w in enumerate(seg["words"])
                       if w["box"] == [533, 930, 631, 966])
        dropped = dict(seg)
        dropped["words"] = [w for i, w in enumerate(seg["words"]) if i != lot_idx]
        verdict, details = gate.gate(img, dropped)
        print(f"  synthetic miss (Lot box dropped): {verdict} "
              f"(T1 {details['t1_flags']}, T2 {details['t2_flags']})")
        self.assertEqual(verdict, "REFUSE")
        self.assertGreater(details["t1_flags"] + details["t2_flags"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
