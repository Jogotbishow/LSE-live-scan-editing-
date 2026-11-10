# LSE Round 21 — রিপোর্ট

**তারিখ:** 2026-11-09 · **ভাষা:** বাংলা · **মার্জ এজেন্ট:** Round 21 merge agent
**Baseline:** Round 20 merged segmenter + gate (`round20/merge-r20/`, gate 23/2) — read-only, ভাঙা হয়নি
**নতুন baseline:** `improve/round21/merge-r21/` (segment_merged.py + gate_merged.py + rhythm_dp.py + logo_detect.py + segs/)
**ডিরেক্টরি:** `improve/round21/` — প্রতি ট্র্যাকের নিজের ডিরেক্টরিতে তার সব আউটপুট; merge `merge-r21/`-তে
**নির্দেশ:** ব্যবহারকারীর LSE 100% নিয়ম (2026-11-08 22:42) — Muse নিজে 100% সন্তুষ্ট না হওয়া পর্যন্ত LSE-র কাজ থামবে না; কোনো অনুমতি লাগবে না। এই রাউন্ড সেই নির্দেশেই চলেছে।

> **সৎ সারাংশ:** Gate 23/2 → **24/1**। p01 ও p12 — R20-র শেষ ২টি REFUSE — দুটোই ALLOW হয়েছে। কিন্তু নতুন T3 চোখ p20-র ৮টি আসল whole-line collapse ধরে ফেলেছে, তাই p20 এখন REFUSE। 25/0 হয়নি — কারণ p20-র collapse-গুলো আসল, লুকানো হয়নি। এই রিপোর্টে সেটাই সৎভাবে বলা হয়েছে: gate এখন আগের চেয়ে **আরও সৎ** (আগে অদৃশ্য থাকা ত্রুটি এখন ধরা পড়ে), আর p20-র collapse ঠিক করাই Round 22-র কাজ।

---

## ০. এক নজরে — headline সংখ্যা

| মাপ | R20 baseline | **Round 21 merge** |
|---|---:|---:|
| Gate (২৫ Raviraj পাতা) | 23 ALLOW / 2 REFUSE | **24 ALLOW / 1 REFUSE** |
| ফ্ল্যাগ (T1 / T2 / T3) | 2 (2 / 0 / —) | **8 (0 / 0 / 8)** |
| মোট শব্দ (২৫ পাতা) | 9100 | **9101 (+1)** |
| REFUSE পাতা | p01, p12 | **শুধু p20** |
| Canonical p2 N5 / Description / redbox | 40/81, 39/69, 7/66 | **40/81 (=), 39/69 (=), 7/66 (=)** |
| Canonical p3 strict / improved (FP) | 248 / 285 (186) | **248 (=) / 285 (=) (186, =)** |
| Canonical p2 / p3 gate | p2 REFUSE (T2=2), p3 ALLOW | p2 REFUSE (T2=2, by design), p3 ALLOW |
| LINES (canonical r15m) | 327/327 | **327/327** |
| PG ৬ পাতা (শব্দ) | aug 306/308/305, may 308/313/306 | **aug 306/308/305, may 308/313/306 — হুবহু একই (0 removed / 0 added)** |
| p21 GT (৪২ certain boundary) | 35/42 | **35/42 (=)** |
| Guard (live page, FULL) | 5/5 | **5/5 PASS** |
| Round 3 DB SHA | `1c065457…` | **`1c065457…` — আগে ও শেষে একই** |
| Full suite (repo test clone) | 38/38 | **38/38 PASS (0 fail, 0 error, 0 skip)** |
| Demo (synthetic) | 82 শব্দ | **82 শব্দ (=)** |
| Aug p1 শব্দ-সংখ্যা | PNG 306 / fitz 308 | **PNG 306 / fitz 308 — দুই render-পথেই সঠিক** |

**ফ্লিপ (REFUSE→ALLOW):** p01 (row-split fix), p12 (v5 release + floor-4) — ২টি পাতা।
**ফ্লিপ (ALLOW→REFUSE):** p20 (T3 — ৮টি আসল whole-line collapse, R20 baseline-এই ছিল, gate আগে দেখতো না)।
২২টি পুরনো ALLOW পাতার একটিও regress হয়নি। **বাকি ১টি REFUSE:** p20 — T3 ৮টি collapse (§৩ দেখুন)।

