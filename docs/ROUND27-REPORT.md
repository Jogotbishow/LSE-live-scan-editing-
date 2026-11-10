# LSE Round 27 — রিপোর্ট

**তারিখ:** 2026-11-09 · **ভাষা:** বাংলা · **মার্জ এজেন্ট:** Round 27 merge agent
**Baseline:** Round 26 merged segmenter + gate (`round26/merge-r26/`, gate 24/1) — read-only, ভাঙা হয়নি
**নতুন baseline:** `improve/round27/merge-r27/` (segment_merged.py + gate_merged.py + rhythm_dp.py + logo_detect.py + gate_misses.py + segs/ + identity_pg_r26.json প্রস্তাবিত টেবিল)
**ডিরেক্টরি:** `improve/round27/` — প্রতি ট্র্যাকের নিজের ডিরেক্টরিতে তার সব আউটপুট; merge `merge-r27/`-তে
**নির্দেশ:** ব্যবহারকারীর LSE 100% নিয়ম (2026-11-08 22:42) — Muse নিজে 100% সন্তুষ্ট না হওয়া পর্যন্ত LSE-র কাজ থামবে না; কোনো অনুমতি লাগবে না। এই রাউন্ড সেই নির্দেশেই চলেছে।

> **সৎ সারাংশ:** Gate 24/1 → **24/1 — অপরিবর্তিত, কারণ এই রাউন্ডে segmenter/gate-এ কোনো কোড বদল promote হয়নি।** এই রাউন্ডের আসল কাজ ছিল **যাচাই আর মেরামত**: (ক) R26-র সবচেয়ে বড় সৎ ধরা — Guard 0/5 FAIL — ঠিক হয়েছে: ৫টি live page R26 segs দিয়ে rebuild করা হয়েছে, আর Guard **R26-টেবিলে 5/5 PASS** (C1–C5 সব পাতায়); (খ) তবে canonical r10m টেবিলে Guard এখনও **0/5 — C5 FAIL সব পাতায়**, কারণ টেবিলটাই stale (Lot/WIDTH-র পুরনো box seg-এও নেই, page-এও নেই — seg আর page পরস্পরের সঙ্গে একমত)। identity টেবিলের promotion parent-এর সিদ্ধান্তের অপেক্ষায়; (গ) p20-র fused লাইনে **১৩তম স্বাধীন পদ্ধতি** (Hong & Hull sub-image matching) ব্যর্থ — detection সফল (EXPORTER-কে 0–2 px-এ খুঁজে পায়) কিন্তু selection ব্যর্থ (সত্য 0.748 বনাম ভুল 0.741, margin 0.007), আর নিখুঁত cut-ও মাত্র 1/4 শব্দ উদ্ধার করত; (ঘ) p21 heading-এ **কোনো নতুন angle নেই** — ট্র্যাকটি probe না চালিয়ে যুক্তি দিয়ে দেখিয়েছে; (ঙ) **সৎ সংশোধন (§৯): full suite 43/43 নয়, 42/43** — একমাত্র fail `test_five_live_pages_byte_identical`, যেটা পুরনো (stale) page-গুলির SHA pin করে; rebuilt page promote করার সরাসরি ফলেই এটা fail করে, regression নয় — fixture re-pin parent-এর সিদ্ধান্তের অপেক্ষায়। বাকি সব মাপ হুবহু একই: canonical অপরিবর্তিত, coverage 95/97, demo ৮২, DB SHA অপরিবর্তিত, Aug p1 PNG 306 / fitz 308।

---

## ০. এক নজরে — headline সংখ্যা

| মাপ | R26 baseline | **Round 27 merge** |
|---|---:|---:|
| Gate (২৫ Raviraj পাতা) | 24 ALLOW / 1 REFUSE | **24 ALLOW / 1 REFUSE (=)** |
| Gate (৩৩ entry) | 32 ALLOW / 1 REFUSE | **32 ALLOW / 1 REFUSE (=)** |
| ফ্ল্যাগ (T1 / T2 / T3 / T4 / T5) | 1 (0 / 0 / 1 / 0 / 0) | **1 (0 / 0 / 1 / 0 / 0) (=)** |
| মোট শব্দ (২৫ পাতা) | 9379 | **9379 (=)** |
| মোট শব্দ (৩৩ পাতা) | 12372 | **12372 (=)** |
| REFUSE পাতা | শুধু p20 | **শুধু p20 (T3 Path C, box `[557,661,986,678]`)** |
| Seg byte-identical | 32/33 (R25→R26) | **33/33 — সব পাতা byte-identical** |
| Canonical p2 N5 / Description ভুল / redbox | 41/81, ভুল ৩০, 7/66 | **41/81 (=), ভুল ৩০ (=, একই list), 7/66 (=)** |
| Canonical p3 strict / improved (FP) | 248 / 285 (186) | **248 (=) / 285 (=) (186, =)** |
| Canonical p2 / p3 gate | p2 ALLOW, p3 ALLOW | **p2 ALLOW, p3 ALLOW (=)** |
| LINES (canonical r15m) | 327/327 | **327/327 (=, p2 seg byte-identical বলে বহাল)** |
| p21 GT (৪২ certain boundary) | 34/42 @ ±5px | **34/42 @ ±5px (হুবহু একই, per-line 6/9, 10/15, 18/18)** |
| PG ৬ পাতা (শব্দ) | aug 306/308/305, may 308/313/306 | **aug 306/308/305, may 308/313/306 — হুবহু একই** |
| Fitz render (১৪ PG পাতা) | aug 308/308/305/307/303/303/311/309, may 307/313/305/306/305/309 | **সব ১৪ পাতা SAME (0/14 differ)** |
| Guard (live page, FULL) — canonical r10m টেবিল | 0/5 FAIL (R26 re-run) | **0/5 FAIL — C1–C4 PASS সব পাতায়, C5 FAIL সব পাতায় (টেবিল stale, §৪)** |
| Guard (live page, FULL) — R26 টেবিল | — (ছিল না) | **5/5 PASS — C1–C5 সব পাতায়** |
| Live page embedded শব্দ | 302/297/302/303/301 (stale) | **306/308/308/313/306 — R26 segs-এর সঙ্গে হুবহু মিলেছে** |
| Round 3 DB SHA | `1c065457…` | **`1c065457…` — আগে ও শেষে একই** |
| Full suite (repo test clone) | 43/43 (429.6s) | **42/43 (419.87s) — ১ fail শুধু stale SHA-pin test (§৯)** |
| Demo (synthetic) | 82 শব্দ | **82 শব্দ (=, নিজে চালিয়ে যাচাই)** |
| Aug p1 শব্দ-সংখ্যা | PNG 306 / fitz 308 | **PNG 306 / fitz 308 — দুই render-পথেই সঠিক** |

