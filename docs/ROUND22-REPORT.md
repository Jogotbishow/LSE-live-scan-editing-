# LSE Round 22 — রিপোর্ট

**তারিখ:** 2026-11-09 · **ভাষা:** বাংলা · **মার্জ এজেন্ট:** Round 22 coordinator
**Baseline:** Round 21 merged segmenter + gate (`round21/merge-r21/`, gate 24/1) — read-only, ভাঙা হয়নি
**নতুন baseline:** `improve/round22/merge-r22/` (segment_merged.py + gate_merged.py + rhythm_dp.py + logo_detect.py + gate_misses.py + segs/)
**ডিরেক্টরি:** `improve/round22/` — প্রতি ট্র্যাকের নিজের ডিরেক্টরিতে তার সব আউটপুট; merge `merge-r22/`-তে
**নির্দেশ:** ব্যবহারকারীর LSE 100% নিয়ম (2026-11-08 22:42) — Muse নিজে 100% সন্তুষ্ট না হওয়া পর্যন্ত LSE-র কাজ থামবে না; কোনো অনুমতি লাগবে না। এই রাউন্ড সেই নির্দেশেই চলেছে।

> **সৎ সারাংশ:** Gate 24/1 → **24/1** — 25/0 হয়নি। p20-র ৮টি whole-line collapse ঠিক হয়েছে (p20 ALLOW), কিন্তু উন্নত T3 চোখ এখন p21-র ১টি আসল collapse দেখে (7 শব্দ এক box-এ — "three months before the date of expiry")। তাই REFUSE এখন p20 থেকে p21-এ সরে গেছে। শব্দ +259 (9101 → 9360), coverage 62/97 → 92/97, T3 recall 73% → 97%। কিন্তু সত্যিটা এটাও: 25/0-র জন্য p21-র ওই ১টি stretch geometry-only উপায়ে ঠিক করা **সম্ভব হয়নি** (§৭) — প্রমাণসহ। আর merge-এর পরে ধরা পড়েছে FIX C-র একটি আসল regression — PG পাতায় box বাড়িয়ে IoU ভেঙেছিল, suite 35/38 হয়েছিল; height floor দিয়ে সেটা ঠিক করা হয়েছে (§৫)। এই রিপোর্টে দুটোই সৎভাবে বলা হয়েছে।

---

## ০. এক নজরে — headline সংখ্যা

| মাপ | R21 baseline | **Round 22 merge** |
|---|---:|---:|
| Gate (২৫ Raviraj পাতা) | 24 ALLOW / 1 REFUSE | **24 ALLOW / 1 REFUSE** |
| ফ্ল্যাগ (T1 / T2 / T3) | 0 (0 / 0 / 8) | **1 (0 / 0 / 1)** |
| মোট শব্দ (২৫ পাতা) | 9101 | **9360 (+259)** |
| মোট শব্দ (৩৩ পাতা) | 12068 | **12353 (+285)** |
| REFUSE পাতা | শুধু p20 | **শুধু p21** |
| Canonical p2 N5 / Description / redbox | 40/81, 39/69, 7/66 | **41/81 (+1), 39/69 (=), 7/66 (=)** |
| Canonical p3 strict / improved (FP) | 248 / 285 (186) | **248 (=) / 285 (=) (186, =)** |
| Canonical p2 / p3 gate | p2 REFUSE (T2=2, by design), p3 ALLOW | p2 ALLOW (T2=0), p3 ALLOW |
| LINES (canonical r15m) | 327/327 | **327/327 (=)** |
| PG ৬ পাতা (শব্দ) | aug 306/308/305, may 308/313/306 | **aug 306/308/305, may 308/313/306 — হুবহু একই (0 removed / 0 added)** |
| p21 GT (৪২ certain boundary) | 35/42 | **35/42 (=)** |
| Guard (live page, FULL) | 5/5 | **5/5 PASS** |
| Round 3 DB SHA | `1c065457…` | **`1c065457…` — আগে ও শেষে একই** |
| Full suite (repo test clone) | 38/38 | **38/38 PASS (402.240s, 0 fail)** |
| Demo (synthetic) | 82 শব্দ | **82 শব্দ (=)** |
| Aug p1 শব্দ-সংখ্যা | PNG 306 / fitz 308 | **PNG 306 / fitz 308 — দুই render-পথেই সঠিক** |

