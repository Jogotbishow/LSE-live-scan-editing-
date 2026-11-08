# LSE Round 17 — রিপোর্ট

**তারিখ:** ২০২৬-১১-০৭
**মার্জ ডিরেক্টরি:** `improve/round17/merge-r17/` (v9 পাতা-সেট)
**ট্র্যাক:** A — প্রতি-লাইন adaptive word-gap threshold + CC-প্রস্থ সংকেত; B — DBNet header-zone review সংকেত + full-page CC-mask gate; C — সরু স্লটে caps retype + E-ce idx307 + bold-এর নতুন সংকেত + universality সম্প্রসারণ।
**নিয়ম:** কোনো কিছু Google Drive-এ আপলোড করা হয়নি; REPORT.md, REPORT-MAY.md, ROUND2–16-REPORT.md ছোঁয়া হয়নি; শেয়ার্ড Round 3 DB শুধু read-only যাচাই; কোথাও OCR নেই।

## ১. সারাংশ — হেডলাইন সংখ্যা

| বিষয় | ফল |
|---|---|
| Adaptive word-gap (Track A) | **REJECTED** — per-line Otsu মোট ভুল ১১০৪ (স্থির ০.২৫-এর ১৩১); 2-means ৬৩৫, jump ১৮৪৬। CC-প্রস্থ সংকেতও REJECTED। |
| SALES ভিত্তি সংশোধন | SALES\|DEPARTMENT ১৪ PG পাতার কোনোটিতেই লুকানো over-merge নয় — আলাদা seg শব্দ, ফাঁক ০.৩৬–০.৪০। একমাত্র আসল over-merge rav-p3-র QUANTITY\|NET (৯px, ০.৫৬)। |
| DBNet header-zone সংকেত (Track B) | **মানুষের review prompt হিসেবে ব্যবহারযোগ্য (প্রস্তাব)।** Signal B ২৮/২৮ আসল, false alarm ০; Signal A-তে আসল শব্দে false flag ০। কখনো auto-add/auto-merge নয়। |
| CC-mask gate (Track B) | **Gate কাজ করে: ১৬/১৬ ALLOW, সব control পাস।** কিন্তু build-time promotion পণ্য-সিদ্ধান্ত — নেওয়া হয়নি। |
| ⚠️ R16 সংশোধন | **R16-র "68.02 seg-miss / silent data loss" ভুল উৎস-ছবির আর্টিফ্যাক্ট** — R16 Track C full-page পরীক্ষা চালিয়েছিল ১৮০° ঘোরা JPG-তে। সত্যিকারের পাতায় "68.02"-র seg box আছে। মার্জ নিজে যাচাই করেছে (নিচে §৩.১)। |
| Caps retype (Track C) | **64px স্লটে কোনো পরিষ্কার ফিট নেই।** সবচেয়ে সরু ফন্ট ExtraCondensed Bold ৮৬px; সেরা আপস ExtraCondensed + ৯২px বাড়ানো স্লট। সিদ্ধান্ত নেওয়া হয়নি। |
| E-ce idx307 (Track C) | **কারণ পাওয়া গেছে** — 14px অবশিষ্ট, fused-core সিমে Telea-র অন্ধকার-ছড়ানো + ink protection; 1×-এ অদৃশ্য, নকশাগত সীমা। |
| Bold (Track C) | **অমীমাংসিতই থাকল** — নতুন VERT-RUN সিগন্যাল ১৫/২৯, FP ৩১, ০/৬ পেজে আলাদাকরণ। |
| Universality (Track C) | Track A প্রস্তুত নয় বলে VALLEY raw-default মাপা: ছাপা ডকুমেন্টে +৯ (FUNSD +৭, SROIE +২), হাতের লেখায় −২; মোট ৫৮/১০৩ বনাম ৫১/১০৩। প্রচার করা হয়নি। |
| Raviraj p2 LINES / N5 / Description / redbox / p3 | **৩২৭/৩২৭ / ৭৭/৮১ (improved ৮১/৮১) / ৬৯/৬৯ / ৬৬/৬৬ (R9: ১৫/৬৬) / ৩৩৪/৩৮৪ (improved ৩৮৪/৩৮৪)** — সব R16-র সমান, কোনো regression নেই। |
| পূর্ণ পাতা (হর ৮৮৬) | strict ক্যানোনিক্যাল **৭৮১/৮৮৬ (৮৮.১%)**, সংশোধিত ৮৩২/৮৮৬ (৯৩.৯%), improved ক্যানোনিক্যাল ৮৩৫/৮৮৬ (৯৪.২%)। |
| লাইভ পাতা | May ৩/৩ byte-identical; Aug ২ পাতায় **মাত্র ১ অক্ষর করে ভিন্ন** (SHORTLIST mean_iou ০.৬৪৪ বনাম ০.৬৪৩ — R15-র মতোই rounding-সীমানা, কার্যকরী পার্থক্য শূন্য) — **promotion লাগেনি**। |
| পূর্ণ যাচাইসূচি | মার্জের নিজের পুনঃচালনায় সব PASS (নিচে §৬) — fontfix ৪৩/৪৩, verify_round2_300 ১৮/১৮ × ২, Guard ৫/৫, identity probe ১৫/১৫, write-back ৪১/৪১ + ৪০/৪০, save→label ৯০/৯০। |

## ২. Track A — প্রতি-লাইন adaptive threshold + CC-প্রস্থ সংকেত (REJECTED)

### ২.১ ফল — মোট ভুল (false merge + false split, ১৬ পাতা)

| নিয়ম | মোট ভুল |
|---|---|
| স্থির ০.২৫ (নিয়ন্ত্রণ, R16-র প্রত্যাখ্যাত নিয়ম) | **১৩১** |
| per-line Otsu | **১১০৪** |
| per-line 2-means | **৬৩৫** |
| per-line largest-jump | **১৮৪৬** |
| page-Otsu-clip V1 (বাড়তি পরীক্ষা) | **৭৮** |
| guarded per-line V4 | **১০০** |

Per-line Otsu-র false split প্রতি PG পাতায় **৫৭–৮৪টি** (স্থির নিয়মে ০–৬টি); min_class=৪ করলে আরও খারাপ (১০৬–১৪১/পাতা)। **মার্জ নিজে পরিমাপ-কোড পুনঃচালিয়ে নিশ্চিত করেছে** — প্রতি-পাতা টেবিলের ১৬×৪টি সংখ্যাই আমার পুনঃচালনার সঙ্গে হুবহু মিলেছে (মোট ১৩১ / ১১০৪ / ৬৩৫ / ১৮৪৬)।

