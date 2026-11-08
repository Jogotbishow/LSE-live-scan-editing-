# LSE engine — API

`lse` is the standalone Live-Scan Editing engine: edit the text on a
scanned document **without OCR, without rebuilding the page**. The scan
IS the page; text is a living layer on top of the original pixels.

Standing rule (user, 2026-11-06): preserve the document's FULL
originality — work at the original's DPI, never downscale, never
re-encode, never change resolution, for every document type.

## Install

Python 3.10+, plus:

```
pip install pymupdf opencv-python-headless numpy pillow fonttools vtracer
```

(`vtracer` only for `lse.dna`; `tesseract` is optional, for the
0-vs-180 flip in `lse.rotate` — without it rotation falls back to
projection + flip3.) No OCR library is used or required anywhere.

## Quick start

```python
from lse import open_document

doc = open_document("PG AUGUST-2026 (25mic) COA.pdf",
                    workdir="/tmp/aug.lse",
                    dna_regular="dna-clone-regular-600.ttf",
                    dna_bold="dna-clone-bold-600.ttf")
print(len(doc), "pages")                       # 8
print(doc.page(1).n_words)                     # 302
print(doc.page(1).gate_verdict)                # ALLOW / REFUSE (quality check)

lot = next(i for i, w in enumerate(doc.page(1).seg["words"])
           if w["box"] == [533, 930, 631, 966])
doc.edit(1, lot, "207/9", old_text="206/7", row_label="Lot No.")

manifest = doc.save("/tmp/aug-edited.pdf", db_path="/tmp/lse.db",
                    client="PG Foils", item="Blister Foil 25 Micron (PG Foils)",
                    customer="Packfirm Limited")
print(manifest["delivery_number"], manifest["label_numbers"])
```

Live pages: `workdir/live-p{n}.html` — one per source page. Open in a
browser, click any word, retype. (The page's save flow stores the
edits in `localStorage`; the Python `edit()` above is the same
operation from code.)

## CLI

```
python -m lse open PDF [--workdir DIR] [--item TEXT]
                [--dna-regular TTF --dna-bold TTF]
                [--bold-mode canonical|anchor|none]
                [--anchor-box x0,y0,x1,y1]
python -m lse edit --workdir DIR --page N --word I --new TEXT
                [--old TEXT] [--row-label TEXT] [--allow-lowercase]
python -m lse save --workdir DIR --out OUT.pdf [--db DB.sqlite]
                [--client TEXT --item TEXT --customer TEXT]
python -m lse gate --workdir DIR
```

`open` segments every page at native DPI and writes `state.json`;
`edit` re-opens from `state.json` and stores one more edit; `save`
writes back the whole document.

## `Document` / `open_document()`

- `open_document(pdf_path, workdir=None, item="", dna_regular=None,
  dna_bold=None, bold_mode="canonical", anchor_box=None, stamps=None)`
  — per page: native-DPI render → `segment_array()` → `clean_page()`
  (inpaint) → `build_live_page()` → `gate_page()`. Native DPI comes from
  the PDF page itself; the live page is the original scan, never a
  re-encode. (The function is `lse.gate.gate()` in its module; it is
  exported at top level as `gate_page` so the name `lse.gate` stays the
  module — a top-level export named `gate` would shadow it.)
  the page image (pixel width / page width in inches), default 300.
  `workdir` defaults to `<pdf-stem>.lse/` next to the PDF.
- `doc.page(n)` (1-based) → `Page` with `.seg`, `.words` (live-page
  styles), `.html_path`, `.gate_verdict`, `.gate_details`, `.dpi`,
  `.edits`, `.image` (PIL RGB), `.gray`.
- `doc.edit(page_no, word_index, new_text, old_text="",
  row_label="", caps_mode="strict", allow_lowercase=False)` — retype
  one word. Caps proposal B is enforced (see `lse.caps`): a caps
  replacement that does not fit raises `CapsDoesNotFitError` (with
  `.suggestion`); with `allow_lowercase=True` the lowercase suggestion
  is stored instead. Returns the edit dict.
