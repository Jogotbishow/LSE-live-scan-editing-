# Contributing to LSE

Thank you for wanting to help. LSE's research is complete through Round 18 (2026-11-07) — contributions that are measured beat contributions that are claimed.

## How to contribute

1. **Open an issue first** for anything bigger than a typo — describe the document type, what you tried, and what you measured.
2. **Test on real scans.** A new document type is the most valuable contribution: run the pipeline on it, report the hand-counted segmentation sample, and attach the (anonymised) page.
3. **Verify by word identity, not position.** Every demo edit in a PR must be checked by row label + box, never by coordinates alone. (We learned this the hard way — a WIDTH edit once landed on the wrong word and passed every position check.)
4. **Eye-check everything visual.** A text check passing does not mean the page looks right. Attach a screenshot clip of every edited word at 1× and 2×.
5. **Never silently degrade originality.** The standing rule: whatever DPI the original has, work at that DPI. If a step cannot preserve it, say so in the report — do not quietly downscale or re-encode.

## What we need most

- New document types (invoices, letters, forms, certificates in other languages) to test universality — the weakest measured area (94/182 on FUNSD/SROIE/Tottel/Shields).
- Fixes for the open items in the latest round report (`docs/ROUND18-REPORT.md`).
- Rotation detection on more layouts.
- Print calibration results from real printers.

## What this repo will NOT accept

- **No real supplier or customer documents** — not in code, tests, issues, or screenshots. Use the generated sample in `demo/` (run `python demo/make_synthetic.py`) or a fully anonymised page. No real lot numbers, company names, quantities, or delivery records, ever.
- **No OCR in the edit path.** Segmentation finds word positions; inpainting erases ink; Document DNA retypes. Recognition may be used only for optional draft/automation features, never to perform or decide an edit — and a human always verifies a draft.
- **No credentials, API keys, or personal data** in issues, PRs, or test files.
- **No silent rewrites of the audit trail.** Edited PDFs keep the original scan as an audit copy; database records are hash-chained and never silently rewritten.

## Ground rules

- Keep the audit trail honest: edited PDFs keep the original scan as an audit copy; database records are hash-chained and never silently rewritten.
- Tests run on the generated synthetic sample only.
- The demo sample is generated, never committed as a binary — see `demo/README.md`.
