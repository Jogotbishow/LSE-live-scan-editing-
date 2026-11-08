# DECISIONS.md — LSE engine package

Reversible decisions applied in this package (2026-11-08, LSE
completion). Each names its evidence, what changes, and how to undo
it. Nothing here decides Q-03–Q-09 or ★2–★8 — those are the user's.

## 1. -2 band rule — ACCEPTED

**Rule:** exclude band-shaped -2 (ambiguous/fused) cores with `cw >
120` from the mask, where the -2 cores are computed for the gate/mask
(`lse/gate.py::full_page_mask`, `lse/ccmask.py::full_page_clean`).

**Evidence (R18 Track B, re-measured in `tests/test_gate.py`):**
May's dotted title band is 449 px wide — a highlight, not a word;
fused-letter -2 cores are ≤ 78 px; bands are ≥ 307 px; 120 sits
cleanly in the 78 → 307 gap. Whole-core exclusion would remove
~13,229 mask px on May p1.

**Surgical refinement (2026-11-08, measured):** the band core is
FUSED with the title letters — at CORE_THR=140 the dotted band and
the title words are a single connected component (box [1007, 584,
1456, 635], area 11,451 px). Whole-core exclusion left 3 title words
with < 50% of their ink covered by the mask (their letters would not
be erased if edited). So the exclusion is surgical: the part of the
core INSIDE word boxes is kept (those pixels are letters), only the
part OUTSIDE word boxes is dropped (the highlight dots). May p1 mask
then shrinks by 4,845 px (dots only), and 0 words lose coverage.
Implemented identically in `gate.full_page_mask` and
`ccmask.full_page_clean`.

**What changes:** the mask no longer erases the title highlight band
when a full-page clean is built. The seg is untouched (the rule never
removes or merges a word box) — verified in tests: May p1 word count
unchanged and every word's ink stays ≥ 50% covered by the ruled mask.

**How to undo:** set `BAND_CORE_MIN_W` to a huge number in
`lse/gate.py` / `lse/ccmask.py` (or delete the two `if wi == -2`
blocks); the pre-rule mask is reproducible via
`gate.mask_px_with_without_band()`.

## 2. Caps — proposal B (never force caps)

**Rule:** when replacement text in CAPS does not fit the word box,
suggest lowercase instead of forcing/squeezing caps. Default: caps
only where they fit, else lowercase suggestion.

**Evidence (R18 Track C `caps_test.py`, re-measured in
`tests/test_caps.py` with the write-back's own ruler — PIL getlength
at `int(round(fs0))`):** a 64 px slot fits no font for "AND" at 37 px
cap height — DejaVu Bold 129 px, narrowest Noto Sans ExtraCondensed
Bold 90 px, DNA Bold 106 px (direct render; R18's 87–91 px was an
ink-based estimate, the conclusion is unchanged). Squeeze
×0.525/×0.744; shrink-to-fit breaks the cap-height match (37 →
19.4 px). Even lowercase "and" is 77–83 px at fs0 — it does not fit
at cap-height size either; the mechanism-grounded difference is the
width-fit floor (0.75×): "and" renders 62.1 px at the floor (inside
a 64 px box), caps "AND" renders 79.9 px (outside it).

**What changes:** `lse/caps.py::fit_caps()` returns
`suggest_lowercase` (never a squeeze); `lse/writeback.py::build_patch()`
and `lse/document.py::Document.edit()` enforce it — `strict` mode
raises `CapsDoesNotFitError` (carrying `.suggestion`), and the
fitted size may never go below `fs0` for caps (that would be
shrink-to-fit by another name). Proposal A (ExtraCondensed + widened
92 px slot + user confirmation) stays available as an explicit
caller opt-in (`allow_widen_slot=True` / `allow_lowercase=True`) —
the engine never widens a slot by itself.

**How to undo:** pass `caps_mode="suggest_lowercase"` (render the
suggestion silently — not recommended on issued COAs) or, for
proposal A, confirm a widened slot with the user and pass
`allow_widen_slot=True`.

## 3. Gate — documented quality check, NOT a ship-gate

**Rule:** the R17 gate (`lse/gate.py::gate`, T1 0.50) stays exactly as
measured: ALLOW/REFUSE per page, T1 threshold **0.50 unchanged**.
It runs at `open_document()` and its verdict is stored on the page;
it does NOT block open/edit/save.

**Evidence:** R18 batch on 25 new Raviraj pages: 9 ALLOW / 16 REFUSE
(the seg is the gap, the gate is correct); T1 margin is thin (0.025)
— that is why promotion is NOT done here.

**How to undo / promote:** promotion to a ship-gate is a product
decision for the user (it needs the T1 margin question settled);
the code change would be one `if` in `Document.save()` — deliberately
not made here.

## 4. Bold — Lot-anchor (PG-only) + heading flip; no automatic bold detection on new templates

**Rule (R18 Track C acceptance):** bold comes from (a) a
known-regular-word anchor (PG: the Lot value word) or (b) heading
flip (H1/H2 lines from `lse/heading.py`). No new automatic bold
signal: RULEMASK-STROKE measured 14/29 with 17 FPs and 0/6 pages
separated — three independent measurement families failed for the
same structural reason (May bold ≈ anchor, 1.00–1.04 vs regular
1.06–1.08).

