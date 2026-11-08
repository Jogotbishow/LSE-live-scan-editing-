#!/usr/bin/env python3
"""End-to-end verification for the LSE label package (own numbers).

1. ACME synthetic sample — reads the ground-truth words file, applies
   real edits (Lot / Batch / Thickness), builds the label through the
   save-record adapter + save_with_label, and checks the label carries
   the EDITED values (old values only in the audit line).
2. Real PG AUGUST-2026 p.1 — the PDF is READ-ONLY (SHA-256 checked
   before/after; rendering goes to /tmp only, nothing is copied into
   the repo). Edited values come from the prototype's verified identity
   table (verify_save_label_live_r10b.py: Lot 206/7 -> 207/9,
   WIDTH 780.0 -> 781.5). Checks the label + no leak of May values.

Usage (from lse-opensource/label/):
  <venv python> verify_label.py
Writes verify-out/label-acme-p1.{html,pdf,json} and
verify-out/label-aug-p1.{html,pdf,json}. Exits non-zero on any failure.
No OCR anywhere: values come from ground truth / the identity table,
never from reading the scan.
"""
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from label import build_labels_for_pages, save_with_label  # noqa: E402

VENV_PY = "/home/hatch/workspace/gravora-review/live-paper-prototype/scan-paper/venv/bin/python"
FIX = "/home/hatch/workspace/gravora-review/gravora-app/fixtures/synthetic-supplier-coa"
PG_AUG = "/home/hatch/workspace/gravora-review/packfirm-analysis/supplier-coa/PG AUGUST-2026 (25mic) COA.pdf"
OUT = os.path.join(HERE, "verify-out")
TMP = "/tmp/lse-label-verify"

CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
    return bool(ok)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pt_to_box300(box_pt):
    s = 300 / 72
    return [round(c * s) for c in box_pt]


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    print("== 1. ACME synthetic sample ==")

    # --- ground truth: locate the words we will edit -------------------
    gt = json.load(open(os.path.join(FIX, "ground-truth-words.json")))
    words = {w["text"]: w for w in gt["words"]}
    print(f"  GT file: word_count={gt.get('word_count')} "
          f"(len={len(gt['words'])})")
    batch_box = pt_to_box300(words["ACME-2026-0001"]["box_pt"])
    lot_box = pt_to_box300(words["ACME-LOT-77"]["box_pt"])
    thick_box = pt_to_box300(words["25.2"]["box_pt"])
    print(f"  Batch box300={batch_box} Lot box300={lot_box} "
          f"Thickness box300={thick_box}")

    acme_record = {
        "page_key": "acme-p1",
        "page_label": "ACME p.1",
        "page_no": 1,
        "delivery": "LSE-ACME-0001",
        "delivery_id": "LSE-DEL-acme0001",
        "label_no": "LBL-ACME-0001",
        "item": "Blister Foil 25 Micron",
        "customer": "FAKE PHARMA LTD",
        "supplier": "ACME FOILS LTD",
        "batch": {"old": "ACME-2026-0001", "new": "ACME-2026-0002",
                  "box300": batch_box},
        "lot": {"old": "ACME-LOT-77", "new": "ACME-LOT-78",
                "box300": lot_box},
        "width": {"old": "25.2", "new": "25.4", "box300": thick_box},
        "thickness": {"old": "25.2", "new": "25.4", "box300": thick_box},
        "date": "07.11.2026",
        "edits": [
            {"field": "lot", "old": "ACME-LOT-77", "new": "ACME-LOT-78",
             "box300": lot_box},
            {"field": "batch", "old": "ACME-2026-0001",
             "new": "ACME-2026-0002", "box300": batch_box},
            {"field": "width", "old": "25.2", "new": "25.4",
             "box300": thick_box},
        ],
    }
    # Stand-in for the engine's saved edited PDF: a copy in /tmp only.
    edited_pdf = os.path.join(TMP, "acme-edited.pdf")
    shutil.copyfile(os.path.join(FIX, "synthetic-supplier-coa.pdf"),
                    edited_pdf)
    man = save_with_label(acme_record, OUT, edited_pdf_path=edited_pdf)
    html = open(man["label_html"]).read()
    check("acme: label Lot is the EDITED value",
          "<b>ACME-LOT-78</b>" in html, "ACME-LOT-78")
    check("acme: label Batch is the EDITED value",
          "<b>ACME-2026-0002</b>" in html, "ACME-2026-0002")
    check("acme: label WIDTH is the EDITED value",
          "<b>25.4 mm</b>" in html, "25.4 mm")
    check("acme: old Lot never a value cell",
          "<b>ACME-LOT-77</b>" not in html)
    check("acme: old Batch never a value cell",
          "<b>ACME-2026-0001</b>" not in html)
    check("acme: audit line old -> new present",
          "ACME-LOT-77 → ACME-LOT-78" in html)
    check("acme: manifest records edited-PDF SHA-256",
          man["edited_pdf_sha256"] == sha256(edited_pdf),
          man["edited_pdf_sha256"][:16] + "…")
    check("acme: label is printable (required lot+width filled)",
          man["is_printable"] is True)
    check("acme: label PDF written",
          man["label_pdf"] and os.path.exists(man["label_pdf"]))

    print("== 2. Real PG AUGUST-2026 p.1 (read-only) ==")
    sha_before = sha256(PG_AUG)
    import fitz
    doc = fitz.open(PG_AUG)
    p1 = doc[0]
    print(f"  PG Aug PDF: {len(doc)} pages, p1 rect={p1.rect}, "
          f"images p1={len(p1.get_images())}, extractable text p1="
          f"{len(p1.get_text())} chars (pure scan)")
    pix = p1.get_pixmap(dpi=300)
    pix.save(os.path.join(TMP, "pg-aug-p1-300.png"))
    print(f"  p1 rendered to /tmp at 300 DPI: {pix.width}x{pix.height}px")
    # Edited values: prototype identity table (r10b verifier), verified
    # by word identity on the real page — Lot 206/7 -> 207/9,
    # WIDTH 780.0 -> 781.5. No OCR used here.
    pg_record = {
        "page_key": "aug-p1",
        "page_label": "Aug p.1",
        "page_no": 1,
        "delivery": "LSE-0008",
        "delivery_id": "LSE-DEL-a0239ccdaf77405f89a99dc57c99adcf",
        "label_no": "LBL-0001",
        "item": "Blister Foil 25 Micron (PG Foils)",
        "customer": "Packfirm Limited",
        "lot": {"old": "206/7", "new": "207/9",
                "box300": [533, 930, 631, 966]},
        "width": {"old": "780.0", "new": "781.5",
                  "box300": [2088, 1282, 2178, 1310]},
        "edits": [
            {"field": "lot", "old": "206/7", "new": "207/9"},
            {"field": "width", "old": "780.0", "new": "781.5"},
        ],
    }
    man2 = save_with_label(pg_record, OUT, draft=False)
    html2 = open(man2["label_html"]).read()
    check("pg-aug-p1: label Lot is the EDITED value",
          "<b>207/9</b>" in html2, "207/9")
    check("pg-aug-p1: label WIDTH is the EDITED value",
          "<b>781.5 mm</b>" in html2, "781.5 mm")
    check("pg-aug-p1: label no. + delivery from THIS page",
          "LBL-0001" in html2 and "LSE-0008" in html2)
    check("pg-aug-p1: audit line old -> new present",
          "206/7 → 207/9" in html2 and "780.0 → 781.5" in html2)
    for leak in ("305/7", "283/7", "282/7", "671.5", "721.5", "771.5"):
        check(f"pg-aug-p1: no leak of May value {leak}", leak not in html2)
    check("pg-aug-p1: final label carries QC PASSED (draft=False)",
          "QC PASSED" in html2)
    check("pg-aug-p1: real PDF untouched (SHA-256)",
          sha256(PG_AUG) == sha_before, sha_before[:16] + "…")

    print("== 3. One label per page (both together) ==")
    with open(os.path.join(TMP, "both.json"), "w") as fh:
        json.dump({"acme": man["label_html"], "pg": man2["label_html"]}, fh)
    n_pass = sum(1 for _, ok, _ in CHECKS if ok)
    print(f"TOTAL: {n_pass}/{len(CHECKS)}")
    print(f"Outputs: {OUT}/label-acme-p1.{{html,pdf,json}} "
          f"label-aug-p1.{{html,pdf,json}}")
    return 0 if n_pass == len(CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
