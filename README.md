# LSE — Live-Scan Editing

**Edit the text on a scanned document — without OCR, without rebuilding the page.**

LSE treats the scan **as the page itself**. Text is a living layer on top of the original pixels: click any word, retype it, and the page still looks exactly like the original — same paper, same table, same stamp, same handwriting. The system never needs to *read* the text to let you edit it.

> যেমন সবাই OCR-এর কথা বলে, তেমন করে একদিন সবাই LSE-র কথা বলবে।
> *Just as everyone talks about OCR today, one day everyone will talk about LSE.*

## The idea in one paragraph

Today, editing a scanned document means running OCR, rebuilding the page from the recognised text, and losing the original format. LSE does the opposite: the scan stays the scan. Word positions come from segmentation (connected components — no recognition), the old word's pixels are erased with inpainting, and the replacement is typed in a font learned from the document's own glyphs (**Document DNA**). Recognition is a separate, optional step for automation only — never in the edit path.

## How it works

```
scan (PDF/JPG, any DPI)
  → word segmentation (OpenCV connected components, NO OCR)
  → Telea inpainting (erase only the word's ink)
  → live page (original scan background + clickable word spans)
  → type the replacement (Document DNA font, matched size/weight/colour)
  → save → edited PDF + audit copy + certificate + DB record (hash-chained)
```

Standing principle: **preserve the document's full originality** — whatever DPI the original has, work at that DPI. Never downscale, never re-encode the background, never change the resolution. The edited PDF embeds the original scan bytes verbatim; only the edited word's pixels change.

## Status — research complete (Round 18, 2026-11-07)

