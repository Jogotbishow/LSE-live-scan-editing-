# LSE Round 23 — রিপোর্ট

**তারিখ:** 2026-11-09 · **ভাষা:** বাংলা · **মার্জ এজেন্ট:** Round 23 coordinator
**Baseline:** Round 22 merged segmenter + gate (`round22/merge-r22/`, gate 24/1) — read-only, ভাঙা হয়নি
**নতুন baseline:** `improve/round23/merge-r23/` (segment_merged.py + gate_merged.py + rhythm_dp.py + logo_detect.py + gate_misses.py + segs/)
**ডিরেক্টরি:** `improve/round23/` — প্রতি ট্র্যাকের নিজের ডিরেক্টরিতে তার সব আউটপুট; merge `merge-r23/`-তে
**নির্দেশ:** ব্যবহারকারীর LSE 100% নিয়ম (2026-11-08 22:42) — Muse নিজে 100% সন্তুষ্ট না হওয়া পর্যন্ত LSE-র কাজ থামবে না; কোনো অনুমতি লাগবে না। এই রাউন্ড সেই নির্দেশেই চলেছে।

> **সৎ সারাংশ:** Gate 24/1 → **23/2** — 25/0 হয়নি, আর সংখ্যায় R22-র চেয়ে **খারাপ** দেখায়। কিন্তু খারাপটা সৎ: নতুন Path C চোখ p20-র ১টি আসল whole-line collapse ধরে (4 শব্দ এক box-এ — "BENEFICIARY/MANUFACTURER/EXPORTER/SHIPPER"), তাই p20 ALLOW→REFUSE হয়েছে — segmenter ওই লাইন ঠিক না করা পর্যন্ত ALLOW ফেরত আসবে না। p21 এখনও REFUSE (7-শব্দ stretch)। শব্দ +13 (9360 → 9373), coverage সত্য 95/97, T3 recall **35/35 (100%)**, ০ false positive। p21-র stretch geometry-only উপায়ে ঠিক করা **সম্ভব হয়নি** — প্রমাণসহ (§৪)। আর merge যাচাইয়ে ধরা পড়েছে সবচেয়ে বড় শিক্ষা: knife ট্র্যাকের E2 removal repo suite-এ **35/38** করেছিল (fitz render-এ ১ শব্দ হারায়) — সেটা বাতিল করে R21 excuse ফেরানো হয়েছে, suite আবার **38/38** (§৭)। এই রিপোর্টে দুটোই সৎভাবে বলা হয়েছে।

---

## ০. এক নজরে — headline সংখ্যা

| মাপ | R22 baseline | **Round 23 merge** |
|---|---:|---:|
| Gate (২৫ Raviraj পাতা) | 24 ALLOW / 1 REFUSE | **23 ALLOW / 2 REFUSE** |
| ফ্ল্যাগ (T1 / T2 / T3) | 1 (0 / 0 / 1) | **2 (0 / 0 / 2)** |
| মোট শব্দ (২৫ পাতা) | 9360 | **9373 (+13)** |
| মোট শব্দ (৩৩ পাতা) | 12353 | **12366 (+13)** |
| REFUSE পাতা | শুধু p21 | **p20 + p21** |
| Canonical p2 N5 / Description ভুল / redbox | 41/81, ভুল ৩০, 7/66 | **41/81 (=), ভুল ৩০ (=, একই list), 7/66 (=)** |
| Canonical p3 strict / improved (FP) | 248 / 285 (186) | **248 (=) / 285 (=) (186, =)** |
| Canonical p2 / p3 gate | p2 ALLOW, p3 ALLOW | **p2 ALLOW, p3 ALLOW (=)** |
| LINES (canonical r15m) | 327/327 | **327/327 (=)** |
| PG ৬ পাতা (শব্দ) | aug 306/308/305, may 308/313/306 | **aug 306/308/305, may 308/313/306 — হুবহু একই** |
| p21 GT (৪২ certain boundary) | 35/42 (পুরনো scorer) | **36/42 @ ±5px meet-rule — R22-ও 36/42, কোনো regression নয় (§৯)** |
| Guard (live page, FULL) | 5/5 | **5/5 PASS** |
| Round 3 DB SHA | `1c065457…` | **`1c065457…` — আগে ও শেষে একই** |
| Full suite (repo test clone) | 38/38 | **প্রথমে 35/38 (E2 regression, §৭) → fix-এর পরে 38/38 PASS (413.34s, 0 fail)** |
| Demo (synthetic) | 82 শব্দ | **82 শব্দ (=)** |
| Aug p1 শব্দ-সংখ্যা | PNG 306 / fitz 308 | **PNG 306 / fitz 308 — দুই render-পথেই সঠিক (আবার)** |

**ফ্লিপ (ALLOW→REFUSE):** p20 (Path C — ১টি আসল 4-শব্দ collapse, R22-র চোখ দেখতো না)। **কোনো ALLOW→REFUSE regression নেই** — ২৩টি পুরনো ALLOW পাতার একটিও regress হয়নি; p20-র flip সৎ ধরা, regression নয় (§৩)।
**বাকি ২টি REFUSE:** p20 — T3 Path C ১টি collapse (§৩); p21 — T3 Path B ১টি collapse (§৪)।
**নোট — E2-ছাড়া merge-এর সংখ্যা:** E2 removal-সহ merge-এ gate-ও 23/2 ছিল, শব্দও 9373/12366, canonical-ও একই — PNG segs byte-identical বলে (§৭)। পার্থক্য শুধু fitz render-এ: E2-off-এ Aug p1 307 শব্দ, suite 35/38; E2-ফেরত-এ 308 শব্দ, suite 38/38।

