# LSE Round 26 — রিপোর্ট

**তারিখ:** 2026-11-09 · **ভাষা:** বাংলা · **মার্জ এজেন্ট:** Round 26 merge agent (coordinator শেষ করেছিল — merge ছাড়া, final answer ছাড়া; merge এই এজেন্ট করেছে)
**Baseline:** Round 25 merged segmenter + gate (`round25/merge-r25/`, gate 23/2) — read-only, ভাঙা হয়নি
**নতুন baseline:** `improve/round26/merge-r26/` (segment_merged.py + gate_merged.py + rhythm_dp.py + logo_detect.py + gate_misses.py + segs/)
**ডিরেক্টরি:** `improve/round26/` — প্রতি ট্র্যাকের নিজের ডিরেক্টরিতে তার সব আউটপুট; merge `merge-r26/`-তে
**নির্দেশ:** ব্যবহারকারীর LSE 100% নিয়ম (2026-11-08 22:42) — Muse নিজে 100% সন্তুষ্ট না হওয়া পর্যন্ত LSE-র কাজ থামবে না; কোনো অনুমতি লাগবে না। এই রাউন্ড সেই নির্দেশেই চলেছে।

> **সৎ সারাংশ:** Gate 23/2 → **24/1** — ২৫/০ হয়নি, কিন্তু এই রাউন্ডে **প্রথমবারের মতো একটি প্রমাণিত known limit ভেঙেছে**: p21-র ৭-শব্দ stretch (R23–R25 তিন রাউন্ড ধরে "geometry-only known limit") τ-signal-এ **৭/৭ শব্দ** word identity-তে উদ্ধার হয়েছে, আর ALLOW-টা সত্য — T4 চোখ চুপ (false pass নয়)। ৯টি ট্র্যাকের মধ্যে **দুটি PROMOTE — τ-signal segmenter-এ, আর gate T5 rule-shred eye** (R25-র fuzzy ট্র্যাকের খুঁজে পাওয়া guard-দুর্বলতা বন্ধ হয়েছে)। p20-র fused লাইন এখনও REFUSE — আরও **চারটি** স্বাধীন পদ্ধতি (JP2000322514A, drop-fall, watershed, DTW) 0/4-এ ব্যর্থ, τ-ও সেখানে উল্টো (inverted)। p21 heading এখনও known limit (reachability wall)। **সৎ প্রশ্নের উত্তর (§১০): geometry-only উপায়ে 25/0 এখনও সম্ভব নয় — p20-র লাইনে ১২টি স্বাধীন পদ্ধতি ব্যর্থ, একটিও separating signal পায়নি।** তবে ইঞ্জিন যা পারে তা মাপা: gate 24/1 (শুধু p20 REFUSE, প্রমাণিত known limit), full suite **43/43**, T3 recall 100%, T4+T5 চোখ, coverage 95/97, canonical হুবহু একই, demo ৮২, DB SHA অপরিবর্তিত। **একটি সৎ সংশোধন (§৯): Guard আসলে 5/5 PASS নয় — re-run-এ 0/5 FAIL (live page-গুলি stale, R25-র segs-এও fail করে; R24/R25-র "5/5 PASS" re-run ছাড়াই বয়ে আনা হয়েছিল)।** এটা segmenter regression নয়, live-page staleness — কিন্তু রিপোর্টে সত্যটাই লেখা হলো।

---

## ০. এক নজরে — headline সংখ্যা

| মাপ | R25 baseline | **Round 26 merge** |
|---|---:|---:|
| Gate (২৫ Raviraj পাতা) | 23 ALLOW / 2 REFUSE | **24 ALLOW / 1 REFUSE** |
| ফ্ল্যাগ (T1 / T2 / T3 / T4 / T5) | 2 (0 / 0 / 2 / 0 / —) | **1 (0 / 0 / 1 / 0 / 0) — T5 নতুন, baseline-এ ০** |
| মোট শব্দ (২৫ পাতা) | 9373 | **9379 (+6 — শুধু p21: 584 → 590)** |
| মোট শব্দ (৩৩ পাতা) | 12366 | **12372 (+6)** |
| REFUSE পাতা | p20 + p21 | **শুধু p20 (T3 Path C, box `[557,661,986,678]`)** |
| Canonical p2 N5 / Description ভুল / redbox | 41/81, ভুল ৩০, 7/66 | **41/81 (=), ভুল ৩০ (=, একই list), 7/66 (=)** |
| Canonical p3 strict / improved (FP) | 248 / 285 (186) | **248 (=) / 285 (=) (186, =)** |
| Canonical p2 / p3 gate | p2 ALLOW, p3 ALLOW | **p2 ALLOW, p3 ALLOW (=)** |
| LINES (canonical r15m) | 327/327 | **327/327 (=)** |
| PG ৬ পাতা (শব্দ) | aug 306/308/305, may 308/313/306 | **aug 306/308/305, may 308/313/306 — হুবহু একই** |
| Fitz render (১৪ PG পাতা) | aug 308/308/305/307/303/303/311/309, may 307/313/305/306/305/309 | **সব ১৪ পাতা SAME (0/14 differ)** |
| p21 GT (৪২ certain boundary) | 36/42 @ ±5px meet-rule (রিপোর্টের নিয়ম) | **৩৪/৪২ @ ±5px (seam scorer-এ, R25-র ৩৪/৪২-এর সঙ্গে হুবহু একই — regression নয়; §৯ দেখো)** |
| Guard (live page, FULL) | 5/5 PASS (বয়ে আনা) | **0/5 FAIL — re-run-এ ধরা পড়েছে, pre-existing (§৭, §৯)** |
| Round 3 DB SHA | `1c065457…` | **`1c065457…` — আগে ও শেষে একই** |
| Full suite (repo test clone) | 40/40 | **43/43 PASS (429.6s, 0 fail) — ৪০ পুরনো + ২ নতুন T5 test + ১ নতুন p21-stretch test** |
| Demo (synthetic) | 82 শব্দ | **82 শব্দ (=, নিজে চালিয়ে যাচাই)** |
| Aug p1 শব্দ-সংখ্যা | PNG 306 / fitz 308 | **PNG 306 / fitz 308 — দুই render-পথেই সঠিক** |

