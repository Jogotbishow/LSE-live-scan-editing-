"""Multi-page LSE document — the engine's public API.

open_document(pdf) -> Document with one live page per source page.
Edit any word on any page; save() writes back the WHOLE document:
edited pages are rebuilt at native DPI from the original bytes
(overlay patches only), untouched pages are copied byte-identical,
and the delivery is permanently recorded (hash-chained) when a
database path is given.

Standing rule (user, 2026-11-06): preserve the document's FULL
originality — work at the original's DPI, never downscale, never
re-encode, never change resolution, for every document type.

The gate (gate.gate) runs per page at open and is stored on the page
as a DOCUMENTED QUALITY CHECK (ALLOW/REFUSE, T1 0.50). It is NOT a
ship-gate and it does not block open/edit/save — a REFUSE page simply
reports why (see DECISIONS.md).

Save -> label (Domino): ``Document.save_with_label()`` runs ``save()``
unchanged and then builds one packing label per edited page from that
page's own edited values, via the sibling ``label`` package
(``labels_from_manifest`` / ``edited_values_from_manifest`` below).
The label step never touches the save or the database.
"""
import base64
import io
import json
import os
import re
import sys

import cv2
import fitz
import numpy as np
from PIL import Image

from . import database
from .caps import fit_caps
from .gate import gate as gate_page
from .inpaint import clean_page
from .page import build_live_page, jpeg_b64, png_b64
from .segment import segment_array
from .writeback import (CapsDoesNotFitError, build_edited_pdf, native_dpi,
                        page_image_info, render_page, sha256_file)


def _hex_to_rgb(hexstr):
    h = hexstr.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def _page_sha_for_db(pg):
    """SHA-256 of a page's first image stream (its source identity)."""
    return getattr(pg, "source_image_sha256", "")


class Page:
    """One source page: seg + live page + gate verdict + edits."""

    def __init__(self, number, source_page, dpi, seg, words, style_info,
                 html_path, gate_verdict, gate_details, image, gray):
        self.number = number            # 1-based page number
        self.source_page = source_page  # 0-based index in the source PDF
        self.dpi = dpi
        self.seg = seg
        self.words = words              # live-page style dicts (x/y/w/h/...)
        self.style_info = style_info
        self.html_path = html_path
        self.gate_verdict = gate_verdict
        self.gate_details = gate_details
        self.image = image              # PIL RGB render at native DPI
        self.gray = gray                # grayscale numpy array
        self.edits = []                 # edit dicts (writeback contract)

    @property
    def n_words(self):
        return len(self.seg["words"])

    def word_box(self, word_index):
        return list(self.seg["words"][word_index]["box"])