**ফ্লিপ:** কোনো flip নেই — gate, শব্দ, canonical, coverage সব অপরিবর্তিত। এই রাউন্ডের ফসল **তিনটি জিনিস**: (ক) live page-গুলি আর stale নয় — Guard-এর page-দিকের staleness সেরেছে, মাপা প্রমাণসহ (§৪); (খ) **দ্বিতীয় staleness ধরা পড়েছে** — identity টেবিলটাও stale, আর তার fix (১০টি box-এর data update) প্রস্তুত, parent-এর ratification-এর অপেক্ষায়; (গ) **p20-র ১৩তম ব্যর্থতার প্রমাণ** — Hong & Hull detection-এ সফল হয়েও selection-এ ব্যর্থ, যা R28-র lead-কে (slash-joiner-নিশ্চিত candidate) জন্ম দিয়েছে।

---

## ১. ট্র্যাক verdicts — ৪টি ট্র্যাক, ১টি PROMOTE (live page)

| ট্র্যাক | verdict | মূল ফল |
|---|---|---|
| **track-livepage** | **PROMOTE — ৫টি rebuilt live page + identity টেবিল (parent ratification-সহ)** | ৫টি page R26 segs দিয়ে rebuild (embedded 306/308/308/313/306, R26 segs-এর সঙ্গে হুবহু); background byte-identical (orig SHA আগের মতোই); Guard R26-টেবিলে **5/5 PASS** (C1–C5 সব পাতায়); canonical r10m টেবিলে C1–C4 PASS, C5 FAIL সব পাতায় — Lot/WIDTH in_seg=False AND in_page=False, অর্থাৎ টেবিল stale, page নয়। Bold flip ~১৫ শব্দ/Aug পাতা (threshold-marginal, render-পরিবর্তনের ফল, §৪)। |
| **track-honghull** | **DO NOT PROMOTE** | EXPORTER-র clean repeat পাতায় আছে (header `[1711,664,1795,680]`) — match 0.748, অবস্থান 0–2 px নির্ভুল, ৯টি variant-এই x=818 — কিন্তু সেরা ভুল 0.741 ("PER", SHIPPER-র tail), margin **0.007**; ৯ variant-এর ৮টিতে ভুল template সত্যকে ছাড়িয়ে যায়; নিখুঁত cut-ও মাত্র **1/4 শব্দ** উদ্ধার করত (BENEFICIARY/MANUFACTURER/SHIPPER-র clean whole-word repeat নেই); gate থাকত 24/1। **p20-র ১৩তম ব্যর্থতা** — প্রথম যেটির detection সফল, selection ব্যর্থ। |
| **track-heading** | **DO NOT PROMOTE — কোনো নতুন angle নেই (probe চালানো হয়নি)** | R24–R26-র রিপোর্ট + কোড পড়ে যুক্তি দিয়ে দেখিয়েছে: একমাত্র নতুন candidate (tall-glyph word-start marking) spelling-এই মরে — ৭ word-initial tall বনাম ৮ word-internal ascender, "প্রতি tall-এর আগে cut" দিত ৮টি ভুল cut, মাত্র 1/8 উদ্ধার; width-rhythm DP R19 থেকে pipeline-এই আছে; Hong & Hull heading-এ চলে না (unique bold title-এর clean repeat নেই)। |
| **track-online** | **গবেষণা (কোড নয়)** | RESEARCH27.md: Hong & Hull প্রথম হাতে যাচাই (r0=0.70, unique token "4,000"-এ সম্পূর্ণ ব্যর্থ — paper-এর নিজের কথা); Farulla fuzzy 2017 প্রথম হাতে যাচাই (81.1% exact cut, column-function combination); US RE47,889 large-blob routing (citation-level); **US 5,734,761 resolved — আসলেই আছে, scan-editing prior art, splitter নয়** (R26 Correction 5 সংশোধন); 2024–2026-এ এখনও কোনো breakthrough নেই। |

---

## ২. merge — কী নেওয়া হয়েছে, কী নেওয়া হয়নি (no-code-change merge)

**নেওয়া হয়েছে (১টি promotion + ১টি প্রস্তাবিত টেবিল):**
- **৫টি rebuilt live page (track-livepage):** `scan-paper/`-র `live-scan-page-aug-300.html`, `-aug-p2-300.html`, `-may-300.html`, `-may-p2-300.html`, `-may-p3-300.html` — track-টি ইতিমধ্যে জায়গায় বসিয়ে দিয়েছিল; merge সেগুলিকে যাচাই করে promote করেছে (§৪, §৭)। Pre-rebuild backup `track-livepage/backup-before-r27/`-তে আছে।
- **identity_pg_r26.json — PROPOSED canonical টেবিল:** `merge-r27/identity_pg_r26.json` হিসেবে কপি করা হয়েছে (byte-identical কপি)। পুরনো r10m টেবিল কোথাও বদলানো বা মোছা হয়নি — তার promotion parent-এর সিদ্ধান্ত; রিপোর্টে এটা pending ratification হিসেবে লেখা হলো (§১১)।

**নেওয়া হয়নি:** Hong & Hull (selection ব্যর্থ), heading-এর কিছুই (নতুন angle নেই) — সবাই মাপা ব্যর্থতা / অনুপস্থিতি, §১-এ প্রমাণসহ।

