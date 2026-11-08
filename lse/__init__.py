"""LSE — Live-Scan Editing. Edit the text on a scanned document
without OCR, without rebuilding the page.

The scan IS the page; text is a living layer on top of the original
pixels. Word positions come from segmentation (connected components —
no recognition); the old word's pixels are erased with Telea
inpainting; the replacement is typed in a font learned from the
document's own glyphs (Document DNA). The document's full originality
is preserved: work at the original's DPI, never downscale, never
re-encode, never change resolution.
"""
from .caps import fit_caps
from .database import (init_db, record_delivery, record_multipage_delivery,
                       resolve_label_for_page, resolve_labels_for_delivery,
                       verify_chain, verify_delivery, verify_delivery3)
from .document import Document, Page, load_document, open_document
from .gate import (ambiguous_band_cores, calibrate, full_page_mask,
                   gate as gate_page)
from .inpaint import clean_page
from .page import build_live_page, word_styles
from .segment import segment_array, segment_file
from .writeback import (CapsDoesNotFitError, build_edited_pdf, build_patch,
                        composite_patches_for_page)

__version__ = "0.1.0"
__all__ = [
    "open_document", "load_document", "Document", "Page",
    "segment_array", "segment_file", "clean_page",
    "gate_page", "full_page_mask", "calibrate", "ambiguous_band_cores",
    "build_live_page", "word_styles",
    "build_edited_pdf", "build_patch", "composite_patches_for_page",
    "CapsDoesNotFitError", "fit_caps",
    "init_db", "record_delivery", "record_multipage_delivery",
    "resolve_label_for_page", "resolve_labels_for_delivery",
    "verify_chain", "verify_delivery", "verify_delivery3",
]
