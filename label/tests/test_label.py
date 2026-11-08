"""Tests for the LSE label package (stdlib unittest).

Run from label/:  python -m unittest discover -s tests -v
PDF tests skip gracefully when PyMuPDF is not installed.
"""
import importlib.util
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from label import (  # noqa: E402
    build_label,
    build_label_html,
    build_label_pdf,
    build_labels_for_pages,
    edited_values_from_save_record,
    save_with_label,
)

HAS_FITZ = importlib.util.find_spec("fitz") is not None

ACME_EDITED = {
    "page_key": "acme-p1",
    "page_label": "ACME p.1",
    "page_no": 1,
    "delivery": "LSE-ACME-0001",
    "delivery_id": "LSE-DEL-acme0001",
    "label_no": "LBL-ACME-0001",
    "item": "Blister Foil 25 Micron",
    "product": "Blister Foil 25 Micron",
    "customer": "FAKE PHARMA LTD",
    "supplier": "ACME FOILS LTD",
    "batch": {"old": "ACME-2026-0001", "new": "ACME-2026-0002",
              "box300": [486, 868, 889, 937]},
    "lot": {"old": "ACME-LOT-77", "new": "ACME-LOT-78",
            "box300": [411, 962, 742, 1031]},
    "width": {"old": "25.2", "new": "25.4"},
    "thickness": {"old": "25.2", "new": "25.4"},
    "date": "07.11.2026",
    "edits": [
        {"field": "lot", "old": "ACME-LOT-77", "new": "ACME-LOT-78"},
        {"field": "batch", "old": "ACME-2026-0001", "new": "ACME-2026-0002"},
        {"field": "width", "old": "25.2", "new": "25.4"},
    ],
}

PG_AUG_P1 = {
    "page_key": "aug-p1",
    "page_label": "Aug p.1",
    "page_no": 1,
    "delivery": "LSE-0008",
    "delivery_id": "LSE-DEL-a0239ccdaf77405f89a99dc57c99adcf",
    "label_no": "LBL-0001",
    "item": "Blister Foil 25 Micron (PG Foils)",
    "customer": "Packfirm Limited",
    "lot": {"old": "206/7", "new": "207/9", "box300": [533, 930, 631, 966]},
    "width": {"old": "780.0", "new": "781.5",
              "box300": [2088, 1282, 2178, 1310]},
    "edits": [
        {"field": "lot", "old": "206/7", "new": "207/9"},
        {"field": "width", "old": "780.0", "new": "781.5"},
    ],
}


