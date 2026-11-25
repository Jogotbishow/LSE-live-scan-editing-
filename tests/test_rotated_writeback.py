"""Rotated-page write-back regression test (portable: no real fixtures).

Proves the 2026-11-24 Raviraj transplant fix: on a page with /Rotate 90
or 270, a span-edit patch must land at the right place, at the right
size, and UPRIGHT — not squashed to a hairline (the pre-fix failure:
a 1754x65 patch landed as 11x0.41 pt) and not upside-down (the first
fix attempt, rotate=360-rotation).

Method: build a synthetic scanned page (PIL text), wrap it in a PDF,
set the page rotation, run build_edited_pdf with one span edit, then
assert (a) the placed patch rect fills the expected unrotated rect and
(b) the rendered page shows the NEW text upright in the expected
display cell (ink correlation vs the patch itself: upright beats the
180-degree-rotated patch by a clear margin, and the old text is gone).
"""
import os
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fitz

from lse.writeback import (build_edited_pdf, composite_patches_for_page,
                           display_to_page_point)

LIB_REG = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
W, H = 2480, 3508          # A4 at 300 DPI
DPI = 300
OLD_TEXT = "Hello 123"
NEW_TEXT = "World 456"


def _make_page_image():
    """White A4 scan with one line of text; return (image, gray, box)."""
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(LIB_REG, size=80)
    x0, y0 = 400, 1000
    d.text((x0, y0), OLD_TEXT, font=font, fill=(0, 0, 0))
    bbox = d.textbbox((x0, y0), OLD_TEXT, font=font)
    box = [bbox[0], bbox[1], bbox[2], bbox[3]]
    gray = np.array(img.convert("L"))
    return img, gray, box


def _wrap_pdf(image, rotation, path):
    """Wrap the scan image in a one-page PDF with the given rotation."""
    doc = fitz.open()
    page = doc.new_page(width=595.28, height=841.89)
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, W, H))
    # feed the PIL bytes through a PNG stream
    import io
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    page.insert_image(page.rect, stream=buf.getvalue())
    page.set_rotation(rotation)
    doc.save(path)
    doc.close()
    return path


def _ink_mask(arr):
    return (arr < 120)


def _corr(a, b):
    """Cosine similarity of two boolean ink masks (same shape)."""
    af, bf = a.reshape(-1).astype(float), b.reshape(-1).astype(float)
    na, nb = np.linalg.norm(af), np.linalg.norm(bf)
    if na == 0 or nb == 0:
        return 0.0
    return float(af @ bf / (na * nb))


class TestRotatedWriteback(unittest.TestCase):
    def _run_case(self, rotation):
        tmp = tempfile.mkdtemp(prefix="lse-rot-")
        src = os.path.join(tmp, "src.pdf")
        out = os.path.join(tmp, "out.pdf")
        image, gray, box = _make_page_image()
        _wrap_pdf(image, rotation, src)

        edit = {"box": box, "line": 0, "row_label": "Test row",
                "old_text": OLD_TEXT, "new_text": NEW_TEXT, "bold": False,
                "ink_rgb": [0, 0, 0]}
        pages_edits = {0: {"image": image, "gray": gray, "dpi": DPI,
                           "edits": [edit]}}
        # the patch itself, for the upright reference
        patches, _c, recs = composite_patches_for_page(
            image, gray, [edit], dna_regular=None, dna_bold=None)
        patch = patches[0]
        rec = recs[0]
        patch_rect = rec["patch_rect"]  # display coords, 300 DPI

        manifest = build_edited_pdf(src, pages_edits, out,
                                    delivery_id="TEST-ROTATED",
                                    source_label="synthetic-rotated.pdf")
        self.assertEqual(len(manifest["edits"]), 1)

        doc = fitz.open(out)
        try:
            page = doc[0]
            self.assertEqual(page.rotation, rotation)
            # ---- (a) placed rect: must fill the expected unrotated rect
            uw, uh = page.mediabox.width, page.mediabox.height
            zoom = DPI / 72.0
            ax, ay = display_to_page_point(patch_rect[0], patch_rect[1],
                                           uw, uh, rotation, zoom)
            bx, by = display_to_page_point(patch_rect[2], patch_rect[3],
                                           uw, uh, rotation, zoom)
            exp = (min(ax, bx), min(ay, by), max(ax, bx), max(ay, by))
            placed = None
            for im in page.get_images(full=True):
                xref = im[0]
                if (im[2], im[3]) == patch.size:  # stored size == patch
                    placed = page.get_image_rects(xref)[0]
            self.assertIsNotNone(placed, "patch XObject not found")
            for got, want, name in zip(
                    (placed.x0, placed.y0, placed.x1, placed.y1), exp,
                    ("x0", "y0", "x1", "y1")):
                self.assertAlmostEqual(got, want, delta=2.0,
                                       msg=f"placed rect {name}: {got} != {want} "
                                           f"(rotation {rotation})")
            # a hairline is the pre-fix failure: height must be real
            self.assertGreater(placed.height, 10.0)
            # ---- (b) rendered upright in the display cell
            pix = page.get_pixmap(dpi=DPI)
            render = np.array(Image.frombytes("RGB", [pix.width, pix.height],
                                              pix.samples).convert("L"))
            x0, y0, x1, y1 = [int(round(v)) for v in patch_rect]
            crop = render[y0:y1, x0:x1]
            self.assertEqual(crop.shape, (patch.size[1], patch.size[0]),
                             "render crop must match patch size exactly")
            patch_ink = _ink_mask(np.array(patch.convert("L")))
            crop_ink = _ink_mask(crop)
            up = _corr(crop_ink, patch_ink)
            flipped = _corr(crop_ink, np.rot90(patch_ink, 2))
            print(f"  rotation {rotation}: placed {placed} upright corr "
                  f"{up:.2f} vs 180deg {flipped:.2f}")
            self.assertGreater(up, 0.5, "new text not visible upright")
            self.assertGreater(up - flipped, 0.2,
                               "rendered text is not upright (180deg wins?)")
            # old text must be gone: crop must NOT match the old text
            old_layer = Image.new("L", patch.size, 255)
            od = ImageDraw.Draw(old_layer)
            ofont = ImageFont.truetype(LIB_REG, size=80)
            od.text((10, 10), OLD_TEXT, font=ofont, fill=0)
            old_ink = _ink_mask(np.array(old_layer))
            self.assertLess(_corr(crop_ink, old_ink), up,
                            "old text still visible in the cell")
        finally:
            doc.close()

    def test_rotate_270(self):
        self._run_case(270)

    def test_rotate_90(self):
        self._run_case(90)

    def test_rotate_0_control(self):
        self._run_case(0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