**কেন ভাঙে:** এক লাইনের gap বণ্টন bimodal নয় — লাইনে আসল WORD ফাঁক ৩–৮টি বনাম ~২৫টি intra ফাঁক। aug-p1-এ ৪টি লাইনে letter-letter শ্রেণিতে আসল WORD ফাঁক একটিও নেই, আর সেই ৪ লাইনেই ৬৫টি false split-এর **৩৮টি**। SALES লাইনে per-line Otsu ঠিকই কাজ করে (১৪/১৪ পাতায় FS=০, thr ০.২৩–০.৩৪) — কিন্তু পাতার বাকি ~১৩ লাইনে ভেঙে পড়ে, তাই promote করা যায় না। SALES লাইনের FM ২–৩টি/পাতা সব DEPARTMENT-এর over-split আর্টিফ্যাক্ট (`DEPAR|T|MENT` ০.০৭–০.১৫) — কোনো gap-threshold-ই ঠিক করতে পারে না।

**পুনরুৎপাদন যাচাই (মার্জ):** aug-p8 সংখ্যা R16 seg-line-এর সঙ্গে অক্ষরে অক্ষরে মিলেছে; aug-p1 gap-সারি ১২৮৬/১২৮৬ অভিন্ন।

### ২.২ ব্রিফের ভিত্তি সংশোধন — SALES|DEPARTMENT কোথাও লুকানো over-merge নয়

**১৪টি PG পাতার কোনোটিতেই SALES|DEPARTMENT এক seg বাক্সের ভেতরে লুকিয়ে নেই** — সব পাতায় SALES ও DEPARTMENT আলাদা seg শব্দ, ফাঁক ০.৩৬–০.৪০ (WORD gap, ইতিমধ্যে আলাদা)। R16-র "০.৪০" সংখ্যাটি এই WORD ফাঁকই। aug-p8-এর একমাত্র ১০px intra ফাঁক (০.৩৫৭) Document No. লাইনে (slash-সংলগ্ন আর্টিফ্যাক্ট), SALES লাইনে নয়। **১৬ পাতায় আসল over-merge (intra gap ≥ ০.৩৫) মাত্র একটি: rav-p3-র QUANTITY|NET (৯px, ০.৫৬)** — per-line Otsu (thr ০.৩৭৫), page-Otsu-clip (০.৩৩৩) ও স্থির ০.২৫ — তিনটিই একে ঠিকভাবে ভাগ করে।

### ২.৩ CC-প্রস্থ সংকেত — নির্ধারক জোড়ায় কাজ করে, সাধারণ নিয়মে নয়

নির্ধারক জোড়া (aug-p1, SALES লাইন, চোখে যাচাই করা): BY|SALES (WORD, ৬px, ০.২৩) — দুই পাশ Y (২১px) ও S (২০px), `minw_n` **০.৭৭**; LIMITED-র M|I (intra, ৬px, ০.২৩) — দুই পাশ M (৩১px) ও I (**৬px**), `minw_n` **০.২৩**। একই ৬px ফাঁক, প্রস্থ দিয়ে আলাদা করা যায় — R16-র অনুমান এই জোড়ায় সত্যি। **কিন্তু পাতা-জুড়ে ভেঙে যায়:** WORD ও intra-র `minw_n` median প্রতি পাতায় প্রায় অভিন্ন (০.৫৫ বনাম ০.৫৬; ০.৬৮ বনাম ০.৬৮; ০.৭৮ বনাম ০.৭৮)। দ্বিধাগ্রস্ত band ০.২০–০.৩০-এ প্রতি PG পাতায় WORD ফাঁক মাত্র **১টি** (BY|SALES-ই), intra ফাঁক ১৪–৬২টি। GRAMMAGE-শ্রেণির ৭px intra ফাঁকে দুই পাশই ২৯px M (`minw_n` **১.০২–১.০৫**) — প্রস্থ-শর্ত এগুলোকে ভুলভাবে ভাগ করবে। যৌথ নিয়ম (`gap_n > tg AND minw_n ≥ tw`) grid-সেরা ফল ১৪/১৬ পাতায় gap-একক নিয়মের সমান; শুধু rav-p3-এ in-sample fit-এ FM ১→১৪-এর বিনিময়ে FS ৩৪→৮ (মোট ৩৫→২২) — এক পাতায় fit করা মান, নিয়ম নয়।

### ২.৪ page-Otsu-clip (V1) — ভালো, কিন্তু bar পার হয় না

V1 মোট ভুল **৭৮** (স্থির ১৩১): Aug ৩০ (স্থির ৫৩), May ২৪ (সমান), rav-p2 ১৯ (সমান — unclipped page-Otsu thr **১.২৬৭** দিয়ে ১৩১টি false merge করেছিল), rav-p3 ৫ (স্থির ৩৫)। **তবু ব্যর্থ:** V1-এর false merge-এ BY|SALES আছে **১২/১৪** PG পাতায়। তাই V1 একটি ভালো threshold-অনুমানক হতে পারে, কিন্তু SALES-সমস্যার সমাধান নয় — **পরীক্ষামূলক মাত্র** (`adaptive_gap.py`-তে "DO NOT PROMOTE" সতর্কতা সহ রাখা হয়েছে)।

**চোখে যাচাই (মার্জ):** `a1-limited-mi.png` — "M/s PACKFIRM LIMITED"-এ M|I ৬px ফাঁক স্পষ্ট (লাল টীকা আংশিক অক্ষরের ওপরে পড়েছে — শুধু টীকা, ফাঁক স্পষ্ট)।

## ৩. Track B — DBNet header-zone review সংকেত + CC-mask gate

### ৩.১ R16 সংশোধন — "68.02 seg-miss" ভুল উৎস-ছবির আর্টিফ্যাক্ট (মার্জ নিজে যাচাই করেছে)

**তথ্য:** R16 Track C full-page পরীক্ষা চালিয়েছিল `improve/round4/track-d/aug-p2-orig.jpg`-তে। ঐ JPG **আসল পাতার তুলনায় ১৮০° ঘোরা**। **মার্জ নিজে মেপে নিশ্চিত করেছে:** সত্যিকারের PNG (`improve/round4/track-a/pages/aug-p2-300.png`)-র সঙ্গে mean abs diff না-ঘুরিয়ে **২৭.৮০**, ১৮০° ঘুরিয়ে **০.৪৪** (Track B-র সংখ্যা ২৭.৯৬ বনাম ১৭.০৬ — আমার ১৮০° ঘূর্ণন আরও ভালো মেলে)। `g2-mirror-test.png` চোখে দেখেছি — মাঝের প্যানেলে (JPG as-is) "PG Foils Ltd." উল্টো নিচে; R16-র নিজের `eye-blobc.png`-তেই ORIG প্যানেলে লেখা উল্টো ("20·89" = "68.02" ১৮০° ঘোরা)।

