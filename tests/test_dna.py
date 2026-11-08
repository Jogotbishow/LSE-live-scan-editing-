"""DNA font build — the ported builder must reproduce the prototype's
production fonts from the same median glyphs (same glyph counts, same
IoU within measurement noise).
"""
import json
import os
import unittest

import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

from helpers import SP, STAGING, requires_real_fixtures
from lse.dna import build_dna_font

OUT = os.path.join(STAGING, "dna")
os.makedirs(OUT, exist_ok=True)
DP = os.path.join(SP, "improve/round2/dna-prod")


@requires_real_fixtures
class TestDnaBuild(unittest.TestCase):
    def test_regular_600(self):
        g = json.load(open(os.path.join(DP, "glyphs-weights-600.json")))
        rec = build_dna_font(os.path.join(DP, "median-regular-600"),
                             g["per_char_regular"], g["cap_trace_px"],
                             os.path.join(OUT, "dna-clone-regular-600.ttf"),
                             family="PGCloneDNA", style="Regular", dpi=600)
        print(f"  regular-600: {rec['glyphs']} glyphs, IoU all {rec['iou_all']}, "
              f"cap {rec['cap_height_units']}u")
        self.assertEqual(rec["glyphs"], 37)
        self.assertAlmostEqual(rec["iou_all"], 0.958, delta=0.01)
        self.assertTrue(os.path.exists(os.path.join(OUT, "dna-clone-regular-600.ttf")))

    def test_bold_600(self):
        g = json.load(open(os.path.join(DP, "glyphs-weights-600.json")))
        rec = build_dna_font(os.path.join(DP, "median-bold-600"),
                             g["per_char_bold"], g["cap_trace_px"],
                             os.path.join(OUT, "dna-clone-bold-600.ttf"),
                             family="PGCloneDNA", style="Bold", dpi=600)
        print(f"  bold-600: {rec['glyphs']} glyphs, IoU all {rec['iou_all']}, "
              f"cap {rec['cap_height_units']}u")
        self.assertEqual(rec["glyphs"], 21)
        self.assertAlmostEqual(rec["iou_all"], 0.982, delta=0.01)
        self.assertTrue(os.path.exists(os.path.join(OUT, "dna-clone-bold-600.ttf")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
