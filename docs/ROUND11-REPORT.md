# LSE Round 11 — প্রতিবেদন

**তারিখ:** ২০২৬-১১-০৭ | **সমন্বয়কারী:** Round 11 coordinator (একমাত্র) | **ভিত্তি:** Round 10 (ROUND10-REPORT.md)

## সারাংশ

Round 11-এর তিনটি ট্র্যাকই সম্পূর্ণ হয়েছে এবং একটিমাত্র সামঞ্জস্যপূর্ণ v8 পাতা-সেটে মার্জ করা হয়েছে। ৫টি live পাতা পুনর্নির্মাণ করে root-এ promote করা হয়েছে, এবং সম্পূর্ণ যাচাই-সূট নিজে আবার চালিয়ে সবুজ পাওয়া গেছে।

| বিষয় | Round 10 | **Round 11** |
|---|---|---|
| Raviraj পূর্ণ পাতা (strict) | ৫৯১/৭৯৫ (৭৪.৩%) — দাবি | **৬৪৩/৭৯৫ (৮০.৯%)** |
| Raviraj p2 (strict) | ৩২৬/৫০২ — দাবি | **৩৭৮/৫০২ (৭৫.৩%)** |
| p2 LINES | ২০৫/৩২৭ (দাবি) | **২৬২/৩২৭ (৮০.১%)** |
| N5 | ৮১/৮১ improved (strict ৭৭/৮১) | **৮১/৮১ improved (strict ৭৭/৮১) — অপরিবর্তিত** |
| Description | ৬৯/৬৯ | **৬৯/৬৯ — অপরিবর্তিত** |
| Heading (TITLE/H2/H1-diff) | r9m workaround দিয়ে ১৪/১৪, ১৪/১৪, ০ | **r10m seg থেকে সরাসরি ১৪/১৪, ১৪/১৪, ০ — workaround সরানো হয়েছে** |
| May WIDTH bold | ratio-তে মাত্র ০.০০১ মার্জিন | **Lot-anchor নিয়মে ন্যূনতম মার্জিন ০.০০৬৫ (৪১ গুণ)** |
| লম্বা replacement clamp | ০.৬০ floor; ১১ অক্ষরে overflow | **floor নেই; ১৪ অক্ষর পর্যন্ত ফিট; `.tiny` সতর্কতা** |
| fontfix_verify300 | ৪৩/৪৩ | **৪৩/৪৩** |

**সবচেয়ে বড় সংশোধন (Track B-র পুনঃমাপ):** Round 10-এর দাবি করা বেসলাইন ভুল ছিল। সত্য বেসলাইন p2 **৩২৩/৫০২** (দাবি ৩২৬) এবং পূর্ণ পাতা **৫৮৮/৭৯৫** (দাবি ৫৯১) — R9/R10-এর eye-count-এ merge বেশি ধরা হয়েছিল। তাই Round 10 থেকে Round 11-এর আসল লাভ strict-এ **+৫৫ শব্দ** (৩২৩→৩৭৮), দাবি করা সংখ্যা দিয়ে মাপলে +৫২ নয়।

## ১. Track A — merge-invariant gap_dark: আসল সমাধান পাওয়া গেছে (R1)

**সমস্যা:** Round 10-এ r10m merge-এর পর aug-p2/p3-র header লাইন H1 থেকে পড়ে গিয়েছিল (gap_dark ০.২২৫→০.১৪৮ এবং ০.১৯৫→০.০৯৭, threshold ০.১৫৫)। ৫৬১টি মাপা লাইনে band_grey / bar_ink / gap_dark / wash-এর কোনো একক বা দ্বিমাত্রিক threshold ৮টি header-কে আলাদা করতে পারেনি। তাই heading r9m seg থেকে হিসাব করা হতো — একটি নথিভুক্ত workaround।

**সমাধান (R1) — exemplar ink-IoU + wash:** একটি লাইন H1 হবে যদি `exemplar_iou ≥ 0.50 AND band_grey < 242` হয়। exemplar_iou হলো ডকুমেন্ট-সেটের নিজের header exemplar-এর (একটি (B)-flag করা, non-title লাইন, সর্বোচ্চ gap_dark দিয়ে নির্ধারণীভাবে বাছা — কোনো পাতা hard-code করা নেই) সঙ্গে লাইনের anchor-এর কাছের পাতার কালির (dx ±২৫, dy ±৮) সেরা ink-IoU। Threshold দুটি মাপা ব্যবধানের মধ্যবিন্দু: IoU (০.৭০৪+০.২৯৮)/২, grey (২৩৭.২+২৪৮.৬)/২।