**সত্যিকারের "68.02":** PNG-তে মানটি x২০৯৭–২১৮৭, y১৩৯৪–১৪২২-এ — এবং তার **seg box আছে: [২০৯৭,১৩৯৪,২১৮৭,১৪২২]** — মার্জ নিজে seg-ফাইলে (`seg-aug-p2-r10m.json`, ২৯৭ শব্দ) হুবহু পেয়েছে, আর `g4-true-6802-png.png` চোখে দেখেছি — সবুজ বাক্স "68.02"-কে হুবহু ঘিরেছে।

**Blast radius (মাপা, অতিরঞ্জন নয়):**
- **প্রভাবিত:** R16 Track C-র full-page ফলাফল — mask ৩৯৭,৬৬১→৬৯,০৫৮ ("rule exclusion grid ধ্বংস সারায়"), only-CC ৭,৮৭৯ / only-v4 ৪৩,১১০ px, ghost-in-box ২,৭০৯, "68.02 seg-miss / silent data loss" সিদ্ধান্ত, `compare_cleans.py`, `bold_signal.py`-র aug-p2 entry — সবই ঘোরা JPG + unrotated seg-এ চলেছে। ROUND16-REPORT-এর §৪ ও §৭-এর ঐ-সংক্রান্ত বাক্যগুলোও। (Track B-র দাবি — mirror R16-র সংখ্যা হুবহু পুনরুৎপাদন করে — মার্জ নিজে পুনঃচালায়নি; ঘূর্ণন + seg box-ই নির্ণায়ক প্রমাণ।)
- **প্রভাবিত নয়:** R16 Track C-র single-word erase/retype/ghost পরীক্ষা (সব `rav-p2-300-rot.png`-এ — সঠিক orientation; E-ce `and`→`or` প্রমাণ, Bank's/Nothing's অপরিবর্তিত), live page, শেয়ার্ড DB, Track A ও B, DBNet eval।
- Rule exclusion-এর ধারণাটি safety net হিসেবে এখনো সঠিক (§৩.৩) — শুধু R16-র সংখ্যাগুলো ভুল ছবিতে মাপা। সঠিক পাতায় টেবিল-grid-এর দৈত্যাকার core (১৯৮,৫৮৭ px) assign হয় **-1 (unassigned)** — তার pixel কোনো word box-এর ভেতরে পড়ে না, তাই mask-এ ঢোকেই না। ঘোরা JPG-তে একই core assign হয় **-2 (ambiguous)** — ঘূর্ণনে grid-রেখা unrotated box-গুলোর ভেতর দিয়ে যায় — আর `full_page_clean` -2 core-কে পুরোটা mask-এ ঢোকায়; তাই ৩৯৭k।

### ৩.২ Part 1 — DBNet header-zone review সংকেত (ব্যবহারযোগ্য, প্রস্তাব হিসেবে)

DBNet প্রথমবার aug-p4–8 / may-p4–6-তে: ১২৪–১২৬ line box/পাতা, median ১০৫২–২৭৬০ ms (aug-p4 ২৭৬০ ms একটিই outlier, reps=2)। মোট ১৬ পাতা: ৫১৬০টি seg শব্দ, ২২৭টি miss-hunt cluster, তার মধ্যে DBNet লাইনের ভেতরে ১৯৭টি।

**সংকেতের সংজ্ঞা (spec — প্রস্তাব):** ZONE — header band, বাক্সের centre-y < **২৮৫ px**। Signal A (coverage flag): zone-র ভেতরের classical শব্দ, যার ক্ষেত্রফলের <৫০% কোনো DBNet line AABB-র ভেতরে + non-word ফিল্টার (h<৮, w<১২, area<১২০, long-thin rule)। Signal B (miss-hunt): uncovered-CC cluster (R16 অ্যালগরিদম) যার centre zone-এ + DBNet লাইনের ভেতরে ≥৫০% + word-like (n_cc≥২, h≥১২, w≥২০, area≥১৫০, median CC height≥১০)। Exclusion: signature zone (y0 ≥ sig_y)। **v4 LOGO আয়তক্ষেত্র (১৫০,১২০,৫১০,৪৫০) ইচ্ছাকৃতভাবে বাদ দেওয়া হয়নি** — মাপা কারণ: PREM/GROUP ১৪ পাতাতেই পুরোপুরি ঐ আয়তক্ষেত্রের ভেতরে (২৮/২৮ cluster-এ `in_logo_rect=True`); logo exclusion দিলে প্রমাণ-কেসটিই মুছে যেত।

**ফল — false-flag হার আগে/পরে (মাপা):**

| | flag | আসল | false alarm |
|---|---|---|---|
| Signal B আগে — page-wide, DBNet-লাইনের ভেতরের cluster | ১৯৭ | ২৮ | **১৬৯ (৮৬%)** |
| Signal B পরে — zone + word-like + sig-exclusion | **২৮** | **২৮** | **০** |
| Signal A আগে — page-wide (tiny+rule ফিল্টার-সহ) | ২৩ | ১০ (সব rav-p2-তে) | ১৩ |
| Signal A পরে — header zone-ই | **৩** | **০** | **৩ (০.১৯/পাতা)** |

প্রতি PG পাতায় ঠিক ২টি করে — **২৮/২৮ শব্দ, ১৪/১৪ পাতা** (R16-এ ছিল ১২/১২, ৬ পাতা)। নতুন ৮ পাতাতেও PREM/GROUP আছে। Raviraj পাতায় Signal B ০ (আসল miss-ও ০)। পরের ৩টি candidate-ই চোখে যাচাই করা non-word: aug-p8 খালি বাক্স [১৫৬,৭৮,২৯৮,৯৮], rav-p2 logo-arc [৫৮৮,১৫৬,৮০৭,২৫৭], rav-p3 stamp-টুকরো [২১৬৪,২৫৪,২২৬২,৩১১]। আগের ১০টি আসল শব্দের ভাঙন R16-র হাতে-গোনা ১০-এর সঙ্গে মিলেছে (decimal সারির ৮টি + `Consignee` + `MOHAKALI`)।

**চোখে যাচাই (মার্জ):** `c10-prem-all14.png` montage — ১৪ পাতার সবকটিতেই "PREM" ও "GROUP" সবুজ বাক্সে হুবহু ঘেরা, ২৮/২৮ চোখে নিশ্চিত।

**সৎ সীমা:** Ink fill আলাদা করে না (মাপা negative: logo-arc ০.৩৯৩, stamp ০.৫৬৩ বনাম PREM ০.৩১৪); tiny-ফিল্টার আসল ১-অক্ষরের শব্দকেও (যেমন "I") Signal A থেকে বাদ দেবে; aug-p5-এ v4-র ২.২× নিয়মে sig_y নীরবে নিষ্ক্রিয় (মাত্র ১টি tall CC); Raviraj-এ header-zone অন্যরকম (২১টি শব্দ); DBNet timing ব্যবহারকারীর i5-এ মাপা হয়নি।

