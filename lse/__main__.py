"""LSE command line: open | edit | save | gate.

  python -m lse open PDF [--workdir DIR] [--item TEXT]
                  [--dna-regular TTF --dna-bold TTF]
                  [--bold-mode canonical|anchor|none]
                  [--anchor-box x0,y0,x1,y1]
  python -m lse edit --workdir DIR --page N --word I --new TEXT
                  [--old TEXT] [--row-label TEXT] [--allow-lowercase]
  python -m lse save --workdir DIR --out OUT.pdf [--db DB.sqlite]
                  [--client TEXT --item TEXT --customer TEXT]
  python -m lse gate --workdir DIR

open segments every page at native DPI, builds one live page per
source page (live-p{n}.html in the workdir) and writes state.json.
edit re-opens the document from state.json and stores one more edit.
save writes back the WHOLE document (edited pages rebuilt at native
DPI, untouched pages byte-identical) and, with --db, records the
delivery permanently (hash-chained, one label per page).
"""
import argparse
import json
import os
import sys


def _parse_box(s):
    return [int(v) for v in s.split(",")]


def main(argv=None):
    ap = argparse.ArgumentParser(prog="lse", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_open = sub.add_parser("open", help="open a scanned PDF (segment + live pages)")
    p_open.add_argument("pdf")
    p_open.add_argument("--workdir")
    p_open.add_argument("--item", default="")
    p_open.add_argument("--dna-regular")
    p_open.add_argument("--dna-bold")
    p_open.add_argument("--bold-mode", default="canonical",
                        choices=["canonical", "anchor", "none"])
    p_open.add_argument("--anchor-box", type=_parse_box)

    p_edit = sub.add_parser("edit", help="retype one word on one page")
    p_edit.add_argument("--workdir", required=True)
    p_edit.add_argument("--page", type=int, required=True)
    p_edit.add_argument("--word", type=int, required=True)
    p_edit.add_argument("--new", required=True)
    p_edit.add_argument("--old", default="")
    p_edit.add_argument("--row-label", default="")
    p_edit.add_argument("--allow-lowercase", action="store_true")

    p_save = sub.add_parser("save", help="write back the whole document")
    p_save.add_argument("--workdir", required=True)
    p_save.add_argument("--out", required=True)
    p_save.add_argument("--db")
    p_save.add_argument("--client", default="")
    p_save.add_argument("--item", default="")
    p_save.add_argument("--customer", default="")
    p_save.add_argument("--actor", default="qc")

    p_gate = sub.add_parser("gate", help="per-page quality-check verdicts")
    p_gate.add_argument("--workdir", required=True)

    args = ap.parse_args(argv)
    from .document import load_document, open_document

    if args.cmd == "open":
        doc = open_document(args.pdf, workdir=args.workdir, item=args.item,
                            dna_regular=args.dna_regular, dna_bold=args.dna_bold,
                            bold_mode=args.bold_mode, anchor_box=args.anchor_box)
        print(f"opened {doc.source_label}: {len(doc)} pages -> {doc.workdir}")
        for pg in doc.pages:
            print(f"  p.{pg.number}: {pg.n_words} words, {pg.dpi} DPI, "
                  f"gate {pg.gate_verdict}, live page {os.path.basename(pg.html_path)}")
        return 0

    if args.cmd == "edit":
        doc = load_document(args.workdir)
        edit = doc.edit(args.page, args.word, args.new, old_text=args.old,
                        row_label=args.row_label,
                        allow_lowercase=args.allow_lowercase)
        doc.save_state()
        print(f"p.{args.page} word {args.word}: {edit['old_text']!r} -> "
              f"{edit['new_text']!r} (box {edit['box']}, caps: {edit['caps_action']})")
        return 0

    if args.cmd == "save":
        doc = load_document(args.workdir)
        manifest = doc.save(args.out, db_path=args.db, actor=args.actor,
                            client=args.client, item=args.item,
                            customer=args.customer)
        print(json.dumps({k: v for k, v in manifest.items()
                          if k != "edits"}, indent=1))
        print(f"edits: {len(manifest['edits'])}")
        return 0

    if args.cmd == "gate":
        with open(os.path.join(args.workdir, "state.json")) as f:
            state = json.load(f)
        doc = load_document(args.workdir)
        print(f"{doc.source_label}: {len(doc)} pages")
        for pg in doc.pages:
            d = pg.gate_details
            print(f"  p.{pg.number}: {pg.gate_verdict} "
                  f"(T1 flags {d['t1_flags']}, T2 flags {d['t2_flags']}, "
                  f"{d['n_words']} words)")
            for r in d["reasons"]:
                print(f"    REFUSE {r['test']}: {r.get('box') or r.get('core_box')}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
