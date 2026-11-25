# LSE — Lessons Learned (training notes)

Training notes for the LSE engine, written from real live work — not from
theory. Each rule below cost a real failure on a real document. Read this
file before touching `lse/writeback.py`, `lse/document.py`, or any
span-edit script. Last updated: 2026-11-24 (Raviraj 20-micron live test
+ 20-micron-into-25-micron-format transplant).

## 1. Rotated pages — the big one (2026-11-24)

**Rule: a page with `/Rotate` 90 or 270 is a different coordinate animal.
Segmentation/display coords are the ROTATED (displayed) space; the PDF
page space is UNROTATED. Every write-back step must use the unrotated
dimensions.**

What went wrong on the Raviraj transplant (source page `/Rotate 270`,
mediabox landscape 841.68×595.2, displayed portrait 595.2×841.68):

1. `display_to_page_point` was fed `page.rect` (the ROTATED rect,
   595.2×841.68 — swapped). Patches landed in the lower empty box,
   squashed/rotated. **Fix:** pass the mediabox dimensions
   (`page.mediabox.width/height`) — verified against
   `page.derotation_matrix` to 0.001 pt.
2. With correct mapping the patches still landed as hairlines: a
   1754×65 px patch placed as 11×0.41 pt. Cause: `insert_image`
   **keeps the image's proportion** — a wide-short patch in a
   tall-narrow unrotated rect shrinks to fit the rect's width.
   **Fix:** pass `rotate=rotation` to `insert_image`.
3. First tried `rotate=(360 - rotation)`: the text came out
   **upside-down**. `insert_image`'s rotate is counter-clockwise, so
   the correct value is `rotate=rotation` (270 for a 270 page, 90 for
   a 90 page, 0 for 0, 180 for 180). Proved by render, not by
   reasoning — the direction was derived backwards twice before the
   render settled it.
4. Regression test: `tests/test_rotated_writeback.py` (rotations 90,
   270, control 0) — asserts the placed rect fills the expected
   unrotated rect AND the rendered text is upright (correlation vs the
   patch, upright beats 180°-rotated by a margin).

**Lesson: never trust a rotation derivation — render and look.**

## 2. Sizing — measure every cell, never assume one size

- Header values on one page can be genuinely TWO sizes: on the Raviraj
  format the spec + invoice glyphs are 55 px tall while
  customer/product/batch are 40–44 px (proven by glyph-component
  measurement, 41/26 real components, not speckle). Calibrate
  `target_fs` per edit from the OLD text's ink width (Liberation width
  at fs 100).
- `build_patch` sets `fs0 = box_h / 0.85` and left/top-aligns new ink
  to the OLD ink's measured bbox (`measure_ink_bbox`). The caps gate
  runs at fs0 — if the target is smaller than fs0, the caps check can
  refuse a value that would actually fit.
- Recipe that renders at the target size exactly:
  `fit_width_px = natural / 0.97` (natural = Liberation width at the
  target fs). Added as the edit key `fit_width_px` in
  `lse/writeback.py:build_patch` (2026-11-24, local only).
- The caps gate (`CapsDoesNotFitError`) is a quality check — **never
  squeeze or shrink text to force a fit**. If it refuses, widen the
  slot or shorten the text, never compress the glyphs.

## 3. Weight — size is not bold (2026-11-24, caught by the user)

- The Raviraj header values look heavier because they are TALLER, not
  bolder. I set the invoice edit `bold=True` and the user spotted it
  immediately. Measured: original invoice ink 2948 px, my Bold 4249 px
  (+44%); spec and batch ink matched exactly (1730/1730, 912/912).
  After `bold=False`: invoice ink 2909 px (−1% vs original).
- **Verify weight by ink-pixel count (original vs new, same cell,
  same render DPI), not by eye alone.** A 40%+ ink difference is a
  wrong weight; within a few % is right.