**কেন দুটি সংকেতই লাগে (মাপা, চোখে যাচাই করা):** ৮টি Aug header লাইন আসলে একই ছাপা লাইন — IoU ০.৭০৪–১.০০০, Aug non-H1 সর্বোচ্চ ০.২৯৮। কিন্তু একই লেখা ৬টি May পাতাতেও আছে (IoU ০.৬৭৮–০.৭৪৮) — wash bar ছাড়া, সাদা কাগজে, band_grey ২৪৮.৬–২৪৯.৮ বনাম header ২৩৩.৪–২৩৭.২ (২× clip-এ নিশ্চিত)। IoU একা ব্যর্থ, grey একা ব্যর্থ; একসঙ্গে পরিষ্কার আলাদা হয়।

**যাচাই (ট্র্যাকের চালানো + মার্জে নিজে আবার চালানো):** r10m, r9m, r8m — তিনটি seg পরিবারেই **TITLE ১৪/১৪, H2 ১৪/১৪, H1-diff ০**। Control (exemplar=None): H1-diff ২ (aug-p2/p3 L3 মিস — সংবেদনশীলতার প্রমাণ)। ১৫/১৫ run, ০ false positive। Grey সংবেদনশীলতা (২৭ কম্বিনেশন): header grey সর্বোচ্চ ২৩৮.০ (threshold ২৪২-এর নিচে ৪.০ মার্জিন), May-লেখা grey সর্বনিম্ন ২৪৭.৮ (৫.৮ মার্জিন)।

**মার্জ সিদ্ধান্ত — একটিমাত্র PG-সেট exemplar:** আমার প্রথম চেকে আলাদা Aug/May exemplar বানানো হয়েছিল; May-সেটের বাছাই ছিল বিকৃত — may-p2 L6, gap_dark ০.০, band_grey ২২০.৫, আকার (১৪, ৪৯), কালি ১৫৮ — এবং সেটি may-p6 L6-কে ভুলভাবে flag করেছিল (তিন পরিবারেই H1-diff ১)। যাচাইকৃত রূপ হলো **১৪ পাতা থেকে একটিমাত্র PG-সেট exemplar** (ট্র্যাক A-র পদ্ধতি ঠিকমতো): aug-p4 L3, gap_dark ০.৫৬, band_grey ২৩৪.৩, আকার (৪৩, ৮৮৯), কালি ১৩৪৫২। `merge-r11/exemplar-pg.npy` (SHA `ca9d2031…`) + `exemplar-provenance.json`। খোলা hardening: exemplar বাছাইয়ে gap_dark floor (অন্য template-এর জন্য)।

**প্রয়োগ:** `heading.py`-তে R1 + `heading_lines_guarded()`-এ exemplar forwarding যোগ করা হয়েছে (ট্র্যাক যে ঘাটতি দেখিয়েছিল)। Shared `heading.py` এখন `merge-r11/staging-heading.py`-র সঙ্গে byte-identical। Constant: `EXEMPLAR_IOU_THR = 0.50`, `EXEMPLAR_GREY_THR = 242.0`, `EXEMPLAR_DX = 25`, `EXEMPLAR_DY = 8`।

**Round 10-এর r9m-heading workaround সরানো হয়েছে** — builder-রা এখন বর্তমান r10m/r11m seg থেকেই heading হিসাব করে।

**সৎ সীমা:** R1-এর জন্য কমপক্ষে ১টি (B)-flag করা header লাইন লাগে (না থাকলে (B)-তেই graceful fallback) এবং লাইনটি কমপক্ষে ২ পাতায় থাকতে হয়; grey মার্জিন ৪.০–৫.৮ level — অন্য supplier-এর wash ঘনত্বে আবার মাপতে হবে।

## ২. Track B — Raviraj p2: ৩২৩ → ৩৭৮/৫০২

**বেসলাইন সংশোধন (গুরুত্বপূর্ণ):** Track B সত্য বেসলাইন আবার মেপেছে — p2 LINES ২০৭/৩২৭ (R10 দাবি ২০৫ নয়), p2 মোট strict **৩২৩/৫০২** (দাবি ৩২৬ নয়), পূর্ণ পাতা **৫৮৮/৭৯৫** (দাবি ৫৯১ নয়)। R9/R10-এর eye-count merge বেশি ধরেছিল (C −৫, D −৩, E-cg −১, F −১, G −২, Inv −১; ২টি G verdict উল্টোদিকে সংশোধন)।