**Promotion bar-এর রায়: পাস — তবে 25/0 নয়, আর gate সংখ্যায় পিছিয়েছে।** T3 recall 100% (35/35), coverage সত্য 95/97, শব্দ +13, canonical হুবহু সমান, suite 38/38। কিন্তু p20-র fused লাইন segmenter ঠিক করতে পারেনি (count-driven cut-এ ০টি ভালো valley), আর p21-র stretch প্রমাণিত known limit। 25/0 দেখাতে T3-কে warn-only করা হতো **অসততা** — Path C-র ধরা collapse লুকানো যাবে না। Gate এখন আরও কঠোর ও সৎ: R22-তে অদৃশ্য p20 collapse এখন ধরা পড়ে। p20-র লাইন আর p21-র stretch ঠিক করা Round 24-র কাজ (§১০)।

---

## ১. ট্র্যাক verdicts — ৬টি ট্র্যাক, সব DONE

| ট্র্যাক | verdict | মূল ফল |
|---|---|---|
| **track-online** | গবেষণা (কোড নয়) | RESEARCH23.md (১৯৯ লাইন, ২২টি নতুন source): Top 3 — (১) EP0780782 pixel-bridge greyscale classification (p21 stretch; `of\|expiry` boundary: Otsu gap ০, dark 4px — binary-তে মৃত, greyscale-এ জীবিত); (২) US 5,253,304 count-driven cut-point (p20 maxgap 2px; expected n আগে, তারপর সেরা valley; cut কম হলে "no valid segmentation"); (৩) Lee & Oh 2010 nonlinear minimum-cost cut path (সাদা pixel দিয়ে বাঁকা seam)। Heading: Bai & Huo ICPR 2004 + Amazon US 9,286,541। নিজের প্রস্তাব (সৎভাবে unproven চিহ্নিত): 2D white-column profile। **সৎ verdict: Round 22-র negative এখনও বহাল — 2024–2026-এ geometry-only word segmentation-এ কোনো breakthrough নেই।** |
| **track-p21stretch** | **DO NOT PROMOTE (প্রমাণিত known limit)** | Otsu-CC piece split (Idea D) stretch-টিকে ঠিক তার ৭টি সত্য শব্দে (three/months/before/the/date/of/expiry) + আরও ৬টি p21 merge-এ ভাঙে, ৬টি victim box অক্ষত, gate 25/0 হতো — **কিন্তু** চোখে যাচাই ২৪টি v2 split-এ **৯টি সঠিক, ১৫টি ভুল** (TRANSPORT→TRANS\|PORT, consignor→con\|signor, Ravi→R\|av\|i, ORIGINAL→ORIG\|INAL, BENEFICIARY, EXPORTER, BANGLADESH, QUANTITY, PROFORMA, COATED-র টুকরো)। কোনো signal শব্দ-boundary-কে intra-word CC boundary থেকে আলাদা করে না — gap (দুটোতেই 5px), bridge-strength, white-column, min-cost seam, reservoir, dark/core sub-count ("the"=১ sub, "T"=১ sub), piece width, uniformity — সব overlap করে। "TRANS"+"PORT" এক শব্দ — এটা letter sequence-এ আছে, CC structure-এ নেই। ফাইল `segment_p21stretch.py` শুধু rejected experiment হিসেবে রাখা, header-এ DO NOT PROMOTE / DO NOT MERGE চিহ্নিত। |
| **track-heading** | **DO NOT PROMOTE, UNFIXABLE (এই ২ পদ্ধতিতে, প্রমাণসহ)** | Bai & Huo + Amazon US 9,286,541 (Justia-তে পুরো পড়া) — দুটোই পরীক্ষা করা। Identification সফল (rule y1111–1114, row-ink 0.84–0.94; Otsu CC ১ = TOUCHED underline) কিন্তু removal ব্যর্থ: Amazon transition-count ভাঙে — dark 1-run column ৩৯৪ = pure-rule ১৪৬ + fused letter+rule ২৪৮, দুটোই ঠিক ১ run; column-wise rule deletion: dark 30 CC ০/৮, Otsu ০ CC (pure column ১/৯৯৩ — fringe ink সব ঢেকে দেয়), core-140 ৭ CC ১/৮ (৭৫২px mega-CC)। নির্ণায়ক: pure-column test word gap-এ ১০০% জ্বলে **আর** letter gap-এও ১০০% — এটা gap-width-ই আরেক রূপে, নতুন তথ্য নয়। কোনো variant ফাইল বানানো হয়নি; baseline অক্ষত। একটি probe ভুল ধরা পড়ে ঠিক করা হয়েছে (pure-column count ৩৭৯ → সঠিক ১৬৪; ভুল সংখ্যায় কোনো সিদ্ধান্ত নেওয়া হয়নি)। |
| **track-misses** | **PROMOTE (EXP2)** | শব্দ 12353 → **12366 (+13; p01 +14, p22 −1, বাকি ৩১ পাতা অপরিবর্তিত)**; gate 24/1 হুবহু একই; canonical হুবহু একই। Word identity-তে: "gal" union 0.368 → 1.0, "by" 0.386 → 1.0, "on of Caution" 0.599 → 0.931, FOB row এখন ৫টি exact box (FOB/VALUE:/USD/56775/21), fused mega-blob `[544,1753,1111,1893]` নেই। EXP2 = ৪টি patch: row-split uneroded retry + retry height guard (retry product >2×med_h হলে বাতিল — p07 signature regression আটকায়) + FIX F overhang + F3 swap। **সৎ wart:** ২টি লাল stamp fragment fake word হিসেবে রয়ে গেছে, H.S.CODE/"7607.19.10" over-split, decimal-point split ("56775"+"21")। Count-driven DO NOT PROMOTE (n estimate ১৩ বনাম সত্য ৮; valley depth পুরো interleaved)। Address-line 2-means DO NOT PROMOTE। p10 "Prepared" geometry-only unfixable — R22-র দাবির চেয়েও শক্ত প্রমাণ (১৯px intra-word gap বনাম ৫px "ared"\|"By"; একই পাতায় "Incharge" ১৮px intra-word বনাম ৬px সত্য word gap)। এখনও অমীমাংসিত: CARRIER NAME লাইন (৮ শব্দ), p21 heading, p21 address লাইন (২৬ শব্দ ১৪ box-এ)। |
| **track-t3** | **PROMOTE (Path C)** | নতুন Path C (fused-CC topology, gap নয়): (i) কোনো letter-sized CC নেই (প্রতিটি CC ≥ 2.0×med_h), (ii) fused union cover ≥ 0.5, (iii) সবচেয়ে লম্বা zero-ink run ≤ 2px। পূর্ণ ৩৫-collapse set-এ recall **34/35 → 35/35 (100%)**, ০ false positive (১৬টি genuine control + ৩৩ পাতা × ২ seg set)। Target p20 `[557,661,986,678]` = "BENEFICIARY/MANUFACTURER/EXPORTER/SHIPPER" (৪ শব্দ, slash-জোড়া), ৩টি CC ১১৭–১৫৮px (8.4–11.3×med_h), gap ১px আর ২px; min_cc_w_med 8.36, fus_cover 0.993। **Margin: target-এর min CC 8.36×med_h, নিকটতম non-target 1.55× — 2.0 boundary খালি interval [1.55, 8.36]-এ, ৫.৪× margin, knife-edge নয়।** RESEARCH23-র signal মেপে বাতিল (count-driven cut হিসেবে ৮টি cut-এর ০টি ভালো valley — কিন্তু REFUSE হিসেবে সঠিক; bridge-strength overlap; white-column সব 1.0; reservoir pocket ratio target 8.0 বনাম genuine সর্বোচ্চ 3.0, **কিন্তু** stamp-overlapped box 30.0 — false positive দিত)। **ফল: R22 seg-এ Path C p20-কে ALLOW → REFUSE ফ্লিপ করে (সৎ flip — আসল collapse; segmenter-কে লাইন ঠিক করে re-allow করতে হবে)।** |
| **track-knife** | **৪টি knife-edge মাপা, একটিও principled নিয়মে বদলানো যায়নি; E2 removal PROMOTE → verification-এ REVERTED (§৭)** | (১) F=1.70 CANNOT REPLACE — ৭টি principled প্রার্থী (per-box/per-line 2-means, Tukey, Otsu, stroke-based, Lee & Oh seam) সব fail; window (1.667, 1.75] reproduce; মূল কারণ: letterspaced genuine শব্দেও bimodal gap — শুধু box-র নিজের letter-gap scale (trim_med) ৫px letter-gap-কে ৭px word-gap থেকে আলাদা করে, আর সেটাই F মাপে। (২) FIX3 3px run floor CANNOT REPLACE — veto population n=1 (৩৩ পাতায় শুধু BENAPOLE, run ২ বনাম floor ৩); speck-free replacement দুই দিকেই ভুল। (৩) E2 width boundary 0.50: two-signal replacement CANNOT REPLACE (height / vertical alignment / white-column সব fail; excused ৩টির ৩টিই চোখে letter piece) — **কিন্তু নিয়ম সরানো PROMOTE** ছিল: E2-off-এ ৩৩/৩৩ byte-identical seg, gate 24/1 অপরিবর্তিত; 0.55 p21 ভাঙে (+১ শব্দ, letter-এর ভিতর দিয়ে কাটা) — 0.50 loose-side-এ load-bearing। **সংশোধন: R21-র "@ ring" identification ভুল ছিল — PNG render-এ ওটা "gfoils"-এর "s"।** Verification-এ PROMOTE বাতিল হয়েছে (§৭) — excuse ফেরানো হয়েছে। (৪) floor-4 evidence n=1 CANNOT REPLACE (প্রমাণ শক্ত হয়েছে): false side এখনও n=1 (সৎ), কিন্তু genuine-min **77px** (p2-র "P", চোখে যাচাই) — R21-র 8px নয়; window [2,77]; floor 0 → p10 REFUSE; floor 4 = ৮টি byte-identical (৩২/৩৩); FRAC=0.01 gate-identical কিন্তু NOT promoted (১% constant-ও fitted, small-core hole: ১০০–২০০px core-এ ২px graze মিস করে)। |

