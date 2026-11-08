#!/usr/bin/env python3
"""Generate the SYNTHETIC supplier COA sample for the LSE demo.

ALL data here is fake: supplier "ACME FOILS LTD", batch "ACME-2026-0001",
lot "ACME-LOT-77", fake test values. NEVER use a real supplier COA
(PG / Raviraj / Amcor) or a real delivery database to make a demo sample.

What it writes (into --out, default: this demo/ directory):
  synthetic-supplier-coa.pdf        A4, 1 page, vector text (ReportLab)
  synthetic-supplier-coa-300.png    the same page rendered at 300 DPI
  ground-truth-words.json           every word + its box in PDF points,
                                    read back from the PDF text layer
                                    (vector text, not OCR)

The PDF and PNG are GENERATED files — they are binary, so they are NOT
committed to the repo (see .gitignore). Anyone can regenerate them with:
    python demo/make_synthetic.py
The ground-truth JSON is UTF-8 text, so a checked-in copy lives in demo/
alongside this script; regenerating must reproduce it exactly
(same words, same boxes).

Design: plain black print on white paper, ruled table, NO grey highlight
bar, generous word spacing so the fixed word-gap rule can separate words.
The batch number "ACME-2026-0001" is the edit-test word: the demo edits
its last segment ("0001" -> "0002").

Layout (same family as the fixture this was adapted from):
  A4, header block at y >= 40 mm from the top so it stays OUTSIDE the
  prototype segmenter's hard-coded logo exclusion zone
  (x 150-510, y 120-450 px @300 DPI — the PG logo's position on the real
  pages; a per-template logo zone is a known product limitation).
  Table top edge at y = 122 mm from top; columns at x = 20/95/150/182 mm.

Usage:
    python demo/make_synthetic.py [--out DIR]
Requires: reportlab, PyMuPDF (see requirements.txt).
No OCR anywhere.
"""
import argparse
import json
import os
import sys

import fitz  # PyMuPDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = HERE

PDF_NAME = "synthetic-supplier-coa.pdf"
PNG_NAME = "synthetic-supplier-coa-300.png"
GT_NAME = "ground-truth-words.json"

# (text, x_mm, y_mm_from_top, font, size_pt) — laid out in reading order.
LINES = [
    ("ACME FOILS LTD", 20, 44, "Helvetica-Bold", 16),
    ("CERTIFICATE OF ANALYSIS", 20, 56, "Helvetica-Bold", 14),
    ("Supplier of Flexible Packaging Films", 20, 64, "Helvetica", 10),
    ("Batch No: ACME-2026-0001", 20, 78, "Helvetica-Bold", 12),
    ("Lot No: ACME-LOT-77", 20, 86, "Helvetica", 12),
    ("Product: Blister Foil 25 Micron", 20, 94, "Helvetica", 12),
    ("Customer: FAKE PHARMA LTD", 20, 102, "Helvetica", 12),
    ("Date: 07 November 2026", 20, 110, "Helvetica", 12),
]
# Table: header + 6 parameter rows (parameter, specification, result, unit).
TABLE = [
    ("Test Parameter", "Specification", "Result", "Unit"),
    ("Thickness", "25.0 +/- 2.0", "25.2", "micron"),
    ("GSM", "36.0 +/- 2.0", "36.4", "g/m2"),
    ("Tensile Strength", "Min 280", "296", "N/mm2"),
    ("Elongation", "Min 90", "204", "percent"),
    ("Pinholes", "Max 5", "2", "per m2"),
    ("Sealing Strength", "Min 25", "28", "N/25mm"),
]
FOOTER = [
    ("Prepared By: A. Tester", 20, 268, "Helvetica", 11),
    ("Authorized By: B. Checker", 20, 276, "Helvetica", 11),
]


def build_pdf(pdf_path):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    w_pt, h_pt = A4
    for text, x_mm, y_mm, font, size in LINES + FOOTER:
        c.setFont(font, size)
        c.drawString(x_mm * mm, h_pt - y_mm * mm, text)
    # Table, top edge at y=122mm from top; columns at x = 20/95/150/182 mm.
    # Unit column widened to 182-200mm: a narrower column let words cross
    # the right border and the border rule ate the crossing letters.
    cols = [20, 95, 150, 182]
    y0 = 122.0
    row_h = 9.0
    c.setFont("Helvetica-Bold", 11)
    for j, cell in enumerate(TABLE[0]):
        c.drawString(cols[j] * mm + 2 * mm, h_pt - (y0 + 6.5) * mm, cell)
    c.setFont("Helvetica", 11)
    for i, row in enumerate(TABLE[1:], start=1):
        for j, cell in enumerate(row):
            c.drawString(cols[j] * mm + 2 * mm, h_pt - (y0 + i * row_h + 6.5) * mm, cell)
    # Ruled lines: outer border + row separators + column separators.
    x_left, x_right = 20 * mm, 200 * mm
    y_top = h_pt - y0 * mm
    y_bot = h_pt - (y0 + len(TABLE) * row_h) * mm
    c.setLineWidth(1)
    c.rect(x_left, y_bot, x_right - x_left, y_top - y_bot, stroke=1, fill=0)
    for i in range(1, len(TABLE)):
        y = h_pt - (y0 + i * row_h) * mm
        c.line(x_left, y, x_right, y)
    for x in cols[1:]:
        c.line(x * mm, y_bot, x * mm, y_top)
    c.showPage()
    c.save()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=DEFAULT_OUT,
                    help="output directory (default: demo/)")
    args = ap.parse_args()
    outdir = os.path.abspath(args.out)
    os.makedirs(outdir, exist_ok=True)

    pdf_path = os.path.join(outdir, PDF_NAME)
    build_pdf(pdf_path)
    doc = fitz.open(pdf_path)
    assert doc.page_count == 1, f"expected 1 page, got {doc.page_count}"
    page = doc[0]
    # Ground truth: words from the PDF text layer (vector text, not OCR).
    gt_words = []
    for x0, y0, x1, y1, text, _b, _l, _w in page.get_text("words"):
        gt_words.append({"text": text,
                         "box_pt": [round(x0, 1), round(y0, 1),
                                    round(x1, 1), round(y1, 1)]})
    # 300 DPI render (300/72 = 4.1667x). A4 @300dpi = 2480 x 3508 px.
    pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))
    png_path = os.path.join(outdir, PNG_NAME)
    pix.save(png_path)
    gt = {"pdf": PDF_NAME, "pages": 1,
          "render_dpi": 300, "render_px": [pix.width, pix.height],
          "word_count": len(gt_words), "words": gt_words}
    gt_path = os.path.join(outdir, GT_NAME)
    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump(gt, f, indent=1, ensure_ascii=False)
    print(f"pdf: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
    print(f"png: {png_path} {pix.width}x{pix.height}")
    print(f"ground-truth words in PDF text layer: {len(gt_words)}")
    for w in gt_words:
        print("  ", w["text"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