**Segmenter/gate byte-identical (সৎ merge):** `segment_merged.py`, `gate_merged.py`, `rhythm_dp.py`, `logo_detect.py`, `gate_misses.py` — R26-র সঙ্গে **৫টি ফাইলই byte-identical** (diff ০)। তাই **৩৩/৩৩ পাতার seg byte-identical** (R26-র 32/33-র চেয়ে ভালো — এবার p21-ও বদলায়নি, কারণ কোড বদলায়নি)। `port_tau_to_repo.py` R26 থেকে কপি হয়ে এসেছে, এই রাউন্ডে অব্যবহৃত — repo-port-এর কোনো বদল নেই বলে port-এরও দরকার পড়েনি।

**Merge-এ ধরা পড়া সমস্যা (১টি — merge-এর নিজের, আগেই ঠিক করা):** `cp -r round26/merge-r26 round27/merge-r27` চালানোর সময় `merge-r27/` আগে থেকে খালি ডিরেক্টরি থাকায় কপিটি ভেতরে `merge-r27/merge-r26/` বানিয়েছিল; সঙ্গে সঙ্গে ধরা পড়েছে, contents উপরে তুলে ঠিক করা হয়েছে — R26 baseline ছোঁয়া হয়নি (read-only যাচাই করা হয়েছে)।

---

## ৩. p20-র fused লাইন — ১৩তম ব্যর্থতা: Hong & Hull (detection সফল, selection ব্যর্থ)

Target: `[557,661,986,678]` = "BENEFICIARY/MANUFACTURER/EXPORTER/SHIPPER" (৪ শব্দ, slash-জোড়া), ৩টি CC ১১৭–১৫৮px, gap ১px আর ২px। Gate T3 Path C-তে REFUSE — সঠিক REFUSE। সব সংখ্যা PNG render (`round18/track-b/pages300/rav-20.png`, R26 segs-এর render) থেকে।

| শব্দ | clean whole-word repeat? | সেরা প্রমাণ |
|---|---|---|
| BENEFICIARY | **না** | span-এর ভেতরে সেরা ২৩px fragment "RY" (0.706) — সত্য partial, সীমানা বসায় না |
| MANUFACTURER | **না — কিছুই নেই** | span-এ 0.60-র উপরে কিছুই নেই |
| EXPORTER | **হ্যাঁ — দুবার, p20-তেই** | header "EXPORTER" `[1711,664,1795,680]`, **0.748, x=818, 0–2 px নির্ভুল**; prefix "EXPORT/" 0.687, ৯px ভুল জায়গায় |
| SHIPPER | **না (whole-word নয়)** | ৩৬px "PER" (SHIPPER/EXPORTER-র tail), **0.741, x=947** — সত্য partial, ভুল cut দিত |

**কেন DO NOT PROMOTE (তিনটি আলাদা কারণ, প্রতিটি মাপা):**
1. **Discrimination নেই:** সত্য 0.748, সেরা ভুল 0.741 — margin **0.007**। আগে থেকে ঠিক করা bar ছিল NCC ≥ 0.90 — সত্য match সেটাও পার হয় না। ৯টি binarisation/trim variant-এর **৮টিতে ভুল template সত্যকে ছাড়িয়ে যায়** (best_other 0.759–0.887) — একটিই cherry-picked operating point-এ (Otsu-217, trim 0) সত্য rank 1।
2. **মাত্র 1/4 শব্দ:** নিখুঁত cut-ও শুধু EXPORTER-কে উদ্ধার করত — বাকি তিনটি fused-ই থাকত, লাইন T3 REFUSE-ই থাকত, gate 24/1-ই থাকত।
3. **Cross-page শুধু ভুল বাড়ায়:** অন্য Raviraj পাতায় কোনো whole-word repeat নেই; resized p21 fragment-গুলি 0.734–0.784-এ সত্যকে ছাড়িয়ে যায়।

**Guardrail:** ৭টি control victim-এ 0/7 false cut NCC ≥ 0.748-এ, 1/7 ≥ 0.70-এ (NO.) — length-aware threshold 0.70 control-দের বাঁচাত, কিন্তু fused লাইনে "PER" ভুল cut-টি (0.741) তখনও ঢুকত। **কোনো fixed threshold সত্য cut-কে ঢুকিয়ে সব ভুল cut-কে বাদ দিতে পারে না।**

**Matcher artifact (ভবিষ্যতের জন্য):** thr 183-এ ১৮টি template all-white হয়ে `TM_CCOEFF_NORMED` 1.000 দিয়েছিল — constant template মানে কিছুই না; cleaned re-run-এ ink fraction [0.05, 0.95] আর ≥15 ink px guard বসানো হয়েছে।

**মোট: p20-র লাইনে এখন ১৩টি স্বাধীন পদ্ধতি ব্যর্থ** (R26-র ১২টি + Hong & Hull)। কিন্তু এটা প্রথম পদ্ধতি যার **detection সফল** (EXPORTER 0–2 px-এ) আর **selection ব্যর্থ** — JP2000322514A-র (R26) মতোই নৈতিক শিক্ষা, আর প্রথমবার blob-এর বাইরের signal কোনো সত্য শব্দ (1/4) উদ্ধার করেছে। **R28 lead (§১১):** match location-কে candidate হিসেবে নিয়ে gate-এর নিজের slash-joiner test (`_is_slash_like_t3`) দিয়ে নিশ্চিত করা — সত্য cut slash-এর ঠিক গায়ে বসে, "PER" ভুল cut শব্দের মাঝখানে, joiner ছাড়া। এটা পরীক্ষা হয়নি, দাবি করা হচ্ছে না।

---

## ৪. Live page rebuild + Guard — দুটি staleness, একটি সেরেছে, একটি parent-এর হাতে

**Rebuild (track-livepage, merge যাচাই করেছে):** ৫টি page R26 segs দিয়ে rebuild — embedded শব্দ **306/308/308/313/306**, R26 segs-এর সঙ্গে হুবহু। Merge নিজে `const WORDS` পার্স করে গুনেছে: page-now 306/308/308/313/306, backup (rebuild-এর আগে) 302/297/302/303/301 — ট্র্যাকের before/after-এর সঙ্গে হুবহু মিলেছে। Background byte-identical: তিনটি embedded image-ই (orig + ২টি clean layer) current আর backup-এ SHA-সহ এক — orig SHA `7b171751…`, `11c3aacf…`, `d0fb6f89…`, `560e5da3…`, `7f56d9f6…` ট্র্যাকের সঙ্গে মিলেছে। Page byte-size ট্র্যাকের "after" মানের সঙ্গে হুবহু (aug-p1 3,629,095 ইত্যাদি)।