---

## ২. merge — কীভাবে EXP2 + Path C এক করা হলো

**নেওয়া হয়েছে:** misses EXP2 (৪টি patch) + T3 Path C।
**নেওয়া হয়নি:** p21stretch (§৪), heading (§৫), knife F=1.70 / FIX3 floor / floor-4 replacement, count-driven cut, p10 "Prepared", address-line 2-means। **E2 removal প্রথমে নেওয়া হয়েছিল, verification-এ বাতিল (§৭)** — merge script-এই revert করা হয়েছে, তাই চূড়ান্ত merge-এ E2-র কোনো চিহ্ন নেই।

মার্জ-প্রক্রিয়া (পুনরুৎপাদনযোগ্য — স্ক্রিপ্ট `improve/round23/`-তে রাখা আছে):
- `merge_segment_r23.py` — R22 baseline-এর উপর exact-string replacement, প্রতিটি anchor ঠিক ১ বার মিলিয়ে যাচাই করে। Base = track-misses `segment_misses.py` (R22 + EXP2); E2 step এখন শুধু assert করে R21 `_gap_mark` বহাল আছে (§৭-র কারণসহ comment)। Diff প্রমাণ: R22-র সঙ্গে = **৪টি hunk** (EXP2-র ৪টি patch — row-split retry, retry height guard, FIX F, F3 swap; ১০৭ লাইন বদল); merged ফাইল track-misses source-এর সঙ্গে **byte-identical** (diff খালি)। compile OK।
- Gate merge: `track-t3/gate_t3.py` হুবহু `merge-r23/gate_merged.py`-তে কপি (R22-র সঙ্গে diff -u-তে **৩টি hunk**, ৯০ লাইন — Path C constants/helpers/hook + evidence field); `track-misses/gate_misses.py` হুবহু কপি। compile OK। `check_dp_integrity` আছে।
- R19/R20/R21/R22 fix-গুলো অক্ষত আছে: eroded positive-gap median, "@" gap-position rule, eroded-subs extension + fallback, E2 gap-mark (ফেরত), p01 row-split, p12v5, floor-4, `_split_light_print`, FIX C rev.2 height floor।