**ফল (মার্জে নিজে আবার মাপা):**
- p2 LINES **২৬২/৩২৭ (৮০.১%)** — verdicts ফাইল থেকে সরাসরি গোনা (১৫৪ 'ok' + ১০৮ 'correct', ৬৫ miss)
- p2 মোট strict **৩৭৮/৫০২ (৭৫.৩%)**, improved **৩৮২/৫০২ (৭৬.১%)**
- পূর্ণ পাতা strict **৬৪৩/৭৯৫ (৮০.৯%)**, improved **৬৪৭/৭৯৫ (৮১.৪%)**
- **৫৫টি শব্দ ঠিক করা হয়েছে** (apply ৪১ + custom ১৫) + ২টি বেসলাইন সংশোধন; ৫৭টি verdict-এ `r11b` tag। **০টি false merge** — diff চেক: ফেলা ৪৪টি box-এর প্রতিটি যাচাইকৃত fix-এর input, যোগ করা ৫৬টি box-এর প্রতিটি যাচাইকৃত fix-এর output। F (২৯/২৯), G (২৩/২৩), E-ce-4 (৭/৭), E-cg-3 (২/২) সম্পূর্ণ।

**Rule D disambiguation (ডেলিভারেবল):** D-merge অনুমোদিত হবে শুধু তখনই যখন merge-span ডকুমেন্টের নিজের vocabulary-র ঠিক একটি শব্দের সঙ্গে মেলে AND ডটটি শব্দের ভেতরে থাকে। মাপা: ১২টি D candidate, ৪টি অনুমোদিত, ৮টি প্রত্যাখ্যাত; Round 10-এর ৪টি পরিচিত ভুল merge প্রস্তাব একবারও ঘটেনি। দশমিক-সংক্রান্ত ৬টি miss-ই ঠিক হয়েছে।

**শেখা দুটি ভুল (প্রতিবেদনে নথিভুক্ত):** S15 "COMPANY/LIMITED" বলে অনুমোদিত হয়েছিল, আসলে সেটি ছিল D-6-এর "Delivery Office" (একই x, ভিন্ন y); আসল C-6 COMPANY/LIMITED আলাদা split-এ ঠিক হয়েছে। S24-এর "SANAND" আসলে GT শব্দ "FARM,SANAND"-এর অর্ধেক ছিল — FARM,+SANAND merge যোগ করা হয়েছে।

**যাচাই (সব code চালিয়ে):** fixed-word ৪১/৪১, custom fix ১৪/১৪, N5 ৭৭/৮১ strict ও ৮১/৮১ improved, Description ৬৯/৬৯ (সংশোধিত GT), redbox ১১/৬৬, PG sample ৫১৮/৫১৮ (০ extra), fontfix_verify300 ৪৩/৪৩ — PG-তে কোনো regression নেই। প্রধান fix-গুলো ২×–৫× clip-এ চোখে যাচাই করা হয়েছে।

**এখনও বাকি (p2):** E-ce ২৭টি miss (cross-line fusion — দুই সারির কালি জোড়া লেগে ৭৫৮×৪৫px দৈত্য component; হাতে split করা box লেখা হয়নি, আলাদা algorithm লাগবে), A-logo ১৬, E-cg-1 ৫, D ৫, redbox ৫৫ (word_repair দিয়ে ঠিক হয় না — আলাদা ট্র্যাক লাগবে: red-box এলাকায় নিম্ন Otsu threshold, অথবা red-channel segmentation)। **p3-র span-level GT করা হয়নি** — Round 10-এর p3 +৯ এখনও R5-এর হাতে গোনার ওপর দাঁড়িয়ে (সত্য লাভ +১২-ও হতে পারে)।

## ৩. Track C — bold mechanism শক্ত করা

**নতুন সংকেত "Lot-anchor diff" (WIDTH ratio − Lot ratio):** Control reproduce-এ দেখা গেছে May p1 WIDTH ratio-মার্জিন মাত্র **+০.০০০১৫৯** (Round 10-এর "০.০০১"-এর চেয়েও তীক্ষ্ণ), Aug p2 **−০.০০০২০১** — দুদিকেই ছুরির ধার। Lot-anchor: Aug ০.০১১৮–০.০২৯৪ বনাম May ০.০৪২৪–০.০৬৩৪ — **১৪ পাতা জুড়ে ব্যবধান +০.০১৩০, threshold ০.০৩৬, LOPO ১৪/১৪ সঠিক**। live ৫ পাতায় ন্যূনতম মার্জিন ০.০০৬৫ (ratio নিয়মের ৪১ গুণ)। ৫/৫ live পাতায় Round 10-এর সিদ্ধান্ত ঠিকমতো reproduce করে (May ৩ পাতা bold, Aug regular)।