**ফ্লিপ:** p21 REFUSE → **ALLOW** (τ-split, ৭/৭ শব্দ, T3=0, T4=0, T5=0 — সত্য ALLOW, false pass নয়)। ২৩টি পুরনো ALLOW পাতার একটিও regress হয়নি। **Promotion bar-এর রায়: দুটি PROMOTE — τ-signal (segmenter) + T5 rule-shred eye (gate)।** T3 recall 35/35 (100%) অপরিবর্তিত, coverage 95/97 অপরিবর্তিত, canonical হুবহু একই। এই রাউন্ডের ফসল **তিনটি জিনিস**: (ক) একটি প্রমাণিত known limit ভেঙেছে (p21 stretch) — geometry-only-তে এখনও নতুন signal পাওয়া যায়; (খ) gate-এর আরেকটি hole বন্ধ (T5) — ভবিষ্যতের rule-shredding আর ধরা পড়বে; (গ) **প্রমাণ** — p20-র লাইনে আরও চারটি স্বাধীন পদ্ধতি-পরিবার ব্যর্থ, আর ১২টি ব্যর্থতার প্রতিটির কারণ মাপা আছে — 25/0-র সৎ উত্তর এখন সংখ্যায় দাঁড়িয়ে আছে (§১০)।

---

## ১. ট্র্যাক verdicts — ৯টি ট্র্যাক, ২টি PROMOTE

| ট্র্যাক | verdict | মূল ফল |
|---|---|---|
| **track-tau** | **PROMOTE** | US 20150086113 (τ = cnt_txt × longest_txt, cut at patent local minima with τ < 1, T=1): p21-র ৭-শব্দ stretch `[827,1970,1317,2005]` ("three months before the date of expiry") **৭/৭ শব্দ** word identity-তে (±3px ও ±5px), **৬/৬ সীমানা, ০ false cut**, দুই render-এই। Threshold interval ৩২-চওড়া ([1,32] সবাই ৬/৬ + ০ false) — T=1 fitted নয়, conservative endpoint (শুধু খালি column-এই cut)। Guard (gate-এর নিজের T3 Path B সিদ্ধান্ত): ৩৩ পাতায় ঠিক **১টি** box-এ fire করে (p21) — p20-র ৩ fused CC ১ group দেয় (n_wl=1), তাই τ p20-কে ছোঁয়ই না। Gate 23/2 → **24/1**। p20-তে τ **উল্টো** (সত্য τ 144/196/144 বনাম intra-word সর্বোচ্চ ৭০; সব threshold-এ 0/4)। Unscoped τ(T=1) আসল শব্দ কাটত (৮টি p20/p21 শব্দে ১৪টি, ১২টি p01 শব্দে ৩৬টি, ১২টি Aug-p1-fitz শব্দে ৫১টি ভুল cut) — guard-ই promotable করেছে, signal নয়। |
| **track-gate (a)** | **PROMOTE — T5 rule-shred eye** | Gate diff ৯৯ insertion, **০ deletion**। Rule-like box iff h ≤ 0.50×med_h AND w ≥ 12×med_h AND একটিই Otsu CC ≥ 0.80 width জুড়ে। ৩৩ পাতায় ঠিক **৫টি** box-এ fire করে, **৫টিই rule, ০ text box**। Fuzzy splitter-এর p01/p2 horizontal rule ৫ টুকরো করা ধরে (fuzzy set 24/1 → **22/3**, দুটি নতুন REFUSE-ই আসল)। Baseline-এ T5 = **০ সর্বত্র** (০ false positive)। ২টি নতুন test (T5 constants + T5 rule-shred) suite-এ। |
| **track-jp2000** | **DO NOT PROMOTE** | JP2000322514A (feature-point contact detection, thinned-stroke): **প্রথম পদ্ধতি যা p20-র ৩টি সত্য সীমানাই খুঁজে পায়** — কিন্তু ২৭টি false cut → **0/4 শব্দ**; ৩৫টি control শব্দে ১৯৬টি false candidate; p01/p12/p21/fitz Aug p1-র ৮৪–৯০% box কাটা পড়ত। ব্যর্থতা selection-এ, detection-এ নয়; patent-এর selector character recognition — LSE-তে নিষিদ্ধ। |
| **track-dropfall** | **DO NOT PROMOTE** | Drop-fall family: **0/4 শব্দ**, ৭ faller × ২ threshold × ২ render — সব config-এই। |
| **track-watershed** | **DO NOT PROMOTE** | Watershed: **0/4 শব্দ**, সব ৬৫টি config-এ। |
| **track-dtw** | **DO NOT PROMOTE** | DTW contour-corner pairing: **0/4 শব্দ**, ২/৩ সীমানা, ৩৬টি ভুল cut — p20-র fused লাইনে **৮ম স্বাধীন ব্যর্থতা**। |
| **track-p21stretch** | **DO NOT PROMOTE — ACCEPTED KNOWN LIMIT বহাল (module 14 exact form-এর জন্য)** | EP0780782 module 14 exact form: patent rule-গুলি chance-এ বা তার নিচে (৩৬-এ ১৬–১৯টি ভুল, chance ১৭)। Post-hoc fitted W threshold (৩৬-এ ১/৩৬) artifact — parameter-এ নড়ে, held-out পাতায় ভাঙে। (**নোট:** module 14-র ব্যর্থতা τ-র সাফল্যকে ছোঁয় না — τ আলাদা signal, আলাদা প্রমাণ; §৪ দেখো।) |
| **track-heading** | **DO NOT PROMOTE — KNOWN LIMIT** | Reduced underline-এর সেরা ফল **৫/৮ = control ৫/৮** (নিখুঁত band deletion-এর সমান)। **Reachability wall:** heading blob (৯৯৩px) comp filter `ww > 900`-এ line-grouping-এর আগেই ফেলে দেওয়া হয় — splitter-এর ভেতরে কোনো বদলই তাকে বাঁচাতে পারে না। Variant A 0/8 + ২ regression; Variant B clean zero-regression bypass — কিন্তু DO NOT PROMOTE (recognition-ছাড়া grouping-এর পথ নেই)। |
| **track-gate (b)** | **DO NOT PROMOTE** | Hoover/OAM over-split eye T4b: **১৫৯টি false positive** (pair form), ৩৫টি (≥3-run form) — আসল over-split-কে tolerated joined token থেকে আলাদা করার কোনো geometric leg নেই। Baseline আসলেই over-split করে (p09 SHAHJALAL, p13/14/15 AHMEDABAD — eye-verified, gate ALLOW) — কিন্তু চোখটি তা ধরতে গিয়ে ১৫৯টি ভুল ধরে। |
| **track-gate (c)** | **DO NOT PROMOTE** | Modal-stroke-width ligature detector: সব wide CC-র **৮১.৪%**-এ fire করে (৮৩৯/১০৩১) — p20-র join full-height slash, পাতলা ligature নয়। |
| **track-online** | **গবেষণা (কোড নয়)** | RESEARCH26.md (২৮৪ লাইন): Top lead — **Hong & Hull visual inter-word constraints / sub-image matching** (fused blob-এর বাইরের signal, এখনও পরীক্ষা হয়নি, শর্ত: পাতায় অন্যত্র পরিষ্কার repeat থাকতে হবে — Round 27-র candidate)। JP2000322514A (candidate stage-এই geometry-only); Pal et al. water-reservoir (cavity signal, ink নয়)। **সৎ verdict: 2024–2026-এ geometry-only word segmentation-এ কোনো breakthrough নেই; newest আসল কাজ ২০১৭।** |