**রায় (১):** Header-zone review সংকেত **মানুষের review prompt হিসেবে ব্যবহারযোগ্য** — Signal B ২৮/২৮ আসল, ০ false; Signal A-তে আসল শব্দে false flag ০, মাত্র ০.১৯টি non-word prompt/পাতা। শর্ত: **কখনো auto-add/auto-merge নয়**। UI-তে বসানো ও header-zone-র DPI-স্কেলিং পণ্য-সিদ্ধান্ত। Page-wide flag হিসেবে ব্যবহার **নিষেধ** — R16-র রায় বহাল।

### ৩.৩ Part 2 — Full-page CC-mask gate (কাজ করে; promotion পণ্য-সিদ্ধান্ত)

**Gate-এর ডিজাইন (`gate_ccmask.py`):** দুটি স্বাধীন পরীক্ষা — যেকোনো একটি REFUSE করলেই gate REFUSE। T1 core-outside: word-এ assign করা প্রতিটি letter-core প্রায় পুরোটা ঐ word-র box-এর ভেতরে থাকতে হবে (box-এর বাইরে core-pixel >৫০% **এবং** box ছাড়িয়ে >৬ px; guard: core_px ≥১০০, letter-shape, band/rule core বাদ; -1/-2 core T1-এর বিচারের বাইরে)। T2 word-like uncovered cluster (R16 miss-hunt clustering + word-like শর্ত + logo rect / signature zone / rule-আকৃতি exclusion)। Signature detector gate-নিজস্ব ১.৮× (v4: ২.২×) — aug-p5-এ ২.২×-এ মাত্র ১টি tall CC, sig_y নীরবে h=৩৪৬৭-এ পড়ে; ১.৮×-এ ৮টি tall CC, min y=২৮৫৬। Shared `inpaint.py` v4 ছোঁয়া হয়নি।

**ফল — gate verdict (১৬ পাতা + control):** ১৬/১৬ সঠিক পাতায় **ALLOW** (T1=০, T2=০)। Control সব পাস: ঘোরা JPG as-is **REFUSE** (T1=১৩৮, T2=২৫৩); JPG ১৮০° ঘুরিয়ে ফিরিয়ে **ALLOW** (T1=০, T2=০); synthetic miss — aug-p2 idx203 ("TEXT") বাক্স মুছে **REFUSE** (T2=১, box ঠিক [৩১০,২০৩০,৩৯০,২০৫৮]); may-p1 idx100 বাক্স মুছে **REFUSE** (T2=১, box ঠিক [১৪২৫,১১৩৪,১৬১৭,১১৬১])। **মার্জ নিজে `run_gate_batch.py` পুনঃচালিয়ে নিশ্চিত করেছে** — ১৬/১৬ ALLOW, ঘোরা JPG REFUSE (T1=১৩৮, T2=২৫৩), ঘুরিয়ে-ফেরানো ALLOW, দুটি synthetic miss-ই ঠিক বাক্স-সহ REFUSE।

**Rule exclusion পুনঃমাপ — সঠিক orientation-এ (৬ পাতা, সব ৫টি লাইভ পাতা-সহ): ০টি core বাদ, mask px অপরিবর্তিত** (যেমন aug-p1 ৪৩৪,১২২→৪৩৪,১২২; may-p2 ৪৭০,৭৬৪→৪৭০,৭৬৪)।

**সৎ সীমা:** T1-র margin পাতলা — নিকটতম সঠিক কল rav-p2 core [৫৩৪,১৭৮৪,৫৬৫,১৮০৯], frac **০.৪৮৪**, threshold ০.৫০ থেকে মাত্র ০.০১৬ দূরে (পাশের শব্দের "I"-অক্ষর box-এর কিনারা ছুঁয়েছে — benign straddle, চোখে যাচাই করা)। Gate-এর নিরাপত্তা T1+T2 একসঙ্গে দেয়, T1 একা নয়।

**রায় (২):** Gate **safety component হিসেবে কাজ করে**, কিন্তু build-time promotion **পণ্য-সিদ্ধান্ত, নেওয়া হয়নি**। Promotion-এর আগে দরকার: (ক) T1-র পাতলা margin আরও পাতায় যাচাই — ২৫টি অন্যান্য PDF পাতা এখনো শুধু contact-sheet দেখা; (খ) -2 (ambiguous) core-কে mask-এ পুরোটা ঢোকানোর R16-আচরণের পর্যালোচনা — May-র dotted band core (~১৩k px) এখন mask-এ ঢোকে, সেটি উদ্দেশ্যমূলক কিনা পণ্য-সিদ্ধান্ত।

## ৪. Track C — Caps retype + E-ce idx307 + bold + universality

### ৪.১ সরু স্লটে caps retype — 64px-এ কোনো পরিষ্কার ফিট নেই

**স্লটের মাপ (মাপা):** L41 `and` (r15m idx310) বাক্স [809,1427,873,1464], আসল কালি 64×37px। বামে `Name` শেষ 796 (ফাঁক 13px), ডানে `Address` শুরু 888 (ফাঁক 15px)। **ফাঁকসহ সর্বোচ্চ 64+13+15 = 92px** (শূন্য clearance)। Caps-এর উচ্চতা 37px ধরতে হবে — ছোট করলে পাশের অক্ষরের সঙ্গে মিলবে না।

**আটটি ফন্টে `AND` @ 37px cap-height (মার্জ নিজে `caps_test.py` পুনঃচালিয়ে নিশ্চিত করেছে):** DejaVu Sans Bold 122px, DejaVu Sans regular 110px, Liberation Sans Bold 114px, Liberation Sans Regular 112px, Noto Sans Bold 114px, Noto Sans SemiCondensed Bold 104px, Noto Sans Condensed Bold 93px, **Noto Sans ExtraCondensed Bold 86px** (সবচেয়ে সরু)। 64px-এ কোনোটিই ফিট করে না; 92px বাড়ানো স্লটে শুধু ExtraCondensed ফিট করে (দুই পাশে 3px করে ফাঁক)। Squeeze: DejaVu Bold 122→64px মানে x-scale **0.525**, ExtraCondensed 86→64px মানে **0.744**। Shrink-to-fit করলে cap-height 37 → **19.4px** — পাশের লেবেলের অর্ধেক উচ্চতা। **ডকুমেন্টের নিজের ফন্টেও একই কথা:** DHAKA/BANGLADESH থেকে স্কেল করলে `AND` হয় **87.7px / 90.5px** — Document DNA দিয়েও 64px-এ বসবে না।