**ফ্লিপ (REFUSE→ALLOW):** p20 (light-print fix + FIX3) — ১টি পাতা।
**ফ্লিপ (ALLOW→REFUSE):** p21 (উন্নত T3 চোখ — ১টি আসল 7-শব্দ collapse, R21-র চোখ দেখতো না)।
২৩টি পুরনো ALLOW পাতার একটিও regress হয়নি। **বাকি ১টি REFUSE:** p21 — T3 ১টি collapse (§৭ দেখুন)।
**নোট — floor-ছাড়া merge-এর সংখ্যা:** FIX C rev.2 height floor বসানোর আগে merge ছিল N5 42/81, p3 249/286 (FP 185)। floor-এ ১টি করে শব্দ কমেছে (N5 42→41, p3 249→248) — কিন্তু দুটোই R21 baseline-র **সমান বা ভালো** (40/81, 248/285)। floor ছাড়া suite 35/38 হতো (§৫) — তাই floor নেওয়া হয়েছে।

**Promotion bar-এর রায়: পাস — তবে 25/0 নয়।** p20 ঠিক হয়েছে, শব্দ +259, coverage 92/97, T3 recall 97%, canonical R21-র চেয়ে ভালো (N5 +1, p3 =), suite 38/38। কিন্তু p21-র ১টি stretch geometry-only উপায়ে ঠিক করা যায়নি — প্রমাণসহ (§৭)। T3-কে warn-only করে 25/0 দেখানো হতো **অসততা**। Gate এখন আরও কঠোর ও সৎ: R21-তে অদৃশ্য collapse এখন ধরা পড়ে। p21-র stretch ঠিক করা Round 23-র কাজ (§৮)।

---

## ১. ট্র্যাক verdicts — ৫টি ট্র্যাক, সব DONE

| ট্র্যাক | verdict | মূল ফল |
|---|---|---|
| **track-p20** | **PROMOTE** | p20-র ৮ collapse-র কারণ: (১) main grouping threshold `max(8, 0.30×med_h)` = 8px, কিন্তু word gap ৫–৮px; (২) হালকা ছাপা (ink median grey ~190–204) — dark threshold 141-এ **শূন্যটি** dark sub, তাই `split_blob_words` early-return করে, v3 split চলেই না। Fix: নতুন `_split_light_print(bbox)` — box-র নিজের Otsu comps re-group, uniform-spacing guard, cut ≥ `max(5, 0.30×med_h)`, F5 merge + `_split_from_subs` validation; dark subs খালি হলেই চলে (rhythm DP নয়)। p20 365 → **505 (+140)**, ৪২/৪৫ সত্য boundary, ১টি ভুল cut, ৩টি miss; gate **25/0 (পুরনো R21 চোখে)**; N5 40→41/81; suite 38/38। |
| **track-misses** | **PROMOTE B–E (FIX A বাদ)** | coverage probe **62/97 → 92/97**; শব্দ +99 (৩৩ পাতা 12068→12167, ২৫ পাতা 9101→9187); canonical N5 41/81, p3 249/286; canonical p2 gate REFUSE (T2=2) → **ALLOW (T2=0)** — CY/BH উদ্ধার; p21 GT 35/42 (=); PG সংখ্যা হুবহু একই। FIX B = 2D footer pass; FIX C = comp-coverage (৪৬৫ comp-reclaim, সব extend, ০ orphan); FIX E = line-graph helpers + F3 loop; FIX D = frag-rescue (p2 "BH")। **FIX A নেওয়া হয়নি** — p21 heading (underlined, ৯৯৩×৩৭, fill 0.65) প্রমাণিতভাবে unfixable (§৪)। Orphan path মৃত প্রমাণিত, সরানো হয়েছে (৪৬৫ reclaim-এ ০ orphan; ছাড়া re-run: ৩৩/৩৩ পাতা byte-identical)। |
| **track-t3** | **PROMOTE** | উন্নত T3 চোখ: Path A′ (1px-margin repair) + Path B (inside split, F=1.70) + tight-joiner guard। **Recall 34/35 (97%)** — task-এর 11-set-এ **11/11** (R21 ছিল ৮/১১)। একমাত্র miss: p20 `[557,661,986,678]` (maxgap 2px, পুরো লাইন fused — কোনো gap signal ধরতে পারে না; segmenter-কে ঠিক করতে হবে)। **False positive ০** (১৬টি eye-verified genuine control + সব ৩৩ পাতা; ২৬টি নতুন flag, সব eye-verified collapse)। Guard ঠিক ৭টি genuine joined-token box ব্লক করে (phone ১ + email ২ + URL ৪), ০টি collapse ব্লক করে না। p20 T3 ৮ → ২৯; p01 ০→৩, p21 ০→১, p2 ০→১। R21 segmenter-এ gate **22/3** (p01, p20, p21 REFUSE) — ৩টি আসল collapse যা R21 চোখ দেখতো না; লুকিয়ে 24/1 রাখা হতো অসততা। |
| **track-online** | গবেষণা (কোড নয়) | RESEARCH22.md (২৮টি source): (১) per-line bimodal gap k-means (US 2014/0270526) — **USEFUL** (প্রতিটি লাইনের নিজের data থেকে threshold; T3-র 1px margin-এর সরাসরি উত্তর); (২) segmentation-copy line/underline removal (US 9,275,030; Kraken `no_hlines`) — **USEFUL** (p20 bridge সরানো; segmentation-copy-তেই, আসল background কখনো নয়); (৩) vertical-projection valley cut (US5809166A, US5040229A) — **USEFUL** (x-height band-এ valley + bridge-row exclusion + CC recount)। সৎ negative finding: 2024–2026-এ geometry-only word segmentation-এ কোনো breakthrough নেই — field neural line/VLM-এ চলে গেছে; classical সেরা Wang et al. ICPR 2000 (97.43%)। Donut/Nougat, Surya 2.5, DocLayout-YOLO — প্রযোজ্য নয়। |
| **track-fix3** | **PROMOTE partial (৩-এর মধ্যে ২)** | Merge-এর পরে বাকি ৩টি collapse-র জন্য: **p01 ঠিক** ("today @ Rs." → ৩টি box); **p20 target ঠিক** ("DHAKA MAIN BRANCH" → ৩টি box) + আরও ৭টি light-print box ঠিক; **p21 ঠিক হয়নি** ("three months before the date of expiry" এখনও ১টি box)। gate 24/1 (শুধু p21), শব্দ +15, canonical অপরিবর্তিত। রাখা fix-গুলো সব `_split_light_print`-র ভিতরে: scale-aware guard, combined cut rule (CC gap ≥ `max(5, 0.30×med_h)` AND Otsu column run ≥ 3px), @-isolation (holes ≥ 4)। profile re-split **মুছে ফেলা হয়েছে** — p21 ঠিক করলেও (৬/৭ শব্দ) ৬টি box over-split করেছিল (§৭)। |