class Document:
    """An opened scanned PDF, ready for live editing on any page."""

    def __init__(self, source_path, workdir, pages, source_label=None,
                 dna_regular=None, dna_bold=None, bold_mode="canonical"):
        self.source_path = os.path.abspath(source_path)
        self.source_label = source_label or os.path.basename(source_path)
        self.workdir = workdir
        self.pages = pages
        self.dna_regular = dna_regular
        self.dna_bold = dna_bold
        self.bold_mode = bold_mode
        self.source_sha256 = sha256_file(self.source_path)

    def __len__(self):
        return len(self.pages)

    def page(self, number):
        """Page by 1-based number."""
        if not 1 <= number <= len(self.pages):
            raise IndexError(f"page {number} out of range (1..{len(self.pages)})")
        return self.pages[number - 1]

    def edit(self, page_no, word_index, new_text, old_text="",
             row_label="", caps_mode="strict", allow_lowercase=False):
        """Retype one word on one page (caps proposal B enforced).

        ``page_no`` is 1-based; ``word_index`` indexes the page's seg
        words. Returns the stored edit dict. Raises CapsDoesNotFitError
        (with .suggestion) when a caps replacement does not fit its box
        and caps_mode is "strict" — unless allow_lowercase=True, in
        which case the lowercase suggestion is stored instead.
        """
        pg = self.page(page_no)
        word = pg.words[word_index]
        box = pg.word_box(word_index)
        w, h = box[2] - box[0], box[3] - box[1]
        bold = bool(word["bold"])
        ink_rgb = _hex_to_rgb(word["color"])
        from .writeback import pick_font
        font_path, _name = pick_font(new_text, bold, self.dna_regular, self.dna_bold)
        fs0 = round(h / 0.85, 1)
        decision = fit_caps(new_text, font_path, fs0, w)
        rendered_text = new_text
        caps_action = decision["action"]
        if decision["action"] == "suggest_lowercase" and decision["suggestion"]:
            if caps_mode == "strict" and not allow_lowercase:
                err = CapsDoesNotFitError(
                    f"caps {new_text!r} ({decision['width_px']}px) does not "
                    f"fit a {w}px box at {fs0}px; suggestion: "
                    f"{decision['suggestion']!r} — never squeezed, never shrunk")
                err.suggestion = decision["suggestion"]
                err.width_px = decision["width_px"]
                err.box_w_px = w
                raise err
            rendered_text = decision["suggestion"]
        edit = {"box": box, "line": pg.seg["words"][word_index].get("line"),
                "row_label": row_label, "old_text": old_text,
                "new_text": rendered_text, "typed_text": new_text,
                "caps_action": caps_action, "bold": bold,
                "ink_rgb": ink_rgb, "word_index": word_index}
        pg.edits.append(edit)
        return edit

    def save(self, out_path, delivery_id=None, db_path=None, actor="qc",
             client="", item="", document_type="supplier COA",
             customer="", caps_mode="strict"):
        """Write back the WHOLE document (edited + untouched pages).

        Returns the write-back manifest. When ``db_path`` is given, the
        delivery is recorded in that SQLite database (hash-chained,
        one label per page) and the manifest gains delivery_id/number/
        label_numbers.
        """
        delivery_id = delivery_id or database.new_id("LSE-DEL")
        pages_edits = {}
        for pg in self.pages:
            if pg.edits:
                pages_edits[pg.source_page] = {
                    "image": pg.image, "gray": pg.gray,
                    "dpi": pg.dpi, "edits": pg.edits}
        manifest = build_edited_pdf(
            self.source_path, pages_edits, out_path, delivery_id,
            source_label=self.source_label, actor=actor,
            dna_regular=self.dna_regular, dna_bold=self.dna_bold,
            caps_mode=caps_mode)
        manifest["delivery_id"] = delivery_id
        if db_path:
            # The DB wants the PATCH records (font + font_size_px, from
            # build_patch), not the raw edit dicts from Document.edit()
            # (which have no font fields). manifest["edits"] carries
            # one record per applied patch, with a 1-based "page".
            recs_by_page = {}
            for r in manifest.get("edits", []):
                recs_by_page.setdefault(r["page"], []).append(r)
            pages_rec, labels_rec = [], []
            for pg in self.pages:
                lot = next((e["new_text"] for e in pg.edits
                            if e["row_label"] == "Lot No."), None)
                wid = next((e["new_text"] for e in pg.edits
                            if e["row_label"] == "02. WIDTH — observation"), None)
                pages_rec.append({
                    "page_no": pg.number, "source_page": pg.source_page,
                    "source_document": self.source_label,
                    "source_sha256": _page_sha_for_db(pg),
                    "output_pdf_name": os.path.basename(out_path),
                    "page_pdf_sha256": manifest["pdf_sha256"],
                    "edits": recs_by_page.get(pg.number, [])})
                labels_rec.append({
                    "page_no": pg.number, "source_page": pg.source_page,
                    "source_document": self.source_label,
                    "item": item, "customer": customer,
                    "batch_no": lot, "width_mm": wid,
                    "label_html_name": None, "label_pdf_name": None,
                    "label_pdf_sha256": None})
            c = database.init_db(db_path)
            try:
                _did, number, label_numbers = database.record_multipage_delivery(
                    c,
                    {"id": delivery_id, "client": client, "item": item,
                     "document_type": document_type,
                     "source_document": self.source_label,
                     "source_page": 1, "source_sha256": self.source_sha256,
                     "output_pdf_name": os.path.basename(out_path),
                     "output_pdf_sha256": manifest["pdf_sha256"],
                     "lse_version": manifest["lse_version"]},
                    pages_rec, labels_rec, actor=actor)
            finally:
                c.close()
            manifest["delivery_number"] = number
            manifest["label_numbers"] = label_numbers
        return manifest

    def save_with_label(self, out_path, label_dir=None, *, db_path=None,
                        delivery_id=None, actor="qc", client="", item="",
                        document_type="supplier COA", customer="",
                        supplier="", draft=True, demo_values=None,
                        caps_mode="strict"):
        """Save the WHOLE document, then build one label per edited page.

        Runs :meth:`save` unchanged (same manifest, same DB records —
        the label step never touches the save or the database), then
        writes the label Domino into ``label_dir`` (default
        ``<out-dir>/labels``) via :func:`labels_from_manifest`:
        one ``label-<page_key>.{html,pdf,json}`` per edited page, from
        that page's own edited values only. ``label_no`` comes from
        the DB-issued label numbers when ``db_path`` is given; without
        a database it stays unfilled (never auto-generated) and the
        label reports itself not printable. Returns the save manifest
        with two added keys: ``"labels"`` (the per-page label
        manifests, in page order — ``[]`` when nothing was edited)
        and ``"label_dir"``.
        """
        manifest = self.save(out_path, delivery_id=delivery_id,
                             db_path=db_path, actor=actor, client=client,
                             item=item, document_type=document_type,
                             customer=customer, caps_mode=caps_mode)
        if label_dir is None:
            label_dir = os.path.join(
                os.path.dirname(os.path.abspath(out_path)), "labels")
        stem = os.path.splitext(os.path.basename(self.source_path))[0]
        manifest["labels"] = labels_from_manifest(
            manifest, label_dir,
            edited_pdf_path=os.path.abspath(out_path),
            item=item, customer=customer, supplier=supplier,
            source_stem=stem, draft=draft, demo_values=demo_values,
            dpi_by_page={pg.number: pg.dpi for pg in self.pages})
        manifest["label_dir"] = label_dir
        return manifest