**Repo test clone-এ port:** suite চালাতে R23 fix-গুলো repo-র `lse/segment.py` ও `lse/gate.py`-তেও port করা হয়েছে (`~/workspace/lse-r23-test/`, স্ক্রিপ্ট `port_segment_r23.py` + `port_gate_r23.py`)। Repo-র segmenter nested (`segment_array`-র ভিতরে, 4-space indent) বলে re-indent করে port করা হয়েছে; gate top-level বলে সরাসরি। Port যাচাই: segment ৮টি check + gate ৯টি check — সব PASS; compile OK। `gate_misses.py` / `rhythm_dp.py` / `logo_detect.py` merge-r23 আর clone-এ হুবহু একই। Demo-তে port করা segmenter ৮২ শব্দ দেয় (= R22)।

**Port-এ ধরা পড়া ভুল (নিজে ধরা, ঠিক করা):** port script-এ দুটি bug ধরা পড়ে ঠিক করা হয়েছে — F3 regex indent, আর একটি check ভুল করে FIX E rev.4-র `any()`-কে মিলিয়েছিল (check ঠিক করা হয়েছে, কোড নয়); gate port-এও দুটি anchor bug — hook anchor `if path is None:` unique ছিল না, `_iv_ev` anchor `continue` unique ছিল না — দুটোই Path B block / `out.append(`-এ anchor করে ঠিক করা হয়েছে। শিক্ষা: R22-র মতোই — nested port-এ প্রতিটি anchor-এর uniqueness আলাদা করে যাচাই করো; script assert-এ ধরা পড়ে লেখার আগেই থেমে গেছে, repo ফাইল অক্ষত ছিল।

**Merge যাচাই (coordinator-এর নিজের run):** ৩৩ পাতা re-segment — শব্দ 9360 → **9373** (২৫ পাতা), 12353 → **12366** (৩৩ পাতা); box diff আছে শুধু ৫ পাতায় (p01 +30/−16 box, p22 +6/−7, p21 +9/−9, p2 +1/−1, aug-p2 +1/−1); PG সংখ্যা হুবহু একই (aug 306/308/305, may 308/313/306)। Gate **23/2** (T1 ০, T2 ০, T3 ২)। Canonical re-score: N5 41/81, Description ভুল ৩০ (একই list), redbox 7/66, p3 248/285, FP 186, LINES 327/327 — সব R22-র সমান। p21 GT scorer নিয়ে §৯ দেখুন।

---

## ৩. p20-র diagnosis — Path C কেন p20-কে REFUSE করল (সৎ flip)

p20-র লাইন ২: box `[557,661,986,678]` — **"BENEFICIARY/MANUFACTURER/EXPORTER/SHIPPER"** (৪ শব্দ, slash-জোড়া)। R22-তে এই লাইন ALLOW ছিল — কারণ R22-র T3 চোখ gap signal খুঁজতো, আর এখানে gap মাত্র **১px আর ২px** (maxgap 2px)। নতুন Path C gap দেখে না, fused-CC topology দেখে:
- ৩টি CC, প্রতিটি ১১৭–১৫৮px চওড়া — **8.4–11.3×med_h** (med_h ১৪-র পাতায় একটি letter ~১৪px; একটি CC ৮টির বেশি letter-এর সমান)।
- min_cc_w_med **8.36**, fus_cover **0.993** (fused union প্রায় পুরো box ঢাকে), longest zero-ink run ≤ 2px।
- Margin: target-এর min CC 8.36×med_h, নিকটতম non-target 1.55× — **2.0 boundary খালি interval [1.55, 8.36]-এ বসে, ৫.৪× margin** — R19-র 0.92 বা F=1.70-র মতো knife-edge নয় (§৬)।

**এটা regression নয় — R22-র চোখের অন্ধত্ব ধরা পড়েছে।** R22-তে p20 ALLOW ছিল কারণ চোখ এই collapse দেখতোই না; R23-তে চোখ ১০০% recall-এ পৌঁছে (৩৫/৩৫) এটাকে ধরেছে। T3-কে warn-only করে 24/1 রাখা যেত — সেটা হতো **অসততা** (R21-র মতো ভুল আর করা হবে না)।

**Segmenter কেন লাইনটি ঠিক করতে পারে না (এখনও):** count-driven cut পরীক্ষা করা হয়েছে — ৮টি cut চাই, কিন্তু **০টি ভালো valley** আছে (valley depth পুরো interleaved)। Gap threshold-ও চলে না (১–২px gap letter gap-এর সমান)। Round 24-র lead (§১০): greyscale bridge (EP0780782 — binary-তে মৃত gap greyscale-এ জীবিত থাকতে পারে) আর Lee & Oh minimum-cost seam (সাদা pixel দিয়ে বাঁকা seam)। দুটোই RESEARCH23-র source, এখনও পরীক্ষা হয়নি।

---

