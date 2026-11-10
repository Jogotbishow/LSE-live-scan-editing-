# LSE Round 25 — রিপোর্ট

**তারিখ:** 2026-11-09 · **ভাষা:** বাংলা · **মার্জ এজেন্ট:** Round 25 coordinator
**Baseline:** Round 24 merged segmenter + gate (`round24/merge-r24/`, gate 23/2) — read-only, ভাঙা হয়নি
**নতুন baseline:** `improve/round25/merge-r25/` (segment_merged.py + gate_merged.py + rhythm_dp.py + logo_detect.py + gate_misses.py + segs/)
**ডিরেক্টরি:** `improve/round25/` — প্রতি ট্র্যাকের নিজের ডিরেক্টরিতে তার সব আউটপুট; merge `merge-r25/`-তে
**নির্দেশ:** ব্যবহারকারীর LSE 100% নিয়ম (2026-11-08 22:42) — Muse নিজে 100% সন্তুষ্ট না হওয়া পর্যন্ত LSE-র কাজ থামবে না; কোনো অনুমতি লাগবে না। এই রাউন্ড সেই নির্দেশেই চলেছে।

> **সৎ সারাংশ:** Gate 23/2 → **23/2 — অপরিবর্তিত**। ৭টি ট্র্যাকের মধ্যে **একটিই PROMOTE — gate T4 over-split eye** (R24-র মাপা blind spot বন্ধ হয়েছে: bridge/seam-এর দুটি false 24/1 এখন T4-এ REFUSE)। Segmenter-এ কোনো বদল নেই — p20-র fused লাইন, p21-র ৭-শব্দ stretch, p21 heading — তিনটিই এখন **প্রমাণিত geometry-only known limit** (R24-র তিনটি ব্যর্থতার সঙ্গে আরও চারটি স্বাধীন ব্যর্থতা যোগ হয়েছে: Omron M, skeleton-graph, tree-indexed demarcation, fuzzy vote — সবাই 0/4)। সৎ প্রশ্নের উত্তর এখনও খোলা: geometry-only উপায়ে 25/0 কি আদৌ সম্ভব? — Round 26-র জন্য নতুন lead আছে (feature-point contact detection, τ-signal, drop-fall), কিন্তু 2024–2026-এ কোনো breakthrough নেই।

---

## ০. এক নজরে — headline সংখ্যা

| মাপ | R24 baseline | **Round 25 merge** |
|---|---:|---:|
| Gate (২৫ Raviraj পাতা) | 23 ALLOW / 2 REFUSE | **23 ALLOW / 2 REFUSE (=)** |
| ফ্ল্যাগ (T1 / T2 / T3 / T4) | 2 (0 / 0 / 2 / —) | **2 (0 / 0 / 2 / 0) — T4 নতুন, baseline-এ ০** |
| মোট শব্দ (২৫ পাতা) | 9373 | **9373 (=)** |
| মোট শব্দ (৩৩ পাতা) | 12366 | **12366 (=)** |
| REFUSE পাতা | p20 + p21 | **p20 + p21 (=)** |
| Canonical p2 N5 / Description ভুল / redbox | 41/81, ভুল ৩০, 7/66 | **41/81 (=), ভুল ৩০ (=, একই list), 7/66 (=)** |
| Canonical p3 strict / improved (FP) | 248 / 285 (186) | **248 (=) / 285 (=) (186, =)** |
| Canonical p2 / p3 gate | p2 ALLOW, p3 ALLOW | **p2 ALLOW, p3 ALLOW (=)** |
| LINES (canonical r15m) | 327/327 | **327/327 (=)** |
| PG ৬ পাতা (শব্দ) | aug 306/308/305, may 308/313/306 | **aug 306/308/305, may 308/313/306 — হুবহু একই** |
| Fitz render (১৪ PG পাতা) | aug 308/308/305/307/303/303/311/309, may 307/313/305/306/305/309 | **সব ১৪ পাতা SAME** |
| p21 GT (৪২ certain boundary) | 36/42 @ ±5px meet-rule | **36/42 (=, segs byte-identical বলে অপরিবর্তিত)** |
| Guard (live page, FULL) | 5/5 | **5/5 PASS (segs byte-identical বলে অপরিবর্তিত)** |
| Round 3 DB SHA | `1c065457…` | **`1c065457…` — আগে ও শেষে একই** |
| Full suite (repo test clone) | 38/38 | **40/40 PASS (402.29s, 0 fail) — ৩৮ পুরনো + ২ নতুন T4 test** |
| Demo (synthetic) | 82 শব্দ | **82 শব্দ (=, নিজে চালিয়ে যাচাই)** |
| Aug p1 শব্দ-সংখ্যা | PNG 306 / fitz 308 | **PNG 306 / fitz 308 — দুই render-পথেই সঠিক** |