**DNA তুলনা mechanism নয়, শুধু সমর্থন:** Round 10-এর নতুন GT-তে আবার মাপা — WIDTH-5 ব্যবধান +০.০২১ (৫/৫ সঠিক, স্বাধীন সমর্থন), কিন্তু WIDTH-14 ব্যবধান মাত্র **+০.০০২**। সাধারণ classifier হিসেবে DNA মৃত: MAIN ব্যবধান −০.০১৩, MAIN+OBS −০.০৯৮, ৫/৫ fold-এ LOPO fit করা অসম্ভব। Ink-fraction diff প্রত্যাখ্যাত (ব্যবধান মাত্র +০.০০৯১)।

**Clamp — shrink floor তুলে দিলেও overflow হয় না:** baseline (floor ০.৬০): May WIDTH "1234.56" fs ০.৬৬০৬ / width ১.০৮৮ (+৮ scan px overflow); "12345678.90" (১১ অক্ষর) width **১.৪৫১ (+৪১ px)** — চোখে দেখা: "90" cell-এর border পেরিয়ে margin-এ ঢোকে। ব্যর্থতার রূপ overflow (clip/wrap নয় — CSS `overflow:visible; nowrap`)। Floor variant (staging): ০.৫০ ভাঙে ১০ অক্ষরে; ০.৪৫ ভাঙে ১১ অক্ষরে; **০.৪০ ফিট করে ১১ অক্ষর পর্যন্ত (width ≤১.০৫৫), ভাঙে ১২-এ**; **floor ছাড়া ফিট করে ১৪ অক্ষর পর্যন্ত (width ≤১.০৫৫)**। `.tiny` flag (fs-ratio < ০.৪০ → amber outline) staging-এ পরীক্ষিত — ওঠে ১২ অক্ষরে, ১১-এ নয়, ২× clip-এ দেখা গেছে।

**প্রয়োগ (মার্জ):** Patch ১ (Lot-anchor) ৪টি r11m builder-এই লাগানো হয়েছে — May builder-দের R10 identity-box override-এর জায়গায়; Aug builder-দেরও একই mechanism হিসেবে (সেখানে ratio verdict-ই reproduce করে)। নিয়ম শুধু WIDTH identity box-এর জন্য; Lot anchor মাপা না গেলে fallback হিসেবে ratio verdict থাকে। May p2 override এখন নিয়ম দিয়েই fires: box [2083,1279,2175,1307], lotdiff **০.০৫৩২**। May p1 lotdiff ০.০৬৪, Aug p1 ০.০২০৮, Aug p2 ~০.০২৯৪ — সব R10-এর সঙ্গে মেলে। (লক্ষণীয়: R10-এর May p1 override তালিকাও খালি ছিল — r10m seg-এ ratio নিয়মই bold বলেছিল; override ছিল শুধু safety net, p1-এ কখনও fire করেনি। May p2-তে fire করেছিল।)

Patch ২ (fitWidth floor ছাড়া + `.tiny`) shared v7 builder `build_page.py` ও `build_page_may.py`-তে লাগানো হয়েছে (300-DPI builder-রা build-এর সময় template ওখান থেকেই নেয়, তাই পুনর্নির্মিত পাতায় পৌঁছায়): `f = Math.min(1.25 * fs0, f);` + `el.classList.toggle('tiny', f < 0.40 * fs0);` + CSS `.wd.tiny { outline:1.5px solid #d97706;}`।

**যাচাই:** fontfix_verify300 copy ৪৩/৪৩; live page SHA তখন অপরিবর্তিত; shared DB read-only SHA 1c065457…। কোথাও OCR ব্যবহার হয়নি; identity row label + box দিয়ে।

**মার্জের `.tiny` probe (পুনর্নির্মিত May p1 পাতায়, worst case bold):** ১১ অক্ষর "12345678.90" width ১.০৫৫, fs-ratio ০.৪০, tiny=False; ১২ অক্ষর "12345678.901" width ১.০৫৫, fs-ratio ০.৩৭, tiny=True; ১৪ অক্ষর "1234567890.123" width ০.৯৮৯, fs-ratio ০.৩১, tiny=True — **TINY PROBE: PASS**, Track C-র staging সংখ্যার সঙ্গে হুবহু মিলেছে। ১২-অক্ষরের clip চোখে দেখা: লেখা cell-এর ভেতরে, amber outline, "Hard" অক্ষত, overflow নেই।