### 3d. Font design — identify the FONT, not just the size (2026-11-24, the user's PLNU catch)

- Sizes/weights measured 0% but the DESIGN differed: Liberation
  Serif's P/L/N/U/0 shapes are wider/rounder than the original's.
  Liberation is metric-compatible with Times, NOT shape-identical.
  The winner, by contact sheet (same string, cap-matched, eye +
  width/stem): **Nimbus Roman** (URW Times clone) — batch width 324
  vs orig 323, shapes match by eye; C059/P052/Noto/DejaVu all visibly
  wrong. The whole transplant now renders in Nimbus Roman
  (Regular + Bold for the invoice); table cells stayed exact.
- PLUMBING BUG, caught the same night: `build_patch` only sees the
  font through `edit["font_path"]` — the apply script's local `font`
  variable never reaches the render. One run silently rendered
  Liberation while measuring Nimbus. Caught because the invoice band
  was PIXEL-IDENTICAL (mean abs diff 0.0) between two runs that
  should have differed. Lesson: after every run, check the manifest's
  `font` field; a zero diff between runs that should differ is a red
  flag, never a pass.
- Probe (PIL) widths are RELATIVE only: Liberation spec probe 1092
  vs pipeline 1174. The pipeline render is the truth; probes rank
  fonts against each other, never against the original in absolute px.

### 3c. Caps vs slashes — measure the CAPS, not the ink box (2026-11-24, the user's second catch — CORRECTS an earlier error)

- CORRECTION: the transplant notes claimed the header values were
  "genuinely TWO sizes" (spec/invoice glyphs 55 px vs batch 40–44 px).
  WRONG. The 55 px components were the SLASHES. The original font's
  slashes span 55 px against 40 px caps (gap 15 px); Liberation's
  slashes span only ~41 px against 39 px caps (gap 2 px). ALL header
  values share ONE cap height (~40 px at 424 DPI, ~28 px at 300 DPI).
  Never infer a size from the ink-box height when the text contains
  slashes (or any glyph taller than the caps) — measure the cap
  height from the components (median height of the tall components).
- Consequences, all fixed the same night: fs 60 for spec, batch AND
  invoice (not 68/70/75); invoice back to Bold (its stems measure
  6 px where Regular gives 4 and the first Bold attempt gave 11 —
  the truth was in between, and Bold at the RIGHT size is 6 px).
- New engine knobs, both measured per edit: `edit["fs0_px"]`
  (cap-height size, overriding box_h/0.85 — needed because the box
  height is the slash height, and the caps rule would otherwise
  refuse the invoice edit) and `edit["dy_px"]` (vertical shift,
  +down: the layer is placed by ink top = slash top in the old text
  but nearly cap top in Liberation — without it the new caps float
  10–13 px too high; dy = (old_ink_h − old_cap_h) − (new_ink_h −
  new_cap_h)). Result (300 DPI): spec caps median 28.0 vs orig
  28.0, invoice 29.5 vs 28.5, spec width 1174 = orig 1174.
- Honest residuals: invoice width 593 vs orig 632 (−6% — Liberation
  Bold is narrower than the original's invoice font; NOT stretched,
  the stretch stays forbidden); the original's slashes poke further
  above the caps than Liberation's (max component 39 vs 30 px).
- The Noto Serif Condensed detour (same night) is SUPERSEDED: its
  letterforms looked closer, but at the true cap size it rendered
  40% too tall (fs 75 from the slash-inflated height) — the font was
  never the problem, the SIZE was. `font_path` stays in the engine
  as a general knob; the transplant itself uses Liberation throughout.

### 3e. Font matching — the module exists, but it does NOT yet pick the right font on a real scan (2026-11-24, the user's goal)