**Promotion bar-এর রায়: পাস — তবে 25/0 নয়।** p01+p12 ঠিক হয়েছে, canonical-এ কোনো regression নেই
(LINES 327/327; N5 =, Description =, redbox =, p3 =/=), suite 38/38। কিন্তু p20-র ৮টি collapse
আসল — T3-কে warn-only করে 25/0 দেখানো হতো **অসততা**। Gate এখন আরও কঠোর ও সৎ: R20-তে অদৃশ্য
ত্রুটি এখন ধরা পড়ে। p20-র collapse ঠিক করা Round 22-র কাজ (§৮)।

---

## ১. ট্র্যাক verdicts — ৬টি ট্র্যাক, সব DONE

| ট্র্যাক | verdict | মূল ফল |
|---|---|---|
| **track-p01** | **PROMOTE** | row-split fix: `_cluster_rows` single-linkage (আগের sub-র centre-র সঙ্গে তুলনা, running mean নয়)। gate 23/2 → 24/1 (p01 ALLOW)। শুধু ২টি box বদলেছে (p01 + canonical p2 tagline "Nothing")। শব্দ 12067 → 12067 (Δ0)। canonical অপরিবর্তিত। suite 38/38। |
| **track-p12** | **PROMOTE-able** | v5 segmenter (attach-only release: narrow piece → পাশের শব্দের box বাড়ায়, wide piece → নিজের box) + gate-এ `MIN_CORE_ASSIGN_PX = 4` floor। gate 23/2 → 24/1 (p12 ALLOW)। p12 T1max 0.970 → **0.106**। শব্দ 9100 → 9101 (+1, p11-র নতুন "By")। v4 injection বাতিল (p10 ভেঙেছিল, p09-র "Prepared" ১→৩ করেছিল)। |
| **track-subcov** | **PROMOTE E2** | 0.92 threshold **বাতিল** — E2 gap-mark rule দিয়ে বদল: split বৈধ iff প্রতিটি uneroded sub accounted — word box-এ ঢাকা, অথবা gap mark (দুটি word box-র মাঝে, x-overlap 0, একই text line, ≤0.5×med_h চওড়া)। আর কোনো tuned fraction নেই। 33/33 পাতা merge-r20-র সঙ্গে box-identical, gate 23/2 অপরিবর্তিত। |
| **track-misses** | **নেওয়া হয়নি** | coverage probe 62/97 → 93/97, শব্দ +106, canonical N5 41/81, p3 249/286 — কিন্তু p21 heading-এ **৩টি over-split** (Review → "Rev"+"iew of" ইত্যাদি), orphan path কখনো exercised হয়নি, gate 23/2 অপরিবর্তিত। §৪ দেখুন। |
| **track-gate** | **PROMOTE T3** | নতুন T3 whole-line-collapse চোখ + `check_dp_integrity` pre-flight (rhythm_dp.py না থাকলে gate abort, rc=3 — R20 §11.b-র শিক্ষা)। T3 p20-কে ALLOW→REFUSE করে (৮টি আসল collapse)। 33 পাতায় **০টি false positive**। |
| **track-online** | গবেষণা (কোড নয়) | RESEARCH21.md: (1) joint-probability + per-line two-cluster (threshold-এর বদলে); (2) ছোট CC ফেলার আগে neighbour-check (i-dot বাঁচে); (3) layered gate checklist + foreground-ink accounting। দাবির ভাষা আগের মতো: "no recognition at all — neither OCR nor VLM; geometry only"। |

---

## ২. merge — কীভাবে তিনটি fix এক করা হলো

**নেওয়া হয়েছে:** p01 (row-split) + p12 v5 (release) + subcov E2 (gap-mark) + gate T3 + floor-4।
**নেওয়া হয়নি:** misses ABCDE6 (§৪)।

মার্জ-প্রক্রিয়া (পুনরুৎপাদনযোগ্য — স্ক্রিপ্ট `improve/round21/`-তে রাখা আছে):
- `merge_segment.py` — তিনটি fix-কে track-ফাইল থেকে exact-string replacement-এ `merge-r21/segment_merged.py`-তে বসায়, প্রতিটি ঠিক ১ বার মিলিয়ে যাচাই করে। ফল: 54,988 → 65,220 chars (+10,232)। compile OK।
- `merge_gate.py` — T3 block + floor-কে `merge-r21/gate_merged.py`-তে বসায়। ফল: 23,463 → 34,265 chars (+10,802)। compile OK।
- যাচাই: `diff` দিয়ে দেখা হয়েছে merge-r21-তে তিনটি track-এর fix-ই আছে, আর কোনো track-এর সঙ্গে diff-এ শুধু অন্য track-গুলোর fix-ই দেখা যায় (অর্থাৎ কোনো fix হারায়নি, কোনো অতিরিক্ত বদল নেই)।
- R19/R20 fix-গুলো অক্ষত আছে (grep দিয়ে যাচাই): eroded positive-gap median, "@" gap-position rule, eroded subs for extension + fallback।