**Coordinator-এর interrupted child — যাচাই:** coordinator-এর ৯টি child-এর সবাই runtime-এ "done" — ৯টি TRACK-REPORT.md-ই সম্পূর্ণ, verdict স্পষ্ট, কোনোটি অসম্পূর্ণ বা অস্পষ্ট নয়। (Coordinator নিজে "completed" হয়ে শেষ হয়েছিল final answer ছাড়া — merge আর রিপোর্ট না করে — সেই ফাঁকটাই এই merge এজেন্ট পূরণ করেছে।) কোনো ট্র্যাকের verdict-কে "interrupted" বলে বাতিল করতে হয়নি।

---

## ২. merge — কী নেওয়া হয়েছে, কী নেওয়া হয়নি

**নেওয়া হয়েছে (২টি):**
- **τ-signal (track-tau):** segmenter diff ৩০৫ addition / ৬ deletion (τ block: constants + ১৩টি `_tau_*` function + `_split_fused_tau` + `_tau_resplit_products`; ৩টি return-site wrap + ১টি fallback + "fused-tau" ৩টি src tuple-এ)। Guard-সহ — শুধু gate-T3-Path-B collapse-এই fire করে।
- **T5 rule-shred eye (track-gate (a)):** gate diff **৯৯ insertion / ০ deletion** (purely additive)।

**নেওয়া হয়নি (৭টি):** JP2000322514A, drop-fall, watershed, DTW, module 14 exact form, p21 heading (কোনো variant-ই নয়), gate T4b, gate ligature detector — সবাই মাপা ব্যর্থতা, §১-এ প্রমাণসহ।