- `doc.save(out_path, delivery_id=None, db_path=None, actor="qc",
  client="", item="", document_type="supplier COA", customer="",
  caps_mode="strict")` — writes back the WHOLE document and returns
  the manifest (`pdf_sha256`, `pages`, `source_pages`,
  `edited_pages`, `edits`, plus `delivery_number` / `label_numbers`
  when `db_path` is given).
  - Untouched pages are copied verbatim (`insert_pdf` — image streams
    byte-identical, rendered pixels identical).
  - Edited pages are copied verbatim first, then only small overlay
    patches are drawn (original crop +3 px, Telea-inpainted, Grain v2,
    new word in Document DNA). Nothing else is touched.
  - Output layout: `[source pages in order] + [one unedited audit
    copy per edited page] + [edit certificate]`. Attachments:
    `lse-edits.json` + verbatim original scan-image streams
    (`lse-original-scan-p{n}.*`).
  - With `db_path`: one delivery + one page row per source page + one
    label per page (batch/width from that page's Lot/WIDTH edits) +
    hash-chained audit events.
- `doc.save_with_label(out_path, label_dir=None, db_path=None, ...)`
  — runs `save()` unchanged (same manifest, same DB records), then
  builds one packing label per edited page into `label_dir`
  (default `<out-dir>/labels`) from that page's own edited values,
  via the sibling `label` package. Returns the save manifest with
  two added keys: `"labels"` (the per-page label manifests, in page
  order — `[]` when nothing was edited) and `"label_dir"`. See
  "Save → label (Domino)" below.
- `load_document(workdir, item="")` — re-open from `state.json`
  (re-segments deterministically, re-applies stored edits).

## Save → label (Domino)

`lse.document.edited_values_from_manifest(manifest, ...)` builds one
label `edited_values` dict per edited page from a `save()` manifest
(pure — writes nothing); `lse.document.labels_from_manifest(manifest,
label_dir, ...)` writes one `label-<page_key>.{html,pdf,json}` per
edited page through the `label` package; `Document.save_with_label()`
is the one-call entry point (save, then labels). The `label` package
is imported lazily — only this step needs it — from the repo root
next to `lse/`; when it is genuinely absent the call raises a clear
`RuntimeError` instead of silently skipping the label.

Rules of the wiring (the label's own rules still apply inside it):

- **One label per edited page.** Values come only from that page's
  `manifest["edits"]` (1-based `"page"`, native-DPI `"box"` scaled
  to `box300`); a field with no edit on that page stays absent and
  renders unfilled — never another page's value, never a demo value.
- **Row-label mapping.** An edit's `row_label` decides its label
  row: `"Lot No."` → `lot`, `"02. WIDTH — observation"` → `width`,
  `"Batch No."` / `"Supplier Batch No"` → `batch`, plus Thickness,
  Material Code, Version, Gross/Net Weight, Packs, Expiry, Mfg,
  Date, Item, Customer, Supplier. A labelled edit that maps to no
  field becomes an `extra_fields` row under its own label; an
  unlabelled edit still appears in the audit line. Lot and Batch are
  never merged.
- **`label_no` is never invented.** It comes only from the DB-issued
  `manifest["label_numbers"]` (page order — page *n* takes
  `label_numbers[n - 1]`); without a database it stays unfilled and
  the label reports itself not printable.
- **The DB is untouched by the label step.** The DB label rows keep
  `label_html_name` / `label_pdf_name` NULL (they are immutable
  once issued); the linkage lives in the label's own
  `label-<page_key>.json` manifest (delivery + label numbers,
  edited-PDF SHA-256, resolved fields).
- **No reassembly.** When the segmenter splits one hyphenated value
  into pieces (ACME: `ACME-2026-0001` → `ACME` / `2026` / `0001`),
  each edited piece maps on its own — the wiring never guesses the
  joins back together. The label carries the edited piece.

## Module map

| module | what it is (prototype source) |
|---|---|
| `segment` | word segmentation, connected components, NO recognition (v5-300, `segment.py`) |
| `inpaint` | Telea erase + title bar + underline re-draw + Grain v2 (`inpaint.py` v4) |
| `heading` | H1 grey-bar / H2 table-header detection (`heading.py`) |
| `deskew` | projection-profile skew estimate + correct (`improve/round2/deskew.py`) |
| `rotate` | rotation detection: projection axis + OSD flip + flip3 override (`rotate_detect.py`; Tesseract optional) |
| `ccmask` | dark-core CCs, core assignment, -2 fused cores, full-page clean (R15/R16) |
| `gate` | seg-completeness gate T1/T2 + full-page mask (R17 `gate_ccmask.py`) — quality check only, T1 0.50 |
| `vocab_gate` | vocabulary gate: merge over-splits by cross-page signature (R6, `vocab_gate.py`) |
| `page` | live-page builder: per-word style from pixels + HTML template (`build_page300.py` v8) |
| `dna` | Document DNA font build from median glyphs, vtracer (`dna-build-prod.py`) |
| `_tracer` | SVG path parse + TTF assembly + font measurement (`tracer-spike.py`) |
| `caps` | caps retype rule, proposal B (`caps_test.py` evidence) |
| `writeback` | multi-page native-DPI PDF write-back, patches (`lse_writeback_300.py` v2.1 lineage) |
| `database` | SQLite record, schema v3, hash-chained audit, one label per page (`lse_db.py` + `lse_db3.py`) |
| `document` | multi-page Document API (new) |
| `__main__` | CLI: `open | edit | save | gate` |

## What is NOT in this package (honest limits)

- **DBNet cross-check validator / font shortlist** (`improve/round2/
  conf.py`, `matcher.py`): PG-specific (hardcoded paths + per-template
  validator boxes). `page.word_styles()` defaults every word's
  confidence tier to `"check"` unless the caller supplies tiers, and
  the font shortlist defaults to `[]`. The live page works without
  them; the confidence overlay just shows "check" everywhere.
- **Single-word CC-mask erase** (`erase_word`, `ref_masks_fixed`,
  `protect_mask` from R16): not ported — the write-back uses the
  box-based patch path (v2.1), which is the verified one.
- **Universality**: segmentation is proven on the PG COA format
  (302/302 on p1, all 14 pages match r10m). On other printed
  documents it is weak (94/182 on FUNSD/SROIE/Tottel/Shields — see
  DECISIONS.md); cursive handwriting is out of scope.
- **Print calibration** and the **US patent check** are the user's
  (physical / legal) — not done here, by design.
- **LSE label (Domino)**: wired in — `Document.save_with_label()`
  (see "Save → label (Domino)" above) builds the per-page label
  artifacts from the save manifest; the label package itself lives
  in `label/` next to `lse/`.

## Verification

```
<venv>/bin/python tests/run_all.py          # full suite
<venv>/bin/python tests/run_all.py --fast   # skip Playwright + full-doc runs
```

Tests re-run everything on the real PG PDFs (read-only) and report
their own numbers: segmentation counts, -2 band numbers, caps
re-measurement, fontfix 43/43 (Playwright, pages built by this
package), multi-page open/edit/save with untouched-page byte/pixel
checks and staging-DB chain verification, DNA rebuild IoU.