**দুটি staleness-এর diagnosis (ট্র্যাকের, merge যাচাই করেছে):**
1. **Page stale (সেরেছে):** page-গুলি r10m word family embed করত (302/297/302/303/301), R26 segs 306/308/308/313/306।
2. **Identity টেবিল stale (সারেনি — টেবিল update লাগবে):** R26 segs গণনা হয়েছে `round4/track-a/pages/*-300.png` render-এ (aug-p1 2483×3485 — orig background-এরই মাপ), আর পুরনো page-গুলি বানানো হয়েছিল `round4/merge/pages300/*.png` থেকে (2480×3484, ২–৩px ছোট, আলাদা render)। ফলে identity box ১–৪px সরে গেছে: dy0 median +2px (aug-p1, may-p1, may-p2), +4px (aug-p2), 0px (may-p3); R26 বনাম r10m exact box overlap aug-p1/aug-p2/may-p1/may-p2-তে **০**, may-p3-তে 137/306।

**Guard re-run (merge নিজে চালিয়েছে, ট্র্যাকের দাবি বিশ্বাস করে নয় — ১০টি run, দুটি টেবিলে):**

(a) canonical (r10m) টেবিল — C5 FAIL, টেবিল stale-র প্রমাণ:

| page | C1 count | C2 ordered | C3 multiset | C4 spot | C5 identity | verdict |
|---|---|---|---|---|---|---|
| aug-p1 | PASS 306=306 | PASS | PASS | PASS 25/25 | **FAIL** Lot/WIDTH in_seg=False, in_page=False; Hard PASS 11.6px | **FAIL** |
| aug-p2 | PASS 308=308 | PASS | PASS | PASS 25/25 | **FAIL** Lot/WIDTH in_seg=False, in_page=False; Hard PASS 3.5px | **FAIL** |
| may-p1 | PASS 308=308 | PASS | PASS | PASS 25/25 | **FAIL** Lot/WIDTH in_seg=False, in_page=False; Hard PASS 15.2px | **FAIL** |
| may-p2 | PASS 313=313 | PASS | PASS | PASS 25/25 | **FAIL** Lot/WIDTH in_seg=False, in_page=False; Hard PASS 13.1px | **FAIL** |
| may-p3 | PASS 306=306 | PASS | PASS | PASS 25/25 | **FAIL** Lot/WIDTH in_seg=False, in_page=False; Hard PASS 13.9px | **FAIL** |

(b) R26-টেবিল (`identity_pg_r26.json`) — **5/5 PASS**:

| page | C1 | C2 | C3 | C4 | C5 | verdict |
|---|---|---|---|---|---|---|
| aug-p1 | PASS 306=306 | PASS | PASS | PASS 25/25 | PASS Lot+WIDTH in_seg=True, in_page=True; Hard 11.6px | **PASS** |
| aug-p2 | PASS 308=308 | PASS | PASS | PASS 25/25 | PASS Lot+WIDTH in_seg=True, in_page=True; Hard 3.5px | **PASS** |
| may-p1 | PASS 308=308 | PASS | PASS | PASS 25/25 | PASS Lot+WIDTH in_seg=True, in_page=True; Hard 15.2px | **PASS** |
| may-p2 | PASS 313=313 | PASS | PASS | PASS 25/25 | PASS Lot+WIDTH in_seg=True, in_page=True; Hard 13.1px | **PASS** |
| may-p3 | PASS 306=306 | PASS | PASS | PASS 25/25 | PASS Lot+WIDTH in_seg=True, in_page=True; Hard 13.9px | **PASS** |

Merge-এর ১০টি Guard JSON (`merge-r27/guard/`) ট্র্যাকের ১০টি JSON-এর সঙ্গে **checks-সহ হুবহু মিলেছে** — ট্র্যাকের দাবি re-run-এ যাচাই হয়েছে, বয়ে আনা হয়নি। মূল কথা: C5 canonical-এ fail করে কারণ টেবিলের box seg-এও নেই, page-এও নেই — **seg আর page পরস্পরের সঙ্গে একমত (C1–C4 প্রমাণ করে)। টেবিলটাই stale।** কোনো faithful rebuild ওই টেবিলে C5 pass করতে পারে না, কারণ বর্তমান segmenter ওই box-গুলি আর বানায়ই না।

**Rebuild-এর পাশ-প্রতিক্রিয়া (সব মাপা, parent-এর জানা দরকার):**
- **Bold flip:** Aug পাতায় ~১৫টি শব্দ bold flip করেছে (aug-p1: 77→88)। কারণ: track-a render pages300 render-এর চেয়ে stroke ~৩.৫% পাতলা মাপে (median ratio 0.1093→0.1054), bold threshold 0.1253→0.1207 সরে গেছে। 1.15× median নিয়মের (R11-তে নথিভুক্ত) fragility — regression নয়, কিন্তু দৃশ্যমান weight-পরিবর্তন। Identity শব্দগুলির bold flag বদলায়নি।
- **নতুন ক্ষুদ্র শব্দ আসল কালি:** aug-p1-এ 5×4px শব্দ (fs 5.7) আর 1×32px sliver — পুরনো render-এ sliver-টির কালিই ছিল ০, track-a-তে ৩১ ink px। দুটোই R26 seg-এর শব্দ, faithfully embedded।
- **Heading line:** aug-p1-এ R26 line grouping-এর জন্য +1 renumbering (H1 [3,5]/13 → [3,6]/14); H1/H2 line identity বদলায়নি।
- **Display size:** aug-p1/aug-p2/may-p2 826→**827px** চওড়া (native-width-এর ২–৩px পার্থক্য, layout বদল নয়)। may-p1/may-p3-র screenshot pixel-identical (0.00% differ); aug-p1/aug-p2/may-p2-তে শুধু printed text-এর pixel সরে (৭–১৩%) — table rule/structure নড়েনি।
- **Demo eye-check:** Lot/WIDTH retype clean, doubling বা ink sliver নেই (aug-p2-তেও, সবচেয়ে বড় shift dy +4 সত্ত্বেও)। Reused clean layer R26 box-গুলির নিচে কাজ করে।