---

## ২. merge — কীভাবে চারটি fix এক করা হলো

**নেওয়া হয়েছে:** p20 light-print + misses FIX B/C/D/E + T3 উন্নত চোখ + FIX3 (light-print v2) + FIX C rev.2 height floor (§৫)।
**নেওয়া হয়নি:** misses FIX A (§৪), `_profile_resplit` (§৭)।

মার্জ-প্রক্রিয়া (পুনরুৎপাদনযোগ্য — স্ক্রিপ্ট `improve/round22/`-তে রাখা আছে):
- `merge_segment.py` — exact-string replacement-এ track-ফাইল থেকে `merge-r22/segment_merged.py`-তে বসায়, প্রতিটি anchor ঠিক ১ বার মিলিয়ে যাচাই করে। Base = track-misses `segment_r22.py` (R21 + FIX B/C/D/E), তার উপর track-p20-র ৪টি বদল (`_split_light_print` ১২৮ লাইন, early-return, keep-list, method note)। **Keep-list conflict composition-এ মিটেছে:** p20 keep-list লাইন আর misses kept/suppressed restructuring একই জায়গা ছোঁয় — merged ফাইলে misses structure নেওয়া হয়েছে, তার kept tuple-এ `"light-split"` যোগ করা হয়েছে (light-split piece filter হওয়ার একমাত্র জায়গা)। Diff প্রমাণ: R21-র সঙ্গে = ৯টি hunk (misses B + p20 light-print + misses C/E/D); misses-এর সঙ্গে = শুধু ৪টি p20 hunk; p20-র সঙ্গে = শুধু misses hunk। compile OK।
- FIX3 merge: `track-fix3/segment_fix3.py` হুবহু `merge-r22/segment_merged.py`-তে কপি (diff identical, compile OK; pre-FIX3 merged-এর সঙ্গে ১১টি hunk)। আর কোনো merge-r22 ফাইল বদলায়নি।
- Gate merge: `track-t3/gate_t3.py` হুবহু `merge-r22/gate_merged.py`-তে কপি (R21-র সঙ্গে diff = শুধু ৫টি T3 hunk); `track-misses/gate_misses.py` হুবহু `merge-r22/gate_misses.py`-তে কপি। compile OK। `check_dp_integrity` আছে, MIN_CORE_ASSIGN_PX=4 আছে।
- R19/R20/R21 fix-গুলো অক্ষত আছে (grep দিয়ে যাচাই): eroded positive-gap median, "@" gap-position rule, eroded-subs extension + fallback, E2 gap-mark, p01 row-split, p12v5 release, floor-4।