**চোখে যাচাই (মার্জ, `caps-methods-3x.png`):** CONDENSED ExtraCond 86px @ 92px স্লট — পড়া যায়, অক্ষরের আকৃতি স্বাভাবিক; তবে `A` প্রায় `Name`-এর `e`-কে ছোঁয়, `D` প্রায় `Address`-এর `A`-কে ছোঁয়, আর caps পাশের lowercase লেবেলের চেয়ে দৃষ্টিকটুভাবে বড়/ভারী লাগে। SQUEEZED DejaVu ×0.52 — `A`/`N` স্পষ্ট চাপা, `D` পিষ্ট, 3×-এ বিকৃতি চোখে পড়ে। SQUEEZED ExtraCond ×0.74 — ×0.52-এর চেয়ে ভালো, তবু স্ট্রোক পাতলা ও `N`-এর কর্ণ ঠাসা।

**রায় (সিদ্ধান্ত নয়, মাপা ফল):** 64px স্লটে caps retype-এর কোনো পরিষ্কার সমাধান নেই। সেরা আপস ExtraCondensed Bold + স্লট 92px-এ বাড়ানো — অক্ষর অবিকৃত, কিন্তু প্রতিবেশীর ফাঁক খেয়ে ফেলে (13/15px → 3/3px)। প্রস্তাব (অনুমোদনের অপেক্ষায়): caps retype শুধু স্লট-বাড়ানো + ব্যবহারকারীর নিশ্চিতকরণে অনুমোদন করা, অথবা lowercase সাজেশন দেওয়া। এই সিদ্ধান্ত Track C নেয়নি।

### ৪.২ E-ce idx307 — কারণ পাওয়া গেছে (98.98%)

**পুনরুৎপাদন (মার্জ নিজে `idx307_probe.py` পুনঃচালিয়ে নিশ্চিত করেছে):** pass-1 erase-এ একই ফল — `core_rem = 98.98%`, `R_tgt = 2626px`, `core_before = 1378px`, অবশিষ্ট **14px**। 14px-ই y1462–1463 সারিতে (ysplit=1465-এর ঠিক ওপরে ২–৩ সারি), ৩টি ক্লাস্টারে (x452–453, x461–463, x471–477); আগে grey ~95 → পরে ~130 (140-এর নিচেই থাকে)। 14px-ই দুটি ambiguous (ফিউজড) কোরের অংশ: cc3513 [449,1459,16,17] ও cc3411 [466,1439,16,37] — দুটোতেই up=307, lo=312/313, ysplit 1465। 14px-ই অন্য শব্দের বাক্সের ভেতরে এবং অন্য শব্দের core-কালি থেকে **0.0px দূরে** (স্পর্শ করে আছে)।

**কার্যপ্রণালী:** (১) Telea ভরাট অন্ধকার টেনে আনে — অবশিষ্ট সারিগুলো target-অর্ধেকের সবচেয়ে নিচের সারি; ঠিক নিচেই ysplit-এর ওপারে মাস্ক-না-করা ঘন কালো L42 value-সারির কালি। (২) Pass 2-ও সারাতে পারে না — নকশাগতভাবে: pass 2-এর পরেও `core_rem = 98.98%` (অপরিবর্তিত), যদিও ghost <210 কমে 1409 → 330px; কারণ 14px-ই **ink_prot-এর ভেতরে** (14/14) — pass-2 মাস্ক নকশা অনুযায়ী প্রতিবেশীর কালি ছোঁয় না।

**কেন শুধু 307?** ysplit সবচেয়ে গভীর (1465 বনাম 1459 — বাক্স সবচেয়ে লম্বা, y1 1475 বনাম 1464); 9টি ambiguous কোর জড়িত (সবচেয়ে বেশি); তিনটি value শব্দের সঙ্গে ওভারল্যাপ; R_tgt-এর **43.1%** অন্য core-কালির 2px-এর মধ্যে (308: 14.3%, 309: 4.6%, 310: 9.1%, 311: 6.5%)। **সংশোধন লক্ষণীয়:** R16-র idx310 নিয়ন্ত্রণ-সংখ্যা ("R_tgt-এর 0% অন্য core-কালির কাছে") ভুল ছিল — সঠিক 9.1% (72/787); 307-এর 43.1% শ্রেষ্ঠত্ব তাতে বদলায় না।

**রায়:** 98.98% কোনো বাগ বা মাপার ভুল নয় — ফিউজড-কোর সিমের নকশাগত সীমা। দৃশ্যমান ক্ষতি শূন্য (1×-এ অদৃশ্য), R_other survival 100% অক্ষত।

### ৪.৩ Bold — নতুন সিগন্যালেও অমীমাংসিত

**নতুন সিগন্যাল (মূল অনুমান):** median **vertical ink-run length / word height** — bold অক্ষরের স্ট্রোক মোটা, তাই উল্লম্ব স্ক্যানলাইন অক্ষরের ভেতরে বেশি পিক্সেল ধরে থাকে। নিয়ম একটাই, আগে থেকে ঠিক করা: line median > 1.15 × page anchor। নিয়ন্ত্রণ: median horizontal run / height, ink density।

| সিগন্যাল | ধরা (29-এর মধ্যে) | ভুল ধরা (FP) | আলাদা হয় এমন পেজ |
|---|---|---|---|
| **VERT-RUN (নতুন)** | **15/29 = 51.7%** | **31** | **0/6** |
| HORIZ-RUN (নিয়ন্ত্রণ) | 18/29 = 62.1% | 34 | 0/6 |
| DENSITY (নিয়ন্ত্রণ) | 15/29 = 51.7% | 20 | 1/6 (may-p2, মাত্র 0.007 ব্যবধানে) |
| R16 line-median ratio | 10/29 = 34.5% | — | 0/6 |

**মার্জ নিজে `bold_signal2_out.txt` যাচাই করেছে:** aug-p1 VERT-RUN 11/11 (FP 2; min bold 1.272 বনাম max regular 1.423 — ওভারল্যাপ); aug-p2 VERT-RUN 1/10 (5টি bold লাইন line_med-এই নেই), max regular **4.474**; HORIZ-RUN aug-p2 max regular **12.531**। **কেন ব্যর্থ — মাপা কারণ:** (১) টেবিলের রুল শব্দের বাক্স ভেদ করে ঢোকে — aug-p2 লাইন 20 (regular) HORIZ-RUN **12.53×** (ব্যান্ডে পুরো প্রস্থের টেবিল-রুল, চোখে যাচাই করা); লাইন 22 VERT-RUN **4.47×** (উল্লম্ব কলাম-রুল)। Run-length সিগন্যাল অক্ষরের পুরুত্বের বদলে রুলের দৈর্ঘ্য মাপে। (২) Page anchor মিশ্র পেজে প্রতিনিধিত্ব করে না — aug-p8-এ 14টি regular লাইনের মধ্যে 12–13টি ধরা পড়ে। (৩) কোনো পেজেই bold/regular আলাদা হয় না।