---

## ৫. p21 heading — KNOWN LIMIT, নতুন angle নেই

Heading (৮ শব্দ, underline-এ fused, dropped)। এই রাউন্ডের heading ট্র্যাক **কোনো probe চালায়নি** — R24/R25/R26-র রিপোর্ট আর R26 baseline কোড (`rhythm_dp.py`, `split_blob_words` call site) পড়ে যুক্তি দিয়ে দেখিয়েছে নতুন angle নেই:

- **Tall-glyph marking (একমাত্র নতুন candidate):** spelling-এই মরে। ৮টি GT শব্দে word-initial tall letter ৭টি (P, R, R, A, t, T, O — "of"-এ নেই), word-internal ascender ৮টি (Periodic-এ d; of-এ f; Recommendation-এ d, t; Accorded-এ d, d; Transport-এ t; Operators-এ t)। "প্রতি tall glyph-এর আগে cut" দিত **৮টি ভুল cut**, Review|of সীমানা miss করত, উদ্ধার করত মাত্র **1/8** ("to") — 5/8 perfect-removal control-এর চেয়ে খারাপ। Capital বনাম ascender আলাদা করা letter recognition — নিষিদ্ধ।
- **Width-rhythm DP:** নতুন নয় — R19 থেকে pipeline-এই আছে (`rhythm_dp.py`); এর forced-cut premise (≥4px clear run = সীমানা) ঠিক inverted-gap premise, যা R22–R25 disprove করেছে।
- **Hong & Hull:** heading-এ চলে না — unique bold title-এর clean repeat নেই (p20 ট্র্যাকের lead, precondition unmet)।
- **Reachability wall বহাল:** `ww > 900` filter-এর আগে blob ফেলে দেওয়া; R26 Variant B-র bypass প্রমাণিতভাবে safe (০ regression) কিন্তু 0/8 উদ্ধার — আসল দেয়াল grouping, reachability নয়। **p21 heading known limit হিসেবে বহাল।**

---

## ৬. অনলাইন গবেষণা — Hong & Hull যাচাই, Farulla যাচাই, US 5,734,761 resolved, 2024–2026 এখনও শূন্য

RESEARCH27.md (৩১টি source, সব URL verbatim):

1. **Hong & Hull প্রথম হাতে যাচাই (SPIE 1995, ৮২৪ লাইন পড়া):** similarity `r = |A∩B|/|A∪B|`, পরীক্ষায় threshold **r0 = 0.70**; ১১০-শব্দ degraded paragraph + ৮০০-শব্দ পাতায় পরীক্ষা। নতুন failure mode: "m"/"n"/"h" ভুলভাবে টুকরো হয়ে যায় (over-split — paper-এর নিজের mode); সংখ্যাশব্দ **"4,000" মোটেই segment হয়নি, "because there are no other instances of numerical words"** — R26-র সতর্কবার্তার paper-এর নিজের ভাষায় নিশ্চিতকরণ; ভুল split-এর fast error propagation; same-font/same-spacing ধরে নেয়। ১৯৯৬-এর পর এই line-এর কোনো reimplementation বা follow-up নেই।
2. **Farulla, Murru & Rossini fuzzy 2017 প্রথম হাতে যাচাই (ar5iv, ৮৪০ লাইন):** ৩-input/১-output Mamdani fuzzy (f = কেন্দ্র থেকে দূরত্ব, g/h = vertical projection-এর second difference), PSO-তে per-dataset tune; handwritten dataset A-তে **81.1% exact cut, 88.9% ±5 column-এর ভেতরে**। p20-তে low prior — g/h R24/R25-র column family-ই; f positional prior, separating signal নয়; R25-র fuzzy vote ইতিমধ্যে 0/4।
3. **US RE47,889 (Xerox, reissue 2020, citation-level):** aligned-text mask দিয়ে oversized/mixed CC fragment করা — প্রথম external source যা বড় blob discard না করে আলাদা path-এ পাঠায়। Heading-এর two-lane দিকের একমাত্র citable support; word-splitting দেয় না, line segmentation-এর জন্য।
4. **US 5,734,761 — RESOLVED (R26 Correction 5 সংশোধন):** patent-টি আসলেই আছে (Justia + EP 0690415 A2 যাচাই) — Xerox/Bagley 1998, "Editing scanned document images using simple interpretations"। কিন্তু substance উল্টো দিকে: এটা **scan-editing prior art (interpretations), splitter নয়** — graphical object আগে থেকে defined ধরে নেয়। Lawyer-এর list-এ "no splitter inside" হিসেবে রাখতে হবে; সাথে cited predecessor US 5,167,016।
5. **আরও:** US 10,586,125 (Konica Minolta 2020, প্রথম হাতে পড়া) — classify-first underline removal + intersection restoration, heading router-এর জন্য borrowable idea, word split দেয় না; US 5,384,864 (Spitz 1993, expired) — modal stroke-width ligature detection, R26-র ব্যর্থ gate eye-এর published origin; US 5,438,630 word spotting (HMM, excluded); JBIG2/symbol-dictionary family (premise support, splitter নয়); ICDAR 2025-এ printed word-segmentation competition নেই; GitHub/YouTube/HN/Reddit/Dev.to-তে geometry-only fused-word method নেই।
6. **সৎ negative (দ্বিতীয় রাউন্ড পরপর):** 2024–2026-এর সব নতুন কাজ neural/VLM/OCR-based (US 11,869,258 ML, US 20240161522 OCR-first, DBNet++ + BART, TrOCR 2026, ICDAR FEST neural)। **নতুনতম যাচাইকৃত geometry-only Latin কাজ এখনও 2017 (Farulla)।**

---

## ৭. R23/R24/R25/R26-র শিক্ষা মানা হয়েছে — দুই render-ই যাচাই, Guard re-run, কোনো সংখ্যা বয়ে আনা হয়নি