**Merge-এ ধরা পড়া সমস্যা (২টি):**
1. **Repo-port trap:** merge-r26/segment_merged.py (improve segmenter) সরাসরি `lse-r26-test/lse/segment.py`-তে copy করা ভুল — repo-port-এর `segment_array` API নেই improve segmenter-এ (ওটা CLI script, module-level globals; repo-port `segment_array`-র ভেতরে nested function, locals)। Copy-টি ধরা পড়েছে import-পরীক্ষায়, সঙ্গে সঙ্গে `lse-r25-push/` (R21–R25 ported, 40/40 verified) থেকে restore করা হয়েছে, আর τ `port_tau_to_repo.py` দিয়ে সঠিকভাবে port করা হয়েছে (২৮৩ লাইন τ block, ৪-space indent-সহ `segment_array`-র ভেতরে; ৩টি call-site wrap + fallback + ৩টি src tuple)। Port-এর প্রমাণ: repo-port p21-তে **590 শব্দ, merge-r26 segs-এর সঙ্গে box-set byte-identical** (removed ০, added ০)।
2. **Guard re-run-এ ধরা পড়েছে (§৭):** R24/R25-র "Guard 5/5 PASS" আসলে re-run ছাড়াই বয়ে আনা হয়েছিল — re-run-এ **0/5 FAIL** (live page stale)। এটা merge-এর আগেই ধরা পড়েছে বলে রিপোর্টে সত্যটা লেখা যাচ্ছে, ভুল "5/5 PASS" বয়ে আনা হয়নি।

**Segmenter byte-identical নয় (সৎ merge):** R24/R25-র মতো byte-identical merge নয় — τ বদলেছে (৩০৫/৬ লাইন)। কিন্তু **৩২/৩৩ পাতা byte-identical** (শুধু p21 বদলেছে, ৫৮৪ → ৫৯০); PG ৬ পাতা byte-identical; fitz ১৪/১৪ identical।

---

## ৩. p20-র fused লাইন — আরও চারটি নতুন ব্যর্থতা, τ-ও উল্টো

Target: `[557,661,986,678]` = "BENEFICIARY/MANUFACTURER/EXPORTER/SHIPPER" (৪ শব্দ, slash-জোড়া), ৩টি CC ১১৭–১৫৮px (8.4–11.3×med_h), gap ১px আর ২px। Gate T3 Path C-তে REFUSE — সঠিক REFUSE (আসল collapse)।

| পদ্ধতি | ফল | ব্যর্থতার কারণ (মাপা) |
|---|---|---|
| JP2000322514A (feature-point) | 0/4 শব্দ, ২৭ false cut | Detection সফল (৩/৩ সত্য সীমানা — প্রথমবার), selection ব্যর্থ: ১৯৬ false candidate (৩৫ control শব্দে); patent-এর selector character recognition — LSE-তে নিষিদ্ধ |
| Drop-fall | 0/4 (৭×২×২ config) | কোনো config-এই সত্য সীমানা পায়নি |
| Watershed | 0/4 (৬৫ config) | কোনো config-এই সত্য সীমানা পায়নি |
| DTW contour-corner | 0/4, ২/৩ সীমানা, ৩৬ ভুল cut | ৮ম স্বাধীন ব্যর্থতা |
| τ-signal | 0/4 (সব threshold) | **τ উল্টো:** সত্য সীমানায় τ 144/196/144, intra-word সর্বোচ্চ ৭০ — signal-টাই উল্টো দিকে |

**মোট: p20-র লাইনে এখন ১২টি স্বাধীন পদ্ধতি ব্যর্থ** (R23-র count-driven, bridge-strength, white-column, reservoir; R24-র greyscale bridge, min-cost seam, EP0780782 pixel-bridge; R25-র Omron M, skeleton-graph, tree-indexed, fuzzy vote; R26-র JP2000322514A, drop-fall, watershed, DTW, τ-inverted)। প্রতিটির ব্যর্থতার কারণ আলাদা করে মাপা আছে — একটিও "ঠিকমতো চেষ্টা করা হয়নি" নয়। **p20-র fused লাইন geometry-only known limit হিসেবে বহাল** — যতক্ষণ না Hong & Hull-এর মতো blob-এর বাইরের signal (Round 27) পরীক্ষা হয়।

---

## ৪. p21-র ৭-শব্দ stretch — KNOWN LIMIT ভেঙেছে (τ)

Target: `[827,1970,1317,2005]` = "three months before the date of expiry" (৭ শব্দ, ৬ সত্য সীমানা rel 68.5/173.5/264.0/310.0/373.0/407.0)। R23-তে প্রমাণিত known limit (২৪ split: ৯ সঠিক, ১৫ ভুল, কোনো separating signal নেই), R24-তে বহাল, R25-তে বহাল।

**τ যা করে:** ৬টি সত্য সীমানাই আক্ষরিক খালি column (τ ০), আর প্রতিটি intra-word column-এ τ ≥ ২৮ (সর্বনিম্ন false local-minimum τ = ৩২)। **প্রতিটি integer threshold T ∈ [1,32] দেয় ৬/৬ + ০ false** — T=1 fitted নয়, interval-এর conservative endpoint। Pieces **৭/৭ শব্দ** word identity-তে (±3px ও ±5px)। দুই render-এই (pipeline round18 + round4 — round4-এ T=2-এ)। thr 183/185/crop-Otsu-তেও ৬/৬।

**কেন এটা false pass নয় (bridge/seam-এর সঙ্গে পার্থক্য):** bridge/seam 24/1 পেয়েছিল 0/4 শব্দে — gate সংখ্যা সত্য ছিল না। এখানে gate flip-এর ভিত্তি ৭/৭ শব্দ word identity-তে, T4 চোখ চুপ (over-split eye কিছু ধরে না), canonical হুবহু একই, ৩২/৩৩ পাতা byte-identical, p20 untouched। **R24-র "known limit" আংশিকভাবে render artefact-ও ছিল:** R24-র "Otsu gap ০" round4 render-এ সত্য (min grey ১৪২), কিন্তু pipeline render-এ একই column-এ min grey ঠিক ১৮৪ = Otsu — শূন্য grey level-এ খালি। τ দুই render-এই কাজ করে, তাই fix-টা এক render-এর accident নয়।