**ফ্লিপ:** কোনোটিই নয় — ২৩টি ALLOW পাতার একটিও regress হয়নি, আর p20/p21-র একটিও ALLOW হয়নি। **Promotion bar-এর রায়: শুধু gate T4 promote হয়েছে — segmenter-এ কিছুই না।** T3 recall 35/35 (100%) অপরিবর্তিত, coverage 95/97 অপরিবর্তিত। এই রাউন্ডের ফসল **দুটি জিনিস**: (ক) gate-এর blind spot বন্ধ (T4) — ভবিষ্যতের ভুল ALLOW আর ধরা পড়বে; (খ) **প্রমাণ** — p20-র লাইনে চারটি নতুন স্বাধীন পদ্ধতি-পরিবারও ব্যর্থ, আর প্রতিটির ব্যর্থতার কারণ মাপা আছে।

---

## ১. ট্র্যাক verdicts — ৭টি ট্র্যাক, ১টি PROMOTE

| ট্র্যাক | verdict | মূল ফল |
|---|---|---|
| **track-omron** | **DO NOT PROMOTE** | US 9,710,945 (P(x) min-projection + fitted line M, S5–S8 faithfully): p20-তে **0/4 শব্দ**, p21-তে **0/7 শব্দ**। Premise মাপায় ভেঙেছে: সবচেয়ে দুর্বল intra-word gap (+18.7) সবচেয়ে শক্ত সত্য সীমানাকে **৯.১–১২.০ grey level-এ** হারায় — প্রতি Dα-তে, উল্টো দিকে। Omron p20-তে ৪২–৪৩টি cut প্রস্তাব করে, ৩১–৩২টি শব্দের ভেতরে। p21-তে ৩৪–৪১টি ভুল run; একই পাতার আসল একক শব্দের ভেতরের run (P−M 126.8) stretch-এর সত্য সর্বনিম্ন (98.6) ছাড়িয়ে যায়; ৩৬টি bridge cut-এ সেরা threshold ভুল **৪/৩৬**, ভুল cut `R\|av` (+148.8) সব সত্য সীমানার ওপরে। ১৮-gap no-false-cut: p20-তে **১৬/১৬** intra gap কাটা, p21-তে ৯৮–১২৬টি ভুল run। |
| **track-skeleton** | **DO NOT PROMOTE** | US 5,787,196 (skeleton-graph): p20-তে **0/4 শব্দ**। Skeleton আসল (নিজের Zhang–Suen thinning, ৪৫টি branch-node cluster, ৪১টি অক্ষর) — কিন্তু node-গুলি শব্দের শেষ কোথায় তা বলে না: যেকোনো ±5px window-এ chance-এই ~১.০৫টি node থাকে; boundary-কাছের depth [1.40, 4.00] বনাম অন্যত্র [1.40, 5.79] — পুরো overlap। প্রতিটি node-এ cut: ৪৪টি cut → ৪৫ টুকরো, **0/4**, ৪১টি ভুল cut। Patent-faithful cost: ৩৪/৪৫টি node disconnect করে, কিন্তু **column overlap সব ৩৪টির ০.০০০** (dead signal — যেকোনো left/right split x-disjoint); boundary node rank ৫ ও ২৮ (৩৪-এর মধ্যে), rank ১ EXPORTER-এর ভেতরে। Control: ৩৫টি আসল একক শব্দে **২৬১টি branch node, ১৬৩টি patent split**, ৩৪/৩৫টি শব্দে ≥১টি। |
| **track-tree** | **DO NOT PROMOTE** | Tang 2017 (tree-indexed demarcation): p20-তে **0/3 সত্য সীমানা, 0/4 শব্দ**। Tree-তে সত্যের কাছের valley আছে (১২২/২৬০/৩৩৯, ১–৫px) — selection-ই ব্যর্থতা। Oracle n=4, ২০,০০২টি ৩-cut combo-র মধ্যে সেরা CV-র cut **[106, 212, 320]**, widths [106,106,108,109], CV **0.0121** — সব cut শব্দের ভেতরে। সত্যের কাছের combo [129,260,345] (CV 0.2122, ৪/৪ উদ্ধার) rank **579th** — width variation সত্য শব্দের চেয়ে সমান slice-কে **১৭.৫×** পছন্দ করে। সত্য শব্দের width [125,130,85,89], CV 0.190 — Tang-এর criterion অক্ষরের (near-equal width), শব্দের নয়। Free-n: pure CV-র optimum k=1 (না কাটা, CV 0)। Count-driven baseline (০ good valley)-র চেয়ে **কোনো উন্নতি নেই**। |
| **track-fuzzy** | **DO NOT PROMOTE** | Farulla 2017 (fuzzy vote, Mamdani R1–R6 + centroid, per-line calibrated): combination আলাদা করে না — **১৮/১৮টি intra gap সব সত্য সীমানার ওপরে** (fuzzy vote 0.3463–0.6436 বনাম সীমানা 0.2948–0.3382; additive vote 0.6489–0.9851 বনাম 0.2470–0.4746)। Fuzzy rank: B1 283, B2 223, B3 229 (৪২৯ কলামের মধ্যে নিচের অর্ধেক)। Integrated splitter: ৯ টুকরো, **0/4 শব্দ**; আর p01/p2-র horizontal **rule**-কে ৫ টুকরো করেছে (৪টি ভুল cut) — guard-এর দুর্বলতা প্রকাশ পেয়েছে (§৬)। Gate 24/1 — **false pass** (bridge/seam-এর মতোই)। ৩৩ পাতায় শুধু p20 (৫২১→৫২৯), p01 (৬৭৬→৬৮০), p2 (৬৭৬→৬৮০) বদলায়। |
| **track-heading** | **DO NOT PROMOTE — KNOWN LIMIT (চতুর্থ পদ্ধতি-পরিবারেও)** | US 10,586,125 (reduced underline): সেরা ফল **৫/৮** — CONTROL-এর (নিখুঁত band deletion) ৫/৮-এর **সমান**, একই ৫টি শব্দ আর একই ৩টি ব্যর্থতা (Review ৬px letter gap-এ ভাঙা; `of` জোড়া; Recommendation-এর `R` নেই)। Patent-এর primary মান দেয় ২/৮। Intersection pattern-এ word-boundary signal নেই (NO-run width সীমানায় [36,8,7,12,15,19,19] বনাম সব NO-run [1..40] — পুরো overlap)। **নতুন নির্ণায়ক তথ্য (reachability wall):** heading blob (৯৯৩px চওড়া) পাইপলাইনের comp filter `ww > 900`-এ line-grouping-এর আগেই ফেলে দেওয়া হয় — splitter-এর ভেতরে কোনো বদলই তাকে বাঁচাতে পারে না, নীতিগতভাবে। End-to-end p21: শব্দ ৫৮৪ = ৫৮৪, heading এখনও dropped — কিন্তু ২টি word box ৭px ও ১px ছোট হয়ে আসল কালি কেটে ফেলে (patent-এর long-row test dense bold text-এ misfire করে)। |
| **track-gate** | **PROMOTE** | **T4 over-split eye** — R24-র blind spot বন্ধ (§৬)। Bridge-এর false 24/1 → **২৩/২** (p20 REFUSE via T4, ৫/৫ white cut); seam-এর false 24/1 → **২৩/২** (p20 REFUSE via T4, ৭/৭ white cut)। Baseline 23/2-এ **T4 = 0 সর্বত্র** (২৩টি ALLOW পাতা, ৮টি extra, ১৪টি fitz PG পাতা × ৩ seg set — ০ false positive)। Synthetic সঠিক split (cut 677/812/897) ALLOW, T4 = 0 — চোখ split-কে বিচার করে, ছবিকে নয়। Gate diff purely additive (১৬০ insertion, ০ deletion)। Suite 40/40 PASS (৩৮ + ২ নতুন T4 test)। |
| **track-online** | **গবেষণা (কোড নয়)** | RESEARCH25.md (২৩০ লাইন, ২৬টি source — R21–R24-এর কোনোটি পুনরাবৃত্তি নয়; ১৪টি আসল নতুন geometry-only lead)। Top 3 — (১) **JP2000322514A (2000)** contact-point detection (thinned-stroke feature-point connection — histogram minimum নয়, ঠিক p20-র ক্ষেত্রে); (২) **US 20150086113 (2015)** τ-signal (column ink-count × longest ink-run, aspect-ratio gate); (৩) **drop-fall family** (Roe & Mello 2009, Chatelain DAS 2006, Congedo ICDAR'95 — valley ছাড়াই contour-following cut path)। আরও: watershed/distance-transform, modal-stroke-width ligature detector, Hoover/OAM over-split eye, DTW contour-corner pairing। **সৎ verdict: 2024–2026-এ geometry-only word segmentation-এ কোনো breakthrough নেই** — newest আসল geometry-only কাজ **২০১৭** (Jstage)। |

---

## ২. merge — কী নেওয়া হয়েছে, কী নেওয়া হয়নি

**নেওয়া হয়েছে:** শুধু gate T4 over-split eye (track-gate) — `gate_merged.py`-তে ১৬০ insertion, ০ deletion (merge script-এ যাচাই: `merge_segment_r25.py`)।
**নেওয়া হয়নি:** Omron M, skeleton-graph, tree-indexed demarcation, fuzzy vote, reduced underline — সব DO NOT PROMOTE, ফাইল শুধু rejected experiment হিসেবে ট্র্যাক-ডিরেক্টরিতে আছে।

মার্জ-প্রক্রিয়া (পুনরুৎপাদনযোগ্য — স্ক্রিপ্ট `improve/round25/merge-r25/`-তে রাখা আছে):
- `merge_segment_r25.py` — segmenter + ৩টি support ফাইল (rhythm_dp.py, logo_detect.py, gate_misses.py) R24-র সঙ্গে **SHA-256 byte-identical** (segment `86541e29af96`); gate diff ০ deletion / ১৬০ addition, T4 marker ৬টি present।
- `run_segs_r25.py` — ৩৩ পাতা re-segment: **৩৩/৩৩ box byte-identical** (R24 segs-এর সঙ্গে diff খালি); শব্দ 9373/12366 হুবহু।
- `run_gate_r25.py` — gate re-run: **ALLOW 23 / REFUSE 2, T1 0, T2 0, T4 0**; ২৫ পাতার প্রতিটি SAME (R24 baseline-এর সঙ্গে); canonical p2/p3 ALLOW, PG ৬ পাতা ALLOW।
- `score_canon.py` — p2 N5/Desc/redbox SAME; p3 strict **248/384**, improved **285/384**, FP 186 — সংখ্যা হুবহু।
- **T4 false-case যাচাই (merge করা gate দিয়ে, নিজে চালানো):** bridge segs-এ p20 REFUSE via T4 (৫ white cut), set 23/2; seam segs-এ p20 REFUSE via T4 (৭ white cut), set 23/2 — দুটি false 24/1-ই ধরা পড়েছে।
- Repo port: `~/workspace/lse-r25-test/` (lse-r24-test-এর কপি) — repo `lse/gate.py`-তে T4 port + ২টি নতুন test; **full suite 40/40 PASS (402.29s, 0 fail)**।

---

## ৩. p20-র fused লাইন — চারটি নতুন ব্যর্থতা, একটিই সত্য

p20-র লাইন `[557,661,986,678]` (BENEFICIARY/MANUFACTURER/EXPORTER/SHIPPER, ৪টি শব্দ, ৩টি সত্য সীমানা) এখন geometry-only known limit — R24-র তিনটি ব্যর্থতার (diagnosis, greyscale bridge, min-cost seam) সঙ্গে এই রাউন্ডে আরও চারটি স্বাধীন পদ্ধতি-পরিবার যোগ হয়েছে, প্রতিটি মাপা প্রমাণসহ:

| পদ্ধতি | ফল | ব্যর্থতার কারণ (মাপা) |
|---|---|---|
| Greyscale bridge (R24) | 0/4, ৫ ভুল cut | সত্য সীমানা সব gap-এর চেয়ে শক্ত bridge |
| Min-cost seam (R24) | 0/4, ৮ টুকরো | seam cost সত্য সীমানায় worst gap-এর ৩.৫–৫.৩× |
| **Omron M (R25)** | **0/4, ৪২–৪৩ cut** | P−M-এ দুর্বলতম intra gap (+18.7) শক্ততম সত্য সীমানাকে ৯.১–১২.০ grey level-এ হারায় — উল্টো দিকে, প্রতি Dα-তে |
| **Skeleton-graph (R25)** | **0/4, ৪৫ টুকরো** | node-গুলি শব্দের শেষ বলে না (chance-এই ±5px window-এ ~১.০৫ node); column overlap সব ০.০০০ (dead signal) |
| **Tree-indexed (R25)** | **0/3, 0/4** | width variation সত্যের চেয়ে সমান slice-কে ১৭.৫× পছন্দ করে (CV 0.0121 বনাম 0.2122); সত্য combo rank 579th / 20,002 |
| **Fuzzy vote (R25)** | **0/4, ৯ টুকরো** | ১৮/১৮টি intra gap সব সত্য সীমানার ওপরে — combination-ও উল্টো, কারণ input-গুলোই উল্টো |

একটিই সত্য বাকি থাকে: **সত্য সীমানাগুলো অক্ষরের sequence ছাড়া চেনা যায় না** — grey halo word-gap আর letter-gap-এ একই, আর আলাদা করার তথ্য letter sequence-এ থাকে, অর্থাৎ recognition-এ। এটা geometry-only সীমার প্রমাণ, চেষ্টার অভাব নয়। Round 26-র lead-গুলি (§১০) এই সীমাকে নতুন দিক থেকে আক্রমণ করে — feature-point topology (ink quantity নয়), τ-signal, drop-fall (valley ছাড়াই cut path)।

---

## ৪. p21-র ৭-শব্দ stretch — ACCEPTED KNOWN LIMIT (বহাল)

p21-র stretch ("three months before the date of expiry", ৭ শব্দ) **accepted known limit** হিসেবে বহাল। এই রাউন্ডে Omron M সেটাকেও পরীক্ষা করেছে: ৬টি সত্য সীমানাই P>M run — কিন্তু একই box-এ **৩৪–৪১টি ভুল run** প্রতিটি Dα-তে, প্রতিটি শব্দ ছিঁড়ে যায়। Box-এর ভেতরে peak P−M আলাদা দেখায় (সত্য সর্বনিম্ন 98.6–103.7 বনাম ভুল সর্বোচ্চ 69.4–80.1) — কিন্তু তা generalise করে না: একই পাতার আসল একক শব্দের ভেতরের run 126.8, আর ৩৬টি bridge cut-এ সেরা threshold ভুল ৪/৩৬ (ভুল cut `R|av` +148.8 সব সত্য সীমানার ওপরে)। **সংশোধন (R24-র §৯ বহাল):** "৯ সঠিক / ১৫ ভুল" আসলে **৮ সঠিক / ১৬ ভুল** (১৭ সত্য / ১৯ ভুল cut)। নতুন discriminator (Omron M / module 14 নির্ভুল রূপ) পরীক্ষা করা হয়েছে — Omron ব্যর্থ; module 14-র নির্ভুল রূপ এখনও বাকি (§১০)।

---

## ৫. p21 heading — KNOWN LIMIT (চতুর্থ পদ্ধতি-পরিবারেও, reachability wall-সহ)

Reduced underline (US 10,586,125) heading-কে বাঁচাতে পারেনি: সেরা ফল **৫/৮**, CONTROL-এর (নিখুঁত band deletion) ৫/৮-এর সমান — একই ৫টি শব্দ, একই ৩টি ব্যর্থতা। Patent-এর primary মান দেয় ২/৮। Intersection pattern-এ word-boundary signal নেই। **নতুন নির্ণায়ক তথ্য:** heading blob (৯৯৩px চওড়া) পাইপলাইনের comp filter `ww > 900`-এ line-grouping-এর আগেই ফেলে দেওয়া হয় — splitter-এর ভেতরে কোনো বদলই তাকে বাঁচাতে পারে না, নীতিগতভাবে। এছাড়া patent-এর long-row test dense bold text-এ misfire করে (৫১px letter-bottom ink-কে "underline" ভেবে ২টি word box ৭px ও ১px ছোট করে আসল কালি কেটে ফেলে)। যা দরকার হবে: (ক) recognition-based grouping (letter sequence/lexicon — বর্তমানে বাদ), যা CONTROL-এর ৫/৮-কে ৮/৮ করতে পারে; অথবা (খ) geometry/grey/run/intersection-pattern-এর বাইরে সম্পূর্ণ নতুন signal।

---

## ৬. Gate blind spot বন্ধ হয়েছে (T4) — আর একটি নতুন সতর্কতা

**T4 কীভাবে কাজ করে:** (১) RUN — একই text line-এ পাশাপাশি টুকরো (gap ≤ 2px, y-overlap ≥ 0.5× ছোট height); (২) RE-FUSE — run-এর union box Path C-র নিজের leg পাস করতে হবে (width ≥ 12×med_h, প্রতিটি Otsu CC ≥ 2.0×med_h, cover ≥ 0.5, longest internal CC gap ≤ 2px); (৩) WHITE-CUT VOTE — প্রতিটি internal boundary কলামে Otsu-ink fraction ≤ **0.60** হলে white cut (মাপা empty interval: ১২টি ভুল cut ≤ 0.529, ৩টি সত্য slash কলাম ≥ 0.647; threshold 0.60 তার মাঝখানে)। একটি white cut-ই run-কে flag করে। সঠিক split কাটে শুধু slash দিয়ে (dark, 0.647+), তাই flag হয় না — চোখ split-কে বিচার করে, ছবিকে নয়।

**মাপা ফল:** bridge false 24/1 → **23/2** (p20 REFUSE via T4, ৫/৫ white cut); seam false 24/1 → **23/2** (p20 REFUSE via T4, ৭/৭ white cut)। Baseline 23/2-এ **T4 = 0 সর্বত্র** (২৩টি ALLOW পাতা, ৮টি extra, ১৪টি fitz PG পাতা × ৩ seg set — ০ false positive)। Synthetic সঠিক split (cut 677/812/897) ALLOW, T4 = 0। **Known limit (লুকানো নয়):** vote একটি কলাম পড়ে, তাই সঠিক cut-কে slash centre-র ~±1px-এর মধ্যে পড়তে হবে (slash-এর dark span ৬–৯ কলাম); ২px+ off cut white পড়ে flag হবে — সেই cut misplaced (letter ink কাটে), তাই flag করা defensible, কিন্তু tolerance সরু।

**নতুন সতর্কতা (fuzzy ট্র্যাকের খুঁজে পাওয়া):** seam guard-এর দুর্বলতা latent ছিল — fuzzy vote তা প্রকাশ করেছে: guard p01/p2-র horizontal **rule**-এও fire করে (৩০৭×৫px, single CC, row ink ২৯৮/৩০৭ পর্যন্ত) আর ৫ টুকরো করে ফেলে। Guard-এর কোনো text-vs-rule test নেই, আর "box-এর নিজের median-এর ওপরে" selection যেকোনো guard-fire করা জিনিসকে shred করতেই বাধ্য। ভবিষ্যতের split src-এর জন্য guard-এ text-vs-rule test দরকার — Round 26-র gate-কাজ।

---

## ৭. R23/R24-র শিক্ষা মানা হয়েছে — দুই render-ই যাচাই, E2 অক্ষত

- **দুই render:** সব segmenter ট্র্যাক PNG + fitz যাচাই করেছে (p20-তে PNG vs raw fitz byte-identical; Omron/skeleton/fuzzy তিনজনেই দুই render-এ একই সংখ্যা; heading PNG ও fitz identical)। কোনো "কিছুই বদলায় না" দাবি এক render-এ করা হয়নি।
- **E2 অক্ষত:** R21 `_gap_mark` excuse-এর কোনো বদল হয়নি — কোনো ট্র্যাকই তা ছোঁয়নি, fitz Aug p1 ৩০৮ ধরে রেখেছে। R23-র E2 removal regression (suite 35/38) এই রাউন্ডে পুনরাবৃত্তি হয়নি।
- **কোনো test expectation বদলানো হয়নি।** কোনো threshold fit করা হয়নি (T4-র 0.60 মাপা empty interval-এর মাঝখানে, fitted value নয় — §৬)। Suite workspace TMPDIR-এ চালানো হয়েছে (`$HOME/workspace/lse-verify-tmp`), /tmp নয়।

---

## ৮. coverage — 95/97 অপরিবর্তিত

এই রাউন্ডে কোনো misses fix নেওয়া হয়নি — coverage সত্য **95/97** (R23-র সংশোধনসহ), অপরিবর্তিত। বাকি ২টি আসল + ৩টি known-limit miss আগের মতোই: CARRIER NAME লাইন (৮ শব্দ), p21 heading, p21 address লাইন (২৬ শব্দ ১৪ box-এ), p10 "Prepared" (geometry-only unfixable), আর stamp fragment-গুলি (সঠিকভাবে drop)।

---

## ৯. সংশোধন (corrections — আগের রিপোর্টের ভুল ঠিক করা)

1. **R24-র "Drop flow method, 96.0%" লাইন — অসমর্থিত (online ট্র্যাকের সংশোধন):** "Drop flow" নামে কোনো স্বাধীন source বা 96.0%-র কোনো source খুঁজে পাওয়া যায়নি — সম্ভবত garbled "Drop Fall"। আসল Drop Fall source-গুলি (Roe & Mello 2009, Chatelain DAS 2006, Congedo ICDAR'95) এখন RESEARCH25.md-তে documented। R24-র লাইনটি আর উদ্ধৃত করা যাবে না।
2. **R24-র §৯ সংশোধনগুলি বহাল:** p21 "৯ সঠিক / ১৫ ভুল" → **৮ সঠিক / ১৬ ভুল** (১৭ সত্য / ১৯ ভুল cut); Omron lead-এর premise বনাম p20diag-র মাপ (এই রাউন্ডে Omron সরাসরি পরীক্ষা করে premise-টি **মাপায় ভেঙেছে** — §১); module 14 vote বনাম weak_frac (prior কম, নির্ভুল রূপ এখনও বাকি)।
3. **R24-র "newest geometry-only কাজ ২০২০-এর" দাবি — সংশোধন:** ২০২০-র seam কাজ sub-word/handwritten ছিল; আসল geometry-only word-splitting-এর newest কাজ **২০১৭** (Jstage) — online ট্র্যাকের মাপ।

---

## ১০. খোলা বিষয় (open items — Round 26-র জন্য)

1. **p20-র fused লাইন** (`[557,661,986,678]`) — proven known limit, কিন্তু Round 26-র নতুন পরীক্ষা (online Top 3-র ক্রমে): (ক) **JP2000322514A feature-point contact detection** (thinned-stroke feature-point connection — histogram minimum নয়, ঠিক p20-র ক্ষেত্রে যেখানে সত্য সীমানা gap-এর চেয়ে গাঢ়); (খ) **US 20150086113 τ-signal** (τ = column ink-count × longest ink-run, aspect-ratio gate A > 1; threshold per-page হতে হবে, patent-এর heuristic "10" নয়); (গ) **drop-fall family** (Roe & Mello 2009, Chatelain DAS 2006, Congedo ICDAR'95 — valley ছাড়াই contour-following cut path); (ঘ) **watershed/distance-transform** (OpenCV tutorial — p20-র ৪র্থ পথ); (ঙ) **DTW contour-corner pairing** (Xu, Yin & Liu — exploratory)। "Do not try" list: global τ threshold, যেকোনো classifier/recognition step, warn-only gate।
2. **p21-র ৭-শব্দ stretch** — **ACCEPTED KNOWN LIMIT** (§৪)। Round 26-র সিদ্ধান্ত: module 14-র নির্ভুল রূপ (dark-threshold connection fraction + weighted neighbour) পরীক্ষা করা, নাহলে limit-টি বহাল রাখা — জোর করে ভাঙা যাবে না। সৎ প্রশ্নটি খোলা থাকে: geometry-only উপায়ে 25/0 কি আদৌ সম্ভব? — এর উত্তর Round 26-র পরীক্ষাগুলি দেবে, অনুমান নয়।
3. **p21 heading** — KNOWN LIMIT (§৫)। Round 26-র পরীক্ষা: recognition-based grouping ছাড়া আর কোনো পথ নেই (comp filter `ww > 900` reachability wall-সহ) — নতুন signal না পেলে limit বহাল।
4. **Gate-কাজ:** (ক) guard-এ text-vs-rule test (fuzzy ট্র্যাকের rule-shredding, §৬); (খ) Hoover/OAM over-split eye T3 v3-র জন্য (online lead); (গ) modal-stroke-width ligature detector (US 5,384,864 — gate-এর fused-CC detection-এর দ্বিতীয় witness)।
5. **Knife-edge-গুলো:** F=1.70, FIX3 3px run floor (n=1), floor-4 (genuine-min 77px, window [2,77]) — principled নিয়মে বদলানো যায়নি, মাপা আছে। T4-র 0.60 threshold মাপা empty interval-এর মাঝখানে — knife-edge নয়, কিন্তু ±1px placement tolerance নথিভুক্ত আছে (§৬)।
6. **আগের মতো খোলা:** Virtako label ৫-field decision (user-এর উত্তর অপেক্ষায় — শীঘ্রই আবার জিজ্ঞেস করবে না); Q-03–Q-09, ★2–★8; print calibration (factory printer — শুধু user, Muse-র কাজ শেষে); US patent legal check (lawyer — lead: US 5,734,761 + Adobe US9741142B2 + US 20250111688 + US 20250078557); Windows .exe (Windows-এ build করতে হবে); .docx capture 100/100 (৯৬.৬০% এখন); first-view ~১৪–১৮s।

---

## ১১. যাচাই (verification — parent-এর জন্য)

- **Merge:** `merge-r25/segment_merged.py` + `gate_merged.py` + `rhythm_dp.py` + `logo_detect.py` + `gate_misses.py` + `segs/` (৩৩ পাতা) + `gate_batch_r25_merged.json` + `canon_r25_merged.json` + `merge_segment_r25.py` + `run_segs_r25.py` + `run_gate_r25.py`। Segmenter + ৩টি support ফাইল R24-র সঙ্গে **SHA-256 byte-identical** (segment `86541e29af96`); gate diff ০ deletion / ১৬০ addition (T4 only)।
- **Gate:** 23/2 (২৫ পাতা); ৩১ ALLOW / ২ REFUSE (৩৩ entry)। REFUSE: p20 (T3 Path C, box `[557,661,986,678]`, min_cc_w_med 8.36, fus_cover 0.993) আর p21 (T3 Path B, box `[827,1970,1317,2005]`)। T1 ০, T2 ০, **T4 ০**। ২৩টি ALLOW পাতার প্রতিটি R24-র সঙ্গে SAME।
- **T4 false-case যাচাই (merge করা gate দিয়ে, নিজে চালানো):** bridge segs-এ p20 REFUSE via T4 (৫ white cut), set 23/2; seam segs-এ p20 REFUSE via T4 (৭ white cut), set 23/2।
- **শব্দ:** ২৫ পাতা 9373 (=), ৩৩ পাতা 12366 (=); p2 ৬৭৬, p3 ৪৭১; p20 ৫২১ (=), p21 ৫৮৪ (=); PG aug 306/308/305, may 308/313/306 (=)। **৩৩/৩৩ seg byte-identical** (R24 segs-এর সঙ্গে diff খালি)।
- **Canonical:** N5 **41/81** (=), Description ভুল **৩০** (একই list), redbox **7/66** (=), p3 strict **248/384**, improved **285/384**, FP 186, p21 GT **36/42** @ ±5px meet-rule (segs byte-identical বলে অপরিবর্তিত), LINES **327/327**।
- **Guard:** **5/5 PASS** (segs byte-identical বলে R24-র ফল অপরিবর্তিত)।
- **DB SHA:** `1c065457bb9cb8e5b276d5007d9b020c18c8a0ae0374b92eb759f12150746939` — আগে ও শেষে একই (DB ছোঁয়া হয়নি)।
- **Fitz render:** Aug p1 **৩০৮ শব্দ**, email ২ শব্দ `[970,417,1080,450]` + `[1122,418,1272,450]`; ১৪টি PG পাতা fitz-এ segment করা হয়েছে (aug 308/308/305/307/303/303/311/309, may 307/313/305/306/305/309 — সব SAME)। PNG 306 / fitz 308 — দুই render-পথেই সঠিক।
- **Full suite (repo clone `~/workspace/lse-r25-test/`, lse-r24-test-এর কপি + T4 port + ২ নতুন test):** **40/40 PASS (402.29s, exit 0, 3 warnings)**। Demo **৮২ শব্দ** (নিজে চালিয়ে যাচাই)।
- **Push করা হয়নি, Drive-এ upload করা হয়নি, MEMORY.md ছোঁয়া হয়নি** — parent যাচাই করে push/upload/memory করবে। **Push সিদ্ধান্ত parent-এর:** R25-এ segmenter-এ কোনো নতুন code নেই, শুধু gate T4 — push করা হবে কিনা (সৎ চোখ + ২ নতুন test-এর জন্য), নাকি Round 26 পর্যন্ত রাখা হবে — সেটা reversible working decision হিসেবে parent-এর হাতে।

---

## ১২. উদ্ভাবন বনাম মেরামত (purpose check — ব্যবহারকারীর নির্দেশ)

এই রাউন্ডের **উদ্ভাবন:** (ক) **T4 over-split eye** — gate-এর blind spot বন্ধ করা নতুন চোখ, যেটা split-কে বিচার করে ছবিকে নয় (সঠিক split-কে ALLOW দেয়, ভুল split-কে REFUSE); (খ) **চারটি স্বাধীন প্রমাণ** — Omron M-র premise মাপায় ভাঙা, skeleton-graph-এর column overlap ০.০০০ (dead signal), tree-র width variation সত্যকে ১৭.৫× হারানো, fuzzy vote-এর ১৮/১৮ উল্টো — প্রতিটি নতুন জ্ঞান, যা ছাড়া Round 26 অন্ধভাবে একই পরীক্ষা আবার করত; (গ) online research-এর নতুন lead-গুলি (feature-point contact detection, τ-signal, drop-fall) — প্রতিটি সুনির্দিষ্ট পরীক্ষাসহ। **মেরামত:** কিছুই না — কোনো regression ঠিক করতে হয়নি, কোনো segmenter বদল হয়নি। সৎ মূল্যায়ন: এই রাউন্ড gate-কে আরও সৎ করেছে আর সীমার প্রমাণে পূর্ণ — আর সীমা না জানলে 100%-র পথে হাঁটা যায় না। সবচেয়ে বড় শিক্ষা (R24-র সঙ্গে একমত): **gate-এর সংখ্যা সত্য নয় — word identity-ই সত্য** — আর এখন gate-ও সেটা জানে (T4)।