- **দুই render:** PNG segs + fitz render (১৪ PG পাতা) — দুটোতেই যাচাই। Aug p1 PNG **৩০৬** / fitz **৩০৮** — দুই render-পথেই সঠিক। Fitz 0/14 differ (fitz-base-এর সঙ্গে), 0/14 differ (fitz-tau-র সঙ্গে)।
- **Guard re-run (নিজে চালানো, ট্র্যাকের দাবি বিশ্বাস করে নয়):** ১০টি run — canonical টেবিলে 0/5 (C5 FAIL), R26 টেবিলে **5/5 PASS**; merge-এর ১০টি JSON ট্র্যাকের JSON-এর সঙ্গে checks-সহ হুবহু মিলেছে (§৪)। R26-র শিক্ষা ("বয়ে আনা সংখ্যা সত্য নয় — re-run-ই সত্য") এই রাউন্ডে মেনে চলা হয়েছে: Guard-এর দুটি রানই merge নিজে চালিয়েছে।
- **Repo-port যাচাই:** এই রাউন্ডে segmenter/gate-এ কোনো কোড বদল নেই, তাই repo-port-এরও কোনো বদল নেই — port করার কিছু ছিল না। (R26-র trap-শিক্ষা এখানে প্রযোজ্য হয়নি, কারণ copy করার মতো নতুন কোডই ছিল না।)
- **E2 অক্ষত:** `_gap_mark` R21-র verbatim — Aug p1 fitz ৩০৮ অক্ষত।

---

## ৮. coverage — 95/97 অপরিবর্তিত

`probe_coverage.py` R27 segs-এ চালানো হয়েছে — output JSON **R26-র সঙ্গে (segdir/suffix label ছাড়া) byte-identical**: exact_box_items ৯৭, covered ৯২, still_missing_exact ৫, no_box_items ৪৬; extra ৯টির ৭টি covered। R23-র সংশোধন (৫টি "miss"-এর ৩টি আসলে miss নয়) একইভাবে প্রযোজ্য — **সত্য coverage 95/97, অপরিবর্তিত**। বাকি ২টি আসল + ৩টি known-limit miss আগের মতোই: CARRIER NAME লাইন (৮ শব্দ), p21 heading, p21 address লাইন (২৬ শব্দ ১৪ box-এ), p10 "Prepared" (geometry-only unfixable), stamp fragment-গুলি (সঠিকভাবে drop)।

---

## ৯. সংশোধন (corrections — আগের রিপোর্টের ভুল ঠিক করা)

1. **Full suite "43/43" — এই রাউন্ডে সত্য 42/43:** R27-র suite ৪২ passed, **১ failed** (`test_five_live_pages_byte_identical`, 419.87s)। Fail-টি regression নয় — test-টি ৫টি live page-কে পুরনো (pre-rebuild, stale) SHA-তে pin করে (aug-p1 expected `bce37147…` = backup-এর SHA); rebuilt aug-p1 এখন `d4d25430…`। **Promoted rebuild-এর সরাসরি ফলেই test-টি fail করে** — page বদলেছে বলেই। Test expectation বদলানো হয়নি (নিয়ম: failing code-কে pass করাতে expectation বদলানো যাবে না) — fixture re-pin (৫টি নতুন SHA, §১২-তে দেওয়া) parent-এর সিদ্ধান্তের অপেক্ষায়। এই ১টি fail ছাড়া suite-এর বাকি ৪২টি test-ই pass করেছে, DB test-সহ।
2. **R26-র "Guard 0/5 FAIL" — এখন দুটি staleness-এ ভাগ হয়েছে:** R26 বলেছিল "live page stale"। R27-র re-measurement দেখিয়েছে page stale ছিল (সেরেছে) **আর** identity টেবিলও stale (সারেনি — ১০টি box-এর data update লাগবে)। "Guard 0/5 FAIL" আর page-এর বিরুদ্ধে উদ্ধৃত করা যাবে না — canonical টেবিলে C5 FAIL এখন stale-টেবিলের signal, page-এর নয়।
3. **p20-র ব্যর্থ পদ্ধতির count ১২ → ১৩:** Hong & Hull ১৩তম স্বাধীন ব্যর্থতা — তবে প্রথম যার detection সফল, selection ব্যর্থ (§৩)।
4. **R26 Correction 5 সংশোধন (online ট্র্যাক):** US 5,734,761 "নেই" বলা ভুল ছিল — patent-টি আছে, যাচাই হয়েছে; কিন্তু এটা splitter নয়, scan-editing prior art (§৬)।
5. **R26-র "p21 heading Variant B clean zero-regression" — বহাল, কিন্তু:** R27 heading ট্র্যাক নিশ্চিত করেছে bypass-টি safe হলেও grouping-এর কোনো নতুন পথ নেই — heading known limit বহাল (§৫)।

---

## ১০. সৎ প্রশ্ন — geometry-only উপায়ে 25/0 কি সম্ভব?

**এই রাউন্ডের পর উত্তর: এখনও না — আর প্রমাণ এখন আরও শক্ত।**

- **p20-র fused লাইন:** ১৩টি স্বাধীন পদ্ধতি ব্যর্থ (§৩)। Hong & Hull সবচেয়ে শিক্ষণীয় ব্যর্থতা: এটা blob-এর **বাইরের** signal ব্যবহার করে — আর তাতেও detection সফল হয়েও selection ব্যর্থ (0.748 বনাম 0.741)। অর্থাৎ সমস্যাটা আর "signal খুঁজে পাওয়া" নয়, **"সত্য আর ভুল আলাদা করা"** — আর geometry-only selection-এর কোনো signal এখনও পাওয়া যায়নি। তদুপরি, ৪ শব্দের মধ্যে ৩টির clean repeat পাতায়/অন্য পাতায় **নেইই** — Hong & Hull-এর নিজের paper-এর "4,000" case: repeat না থাকলে method চলেই না।
- **p21 heading:** নতুন angle নেই বলে প্রমাণিত (§৫) — grouping-এর বাইরে recognition ছাড়া কোনো পথ নেই।
- **কিন্তু "অসম্ভব" বলা যাবে না:** R28-র lead এখনও untried — match location-কে candidate হিসেবে নিয়ে gate-এর slash-joiner test দিয়ে নিশ্চিত করা (§৩, §১১)। τ R26-তে একটা limit ভেঙেছে — নতুন signal এখনও আসতে পারে। সৎ অবস্থান: **২৫/০ এখনও সম্ভব নয়, কিন্তু অসম্ভব প্রমাণিত নয়** — বাকি আছে একটিই untried lead।
- **ইঞ্জিন যা পারে (মাপা):** gate **24/1** (শুধু p20 REFUSE — প্রমাণিত known limit, সঠিক REFUSE); full suite **42/43** (১ fail শুধু stale SHA-pin, §৯); T3 recall অপরিবর্তিত, T4+T5 চোখ (০ false positive baseline-এ); coverage **95/97**; canonical হুবহু একই (N5 41/81, p3 248/285, LINES 327/327); **Guard R26-টেবিলে 5/5 PASS** (প্রথমবার মাপা); demo **৮২**; DB SHA অপরিবর্তিত; PG/fitz দুই render-এই সঠিক। **এই অবস্থাটাই সৎ 100%-র পথের মাইলফলক — 24/1, যেখানে ১টি REFUSE-এর কারণ মাপা আর প্রমাণিত, আর live page-গুলি আর stale নয়।**