- `lse/fontmatch.py` (built 2026-11-24, tests 5/5 green on SYNTHETIC
  renders): `fingerprint` (cap/x-height/stem/slash/ink-width from
  components), `render_metrics` (fs sweep ±3 around the cap-matched
  fs — the true font must be able to score ~0), `rank_fonts`
  (weighted distance with a 1 px tolerance for quantization),
  `overlay_score` / `overlay_rank` (best-IoU of the rendered string
  against the scan's ink), `match_font`, `system_serif_candidates`,
  `candidates_from_dirs` (so a Windows Fonts folder can enter the
  ranking later).
- HONEST LIMIT: on the REAL Raviraj scan the module ranks the WRONG
  font — fingerprint picks P052/Noto, overlay picks Liberation/Noto/
  C059-Bold, per-character profile picks Noto (all within noise of
  each other). The differences between Times clones are smaller than
  the scan noise: dot gain fattens ink_w ~7%, letters touch (x_h
  reads 0), the PIL probe is unstretched while the pipeline stretches
  the text layer to the fit box (~+12% on the spec), and the
  per-character profile shows the original's LETTERS narrower than
  any candidate's at the same cap (P 17 vs Nimbus 23, L 15 vs 25)
  with wider gaps — a condensed-Times pattern no installed font
  reproduces. The eye + contact sheet remain the authority for now;
  the module is the first step toward the confirmed 100% goal, not
  the finished capability. Do NOT present it as proven on scans.
- The original's font is almost certainly Times New Roman (Excel on
  Windows) — not installed here. The EXACT font would come from the
  user's Windows PC (`C:\Windows\Fonts\times.ttf`); only he can
  supply that file. Nimbus Roman is the closest open clone available
  here (batch width 320 vs 323, caps within 1 px, shapes match by eye).

### 3f. Bundled fonts — Times New Roman lives inside LSE now (2026-11-24, the user's order)

- The user's rule: every font LSE uses must live INSIDE LSE, or it
  cannot work universally. `lse/fonts/` now holds 12 files: Times
  New Roman (Regular/Bold/Italic/Bold Italic, from Microsoft Core
  Fonts `times32.exe`, SourceForge — redistributable unmodified),
  Liberation Serif (4, SIL OFL), Nimbus Roman (4, URW GPL).
  `lse/fonts.py` resolves names — bundled first, system fallback —
  and the engine (`writeback.py`, `page.py`) and the matcher use it.
  No `lse/` code may assume `/usr/share/fonts/...` for a bundled font.
- PROOF the original is Times: the bundled Times renders the batch
  string at width **325 vs the original's 323** (+2 px) at cap 29 —
  Nimbus +8, Liberation +17. The invoice is still the odd row
  (Times Bold 600 vs 630; Liberation Bold 614) — width alone does
  not settle it, and the matcher on the real scan still picks the
  wrong font for spec/invoice (see §3e). The batch fingerprint now
  ranks Times #1 (d=0.000, tied with Nimbus — the two Times clones
  are metrically identical on that string).
- Test note: the FULL suite cannot run in this venv — `tests/test_dna.py`
  needs `vtracer`, which is not installed (pre-existing environment
  gap, not caused by any change). Run with `--ignore=tests/test_dna.py`.
  The `test_rotate_90` failure seen once (2026-11-24 ~22:05) did not
  reproduce on re-run — treated as a flake, not a regression.
- PRE-EXISTING FAILURE (found 2026-11-24 ~22:10, full suite 50 passed
  + 1 failed): `test_five_live_pages_byte_identical` fails on
  `live-scan-page-aug-300.html` — the file's SHA is d4d25430 but
  `helpers.py` pins bce37147. The pin was written 2026-11-08, the
  file was regenerated 2026-11-09 — the pin is STALE, 15 days old,
  unrelated to any 2026-11-24 work (nothing tonight wrote to
  live-paper-prototype). Do NOT silently update the pin: it is a
  safety anchor, and only a deliberate re-promotion may change it.

### 3b. Condensed source fonts — `scale_x` (2026-11-24, caught by the user)