**Repo test clone-এ port:** suite চালাতে R22 fix-গুলো repo-র `lse/segment.py`, `lse/gate.py` ও `lse/gate_misses.py`-তেও port করা হয়েছে (`~/workspace/lse-r22-test/`, স্ক্রিপ্ট `port_segment_r22.py` + `port_gate_r22.py`)। Repo-র segmenter nested (`segment_array`-র ভিতরে, 4-space indent) বলে re-indent করে port করা হয়েছে; gate top-level বলে সরাসরি। Port যাচাই: segment ২১টি check + gate ২৪টি check — সব PASS; compile OK। `gate_misses.py` repo-র `lse/`-তে কপি করা হয়েছে (FIX D-র relative import `from .gate_misses import`-এর জন্য দরকার)। rhythm_dp.py ও logo_detect.py merge-r22 আর repo-তে হুবহু একই। Demo-তে port করা segmenter ৮২ শব্দ দেয় (= R21)।

**Port-এ ধরা পড়া ভুল (নিজে ধরা, ঠিক করা):** প্রথম port-এ `_subcov_c`/`_all_subs_accounted`-এর `[:4]` tolerance আর `_split_from_subs`-এর F5 block-এর indent ভুল ছিল (৪-space লেখা, nested-এ ৮-space দরকার) — script assert-এ ধরা পড়ে, লেখার আগেই থেমে গেছে, repo ফাইল অক্ষত ছিল। ঠিক করে re-run করা হয়েছে। শিক্ষা: nested port-এ প্রতিটি anchor-এর indent আলাদা করে যাচাই করো — substring match count ঠিক থাকলেও replacement ভুল হতে পারে।

---

## ৩. p20-র diagnosis — কেন ৮টি লাইন collapse হয়েছিল

p20 (med_h 14, otsu 217, ৩৬৫ শব্দ) — ৮টি T3 box, GT ৫৩ শব্দ / ৪৫ boundary। কী **নয়**: rule/stamp/underline নয় (০টি straddling comp, gap column-এ clean paper mean grey 240–248, কোনো row ink >0.90 নয়)। দুটি কারণ:
1. **Grouping threshold বড়:** main grouping threshold `max(8, 0.30×med_h)` = 8px, কিন্তু p20-র word gap ৫–৮px — threshold word gap-কে ছাড়িয়ে যায়, তাই শব্দগুলো এক box-এ জুড়ে যায়।
2. **হালকা ছাপা:** ink median grey ~190–204 — dark threshold 141-এ ৮টি box-এই **শূন্যটি** dark sub পাওয়া যায়, তাই `split_blob_words` early-return করে `([], 0)` আর v3 split চলেই না। Rhythm DP মেপে বাতিল করা হয়েছে (GT ৩ → DP ৬)।

Fix (`_split_light_print`): box-র নিজের pipeline comps (8-connected Otsu, area≥14) re-group করে; uniform-spacing guard (min_pos > 0.5×max_pos → এক শব্দ); cut ≥ `max(5, 0.30×med_h)`; F5 merge + `_split_from_subs` validation; dark subs খালি হলেই চলে (rhythm DP নয়); keep-list-এ `"light-split"` যোগ করা অপরিহার্য (ছাড়া p20 ৩৬৫→২৮৮-এ পড়ে যায়)। ফল: p20 ৩৬৫ → ৫০৫ (+১৪০), ৪২/৪৫ সত্য boundary, ১টি ভুল cut ("000443918-0101" — "000"-এর পরে কাটা), ৩টি miss (PLC|DHAKA fused, ৩px OPERATIONS|ON, ৪px &|WORKS)। N5 40→41/81 (right-st-reg +২, chg-service-tax −১ — "Service" → ২ টুকরো over-split, ৭px letter gap = 0.35×med_h বনাম সত্য ৫px word gap = 0.36×med_h — gap size দিয়ে আলাদা করা যায় না)।