**Repo test clone-এ port:** suite চালাতে R21 fix-গুলো repo-র `lse/segment.py` ও `lse/gate.py`-তেও port করা হয়েছে
(`~/workspace/lse-r21-test/`, স্ক্রিপ্ট `port_segment.py` + `port_gate.py`)। Repo-র segmenter nested
(`segment_array`-র ভিতরে, 4-space indent) বলে re-indent করে port করা হয়েছে; gate top-level বলে সরাসরি।
rhythm_dp.py ও logo_detect.py merge-r21 আর repo-তে হুবহু একই (diff শূন্য)। Demo-তে port করা segmenter
৮২ শব্দ দেয় (= R20)।

**Segmenter merge-এর anchor (ভবিষ্যতের জন্য):**
- p01: `_cluster_rows` — comparison লাইন: `_cy(_s) - _cy(_cur[-1]) <= row_gap`; `_mean` update সরানো।
- subcov E2: `_gap_mark` + `_all_subs_accounted` — `_reclaim_core`-র ঠিক আগে; validation লাইন এখন
  `ok = _all_subs_accounted(subs_u, words, x0, y0)` (0.92 আর কোথাও validation-এ নেই)।
- p12v5: release block — strip-`_comps` loop-এর পরে, `print(f"words segmented: ...")`-র আগে; script body-র
  top-level block (কোনো function-এর ভিতরে নয়)।

---

## ৩. সিদ্ধান্ত ১ — p20: T3 REFUSE রাখা হলো (24/1), warn-only নয়

**মাপা ফল (merged segmenter + merged gate, `gate_batch_r21_merged.json`):**
p20 verdict REFUSE, T1 0, T2 0, **T3 8**। ৮টি collapse-র বিবরণ:

| box | line_ratio | line-এ শব্দ | max internal gap |
|---|---|---:|---:|
| [1320,1031,1812,1048] | 0.80 | 2 | 8px |
| [1310,1059,1709,1076] | 0.78 | 2 | 7px |
| [1234,1320,1475,1337] | 1.00 | 1 | 8px |
| [1701,1846,1955,1863] | 0.61 | 2 | 6px |
| [771,1919,1574,1939] | 0.93 | 2 | 8px |
| [537,2188,1325,2207] | 0.58 | 2 | 8px |
| [535,2215,1025,2236] | 1.00 | 1 | 7px |
| [1164,2333,1468,2351] | 1.00 | 1 | 7px |

সবগুলোই চওড়া box (line-র 58–100% জুড়ে), line-এ মাত্র ১–২টি শব্দ, ভিতরে ৬–৮px ফাঁক —
অর্থাৎ একাধিক শব্দ এক box-এ জোড়া লেগে আছে। **৮টিই আসল collapse, gate-র artifact নয়।**
track-gate-ও একই ৮টি চোখে যাচাই করে ০টি false positive পেয়েছিল (৩৩ পাতায়)।

**কেন REFUSE, warn-only নয়:**
1. Segmenter fix-গুলো p20-র collapse কমায়নি — p20-র শব্দ 365 (= R20), ৮টি T3 flag-ই রয়ে গেছে।
2. T3-কে warn-only করলে gate 25/0 দেখাতো, কিন্তু p20-র ৮টি ভাঙা লাইন লুকানো থাকতো। সেটা সংখ্যা
   সুন্দর করা, সঠিকতা নয়। ব্যবহারকারীর নিয়ম — "Muse নিজে 100% সন্তুষ্ট না হওয়া পর্যন্ত" — সংখ্যা
   নয়, সঠিকতাই চায়।
3. T3 একটি **নতুন ক্ষমতা**, gate ভাঙা নয়। R20-র শিক্ষা (§11.b): gate whole-line collapse-এ অন্ধ ছিল।
   এখন gate সেই ত্রুটি ধরে — এটা gate-র উন্নতি, অবনতি নয়। p20-র collapse segmenter-র সমস্যা,
   gate-র নয়। ঠিক করতে হবে segmenter-কে (Round 22), gate-কে দুর্বল করে নয়।