- The Raviraj header font is CONDENSED: tall and narrow. Cap-height
  per char-width: invoice 1.79, spec 1.62, batch 1.29 — the big values
  are a condensed cut, the batch is not. Liberation Serif is 1.52, so
  no single fs matches both height and width: fs for the height
  overshoots the width (spec +3%, invoice +9% — the user spotted it),
  fs for the width undershoots the height (invoice −12%).
- Fix: `edit["scale_x"]` (0.85–1.0) squeezes the RENDERED TEXT LAYER
  horizontally in `build_patch` — background untouched, cap height
  kept. Values: spec 0.970 at fs 68, invoice 0.851 at fs 75.5. Result
  (200 DPI): spec 783×24 vs orig 784×25, invoice 423×25 vs 421×26 —
  all within 1 px. Never stretch (>1.0), never past 0.85 — beyond
  that, a condensed font is the answer, not a squeeze.
- Guard: a taller fs grows the erase box — it must never cross a table
  border (the spec box at fs 75.5 would have reached x 3138, past the
  right border at ~3097, and inpainted it away). The script's
  "extra ink right of probe ink < 500 px" assertion is the safety net,
  not the solution: keep the box inside the cell by construction.

### 3g. Glyph harvest + retouch — the document IS its own font (2026-11-24 ~23:54, the user's order: build NEW technology so LSE can copy ANY font exactly by looking at it)

- The font hunt FAILED (16 fonts, 3 identifier tools — see the
  measurement-gaps note): the Raviraj original is a condensed
  old-style serif nobody could name. The answer is not a better
  hunt — it is to stop needing the font at all. The document
  CONTAINS the letterforms: harvest cuts a word's ink into its
  characters (known text from the edit context, never OCR) and
  compose pastes the document's own glyph bitmaps into a new
  string. Exact by construction — P 25, L 20, N 30, U 31 px at
  display scale, the original's own widths, flat L foot, plain P
  stem ends. The invoice −6% gap that survived Liberation, Nimbus
  AND Times Bold is gone: the invoice is the document's own glyphs.
- Layer 1 — `lse/glyphharvest.py`. Segmenter: connected
  components → merge dotted ('i' dot+stem, x-overlap ≥50% of the
  narrower + vertical separation) → split wide (THREE-part bridge
  rule ONLY: cut column ≤3 dark px AND columns ±4 px have ink
  ≥0.5×component height AND cut ≥0.8×median width from BOTH edges;
  v1 argmin cut the 'U' and every 'm'; v2 <210 2-column run still
  cut the 'U' because its bottom curve is 2 px thick over 5
  columns; a component failing any test stays whole and the harvest
  reports a mismatch LOUDLY) → small-glyph baseline rule (a '.'
  area 26, bottom == baseline, vs a scan speck area 21, bottom
  ~35 px above the baseline — area alone cannot tell them apart)
  → space detection (gap > 1.8×median gap AND > 0.35×median glyph
  height; real space 21 px, '.'-adjacent gaps ~12–14 px).
- Gaps are PAIR-SPECIFIC, and this took three fixes to learn.
  (a) The gap before a '.' is the dot's wide side bearing (~12 px),
  the gap before a letter ~5 px: a glyph harvested from before a
  dot carries the dot-gap into any new string. Each glyph now
  records `gap_after` (to a letter) and `gap_after_dot` (to a '.'),
  and compose picks by the following character. (b) The gap before
  a SPACE belongs to the space item, not the glyph: the spec's
  "HSL" 'L' carried a 21 px space gap into the batch, sitting 14 px
  too far from 'N'. A glyph before a space now keeps the median
  letter gap. (c) A glyph's spacing depends on WHICH word it came
  from (the batch's 'L' sits 6 px from 'N'; the spec's 'L' 21 px
  from a space): variants are tagged with their source word and
  compose takes `prefer_source` — a new value for a cell is set in
  that cell's own glyphs. After all three: batch 462 vs old ink 457
  (+1%, the '4' genuinely wider than the '3' it replaces), spec
  1488 vs 1477 (+0.7%), invoice 882 vs 893 (−1%), all 18 cells
  within ±5%, every deviation explained by the font's own digit
  widths — and 0 differing pixels outside the 18 patch rects.