## ৪. p21-র stretch — প্রমাণিত known limit (কেন 25/0 হলো না)

বাকি ১টি T3 (Path B): p21 `[827,1970,1317,2005]` — **"three months before the date of expiry"** (৭ শব্দ, ১ box, line 31, maxgap 6px)।

p21stretch ট্র্যাক Otsu-CC piece split (Idea D) দিয়ে এটাকে **ঠিক ৭টি সত্য শব্দে** ভেঙেছিল, আরও ৬টি p21 merge-ও ঠিক করেছিল, ৬টি victim box অক্ষত ছিল — gate 25/0 হতো। কিন্তু একই পদ্ধতি পুরো পাতায় চালালে ২৪টি v2 split-এর মধ্যে **৯টি সঠিক, ১৫টি ভুল** — TRANSPORT→TRANS|PORT, consignor→con|signor, Ravi→R|av|i, ORIGINAL→ORIG|INAL, BENEFICIARY / EXPORTER / BANGLADESH / QUANTITY / PROFORMA / COATED-র টুকরো।

**কোনো signal আলাদা করে না** — মেপে দেখা হয়েছে: gap (সত্য word gap 5px, ভুল intra-word cut-ও 5px), bridge-strength, white-column (সব 1.0), min-cost seam, reservoir, dark/core sub-count ("the"=১ sub, "T"=১ sub — একই), piece width, uniformity — প্রতিটি মাপে সত্য আর ভুল overlap করে। নির্ণায়ক সত্য: **"TRANS"+"PORT" এক শব্দ — এটা letter sequence-এ আছে, CC structure-এ নেই।** শব্দের পরিচয় জানতে হলে অক্ষর চিনতে হয় — সেটা recognition, আর recognition (OCR/VLM) ব্যবহারকারীর নিষেধ। তাই এই stretch geometry-only toolset-এর **প্রমাণিত known limit** — R22-র profile re-split-এর মতোই (সেটাও ৬/৭ ঠিক করে ৬টি box over-split করেছিল)। Function রাখা হয়নি — শুধু rejected experiment হিসেবে ফাইল আছে, DO NOT PROMOTE / DO NOT MERGE চিহ্নিত।

**Round 24-র জন্য সৎ সিদ্ধান্ত (§১০):** হয় greyscale bridge / min-cost seam-এর মতো নতুন discriminator পরীক্ষা করা, নয়তো এই stretch-কে accepted known limit হিসেবে ঘোষণা করা — জোর করে ভাঙা যাবে না।

---

## ৫. p21 heading — এখনও unfixable (দুটি নতুন পদ্ধতিতেও)

p21 heading blob `[555,1082,1548,1119]` (৯৯৩×৩৭, fill 0.65) **underlined** — R22-তে FIX A প্রমাণিত unfixable ছিল (কোনো gap threshold চলে না)। R23-তে দুটি নতুন পদ্ধতি পরীক্ষা করা হয়েছে:

- **Bai & Huo ICPR 2004 + Amazon US 9,286,541** (Amazon patent Justia-তে পুরো পড়া হয়েছে)। Identification সফল: rule y1111–1114, row-ink 0.84–0.94; Otsu CC ১ = TOUCHED underline।
- **Removal ব্যর্থ — তিনভাবে মাপা:** (১) Amazon transition-count: dark 1-run column ৩৯৪ = pure-rule ১৪৬ + fused letter+rule ২৪৮ — দুটোই ঠিক ১ run, আলাদা করা যায় না। (২) Column-wise rule deletion: dark 30 CC ০/৮ শব্দ, Otsu ০ CC (pure column মাত্র ১/৯৯৩ — fringe ink সব ঢেকে দেয়), core-140 ৭ CC ১/৮ (৭৫২px mega-CC)। (৩) **নির্ণায়ক:** pure-column test word gap-এ ১০০% জ্বলে **আর** letter gap-এও ১০০% — এটা gap-width-ই আরেক রূপে, নতুন তথ্য নয়।

কোনো variant ফাইল বানানো হয়নি; baseline অক্ষত। একটি probe ভুল ধরা পড়ে ঠিক করা হয়েছে (pure-column count ৩৭৯ → সঠিক ১৬৪; ভুল সংখ্যায় কোনো সিদ্ধান্ত নেওয়া হয়নি)। Heading তাই **known limit** হিসেবেই থাকে — R22-র FIX A-র সঙ্গে একমত।

---

## ৬. T3 চোখ — recall 35/35 (100%), ০ false positive

R21-র চোখ ৮/৩০ ধরতো (R21 report-এর "৮/১১" অসম্পূর্ণ ছিল — §৯)। R22 Path A′ + Path B-তে ৩৪/৩৫ (৯৭%) হয়েছিল — একমাত্র miss p20-র fully-fused লাইন (maxgap 2px)। R23 Path C সেই miss-টাও ধরে:

- **Path C (fused-CC topology):** (i) কোনো letter-sized CC নেই (সব CC ≥ 2.0×med_h), (ii) fused union cover ≥ 0.5, (iii) longest zero-ink run ≤ 2px। পূর্ণ ৩৫-collapse set-এ **৩৫/৩৫ (১০০%)**, ০ false positive (১৬টি genuine control + ৩৩ পাতা × ২ seg set)।
- **Margin knife-edge নয়:** target min CC 8.36×med_h, নিকটতম non-target 1.55× — 2.0 boundary ৫.৪× margin-সহ খালি interval-এ। R19-র 0.92 (13/14=0.9286 বনাম 10/11=0.9091) বা F=1.70-র মতো fitted threshold নয়।
- **বাতিল signal (মেপে):** count-driven cut হিসেবে ০টি ভালো valley — কিন্তু REFUSE হিসেবে সঠিক (cut কম হলে "no valid segmentation" — US 5,253,304-র যুক্তি); bridge-strength overlap; white-column সব 1.0; reservoir pocket ratio target 8.0 বনাম genuine সর্বোচ্চ 3.0 — **কিন্তু** stamp-overlapped box 30.0, false positive দিত।
- **ফল:** gate-এ T3 flag এখন ২টি (p20 Path C + p21 Path B) — দুটোই আসল collapse, ০টি ভুল। চোখ এখন segmenter-এর চেয়ে কঠোর — এটাই সঠিক ক্রম: চোখ ধরবে, segmenter ঠিক করবে।