---

## ১১. খোলা বিষয় (open items — Round 28-র জন্য)

1. **Identity টেবিলের promotion (parent-এর সিদ্ধান্ত):** `merge-r27/identity_pg_r26.json`-কে canonical টেবিল হিসেবে ratify করা — অর্থাৎ `improve/round13/merge-r13/scripts/identity_pg.json`-এর Lot/WIDTH box ১০টি R26 box দিয়ে বদলানো (Hard target অপরিবর্তিত)। যতক্ষণ না হয়, canonical Guard run C5 FAIL দেখাতেই থাকবে — সেটা stale-টেবিলের signal, page-এর নয়। পুরনো r10m টেবিল কোথাও মোছা হয়নি।
2. **Live-page SHA fixture re-pin (parent-এর সিদ্ধান্ত):** `tests/test_canonical.py`-র `CANONICAL_LIVE_SHAS`-এ ৫টি নতুন SHA বসানো (নতুন SHA §১২-তে)। না বসালে suite 42/43-ই থাকবে — ১ fail শুধু stale pin-এর জন্য।
3. **p20-র fused লাইন — R28 lead (একমাত্র untried):** Hong & Hull match location-কে candidate হিসেবে নিয়ে gate-এর slash-joiner test (`_is_slash_like_t3`) দিয়ে নিশ্চিত করা — সত্য cut slash-এর গায়ে, "PER" ভুল cut শব্দের মাঝখানে। পরীক্ষা হয়নি, দাবি করা হচ্ছে না।
4. **p21 heading — known limit বহাল:** recognition-ছাড়া grouping-এর পথ নেই; দুটি borrowable external idea আছে (US RE47,889 fragmentation, US 10,586,125 classify-first underline handling) — কোনোটিই word-splitting দেয় না।
5. **R25/R26 push এখনও বাকি:** repo এখনও Round 20-তে (commit `495c1086`) — R25 push approval card timeout-এ আটকে আছে (parent-এর হাতে)। R27-কে আলাদা push করা হবে নাকি R25+R26+R27 একসাথে, সেটা reversible working decision হিসেবে parent-এর হাতে।
6. **আগের মতোই খোলা:** Virtako label ৫-field decision (user-এর — আবার জিজ্ঞাসা করা যাবে না, তিনি সুবিধামতো জানাবেন); Windows .exe (তার PC-তে build); print calibration (factory printer — শুধু তিনি, Muse-র কাজ শেষ হলে); US patent legal check (lawyer — তিনি ব্যবস্থা করবেন; lead এখন: US 5,734,761 + US 5,167,016 + Adobe US9741142B2 + US 20250111688 + US 20250078557 + US RE47,889 + US 10,586,125); .docx capture 100/100 (৯৬.৬০% এখন); first-view ~১৪–১৮s (Phase-4-sized কাজ); Q-03–Q-09 + ★2–★8 + ১৮ borderless edge (DECISIONS-PENDING.md-তে)।

---

## ১২. যাচাই (verification — parent-এর জন্য)