class TestBuildLabel(unittest.TestCase):
    def test_acme_edited_values_win(self):
        res = build_label(ACME_EDITED)
        # Edited values in the bold value cells...
        self.assertIn("<b>ACME-LOT-78</b>", res.html)
        self.assertIn("<b>ACME-2026-0002</b>", res.html)
        self.assertIn("<b>25.4 mm</b>", res.html)
        # ...old values only in the audit line, never as a value cell.
        self.assertNotIn("<b>ACME-LOT-77</b>", res.html)
        self.assertNotIn("<b>ACME-2026-0001</b>", res.html)
        self.assertIn("ACME-LOT-77 → ACME-LOT-78", res.html)
        self.assertEqual(res.page_key, "acme-p1")
        self.assertEqual(res.label_no, "LBL-ACME-0001")

    def test_pg_aug_p1_values(self):
        res = build_label(PG_AUG_P1)
        self.assertIn("<b>207/9</b>", res.html)
        self.assertIn("<b>781.5 mm</b>", res.html)
        self.assertIn("LBL-0001", res.html)
        self.assertIn("LSE-0008", res.html)
        self.assertIn("206/7 → 207/9", res.html)
        self.assertIn("780.0 → 781.5", res.html)
        # No May page values leak into the Aug p.1 label.
        for leak in ("305/7", "283/7", "282/7", "671.5", "721.5", "771.5"):
            self.assertNotIn(leak, res.html)

    def test_missing_value_is_flagged_never_faked(self):
        vals = dict(PG_AUG_P1)
        vals.pop("lot")
        res = build_label(vals)
        self.assertIn("— পূরণ হয়নি —", res.html)
        self.assertIn("lot", res.unfilled_fields)
        self.assertFalse(res.is_printable)
        # Nothing invented: no other lot-like value appears as a value.
        self.assertNotIn("<b>207/9</b>", res.html)

    def test_missing_label_no_is_unfilled_not_invented(self):
        vals = dict(PG_AUG_P1)
        vals.pop("label_no")
        res = build_label(vals)
        self.assertIsNone(res.label_no)
        self.assertIn("label_no", res.unfilled_fields)
        self.assertFalse(res.is_printable)

    def test_demo_value_refused(self):
        # Phase 1.1's known template-demo values must never reach a label.
        vals = dict(PG_AUG_P1)
        vals["material_code"] = "12000905"
        vals["expiry_date"] = "15.06.2028"
        res = build_label(vals, demo_values={"12000905", "15.06.2028",
                                             "2", "/ 6", " kg"})
        self.assertIn("material_code", res.refused_demo)
        self.assertIn("expiry_date", res.refused_demo)
        self.assertNotIn("<b>12000905</b>", res.html)
        self.assertNotIn("15.06.2028", res.html)
        self.assertIn("material_code", res.unfilled_fields)

    def test_lot_and_batch_never_conflate(self):
        vals = dict(PG_AUG_P1)
        vals.pop("batch", None)
        res = build_label(vals)
        by_key = {f["key"]: f for f in res.fields}
        self.assertFalse(by_key["batch"]["filled"])
        self.assertTrue(by_key["lot"]["filled"])

    def test_draft_default_and_final(self):
        res = build_label(PG_AUG_P1)
        self.assertTrue(res.is_draft)
        self.assertIn("খসড়া", res.html)
        self.assertNotIn("QC PASSED", res.html)
        res2 = build_label(PG_AUG_P1, draft=False)
        self.assertFalse(res2.is_draft)
        self.assertIn("QC PASSED", res2.html)

    def test_html_escaping(self):
        vals = dict(PG_AUG_P1)
        vals["item"] = '<script>alert("x")</script>'
        res = build_label(vals)
        self.assertNotIn("<script>alert", res.html)
        self.assertIn("&lt;script&gt;", res.html)

    def test_requires_page_key_and_label(self):
        with self.assertRaises(ValueError):
            build_label({"page_key": "x"})
        with self.assertRaises(ValueError):
            build_label({"page_label": "p.1"})
        with self.assertRaises(ValueError):
            build_label({}, template="nope")

    def test_stale_edits_list_cannot_leak_other_page_values(self):
        # A copied record whose edits list still holds another page's
        # values: the audit line must drop them (fields rule).
        vals = dict(PG_AUG_P1)
        vals.update({"page_key": "may-p1", "page_label": "May p.1",
                     "lot": {"old": "304/5", "new": "305/7"},
                     "width": {"old": "670.0", "new": "671.5"}})
        res = build_label(vals)
        self.assertNotIn("206/7", res.html)
        self.assertNotIn("207/9", res.html)
        self.assertNotIn("780.0", res.html)
        self.assertNotIn("781.5", res.html)
        self.assertIn("304/5 → 305/7", res.html)

    def test_printable_when_required_filled(self):
        res = build_label(PG_AUG_P1, draft=False)
        self.assertTrue(res.is_printable)
        # Only the always-shown rows with no value in this record.
        self.assertEqual(sorted(res.unfilled_fields), ["batch", "supplier"])


class TestSaveRecordAdapter(unittest.TestCase):
    def test_prototype_shape_and_camelcase(self):
        rec = {
            "pageKey": "aug-p1", "pageLabel": "Aug p.1",
            "lot": {"old": "206/7", "new": "207/9",
                    "box300": [533, 930, 631, 966]},
            "width": {"old": "780.0", "new": "781.5",
                      "box300": [2088, 1282, 2178, 1310]},
            "edits": [{"field": "lot", "old": "206/7", "new": "207/9"}],
            "labelNo": "LBL-0001", "delivery": "LSE-0008",
            "deliveryId": "LSE-DEL-a0239ccdaf77405f89a99dc57c99adcf",
        }
        vals = edited_values_from_save_record(rec)
        res = build_label(vals)
        self.assertIn("<b>207/9</b>", res.html)
        self.assertIn("<b>781.5 mm</b>", res.html)
        self.assertEqual(res.label_no, "LBL-0001")