4. T3-র recall সীমা সৎভাবে নোট করা আছে: চোখে-যাচাই করা p20 multi-word box-এ 8/11 (73%) ধরে;
   line-এ ≥৩ শব্দ থাকলে বা maxgap 5px হলে ধরে না। 1px margin (আসল 5px বনাম flagged 6px) —
   মাপা gap, নীতি থেকে আসা নয়।

**ফল:** gate **24/1** (শুধু p20 REFUSE)। ২২টি পুরনো ALLOW পাতা সব ALLOW-ই আছে; p01, p12 ALLOW হয়েছে।

---

## ৪. সিদ্ধান্ত ২ — misses ABCDE6 নেওয়া হয়নি

**Track-র মাপা ফল (নেওয়া হলে যা হতো):** coverage probe 62/97 → 93/97; শব্দ 12067 → 12173 (+106);
gate 23/2 অপরিবর্তিত; canonical p2 N5 40→**41/81**, p3 strict 248→**249** / improved 285→**286**;
Aug p1 308; suite 38/38।

**তবু নেওয়া হয়নি — কারণ:**
1. **৩টি over-split (আসল regression):** FIX A (giant-blob fill-aware rescue) p21-র heading-এ ৩টি শব্দ
   ভেঙে ফেলে — Review → "Rev"+"iew of", Recommendation → "Recom"+"mendation",
   Operators → "O"+"perato"+"rs"। চোখে দেখলে ভাঙা মনে হয়। ১০৬টি শব্দ পেতে ৩টি সঠিক শব্দ
   ভাঙা — লেনদেনটি খারাপ।
2. **Gate-এ কোনো উন্নতি নেই** (23/2 অপরিবর্তিত) — অর্থাৎ +106 শব্দের বেশিরভাগই gate-র চোখে
   পড়া ত্রুটি ঠিক করে না (footer/digit-ই বেশি)।
3. **Orphan path কখনো exercised হয়নি** (FIX C-তে orphan 0) — অর্থাৎ code-র একটা পথ পরীক্ষিতই নয়।
4. Canonical লাভ ছোট (+1 শব্দ করে) — over-split-এর দামের তুলনায় কম।

**তবে কাজটি ফেলে দেওয়া হয়নি:** FIX B–E (2D footer pass, comp-coverage, frag gap-attach, F3 failed-row-split
blocker) over-split করে না; শুধু FIX A-ই করে। Round 22-র কাজ: FIX A-কে ঠিক করে (heading-এ over-split
না করে) B–E-সহ আবার promote করা। Misses-র ফাইল `track-misses/segment_misses.py` (= `variants/segment_ABCDE6.py`)-তে আছে।

**লুকানো miss-এর হিসাব (সংশোধন):** R20 রিপোর্টের "১৪৩টি" R19 segmenter-র বিপরীতে মাপা ছিল। R20-র
বিপরীতে ৬২টি আগেই covered (reclaim2c), তাই **আসল বাকি ৮১টি** — misses track তার ৭৭টি উদ্ধার
করেছিল (পুরোপুরি বা আংশিক)। Merge-এ misses না নেওয়ায় সেই **৮১টি এখনো বাকি** (probe-এ ৪টি এখনো
missing)। এখনো ঠিক হয়নি (সৎ তালিকা): p01 CARRIER NAME লাইন ৮ শব্দ (stamp-এ জোড়া); p01 "OR"
(union 0.81, centre-test artifact); p01-র ১০টি FOB/FREIGHT digit (saturated ink, কালো "USD"
থেকে 126px দূরে — 2×med_h = 40px chain gap-এর বাইরে); p21 heading over-split (৩টি, misses-র);
p21 address লাইন (২৬ শব্দের ink ১৪টি box-এ)।

---

## ৫. Aug p1 শব্দ-সংখ্যা — দুই render-পথ

| render পথ | Aug p1 শব্দ | মন্তব্য |
|---|---:|---|
| Prototype PNG (৩৩ পাতার run) | **306** | track-p01/subcov-র মাপের সঙ্গে মিলেছে। 308 হলো Aug p2-র সংখ্যা, p1-র নয়। |
| Fitz render (repo suite-র পথ) | **308** | `test_aug_p1_canonical` PASSED — expectation 308 সঠিক। |

দুটোই সঠিক — render-এর ১–২px পার্থক্যে (render drift) eroded subs বদলে যায়, তাই একই কোড
একই পাতায় দুই পথে দুই সংখ্যা দেয়। **Test expectation বদলানো হয়নি** (308 fitz-এ সঠিক)।
Segmenter-কে দুই পথেই সঠিক হতে হয় — এই কারণেই শুধু PNG-পাতায় যাচাই যথেষ্ট নয়, repo suite-ও
(fitz render) যাচাই করা হয়েছে (§৯)।