**Merge-এর নিজের যাচাই:** ৩২/৩৩ পাতা box-identical (শুধু p21); p21-র ৭টি নতুন piece সব src `fused-tau` (`[827,1970,898,2005]` … `[1235,1970,1317,2005]`); p21 GT seam scorer-এ ৩৪/৪২ (R25-র সঙ্গে হুবহু একই); gate p21 ALLOW (T3=0, T4=0, T5=0)।

---

## ৫. p21 heading — KNOWN LIMIT (reachability wall-সহ)

Heading (৮ শব্দ, underline-এ fused, dropped)। এই রাউন্ডে reduced underline-এর সেরা ফল **৫/৮ = control ৫/৮** (নিখুঁত band deletion-এর সমান — একই ৫টি শব্দ, একই ৩টি ব্যর্থতা)। Patent-এর primary মান দেয় ২/৮। Intersection pattern-এ word-boundary signal নেই (NO-run width পুরো overlap)।

**Reachability wall (R25-তেও, এখনও):** heading blob (৯৯৩px চওড়া) পাইপলাইনের comp filter `ww > 900`-এ **line-grouping-এর আগেই** ফেলে দেওয়া হয় — splitter-এর ভেতরে কোনো বদলই তাকে বাঁচাতে পারে না, নীতিগতভাবে। Variant A 0/8 + ২ regression; Variant B clean zero-regression bypass — কিন্তু DO NOT PROMOTE: recognition-ছাড়া grouping-এর কোনো পথ নেই। **p21 heading known limit হিসেবে বহাল।**

---

## ৬. Gate-কাজ — T5 PROMOTE, T4b/T4c DO NOT PROMOTE

**(ক) T5 rule-shred eye — PROMOTE।** R25 §৬-র সতর্কতা (fuzzy splitter-এর guard p01/p2-র horizontal rule-কে ৫ টুকরো করেছিল, gate কিছু বলেনি) বন্ধ হয়েছে। Rule-like iff: (i) h ≤ 0.50×med_h AND w ≥ 12×med_h; (ii) একটিই Otsu CC ≥ 0.80 width জুড়ে। ৩৩ পাতায় ঠিক ৫টি box-এ fire — **৫টিই rule, ০ text**। Fuzzy set-এ 24/1 → **22/3** (দুটি নতুন REFUSE-ই আসল rule-shred)। Baseline-এ T5 = ০ সর্বত্র — **০ false positive**। Gate diff purely additive (৯৯ insertion, ০ deletion)।

**(খ) Hoover/OAM over-split eye T4b — DO NOT PROMOTE।** ১৫৯টি false positive (pair form), ৩৫টি (≥3-run form)। আসল over-split-কে tolerated joined token থেকে আলাদা করার কোনো geometric leg নেই। Baseline আসলেই over-split করে (p09 SHAHJALAL, p13/14/15 AHMEDABAD — eye-verified) — কিন্তু চোখটি ধরতে গিয়ে ১৫৯টি ভুল ধরে। **সৎ স্বীকারোক্তি:** gate এখনও over-split-কে পুরো ধরতে পারে না — T4 শুধু Path-C collapse-এর ভেতরের over-split ধরে, সাধারণ over-split নয়।

**(গ) Modal-stroke-width ligature detector — DO NOT PROMOTE।** সব wide CC-র ৮১.৪%-এ fire করে (৮৩৯/১০৩১)। p20-র join full-height slash, পাতলা ligature নয় — detector-টি ভুল জিনিস মাপে।

---

## ৭. R23/R24/R25-র শিক্ষা মানা হয়েছে — দুই render-ই যাচাই, Guard re-run, repo-port যাচাই

- **দুই render:** PNG segs + fitz render (১৪ PG পাতা) — দুটোতেই যাচাই। Aug p1 PNG **৩০৬** / fitz **৩০৮** — দুই render-পথেই সঠিক। Fitz 0/14 differ (fitz-base-এর সঙ্গে), 0/14 differ (τ track-এর fitz-tau-র সঙ্গে)।
- **Guard re-run (τ track-এর নির্দেশে, R25-তে skip করা হয়েছিল):** **0/5 FAIL — এই রাউন্ডের সবচেয়ে গুরুত্বপূর্ণ সৎ ধরা।** Live page-গুলি embed করে ৩০২/২৯৭/৩০২ শব্দ (পুরনো seg family), বর্তমান segs ৩০৬/৩০৮/৩০৫। C1 count FAIL (page 302 vs seg 306, aug-p1), C2 ordered FAIL, C3 multiset FAIL, C4 spot FAIL (০/২৪), C5 identity FAIL (Lot/WIDTH in_seg=False)। **R25-র segs-এও একইভাবে FAIL** — pre-existing, R26 regression নয়। R24/R25-র "Guard 5/5 PASS" re-run ছাড়াই বয়ে আনা হয়েছিল (segs byte-identical বলে "অপরিবর্তিত" ধরে নেওয়া) — সেটা ছিল অনুমান, মাপ নয়। **এটা segmenter regression নয় — live page stale।** ঠিক করার কাজ: live page-গুলি বর্তমান segs দিয়ে rebuild করা (আলাদা কাজ, segmenter বদল নয়) — §১১-তে open item হিসেবে রাখা হয়েছে।
- **Repo-port যাচাই:** τ port-টি merge segmenter-এর সঙ্গে p21-তে byte-identical (৫৯০ শব্দ, box-set identical) — §২-এর trap-সহ।
- **E2 অক্ষত:** `_gap_mark` R21-র verbatim — Aug p1 fitz ৩০৮ অক্ষত (R23-র শিক্ষা)।

