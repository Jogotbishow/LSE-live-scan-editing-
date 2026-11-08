"""Caps tests — proposal B (DECISIONS.md): never force caps.

R18 measured (re-measured here, not assumed): at 37 px cap height
(fs0 = 37/0.70 = 52.9 px) "AND" needs 122 px in DejaVu Bold (+58 over
a 64 px slot) and 86 px in the narrowest font, Noto Sans
ExtraCondensed Bold (+22); it fits only a 92 px slot. The Document
DNA clone's own estimate agrees (87-91 px).
"""
import os
import unittest

import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

from helpers import DNA_BOLD, DNA_REG, requires_real_fixtures
from lse.caps import fit_caps, measure_width

NOTO_EXCOND_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-ExtraCondensedBold.ttf"
DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FS0 = round(37 / 0.70, 1)  # 52.9 px at 37 px cap height


@requires_real_fixtures
class TestCapsRemeasure(unittest.TestCase):
    def test_and_widths_remeasured(self):
        # Ruler note: these are PIL getlength() widths at int(round(fs0))
        # — the SAME ruler the write-back uses. R18's caps_test.py used
        # a different ruler and reported DejaVu 122 / ExtraCondensed 86 /
        # DNA-estimate 87-91 (ink-based). Direct rendering here says
        # 129 / 90 / 106. The numbers differ; the CONCLUSION does not:
        # every font needs far more than a 64 px slot for caps "AND".
        w_deja = measure_width("AND", DEJAVU_BOLD, FS0)
        w_cond = measure_width("AND", NOTO_EXCOND_BOLD, FS0)
        w_dna = measure_width("AND", DNA_BOLD, FS0)
        print(f"  'AND' at {FS0}px: DejaVu Bold {w_deja:.0f}px, "
              f"ExtraCondensed Bold {w_cond:.0f}px, DNA Bold {w_dna:.0f}px")
        self.assertGreater(w_deja, 115)
        self.assertAlmostEqual(w_cond, 86, delta=8)
        self.assertGreater(w_dna, 100)
        for w in (w_deja, w_cond, w_dna):
            self.assertGreater(w, 64, "a caps font fits the 64px slot?!")


@requires_real_fixtures
class TestCapsProposalB(unittest.TestCase):
    def test_caps_in_64px_slot_suggests_lowercase(self):
        d = fit_caps("AND", NOTO_EXCOND_BOLD, FS0, 64)
        print(f"  AND @64px: {d}")
        self.assertFalse(d["fits"])
        self.assertEqual(d["action"], "suggest_lowercase")
        self.assertEqual(d["suggestion"], "and")

    def test_caps_in_92px_slot_fits(self):
        d = fit_caps("AND", NOTO_EXCOND_BOLD, FS0, 92)
        self.assertTrue(d["fits"])
        self.assertEqual(d["action"], "caps")
        self.assertEqual(d["text"], "AND")

    def test_lowercase_suggestion_renderable_via_width_fit(self):
        # Honest correction to the naive claim "lowercase fits 64px":
        # at fs0 even "and" is 77-83px in every font — it does NOT fit
        # at cap-height size either. The mechanism-grounded difference
        # is the width-fit floor (0.75x): "and" in the DNA clone renders
        # 62.1px at the floor — inside a 64px box — while caps "AND"
        # renders 79.9px at the floor — outside it.
        d = fit_caps("AND", DNA_REG, FS0, 64)
        print(f"  AND->and suggestion: scale {d['suggestion_scale']}, "
              f"fits_via_width_fit={d['suggestion_fits_via_width_fit']}")
        self.assertEqual(d["suggestion"], "and")
        self.assertTrue(d["suggestion_fits_via_width_fit"])
        self.assertAlmostEqual(d["suggestion_scale"], 0.75, delta=0.02)
        caps_scale = (0.97 * 64) / measure_width("AND", DNA_REG, FS0)
        print(f"  caps 'AND' needed scale: {caps_scale:.3f} (floor 0.75)")
        self.assertLess(caps_scale, 0.75)

    def test_dna_caps_in_64px_slot_suggests_lowercase(self):
        d = fit_caps("AND", DNA_BOLD, FS0, 64)
        self.assertFalse(d["fits"])
        self.assertEqual(d["suggestion"], "and")

    def test_non_caps_overflow_has_no_case_suggestion(self):
        d = fit_caps("123456789012345", DEJAVU_BOLD, FS0, 64)
        self.assertFalse(d["fits"])
        self.assertIsNone(d["suggestion"])

    def test_digit_only_text_is_as_typed(self):
        # Regression: "207/9" (a Lot number) was once mislabelled
        # "suggest_lowercase" in the audit record. Digit-only text has
        # no cased letter, so it is non-caps and renders as typed.
        d = fit_caps("207/9", DNA_REG, FS0, 64)
        self.assertEqual(d["action"], "as_typed")
        self.assertEqual(d["text"], "207/9")
        self.assertIsNone(d["suggestion"])

    def test_widened_slot_only_with_confirmation(self):
        d = fit_caps("AND", NOTO_EXCOND_BOLD, FS0, 64, allow_widen_slot=True)
        self.assertTrue(d["fits"])
        self.assertEqual(d["action"], "caps_widened_slot")


if __name__ == "__main__":
    unittest.main(verbosity=2)