- Space double-count: a glyph's advance already includes the
  following gap, so a glyph before a space advances by its width
  alone; the space item carries the spacing. The first fin10 draft
  rendered the spec 123 px too wide that way. Canvas overflow: a
  '.' whose bottom sits 1 px below the caps' baseline overflowed
  the layer — the canvas covers the lowest bottom_rel and compose
  crops to the tight ink bbox (letter x positions are crop-relative).
- Layer 2 — `lse/glyphretouch.py` (the user's 23:58 refinement:
  if exact copy is impossible, take a CLOSE font and retouch it
  Photoshop-style until the letters LOOK same-to-same). For a
  character that never appears on the page ('a' and 'x' for
  "2 max"): rework the closest font's glyph toward the document's
  MEASURED profile — width = font width × width-factor (median
  doc/font ratio, anchored per case class), height = doc's cap
  height / x-height, stem by erode/dilate at 2× supersampling,
  spacing = doc's median gap. Lora chosen BY MEASUREMENT over
  Times (Times 'x' stem 6.0, Lora 'x' stem 5.0 exact; both 'a'
  exact). Retouched glyphs are MARKED retouched everywhere — in
  the library, the compose metrics, the writeback record and the
  certificate — never passed off as harvested ink.
- Retouch bugs paid for twice. (a) The 2× halving bug: targets
  were scaled 1× against the 2× render and every glyph came out
  half size — targets are now × supersample before scaling.
  (b) The morph-loop overshoot (fin10's first TEMP): the stem
  ruler is a MODE over horizontal run lengths, and on a diagonal
  ('x') one dilate too many merges the strokes into a blob whose
  mode run jumps far past the target (target 5.5, two dilates,
  achieved stem 9.0). The loop now keeps the BEST state seen and
  stops as soon as a step moves away from the target — never trust
  the last measurement alone. Also fixed the same night: the
  stem target must be measured from the SAME weight as the retouch
  (a bold invoice 'N' is 7 px where a regular table 'N' is 5 px;
  mixing them moved the target to 5.5).
- Writeback wiring: `build_patch` accepts `edit["glyph_image"]`
  (a PIL RGBA layer). When present, the font pick, caps gate and
  width-fit are ALL skipped — shrinking would destroy the
  exactness. Ink must fit box + 2×PATCH_MARGIN_PX (3 px) or it
  raises (never clips silently). The record says
  `"font": "glyph-harvest"` with `"glyph_retouched": [...]`.
  Safety: `lse-edits.json` embeds the RECORDS only, never the raw
  edit dicts (a PIL layer is not JSON-serialisable); `Document.save`
  does not call save_state; `_save_state` sanitises a PIL
  glyph_image to None + a note; build_patch RAISES on a non-Image
  glyph_image (a reloaded edit must be re-composed from the
  library — never silently fall back to a font render).
- Plumbing lesson, repeated: the render font reaches `build_patch`
  ONLY via `edit["font_path"]`, and a glyph composition ONLY via
  `edit["glyph_image"]` — a script-local variable changes
  measurements only, never the render (fin7 rendered Liberation
  while measuring Nimbus; caught because two runs that should
  differ were pixel-identical — a zero diff between runs that
  should differ is a red flag, never a pass).

## 4. Erase — the box must cover ALL old ink

- The erase mask is the box interior dilated 1 px. Ink outside the box
  survives as ghosts. When a value's ink extends past its word box
  (e.g. a 13 px tail past the glyph-filter bbox), widen the box to
  cover it — the box, not the mask, is the fix.
- `measure_ink_bbox` excludes long thin rules (cw>375 & ch<9, or
  ch>180 & cw<9), but a SHORT vertical border segment inside a probe
  is NOT excluded and inflates the bbox. Check the bbox against the
  table dividers before trusting it (Raviraj dividers: left border
  x≈404–418, standards/actual ≈2514–2526, right border ≈3097–3111 in
  display px; the standards column runs to x≈2520, not 2360).
- A 5×5 px scan speck inside a widened box is inpainted with the
  patch — harmless, no special handling.

## 5. Write-back plumbing

- `display_to_page_point` requires UNROTATED (mediabox) page dims —
  see §1. Its docstring says so now.
- The freetext-annotation rect still uses `page.rect` dims: on a 270
  page it displays vertical on the left edge. Unavoidable with a plain
  rect; the annotation is deleted in final deliveries anyway.
- `Document.save()` adds a red freetext annot + audit copy +
  certificate + embedded `lse-edits.json` + verbatim original scan
  stream. The red mark is a PDF annotation only, never in the page
  image.
- **Edited supplier COAs go out clean, no red mark** (user's standing
  preference, 2026-11-24: "oita raikho na"). The certificate page +
  embedded manifest remain the audit record.
- The engine certificate boilerplate falsely claims "recorded in the
  database" for no-DB saves. For test/no-DB deliveries, replace it
  with an accurate certificate (own page, own wording).
- `Document.edit()` is per-word with caps-fit enforcement. Span edits
  work by appending dicts directly to `page(1).edits` — they flow
  through `build_patch`.
- Gate REFUSE flags are a quality check, NOT a ship-gate. Do not block
  open/edit/save on them.

## 6. PyMuPDF gotchas (paid for in debugging time)

- `insert_textbox` inserts **NOTHING** when the text overflows the
  box (returns a negative rect, page stays blank). Always assert the
  text landed (`len(page.get_text()) > …`) — a 70-line certificate
  silently produced a blank page on 2026-11-24.
- Annotations are bound to the Page *instance* that produced them.
  Hold one `p1 = doc[0]` and use it for both `annots()` and
  `delete_annot()` — calling `doc[0]` twice gives a different Page
  object and `delete_annot` raises "Annot is not bound to a page".
- `page.get_image_rects(xref)` returns rects in UNROTATED page
  coords. Use it to verify where a patch really landed (this is how
  the 11×0.41 pt hairline was proven).

## 7. Load / segment costs

- `load_document()` re-segments every load (~13–21 s) with very noisy
  stdout. Grep-filter it or write results to a file. `2>/dev/null`
  hides tracebacks — a script can die silently mid-print.
- JPGs wrap losslessly via PyMuPDF (JPEG bytes embedded, 300 DPI).
- No DNA extraction pipeline exists yet for an arbitrary new document
  — new text on a fresh document is Liberation Serif, not the
  document's own glyphs. Say so in the certificate.

## 8. Document-specific facts (do not generalise, do not invent)

- Raviraj "Batch/Lot No." row sits BETWEEN Specification and
  Invoice No. & Date, value bold in the same value column — PROVEN
  from `Raviraj COA with batch number.pdf` (all 10 pages). Never
  invent a row or a placement on any document.
- The 25-micron bundle (`raviraj-COA-25-micron.pdf`, 27 pages) has NO
  batch row anywhere; only the separate 'with batch number' file does.
  Do not re-report otherwise.
- The Raviraj 20-micron page has a 4-row header (no batch row); the
  25-micron with-batch-number format has a 5-row header.

## 9. What "done" means

- Eye-check the RENDER (full page, edges and corners), not the pass
  scores. Measure the ink (old vs new per cell). A report link or a
  green suite alone never counts as showing the output.
- The LSE 100% rule still stands: do not stop, and never claim 100%,
  until Muse itself feels 100% satisfied with the accuracy.
