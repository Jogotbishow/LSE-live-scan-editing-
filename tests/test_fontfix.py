"""Fontfix verification (43 checks) against live pages built by THIS
package's builder — adapted from the prototype's fontfix_verify300.py
(same checks, same expectations, pages built by lse.page).

Inputs are the prototype's canonical artifacts (segs, renders, cleans,
DNA fonts, stamps) — the BUILDER under test is the package's. The seg
counts use MY segmenter's output (test_segment.py proves 302/302);
the Playwright checks use pages built from the canonical segs so the
builder, not the segmenter, is what's measured here.
"""
import base64
import hashlib
import json
import os
import re
import unittest

import cv2
import numpy as np

import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

from helpers import DNA_BOLD, DNA_REG, SP, STAGING, STAMPS_JSON, requires_real_fixtures
from lse.page import build_live_page, jpeg_b64, png_b64
from lse.segment import segment_array
from PIL import Image

OUT = os.path.join(STAGING, "fontfix")
os.makedirs(OUT, exist_ok=True)

CFG = {
    "aug": {"skew": 0.26, "orig": "pages/aug-p1-orig.jpg",
            "orig_sha": "7b171751fb6ab7570560b11d70c614072ebfd8f284b30c440f3374390f172a5d",
            "orig_mime": "image/jpeg", "clean_fmt": "jpeg",
            "demo_lot_c": (582, 948), "demo_wid_c": (2133, 1296),
            "demo_lot_new": "207/9", "demo_wid_new": "781.5",
            "lot_box": [533, 930, 631, 966], "wid_box": [2088, 1282, 2178, 1310],
            "page_meta": {"page_key": "aug-p1", "page_no": 1, "source_page": 1,
                          "source_document": "PG AUGUST-2026 (25mic) COA.pdf p.1",
                          "item": "Blister Foil 25 Micron (PG Foils)",
                          "page_label": "Aug p.1", "old_lot": "206/7", "old_width": "780.0"}},
    "may": {"skew": 0.11, "orig": "pages/may-p1-orig-stored.png",
            "orig_sha": "d0fb6f89f8e931e7e892f1f838108c2919a0ab309a407aac08c61e24ba684682",
            "orig_mime": "image/png", "clean_fmt": "png",
            "demo_lot_c": (570, 932), "demo_wid_c": (2124, 1304),
            "demo_lot_new": "305/7", "demo_wid_new": "671.5",
            "lot_box": [521, 913, 619, 950], "wid_box": [2078, 1290, 2169, 1318],
            "page_meta": {"page_key": "may-p1", "page_no": 1, "source_page": 1,
                          "source_document": "PG MAY-2026 (20mic) COA.pdf p.1",
                          "item": "Blister Foil 20 Micron (PG Foils)",
                          "page_label": "May p.1", "old_lot": "304/5", "old_width": "670.0"}},
}


def _raw_b64(path, mime, sha_expected):
    raw = open(path, "rb").read()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == sha_expected, f"{path}: SHA mismatch {digest}"
    return "data:%s;base64,%s" % (mime, base64.b64encode(raw).decode())


def build_page(page):
    c = CFG[page]
    seg = json.load(open(os.path.join(SP, f"seg-{page}-p1-300.json")))
    gray = cv2.imread(os.path.join(SP, f"pages/{page}-p1-300.png"), cv2.IMREAD_GRAYSCALE)
    color = cv2.imread(os.path.join(SP, f"pages/{page}-p1-300.png"))
    orig_b64 = _raw_b64(os.path.join(SP, c["orig"]), c["orig_mime"], c["orig_sha"])
    if c["clean_fmt"] == "jpeg":
        clean_b64 = jpeg_b64(os.path.join(SP, f"cleans/{page}-p1-clean-300.png"), q=88)
        manual_b64 = jpeg_b64(os.path.join(SP, f"cleans/{page}-p1-clean-manual-300.png"), q=88)
    else:
        clean_b64 = png_b64(os.path.join(SP, f"cleans/{page}-p1-clean-300.png"))
        manual_b64 = png_b64(os.path.join(SP, f"cleans/{page}-p1-clean-manual-300.png"))
    stamps = json.load(open(STAMPS_JSON))[page]["stamp_regions"]
    stamps = [{"box": [round(v * 1.5) for v in s["box"]]} for s in stamps]
    demo = {"lot": {"center": c["demo_lot_c"], "new": c["demo_lot_new"],
                    "expected_box": c["lot_box"]},
            "width": {"center": c["demo_wid_c"], "new": c["demo_wid_new"],
                      "expected_box": c["wid_box"]}}
    out_path = os.path.join(OUT, f"live-scan-page-{page}-300.html")
    _path, words, info = build_live_page(
        gray, color, seg, orig_b64, clean_b64, manual_b64,
        c["page_meta"], out_path, skew_deg=c["skew"],
        bold_mode="canonical", stamps=stamps, demo=demo,
        dna_regular=DNA_REG, dna_bold=DNA_BOLD)
    print(f"  built {page}: {len(words)} words, bold {info['n_bold']}, "
          f"heading flips {len(info['heading_flips'])}, "
          f"fonts {info['dna_fonts']}")
    return out_path