---

## ৭. E2 removal REVERTED — merge যাচাইয়ে ধরা পড়া regression (সবচেয়ে বড় শিক্ষা)

**সমস্যা:** প্রথম merge-এ (E2 removal-সহ) repo suite **35/38 FAIL** হয় — `test_aug_p1_canonical`, `test_page_counts_and_dpi`, `test_all_43` — তিনটিই একই কারণে: **Aug p1 ৩০৭ শব্দ, চাওয়া ৩০৮**।

**Diagnosis (প্রমাণিত, দুই ধাপে):**
1. **Port নির্দোষ:** merged segmenter-ও fitz render-এ ৩০৭ দেয়; R22 clone একই ছবিতে ৩০৮ দেয়। Regression merge-এই (Round 23 বদলে), port-এ নয়।
2. **দোষী E2 removal:** R22 বনাম R23 diff-এ Aug p1 fitz-এ ঠিক ১টি box বদলেছে — email blob `[967,415,1275,456]` ("pgfoils@pgfoils.in"): R22-তে ২ শব্দ `[970,417,1080,450]` + `[1122,418,1272,450]`; R23-তে ১টি fused box `[967,415,1275,456]`। Probe-এ নিশ্চিত: eroded split ২ শব্দ দেয়, কিন্তু **একটি** uneroded sub uncovered থাকে — `[1067,425,1080,446]`, w=13 h=21 ("gfoils"-এর "s"-এর লেজ; centre ৬১px word gap-এ, 1061 → 1122-র মাঝে)। পুরো Aug p1 fitz পাতায় এই একটিই ACCT-FAIL। R22-তে `_gap_mark` excuse এটাকে মাফ করতো (13px = 0.50×med_h, gap-বন্দি) → split accept → ৩০৮। R23-তে excuse নেই → split reject → uneroded retry ১ শব্দে collapse → ৩০৭। আর একটি fragment `[1175,417,1274,448]` overlapping হিসেবে drop হয়।

**কেন knife ট্র্যাক এটা ধরতে পারেনি:** তাদের "৩৩/৩৩ byte-identical segs" মাপটি শুধু **PNG render**-এর (merge pipeline input)। PNG-তে excuse-এর ৩টি firing-ই redundant ছিল (প্রতিটি split-এ অন্য uncovered sub-ও veto করত)। কিন্তু repo suite **fitz render**-এ segment করে — render drift (mean abs diff 1.56, 41.8% pixel ≥1 level) threshold-ঘেঁষা সিদ্ধান্ত উল্টে দেয়: fitz-এ ওই sub-এর centre gap-এ পড়ে, PNG-তে পড়ে না। Knife ট্র্যাকের নিজের report-এই সতর্কতা ছিল ("merge agent-কে চালিয়ে নিশ্চিত করতে হবে") — merge verification-ই ধরা পড়েছে। প্রক্রিয়াটা কাজ করেছে।

**Fix — E2 removal REVERTED (verbatim restore, নতুন নিয়ম নয়):** R21 `_gap_mark` হুবহু ফেরানো হয়েছে — merge script-এ (`merge_segment_r23.py` step 2, কারণসহ comment), repo clone-এ (`restore_gapmark_r23.py`, R21 version extract করে বসানো), আর port script-এ section 1 এখন verify-only (sections 2–4 skip-if-applied — script আবার চালানো যায়)। **ফল:** fitz Aug p1 আবার **৩০৮, box-গুলো R22-র সঙ্গে byte-identical**; ১৪টি PG পাতার সবগুলোতেই fitz-এ R22-র সঙ্গে **০টি box পার্থক্য**; PNG ৩৩ পাতার segs **byte-identical** (re-seg করে যাচাই — excuse ON/OFF-এ PNG-তে কিছুই বদলায় না, যেমন knife ট্র্যাক মেপেছিল); gate **23/2 অপরিবর্তিত**; canonical **হুবহু একই**; suite **38/38 PASS (413.34s)**।

**সংশোধন (knife ট্র্যাকের দাবিতে):** excuse-এর ভিত্তি-অনুমান ("সরু + gap-বন্দি টুকরো শব্দ হতে পারে না") এখনও ভুল — ৩/৩ PNG firing-ই letter piece ছিল, ০টি genuine gap mark। কিন্তু accounting নিজে একটি heuristic, আর এই sub-এর centre word gap-এ পড়ে বলে excuse-এর **প্রভাব** এখানে সঠিক। R21-র "@ ring" identification-ও ভুল ছিল — PNG render-এ ওটা "gfoils"-এর "s"। Track-knife report-এ correction section যোগ করা হয়েছে। **শিক্ষা (ভবিষ্যতের জন্য):** কোনো নিয়ম "কিছুই বদলায় না" দাবি করতে হলে **দুই render-ই** (PNG pipeline + fitz test render) যাচাই করতে হবে — এই শিক্ষা Round 24-এ যাবে।

---

## ৮. misses EXP2 — coverage সত্য 95/97 (সংশোধনসহ)