**সৎ সীমা:** Lot-anchor threshold ০.০৩৬ একটি template (PG COA) ও ২টি ডকুমেন্টে fit করা — অন্য template-এ promote করার আগে আবার যাচাই করতে হবে; May p4–p6 bold GT অনুমান-নির্ভর (একই May ডকুমেন্ট); Lot নিজে regular-weight ধরে নেওয়া হয় (কোনো ডকুমেন্ট Lot-ই bold ছাপলে ভাঙবে — fallback ratio verdict রাখে)। সাধারণ bold classification এখনও অমীমাংসিত (সব সংকেতে obs regular বনাম bold overlap)।

## ৪. মার্জ — একটিমাত্র সামঞ্জস্যপূর্ণ v8 পাতা-সেট

- `improve/round11/merge-r11/` তৈরি; পরিবর্তনের আগে ৫টি live পাতা, root seg, `heading.py`, `fontfix_verify300.py`, `build_page.py`, `build_page_may.py` ব্যাকআপ করা হয়েছে।
- r10m seg পরিবার copy করা হয়েছে + Rav p2 r11m seg (Track B-র চূড়ান্ত seg, ৬১০ শব্দ; r10m-এ ৫৯৯ ছিল)। Rav p3 r10m ৪৪৭ শব্দ অপরিবর্তিত।
- ৪টি R10 builder copy করে r11m builder বানানো হয়েছে (`patch_builders_r11m.py` — নথিভুক্ত, আবার চালানো যায়, তবে idempotent নয়: আবার চালাতে হলে R10 copy থেকে restore করতে হয়)। পরিবর্তন: merge dir round10 → round11; heading JSON নাম r10m → r11m; r9m ব্লক সরানো (সব builder থেকে); exemplar `exemplar-pg.npy` থেকে load করে `heading_lines_guarded(..., exemplar=...)`-এ দেওয়া; Lot-anchor নিয়ম যোগ। ৪টি builder-তেই syntax OK, `r9m`/`lines_h` উল্লেখ নেই (R11 comment ছাড়া, যেখানে সরানো workaround-এর কথা বলা আছে)।
- Clean `merge-r10/cleans/` থেকে `merge-r11/cleans/`-এ byte-identical copy করা হয়েছে (১০ ফাইল, SHA যাচাই করা)।
- ৫টি পাতা নির্মাণ: Aug p1 (৩০২ শব্দ, ৭৭ bold, H1 [3,5], H2 ১৩), Aug p2 (২৯৭ শব্দ, ৭০ bold, H1 [3,5], H2 ১৩), May p1 (৩০২ শব্দ, ৪৩ bold, H1 [7], H2 ১৫), May p2 (৩০৩ শব্দ, ৪৩ bold, H1 [6,7], H2 ১৫), May p3 (৩০১ শব্দ, ৪৫ bold, H1 [6], H2 ১৪)। ৫ পাতাতেই H1/H2/flip R10-এর সঙ্গে identical।
- **WORDS JSON R10 root পাতা বনাম R11 staging পাতায় ৫ পাতাতেই byte-identical** (শব্দে শব্দে: bold flag, ratio, রং)। একমাত্র HTML পার্থক্য (base64 blob বাদ দিয়ে normalised diff): `.wd.tiny` CSS লাইন + fitWidth floor-ছাড়া পরিবর্তন ও তার comment।
- Root seg `seg-aug-p1-300.json` / `seg-may-p1-300.json` r11m seg-এর সঙ্গে byte-identical (SHA যাচাই করা)।
- Verifier পরিবর্তন (Track C প্রস্তাব অনুযায়ী): `fontfix_verify300.py`-র long-replacement চেক এখন ceiling-only (fs_ratio ≤ ১.২৫), width gate (≤১.১০) বাধ্যতামূলক চেক; বার্তায় "R11C no-floor" লেখা। May p2/p3 verifier-এর staging copy-তেও একই পরিবর্তন। R10-এর canonical May p2/p3 verifier (`merge-r10/verifiers/`-এ) পুরনো clamp wording-সহ অপরিবর্তিত আছে — R10 artifact হিসেবে ইচ্ছাকৃতভাবে ছোঁয়া হয়নি।