def words_of(html_path):
    s = open(html_path).read()
    m = re.search(r"const WORDS = (\[.*?\]);\nconst DEMO", s, re.S)
    return json.loads(m.group(1))


def near(words, cx, cy):
    best, bd = None, 1e9
    for w in words:
        ccx = w["x"] + w["w"] / 2
        ccy = w["y"] + w["h"] / 2
        d = (ccx - cx) ** 2 + (ccy - cy) ** 2
        if d < bd:
            bd, best = d, w
    return best


SPAN_INFO_JS = """(w) => {
  const S = 1/3;
  const el = [...document.querySelectorAll('.wd')].find(e => {
    const cx = (parseFloat(e.style.left) + parseFloat(e.style.width)/2) / S;
    const cy = (parseFloat(e.style.top) + parseFloat(e.style.height)/2) / S;
    return Math.abs(cx - (w.x + w.w/2)) < 18 && Math.abs(cy - (w.y + w.h/2)) < 18;
  });
  if (!el) return null;
  const cs = getComputedStyle(el);
  let tw = null;
  if (el.textContent.trim()) {
    const r = document.createRange();
    r.selectNodeContents(el);
    tw = r.getBoundingClientRect().width;
  }
  return {text: el.textContent, cls: el.className,
          fontWeight: cs.fontWeight, color: cs.color,
          fontSize: cs.fontSize, fs0: el.dataset.fs0,
          spanW: parseFloat(el.style.width), textW: tw,
          bg: cs.backgroundImage.slice(0, 40)};
}"""


