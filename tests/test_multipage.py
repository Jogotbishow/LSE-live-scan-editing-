"""Multi-page end-to-end — the main job.

Opens the REAL PG Aug (8 pp) and May (6 pp) PDFs at native 300 DPI,
edits words on SEVERAL pages (p1 Lot + WIDTH, plus one word on a later
page), saves the WHOLE document, and verifies:
  * untouched pages: image-stream SHA identical + rendered pixels
    identical (0 diff at 150 DPI);
  * edited pages: rendered diff confined to the patch rects;
  * the staging-DB delivery record: hash chain ok, v3 delivery hash
    ok, one label per page, p1 label carries the new Lot/WIDTH.
The Round 3 shared DB is never touched (a temp staging DB is used).
"""
import json
import os
import unittest

import cv2
import fitz
import numpy as np

import helpers
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

from helpers import DNA_BOLD, DNA_REG, PG_AUG, PG_MAY, STAGING, requires_real_fixtures
from lse import database
from lse.document import open_document
from lse.writeback import page_image_info, sha256_bytes


def _render(pdf, pageno, dpi):
    doc = fitz.open(pdf)
    try:
        pix = doc[pageno].get_pixmap(matrix=fitz.Matrix(dpi / 72.0, dpi / 72.0))
        return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    finally:
        doc.close()


def _image_shas(pdf):
    doc = fitz.open(pdf)
    try:
        out = []
        for p in range(len(doc)):
            out.append([im["stream_sha256"] for im in page_image_info(doc, p)])
        return out
    finally:
        doc.close()


def _find_word(doc_page, box, tol=6):
    """The canonical box, found in the page's seg within a few px
    (render drift shifts boxes by ~1 px — see test_segment.py)."""
    best, best_d = None, None
    for i, w in enumerate(doc_page.seg["words"]):
        d = max(abs(a - t) for a, t in zip(w["box"], box))
        if best_d is None or d < best_d:
            best, best_d = i, d
    assert best is not None and best_d <= tol, f"no word near {box}"
    return best