EXP2-র ৪টি patch (row-split uneroded retry + retry height guard + FIX F overhang + F3 swap) নেওয়া হয়েছে:
- **উদ্ধার (word identity-তে):** "gal" union 0.368 → 1.0, "by" 0.386 → 1.0, "on of Caution" 0.599 → 0.931; FOB row এখন ৫টি exact box (FOB/VALUE:/USD/56775/21); fused mega-blob `[544,1753,1111,1893]` নেই; শব্দ +13 (p01 +14, p22 −1)।
- **সৎ wart:** ২টি লাল stamp fragment fake word হিসেবে রয়ে গেছে; H.S.CODE/"7607.19.10" over-split; decimal-point split ("56775"+"21")। এগুলো EXP2-র দাম — লুকানো হয়নি।
- **সংশোধন — R22-র "92/97" ভুল ছিল, সত্য 95/97:** (১) "১০টি FOB/FREIGHT digit" আসলে লাল stamp fragment ছিল, digit নয় — সঠিকভাবেই drop থাকে; (২) centre-test-এর ৫টি "miss"-এর ৩টি আসলে miss নয় ("OR"-এর centre 3px gap-এ পড়ে, union 0.805; "Yours"/"faithfully," diagnosis box-এ signature scribble ঢুকে আছে)। সত্য coverage ছিল **95/97**, 92/97 নয়। এখনও missing ৫টি নয়, **২টি আসল + ৩টি known-limit**: CARRIER NAME লাইন (৮ শব্দ), p21 heading, p21 address লাইন (২৬ শব্দ ১৪ box-এ), p10 "Prepared" (geometry-only unfixable, §১), আর stamp fragment-গুলো (সঠিকভাবে drop)।
- **নেওয়া হয়নি:** count-driven cut (n estimate ১৩ বনাম সত্য ৮), address-line 2-means, p10 "Prepared"।
- **সতর্কতা:** `round16/track-a/scorer.py` দিয়ে EXP2 score করা যায়নি (তার `gt.json` round15c/16 seg path hardcode করে; বদলানো হতো test expectation বদলানো — নিষিদ্ধ); probe coverage + canonical + gate re-run করা হয়েছে তার বদলে।

---

## ৯. সংশোধন (corrections — আগের রিপোর্টের ভুল ঠিক করা)

1. **p21 GT 35/42 বনাম 36/42 — scorer-নিয়মের পার্থক্য, পরিবর্তন নয়:** R19–R22 report-এর 35/42 আর coordinator-এর scorer-এর 36/42 (@ ±5px, meet-rule) — দুটোই একই GT file (`round20/track-top2b/gt-p21.json`, ৪২টি certain boundary: L1648 ৯, L1926 ১৫, L2379 ১৮)। Coordinator-এর scorer-এ **R22 আর R23 দুটোতেই 36/42** (18/42 @ ±2–3px, 27/42 @ ±4px, 34/42 @ ±8px) — তাই কোনো regression নেই, সংখ্যার পার্থক্য scoring rule/tolerance-এর। 35/42 বনাম 36/42-কে পরিবর্তন হিসেবে উদ্ধৃত করা যাবে না।
2. **"১৪৩টি hidden miss" → আসলে বাকি ৫টির মতো:** R20-র ১৪৩ diagnosis-এর বেশিরভাগই footer (৫৩) আর single character (৮২) — EXP2-তে ৭৭টি উদ্ধার হয়েছে; বাকি coverage সত্য **95/97** (§৮) — R22-র "92/97" ভুল ছিল।
3. **T3 recall:** R21-র "৮/১১ (73%)" অসম্পূর্ণ ছিল — সত্য ছিল ৮/৩০ (R22-তে সংশোধন করা হয়েছে)। Round 23-তে পূর্ণ ৩৫-collapse set-এ recall **৩৫/৩৫ (১০০%)**।
4. **E2 removal বাতিল (§৭):** knife ট্র্যাকের PROMOTE সিদ্ধান্ত verification-এ বাতিল — excuse R21-র মতোই বহাল। R21-র "@ ring" identification-ও ভুল ছিল (PNG-তে ওটা "gfoils"-এর "s")।
5. **PG "identical counts" ≠ identical boxes:** R22 §৮-র শিক্ষা এই রাউন্ডে মানা হয়েছে — PNG segs byte-identical যাচাই করা হয়েছে (diff খালি), শুধু শব্দ-সংখ্যা মেলানো হয়নি; fitz render-ও ১৪ পাতায় box-identical যাচাই করা হয়েছে (§৭)।

---

## ১০. খোলা বিষয় (open items — Round 24-র জন্য)

1. **p20-র fused লাইন** (`[557,661,986,678]`, "BENEFICIARY/MANUFACTURER/EXPORTER/SHIPPER") — Path C ধরে, segmenter ঠিক করতে পারেনি। Lead: greyscale bridge (EP0780782) আর Lee & Oh minimum-cost seam (RESEARCH23.md) — count-driven cut প্রমাণিতভাবে ০ ভালো valley দেয়, তাই আর চালানো যাবে না।
2. **p21-র ৭-শব্দ stretch** — প্রমাণিত known limit (§৪)। Round 24-র সিদ্ধান্ত: নতুন discriminator (greyscale bridge / seam) পরীক্ষা করা, নাহলে accepted known limit হিসেবে ঘোষণা করা — জোর করে ভাঙা যাবে না।
3. **p21 heading** (৮ শব্দ, underlined — §৫) আর **p21 address লাইন** (২৬ শব্দ ১৪ box-এ) আর **p01 CARRIER NAME লাইন** (৮ শব্দ) আর **p10 "Prepared"** — geometry-only unfixable-র তালিকা।
4. **Knife-edge-গুলো:** F=1.70, FIX3 3px run floor (n=1), floor-4 (genuine-min 77px, window [2,77]) — principled নিয়মে বদলানো যায়নি, মাপা আছে। E2 width boundary এখন আর knife-edge নয় — excuse বহাল আছে।
5. **আগের মতো খোলা:** Virtako label ৫-field decision (user-এর উত্তর অপেক্ষায় — শীঘ্রই আবার জিজ্ঞেস করবে না); Q-03–Q-09, ★2–★8; print calibration (factory printer — শুধু user, Muse-র কাজ শেষে); US patent legal check (lawyer — lead: US 5,734,761 + Adobe US9741142B2 + US 20250111688 + US 20250078557); Windows .exe (Windows-এ build করতে হবে); .docx capture 100/100 (৯৬.৬০% এখন); first-view ~১৪–১৮s।