def _field_for_row_label(row_label):
    """Map an edit's row_label to a label field key, or None.

    The label's Domino fields are Lot / Batch / WIDTH / Thickness /
    ... — the row_labels the engine already uses are "Lot No." and
    "02. WIDTH — observation" (see Document.save's DB linkage); this
    table covers those plus the other supplier-foil rows by substring,
    so a caller that labels its edits gets the right label row without
    the engine ever guessing a value. An unmapped, non-empty row_label
    is NOT dropped — it becomes an extra_fields row under its own
    label (see edited_values_from_manifest).
    """
    s = re.sub(r"[^a-z0-9]+", " ", (row_label or "").lower()).strip()
    if not s:
        return None
    if s in ("lot no", "lot", "lot number"):
        return "lot"
    if s in ("batch no", "batch", "batch number",
             "supplier batch no", "supplier batch"):
        return "batch"
    if "width" in s:
        return "width"
    if "thickness" in s:
        return "thickness"
    if "material code" in s:
        return "material_code"
    if "version" in s:
        return "version"
    if "gross" in s:
        return "gross_weight"
    if "net" in s:
        return "net_weight"
    if "packs" in s:
        return "packs"
    if "expiry" in s:
        return "expiry_date"
    if "mfg" in s or "manufactur" in s or "production" in s:
        return "mfg_date"
    if s == "date":
        return "date"
    if s in ("item", "product"):
        return "item"
    if "customer" in s:
        return "customer"
    if "supplier" in s:
        return "supplier"
    return None


def _box300(box, dpi):
    """A word box in native render coordinates -> 300-DPI coordinates.

    The label records ``box300`` (the prototype save-record shape).
    At the usual native 300 DPI this is the identity; at any other
    native DPI it is a plain scale — the pixels are never touched,
    only the recorded coordinates change.
    """
    scale = 300.0 / (dpi or 300)
    return [round(c * scale) for c in box]


