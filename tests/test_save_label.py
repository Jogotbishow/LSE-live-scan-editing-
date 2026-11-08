"""Save -> label (Domino) wiring — end-to-end verification.

Proves, with the repo-copy code (``lse/`` + ``label/``, not the
prototype), that ``Document.save_with_label()`` runs ``save()``
unchanged and then builds one real label per edited page from that
page's own edited values:

  * ACME synthetic (no DB): Batch / Lot tail pieces + Thickness
    edited on the live page -> the label shows the EDITED values
    (old values only in the audit line), no demo values, label_no
    unfilled (never auto-generated).
  * Real PG AUGUST-2026 p.1 (read-only, worked in /tmp only): Lot +
    WIDTH edited -> the label shows the EDITED values, carries the
    DB-issued label_no, and is printable; the DB record is the same
    as a plain ``save()`` (chain ok, v3 hash ok).

The ACME hyphenated values (``ACME-2026-0001``, ``ACME-LOT-77``)
are split by the segmenter into three hyphen-separated pieces each
(verified against the ground-truth word boxes + a visual read of the
rows); the tests edit the distinctive TAIL piece of each value
(``0001`` -> ``0002``, ``77`` -> ``78``) and the whole Thickness
word (``25.2`` -> ``25.4``), and say so — the label carries the
edited piece, not a reassembled whole value (no reassembly is
attempted anywhere in the wiring).

Real PG PDFs are READ-ONLY inputs (SHA-256 checked before/after);
the Round 3 shared DB is never touched (a temp staging DB is used).
"""
import hashlib
import json
import os
import unittest

import fitz

import helpers
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

from helpers import DNA_BOLD, DNA_REG, PG_AUG, STAGING, requires_real_fixtures
from lse import database
from lse.document import (_field_for_row_label,
                          edited_values_from_manifest, open_document)

ACME_PDF = "/home/hatch/workspace/gravora-review/gravora-app/fixtures/synthetic-supplier-coa/synthetic-supplier-coa.pdf"
ACME_GT = "/home/hatch/workspace/gravora-review/gravora-app/fixtures/synthetic-supplier-coa/ground-truth-words.json"


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _find_word(doc_page, box, tol=6):
    """The canonical box, found in the page's seg within a few px."""
    best, best_d = None, None
    for i, w in enumerate(doc_page.seg["words"]):
        d = max(abs(a - t) for a, t in zip(w["box"], box))
        if best_d is None or d < best_d:
            best, best_d = i, d
    assert best is not None and best_d <= tol, \
        f"no word near {box} (best {best} d={best_d})"
    return best


def _pt_to_px(box_pt):
    return [round(c * 300 / 72) for c in box_pt]


