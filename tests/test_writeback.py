"""Write-back unit tests — one patch at native DPI + caps enforcement
in the retype path.
"""
import unittest

import numpy as np
from PIL import Image

import helpers
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

from helpers import DNA_BOLD, DNA_REG, PG_AUG, requires_real_fixtures
from lse.segment import segment_array
from lse.writeback import (CapsDoesNotFitError, build_patch,
                           measure_ink_bbox, render_page)
import fitz


def _nearest_box(seg, target, tol=6):
    """The canonical box, found in MY seg within a few px (render
    drift shifts boxes by ~1 px — see test_segment.py)."""
    best, best_d = None, None
    for w in seg["words"]:
        d = max(abs(a - t) for a, t in zip(w["box"], target))
        if best_d is None or d < best_d:
            best, best_d = w["box"], d
    assert best is not None and best_d <= tol, f"no box near {target}"
    return best


@requires_real_fixtures
class TestBuildPatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        doc = fitz.open(PG_AUG)
        try:
            cls.image, cls.gray, cls.dpi = render_page(doc, 0)
        finally:
            doc.close()
        cls.seg = segment_array(
            __import__("cv2").cvtColor(np.array(cls.image), __import__("cv2").COLOR_RGB2BGR),
            image_name="aug p.1")
        # canonical Lot / WIDTH boxes, located in MY seg (1 px drift)
        cls.lot_box = _nearest_box(cls.seg, [533, 930, 631, 966])
        cls.wid_box = _nearest_box(cls.seg, [2088, 1282, 2178, 1310])

    def test_measure_ink_bbox(self):
        bbox, touched = measure_ink_bbox(self.gray, self.lot_box)
        print(f"  Lot ink bbox: {bbox}, touched={touched}")
        self.assertIsNotNone(bbox)
        self.assertLessEqual(bbox[0], self.lot_box[2])
        self.assertGreaterEqual(bbox[2], self.lot_box[0])

    def test_lot_patch(self):
        box = self.lot_box
        edit = {"box": box, "line": 0, "row_label": "Lot No.",
                "old_text": "206/7", "new_text": "207/9", "bold": False,
                "ink_rgb": [0, 0, 0]}
        patch, clean, rec = build_patch(self.image, self.gray, edit["box"], edit,
                                        dna_regular=DNA_REG, dna_bold=DNA_BOLD)
        w, h = box[2] - box[0], box[3] - box[1]
        print(f"  Lot patch: {patch.size}, font {rec['font']}, "
              f"fs {rec['font_size_px']}, orig ink {rec['orig_ink_bbox']}")
        self.assertEqual(patch.size, (w + 6, h + 6))  # box + 2x3px margin
        self.assertEqual(rec["font"], "Document DNA Regular")
        self.assertEqual(rec["new_text"], "207/9")
        # digit-only text is non-caps: rendered as typed, never routed
        # to the lowercase suggestion (caps.py regression check)
        self.assertEqual(rec["caps_action"], "as_typed")
        # the clean patch must have no ink left inside the word box
        import cv2
        cg = np.array(clean.convert("L"))
        roi = cg[3:3 + h, 3:3 + w]
        self.assertLess(int((roi < 210).sum()), 50)

    def test_caps_strict_raises(self):
        # a 64px-wide slot, caps "AND" at the document's cap height.
        # NOTE: this box is synthetic (the R18 L41 'and' slot) — it is
        # not a word in the Aug p1 seg; build_patch only needs the
        # image + box, so the caps check does not depend on the seg.
        box = [809, 1427, 873, 1464]  # the R18 L41 'and' box (64x37)
        edit = {"box": box, "line": 0, "row_label": "L41",
                "old_text": "and", "new_text": "AND", "bold": True,
                "ink_rgb": [0, 0, 0]}
        with self.assertRaises(CapsDoesNotFitError) as ctx:
            build_patch(self.image, self.gray, box, edit,
                        dna_regular=DNA_REG, dna_bold=DNA_BOLD,
                        caps_mode="strict")
        print(f"  strict caps error: {ctx.exception} "
              f"(suggestion {ctx.exception.suggestion!r})")
        self.assertEqual(ctx.exception.suggestion, "and")

    def test_caps_suggest_lowercase_renders(self):
        box = [809, 1427, 873, 1464]
        edit = {"box": box, "line": 0, "row_label": "L41",
                "old_text": "and", "new_text": "AND", "bold": True,
                "ink_rgb": [0, 0, 0]}
        _patch, _clean, rec = build_patch(
            self.image, self.gray, box, edit,
            dna_regular=DNA_REG, dna_bold=DNA_BOLD,
            caps_mode="suggest_lowercase")
        print(f"  suggest_lowercase: typed 'AND' -> rendered {rec['new_text']!r}, "
              f"caps_action {rec['caps_action']}")
        self.assertEqual(rec["new_text"], "and")
        self.assertEqual(rec["typed_text"], "AND")
        self.assertEqual(rec["caps_action"], "suggest_lowercase")


if __name__ == "__main__":
    unittest.main(verbosity=2)
