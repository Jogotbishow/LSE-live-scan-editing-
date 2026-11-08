# demo/ — the synthetic sample

All data here is fake: supplier **ACME FOILS LTD**, Batch **ACME-2026-0001**,
Lot **ACME-LOT-77**, fake test values. No real supplier document is in
this repo, and none ever will be.

## Files

- `make_synthetic.py` — the generator (pure Python + ReportLab + PyMuPDF).
  Run it to rebuild the sample. No OCR anywhere.
- `ground-truth-words.json` — every word on the page + its box in PDF
  points, read back from the PDF text layer (vector text, not OCR).
  UTF-8 text, so it IS checked in. Regenerating must reproduce it
  exactly (verified: byte-identical across runs).
- `synthetic-supplier-coa.pdf` / `synthetic-supplier-coa-300.png` —
  GENERATED, binary, NOT committed (see `.gitignore`). Rebuild with:

```bash
python demo/make_synthetic.py [--out DIR]
```

The PDF is A4, 1 page; the PNG is the same page at 300 DPI (2481×3508 px);
the ground truth has 78 words.

## Verified numbers (2026-11-08, clean directory, prototype engine)

- Generator reproduces the reference fixture exactly: **78/78 words
  identical** (same texts, same boxes), PNG byte-identical on re-run.
- Segmentation (`segment.py` on the generated PNG): **78/78 ground-truth
  words covered, 0 extras**; 82 words segmented (the batch and lot
  numbers split at their hyphens, +4 — expected).
- End-to-end (open → edit → save): **82 words** opened; batch segment
  `0001 → 0002` found by box and confirmed against ground truth;
  write-back **original bytes intact, 0 pixels changed outside the
  edited box**; delivery record written (the save → label handoff).