---

## ৪. misses FIX A — নেওয়া হয়নি (প্রমাণিতভাবে unfixable)

p21 heading blob `[555,1082,1548,1119]` (৯৯৩×৩৭, fill 0.65) **underlined** — baseline-এ solid rule আছে (row-ink 0.84–0.94, y1111–1114)। strip 0.90 শুধু ২টি মাঝের row সরায়। strip 0.80-তেও (rule পুরো সরে, letter row ≤0.61 বনাম rule row ≥0.84, ০.২৩ gap) letter gap (৬–১৪px) আর word gap (১–১১px) overlap করে আর উল্টে যায় ("Periodic" ১৩px letter gap-এ কাটা, "Review" ১৪px-এ, অথচ "of"|"Recommendation" মাত্র ১px word gap-এ জুড়ে যায়)। কোনো gap threshold চলে না (6.0 → ২ over-split + ১ merge; 8.4/10 → ৩ merge); band profile, pitch/rhythm, Rhythm-DP (৬ box) — সব fail। শুধু letter identity আলাদা করতে পারে — recognition, নিষিদ্ধ। Variants: V3a (FIX A as-is) ৪ box, শেষটি ৮১২px mega-box (৫ শব্দ জোড়া — ABCDE6-র ৯-এর চেয়ে খারাপ, কারণ R21 E2 ABCDE6-র eroded split বাতিল করে); V3b (strip 0.80) ৯ box, ২ over-split + ১ merge; V4 (F5 0.7→1.0) "Periodic" সারায় কিন্তু p21-র অন্যত্র ৮টি আসল শব্দ জুড়ে দেয় — বাতিল। Gate এই ক্ষতি দেখতে পায় না (সব variant-এ 24/1; T3-র ১–২ শব্দ/লাইন দরকার, heading লাইনে ৪–৯ box) — বাতিলের কারণ word-identity inspection, gate নয়।

**FIX B–E নেওয়া হয়েছে:** coverage 62/97 → **92/97** (ABCDE6 ছিল 93/97 — ১টির পার্থক্য শুধু heading); শব্দ +99; canonical p2 gate REFUSE → ALLOW; p21 GT 35/42 (=)। এখনও missing: p01 CARRIER NAME লাইন ৮ শব্দ (stamp-joined), p21 heading, p21 "gal of Bengal" / "by", p01-র ১০টি FOB/FREIGHT digit (black "USD" থেকে ১২৬px দূরে — ৪০px chain gap-র বাইরে), p21 address লাইন ২৬ শব্দের ink ১৪ box-এ, p10 "Prepared" (দুটি box; ১৯px খালি gap শব্দের ভিতরে বনাম "ared"|"By"-র মাঝে ৩–৪px — lexicon ছাড়া জোড়া যায় না)।

---

## ৫. FIX C rev.2 — merge-এর পরে ধরা পড়া PG regression (সবচেয়ে বড় শিক্ষা)

**সমস্যা:** প্রথম merge-এ (floor ছাড়া) repo suite **35/38 FAIL** হয় — Aug p1 m=281 (<285), May p1 m=285 (<290), Aug p6 m=269 (<271.8)। শব্দ-সংখ্যা ঠিক ছিল (Aug p1 ৩০৮, May p1 ৩০৭), কিন্তু box-গুলো সরে গিয়েছিল।

**Diagnosis (দুই ধাপে প্রমাণিত):**
1. **Port নির্দোষ:** merged segmenter-ও একই m দেয় (Aug p1 ২৮১, May p1 ২৮৫), আর merged বনাম repo box set **byte-identical** (০টি box পার্থক্য)। Regression merge-এই (Round 22 বদলে), port-এ নয়।
2. **দোষী FIX C:** R21 বনাম R22 diff-এ Aug p1-এ ১৩টি, May p1-এ ১৩টি, Aug p6-এ ১০টি box বদলেছে — **সবই FIX C extension** (৯–১৯px একদিকে বাড়ানো)। R21 box-গুলোর ref-IoU ছিল 0.92–1.00; R22-র 0.72–0.89 (0.9 threshold-এর নিচে)। ৮টি (Aug p1), ৯টি (May p1) ref box match হারিয়েছে।