def edited_values_from_manifest(manifest, *, item="", customer="",
                                supplier="", source_stem=None,
                                delivery=None, draft=True,
                                label_numbers=None, dpi_by_page=None,
                                page_key_fmt="{stem}-p{n}",
                                page_label_fmt="{stem} p.{n}"):
    """Build one label ``edited_values`` dict per EDITED page.

    Pure function over a :meth:`Document.save` manifest — it reads
    only ``manifest["edits"]`` (one record per applied patch, with a
    1-based ``"page"``), plus ``delivery_id`` / ``delivery_number`` /
    ``label_numbers`` when present. No file is written, no value is
    invented: a field with no edit on that page stays absent (the
    label renders it as unfilled), ``label_no`` comes only from the
    DB-issued ``label_numbers`` (in page order, so page *n* takes
    ``label_numbers[n - 1]``) and is None without a database, and
    every value comes from that page's own edits — never another
    page's, never a demo value.
    """
    edits = manifest.get("edits") or []
    by_page = {}
    for rec in edits:
        by_page.setdefault(rec["page"], []).append(rec)
    label_numbers = label_numbers if label_numbers is not None \
        else manifest.get("label_numbers") or []
    delivery = delivery if delivery is not None \
        else manifest.get("delivery_number")
    stem = source_stem or "document"
    out = []
    for n in sorted(by_page):
        dpi = (dpi_by_page or {}).get(n, 300)
        values = {
            "page_key": page_key_fmt.format(stem=stem, n=n),
            "page_label": page_label_fmt.format(stem=stem, n=n),
            "page_no": n,
            "delivery": delivery,
            "delivery_id": manifest.get("delivery_id"),
            "label_no": (label_numbers[n - 1]
                         if 0 < n <= len(label_numbers) else None),
            "item": item or None,
            "customer": customer or None,
            "supplier": supplier or None,
            "draft": draft,
            "edits": [],
            "extra_fields": {},
            "source_note": (f"Source: {stem}, page {n} "
                            "(this pack's page)"),
        }
        for rec in by_page[n]:
            old = (rec.get("old_text") or "").strip() or None
            new = (rec.get("new_text") or "").strip()
            if not new:
                continue
            box300 = _box300(rec.get("box") or [], dpi)
            row_label = (rec.get("row_label") or "").strip()
            field = _field_for_row_label(row_label)
            value = {"old": old, "new": new, "box300": box300}
            if field is not None:
                values[field] = value  # last edit to a field wins
            elif row_label:
                values["extra_fields"][row_label] = value
            values["edits"].append({
                "field": field or row_label or "edited word",
                "old": old, "new": new, "box300": box300})
        if not values["extra_fields"]:
            del values["extra_fields"]
        out.append(values)
    return out


def _load_label_module():
    """Import the sibling ``label`` package (repo root, next to ``lse``).

    The engine does not depend on the label package at import time —
    only the Domino step needs it. When the repo layout is in use,
    ``label/`` sits next to ``lse/``; if it is not importable yet,
    its parent directory is added to ``sys.path`` once and the import
    is retried. Raises a clear RuntimeError when it is genuinely
    absent, instead of silently skipping the label.
    """
    try:
        from label import save_with_label as label_save
        from label import edited_values_from_save_record as adapter
        return label_save, adapter
    except ImportError:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        try:
            from label import save_with_label as label_save
            from label import edited_values_from_save_record as adapter
            return label_save, adapter
        except ImportError as exc:
            raise RuntimeError(
                "save -> label needs the sibling 'label' package "
                "(lse-opensource/label/ next to lse/); it was not found "
                f"on sys.path (tried repo root {repo_root!r})"
            ) from exc


def labels_from_manifest(manifest, label_dir, *, edited_pdf_path=None,
                         make_pdf=True, demo_values=None, **values_kw):
    """Write one label per edited page from a save() manifest.

    Builds the per-page ``edited_values`` with
    :func:`edited_values_from_manifest` (``**values_kw`` are its
    keyword arguments: ``item``, ``customer``, ``supplier``,
    ``source_stem``, ``delivery``, ``draft``, ``label_numbers``,
    ``dpi_by_page``, ``page_key_fmt``, ``page_label_fmt``) and calls
    the label package's ``save_with_label`` once per edited page into
    ``label_dir``. ``edited_pdf_path`` (default:
    ``manifest["pdf_path"]``) is recorded in each label manifest as
    path + SHA-256; the edited PDF itself is never copied or moved.
    ``demo_values`` are passed through to the label builder (a field
    whose new value equals a known demo string is refused and reported,
    never printed). Returns the list of per-page label manifests, in
    page order (``[]`` when nothing was edited).
    """
    label_save, adapter = _load_label_module()
    edited_pdf_path = edited_pdf_path or manifest.get("pdf_path")
    manifests = []
    for values in edited_values_from_manifest(manifest, **values_kw):
        manifests.append(label_save(
            adapter(values), label_dir,
            edited_pdf_path=edited_pdf_path, make_pdf=make_pdf,
            demo_values=demo_values))
    return manifests