**রায়:** Bold classification **অমীমাংসিতই থাকল**। কোনো সিগন্যাল প্রচার করা হচ্ছে না। আগের মতোই একমাত্র কার্যকর পদ্ধতি: Lot-anchor (একক known-regular শব্দ, PG-only, 0.036 HOLD) + heading flip।

### ৪.৪ Universality সম্প্রসারণ — VALLEY raw-default (Track A প্রস্তুত নয়)

Track A-র ডিরেক্টরি যাচাই করে দেখা গেছে তার নিয়ম **প্রস্তুত নয়**: নিজের মডিউল `adaptive_gap.py`-র শিরোনামে লেখা — **"STATUS: EXPERIMENTAL — DO NOT PROMOTE"**; universality নমুনার জন্য কোনো seg ফাইল নেই, কোনো ready-marker নেই। তাই নির্দেশ অনুযায়ী **VALLEY raw-default** পরীক্ষা করা হয়েছে। **মার্জ নিজে AUTHORITATIVE স্কোরার (`improve/round16/track-a/scorer.py`) পুনরায় চালিয়ে নিশ্চিত করেছে — আউটপুট `scorer_out.txt`-এর সঙ্গে byte-identical, PROBLEMS: none।** কোনো সংখ্যা হাতে গোনা হয়নি।

| ডকুমেন্ট | Base (old) | VALLEY (old) | পার্থক্য |
|---|---|---|---|
| FUNSD | 20/38 (52.6%) | **27/38 (71.1%)** | **+7** |
| SROIE | 3/16 (18.8%) | **5/16 (31.2%)** | **+2** |
| Tottel | 16/24 (66.7%) | 16/24 (66.7%) | 0 (seg অভিন্ন) |
| Shields (হাতের লেখা) | 12/25 (48.0%) | **10/25 (40.0%)** | **−2** |
| **প্রতি মোডে মোট** | **51/103 (49.5%)** | **58/103 (56.3%)** | **+7** |
| সব মোড মিলিয়ে (Rule D-এর আগে) | 93/182 (51.1%) | — | — |
| সব মোড মিলিয়ে (Rule D-এর পরে, তুলনার জন্য) | 94/182 (51.6%) | — | +1 (শুধু SROIE base L6 "4.95") |

VALLEY-র লাভ ছাপা ডকুমেন্টে (FUNSD +7, SROIE +2), কিন্তু হাতের লেখায় (Shields) **ক্ষতি −2** — valley সেখানে "wanted" ও "and" দুই ভাগ করে। **রায়: VALLEY raw-default মাপা হয়েছে, প্রচার করা হয়নি।** Track A-র per-line adaptive নিয়ম এখনো প্রস্তুত নয় — universality-র পরের পরীক্ষা সেই নিয়ম প্রস্তুত হলে তবেই হবে।

## ৫. মার্জ — v9 পাতা-সেট (কোনো seg বদলায়নি, promotion লাগেনি)

- তিনটি ট্র্যাকের কোনোটিই প্রকাশিত seg বদলায়নি (Track A শুধু মেপেছে; Track B শুধু মেপেছে; Track C আলাদা মডিউলে কাজ করেছে) — তাই v9 সেট = r15m পরিবারই। `merge-r17/segs/` r15m-র সঙ্গে `diff -r`-এ **অভিন্ন** (মার্জ নিজে যাচাই করেছে)।
- r17m builder দিয়ে ৫টি লাইভ পাতা `merge-r17/pages/`-এ পুনর্নির্মাণ করা হয়েছে — **May ৩/৩ root-এর সঙ্গে byte-identical; Aug p1 / Aug p2 মাত্র ১ অক্ষর করে ভিন্ন** — SHORTLIST "Document DNA Regular" mean_iou **০.৬৪৪ বনাম ০.৬৪৩** (root), একই offset (p1: 796964, p2: 800068) — R15-র মতোই rounding-সীমানার মান (~০.৬৪৩৫)। R16-র rebuild ৫/৫ identical ছিল; এই রানে সীমানা আবার ওপরে গেছে। এটি diagnostic font-match স্কোর, কোনো শব্দ/বাক্স/ছবি/এডিট আচরণ নয় — কার্যকরী পার্থক্য **শূন্য**।
- Heading JSON ৫টি R11-র সঙ্গে ৫/৫ identical (মার্জ নিজে `cmp` দিয়ে যাচাই করেছে)।
- **সিদ্ধান্ত: promotion নয়।** R11-এ তৈরি root পাতাই ক্যানোনিক্যাল থাকবে।

## ৬. পূর্ণ যাচাই তালিকা (মার্জের নিজের পুনঃচালনা — ট্র্যাকের সংখ্যা নয়)

| পরীক্ষা | ফল |
|---|---|
| LINES, combined r15m (`rescore_lines_r17m.py`, merge-r17 কপিতে) | **৩২৭/৩২৭** (ok ২১৯ + correct ১০৮) |
| N5 strict / improved | **৭৭/৮১ / ৮১/৮১** (per-line R14-র সঙ্গে হুবহু) |
| Description (r10 GT) | **৬৯/৬৯, wrong ০** (নোট: পুরনো r9 GT দিলে ৬৩/৬৯ — r9 GT stale, r10 GT-ই ক্যানোনিক্যাল) |
| redbox (r12 / R9) | **৬৬/৬৬ / ১৫/৬৬** |
| p3 strict / improved | **৩৩৪/৩৮৪ / ৩৮৪/৩৮৪** (SPLIT/MERGE/MISS ০/০/০, FP ১৬) |
| পূর্ণ পাতা গাণিতিক যাচাই (R12 সূত্র: ৩২৭ + ১৫ + ১০৫ = ৪৪৭; ৩২৭ + ৬৬ + ১০৫ = ৪৯৮; improved ৪৫১) | **৪৪৭/৫০২, ৪৯৮/৫০২, ৪৫১/৫০২; পূর্ণ পাতা ৭৮১/৮৮৬, ৮৩২/৮৮৬, ৮৩৫/৮৮৬** ✓ |
| PG sample | **৫১৮/৫১৮, extras ০** |
| fontfix_verify300 | **৪৩/৪৩** |
| verify_round2_300 (rebuild ধাপ RETIRED) | **১৮/১৮ × ২ বার, SHA+mtime অপরিবর্তিত** |
| repro300 | **PASS** (২টি edited span, exact text, .done, doubling নেই) |
| manual_proof300 | **১০/১০** |
| Guard check (full mode, ৫ পাতা, probe-এর আগে) | **৫/৫ PASS** (C1–C5 সব, exit ০) |
| identity probe (ফিক্সড r14m প্রোব, merge-r17 seg) | **১৫/১৫ PASS** (Lot+WIDTH+Hard × ৫; ক্লিপ চোখে যাচাই: Aug p2 WIDTH ৭৭৬.৫ পরিষ্কার, "Hard" অছোঁয়া) |
| write-back (R10) | **৪১/৪১ + ৪০/৪০, FAILURES: none** |
| Track D staging | **৪৮/৪৮, FAILURES: none** |
| Track C (R5) staging | **৭৪/৭৪, FAILURES: none** |
| May multipage | **৫৯/৫৯, FAILURES: none** |
| May p2/p3 (r17m verifier) | **৪৩/৪৩ PASS** |
| sqlcipher_test.py | **১৫/১৫, FAILURES: none** |
| keymgmt_proof.py | **২৫/২৫, FAILURES: none** |
| save→label LIVE (১৮/পাতা × ৫) | **৯০/৯০** |
| Aug p2 (r10m verifier) | **১৬/১৬** (Hard neighbour untouched) |
| heading R1 (check_heading_r17m.py) | **PASS ১৪/১৪ × ৩ family** (TITLE ১৪/১৪, H2 ১৪/১৪, control-এ H1-diff ২ প্রত্যাশিত) |
| Universality scorer (R16 authoritative) | **byte-identical** to `scorer_out.txt`, PROBLEMS: none |
| শেয়ার্ড DB (read-only) | SHA `1c065457…`, chain **(True, ২০, None)**, LSE-0001–0007, ১৪টি edit — অপরিবর্তিত |