## ৫. Root p1 পাতা পুনর্লেখন — অসঙ্গতি, তদন্ত ও সমাধান

**যা ঘটেছিল:** Promotion-এর সময় (২০২৬-১১-০৭ ~১০:০১:৫৩ UTC) ৫টি root পাতাই staging-এর সঙ্গে byte-identical ছিল (`cmp -s` পাস)। পরে একই run-এ দেখা গেল root Aug p1 ও May p1-র SHA বদলে গেছে (Aug `bce37147…` → `e561eb3d…`, May `d0948b0f…` → `1a56cb7b…`); Aug p2, May p2, May p3 অপরিবর্তিত। mtime: aug-300 **১০:০২:৩০**, may-300 **১০:০২:৩৫** — promotion-এর ~৪০ সেকেন্ড পর।

**তদন্তের ধাপ:**
- Byte-level diff: একমাত্র পার্থক্য clean-layer base64 blob-এর ভেতরে। Aug p1 root ৯৮৮ byte লম্বা, May p1 ৫,৬৬৪ byte লম্বা। Normalised diff (blob বাদ দিয়ে) খালি — WORDS, template, JS সব identical।
- Blob শনাক্তকরণ: ৩টি embedded blob-এর মধ্যে শুধু blob ১ (auto-CLEAN) বদলেছে; ORIG ও MANUAL clean identical।
- মূল প্রমাণ: root-এর clean blob **R10 ব্যাকআপ পাতার clean blob-এর সঙ্গে হুবহু মিলেছে** (Aug `9c21a01d…`, May `f45e2fd9…`), আর R11 staging blob ভিন্ন (Aug `9d237576…`, May `371e6a33…`)।
- Pixel তুলনা: R10 clean বনাম R11 clean আসলেই ভিন্ন ছবি (Aug max diff ২৩৬, গড় ০.৫২২, ৯৯,৯৬১ px >১০; May max ২৫৫, গড় ০.০৮৬) — শুধু JPEG re-encoding নয়।
- লেখক শনাক্ত: `verify_round2_300.py` লাইন ৩১ — প্রতিবার চালানোর সময় `build_page300.py` (shared root builder) দিয়ে দুটি p1 পাতা **আবার নির্মাণ করে**। mtime (১০:০২:৩০/৩৫) fontfix run-এর শেষ ও verify_round2 run-এর শুরুর মাঝখানে পড়ে — ঠিক সেই সময়। অন্য কোনো suite script builder চালায় না (grep করে নিশ্চিত)। কোনো cron job দায়ী নয় (cron তালিকায় LSE-সংক্রান্ত job নেই)। সমান্তরাল ৪টি কাজ তখন শেষ হয়ে গিয়েছিল; ১০:০২:৩০-এ একমাত্র চলমান কাজ ছিল আমার নিজের merge।
- কারণ: `build_page300.py` root `cleans/` ডিরেক্টরি থেকে clean পড়ে — আর root cleans/ stale ছিল: ৬টি PNG পুরনো inpainting-এর (R10 merge cleans `merge-r10/cleans/`-এ পুনর্নির্মাণ করেছিল, কিন্তু root `cleans/`-এ sync করেনি)। প্রমাণ: root clean PNG (SHA `678a3156…`) বনাম M10/M11 clean (`bff1c9f1…`); `jpeg_b64(root clean, q88)` = `9c21a01d…` = বর্তমান root blob। আরও প্রমাণ: M10 staging পাতার clean blob == M11 staging blob (`9d237576…`) — R10 ও R11 merge builder একই clean দেয়; R10 ব্যাকআপ পাতাও আসলে verify_round2 rebuild ছিল, R10 merge builder-এর output নয়।

**সমাধান:**
1. ৬টি stale root clean PNG `merge-r11/backup/root-cleans-stale/`-এ archive করে M11 clean দিয়ে sync করা হয়েছে (১০/১০ SYNCED)।
2. দুটি p1 root পাতা staging থেকে restore করা হয়েছে (SHA আবার `bce37147…` / `d0948b0f…`)।
3. নির্ণায়ক পরীক্ষা: verify_round2_300 আবার চালানো হয়েছে — **১৮/১৮ PASS**, এবং rebuild-এর পর root পাতা staging-এর সঙ্গে **byte-identical** (`cmp` পাস)। অর্থাৎ sync-এর পর shared builder এখন R11 পাতা হুবহু reproduce করে (p1 পাতায় (B)-heading + ratio-bold + patched template + synced clean = R11 build)।
4. এরপর clean-সংবেদনশীল সব চেক চূড়ান্ত root পাতায় আবার চালানো হয়েছে (নিচের টেবিল)।