- **Merge:** `merge-r27/segment_merged.py` + `gate_merged.py` + `rhythm_dp.py` + `logo_detect.py` + `gate_misses.py` + `segs/` (৩৩টি r27 seg + ৩৩টি r26 baseline কপি + summary_r27.json) + `gate_batch_r27_merged.json` + `canon_r27_merged.json` + `coverage_r27.json` + `run_segs_r27.py` + `run_gate_r27.py` + `score_canon.py` + `verify_fitz_r27.py` + `identity_pg_r26.json` (প্রস্তাবিত) + `guard/` (১০টি Guard JSON)। Segmenter/gate/support **৫টি ফাইলই R26-র সঙ্গে byte-identical** (diff ০); কোনো কোড বদল নেই।
- **Gate (নিজে JSON পড়ে গুনেছি):** **24/1** (২৫ পাতা); **৩২ ALLOW / ১ REFUSE** (৩৩ entry)। REFUSE: শুধু rav-p20 (T3 Path C, box `[557,661,986,678]`)। p21 **ALLOW** (T1 0, T2 0, T3 0, T4 0, T5 0, ৫৯০ শব্দ)। T1 ০, T2 ০, **T4 ০, T5 ০**। ২৫টি পাতার প্রতিটি R26 baseline-এর সঙ্গে SAME।
- **শব্দ:** ২৫ পাতা **9379 (=)**, ৩৩ পাতা **12372 (=)**; p2 ৬৭৬, p3 ৪৭১; p20 ৫২১ (=), p21 **৫৯০ (=)**; PG aug 306/308/305, may 308/313/306 (=)। **৩৩/৩৩ seg byte-identical** (R26-র সঙ্গে)।
- **Canonical:** N5 **41/81** (=, per-line যোগফল নিজে মিলিয়েছি), Description ভুল **৩০** (একই list), redbox **7/66** (=, scorer সরাসরি চালিয়ে যাচাই), p3 strict **248/384**, improved **285/384**, FP 186, p21 GT **34/42** @ ±5px (seam scorer — R26-র ৩৪/৪২-এর সঙ্গে হুবহু একই, per-line 6/9, 10/15, 18/18), LINES **327/327** (p2 seg byte-identical বলে বহাল; r15m rescorer তার নিজের seg-এ hardcode করা, নতুন seg-এ চালানো যায় না)। PG diff vs R20 baseline: শুধু aug-p2-তে ১টি box বদল (R26-র সঙ্গে হুবহু একই — pre-existing)। Canon JSON R26-র সঙ্গে tag আর path string ছাড়া identical।
- **Guard (নিজে ১০টি run চালিয়েছি):** canonical r10m টেবিলে **0/5** (C1–C4 PASS সব পাতায়, C5 FAIL সব পাতায় — Lot/WIDTH in_seg=False AND in_page=False; Hard PASS 11.6/3.5/15.2/13.1/13.9px); R26 টেবিলে **5/5 PASS** (C1–C5 সব পাতায়)। Merge-এর ১০টি JSON ট্র্যাকের ১০টি JSON-এর সঙ্গে checks-সহ হুবহু মিলেছে। Embedded count নিজে গুনেছি: 306/308/308/313/306; background byte-identical (orig SHA ট্র্যাকের সঙ্গে মিলেছে)।
- **Coverage:** **95/97** অপরিবর্তিত (probe JSON R26-র সঙ্গে segdir/suffix ছাড়া identical)।
- **DB SHA:** `1c065457bb9cb8e5b276d5007d9b020c18c8a0ae0374b92eb759f12150746939` — আগে ও শেষে একই (DB ছোঁয়া হয়নি; suite-এর DB test-ও pass করেছে)।
- **Fitz render:** Aug p1 **৩০৮ শব্দ**; ১৪টি PG পাতা fitz-এ segment করা হয়েছে (aug 308/308/305/307/303/303/311/309, may 307/313/305/306/305/309 — সব SAME, 0/14 differ)। PNG 306 / fitz 308 — দুই render-পথেই সঠিক।
- **Full suite (repo test clone `~/workspace/lse-r27-test/`, lse-r26-test-এর কপি, কোনো কোড বদল নেই):** **42 passed, 1 failed, 419.87s** (scan-paper venv python, `TMPDIR=$HOME/workspace/lse-verify-tmp`)। একমাত্র fail: `test_five_live_pages_byte_identical` — stale SHA-pin (§৯)। নতুন ৫টি SHA (fixture re-pin-এর জন্য, parent-এর সিদ্ধান্তে): aug-300 `d4d25430…`, aug-p2 `c3d9b7a4…`, may-300 `7d4d19cc…`, may-p2 `3d934434…`, may-p3 `9cf42b25…` (পূর্ণ SHA: `d4d254308a29e933fa7011e0cca8b65854058673ea7fe1d330225e774a9224d5`, `c3d9b7a4c41af3a7f07c7843f1140abe3de1443543bad5fab3cd21dd13901391`, `7d4d19cc97816fbc39dbc6442b16eeb5bcb8941852980baf686858fabf256ade`, `3d93443414704a96151956a8f8ea8b2dd914426ff23944f59a6e689ac06584eb`, `9cf42b25b428f5596761da2e49769742b4d8ac929131a7d4fdd34ac0acda92d6`)। Demo **৮২ শব্দ** (নিজে চালিয়ে যাচাই)।
- **Push করা হয়নি, Drive-এ upload করা হয়নি, MEMORY.md ছোঁয়া হয়নি** — parent যাচাই করে push/upload/memory করবে। (নোট: এই রাউন্ড চলাকালীন MEMORY.md-তে বাইরে থেকে (parent/main-এর হাতে) branding/naming সংক্রান্ত লাইন যোগ হয়েছে — merge এজেন্ট সেটা ছোঁয়নি।) **Push সিদ্ধান্ত parent-এর:** R25 push এখনও বাকি (approval timeout) — R26/R27-কে আলাদা push করা হবে নাকি R25+R26+R27 একসাথে, সেটা reversible working decision হিসেবে parent-এর হাতে।

---

## ১৩. উদ্ভাবন বনাম মেরামত (purpose check — ব্যবহারকারীর নির্দেশ)

এই রাউন্ডের **উদ্ভাবন — সৎভাবে বললে, নতুন উদ্ভাবন নেই।** যা আছে তা **মেরামত আর প্রমাণ**: (ক) live page-গুলি rebuild করে Guard-কে প্রথমবার মাপা 5/5 PASS-এ আনা (R26-টেবিলে) — demo-র ভিত্তি মেরামত; (খ) identity টেবিলের staleness ধরা — ভুল সংখ্যা (canonical C5 FAIL) আর page-এর বিরুদ্ধে উদ্ধৃত না করা; (গ) Hong & Hull-এর সৎ ব্যর্থতা — detection সফল হয়েও selection ব্যর্থ, যা R28-র lead-কে জন্ম দিয়েছে; (ঘ) suite-এর 42/43-কে লুকিয়ে 43/43 না বলা — stale SHA-pin-কে নাম ধরে লেখা। **মেরামতই এই রাউন্ডের কাজ ছিল** — gate-কে এগোনোর মতো নতুন signal এই রাউন্ডে আসেনি, আর সেটা লুকানো হয়নি। সবচেয়ে বড় শিক্ষা (R24–R26-র সঙ্গে একমত): **gate-এর সংখ্যা সত্য নয় — word identity-ই সত্য; বয়ে আনা সংখ্যা সত্য নয় — re-run-ই সত্য** — আর এই রাউন্ডে দুটো শিক্ষাই মেনে চলা হয়েছে: Guard দুটি টেবিলেই নিজে re-run করা হয়েছে, আর suite-এর ১টি fail-কে "প্রত্যাশিত" বলে চাপা দেওয়া হয়নি, কারণসহ লেখা হয়েছে। পরের উদ্ভাবনের পথ একটিই খোলা আছে — R28-র slash-joiner-নিশ্চিত Hong & Hull candidate — আর সেটা পরীক্ষা না হওয়া পর্যন্ত 25/0-র উত্তর "এখনও না"-ই থাকবে।