@requires_real_fixtures
class TestFontfix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = {p: build_page(p) for p in ("aug", "may")}
        cls.results = []

    def check(self, name, ok, detail=""):
        self.__class__.results.append((name, ok, detail))
        print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")
        self.assertTrue(ok, f"{name}: {detail}")

    def test_all_43(self):
        # ---- segmentation counts (MY segmenter — test_segment proves
        # it; re-run here so the count is from the package, not the
        # JSON). Counts are MY numbers on MY render (render drift, see
        # test_segment.py): Aug 308 total / 38 rows, May 307 / 37.
        import helpers
        for page, bands, exp, tot_exp, label in (
                ("aug", {1: (1200, 1252), 2: (1260, 1308), 3: (1323, 1372),
                        4: (1384, 1432), 5: (1446, 1497)}, 38, 308, "Aug rows 01-05"),
                ("may", {1: (1200, 1260), 2: (1260, 1327), 3: (1327, 1402),
                        4: (1402, 1485), 5: (1485, 1567)}, 37, 307, "May rows 01-05")):
            pdf = helpers.PG_AUG if page == "aug" else helpers.PG_MAY
            seg = segment_array(helpers.render_bgr(pdf, 0, dpi=300), image_name=page)
            tot = 0
            for lo, hi in bands.values():
                tot += sum(1 for w in seg["words"] if lo <= (w["box"][1] + w["box"][3]) / 2 <= hi)
            self.check(f"{label} boxes", tot == exp, f"got {tot}, expected {exp}")
            self.check(f"{label.split()[0]} total words", len(seg["words"]) == tot_exp,
                       f"got {len(seg['words'])}")
        may = json.load(open(os.path.join(SP, "seg-may-p1-300.json")))
        title_boxes = [w for w in may["words"] if 592 <= (w["box"][1] + w["box"][3]) / 2 <= 630]
        self.check("May title boxes", len(title_boxes) == 3, f"got {len(title_boxes)}")
        note_boxes = [w for w in may["words"] if 2985 <= (w["box"][1] + w["box"][3]) / 2 <= 3030]
        self.check("May note-line boxes", len(note_boxes) == 17, f"got {len(note_boxes)}")

        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            for label, html, lot_xy, wid_xy, lot_new, wid_new in (
                    ("Aug", self.html["aug"], (582, 948), (2133, 1296), "207/9", "781.5"),
                    ("May", self.html["may"], (570, 932), (2124, 1304), "305/7", "671.5")):
                words = words_of(html)
                pg = b.new_page(viewport={"width": 900, "height": 1520})
                pg.goto("file://" + html + "?demo=1&boxes=1")
                pg.wait_for_timeout(3000)
                lot_w, wid_w = near(words, *lot_xy), near(words, *wid_xy)
                exp_lot = [533, 930, 631, 966] if label == "Aug" else [521, 913, 619, 950]
                exp_wid = [2088, 1282, 2178, 1310] if label == "Aug" else [2078, 1290, 2169, 1318]
                self.check(f"{label} demo Lot box identity",
                           [lot_w["x"], lot_w["y"], lot_w["x"] + lot_w["w"], lot_w["y"] + lot_w["h"]] == exp_lot,
                           f"got {[lot_w['x'], lot_w['y'], lot_w['x'] + lot_w['w'], lot_w['y'] + lot_w['h']]}")
                self.check(f"{label} demo WIDTH box identity",
                           [wid_w["x"], wid_w["y"], wid_w["x"] + wid_w["w"], wid_w["y"] + wid_w["h"]] == exp_wid,
                           f"got {[wid_w['x'], wid_w['y'], wid_w['x'] + wid_w['w'], wid_w['y'] + wid_w['h']]}")
                lot_i = pg.evaluate(SPAN_INFO_JS, lot_w)
                wid_i = pg.evaluate(SPAN_INFO_JS, wid_w)
                self.check(f"{label} demo Lot -> {lot_new}", lot_i and lot_i["text"] == lot_new, f"got {lot_i}")
                self.check(f"{label} demo WIDTH -> {wid_new}", wid_i and wid_i["text"] == wid_new, f"got {wid_i}")
                for nm, info in (("Lot", lot_i), ("WIDTH", wid_i)):
                    self.check(f"{label} {nm} typed span has clean bg (no doubling)",
                               info is not None and (info["bg"] or "").startswith('url("data:image/'),
                               f"bg={info and info['bg'][:40]}")
                _want_w = "700" if label == "May" else "400"
                self.check(f"{label} WIDTH obs {'bold (700)' if label == 'May' else 'regular (400)'}",
                           wid_i and wid_i["fontWeight"] == _want_w,
                           f"weight={wid_i and wid_i['fontWeight']} ratio={wid_w.get('ratio')}")
                for nm, info, w in (("Lot", lot_i, lot_w), ("WIDTH", wid_i, wid_w)):
                    if info and info["textW"]:
                        r = info["textW"] / info["spanW"]
                        self.check(f"{label} {nm} typed width / box width", 0.7 <= r <= 1.05,
                                   f"ratio={r:.2f} textW={info['textW']:.1f} boxW={info['spanW']:.1f} fs={info['fontSize']} fs0={info['fs0']}")
                hdr_xy = (345, 1160) if label == "Aug" else (334, 1143)
                par_xy = (510, 1160) if label == "Aug" else (502, 1143)
                for nm, xy, want in (("TEST header", hdr_xy, "700"), ("PARAMETERS header", par_xy, "700")):
                    w = near(words, *xy)
                    info = pg.evaluate(SPAN_INFO_JS, w)
                    got = info["fontWeight"] if info else None
                    self.check(f"{label} {nm} bold ({want})", got == want,
                               f"weight={got} ratio={w.get('ratio')} box={[w['x'], w['y'], w['x'] + w['w'], w['y'] + w['h']]}")
                tline = [w for w in words if (607 <= (w["y"] + w["h"] / 2) <= 660 if label == "Aug" else 592 <= (w["y"] + w["h"] / 2) <= 630)]
                for w in tline:
                    info = pg.evaluate(SPAN_INFO_JS, w)
                    got = info["fontWeight"] if info else None
                    self.check(f"{label} title word {[w['x'], w['y'], w['x'] + w['w'], w['y'] + w['h']]} bold (700)", got == "700",
                               f"weight={got} ratio={w.get('ratio')}")
                self.check(f"{label} WIDTH ink colour != #111", wid_i and wid_i["color"] not in ("rgb(17, 17, 17)",),
                           f"color={wid_i and wid_i['color']} (word color={wid_w.get('color')})")
                pg.screenshot(path=f"{OUT}/fontfix-page-{label.lower()}-edited-300.png", full_page=True)
                pg2 = b.new_page(viewport={"width": 900, "height": 1520})
                pg2.goto("file://" + html)
                pg2.wait_for_timeout(2000)
                wid_el = pg2.locator(f".wd[data-i='{words.index(wid_w)}']")
                wid_el.click()
                pg2.wait_for_timeout(300)
                pg2.keyboard.press("ControlOrMeta+a")
                pg2.keyboard.type("1234.56")
                pg2.wait_for_timeout(400)
                info = pg2.evaluate(SPAN_INFO_JS, wid_w)
                r = info["textW"] / info["spanW"] if info and info["textW"] else None
                fs_ratio = float(info["fontSize"].replace("px", "")) / float(info["fs0"]) if info else None
                self.check(f"{label} long replacement '1234.56' width-fit", r is not None and r <= 1.10,
                           f"width ratio={r and round(r, 2)} font-size ratio={fs_ratio and round(fs_ratio, 2)}")
                self.check(f"{label} long replacement font-size within ceiling", fs_ratio is not None and fs_ratio <= 1.25,
                           f"fs ratio={fs_ratio and round(fs_ratio, 2)}")
                pg2.close()
                pg.close()

            # ---- D1 edge case (Aug page, fresh load) ----
            pg = b.new_page(viewport={"width": 900, "height": 1520})
            pg.goto("file://" + self.html["aug"])
            pg.wait_for_timeout(2000)
            words = words_of(self.html["aug"])
            lot_w = near(words, 582, 948)
            wid_w = near(words, 2133, 1296)
            lot_el = pg.locator(f".wd[data-i='{words.index(lot_w)}']")
            wid_el = pg.locator(f".wd[data-i='{words.index(wid_w)}']")
            lot_el.click()
            pg.wait_for_timeout(300)
            pg.keyboard.type("207/9")
            pg.wait_for_timeout(300)
            wid_el.click()
            pg.wait_for_timeout(300)
            st1 = pg.evaluate(SPAN_INFO_JS, lot_w)
            self.check("D1 after click-away, typed Lot keeps .done", st1 and "done" in st1["cls"],
                       f"cls={st1 and st1['cls']}")
            lot_el.click()
            pg.wait_for_timeout(300)
            pg.keyboard.press("ControlOrMeta+a")
            pg.keyboard.press("Delete")
            pg.wait_for_timeout(300)
            wid_el.click()
            pg.wait_for_timeout(400)
            st2 = pg.evaluate(SPAN_INFO_JS, lot_w)
            self.check("D1 after delete-all + click-away, empty Lot LOSES .done",
                       st2 is not None and "done" not in st2["cls"] and st2["text"] == "",
                       f"cls={st2 and st2['cls']} text={st2 and repr(st2['text'])} bg={st2 and st2['bg']}")
            self.check("D1 empty Lot shows original scan again (no clean bg)",
                       st2 is not None and st2["bg"] in ("none", ""),
                       f"bg={st2 and st2['bg']}")
            pg.close()
            b.close()
        npass = sum(1 for _, ok, _ in self.results if ok)
        print(f"\nTOTAL: {npass}/{len(self.results)} checks passed")
        self.assertEqual(npass, 43, f"expected 43/43, got {npass}/43")


if __name__ == "__main__":
    unittest.main(verbosity=2)