**নোট:** Round 4-র পুরনো `verify_writeback300.py` এখনো তার ৪টি known ink-IoU fail দেখায় (৩৭ PASS) — v1 staging artifact, superseded, regression নয় (R15/R16-র নোটের মতোই; মার্জ নিজে চালিয়ে নিশ্চিত করেছে — ৪টি fail ঠিক সেই পরিচিত IoU fail-গুলোই: aug Lot, aug WIDTH, may Lot, may WIDTH)।

**মার্জ-প্রক্রিয়ার সৎ নোট (দুটি নিজের ভুল, দুটোই ধরা পড়ে ঠিক করা হয়েছে; R16-র কোনো বিষয়বস্তু শেষ পর্যন্ত বদলায়নি):**
1. Identity probe প্রথমবার চালানো হয়েছিল MG এখনো round16-এ নির্দেশ করা অবস্থায় (আমার sed comma-form পথটি ধরেনি) — ফলে সেটি r16m-র `probe_identity_r14m.json` + clips ওভাররাইট করেছিল। ধরা পড়ার পর দুটোই run-আগের কপি থেকে ফিরিয়ে দেওয়া হয়েছে (বিষয়বস্তু হুবহু অভিন্ন যাচাই করা — ১৫টি entry), আর ঠিক করা probe merge-r17-তে পুনঃচালিয়ে ১৫/১৫ PASS পাওয়া গেছে।
2. Aug2 verifier ফাইলটি same-name sed redirect-এ (`sed ... file > file`) খালি হয়ে গিয়েছিল (০ লাইন) — r16m-র মূল থেকে (১৩৭ লাইন) ফিরিয়ে এনে সঠিকভাবে repoint করে পুনঃচালানো হয়েছে (১৬/১৬ PASS)।
3. প্রথম `cmp`-এ ভুল relative পথ (`../../` বনাম `../../../`) ব্যবহার করায় ৫টি পাতাই "ভিন্ন" দেখিয়েছিল — Python byte-diff-এ সত্যিটা বেরিয়েছে (May ৩/৩ identical, Aug ১ অক্ষর করে)।

## ৭. সৎ সীমা ও খোলা বিষয়

- **Adaptive gap:** per-line Otsu-র ব্যর্থ লাইনগুলোর প্রতিটি ফাঁক চোখে দেখা হয়নি; CC-প্রস্থের grid-সেরা মান in-sample fit; V1 page-Otsu-clip universality sample-এ পরীক্ষা করা হয়নি।
- **DBNet সংকেত:** T1 margin পাতলা (০.৪৮৪ বনাম ০.৫০); DBNet timing ব্যবহারকারীর i5-এ মাপা হয়নি; aug-p4-র ২৭৬০ ms outlier অমীমাংসিত; header-zone ২৮৫px PG ফর্মের জন্য টিউন করা; tiny-ফিল্টার আসল ১-অক্ষরের শব্দকে Signal A থেকে বাদ দেয়।
- **Gate:** ২৫টি অন্যান্য PDF পাতায় যাচাই হয়নি; -2 core-কে mask-এ পুরোটা ঢোকানোর আচরণের পর্যালোচনা বাকি (May dotted band ~১৩k px)।
- **Caps:** সব ফন্ট stand-in; Document DNA দিয়ে সরাসরি রেন্ডার করা হয়নি (DHAKA/BANGLADESH থেকে স্কেল করা অনুমান ~৮৮–৯১px)।
- **idx307:** সিম-সারির লক্ষ্যযুক্ত হালকা-করণ পরীক্ষা করা হয়নি (ink protection ভাঙার ঝুঁকি আছে কি না, আলাদা পরীক্ষা ছাড়া বলা যাবে না)।
- **Bold:** দূষণ শুধু aug-p2-র দুটি লাইনে চোখে যাচাই করা হয়েছে; সব পেজের সব লাইন চোখে দেখা হয়নি।
- **Universality:** নতুন কোনো seg তৈরি করা হয়নি (Track A প্রস্তুত নয় বলে); VALLEY-র লাভ-ক্ষতি ডকুমেন্টের ধরনের ওপর নির্ভর করে।
- **R16 সংশোধনের পরিধি:** শুধু Track C-র full-page অংশ ও ROUND16-REPORT-এর ঐ-সংক্রান্ত বাক্যগুলো প্রভাবিত; R16-র বাকি সব অপরিবর্তিত। সংশোধনটি parent-এর যাচাই-সাপেক্ষ — R16-র ফাইল বদলানো হয়নি।
- **মার্জ নিজে যা পুনঃচালায়নি:** Track B-র mirror-দিয়ে R16 mask-সংখ্যার পুনরুৎপাদন (ঘূর্ণন + seg box + gate batch নিজে যাচাই করেছে); Track B-র Signal A/B false-flag গণনা (gate batch ও PREM GROUP ডেটা নিজে যাচাই করেছে; c10 montage চোখে দেখেছে); Track A-র CC-প্রস্থ grid-সেরা মান (in-sample fit হিসেবে নথিভুক্ত)।
- **এখনো খোলা (আগের মতো):** প্রিন্ট ক্যালিব্রেশন (ফ্যাক্টরি প্রিন্টার, শুধু ব্যবহারকারী পারেন), US পেটেন্ট আইনি যাচাই (আইনজীবীর কাজ), DBNet KEEP CLASSICAL (deferred), DPAPI VM-এ অপ্রমাণিত, `raviraj COA 20 micron.jpg` পাওয়া যায়নি, ২৫টি অন্যান্য PDF পাতা শুধু contact-sheet দেখা, ১৮টি borderless edge, Q-03–Q-09।