---

## ৮. coverage — 95/97 অপরিবর্তিত

`probe_coverage.py` R26 segs-এ চালানো হয়েছে — output JSON **R25-র সঙ্গে (segdir/suffix label ছাড়া) byte-identical**: exact_box_items ৯৭, covered ৯২, still_missing_exact ৫, no_box_items ৪৬; extra ৯টির ৭টি covered। R23-র সংশোধন (৫টি "miss"-এর ৩টি আসলে miss নয় — "OR"-এর centre 3px gap-এ, union 0.805; "Yours"/"faithfully," diagnosis box-এ signature scribble) একইভাবে প্রযোজ্য — **সত্য coverage 95/97, অপরিবর্তিত**। τ split coverage বদলায় না — stretch-এর কালি fused box-এও covered ছিল (union 1.0), এখন ৭টি box-এ covered। বাকি ২টি আসল + ৩টি known-limit miss আগের মতোই: CARRIER NAME লাইন (৮ শব্দ), p21 heading, p21 address লাইন (২৬ শব্দ ১৪ box-এ), p10 "Prepared" (geometry-only unfixable), stamp fragment-গুলি (সঠিকভাবে drop)।

---

## ৯. সংশোধন (corrections — আগের রিপোর্টের ভুল ঠিক করা)

1. **Guard "5/5 PASS" — ভুল ছিল, সত্য 0/5 FAIL (pre-existing):** R24/R25-র "Guard 5/5 PASS (segs byte-identical বলে অপরিবর্তিত)" re-run ছাড়াই বয়ে আনা হয়েছিল। এই রাউন্ডে re-run-এ দেখা গেল live page-গুলি stale (৩০২/২৯৭/৩০২ শব্দ embed করে, বর্তমান segs ৩০৬/৩০৮/৩০৫) — **R25-র segs-এও 0/5 FAIL**। "5/5 PASS" আর উদ্ধৃত করা যাবে না। এটা segmenter regression নয় (PG segs byte-identical), live-page staleness — কিন্তু সংখ্যাটা এখন মাপা, অনুমান নয়।
2. **p21 GT 36/42 বনাম 34/42 — scorer-নিয়মের পার্থক্য, পরিবর্তন নয়:** R19–R25 report-এর 36/42 (meet-rule) আর seam-track scorer-এর 34/42 (@ ±5px) — দুটোই একই GT file (`round20/track-top2b/gt-p21.json`, ৪২টি certain boundary: L1648 ৯, L1926 ১৫, L2379 ১৮)। একই scorer-এ (seam's `score_p21gt.py`) **R25 আর R26 দুটোতেই 34/42** (per-line L1648 ৬/৯, L1926 ১০/১৫, L2379 ১৮/১৮; ±4px-এ ২৭/৪২, ±8px-এ ৩৫/৪২) — কোনো regression নেই, সংখ্যার পার্থক্য scoring rule-এর। 36/42 বনাম 34/42-কে পরিবর্তন হিসেবে উদ্ধৃত করা যাবে না।
3. **R24/R25-র "p21 stretch ACCEPTED KNOWN LIMIT" — ভেঙেছে:** τ ৭/৭ শব্দে stretch-টি ঠিক করেছে (§৪)। Known-limit list থেকে stretch বাদ গেল — বাকি আছে শুধু **p20-র fused লাইন আর p21 heading**। (Module 14 exact form-এর known-limit verdict বহাল — সেটা আলাদা পদ্ধতি, আলাদা প্রমাণ।)
4. **R25-র "৭টি ট্র্যাক" — এই রাউন্ডে ৯টি ট্র্যাক:** coordinator ৯টি track চালিয়েছিল (৫টি p20 lead + p21stretch + heading + gate + online)। সবাই complete, সবাই report দিয়েছে — কোনোটি "interrupted" নয় (§১)।

---

## ১০. সৎ প্রশ্ন — geometry-only উপায়ে 25/0 কি সম্ভব?

**এই রাউন্ডের পর উত্তর: এখনও না — আর প্রমাণ এখন সংখ্যায় দাঁড়িয়ে আছে।**

- **p20-র fused লাইন:** ১২টি স্বাধীন পদ্ধতি ব্যর্থ (§৩)। প্রতিটির ব্যর্থতার কারণ আলাদা করে মাপা — কোনো common bug নেই, কোনো "ঠিকমতো চেষ্টা করা হয়নি" নেই। সবচেয়ে শক্তিশালী তথ্য: JP2000322514A **সত্য সীমানা খুঁজে পায়** (৩/৩) — তবু 0/4 শব্দ, কারণ selection-এর জন্য recognition লাগে, যা LSE নিষিদ্ধ করে। অর্থাৎ detection-এর সমস্যা নয়, **selection-এর সমস্যা** — আর geometry-only selection-এর কোনো signal এখনও পাওয়া যায়নি (gap, bridge-strength, white-column, reservoir, width, uniformity, τ, skeleton depth — সব overlap করে)।
- **p21 heading:** reachability wall (`ww > 900`) — splitter-এর ভেতরে কোনো বদলই তাকে বাঁচাতে পারে না; recognition-ছাড়া grouping-এর পথ নেই।
- **কিন্তু "অসম্ভব" বলা যাবে না — τ প্রমাণ করেছে:** R23-তে "প্রমাণিত known limit" বলা stretch-টি R26-তে ভেঙেছে। একটা নতুন signal (τ) একটা limit ভেঙেছে — তাই "আর কোনো signal নেই" দাবি করা অসততা হবে। সৎ অবস্থান: **২৫/০ এখনও সম্ভব নয়, কিন্তু অসম্ভব প্রমাণিত নয়** — বাকি আছে একটিই untried lead (Hong & Hull, blob-এর বাইরের signal — §১১)।
- **ইঞ্জিন যা পারে (মাপা):** gate **24/1** (শুধু p20 REFUSE — প্রমাণিত known limit, সঠিক REFUSE); full suite **43/43**; T3 recall **35/35 (100%)**, ০ false positive; T4+T5 চোখ (০ false positive baseline-এ); coverage **95/97**; canonical হুবহু একই (N5 41/81, p3 248/285, LINES 327/327); demo **৮২**; DB SHA অপরিবর্তিত; PG/fitz দুই render-এই সঠিক। **এই অবস্থাটাই সৎ 100%-র পথের মাইলফলক — 24/1, যেখানে ১টি REFUSE-এর কারণ মাপা আর প্রমাণিত।**

---

## ১১. খোলা বিষয় (open items — Round 27-র জন্য)

1. **p20-র fused লাইন — Hong & Hull lead (Round 27-র candidate):** visual inter-word constraints / sub-image matching — fused blob-এর **বাইরের** signal (পাতায় অন্যত্র পরিষ্কার repeat থাকলে)। শর্ত: repeat-টি পরিষ্কার হতে হবে; না থাকলে এই lead-ও চলবে না। এটাই শেষ untried geometry-only lead (RESEARCH26.md)।
2. **p21 heading — known limit বহাল:** `ww > 900` reachability wall; recognition-ছাড়া grouping-এর পথ নেই।
3. **Live page rebuild (Guard-এর fix):** ৫টি live page (`live-scan-page-aug-300.html` ইত্যাদি) বর্তমান segs (৩০৬/৩০৮/৩০৫) দিয়ে rebuild করতে হবে, তারপর Guard re-run করে 5/5 PASS মাপতে হবে। এটা segmenter-এর কাজ নয়, demo-page maintenance — কিন্তু "5/5 PASS" দাবি করার আগে এটা করতেই হবে।
4. **Gate-এর over-split সীমা:** T4 শুধু Path-C collapse-এর ভেতরের over-split ধরে; সাধারণ over-split (p09 SHAHJALAL, p13/14/15 AHMEDABAD) এখনও ALLOW — T4b ১৫৯ FP-তে ব্যর্থ হয়েছে, নতুন চোখ লাগবে।
5. **R25 push এখনও বাকি:** repo এখনও Round 20-তে (commit `495c1086`) — R25 push approval card timeout-এ আটকে আছে (parent-এর হাতে)। R26 push-এর আগে R25-র push সিদ্ধান্ত নিতে হবে (parent-এর reversible decision)।
6. **আগের মতোই খোলা:** Virtako label ৫-field decision (user-এর — আবার জিজ্ঞাসা করা যাবে না, তিনি সুবিধামতো জানাবেন); Windows .exe (তার PC-তে build); print calibration (factory printer — শুধু তিনি, Muse-র কাজ শেষ হলে); US patent legal check (lawyer — তিনি ব্যবস্থা করবেন; lead: US 5,734,761 + Adobe US9741142B2 + US 20250111688 + US 20250078557); .docx capture 100/100 (৯৬.৬০% এখন); first-view ~১৪–১৮s (Phase-4-sized কাজ); Q-03–Q-09 + ★2–★8 + ১৮ borderless edge (DECISIONS-PENDING.md-তে)।

---

## ১২. যাচাই (verification — parent-এর জন্য)

- **Merge:** `merge-r26/segment_merged.py` + `gate_merged.py` + `rhythm_dp.py` + `logo_detect.py` + `gate_misses.py` + `segs/` (৩৩ পাতা) + `gate_batch_r26_merged.json` + `canon_r26_merged.json` + `coverage_r26.json` + `merge_segment_r26.py` + `run_segs_r26.py` + `run_gate_r26.py` + `score_canon.py` + `verify_fitz_r26.py` + `port_tau_to_repo.py`। Segmenter diff R25→R26: **৩০৫ addition / ৬ deletion** (τ only); gate diff **৯৯ insertion / ০ deletion** (T5 only); support ফাইল byte-identical।
- **Gate:** **24/1** (২৫ পাতা); **৩২ ALLOW / ১ REFUSE** (৩৩ entry)। REFUSE: শুধু p20 (T3 Path C, box `[557,661,986,678]`, min_cc_w_med 8.36, fus_cover 0.993)। p21 **ALLOW** (T1 0, T2 0, T3 0, T4 0, T5 0, ৫৯০ শব্দ)। T1 ০, T2 ০, **T4 ০, T5 ০**। ২৩টি পুরনো ALLOW পাতার প্রতিটি R25-র সঙ্গে SAME। (T3 recall-এর নোট: T3-র code অপরিবর্তিত (gate diff-এ ০ deletion) — p21-তে T3=0 কারণ collapse-টি segmenter ঠিক করেছে (৭ শব্দে ভেঙেছে), T3 miss করেনি; p20-র collapse এখনও T3-তে ধরা পড়ে। "35/35" R23-র collapse set-এর মাপ — সেই set-এর p21 সদস্যটি এখন fixed, বাকি সবাই এখনও flagged।)
- **শব্দ:** ২৫ পাতা **9379 (+6)**, ৩৩ পাতা **12372 (+6)**; p2 ৬৭৬, p3 ৪৭১; p20 ৫২১ (=), p21 **৫৯০ (+6)**; PG aug 306/308/305, may 308/313/306 (=)। **৩২/৩৩ seg byte-identical** (শুধু p21 বদলেছে — ৭টি নতুন piece সব src `fused-tau`)।
- **Canonical:** N5 **41/81** (=), Description ভুল **৩০** (একই list), redbox **7/66** (=), p3 strict **248/384**, improved **285/384**, FP 186, p21 GT **34/42** @ ±5px (seam scorer — R25-র ৩৪/৪২-এর সঙ্গে হুবহু একই, §৯), LINES **327/327**। PG diff vs R20 baseline: শুধু aug-p2-তে ১টি box বদল (R25-র সঙ্গে হুবহু একই — pre-existing)।
- **Guard:** **0/5 FAIL** (re-run, §৭) — pre-existing, R25 segs-এও fail; live page stale (৩০২/২৯৭/৩০২ বনাম ৩০৬/৩০৮/৩০৫)। Segmenter regression নয়।
- **Coverage:** **95/97** অপরিবর্তিত (probe JSON R25-র সঙ্গে identical)।
- **DB SHA:** `1c065457bb9cb8e5b276d5007d9b020c18c8a0ae0374b92eb759f12150746939` — আগে ও শেষে একই (DB ছোঁয়া হয়নি)।
- **Fitz render:** Aug p1 **৩০৮ শব্দ**; ১৪টি PG পাতা fitz-এ segment করা হয়েছে (aug 308/308/305/307/303/303/311/309, may 307/313/305/306/305/309 — সব SAME, 0/14 differ)। PNG 306 / fitz 308 — দুই render-পথেই সঠিক।
- **Full suite (repo test clone `~/workspace/lse-r26-test/`, lse-r25-push-এর কপি + τ port + T5 port + ৩ নতুন test):** **43/43 PASS (429.6s, exit 0, 0 fail, 0 error, 0 skip)**। ৩টি নতুন test আলাদাভাবে যাচাই করা হয়েছে (p21-stretch PASSED, ২টি T5 PASSED)। Demo **৮২ শব্দ** (নিজে চালিয়ে যাচাই)। Repo-port p21-তে merge segs-এর সঙ্গে **box-set byte-identical** (৫৯০ শব্দ)।
- **Push করা হয়নি, Drive-এ upload করা হয়নি, MEMORY.md ছোঁয়া হয়নি** — parent যাচাই করে push/upload/memory করবে। **Push সিদ্ধান্ত parent-এর:** R25 push এখনও বাকি (approval timeout) — R26-কে আলাদা push করা হবে নাকি R25+R26 একসাথে, সেটা reversible working decision হিসেবে parent-এর হাতে।

---

## ১৩. উদ্ভাবন বনাম মেরামত (purpose check — ব্যবহারকারীর নির্দেশ)

এই রাউন্ডের **উদ্ভাবন:** (ক) **τ-signal** — একটি patent signal (US 20150086113) নতুন guard-সহ প্রয়োগ করে প্রমাণিত known limit ভাঙা — geometry-only-তে নতুন signal পাওয়া যায়, এটা তার প্রমাণ; (খ) **T5 rule-shred eye** — gate-এর hole বন্ধ করা নতুন চোখ, যেটা rule-কে text থেকে আলাদা করে (০ false positive); (গ) **Guard-এর সৎ ধরা** — "5/5 PASS" অনুমানটি ভেঙে সত্যটা মাপা (0/5 FAIL, pre-existing) — ভুল সংখ্যা বয়ে না আনা; (ঘ) **১২টি ব্যর্থতার প্রমাণ-ভাণ্ডার** — p20-র লাইনে প্রতিটি পদ্ধতির ব্যর্থতার কারণ মাপা, যা ছাড়া Round 27 অন্ধভাবে একই পরীক্ষা আবার করত। **মেরামত:** repo-port trap ধরা আর ঠিক করা (§২) — একটিই, আর সেটাও যাচাই-প্রক্রিয়ার অংশ। সৎ মূল্যায়ন: এই রাউন্ড gate-কে 24/1 করেছে, একটি known limit ভেঙেছে, gate-কে আরও সৎ করেছে, আর সীমার প্রমাণে পূর্ণ — আর সীমা না জানলে 100%-র পথে হাঁটা যায় না। সবচেয়ে বড় শিক্ষা (R24–R25-র সঙ্গে একমত): **gate-এর সংখ্যা সত্য নয় — word identity-ই সত্য** — আর এখন gate-ও সেটা জানে (T4+T5)। আর নতুন শিক্ষা: **বয়ে আনা সংখ্যা সত্য নয় — re-run-ই সত্য** (Guard)।