class TestSaveWithLabel(unittest.TestCase):
    def test_writes_html_pdf_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            man = save_with_label(ACME_EDITED, td)
            self.assertTrue(os.path.exists(man["label_html"]))
            self.assertTrue(os.path.exists(man["manifest"]))
            self.assertEqual(man["page_key"], "acme-p1")
            self.assertEqual(man["label_no"], "LBL-ACME-0001")
            self.assertTrue(man["is_printable"])
            with open(man["manifest"]) as _fh:
                saved = json.load(_fh)
            self.assertEqual(saved["edited_values"]["lot"]["new"],
                             "ACME-LOT-78")
            if HAS_FITZ:
                self.assertTrue(os.path.exists(man["label_pdf"]))
                with open(man["label_pdf"], "rb") as _fh:
                    self.assertTrue(_fh.read(4) == b"%PDF")

    def test_edited_pdf_sha_recorded_not_copied(self):
        with tempfile.TemporaryDirectory() as td:
            edited = os.path.join(td, "edited.pdf")
            with open(edited, "wb") as _fh:
                _fh.write(b"%PDF-fake-edited-page")
            man = save_with_label(PG_AUG_P1, td, edited_pdf_path=edited)
            import hashlib
            expect = hashlib.sha256(b"%PDF-fake-edited-page").hexdigest()
            self.assertEqual(man["edited_pdf_sha256"], expect)
            self.assertEqual(man["edited_pdf"], edited)
            # Only the 3 label files were created in out dir besides input.
            names = sorted(os.listdir(td))
            self.assertEqual(names, ["edited.pdf", "label-aug-p1.html",
                                     "label-aug-p1.json", "label-aug-p1.pdf"]
                            if HAS_FITZ else
                            ["edited.pdf", "label-aug-p1.html",
                             "label-aug-p1.json"])

    def test_one_label_per_page_no_leak(self):
        may = dict(PG_AUG_P1)
        may.update({"page_key": "may-p1", "page_label": "May p.1",
                    "delivery": "LSE-0009", "label_no": "LBL-0003",
                    "lot": {"old": "304/5", "new": "305/7"},
                    "width": {"old": "670.0", "new": "671.5"},
                    "edits": [
                        {"field": "lot", "old": "304/5", "new": "305/7"},
                        {"field": "width", "old": "670.0", "new": "671.5"},
                    ]})
        with tempfile.TemporaryDirectory() as td:
            mans = build_labels_for_pages([PG_AUG_P1, may], td)
            self.assertEqual(len(mans), 2)
            with open(mans[0]["label_html"]) as _fh:
                aug_html = _fh.read()
            with open(mans[1]["label_html"]) as _fh:
                may_html = _fh.read()
            self.assertIn("<b>207/9</b>", aug_html)
            self.assertNotIn("305/7", aug_html)
            self.assertNotIn("671.5", aug_html)
            self.assertIn("<b>305/7</b>", may_html)
            self.assertNotIn("207/9", may_html)
            self.assertNotIn("781.5", may_html)
        with self.assertRaises(ValueError):
            build_labels_for_pages([PG_AUG_P1, PG_AUG_P1], td)


@unittest.skipUnless(HAS_FITZ, "PyMuPDF not installed")
class TestLabelPdf(unittest.TestCase):
    def test_pdf_bytes_and_text(self):
        import fitz
        pdf = build_label_pdf(PG_AUG_P1)
        self.assertTrue(pdf[:4] == b"%PDF")
        self.assertGreater(len(pdf), 1000)
        doc = fitz.open(stream=pdf, filetype="pdf")
        self.assertEqual(len(doc), 1)
        text = doc[0].get_text()
        self.assertIn("207/9", text)
        self.assertIn("781.5", text)
        # Page is the 100mm label card size (within rounding).
        self.assertAlmostEqual(doc[0].rect.width, 100 * 72 / 25.4, delta=1)


if __name__ == "__main__":
    unittest.main()
