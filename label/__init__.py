"""LSE label package — save -> label (Domino) for scanned documents.

After the LSE engine saves an edited scan page, this package builds the
packing label for THAT page/pack from THAT page's edited values — one
label per page, never another page's values, never a demo/fake value.

No OCR anywhere in this package. It only renders values the caller
supplies (values the user typed on the live page / the engine's save
record). A missing value stays visibly blank — it is flagged, never
faked.
"""

from .label import (
    LabelResult,
    build_label,
    build_label_html,
    build_label_pdf,
    build_labels_for_pages,
    edited_values_from_save_record,
    save_with_label,
)

__all__ = [
    "LabelResult",
    "build_label",
    "build_label_html",
    "build_label_pdf",
    "build_labels_for_pages",
    "edited_values_from_save_record",
    "save_with_label",
]