The research rounds are finished: **Round 18 was the last research round**. Three rounds in a row (R16–R18) changed no score; the live pages rebuild byte-identically. What remains is product work — the integration build, the open product decisions below, and the two things only a human can do (a real-printer calibration and a lawyer's patent check).

LSE is the **editing technology inside GRAVORA's COA, template, and supplier modules** — a local-first offline QC/QMS app for flexible-packaging factories in Bangladesh, the software it was invented for. It is not a standalone module of GRAVORA. This repo is the same technology, standalone and public, so everyone can use it, learn from it, and make it better.

## What is proven (measured, not claimed)

Proven on real scanned supplier Certificates of Analysis (PG Foils, 300 DPI, colour and B&W), plus a second supplier's pages (Raviraj) and a synthetic sample. All numbers are from the Round 18 report (`docs/ROUND18-REPORT.md`); nothing here is claimed without a measurement behind it.

- **Native 300 DPI end-to-end** — segmentation → live page → edited PDF, no downscaling, no re-encoding of the background. Live pages rebuild **5/5 byte-identical**.
- **Identity-verified edits** — every demo edit is checked by word identity (row label + box), never by position alone. Lot No. `206/7 → 207/9`, WIDTH `780.0 → 781.5`, on the correct words, "Hard" untouched. Identity probe **15/15, three runs**.
- **Document DNA** — the rendering font is cloned from the document's own glyphs (vtracer, per-weight Regular + Bold). Font-fix verification **43/43**.
- **PDF write-back + database record** — the edited page is written back as a PDF (edited page + full-resolution audit copy + edit certificate, original scan embedded verbatim) and recorded permanently in a SQLite database with a hash-chained audit log (**20/20 entries chain-linked**). Write-back verifier **41/41**.
- **Save → label** — saving a delivery auto-updates its packing label: **90/90** (5 pages × 18 checks).
- **Segmentation on the tested formats** — PG sample **518/518**, extras 0. Raviraj p2 strict **447/502 = 89.0%** (corrected 498/502 = 99.2%); p3 improved **384/384 = 100%**; full page strict **781/886 = 88.1%**, corrected **832/886 = 93.9%**.
- **Bengali certificate** — the edit certificate renders in Bengali script with correct conjuncts.
- **Synthetic demo sample** — the generated ACME sample (see `demo/`) segments **78/78** ground-truth words, 0 extras, and runs open → edit → save end-to-end (see below).

## Honest limits

- **Universality is not yet proven.** On printed documents outside the tested formats, the editing machinery works but word segmentation does not yet: **94/182** across the FUNSD / SROIE / Tottel / Shields samples. On cursive handwriting, no. The fixed word-gap rule cannot separate words when loose letter-spacing overlaps word gaps. This is the biggest open technical problem.
- **Gate: 9 ALLOW / 16 REFUSE.** On 25 new Raviraj pages the quality gate allows 9 and refuses 16 (threshold T1 0.50, margin only 0.025). The refusals are real segmentation misses (pale blue ink, stamp-covered words, dense small print) — the gate measures the gap correctly; the gap itself is not closed yet. Gate promotion is **not** decided.
- **Write-back, 300-DPI verifier: 37/41.** The 4 failures are ink-IoU only, a known limit of the stand-in font — not a regression.
- **Print calibration needs a real printer.** Screen-perfect is not print-perfect; calibration against the factory printer has not been done and cannot be done without the physical printer.
- **US patent: legal check needed before any sale.** US patent US20150332491A1 exists (enforceability unverified), and Adobe US9741142B2 (active until 2035-02-05) is the first thing a lawyer must look at. No professional freedom-to-operate opinion exists. This is not legal advice — do not sell on the strength of this README.
- **Open product decisions (tracked in GRAVORA, none decided here):** the acceptance bar for supplier COAs (Q-03, proposal 90%+), the patent-check timing (Q-04), the vault path (Q-06), warnings-vs-relations (Q-07), scan-COA intake (Q-08), the 18 borderless edges (Q-09, proposal: keep faithful), the caps policy (proposal: lowercase suggestion where caps do not fit), and gate promotion. The build runs on reversible defaults; none of these block it.
- **DBNet is deferred.** Classical segmentation stays; DBNet is a line-detection cross-check only, not a swap.

## Install

Python **3.11+**. All packages have wheels for Linux and Windows (including `sqlcipher3` and `opencv-python-headless` on Windows).

**Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

For the visual verification scripts only, also run once:
```bash
python -m playwright install chromium
```

## Run the demo on the synthetic sample

No real supplier data is in this repo — the demo sample is **generated** from fake data (ACME FOILS LTD, Batch ACME-2026-0001, Lot ACME-LOT-77). The PDF/PNG are binary, so they are not committed; the generator rebuilds them, and the ground-truth JSON (UTF-8 text) is checked in.

```bash
# 1. Generate the sample (300-DPI PDF + PNG + ground-truth words JSON)
python demo/make_synthetic.py

# 2. Segment it (no OCR — connected components only)
python -m lse.segment demo/synthetic-supplier-coa-300.png /tmp/seg.json
#    expected: 82 words segmented (78 ground-truth words; the batch and
#    lot numbers split at their hyphens, +4)

# 3. Open it as a live page, edit a word, save it back — the
#    end-to-end test in tests/ does exactly this on the generated
#    sample: it opens the PDF (82 words found), edits the batch
#    number's last segment 0001 -> 0002 — found by word identity
#    (row label + box), never by position alone — writes the edited
#    PDF back, and checks that no pixel changed outside the edited
#    box. (The same flow was verified against the prototype engine
#    on 2026-11-08 — see demo/README.md for the numbers.)
python -m pytest tests/ -v
```

Verified end-to-end on the generated sample (2026-11-08, clean directory): open **82 words** (ground truth 78), batch segment `0001 → 0002` found by box and confirmed against ground truth, write-back **original bytes intact, 0 pixels changed outside the edited box**, delivery record written. See `demo/README.md` for the numbers.

## Run the demo on your own scans

```bash
python -m lse.segment your-scan-300dpi.png /tmp/seg.json
```

Any DPI works — the pipeline works at the scan's native DPI. Colour and B&W scans both work. Handwriting and unusual layouts will segment poorly (see Honest limits); please report them — a new document type is the most valuable contribution (see `CONTRIBUTING.md`).

## How to test

```bash
python -m pytest tests/ -v
```

The full suite (38 tests) runs against the real prototype fixtures — the PG supplier COA PDFs and the prototype DNA fonts — which live outside this repo and are **not** committed (real supplier data must never go public). In a clean clone those tests **skip** (pytest exits 0, reporting them as skipped) and only the portable tests run (gate constants, row-label mapping). To verify the engine in a clean clone, run the demo path above (`make_synthetic.py` → `python -m lse.segment` → 82 words). A test that edits must check the edit by word identity (row label + box), not by coordinates.

## Repository layout

```
lse/            pipeline: segment, inpaint, build page, DNA font, write-back, DB
label/          save → label (Domino label builder)
tests/          end-to-end tests on the generated synthetic sample only
docs/           research synthesis + round reports (all measured, Bengali + English)
demo/           make_synthetic.py + ground-truth-words.json (generated PDF/PNG
                are rebuilt, never committed — no real supplier data)
```

## License

MIT — see `LICENSE`. Permissive: use it, change it, sell with it (subject to the patent note above — get the legal check first).

## Contributing

See `CONTRIBUTING.md`. Issues, ideas, and pull requests are welcome — especially new document types to test universality, and fixes for the open items in the latest round report.

## Origin

Invented in 2026 by Muse (the main craftsman) with Jogot (partner and friend) for GRAVORA, Bangladesh. Built in the open so others can use it, learn from it, and make it better.