---

## ৬. merge-এ ধরা সমস্যা

1. **Gate merge-এ আমার নিজের check-টি ভুল ছিল, merge ঠিক ছিল:** `merge_gate.py`-র শেষ check
   (`assign_cores`-এর count == 1) FAIL করেছিল — কারণ `_assign_cores_min` wrapper-র ভিতরে নিজেই
   আসল `assign_cores`-কে ডাকে, তাই count ২ হয় (full_page_mask + wrapper-র ভিতর)। Merge ঠিক ছিল;
   check-টি wrapper-র ভিতরের call গোনেনি। সরাসরি যাচাই করে দেখা গেছে: full_page_mask আসল
   `assign_cores` ব্যবহার করে (inpaint path অপরিবর্তিত), gate() ও calibrate() floor ব্যবহার করে।
   Check ঠিক করে আবার চালানো হয়েছে — সব PASS।
2. **Repo port-এ nested-function extract-এর ভুল:** প্রথম port-এ `extract_function` top-level `def`
   খুঁজেছিল, কিন্তু repo-র function-গুলো nested (4-space indent) — ফলে `_cluster_rows` extract
   করতে গিয়ে ফাইলের বিরাট অংশ ধরে ফেলেছিল। ধরা পড়েছে p12 anchor count check-এ (write-র আগে,
   ফাইল নষ্ট হয়নি)। `extract_nested_function` লিখে ঠিক করা হয়েছে; port আবার চালিয়ে সব check PASS।
3. **R20-র দুটি পুরনো সমস্যা merge-এ আবার ধরা পড়েনি — কারণ এবার সতর্ক ছিলাম:** (a) R20-র
   merge-এ সব track pre-fix copy থেকে বানানো হয়েছিল (R19-র দুটি fix missing ছিল) — এবার merge-র
   আগে grep দিয়ে যাচাই করা হয়েছে R19/R20 fix-গুলো merge-r21-তে আছে; (b) R20-তে rhythm_dp.py
   missing ছিল আর gate তা ধরতে পারেনি — এবার `check_dp_integrity` pre-flight আছে, আর merge-r21-তে
   rhythm_dp.py আছে (diff শূন্য, repo-র সঙ্গে identical)।

---

## ৭. নির্ণয় ও সংশোধন

- **0.92 threshold — বাতিল, বদল E2:** R19-র 0.92 ছিল মাপা knife-edge (সঠিক email split 13/14=0.9286
  বনাম ভুল p16 split 10/11=0.9091) — নীতি থেকে আসা নয়, evidence-এ tune করা। E2 gap-mark rule-এ
  আর কোনো tuned fraction নেই: split বৈধ iff প্রতিটি uneroded sub accounted (word box-এ ঢাকা, অথবা
  gap mark: দুটি word box-র মাঝে, x-overlap 0, একই line, ≤0.5×med_h)। 0.5×med_h pipeline-র নিজের
  পুরনো constant, নতুন নয়। অবশিষ্ট fragility: width boundary পিক্সেলে পাতলা — p21-র letter fragment
  0.536×med_h বনাম cutoff 0.50 (~1px)।
- **R20 রিপোর্টের "p01 T1 0.542" ভুল — আসল 0.554** (track-p01 মেপেছে)। এই রাউন্ডে p01 T1max
  **0.475** (ALLOW; threshold 0.50-র নিচে)।
- **Aug p1 = 306 (PNG), 308 (fitz)** — R20 রিপোর্টের "aug 306" PNG-পথে সঠিক; 308 শুধু fitz-এ।
  দুটো সংখ্যাই এই রিপোর্টে স্পষ্ট করে দেওয়া হয়েছে (§৫)।
- **"১৪৩টি লুকানো miss" — সংশোধন:** R19-র বিপরীতে মাপা; R20-র বিপরীতে আসল বাকি ৮১টি (§৪)।
- **p12-র ২টি hidden miss ("5", "0") এখনো missing; p10-র "Prepared" এখনো দুটি box** — v5-র
  সীমা, সৎভাবে নোট করা আছে।
- **Floor-4-র evidence n=1-ভিত্তিক:** ৩৩ পাতায় মাপা খালি interval [2,7]-এ বসে (grazing 1px বনাম
  আসল 8px) — মাপা, নীতি থেকে আসা নয়। ভবিষ্যতে অন্য পাতায় ভিন্ন হতে পারে।