**Eye-verified প্রমাণ:** Aug p1-র box `(982,357,1084,384)` ("02937") → R22 `(982,357,1098,384)` — claimed comp `[1087,374,1098,379]` (১১×৫px)। Crop ছবিতে দেখা গেছে এটা **"02937" আর "2871"-র মাঝের hyphen** — আলাদা token, কোনো শব্দের অংশ নয়। FIX C ভুল করে hyphen-কে বাম শব্দের সঙ্গে জুড়ে box বাড়িয়েছে। R21/reference box-ই সঠিক ছিল।

**Fix — FIX C rev.2 height floor:** FIX C শুধু letter-sized comp claim করবে — `h >= 0.5 × med_h`। যুক্তি (fitted নয়, principled): median character height-এর অর্ধেকের ছোট comp letter হতে পারে না; FIX C-র কাজ missed word part উদ্ধার করা (letter-sized), gap mark গিলে ফেলা নয়। মাপা তথ্য: PG-তে FIX C-র claimed সব comp h≤0.38×med_h; debug feature table-এ Raviraj-র tall rescue (৭×২৬, ১৩×২৬, h_med 1.30) আর PG hyphen (১১×৫, h_med 0.19) আলাদা। **কিন্তু সৎ সীমা:** কোনো height threshold দুটোকে পুরো আলাদা করতে পারে না — Raviraj ৯px comp রাখে (h_med 0.45, desc-L08), PG-তে ১০px comp আছে (h_med 0.38) — তাই fitted 0.34 floor না নিয়ে principled half-height boundary নেওয়া হয়েছে। **মূল্য:** N5 42→41 (desc-L08), p3 249→248 — দুটোই R21 baseline-র সমান বা ভালো (40/81, 248/285)। **ফল:** PG m ফিরেছে (Aug p1 ২৮৮, May p1 ২৯৪, Aug p6 ২৭৬ — সব PASS), suite **38/38**। Raviraj gate 24/1 আর শব্দ ৯৩৬০ অপরিবর্তিত।

---

## ৬. T3 চোখ — 73% → 97% recall, ০ false positive

Path A (R21) ৮/১১ ধরতো। নতুন দুটি leg (৩৩ পাতা / ১০৮ wide box-এ মেপে নেওয়া):
- **Path A′ (1px-margin repair):** (a)+(b)+maxgap==5+maxgap ≥ ৩× লাইনের median letter gap — p01-র `[626,746,819,764]` "AHMEDABAD 382110" ধরে (maxgap ৫px, 1px margin, ruler 1.0px, ৫.০×)।
- **Path B (inside split):** box-র CC-গুলো thr = max(5, 1.70×trim_med)-এ split করে; trim_med = ২টি বৃহত্তম gap বাদে median; ≥২ word-like group → flag; hyphen-পাশের gap কখনো split নয়। F window মাপা (5/3, 7/4] = (1.667, 1.75] — F=1.70 ভিতরে, margin-সহ; R19-র 0.92-র মতো সৎ knife-edge, principle থেকে আসেনি।
- **Tight-joiner guard (শুধু Path B):** hyphen-like (h < 0.55×med_h, w ≥ 1.5×h, w ≥ 0.4×med_h, vertically centred |Δy| ≤ 0.25×med_h), slash-like (h ≥ 0.8×med_h, w ≤ 0.5×med_h, fill ≤ 0.30), at-like (h ≥ 1.5×med_h, 1.5×med_h ≤ w ≤ 2.5×med_h, ১–২ enclosed hole)। Guard ঠিক ৭টি genuine joined-token box ব্লক করে, ০টি collapse ব্লক করে না।
- বাতিল signal: inter-word-gap ruler (মৃত), hyphen-containment guard (২টি আসল collapse মেরে ফেলে), CLIFF একা (সর্বোচ্চ ২১/২৯)।
- **সংশোধন:** R21-র "১১" অসম্পূর্ণ ছিল — সত্য p20 recall ছিল ৮/৩০, ৮/১১ নয়। পূর্ণ ৩৫-collapse set: R21-ধরা ৮টি + নতুন ২৭টি।

---

## ৭. p21-র stretch — কেন 25/0 হলো না (সৎ উত্তর)