## ৮. Round 18 প্রস্তাব + GRAVORA integration প্রস্তুতি

**Round 18 প্রস্তাব:**
1. **V1 page-Otsu-clip universality sample-এ** — মোট ভুল ৭৮ (স্থির ১৩১-এর চেয়ে ভালো) একমাত্র প্রার্থী; authoritative scorer দিয়ে FUNSD/SROIE/Tottel/Shields-এ মাপা; BY|SALES ১২/১৪ ব্যর্থতা hybrid (V1 + SALES-line guard) দিয়ে সারে কি না দেখা।
2. **DBNet header-zone সংকেত** — UI-তে বসানো ও ২৮৫px zone-র DPI-স্কেলিং (পণ্য-সিদ্ধান্ত); Raviraj-ধাঁচের ফর্মে zone-সংজ্ঞা।
3. **Gate T1 margin** — ২৫টি অন্যান্য PDF পাতায় চালিয়ে threshold পুনঃcalibrate; -2 core আচরণের পর্যালোচনা।
4. **Caps** — পণ্য-সিদ্ধান্ত (ExtraCondensed + ৯২px স্লট + ব্যবহারকারীর confirm, নাকি lowercase সাজেশন)।
5. **idx307 সিম-হালকা-করণ পরীক্ষা** — ink protection না ভেঙে 14px সারানো যায় কি না।
6. **Bold** — আরেকটি principled সংকেত, নইলে Lot-anchor + heading flip-কেই নকশা হিসেবে মেনে নেওয়া।
7. **Q-03–Q-09 + ১৮টি borderless edge** — এখনো খোলা পণ্য-সিদ্ধান্ত।

**GRAVORA integration প্রস্তুতি (নকশা `improve/gravora-integration/`-এ তৈরি):**
- **শুরু করা যায়।** LSE core তিন রাউন্ড ধরে স্থিতিশীল: Raviraj p2 LINES ৩২৭/৩২৭ (R14 থেকে অপরিবর্তিত), p3 improved ৩৮৪/৩৮৪, PG sample ৫১৮/৫১৮, লাইভ পাতা R11 থেকে byte-identical, শেয়ার্ড DB hash-chain অক্ষত। দুটি engine-ই প্রমাণিত: .xlsx live-paper (১০০/১০০) ও LSE scan editing (E-ce এডিট প্রমাণিত, CC-mask 2-pass ghost এডিট-পথে সমাধান, DBNet header-zone review সংকেত মানুষের confirm-সহ ব্যবহারযোগ্য, CC-mask gate safety component হিসেবে কাজ করে)।
- **Integration-কে আটকে রাখে না, কিন্তু জানা সীমা হিসেবে সঙ্গে যাবে:** non-PG ফর্মে segmentation (universality strict ৫১.৬% — page-adaptive gap-ই খোলা গবেষণা-সূত্র; VALLEY ছাপায় +৭, হাতের লেখায় −২); bold classification অমীমাংসিত (Lot-anchor PG-only); caps retype সরু স্লটে পণ্য-সিদ্ধান্তের অপেক্ষায়; full-page CC-mask gate প্রস্তুত কিন্তু build-time promotion পণ্য-সিদ্ধান্ত; DBNet সংকেত শুধু review prompt, কখনো auto-add নয়।
- **পণ্য-সিদ্ধান্ত হিসেবে খোলা (integration-এর আগে বা সঙ্গে সঙ্গে দরকার):** Q-03–Q-09, ১৮টি borderless edge, প্রিন্ট ক্যালিব্রেশন (শুধু ব্যবহারকারী পারেন), US পেটেন্ট আইনি যাচাই (আইনজীবীর কাজ)।
- **পরামর্শ:** integration build শুরু করা যায় — adaptive-gap নিয়ম, bold classifier ও caps নীতিকে pluggable/অমীমাংসিত হিসেবে রেখে; গবেষণা-রাউন্ড সমান্তরালে চলবে, আর যা প্রমাণিত হবে তা পরে ঢুকবে। Integration-কে এই তিনটির ওপর আটকে রাখা ঠিক হবে না।

## ৯. ফাইল তালিকা

- **প্রতিবেদন:** `improve/ROUND17-REPORT.md` (+ কপি `improve/round17/merge-r17/ROUND17-REPORT.md`)
- **মার্জ ডিরেক্টরি:** `improve/round17/merge-r17/` — `segs/` (১৭টি, r15m-র সঙ্গে অভিন্ন), `scripts/` (৪টি r17m builder + `guard_check.py` + `identity_pg.json` + `rescore_lines_r17m.py` + N5/Description/redbox/p3 scorer + `sample_rows_r17m.py`), `verifiers/` (probe_identity_r17m + may23/aug2/heading-এর r17m কপি), `pages/` (৫টি rebuild পাতা — May ৩/৩ identical, Aug ১-অক্ষর diagnostic পার্থক্য), `clips/` (১৫টি identity ক্লিপ + sample-rows crop), `cleans/` (r16m থেকে কপি), `exemplar-pg.npy`, `heading-*-300-r11m.json` (৫টি, R11-র সঙ্গে identical), `verdicts-r15m.json`, `verify-logs/` (rescore/N5/desc/redbox/sample + এই রিপোর্টের §৬), `probe_identity_r14m.json`, `verify-may23-summary-r17m.json`
- **Track A:** `improve/round17/track-a/` (TRACK-A-REPORT.md, adaptive_gap.py — EXPERIMENTAL, DO NOT PROMOTE, measure_adaptive.py, test_guards.py, adaptive_summary.json, ccwidth_summary.json, guarded_variants.json, gaps-adaptive-<tag>.json ×১৬, crops/ ×৭)
- **Track B:** `improve/round17/track-b/` (TRACK-B-REPORT.md, header_signal.py + header_signal_raw.json, dbnet-r17-*.json ×৮, gate_ccmask.py + run_gate_batch.py + gate_batch.json, crops/ c1–c10 + g1–g6)
- **Track C:** `improve/round17/track-c/` (TRACK-C-REPORT.md, idx307_probe.py, caps_test.py, bold_signal2.py, out/ — idx307-residual-4x.png, caps-methods-3x.png, bold-contamination-2x.png, bold_signal2_out.txt, scorer_rerun.txt)
- **কিছুই Google Drive-এ আপলোড করা হয়নি।** শেয়ার্ড Round 3 DB শুধু read-only যাচাই করা হয়েছে; নতুন delivery staging DB-তেই আছে। R16-র কোনো ফাইল বদলানো হয়নি (মার্জ-প্রক্রিয়ায় দুটি ভুল হয়েছিল — §৬-এর নোট দেখুন — দুটোই run-আগের কপি থেকে ফিরিয়ে দেওয়া হয়েছে)।