**Round 12-এর জন্য ফাঁদ হিসেবে নথিভুক্ত:** verify_round2_300.py-র rebuild ধাপ প্রতিটি suite run-এ root p1 পাতা আবার লেখে — এটি Round 2 থেকে চলে আসা আচরণ, এতদিন flag করা হয়নি। Round 12-এ হয় rebuild ধাপটি সরাতে হবে, নয়তো `build_page300.py`-কে বর্তমান merge builder-দের দিকে point করতে হবে।

## ৬. চূড়ান্ত যাচাই তালিকা (সব নিজে চালানো, promote-এর পর চূড়ান্ত root পাতায়)

| যাচাই | ফল |
|---|---|
| fontfix_verify300.py (root, patched) | **৪৩/৪৩** |
| verify_round2_300.py | **১৮/১৮** |
| repro300.py | **PASS** (২টি edited span, exact text, .done, doubling নেই) |
| manual_proof300.py | **১০/১০** |
| Identity probe r11m (Lot+WIDTH+Hard × ৫ পাতা) | **১৫/১৫** |
| Write-back verify_writeback300_r10 | **৪১ PASS, ০ FAIL** |
| Write-back verify_rebuild_300 | **৪০ PASS, ০ FAIL** |
| Track D staging (verify_track_d1.py) | **৪৮ PASS** |
| Track C R5 (verify_track_c_r5.py) | **৭৪ PASS** |
| May multipage (verify_may_multipage.py) | **৫৯ PASS, ০ FAIL** |
| May p2/p3 verifier (r11m staging copy) | **৪৩/৪৩** |
| sqlcipher (sqlcipher_test.py) | **১৫ PASS** |
| keymgmt (keymgmt_proof.py) | **২৫ PASS** |
| save→label LIVE (১৮/পাতা × ৫) | **৯০/৯০** |
| Aug p2 (verify_aug2_page_r10m.py, root) | **১৬/১৬** |
| Heading R1 (r10m/r9m/r8m) | **TITLE ১৪/১৪, H2 ১৪/১৪, H1-diff ০** (×৩ পরিবার) |
| Sample rows r11m | **৫১৮/৫১৮, ০ extra** |
| N5 (r11m seg) | **৭৭/৮১ strict, ৮১/৮১ improved** |
| Description (r11m seg, সংশোধিত GT) | **৬৯/৬৯, ০ ভুল** |
| Redbox (canonical R9 scorer) | **১১/৬৬** (r10m ও r11m — অপরিবর্তিত) |
| `.tiny` probe (May p1, ১১/১২/১৪ অক্ষর) | **PASS** |
| Shared DB (read-only) | SHA `1c065457…`, **৭ delivery (LSE-0001–0007), ২০ audit entry**, chain অক্ষত |

**চূড়ান্ত root SHA:** Aug p1 `bce37147…`, Aug p2 `f4f72713…`, May p1 `d0948b0f…`, May p2 `539995a9…`, May p3 `8587be86…` (promotion-এর SHA-র সঙ্গে identical)।

**দুটি গণনা-স্পষ্টকরণ:** (ক) save→label ৯০/৯০ হলো LIVE verifier (১৮ চেক/পাতা × ৫); staging verify_save_label.py দেয় ৩৪/৩৪ (R8 staging পাতায়)। (খ) Aug p2 ১৬/১৬ হলো R10 merge verifier root পাতায়; R8 script `verify_aug2_page.py` দেয় ১৫/১৫ কিন্তু সেটি নিজের R8 staging পাতা (৩০১ শব্দ, r7m seg) চেক করে — R11-এ অপরিবর্তিত stale artifact, root পাতা নয়।

**Eye-check:** May WIDTH clip (৬৭১.৫ bold, পরিষ্কার, Hard অক্ষত), Aug Lot clip (২০৭/৯ পরিষ্কার, doubling নেই), May Lot clip (৩০৫/৭ পরিষ্কার), Aug WIDTH clip (৭৮১.৫ regular, Hard অক্ষত), ১২-অক্ষরের `.tiny` clip (cell-এর ভেতরে, amber outline)। save→label live run-এ May p.2 label card: Batch/Lot ২৮৩/৭, WIDTH ৭২১.৫ mm, "May p.2 only (this pack's page)", QC PASSED, old→new (Lot ২৮২/৫ → ২৮৩/৭, WIDTH ৭২০.০ → ৭২১.৫), leak নেই।