বাকি ১টি T3: p21 `[827,1970,1317,2005]` — "three months before the date of expiry" (৭ শব্দ, ১ box)। FIX3-র profile re-split এটা ঠিক করেছিল (৬/৭ শব্দ) কিন্তু **৬টি box over-split** করেছিল: p01 email "mataplt@matagroup.in" ৬ টুকরো (+৪ reclaim orphan), p09/p12 code "U"/"U1" আলাদা, p2 GSTIN ৩ টুকরো, p22 "DISCHARGEBDBNP" ভুল কাটা, p3 "COMMERCIAL" → "COM"+"MERCIAL"। সত্য word run (৭, ৯, ১০px) আর ভুল letter run (৫, ৬, ৯px) প্রতিটি gap/run মাপে overlap করে; 1.75× multiplier knife-edge fitted threshold হতো — বাতিল। Function মুছে ফেলা হয়েছে (শুধু warning comment আছে)। `of|expiry` boundary কোনো gap মাপে আলাদা করা যায় না (dark 4px, Otsu 0, core 3px বনাম পাশের letter gap 5px); Rhythm DP-ও fail। **১টি সঠিক fix বনাম ৬টি regression — সেটা fix নয়।** p21 stretch তাই ১টি merged box-ই আছে (gate T3 ১)।

**জানা ভুল cut (সৎ):** "58DILKUSHA" → "DILK"+"USHA" over-split — অনিবার্য: ৫px letter gap প্রতিটি মাপে word gap-এর সমান। p05 "CONTINUATION" split হারিয়েছে (baseline-এ ফেরত, খারাপ নয়)।

---

## ৮. সংশোধন (corrections — আগের রিপোর্টের ভুল ঠিক করা)

1. **p12-র "5","0" আসলে আছেই:** R21 report §৭-র "still missing" ভুল ছিল — R20-র সঙ্গে মেপেছিল। R21 baseline-এই exact box আছে (`[2131,2338,2147,2362]` আর `[1295,3228,1313,3262]`, R21 p12v5-র উদ্ধার)।
2. **T3 recall:** R21-র "৮/১১ (73%)" অসম্পূর্ণ ছিল — সত্য ছিল ৮/৩০। Round 22-তে পূর্ণ set ৩৫টি, recall ৩৪/৩৫ (97%)।
3. **PG "identical counts" ≠ identical boxes:** coordinator-এর merge যাচাই শুধু শব্দ-সংখ্যা মিলিয়েছিল (aug 306/308/305, may 308/313/306) — box shift ধরা পড়েনি। IoU যাচাই (§৫) ছাড়া "PG identical" দাবি করা যাবে না — এই শিক্ষা Round 23-এ যাবে।
4. **p10 "Prepared" এখনও ঠিক হয়নি:** দুটি box (`[491,2551,576,2580]` + `[592,2552,751,2589]`); শব্দের ভিতরে ১৯px খালি gap বনাম "ared"|"By"-র মাঝে ৩–৪px — lexicon ছাড়া জোড়া যায় না, geometry-only unfixable।

---

## ৯. খোলা বিষয় (open items — Round 23-র জন্য)

1. **p21-র ৭-শব্দ stretch** ("three months before the date of expiry") — একমাত্র REFUSE। নতুন discriminator দরকার (online research-এর per-line bimodal k-means / valley cut — §১ RESEARCH22.md-র ৭টি "Round 22 should try" item, guardrail-সহ) অথবা known limit হিসেবে সৎ স্বীকার।
2. **p21 heading** (৮ শব্দ, underlined bold, FIX A unfixable — §৪)।
3. **৮১ hidden miss-এর বাকি:** coverage 92/97 — এখনও missing p01 CARRIER NAME লাইন, p21 "gal of Bengal" / "by", p01 FOB/FREIGHT digit, p21 address লাইন, p10 "Prepared" (§৪)।
4. **T3 recall 34/35 (97%):** একমাত্র miss p20 `[557,661,986,678]` (maxgap 2px, পুরো fused লাইন — কোনো gap signal ধরতে পারে না; segmenter-কে ঠিক করতে হবে)।
5. **Knife-edge-গুলো:** F=1.70 (window (1.667, 1.75]); FIX3 3px run floor margin মাত্র ১px (BENAPOLE run ২ বনাম floor ৩); E2 width boundary (~1px — p21 fragment 0.536×med_h বনাম cutoff 0.50); floor-4 evidence n=1।
6. **আগের মতো খোলা:** Virtako label ৫-field decision (user-এর উত্তর অপেক্ষায় — শীঘ্রই আবার জিজ্ঞেস করবে না); Q-03–Q-09, ★2–★8; print calibration (factory printer — শুধু user, Muse-র কাজ শেষে); US patent legal check (lawyer — lead: US 5,734,761 + Adobe US9741142B2 + US 20250111688 + US 20250078557); Windows .exe (Windows-এ build করতে হবে); .docx capture 100/100 (৯৬.৬০% এখন); first-view ~১৪–১৮s।