class TestRowLabelMapping(unittest.TestCase):
    def test_field_for_row_label(self):
        cases = {
            "Lot No.": "lot",
            "02. WIDTH — observation": "width",
            "Batch No.": "batch",
            "Supplier Batch No": "batch",
            "Thickness": "thickness",
            "Material Code": "material_code",
            "Version No.": "version",
            "Gross Weight": "gross_weight",
            "Net Weight": "net_weight",
            "Number of Packs": "packs",
            "Expiry Date": "expiry_date",
            "Mfg Date": "mfg_date",
            "Date": "date",
            "Customer": "customer",
            "p2 word 10": None,
            "": None,
        }
        for label, want in cases.items():
            self.assertEqual(_field_for_row_label(label), want, label)

    def test_edited_values_from_manifest(self):
        manifest = {
            "delivery_id": "LSE-DEL-test",
            "delivery_number": "LSE-0009",
            "label_numbers": ["LBL-0001", "LBL-0002"],
            "edits": [
                {"page": 1, "box": [533, 930, 631, 966],
                 "row_label": "Lot No.", "old_text": "206/7",
                 "new_text": "207/9"},
                {"page": 1, "box": [2088, 1282, 2178, 1310],
                 "row_label": "02. WIDTH — observation",
                 "old_text": "780.0", "new_text": "781.5"},
                {"page": 2, "box": [100, 100, 200, 200],
                 "row_label": "Roll No.", "old_text": "R-1",
                 "new_text": "R-2"},
            ],
        }
        vals = edited_values_from_manifest(
            manifest, item="Blister Foil 25 Micron",
            customer="Packfirm Limited", source_stem="aug",
            dpi_by_page={1: 300, 2: 150})
        self.assertEqual(len(vals), 2)  # one per EDITED page only
        p1, p2 = vals
        self.assertEqual(p1["page_key"], "aug-p1")
        self.assertEqual(p1["page_label"], "aug p.1")
        self.assertEqual(p1["label_no"], "LBL-0001")  # page order
        self.assertEqual(p2["label_no"], "LBL-0002")
        self.assertEqual(p1["delivery"], "LSE-0009")
        self.assertEqual(p1["lot"], {"old": "206/7", "new": "207/9",
                                     "box300": [533, 930, 631, 966]})
        self.assertEqual(p1["width"]["new"], "781.5")
        # unmapped row_label -> extra_fields under its own label,
        # never dropped, never forced into lot/width/batch
        self.assertEqual(p2["extra_fields"]["Roll No."],
                         {"old": "R-1", "new": "R-2",
                          "box300": [200, 200, 400, 400]})  # 150 DPI scaled
        self.assertNotIn("lot", p2)
        self.assertNotIn("width", p2)

    def test_edited_values_no_db_no_label_no(self):
        manifest = {"delivery_id": "LSE-DEL-x", "edits": [
            {"page": 1, "box": [0, 0, 10, 10], "row_label": "Lot No.",
             "old_text": "A", "new_text": "B"}]}
        vals = edited_values_from_manifest(manifest, source_stem="s")
        self.assertIsNone(vals[0]["label_no"])  # never auto-generated
        self.assertIsNone(vals[0]["delivery"])