def open_document(pdf_path, workdir=None, item="", dna_regular=None,
                  dna_bold=None, bold_mode="canonical", anchor_box=None,
                  stamps=None, page_label_fmt="{stem} p.{n}"):
    """Open a scanned PDF: per-page segmentation + live pages + gate.

    ``workdir`` (default ``<pdf-stem>.lse/`` next to the PDF) receives
    one live-page HTML per source page (``live-p{n}.html``) and
    ``state.json`` (source path + edit list, for the CLI).
    Returns a Document. Raises FileNotFoundError for a missing PDF.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(pdf_path)
    pdf_path = os.path.abspath(pdf_path)
    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    if workdir is None:
        workdir = os.path.join(os.path.dirname(pdf_path), stem + ".lse")
    os.makedirs(workdir, exist_ok=True)
    src = fitz.open(pdf_path)
    pages = []
    try:
        for pageno in range(len(src)):
            dpi = native_dpi(src, pageno)
            image, gray, dpi = render_page(src, pageno, dpi=dpi)
            color = np.array(image)
            img_bgr = cv2.cvtColor(color, cv2.COLOR_RGB2BGR)
            seg = segment_array(img_bgr, image_name=f"{stem} p.{pageno + 1}")
            clean, _info = clean_page(img_bgr, seg["words"])
            clean_pil = Image.fromarray(cv2.cvtColor(clean, cv2.COLOR_BGR2RGB))
            # Original bytes for the live-page background: JPEG streams
            # verbatim; anything else -> lossless PNG of the render
            # (same rule as the prototype: May's CCITT decode is PNG).
            imgs = page_image_info(src, pageno)
            if imgs and imgs[0]["ext"] == "jpg":
                orig_b64 = ("data:image/jpeg;base64," +
                            base64.b64encode(imgs[0]["stream"]).decode())
                clean_b64 = jpeg_b64(clean_pil, q=88)
            else:
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                orig_b64 = ("data:image/png;base64," +
                            base64.b64encode(buf.getvalue()).decode())
                buf2 = io.BytesIO()
                clean_pil.save(buf2, format="PNG")
                clean_b64 = ("data:image/png;base64," +
                             base64.b64encode(buf2.getvalue()).decode())
            page_meta = {"page_key": f"{stem}-p{pageno + 1}",
                         "page_no": pageno + 1, "source_page": pageno + 1,
                         "source_document": f"{os.path.basename(pdf_path)} p.{pageno + 1}",
                         "item": item,
                         "page_label": page_label_fmt.format(stem=stem, n=pageno + 1),
                         "old_lot": "", "old_width": ""}
            html_path = os.path.join(workdir, f"live-p{pageno + 1}.html")
            _path, words, style_info = build_live_page(
                gray, color, seg, orig_b64, clean_b64, clean_b64,
                page_meta, html_path, skew_deg=0.0, bold_mode=bold_mode,
                anchor_box=anchor_box, stamps=stamps,
                dna_regular=dna_regular, dna_bold=dna_bold)
            verdict, details = gate_page(img_bgr, seg)
            pages.append(Page(pageno + 1, pageno, dpi, seg, words,
                              style_info, html_path, verdict, details,
                              image, gray))
    finally:
        src.close()
    doc = Document(pdf_path, workdir, pages,
                   dna_regular=dna_regular, dna_bold=dna_bold,
                   bold_mode=bold_mode)
    # store the per-page image SHAs on the pages for the DB record
    src = fitz.open(pdf_path)
    try:
        for pg in pages:
            infos = page_image_info(src, pg.source_page)
            pg.source_image_sha256 = infos[0]["stream_sha256"] if infos else doc.source_sha256
    finally:
        src.close()
    doc.save_state()
    return doc


def _save_state(self):
    state = {"source_path": self.source_path,
             "source_label": self.source_label,
             "workdir": self.workdir,
             "dna_regular": self.dna_regular, "dna_bold": self.dna_bold,
             "bold_mode": self.bold_mode,
             "edits": [{"page": e_page, **e}
                       for pg in self.pages for e_page in [pg.number]
                       for e in pg.edits]}
    with open(os.path.join(self.workdir, "state.json"), "w") as f:
        json.dump(state, f, indent=1)
    return state


Document.save_state = _save_state


def load_document(workdir, item=""):
    """Re-open a Document from a workdir state.json (re-segments the
    source PDF deterministically, then re-applies the stored edits)."""
    with open(os.path.join(workdir, "state.json")) as f:
        state = json.load(f)
    doc = open_document(state["source_path"], workdir=workdir, item=item,
                        dna_regular=state.get("dna_regular"),
                        dna_bold=state.get("dna_bold"),
                        bold_mode=state.get("bold_mode", "canonical"))
    for e in state.get("edits", []):
        pg = doc.page(e["page"])
        pg.edits.append({k: v for k, v in e.items() if k != "page"})
    doc.save_state()  # re-persist (open_document overwrote state.json)
    return doc