---

## ১০. যাচাই (verification — parent-এর জন্য)

- **Merge:** `merge-r22/segment_merged.py` + `gate_merged.py` + `rhythm_dp.py` + `logo_detect.py` + `gate_misses.py` + `segs/` (৩৩ পাতা) + `gate_batch_r22_merged.json` + `canon_r22_merged.json`। `segs-r22-nofloor/` — floor-ছাড়া merge-এর segs (রেকর্ডের জন্য রাখা)।
- **Gate:** 24/1 (শুধু p21 REFUSE, T3 ১, Path B, box `[827,1970,1317,2005]`); ৩২ ALLOW / ১ REFUSE (৩৩ entry)। T1 ০, T2 ০।
- **শব্দ:** ২৫ পাতা ৯৩৬০ (p01 ৬০৮→৬৬২ +৫৪, p07 +২, p09 +৩, p12 +৪, p13/14/15 +৪ করে, p20 ৩৬৫→৫২১ +১৫৬, p21 ৫৬৩→৫৮৪ +২১, p22 ৬৬২→৬৬৯ +৭); ৩৩ পাতা ১২৩৫৩; p2 ৬৭৬, p3 ৪৭১।
- **Canonical:** N5 **41/81** (desc-L08 ২/৪, right-st-reg ৩/৫, chg-service-tax ১/৪), Description wrong **৩০** (একই list), redbox **7/66** (L8), p3 strict **248/384**, improved **285/384**, FP 186, p21 GT **35/42** (floor-এ p21-র GT লাইনে box-সংখ্যা অপরিবর্তিত — L1648 ২১, L1926 ১৭, L2379 ২০, no-floor-এর হুবহু একই), LINES **327/327** (rescore_lines_r15m.py দিয়ে যাচাই)।
- **DB SHA:** `1c065457bb9cb8e5b276d5007d9b020c18c8a0ae0374b92eb759f12150746939` — আগে ও শেষে একই (DB ছোঁয়া হয়নি)।
- **Full suite (repo clone `~/workspace/lse-r22-test/`):** **38/38 PASS** (402.240s, exit 0)। Aug p1 IoU-matched ২৮৮/৩০২ (≥২৮৫), May p1 ২৯৪/৩০২ (≥২৯০), Aug p6 ২৭৬ (≥২৭১.৮)। Demo ৮২ শব্দ। Aug p1 PNG ৩০৬ / fitz ৩০৮।
- **Port:** `port_segment_r22.py` + `port_gate_r22.py` — segment ২১টি check + gate ২৪টি check, সব PASS; compile OK। Repo segmenter merged segmenter-এর সঙ্গে PG পাতায় box-identical (diag দিয়ে যাচাই)।
- **Push করা হয়নি, Drive-এ upload করা হয়নি, MEMORY.md ছোঁয়া হয়নি** — parent যাচাই করে push/upload/memory করবে।

---

## ১১. উদ্ভাবন বনাম মেরামত (purpose check — ব্যবহারকারীর নির্দেশ)

এই রাউন্ডের **উদ্ভাবন:** LSE-র light-print split (`_split_light_print` — dark ink না থাকলে Otsu comps re-group করে শব্দ বের করা, OCR ছাড়া), T3-র Path B inside-split (box-র ভিতরের CC gap দিয়ে collapse ধরা), FIX C rev.2 height floor (letter-sized comp-ই word part — principled boundary)। **মেরামত:** FIX C-র PG regression ঠিক করা, port indent ভুল ঠিক করা, p21 stretch-এ profile re-split মুছে ফেলা। সৎ মূল্যায়ন: p20 fix আর T3 চোখ আসল নতুন technology; FIX C floor আর port fix মেরামত — কিন্তু মেরামতটাও প্রমাণ-ভিত্তিক (eye-verified hyphen crop, IoU মাপ)।