---

## ১১. যাচাই (verification — parent-এর জন্য)

- **Merge:** `merge-r23/segment_merged.py` + `gate_merged.py` + `rhythm_dp.py` + `logo_detect.py` + `gate_misses.py` + `segs/` (৩৩ পাতা) + `gate_batch_r23_merged.json` + `canon_r23_merged.json` + `merge_segment_r23.py` + `port_segment_r23.py` + `port_gate_r23.py` + `restore_gapmark_r23.py`। `segs/` backup `/tmp/segs_r23_backup`-এর সঙ্গে **byte-identical** (fix-এর পরে re-seg করে যাচাই)।
- **Gate:** 23/2 (২৫ পাতা); ৩১ ALLOW / ২ REFUSE (৩৩ entry)। REFUSE: p20 (T3 Path C, box `[557,661,986,678]`, min_cc_w_med 8.36, fus_cover 0.993) আর p21 (T3 Path B, box `[827,1970,1317,2005]`)। T1 ০, T2 ০। ২৩টি পুরনো ALLOW পাতার একটিও regress হয়নি।
- **শব্দ:** ২৫ পাতা 9373 (p01 +14, p22 −1, বাকি অপরিবর্তিত); ৩৩ পাতা 12366; p2 ৬৭৬, p3 ৪৭১; p20 ৫২১ (=), p21 ৫৮৪ (=)।
- **Canonical:** N5 **41/81** (=), Description ভুল **৩০** (একই list), redbox **7/66** (=), p3 strict **248/384**, improved **285/384**, FP 186, p21 GT **36/42** @ ±5px meet-rule (§৯), LINES **327/327** (merge verification-এ rescore; fix-এর পরে segs byte-identical বলে অপরিবর্তিত)।
- **Guard:** **5/5 PASS** (merge verification; segs byte-identical বলে অপরিবর্তিত)।
- **DB SHA:** `1c065457bb9cb8e5b276d5007d9b020c18c8a0ae0374b92eb759f12150746939` — আগে ও শেষে একই (DB ছোঁয়া হয়নি)।
- **Full suite (repo clone `~/workspace/lse-r23-test/`):** প্রথম run **35/38 FAIL** (381.15s — ৩টি fail, সব একই হারানো শব্দ); E2 revert-এর পরে **38/38 PASS (413.34s, exit 0)**। Aug p1 IoU-matched ≥২৮৫, May p1 ≥২৯০ (suite-র নিজের threshold)। Demo ৮২ শব্দ। Aug p1 PNG ৩০৬ / fitz ৩০৮।
- **Port:** `port_segment_r23.py` (re-run: ৮টি check, সব PASS — section 1 এখন verify-only, sections 2–4 skip-if-applied) + `port_gate_r23.py` (৯টি check, সব PASS) + `restore_gapmark_r23.py` (৭টি check, সব PASS); compile OK। Repo segmenter merged segmenter-এর সঙ্গে PG পাতায় box-identical (fitz ১৪ পাতা + PNG ৩৩ পাতা, দুটোতেই যাচাই)।
- **Push করা হয়নি, Drive-এ upload করা হয়নি, MEMORY.md ছোঁয়া হয়নি** — parent যাচাই করে push/upload/memory করবে। **Push সিদ্ধান্ত parent-এর:** gate সংখ্যায় 23/2 (R22-র 24/1-র চেয়ে কম) — কিন্তু কমতিটা সৎ ধরা (Path C), আর suite 38/38; R23 push করা হবে কিনা (সৎ চোখ + EXP2 উদ্ধারের জন্য) নাকি Round 24 পর্যন্ত রাখা হবে — সেটা reversible working decision হিসেবে parent-এর হাতে।

---

## ১২. উদ্ভাবন বনাম মেরামত (purpose check — ব্যবহারকারীর নির্দেশ)

এই রাউন্ডের **উদ্ভাবন:** T3-র Path C (fused-CC topology — gap signal ছাড়া collapse ধরা, ১০০% recall, ৫.৪× margin — knife-edge নয়), EXP2-র row-split uneroded retry (erosion-এ নষ্ট হওয়া subs uneroded-এ ফিরিয়ে উদ্ধার করা), আর online research-এর greyscale/count-driven/min-cost-seam lead-গুলো। **মেরামত:** E2 removal বাতিল করে R21 excuse ফেরানো, port script bug ঠিক করা, p21 stretch/heading-কে known limit হিসেবে সৎ স্বীকার। সৎ মূল্যায়ন: Path C আর EXP2 আসল নতুন technology; E2 revert মেরামত — কিন্তু মেরামতটাও প্রমাণ-ভিত্তিক (probe-এ একটিই uncovered sub, দুই render-এ যাচাই, suite 35/38 → 38/38)। আর সবচেয়ে বড় উদ্ভাবন নয়, সবচেয়ে বড় **শিক্ষা**: "কিছুই বদলায় না" দাবি করতে হলে দুই render-ই যাচাই করতে হবে — এই শিক্ষাটাই Round 24-কে আরও সৎ করবে।