@requires_real_fixtures
class TestMultiPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work_aug = os.path.join(STAGING, "aug-doc")
        cls.work_may = os.path.join(STAGING, "may-doc")
        print("opening Aug (8 pp) ...")
        cls.doc_aug = open_document(PG_AUG, workdir=cls.work_aug,
                                    item="Blister Foil 25 Micron (PG Foils)",
                                    dna_regular=DNA_REG, dna_bold=DNA_BOLD)
        print("opening May (6 pp) ...")
        cls.doc_may = open_document(PG_MAY, workdir=cls.work_may,
                                    item="Blister Foil 20 Micron (PG Foils)",
                                    dna_regular=DNA_REG, dna_bold=DNA_BOLD)

    def test_page_counts_and_dpi(self):
        self.assertEqual(len(self.doc_aug), 8)
        self.assertEqual(len(self.doc_may), 6)
        for doc in (self.doc_aug, self.doc_may):
            for pg in doc.pages:
                self.assertEqual(pg.dpi, 300, f"{doc.source_label} p.{pg.number}")
                self.assertGreater(pg.n_words, 100)
        print(f"  Aug words/page: {[p.n_words for p in self.doc_aug.pages]}")
        print(f"  May words/page: {[p.n_words for p in self.doc_may.pages]}")
        # MY numbers on MY render (render drift, see test_segment.py):
        # canonical p1 was 302/302; mine is 308/307.
        self.assertEqual(self.doc_aug.page(1).n_words, 308)
        self.assertEqual(self.doc_may.page(1).n_words, 307)

    def test_gate_verdicts_recorded(self):
        for doc in (self.doc_aug, self.doc_may):
            for pg in doc.pages:
                self.assertIn(pg.gate_verdict, ("ALLOW", "REFUSE"))
                print(f"  {doc.source_label} p.{pg.number}: gate {pg.gate_verdict} "
                      f"(T1 {pg.gate_details['t1_flags']}, T2 {pg.gate_details['t2_flags']})")

    def test_open_edit_save_aug(self):
        doc = self.doc_aug
        lot_i = _find_word(doc.page(1), [533, 930, 631, 966])
        wid_i = _find_word(doc.page(1), [2088, 1282, 2178, 1310])
        e1 = doc.edit(1, lot_i, "207/9", old_text="206/7", row_label="Lot No.")
        e2 = doc.edit(1, wid_i, "781.5", old_text="780.0",
                      row_label="02. WIDTH — observation")
        # a later page, too (multi-page is the point): p2 word 10
        p2 = doc.page(2)
        w = p2.seg["words"][10]
        e3 = doc.edit(2, 10, "9999", old_text="", row_label="p2 word 10")
        print(f"  Aug edits: Lot {e1['new_text']}, WIDTH {e2['new_text']}, "
              f"p2 word10 box {e3['box']} -> '9999'")
        out_pdf = os.path.join(STAGING, "aug-edited.pdf")
        db_path = os.path.join(STAGING, "staging-aug.db")
        for p in (out_pdf, db_path):
            if os.path.exists(p):
                os.remove(p)
        manifest = doc.save(out_pdf, db_path=db_path, actor="qc-test",
                            client="PG Foils", item="Blister Foil 25 Micron (PG Foils)",
                            customer="Packfirm Limited")
        print(f"  Aug saved: {manifest['pdf_bytes']}B, pages {manifest['pages']} "
              f"(source {manifest['source_pages']}), edited {manifest['edited_pages']}, "
              f"delivery {manifest['delivery_number']}, labels {manifest['label_numbers']}")
        self.assertEqual(manifest["source_pages"], 8)
        self.assertEqual(manifest["edited_pages"], [1, 2])
        self.assertEqual(manifest["pages"], 8 + 2 + 1)  # source + audit + cert
        self.assertEqual(len(manifest["edits"]), 3)
        self._check_output(PG_AUG, out_pdf, edited_pages=[0, 1],
                           patch_boxes={0: [e1["box"], e2["box"]], 1: [e3["box"]]})
        self._check_db(db_path, manifest, n_pages=8, n_edits=3,
                       lot="207/9", width="781.5")

    def test_open_edit_save_may(self):
        doc = self.doc_may
        lot_i = _find_word(doc.page(1), [521, 913, 619, 950])
        wid_i = _find_word(doc.page(1), [2078, 1290, 2169, 1318])
        e1 = doc.edit(1, lot_i, "305/7", old_text="304/5", row_label="Lot No.")
        e2 = doc.edit(1, wid_i, "671.5", old_text="670.0",
                      row_label="02. WIDTH — observation")
        p3 = doc.page(3)
        w = p3.seg["words"][10]
        e3 = doc.edit(3, 10, "8888", old_text="", row_label="p3 word 10")
        print(f"  May edits: Lot {e1['new_text']}, WIDTH {e2['new_text']}, "
              f"p3 word10 box {e3['box']} -> '8888'")
        out_pdf = os.path.join(STAGING, "may-edited.pdf")
        db_path = os.path.join(STAGING, "staging-may.db")
        for p in (out_pdf, db_path):
            if os.path.exists(p):
                os.remove(p)
        manifest = doc.save(out_pdf, db_path=db_path, actor="qc-test",
                            client="PG Foils", item="Blister Foil 20 Micron (PG Foils)",
                            customer="Packfirm Limited")
        print(f"  May saved: {manifest['pdf_bytes']}B, pages {manifest['pages']} "
              f"(source {manifest['source_pages']}), edited {manifest['edited_pages']}, "
              f"delivery {manifest['delivery_number']}, labels {manifest['label_numbers']}")
        self.assertEqual(manifest["source_pages"], 6)
        self.assertEqual(manifest["edited_pages"], [1, 3])
        self.assertEqual(manifest["pages"], 6 + 2 + 1)
        self.assertEqual(len(manifest["edits"]), 3)
        self._check_output(PG_MAY, out_pdf, edited_pages=[0, 2],
                           patch_boxes={0: [e1["box"], e2["box"]], 2: [e3["box"]]})
        self._check_db(db_path, manifest, n_pages=6, n_edits=3,
                       lot="305/7", width="671.5")

    def _check_output(self, src_pdf, out_pdf, edited_pages, patch_boxes):
        # untouched pages: image streams byte-identical + pixels identical
        src_shas = _image_shas(src_pdf)
        out_shas = _image_shas(out_pdf)
        n_src = len(src_shas)
        for p in range(n_src):
            if p in edited_pages:
                continue
            self.assertEqual(out_shas[p], src_shas[p],
                             f"untouched p.{p + 1} image stream changed!")
            a = _render(src_pdf, p, 150)
            b = _render(out_pdf, p, 150)
            diff = int(np.abs(a.astype(int) - b.astype(int)).max())
            print(f"  untouched p.{p + 1}: stream SHA ok, max pixel diff {diff}")
            self.assertEqual(diff, 0, f"untouched p.{p + 1} pixels differ!")
        # edited pages: diff confined to patch rects (+8px) or the
        # freetext annotation mark at the top of the page
        # (Rect(w_pt-265, 6, w_pt-6, 26) in points).
        for p in edited_pages:
            a = _render(src_pdf, p, 300)
            b = _render(out_pdf, p, 300)
            doc = fitz.open(src_pdf)
            try:
                w_pt = doc[p].rect.width
            finally:
                doc.close()
            ann = ((w_pt - 265) * 300 / 72 - 4, 0,
                   w_pt * 300 / 72, 26 * 300 / 72 + 4)
            diff = (np.abs(a.astype(int) - b.astype(int)).max(axis=2) > 12).astype(np.uint8)
            n, _, stats, _ = cv2.connectedComponentsWithStats(diff, 8)
            blobs = [(stats[i, 0], stats[i, 1], stats[i, 2], stats[i, 3], stats[i, 4])
                     for i in range(1, n) if stats[i, 4] >= 20]
            boxes = patch_boxes[p]
            disp = [(bx0 - 8, by0 - 8, bx1 + 8, by1 + 8) for bx0, by0, bx1, by1 in boxes]

            def _inside(bl):
                bx0, by0, bw, bh, _ = bl
                bx1, by1 = bx0 + bw, by0 + bh
                if bx0 >= ann[0] and by0 >= ann[1] and bx1 <= ann[2] and by1 <= ann[3]:
                    return True  # the freetext annotation mark
                return any(bx0 >= d[0] - 1 and by0 >= d[1] - 1 and bx1 <= d[2] + 1
                           and by1 <= d[3] + 1 for d in disp)

            bad = [bl for bl in blobs if not _inside(bl)]
            print(f"  edited p.{p + 1}: {len(blobs)} diff blobs >=20px, outside patches: {len(bad)}")
            self.assertGreaterEqual(len(blobs), 1)
            self.assertEqual(bad, [], f"diff outside patches on p.{p + 1}: {bad}")

    def _check_db(self, db_path, manifest, n_pages, n_edits, lot, width):
        c = database.connect(db_path)
        try:
            ok, n, bad = database.verify_chain(c)
            print(f"  DB chain: ok={ok}, entries={n}, first_bad={bad}")
            self.assertTrue(ok)
            self.assertGreaterEqual(n, 2)
            did = manifest["delivery_id"]
            ok3, msg = database.verify_delivery3(c, did)
            print(f"  DB delivery v3: ok={ok3} ({msg})")
            self.assertTrue(ok3, msg)
            d = database.get_delivery(c, did)
            self.assertEqual(d["number"], manifest["delivery_number"])
            self.assertEqual(len(d["pages"]), n_pages)
            self.assertEqual(len(d["labels"]), n_pages)
            self.assertEqual(len(d["edits"]), n_edits)
            lab1 = database.resolve_label_for_page(c, did, 1)
            print(f"  p1 label: {lab1['number']} batch={lab1['batch_no']} width={lab1['width_mm']}")
            self.assertEqual(lab1["batch_no"], lot)
            self.assertEqual(lab1["width_mm"], width)
            self.assertEqual(d["label_ref"], lab1["id"])
        finally:
            c.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