**What changes in code (`lse/page.py::word_styles`,
`bold_mode=`):**
- `"canonical"` (default): page-median stroke ratio × 1.15 +
  heading flip — exactly the merged builder's rule, the rule the
  verified 43/43 fontfix pages were built with.
- `"anchor"` (PG-only): caller supplies `anchor_box` (known-regular
  word); threshold = anchor ratio × 1.15 + heading flip. R18's
  measured Lot-anchor hold margin (0.036) is recorded as
  `LOT_ANCHOR_HOLD` and reported as a diagnostic.
- `"none"` (new templates without an anchor): no automatic bold
  detection at all — bold only from heading-flip lines.

**How to undo:** `bold_mode` is a per-call parameter; switching it
changes nothing else.

## 5. Multi-page write-back design

**Rule:** untouched pages are copied verbatim (`insert_pdf` — image
streams byte-identical); edited pages are copied verbatim first and
only small overlay patches are drawn. One output PDF per document:
`[source pages] + [unedited audit copy per edited page] + [edit
certificate]`, with `lse-edits.json` + verbatim original scan-image
streams attached. This generalises the v2.1 single-page rebuild
(no 200→300 affine is needed anymore — seg boxes are native render
coordinates).

**How to undo:** the single-page v2.1 builder is preserved in the
prototype (`lse_writeback_300.py`); this package's `build_edited_pdf`
is its multi-page successor, not a fork of its outputs.

## 6. Database — clean schema v3 (no migration)

The prototype reached v3 by migration (v1 → v2 → v3). This package
ships the v3 schema directly (deliveries + delivery_pages + labels
with page_no/source_page/source_document + lse_edits + hash-chained
audit_log). Hash formulas are unchanged (label_hash is the frozen v2
formula; delivery_hash is the v3 formula including the per-page
labels list). One label per page; `deliveries.label_ref` is the p.1
label. Labels carry batch/width from the page's Lot/WIDTH edits (NULL
when the page has none); the label artifact itself is issued by the
caller.

## 7. Save → label (Domino) wiring — engine calls the label package

**Rule (2026-11-08, integration):** `Document.save_with_label()`
runs `save()` first, byte-for-byte the same call (same manifest, same
DB records — verified in `tests/test_save_label.py` by a second plain
`save()` of the same edits carrying identical patch records and no
`"labels"` key), and only then builds the labels as a post-save step
(`lse/document.py::edited_values_from_manifest`,
`labels_from_manifest`, `Document.save_with_label`). The label
package is imported lazily, only by this step; `save()` itself never
imports it.

**Evidence (own re-run, `tests/test_save_label.py`, 5/5):** ACME
synthetic — Batch tail `0001 → 0002`, Lot tail `77 → 78`, Thickness
`25.2 → 25.4`, all three EDITED values in the label, old values only
in the audit line, `label_no` unfilled (no DB, never invented);
real PG Aug p.1 — Lot `206/7 → 207/9`, WIDTH `780.0 → 781.5`,
`LBL-0001`, printable, DB chain ok (10 entries), v3 hash ok, and the
DB p.1 label carries batch `207/9` / width `781.5`.

**What changes:** `lse/document.py` gains the three functions above
(plus the row-label → field table); `tests/test_save_label.py` is
new. Nothing else in the engine changes: `save()`, the core
algorithms, `label/`, `demo/`, the root docs and the prototype are
untouched.

**Known limit (honest):** the DB label rows keep
`label_html_name` / `label_pdf_name` NULL — the issued label rows are
immutable, so the artifact filenames cannot be written back into
them. The linkage is the label's own `label-<page_key>.json`
manifest (delivery + label numbers + edited-PDF SHA-256). If the
product later wants the filenames in the DB, that needs a DB-schema
decision (a separate link table, not an UPDATE of the issued rows).

**How to undo:** call `doc.save()` instead of `doc.save_with_label()`
— the label step is purely additive; no save behaviour depends on it.

## Known limits (NOT fixed here — out of scope by instruction)

- **Universality 94/182** (FUNSD base 20/38, SROIE 4/16, Tottel
  16/24, Shields 12/25 — R18 §6): word segmentation on non-PG
  printed documents is not yet ready; cursive handwriting is out of
  scope. No universality research was started here.
- **Q-03–Q-09, ★2–★8**: the user's decisions; briefs exist in
  R18 Track C. Not decided here.
- **US patent check** (US20150332491A1 — existence verified,
  enforceability unverified) and **print calibration**: the user's
  (lawyer / factory printer). Not done here.
- **Gate promotion, -2 band threshold, 18 borderless edges**: the
  gate stays a quality check; the band threshold (120) is reversible
  per §1; the 18 borderless edges await the user (Q-09).
- **DBNet swap**: deferred (R18 Track B: classical stays; DBNet line
  detection only as a cross-check/fallback when the 4 swap conditions
  are met). `lse/gate.py` does not use DBNet.
- **Single-page LSE** is subsumed: a 1-page document is just a
  multi-page document with one page; the old single-page scripts are
  not ported as a separate path.