@requires_real_fixtures
class TestSaveLabel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work_aug = os.path.join(STAGING, "aug-doc-label")
        print("opening Aug (8 pp) ...")
        cls.doc_aug = open_document(PG_AUG, workdir=cls.work_aug,
                                    item="Blister Foil 25 Micron (PG Foils)",
                                    dna_regular=DNA_REG, dna_bold=DNA_BOLD)
        cls.sha_aug_before = _sha256(PG_AUG)
        cls.sha_acme_before = _sha256(ACME_PDF)

    def test_acme_save_with_label(self):
        doc = open_document(
            ACME_PDF, workdir=os.path.join(STAGING, "acme-doc-label"),
            item="Blister Foil 25 Micron",
            dna_regular=DNA_REG, dna_bold=DNA_BOLD)
        self.assertEqual(len(doc), 1)
        self.assertEqual(doc.page(1).dpi, 300)
        p1 = doc.page(1)
        # Tail pieces of the hyphen-split values (see module docstring),
        # plus the whole Thickness word — boxes from ground truth.
        batch_i = _find_word(p1, [780, 885, 880, 922])      # "0001"
        lot_i = _find_word(p1, [688, 981, 740, 1016])        # "77"
        gt = json.load(open(ACME_GT))
        thick_box = _pt_to_px([w for w in gt["words"]
                               if w["text"] == "25.2"][0]["box_pt"])
        thick_i = _find_word(p1, thick_box, tol=25)          # "25.2"
        doc.edit(1, batch_i, "0002", old_text="0001",
                 row_label="Batch No.")
        doc.edit(1, lot_i, "78", old_text="77", row_label="Lot No.")
        doc.edit(1, thick_i, "25.4", old_text="25.2",
                 row_label="Thickness")
        out_pdf = os.path.join(STAGING, "acme-edited-label.pdf")
        label_dir = os.path.join(STAGING, "labels-acme")
        for p in (out_pdf,):
            if os.path.exists(p):
                os.remove(p)
        manifest = doc.save_with_label(
            out_pdf, label_dir, item="Blister Foil 25 Micron",
            customer="FAKE PHARMA LTD", supplier="ACME FOILS LTD")
        # save() part unchanged: whole doc, 1 edited page, 3 edits
        self.assertEqual(manifest["source_pages"], 1)
        self.assertEqual(manifest["edited_pages"], [1])
        self.assertEqual(len(manifest["edits"]), 3)
        self.assertEqual(manifest["pages"], 1 + 1 + 1)  # src + audit + cert
        self.assertEqual(len(manifest["labels"]), 1)
        lab = manifest["labels"][0]
        print(f"  ACME label: {lab['page_key']} lot/batch/thickness "
              f"-> {[f for f in lab['fields'] if f['key'] in ('lot', 'batch', 'thickness')]}")
        self.assertEqual(lab["page_key"], "synthetic-supplier-coa-p1")
        self.assertEqual(lab["edited_pdf_sha256"], manifest["pdf_sha256"])
        self.assertIsNone(lab["label_no"])  # no DB -> never invented
        self.assertFalse(lab["is_printable"])  # WIDTH + label_no unfilled
        self.assertIn("width", lab["unfilled_fields"])
        self.assertIn("label_no", lab["unfilled_fields"])
        self.assertEqual(lab["refused_demo"], [])
        with open(lab["label_html"], encoding="utf-8") as fh:
            html = fh.read()
        # EDITED values are the value cells ...
        self.assertIn("<b>78</b>", html)        # Lot tail piece
        self.assertIn("<b>0002</b>", html)      # Batch tail piece
        self.assertIn("<b>25.4</b>", html)      # Thickness
        # ... old values never a value cell, only in the audit line
        self.assertNotIn("<b>77</b>", html)
        self.assertNotIn("<b>0001</b>", html)
        self.assertNotIn("<b>25.2</b>", html)
        self.assertIn("77 → 78", html)
        self.assertIn("0001 → 0002", html)
        self.assertIn("25.2 → 25.4", html)
        # Lot and Batch stay separate rows (no merged value)
        self.assertIn("Batch / Lot No.", html)
        # label PDF: 100mm x 160mm
        self.assertTrue(lab["label_pdf"]
                        and os.path.exists(lab["label_pdf"]))
        ldoc = fitz.open(lab["label_pdf"])
        try:
            r = ldoc[0].rect
            self.assertAlmostEqual(r.width, 100 * 72 / 25.4, delta=1)
            self.assertAlmostEqual(r.height, 160 * 72 / 25.4, delta=1)
        finally:
            ldoc.close()
        # label manifest JSON echoes the edited values, per page
        with open(lab["manifest"], encoding="utf-8") as fh:
            lman = json.load(fh)
        self.assertEqual(lman["edited_values"]["lot"]["new"], "78")
        self.assertEqual(lman["edited_values"]["batch"]["new"], "0002")
        self.assertEqual(lman["edited_values"]["thickness"]["new"], "25.4")
        # the edited PDF itself is a real save: audit + certificate
        _check = fitz.open(out_pdf)
        try:
            self.assertEqual(len(_check), 3)
        finally:
            _check.close()
        self.assertEqual(_sha256(ACME_PDF), self.sha_acme_before)

    def test_pg_aug_p1_save_with_label(self):
        doc = self.doc_aug
        lot_i = _find_word(doc.page(1), [533, 930, 631, 966])
        wid_i = _find_word(doc.page(1), [2088, 1282, 2178, 1310])
        doc.edit(1, lot_i, "207/9", old_text="206/7", row_label="Lot No.")
        doc.edit(1, wid_i, "781.5", old_text="780.0",
                 row_label="02. WIDTH — observation")
        out_pdf = os.path.join(STAGING, "aug-edited-label.pdf")
        db_path = os.path.join(STAGING, "staging-aug-label.db")
        label_dir = os.path.join(STAGING, "labels-aug")
        for p in (out_pdf, db_path):
            if os.path.exists(p):
                os.remove(p)
        manifest = doc.save_with_label(
            out_pdf, label_dir, db_path=db_path, actor="qc-test",
            client="PG Foils", item="Blister Foil 25 Micron (PG Foils)",
            customer="Packfirm Limited")
        # save() part: same as a plain save (checked against a second
        # plain save below); whole doc, 1 edited page, 2 edits
        self.assertEqual(manifest["source_pages"], 8)
        self.assertEqual(manifest["edited_pages"], [1])
        self.assertEqual(manifest["pages"], 8 + 1 + 1)
        self.assertEqual(len(manifest["edits"]), 2)
        self.assertEqual(manifest["label_numbers"][0], "LBL-0001")
        self.assertEqual(len(manifest["labels"]), 1)
        lab = manifest["labels"][0]
        print(f"  Aug p1 label: {lab['page_key']} "
              f"label_no={lab['label_no']} printable={lab['is_printable']}")
        self.assertEqual(lab["page_key"],
                         "PG AUGUST-2026 (25mic) COA-p1")
        self.assertEqual(lab["label_no"], "LBL-0001")
        self.assertEqual(lab["edited_pdf_sha256"], manifest["pdf_sha256"])
        self.assertTrue(lab["is_printable"])  # lot + width filled, LBL given
        self.assertEqual(lab["refused_demo"], [])
        with open(lab["label_html"], encoding="utf-8") as fh:
            html = fh.read()
        self.assertIn("<b>207/9</b>", html)       # Lot, EDITED
        self.assertIn("<b>781.5 mm</b>", html)    # WIDTH, EDITED
        self.assertNotIn("<b>206/7</b>", html)
        self.assertNotIn("<b>780.0", html)
        self.assertIn("206/7 → 207/9", html)
        self.assertIn("780.0 → 781.5", html)
        # Batch row stays visibly unfilled: Lot and Batch are separate
        self.assertIn("— পূরণ হয়নি —", html)
        # no leak of May values into the Aug p1 label
        for leak in ("305/7", "304/5", "671.5", "670.0"):
            self.assertNotIn(leak, html)
        self.assertTrue(lab["label_pdf"]
                        and os.path.exists(lab["label_pdf"]))
        ldoc = fitz.open(lab["label_pdf"])
        try:
            r = ldoc[0].rect
            self.assertAlmostEqual(r.width, 100 * 72 / 25.4, delta=1)
            self.assertAlmostEqual(r.height, 160 * 72 / 25.4, delta=1)
            self.assertIn("207/9", ldoc[0].get_text())
            self.assertIn("781.5", ldoc[0].get_text())
        finally:
            ldoc.close()
        # DB record is exactly what plain save() writes: chain ok,
        # v3 hash ok, p1 label carries the new Lot/WIDTH
        c = database.connect(db_path)
        try:
            ok, n, bad = database.verify_chain(c)
            print(f"  DB chain: ok={ok}, entries={n}, first_bad={bad}")
            self.assertTrue(ok)
            ok3, msg = database.verify_delivery3(c, manifest["delivery_id"])
            self.assertTrue(ok3, msg)
            lab1 = database.resolve_label_for_page(
                c, manifest["delivery_id"], 1)
            self.assertEqual(lab1["number"], "LBL-0001")
            self.assertEqual(lab1["batch_no"], "207/9")
            self.assertEqual(lab1["width_mm"], "781.5")
        finally:
            c.close()
        # save() itself is untouched by the wiring: a second plain
        # save() of the same edits carries the same patch records and
        # no "labels" key
        out2 = os.path.join(STAGING, "aug-edited-label-plain.pdf")
        db2 = os.path.join(STAGING, "staging-aug-label-plain.db")
        for p in (out2, db2):
            if os.path.exists(p):
                os.remove(p)
        manifest2 = doc.save(out2, db_path=db2, actor="qc-test",
                             client="PG Foils",
                             item="Blister Foil 25 Micron (PG Foils)",
                             customer="Packfirm Limited")
        self.assertNotIn("labels", manifest2)
        self.assertEqual(manifest2["edits"], manifest["edits"])
        self.assertEqual(manifest2["edited_pages"], [1])
        self.assertEqual(_sha256(PG_AUG), self.sha_aug_before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