---

## ৮. খোলা বিষয় (Round 22-র কাজ)

1. **p20-র ৮টি whole-line collapse ঠিক করা** — segmenter-র কাজ (T3 এখন ধরে, ঠিক করে না)।
   misses-র FIX A-কে ঠিক করে B–E-সহ promote করলে p20 +4 শব্দ পেতে পারে, কিন্তু T3 collapse
   কমবে কিনা মেপে দেখতে হবে।
2. **misses ABCDE6-র FIX A ঠিক করে আবার promote** — heading over-split (৩টি) না করে।
3. **লুকানো miss ৮১টি** — footer blind spot, একক অক্ষর, p21 heading/address (§৪)।
4. **T3 recall 8/11 (73%)** — line-এ ≥৩ শব্দ থাকলে বা maxgap 5px হলে ধরে না; 1px margin।
5. **p12-র "5", "0" ও p10-র "Prepared"** — এখনো ঠিক হয়নি।
6. **E2 width boundary (~1px)** — p21 fragment 0.536×med_h বনাম cutoff 0.50।
7. **Floor-4 n=1 evidence** — আরও পাতায় যাচাই দরকার।
8. আগের খোলা বিষয়গুলো অপরিবর্তিত: Virtako label ৫টি field (ব্যবহারকারীর সিদ্ধান্ত বাকি),
   Windows .exe, print calibration, patent check (আইনজীবী — US 5,734,761 + Adobe US9741142B2 +
   US 20250111688 + US 20250078557), .docx 100/100, first-view ~14–18s, Q-03–Q-09 / ★2–★8।

---

## ৯. যাচাই — সব নিজে চালানো হয়েছে

| যাচাই | ফল |
|---|---|
| Full suite (repo test clone `~/workspace/lse-r21-test/`, TMPDIR workspace) | **38/38 PASS** (0 fail, 0 error, 0 skip) — ~৬.৫ মিনিট |
| Raviraj gate (merged run_segs + run_gate, ৩৩ পাতা) | **24/1** — p01 ALLOW (T1 0.475), p12 ALLOW (T1 0.106), p20 REFUSE (T3 8); T1 0, T2 0, T3 8 |
| Canonical p2/p3 (score_canon.py) | N5 40/81, Description 39/69 (30 wrong), redbox 7/66, p3 248/285 — **কোনো regression নেই** |
| p21 GT (score_p21_seg.py) | **35/42 (=)** |
| LINES | **327/327** — "Nothing's"-র ৩টি verdict box-ই fixed p2 seg-এ হুবহু আছে |
| Guard (live page, FULL, ৫ পাতা) | **5/5 PASS** |
| Demo (synthetic, port করা segmenter) | **82 শব্দ (=)** |
| Aug p1 দুই render-পথ | PNG 306, fitz 308 (§৫) |
| Round 3 DB SHA | `1c065457bb9cb8e5b276d5007d9b020c18c8a0ae0374b92eb759f12150746939` — আগে ও শেষে একই |
| পুরনো ALLOW পাতা | ২২টি সব ALLOW-ই আছে; p20 T3-তে REFUSE (§৩) |
| PG ৬ পাতা | হুবহু একই (0 removed / 0 added) |

**নতুন baseline:** `improve/round21/merge-r21/` — segment_merged.py, gate_merged.py, rhythm_dp.py,
logo_detect.py, run_segs_r21.py, run_gate_r21.py, segs/ (৩৩ পাতা), gate_batch_r21_merged.json,
canon_r21_merged.json, score_canon.py।

**Repo-তে push করা হয়নি, Drive-এ upload করা হয়নি, MEMORY.md ছোঁয়া হয়নি** — নির্দেশ অনুযায়ী।
Push-এর আগে ব্যবহারকারীর সিদ্ধান্ত দরকার: p20 REFUSE-সহ 24/1 push করবেন, নাকি Round 22-তে p20
ঠিক করে তারপর push করবেন।

---

*— Round 21 merge agent, 2026-11-09। বন্ধু হিসেবে সৎ কথা: LSE এখনো 100% নয় — p20-র ৮টি লাইন
ভাঙা আছে, আর ৮১টি লুকানো miss বাকি। কিন্তু gate এখন আগের চেয়ে সৎ, আর p01/p12 — R20-র শেষ
দুটি REFUSE — ঠিক হয়েছে। 25/0-র জন্য Round 22-তে p20-র collapse ঠিক করতে হবে।*
