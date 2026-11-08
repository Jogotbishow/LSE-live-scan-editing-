"""LSE label — the save -> label Domino for scanned documents.

This is the standalone (open-source repo) version of the wiring proven
in the prototype (Round 8 Track C ``save-label.js`` + Round 10 verifier
``verify_save_label_live_r10b.py`` — 90/90 on 5 pages — and the Round 7
labels ``labels/label-lse-*.html``). Same layout family, same rule:

    save an edited page  =>  that page's own label opens,
    with that page's own EDITED values (Lot, WIDTH, Batch, ...).

Rules (GRAVORA rules, non-negotiable):

1.  One label per page/pack. ``build_label`` only ever sees ONE page's
    ``edited_values``; nothing from another page can leak in.
2.  Never silently fill a demo/fake value. A missing, blank, or
    demo-refused value is rendered visibly as "— পূরণ হয়নি —"
    (NOT FILLED), listed in ``unfilled_fields``, and — when it is a
    required field — the label is marked not printable
    (``is_printable is False``). The caller may pass ``demo_values``
    (a set of known template/demo strings); any field whose new value
    equals one of them is treated as unfilled and reported.
3.  No OCR. This module never reads a scan. It renders only the values
    the caller supplies — the values the user typed on the live page,
    as carried by the engine's save record.
4.  No invented numbers. ``label_no``, ``delivery`` etc. are shown
    only when supplied; when absent they render as unfilled, never as
    an auto-generated number (the file name uses ``page_key`` instead).

``edited_values`` — the exact dict ``build_label`` expects
-----------------------------------------------------------
Required keys: ``page_key`` (str, e.g. ``"aug-p1"``) and ``page_label``
(str, e.g. ``"Aug p.1"`` — shown on the label as the WIDTH row's page).

Value fields — each may be a plain string (the current/edited value),
a dict ``{"new": ..., "old": ..., "box300": [x0, y0, x1, y1]}`` (the
prototype save-record shape: ``new`` is the edited value, ``old`` the
printed value, ``box300`` the word's box at native DPI — used for the
``old -> new`` audit line), or ``None`` / ``""`` / missing (= unfilled):

    lot, batch, width, thickness, item, product, customer, supplier,
    date, mfg_date, expiry_date, gross_weight, net_weight, packs,
    version, material_code

Aliases: ``product`` falls back to ``item`` and vice versa; ``lot``
and ``batch`` are DIFFERENT fields and never fall back to each other
(the prototype label merged them into one "Batch / Lot No." row —
here they are separate rows; when only ``lot`` is given the Batch row
stays unfilled, and vice versa).

Optional keys: ``delivery`` (e.g. ``"LSE-0008"``), ``delivery_id``,
``label_no`` (e.g. ``"LBL-0001"``), ``page_no`` (int), ``edits`` (list
of ``{"field", "old", "new", "box300"}`` — shown in the audit line),
``draft`` (bool, default True), ``source_note`` (str, shown in the
footer), ``extra_fields`` (dict of extra ``label -> value`` rows,
same value rules), ``required`` (iterable of field names that must be
filled for the label to be printable; default ``("lot", "width")`` for
the ``supplier-foil`` template).

The ``edited_values`` shape is deliberately the same as the prototype
save record (``lse-edits-<page>.json``: ``page_key``, ``lot``/``width``
as ``{old, new, box300}``, ``edits`` list). Use
``edited_values_from_save_record`` to normalise a raw save record
(it also accepts the live page's camelCase keys: ``pageKey``,
``pageLabel``, ``labelNo``, ``deliveryId``).

Public API
----------
``build_label(edited_values, *, template="supplier-foil", draft=None,
demo_values=None, required=None) -> LabelResult``
    ``LabelResult`` carries ``.html``, ``.fields`` (resolved rows),
    ``.unfilled_fields``, ``.refused_demo``, ``.is_printable``,
    ``.is_draft``, ``.page_key``, ``.label_no`` and ``.to_dict()``.

``build_label_html(edited_values, **kw) -> str``
``build_label_pdf(edited_values, **kw) -> bytes``
    Label PDF (100 mm x 160 mm) drawn with PyMuPDF. Raises
    RuntimeError with a clear message when PyMuPDF is unavailable.
    HTML never needs any third-party package.

``save_with_label(edited_values, out_dir, *, edited_pdf_path=None,
make_pdf=True, **kw) -> dict``
    The Domino flow: after the engine saves the edited PDF, call this
    once per page. Writes ``label-<page_key>.html`` (+ ``.pdf``) and a
    ``label-<page_key>.json`` manifest (the ``edited_values`` as
    received, resolved fields, unfilled fields, and — when
    ``edited_pdf_path`` is given — that file's SHA-256; the edited PDF
    itself is never copied or moved). Returns the manifest dict.

``build_labels_for_pages(pages, out_dir, **kw) -> list[dict]``
    One ``save_with_label`` per page; ``page_key`` values must be
    unique, so no page's values can land in another page's label.

``edited_values_from_save_record(record) -> dict``
    Normalise a prototype/engine save record into ``edited_values``.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
from dataclasses import dataclass, field

__all__ = [
    "LabelResult",
    "build_label",
    "build_label_html",
    "build_label_pdf",
    "build_labels_for_pages",
    "edited_values_from_save_record",
    "save_with_label",
]

# ---------------------------------------------------------------------------
# Field model
# ---------------------------------------------------------------------------

#: Shown wherever a value is missing / blank / refused. Deliberately
#: loud: a blank on a printed label must be seen, never mistaken for a
#: value that simply looks empty.
UNFILLED_TEXT = "— পূরণ হয়নি —"

#: Default required fields for the supplier-foil template (the Domino
#: fields proven in the prototype: Lot + WIDTH).
DEFAULT_REQUIRED = ("lot", "width")

#: Label rows for the supplier-foil template, in print order.
#: (field key, row heading, unit suffix appended when absent)
_ROWS = (
    ("item", "Item", ""),
    ("customer", "Customer", ""),
    ("supplier", "Supplier", ""),
    ("batch", "Batch No.", ""),
    ("lot", "Batch / Lot No.", ""),
    ("width", "WIDTH", " mm"),
    ("thickness", "Thickness", ""),
    ("date", "Date", ""),
    ("mfg_date", "Production / Mfg. Date", ""),
    ("expiry_date", "Expiry Date", ""),
    ("gross_weight", "Gross Weight", ""),
    ("net_weight", "Net Weight", ""),
    ("packs", "Number of Packs", ""),
    ("version", "Version No.", ""),
    ("material_code", "Material Code", ""),
)

# Fields that are shown even when unfilled (the Domino core + identity).
# Any other row is shown only when it has a value or was explicitly
# present in the input (so a template with no expiry date does not
# print a scary empty Expiry row it never had).
_ALWAYS_SHOW = {"item", "customer", "supplier", "batch", "lot", "width"}


def _norm_value(raw):
    """Normalise one field value to (new, old, box300).

    Accepts a plain string, a ``{"new","old","box300"}`` dict, or
    None/"" (=> all None). Anything else is stringified.
    """
    if raw is None:
        return None, None, None
    if isinstance(raw, dict):
        new = raw.get("new")
        old = raw.get("old")
        box = raw.get("box300") or raw.get("box")
        new = None if new is None else str(new).strip() or None
        old = None if old is None else str(old).strip() or None
        return new, old, box
    s = str(raw).strip()
    return (s or None), None, None


def _is_filled(value):
    return value is not None and str(value).strip() != ""


@dataclass
class LabelResult:
    """Result of :func:`build_label`."""

    html: str
    page_key: str
    page_label: str
    label_no: str | None
    fields: list  # [{key, label, new, old, box300, filled}]
    unfilled_fields: list = field(default_factory=list)
    refused_demo: list = field(default_factory=list)
    is_printable: bool = False
    is_draft: bool = True
    edits: list = field(default_factory=list)

    def to_dict(self):
        return {
            "page_key": self.page_key,
            "page_label": self.page_label,
            "label_no": self.label_no,
            "is_printable": self.is_printable,
            "is_draft": self.is_draft,
            "unfilled_fields": list(self.unfilled_fields),
            "refused_demo": list(self.refused_demo),
            "fields": [
                {k: f[k] for k in ("key", "label", "new", "old", "filled")}
                for f in self.fields
            ],
            "edits": list(self.edits),
        }


def _resolve_fields(values, required, demo_values):
    """Resolve every template row. Returns (fields, unfilled, refused)."""
    demo_values = {str(v) for v in (demo_values or ())}
    fields, unfilled, refused = [], [], []
    for key, label, unit in _ROWS:
        raw = values.get(key)
        # product <-> item alias (one name for the same thing).
        if raw is None and key == "item":
            raw = values.get("product")
        if raw is None and key == "product":
            raw = values.get("item")
        new, old, box = _norm_value(raw)
        if new is not None and new in demo_values:
            refused.append(key)
            new, old = None, None
        filled = _is_filled(new)
        display = new
        if filled and unit and not str(new).endswith("mm"):
            display = f"{new}{unit}"
        show = key in _ALWAYS_SHOW or filled or key in values
        if show and not filled:
            unfilled.append(key)
        if show:
            fields.append(
                {
                    "key": key,
                    "label": label,
                    "new": display,
                    "old": old,
                    "box300": box,
                    "filled": filled,
                }
            )
    # Caller-supplied extra rows (same rules, never required).
    for label, raw in (values.get("extra_fields") or {}).items():
        new, old, box = _norm_value(raw)
        if new is not None and new in demo_values:
            refused.append(str(label))
            new = None
        filled = _is_filled(new)
        if not filled:
            unfilled.append(str(label))
        fields.append(
            {
                "key": str(label),
                "label": str(label),
                "new": new,
                "old": old,
                "box300": box,
                "filled": filled,
            }
        )
    return fields, unfilled, refused


def _audit_line(values, fields):
    """'old -> new' lines for fields that actually changed.

    Each ``edits`` entry is validated against the resolved field value:
    a stale/foreign edit (e.g. another page's Lot carried over in a
    copied record) is dropped, so the audit line can never show values
    the label's own fields do not carry.
    """
    parts = []
    by_key = {f["key"]: f for f in fields}
    for edit in values.get("edits") or []:
        if not isinstance(edit, dict):
            continue
        fkey, old, new = edit.get("field"), edit.get("old"), edit.get("new")
        if not (_is_filled(old) and _is_filled(new)
                and str(old) != str(new)):
            continue
        f = by_key.get(fkey)
        if f is not None:
            new_disp = str(f["new"] or "")
            if str(new) not in (new_disp, new_disp.removesuffix(" mm")):
                continue
            if _is_filled(f["old"]) and str(old) != str(f["old"]):
                continue
        parts.append(f"{fkey} {old} → {new}")
    if not parts:  # fall back to the resolved lot/width old->new
        for key in ("lot", "width", "batch"):
            f = by_key.get(key)
            if f and _is_filled(f["old"]) and _is_filled(f["new"]):
                if str(f["old"]) != str(f["new"]).removesuffix(" mm"):
                    parts.append(f"{key} {f['old']} → {f['new']}")
    return "; ".join(parts)


# ---------------------------------------------------------------------------
# HTML rendering (stdlib only — same layout family as Round 7 labels)
# ---------------------------------------------------------------------------

_CSS = """
  * { box-sizing: border-box; }
  body { margin: 0; background: #e8e6e1; font-family: 'Noto Sans Bengali','Calibri',sans-serif; }
  .label { width: 100mm; min-height: 150mm; margin: 24px auto; background: #fff;
           border: 2.5px solid #000; padding: 10px 12px; color: #000; }
  .label h2 { text-align: center; font-size: 20px; letter-spacing: 2px; margin: 2px 0 4px;
              border-bottom: 2px solid #000; padding-bottom: 6px; }
  .label .sub { text-align: center; font-size: 12px; margin: 0 0 8px; }
  .label .item { font-size: 19px; font-weight: bold; text-align: center; margin: 8px 0 2px; }
  .label .pack { text-align: center; font-size: 13px; margin: 0 0 10px; }
  .label table { width: 100%; border-collapse: collapse; font-size: 14px; }
  .label td { border: 1px solid #000; padding: 5px 7px; vertical-align: top; }
  .label td.k { width: 38%; font-weight: bold; background: #f3f4f6; }
  .label td.from-coa { background: #fef3c7; }
  .label td.unfilled { background: #fee2e2; color: #b91c1c; font-weight: bold; }
  .label .warn { background: #fee2e2; border: 2px solid #b91c1c; color: #b91c1c;
                 font-weight: bold; text-align: center; padding: 6px; margin: 8px 0; font-size: 13px; }
  .label .draft { background: #fef3c7; border: 2px dashed #92400e; color: #92400e;
                  font-weight: bold; text-align: center; padding: 6px; margin: 8px 0;
                  font-size: 15px; letter-spacing: 2px; }
  .label .src { font-size: 12.5px; margin: 10px 0 4px; line-height: 1.5; }
  .label .stamp { margin-top: 12px; border: 2px dashed #15803d; color: #15803d; text-align: center;
                  font-weight: bold; font-size: 17px; letter-spacing: 3px; padding: 8px 4px; }
  .label .sign { display: flex; justify-content: space-between; margin-top: 16px; font-size: 13px; }
  .label .sign div { border-top: 1px solid #000; padding-top: 3px; width: 45%; text-align: center; }
  .foot { width: 100mm; margin: 0 auto 24px; color: #555; font-size: 13px; line-height: 1.6; }
  @media print { body { background: #fff; } .foot { display: none; } }
"""

_TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Packing Label — {title}</title>
<style>{css}</style></head>
<body>
<div class="label">
  <h2>PACKING LABEL</h2>
  <p class="sub">Auto-filled from the saved COA page (LSE, per-page label)</p>
  {draft_banner}
  {warn_banner}
  <p class="item">{item}</p>
  <p class="pack">{customer}</p>
  <table>
{rows}  </table>
  <p class="src">{src}</p>
  {stamp}
  <div class="sign"><div>Prepared By</div><div>Authorised By</div></div>
</div>
<p class="foot"><b>How this label was made:</b> the COA page {page_label} was saved,
and this label auto-filled from that page's own edited fields — the GRAVORA
save-COA &#8594; label mechanism, one label per page. The link lives
in the database: labels(delivery_id, page_no) &#8594; this label ({label_no}).
{source_note}</p>
</body></html>
"""


def build_label(edited_values, *, template="supplier-foil", draft=None,
                demo_values=None, required=None):
    """Build the label for ONE edited page. See module docstring."""
    if template != "supplier-foil":
        raise ValueError(f"unknown template: {template!r}")
    if not isinstance(edited_values, dict):
        raise TypeError("edited_values must be a dict")
    page_key = edited_values.get("page_key")
    page_label = edited_values.get("page_label")
    if not page_key or not page_label:
        raise ValueError("edited_values needs 'page_key' and 'page_label'")
    is_draft = True if draft is None else bool(draft)
    if draft is None and "draft" in edited_values:
        is_draft = bool(edited_values["draft"])
    req = tuple(required) if required is not None else tuple(
        edited_values.get("required") or DEFAULT_REQUIRED
    )
    fields, unfilled, refused = _resolve_fields(
        edited_values, req, demo_values)
    by_key = {f["key"]: f for f in fields}

    def _cell(f):
        if f["filled"]:
            return f'<td class="from-coa"><b>{html.escape(str(f["new"]))}</b></td>'
        return f'<td class="unfilled">{html.escape(UNFILLED_TEXT)}</td>'

    def _row_label(key):
        f = by_key.get(key)
        if not f:
            return None
        lbl = f["label"]
        if key == "width":
            lbl = f"WIDTH ({page_label})"
        return lbl

    rows = []
    for f in fields:
        rows.append(
            f'    <tr><td class="k">{html.escape(_row_label(f["key"]))}</td>'
            f"{_cell(f)}</tr>"
        )
    # Source + label-number rows (identity, always shown).
    delivery = edited_values.get("delivery")
    label_no = edited_values.get("label_no")
    rows.append(
        '    <tr><td class="k">Source COA page</td><td>'
        + html.escape(
            f"{delivery} — {page_label} only (this pack's page)"
            if _is_filled(delivery)
            else f"{page_label} only (this pack's page)")
        + "</td></tr>"
    )
    rows.append(
        '    <tr><td class="k">Label</td>'
        + (f"<td>{html.escape(str(label_no))} (this page's own label)</td>"
           if _is_filled(label_no)
           else f'<td class="unfilled">{html.escape(UNFILLED_TEXT)}</td>')
        + "</tr>"
    )
    if not _is_filled(label_no):
        unfilled.append("label_no")

    item = by_key.get("item", {})
    customer = by_key.get("customer", {})
    title = (
        f"{item.get('new') or '—'} "
        f"(LSE delivery {delivery or '—'}, {page_label})"
    )
    audit = _audit_line(edited_values, fields)
    src_parts = [
        "This label was filled automatically when its COA page was saved:"
    ]
    if audit:
        src_parts.append(
            f"Batch/Lot and WIDTH are the <b>edited</b> values from the "
            f"live-scan page {html.escape(str(page_label))} ({audit}), "
            "not the old printed values."
        )
    else:
        src_parts.append(
            "Values below are the <b>edited</b> values from the live-scan "
            f"page {html.escape(str(page_label))}, not the old printed values."
        )
    if _is_filled(edited_values.get("delivery_id")):
        src_parts.append(
            f"Delivery id: {html.escape(str(edited_values['delivery_id']))}"
        )
    src = " ".join(src_parts)

    required_unfilled = [k for k in req if k in unfilled]
    is_printable = not required_unfilled and _is_filled(label_no)
    warn = ""
    if unfilled:
        warn = (
            '<div class="warn">⚠ এই লেবেলে '
            f"{len(unfilled)}টি ঘর খালি ({html.escape(', '.join(unfilled))})"
            " — ছাপার আগে পূরণ করুন। খালি ঘরে কোনো ডেমো মান বসানো হয়নি।</div>"
        )
    draft_banner = (
        '<div class="draft">খসড়া — DRAFT</div>' if is_draft else ""
    )
    stamp = (
        "" if is_draft else '<div class="stamp">QC PASSED</div>'
    )
    source_note = edited_values.get("source_note") or ""
    html_out = _TEMPLATE.format(
        title=html.escape(title),
        css=_CSS,
        draft_banner=draft_banner,
        warn_banner=warn,
        item=html.escape(str(item.get("new") or UNFILLED_TEXT)),
        customer=html.escape(str(customer.get("new") or UNFILLED_TEXT)),
        rows="\n".join(rows) + "\n",
        src=src,
        stamp=stamp,
        page_label=html.escape(str(page_label)),
        label_no=html.escape(str(label_no) if _is_filled(label_no)
                             else UNFILLED_TEXT),
        source_note=html.escape(str(source_note)),
    )
    return LabelResult(
        html=html_out,
        page_key=str(page_key),
        page_label=str(page_label),
        label_no=str(label_no) if _is_filled(label_no) else None,
        fields=fields,
        unfilled_fields=unfilled,
        refused_demo=refused,
        is_printable=is_printable,
        is_draft=is_draft,
        edits=list(edited_values.get("edits") or []),
    )


def build_label_html(edited_values, **kw):
    """``build_label(...).html`` — convenience wrapper."""
    return build_label(edited_values, **kw).html


# ---------------------------------------------------------------------------
# PDF (PyMuPDF; HTML path never needs it)
# ---------------------------------------------------------------------------

def build_label_pdf(edited_values, **kw):
    """Render the same label as PDF bytes (100 mm x 160 mm page).

    Drawn natively with PyMuPDF — no HTML engine, no network. Raises
    RuntimeError when PyMuPDF is not installed.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:  # pragma: no cover - env dependent
        raise RuntimeError(
            "build_label_pdf needs PyMuPDF (pip install PyMuPDF); "
            "build_label_html works without it"
        ) from exc
    res = build_label(edited_values, **kw)
    mm = 72 / 25.4
    doc = fitz.open()
    page = doc.new_page(width=100 * mm, height=160 * mm)
    x0, w = 28, 100 * mm - 56
    y = 30
    page.draw_rect(fitz.Rect(14, 14, 100 * mm - 14, 160 * mm - 14),
                   color=(0, 0, 0), width=2)
    if res.is_draft:
        page.insert_text((x0, y), "DRAFT — খসড়া", fontsize=13,
                         color=(0.57, 0.25, 0.05))
        y += 22
    page.insert_text((x0, y), "PACKING LABEL", fontsize=17, color=(0, 0, 0))
    y += 24
    page.draw_line((x0, y), (x0 + w, y), color=(0, 0, 0), width=1.5)
    y += 20
    for f in res.fields:
        label = f["label"]
        if f["key"] == "width":
            label = f"WIDTH ({res.page_label})"
        val = str(f["new"]) if f["filled"] else UNFILLED_TEXT
        page.insert_text((x0, y), f"{label}:", fontsize=10,
                         color=(0, 0, 0))
        y += 14
        page.insert_text((x0 + 8, y), val, fontsize=11,
                         color=(0, 0, 0) if f["filled"] else (0.72, 0.11, 0.11))
        y += 18
        if y > 160 * mm - 70:
            break
    page.insert_text(
        (x0, y + 4),
        f"Source: {res.page_label} only (this pack's page)"
        + (f" — {res.label_no}" if res.label_no else " — label no. not assigned"),
        fontsize=9, color=(0.3, 0.3, 0.3))
    if not res.is_printable:
        page.insert_text(
            (x0, y + 20),
            "NOT PRINTABLE — unfilled: " + ", ".join(res.unfilled_fields),
            fontsize=9, color=(0.72, 0.11, 0.11))
    elif not res.is_draft:
        page.insert_text((x0, y + 20), "QC PASSED", fontsize=13,
                         color=(0.08, 0.5, 0.24))
    return doc.tobytes()


# ---------------------------------------------------------------------------
# Save-record adapter (prototype / engine wiring bridge)
# ---------------------------------------------------------------------------

_CAMEL = {
    "pageKey": "page_key", "pageLabel": "page_label",
    "labelNo": "label_no", "deliveryId": "delivery_id",
    "pageNo": "page_no",
}


def edited_values_from_save_record(record):
    """Normalise a prototype/engine save record into ``edited_values``.

    Accepts the ``lse-edits-<page>.json`` shape (``page_key``,
    ``lot``/``width`` as ``{old, new, box300}``, ``edits`` list) and the
    live page's camelCase keys. Unknown keys pass through untouched.
    """
    if not isinstance(record, dict):
        raise TypeError("save record must be a dict")
    out = {}
    for k, v in record.items():
        out[_CAMEL.get(k, k)] = v
    if "page_key" not in out or "page_label" not in out:
        raise ValueError("save record needs 'page_key' and 'page_label'")
    return out


# ---------------------------------------------------------------------------
# Domino flow: save_with_label
# ---------------------------------------------------------------------------

def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def save_with_label(edited_values, out_dir, *, edited_pdf_path=None,
                    make_pdf=True, **kw):
    """Domino step: after the engine saves the edited PDF, build the label.

    Writes ``label-<page_key>.html`` (+ ``.pdf`` when ``make_pdf`` and
    PyMuPDF is available) and ``label-<page_key>.json`` (manifest) into
    ``out_dir``. The edited PDF is never copied or moved — only its
    path + SHA-256 are recorded. Returns the manifest dict.
    """
    values = edited_values_from_save_record(edited_values)
    res = build_label(values, **kw)
    os.makedirs(out_dir, exist_ok=True)
    base = f"label-{res.page_key}"
    html_path = os.path.join(out_dir, base + ".html")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(res.html)
    pdf_path = None
    if make_pdf:
        try:
            pdf_bytes = build_label_pdf(values, **kw)
        except RuntimeError:
            pdf_bytes = None
        if pdf_bytes is not None:
            pdf_path = os.path.join(out_dir, base + ".pdf")
            with open(pdf_path, "wb") as fh:
                fh.write(pdf_bytes)
    manifest = {
        "page_key": res.page_key,
        "page_label": res.page_label,
        "label_no": res.label_no,
        "is_printable": res.is_printable,
        "is_draft": res.is_draft,
        "unfilled_fields": list(res.unfilled_fields),
        "refused_demo": list(res.refused_demo),
        "fields": res.to_dict()["fields"],
        "edits": list(res.edits),
        "edited_values": values,
        "label_html": html_path,
        "label_pdf": pdf_path,
        "edited_pdf": edited_pdf_path,
        "edited_pdf_sha256": (
            _sha256_file(edited_pdf_path)
            if edited_pdf_path and os.path.exists(edited_pdf_path)
            else None
        ),
    }
    manifest_path = os.path.join(out_dir, base + ".json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    manifest["manifest"] = manifest_path
    return manifest


def build_labels_for_pages(pages, out_dir, **kw):
    """One :func:`save_with_label` per page (``page_key`` must be unique)."""
    seen = set()
    manifests = []
    for values in pages:
        key = values.get("page_key") or values.get("pageKey")
        if key in seen:
            raise ValueError(f"duplicate page_key: {key!r}")
        seen.add(key)
        manifests.append(save_with_label(values, out_dir, **kw))
    return manifests
