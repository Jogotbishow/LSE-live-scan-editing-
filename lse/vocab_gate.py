#!/usr/bin/env python3
"""Vocabulary gate (Round 6 Track B, PROMOTED — v3 logic).

Two-pass post-process over pass-1 segmentation JSONs. Fixes over-splits
(a word broken into 2-4 pieces by blob-splitting) by matching the union's
component-width signature against whole words elsewhere in the document
set. Merge only if the signature matches a normal word on >= 2 DISTINCT
pages (cross-page corroboration — the only discriminator that survived
Round 5's negative result: no gap/geometry rule separates a merged pair
from a single word when the exemplar itself is the merged pair).

Measured on the 14 PG pages (Round 6 Track B): 37 merges, 0 false merges
(every merge eye-verified true), sample 528 -> 522 boxes (518 true; 6
over-splits fixed, 4 speck FPs remain), titles 14/14, H2 14/14.
Cost: 5 true fixes missed — DEPARTMENT (whole on 1 page only) and the
header e-mail x4 (whole on may-p6 only) stay split; they remain covered
and editable in pieces.

Rule-component exclusion (w>=100px, h<=15px) applies to every signature.
The v2 piece-attestation veto is NOT used (proven unusable: short piece
signatures collide with 17-136 unrelated words; the SALES piece is
attested nowhere).

Usage:
  venv/bin/python3 vocab_gate.py --segs <dir> --images <dir> --out <dir> \
      --pages aug-p1,...,may-p6 [--in-suffix v5] [--out-suffix v5-gate]
Input segs:  <dir>/seg-<page>-<in-suffix>.json
Images:      <dir>/<kind>-<n>.png  (page aug-p1 -> aug-1.png)
Output segs: <dir>/seg-<page>-<out-suffix>.json
Decisions:   <out>/vocab-gate-decisions.json
"""
import argparse
import json, os, sys
import cv2
import numpy as np

SP = "/home/hatch/workspace/gravora-review/live-paper-prototype/scan-paper"
W_TOL = 3      # per-component width tolerance (px)
N_TOL = 1      # n_comp tolerance
TOT_W_TOL = 8  # total-width tolerance (px)
RULE_W = 100
RULE_H = 15
MIN_PAGES = 2  # corroboration: exemplar attested whole on >=2 pages

def parse_args():
    ap = argparse.ArgumentParser(description="vocabulary gate (Round 6 Track B)")
    ap.add_argument("--segs", required=True, help="dir with input seg JSONs")
    ap.add_argument("--images", required=True, help="dir with page PNGs (<kind>-<n>.png)")
    ap.add_argument("--out", required=True, help="dir for gated seg JSONs + decisions")
    ap.add_argument("--pages", required=True, help="comma-separated page names, e.g. aug-p1,aug-p2")
    ap.add_argument("--in-suffix", default="v5", help="input seg suffix (seg-<page>-<suffix>.json)")
    ap.add_argument("--out-suffix", default="v5-gate", help="output seg suffix")
    return ap.parse_args()

ARGS = None

def page_comps(img_path):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    otsu_val, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    num, labels, stats, cent = cv2.connectedComponentsWithStats(bw, connectivity=8)
    comps = []
    for i in range(1, num):
        x, y, w, h, area = (int(v) for v in stats[i])
        if area < 14:
            continue
        comps.append({"x": x, "y": y, "w": w, "h": h, "area": area,
                      "cx": float(cent[i][0]), "cy": float(cent[i][1])})
    return comps

def signature(comps, box):
    x0, y0, x1, y1 = box
    ws = sorted((c["x"], c["w"]) for c in comps
                if x0 <= c["cx"] <= x1 and y0 <= c["cy"] <= y1
                and not (c["w"] >= RULE_W and c["h"] <= RULE_H))
    return [w for _, w in ws]

def match_sig(u, e):
    if abs(len(u) - len(e)) > N_TOL:
        return None
    if len(u) == len(e):
        devs = [abs(a - b) for a, b in zip(u, e)]
        return max(devs) if devs and max(devs) <= W_TOL else None
    long_s, short_s = (u, e) if len(u) > len(e) else (e, u)
    best = None
    for skip in range(len(long_s)):
        cand = long_s[:skip] + long_s[skip + 1:]
        devs = [abs(a - b) for a, b in zip(cand, short_s)]
        if devs and max(devs) <= W_TOL:
            m = max(devs)
            best = m if best is None else min(best, m)
    return best

def group_events(words):
    bs = [w for w in words if w.get("src") == "blob-split"]
    events, used = [], set()
    for i, w in enumerate(bs):
        if i in used:
            continue
        grp = [w]
        used.add(i)
        changed = True
        while changed:
            changed = False
            for j, w2 in enumerate(bs):
                if j in used:
                    continue
                cy1 = (grp[-1]["box"][1] + grp[-1]["box"][3]) / 2
                cy2 = (w2["box"][1] + w2["box"][3]) / 2
                gap = w2["box"][0] - max(g["box"][2] for g in grp)
                gap2 = min(g["box"][0] for g in grp) - w2["box"][2]
                if abs(cy1 - cy2) <= 15 and (0 <= gap <= 40 or 0 <= gap2 <= 40):
                    grp.append(w2)
                    used.add(j)
                    changed = True
        grp.sort(key=lambda w: w["box"][0])
        events.append(grp)
    return events

