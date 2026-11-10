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
    # Re-pinned 2026-11-09 (Round 27): the 5 live pages were intentionally
    # rebuilt with current R26 segs (Guard 0/5 FAIL -> 5/5 PASS). Old SHAs
    # were the stale r10m-family pages (bce37147..., f4f72713..., d0948b0f...,
    # 539995a9..., 8587be86...). New SHAs verified by parent (sha256sum).
    "live-scan-page-aug-300.html": "d4d254308a29e933fa7011e0cca8b65854058673ea7fe1d330225e774a9224d5",
    "live-scan-page-aug-p2-300.html": "c3d9b7a4c41af3a7f07c7843f1140abe3de1443543bad5fab3cd21dd13901391",
    "live-scan-page-may-300.html": "7d4d19cc97816fbc39dbc6442b16eeb5bcb8941852980baf686858fabf256ade",
    "live-scan-page-may-p2-300.html": "3d93443414704a96151956a8f8ea8b2dd914426ff23944f59a6e689ac06584eb",
    "live-scan-page-may-p3-300.html": "9cf42b25b428f5596761da2e49769742b4d8ac929131a7d4fdd34ac0acda92d6",
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
