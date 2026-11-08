"""Shared helpers for the LSE engine tests.

All paths are absolute. Real PG PDFs are READ-ONLY inputs (never
copied into the repo, never modified). The Round 3 database is checked
read-only by SHA. Every test writes only under STAGING (/tmp).
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SP = "/home/hatch/workspace/gravora-review/live-paper-prototype/scan-paper"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PG_AUG = "/home/hatch/workspace/gravora-review/packfirm-analysis/supplier-coa/PG AUGUST-2026 (25mic) COA.pdf"
PG_MAY = "/home/hatch/workspace/gravora-review/packfirm-analysis/supplier-coa/PG MAY-2026 (20mic) COA.pdf"
DNA_REG = os.path.join(SP, "improve/round2/dna-prod/dna-clone-regular-600.ttf")
DNA_BOLD = os.path.join(SP, "improve/round2/dna-prod/dna-clone-bold-600.ttf")
STAMPS_JSON = os.path.join(SP, "improve/round2/stamps.json")
R3_DB = os.path.join(SP, "improve/round3/track-c/lse_gravora.db")
R3_DB_SHA = "1c065457bb9cb8e5b276d5007d9b020c18c8a0ae0374b92eb759f12150746939"

CANONICAL_LIVE_SHAS = {
    "live-scan-page-aug-300.html": "bce371471cbe10d8ce30ef005b6d17a9a4a7771f55d0726bcc3b418036e70d4f",
    "live-scan-page-aug-p2-300.html": "f4f72713b1059967427629df28015c67faf80f6f329a3981c2f2e6602b57e6ed",
    "live-scan-page-may-300.html": "d0948b0f5a9a1bb8ae2b2d6191ddbf5f3eb996d7be1354321d044f0eb1d82a67",
    "live-scan-page-may-p2-300.html": "539995a946a3b66b2cbf076d6efe1e97040db84312d086590697f2205fce77d2",
    "live-scan-page-may-p3-300.html": "8587be86243d7c2ff9dca8b4d733ba44e0121440fbd88fe107180d7de9656796",
}

# Real-fixture availability: the full suite runs against the real PG
# supplier COA PDFs + prototype DNA fonts, which are NOT in this repo
# (real supplier data must never go public). In a clean clone these
# paths are absent, so real-fixture tests SKIP (exit 0) and only the
# portable tests + the demo path run. See README "How to test".
REAL_FIXTURES = (
    os.path.isfile(PG_AUG)
    and os.path.isfile(PG_MAY)
    and os.path.isfile(DNA_REG)
    and os.path.isfile(DNA_BOLD)
    and os.path.isdir(SP)
)
requires_real_fixtures = unittest.skipUnless(
    REAL_FIXTURES,
    "real PG/DNA fixtures not present (not in repo; run the demo path instead)",
)

STAGING = os.path.join(tempfile.gettempdir(), "lse-verify")
os.makedirs(STAGING, exist_ok=True)


def render_bgr(pdf_path, pageno, dpi=300):
    """Render one PDF page at dpi -> BGR numpy array (native DPI)."""
    import cv2
    import fitz
    import numpy as np
    doc = fitz.open(pdf_path)
    try:
        pix = doc[pageno].get_pixmap(matrix=fitz.Matrix(dpi / 72.0, dpi / 72.0))
        rgb = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    finally:
        doc.close()


def render_rgb(pdf_path, pageno, dpi=300):
    import fitz
    import numpy as np
    doc = fitz.open(pdf_path)
    try:
        pix = doc[pageno].get_pixmap(matrix=fitz.Matrix(dpi / 72.0, dpi / 72.0))
        return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    finally:
        doc.close()


def page_count(pdf_path):
    import fitz
    doc = fitz.open(pdf_path)
    try:
        return len(doc)
    finally:
        doc.close()