def main():
    global ARGS
    ARGS = parse_args()
    PAGES = [p.strip() for p in ARGS.pages.split(",") if p.strip()]
    SEGDIR = ARGS.segs
    IMGDIR = ARGS.images
    OUTDIR = ARGS.out
    os.makedirs(OUTDIR, exist_ok=True)
    vocab = []  # {page, box, sig, width}
    page_data = {}
    for p in PAGES:
        kind, n = p.split("-p")
        img_path = os.path.join(IMGDIR, f"{kind}-{n}.png")
        comps = page_comps(img_path)
        seg = json.load(open(os.path.join(SEGDIR, f"seg-{p}-{ARGS.in_suffix}.json")))
        page_data[p] = {"comps": comps, "seg": seg}
        for w in seg["words"]:
            if w.get("src") == "blob-split":
                continue
            sig = signature(comps, w["box"])
            if len(sig) >= 2:
                vocab.append({"page": p, "box": w["box"], "sig": sig,
                              "width": w["box"][2] - w["box"][0]})
    print(f"vocabulary: {len(vocab)} normal words with >=2 comps (rule-excluded)")

    decisions = []
    n_merge = n_keep = 0
    for p in PAGES:
        seg = page_data[p]["seg"]
        comps = page_data[p]["comps"]
        events = group_events(seg["words"])
        words = list(seg["words"])
        merged_boxes = set()
        for grp in events:
            if len(grp) < 2:
                continue
            ubox = [min(w["box"][0] for w in grp), min(w["box"][1] for w in grp),
                    max(w["box"][2] for w in grp), max(w["box"][3] for w in grp)]
            usig = signature(comps, ubox)
            uw = ubox[2] - ubox[0]
            # all matching exemplars, with distinct-page count
            matches = []
            for ex in vocab:
                if abs(len(usig) - len(ex["sig"])) > N_TOL:
                    continue
                if abs(uw - ex["width"]) > TOT_W_TOL:
                    continue
                dev = match_sig(usig, ex["sig"])
                if dev is None:
                    continue
                matches.append((dev, abs(uw - ex["width"]), ex))
            matches.sort(key=lambda t: (t[0], t[1]))
            pages = sorted({m[2]["page"] for m in matches})
            rec = {"page": p, "event_boxes": [w["box"] for w in grp],
                   "union_box": ubox, "union_sig": usig, "union_w": uw,
                   "line": grp[0].get("line"),
                   "n_exemplar_pages": len(pages), "exemplar_pages": pages}
            if matches and len(pages) >= MIN_PAGES:
                dev, wd, ex = matches[0]
                rec.update({"decision": "MERGE", "exemplar_page": ex["page"],
                            "exemplar_box": ex["box"], "exemplar_sig": ex["sig"],
                            "max_dev": dev, "width_diff": wd})
                n_merge += 1
                for w in grp:
                    merged_boxes.add(tuple(w["box"]))
                words.append({"box": ubox, "line": grp[0].get("line"),
                              "font_px": round(float(max(w["box"][3] - w["box"][1] for w in grp)), 1),
                              "n_comp": len(usig), "src": "vocab-gate",
                              "gate": {"version": 3, "exemplar_page": ex["page"],
                                       "exemplar_box": ex["box"],
                                       "exemplar_pages": pages,
                                       "max_dev": dev, "width_diff": wd}})
            else:
                rec.update({"decision": "KEEP",
                            "reason": ("no-exemplar" if not matches
                                       else "single-page-exemplar"),
                            "best_exemplar_page": matches[0][2]["page"] if matches else None,
                            "best_exemplar_box": matches[0][2]["box"] if matches else None})
                n_keep += 1
            decisions.append(rec)
        words = [w for w in words if tuple(w["box"]) not in merged_boxes]
        words.sort(key=lambda w: (w.get("line", 0), w["box"][0]))
        out = dict(seg)
        out["words"] = words
        out["method"] = seg["method"] + " + vocab-gate v3 (Round 6 Track B)"
        with open(os.path.join(OUTDIR, f"seg-{p}-{ARGS.out_suffix}.json"), "w") as f:
            json.dump(out, f, indent=1)
        print(f"{p}: words {len(seg['words'])} -> {len(words)}")

    with open(os.path.join(OUTDIR, "vocab-gate-decisions.json"), "w") as f:
        json.dump({"W_TOL": W_TOL, "N_TOL": N_TOL, "TOT_W_TOL": TOT_W_TOL,
                   "RULE_W": RULE_W, "RULE_H": RULE_H, "MIN_PAGES": MIN_PAGES,
                   "vocab_size": len(vocab), "decisions": decisions}, f, indent=1)
    print(f"DECISIONS: MERGE={n_merge} KEEP={n_keep}")
    for d in decisions:
        if d["decision"] == "MERGE":
            print(f"  MERGE {d['page']} union={d['union_box']} pages={d['exemplar_pages']} "
                  f"<- {d['exemplar_page']} {d['exemplar_box']} max_dev={d['max_dev']}")
        elif d.get("reason") == "single-page-exemplar":
            print(f"  KEEP1 {d['page']} union={d['union_box']} exemplar {d['best_exemplar_page']} {d['best_exemplar_box']}")

if __name__ == "__main__":
    main()