## ৭. এখনও খোলা (সৎ তালিকা)

- Raviraj p2: E-ce ২৭ (cross-line fusion — আলাদা দুই-সারি পৃথকীকরণ algorithm লাগবে), A-logo ১৬, E-cg-1 ৫, D ৫, redbox ৫৫ (আলাদা ট্র্যাক লাগবে)।
- p3-র span-level GT করা হয়নি (R10-এর p3 +৯ এখনও R5-এর হাতে গোনার ওপর; সত্য লাভ +১২-ও হতে পারে)।
- Lot-anchor threshold ০.০৩৬ একটি template ও ২ ডকুমেন্টে fit — অন্য template-এ promote-এর আগে আবার যাচাই করতে হবে; Lot নিজে bold হলে fallback ratio verdict রাখে। সাধারণ bold classification এখনও অমীমাংসিত।
- Exemplar grey মার্জিন ৪.০–৫.৮ level — অন্য supplier-এর wash ঘনত্বে আবার মাপতে হবে; R1-এর জন্য ≥১টি (B)-flag header + ≥২ পাতায় লাইন থাকা লাগে; exemplar বাছাইয়ে gap_dark floor খোলা hardening।
- verify_round2_300.py-র rebuild side-effect — Round 12-এ সরাতে বা repoint করতে হবে (§৫)।
- Print calibration (ব্যবহারকারীর factory printer), US patent legal check (আইনজীবীর কাজ), DBNet swap deferred (KEEP CLASSICAL verdict বহাল), DPAPI VM-এ অপ্রমাণিত, `raviraj COA 20 micron.jpg` workspace-এ পাওয়া যায়নি, অন্য ২৫টি PDF পাতা শুধু contact-sheet দেখা হয়েছে।
- R10-এর canonical May p2/p3 verifier-এ পুরনো clamp wording আছে (staging copy R11C-তে update করা; R10 artifact ইচ্ছাকৃতভাবে ছোঁয়া হয়নি)।
- Staging-সংখ্যা সতর্কতা: merge-এর LSE-0008/0009 আর Track C-র staging LSE-0008/0009 একই সংখ্যা হলেও ভিন্ন DB ফাইল — সংখ্যা দিয়ে কখনও মেলানো যাবে না।

## ৮. ফাইল

- প্রতিবেদন: `improve/ROUND11-REPORT.md` (এই ফাইল); নিরাপদ copy `improve/round11/merge-r11/ROUND11-REPORT.md`
- Track A: `improve/round11/track-a/` (`track-a-report.md`, `heading_patch.diff`, `heading_patched.py`, `verify_r1.py`, `verify_grey_sens.py`)
- Track B: `improve/round11/track-b/` (`track-b-report.md`, `segs/seg-rav-p2-r11b-final.json` ৬১০ শব্দ, `verdicts-r11-final.json` ৩২৭ verdict)
- Track C: `improve/round11/track-c/` (`track-c-report.md`, `patch-proposal-r11c.md`, `scripts/`, `staging/`, `clips/`)
- Merge: `improve/round11/merge-r11/` (`segs/` r11m পরিবার, `pages/` ৫টি staging পাতা, `cleans/` ১০টি, `scripts/` ৪টি r11m builder + `patch_builders_r11m.py` + `probe_tiny_r11.py` + `check_heading_r11.py`, `verifiers/`, `exemplar-pg.npy` + `exemplar-provenance.json`, `check-heading-r11.log`, `staging-heading.py`, `backup/` R10 পাতা/seg/heading/fontfix/builder + `root-cleans-stale/` ৬টি পুরনো clean PNG, `clips/`)
- Shared পরিবর্তন: `heading.py` (R1 + guarded exemplar forwarding), `build_page.py` / `build_page_may.py` (fitWidth floor ছাড়া + `.tiny`), `fontfix_verify300.py` (long-replacement ceiling-only + width gate), root `cleans/` ৬টি PNG sync, ৫টি root live পাতা।
- Shared DB অপরিবর্তিত (read-only): `improve/round3/track-c/lse_gravora.db`, SHA `1c065457…`।

---
*Round 11 সম্পূর্ণ। পরবর্তী প্রস্তাব: Round 12 — Raviraj p2-র E-ce ২৭ (cross-line fusion) + redbox ৫৫ আলাদা ট্র্যাক, p3 span-level GT, verify_round2 rebuild ধাপের স্থায়ী সমাধান।*
