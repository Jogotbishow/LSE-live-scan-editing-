# LSE Round 15 — প্রতিবেদন

**তারিখ:** ২০২৬-১১-০৭ | **সমন্বয়কারী:** মার্জ (`improve/round15/merge-r15/`) | **ধরন:** শুদ্ধতা/প্রকৌশল রাউন্ড — স্কোর রাউন্ড নয়

## ০. সারাংশ

Round 15-এর শিরোনাম সংখ্যা R14-এর সমান — **কোনো স্কোর বাড়েনি, কোনো স্কোর কমেনি**। এটাই সৎ ফল: এই রাউন্ডের কাজ ছিল ভুল শুধরানো (verdict), একটি নিয়মের আসল পরীক্ষা (VALLEY), একটি নতুন নিয়মের প্রমাণ (Rule D), আর একটি প্রকৌশল-ধাপ (CC-mask inpainting) — স্কোর বাড়ানো নয়।

| মাপ | R14 | **R15 (মার্জ নিজে পুনঃচালিয়ে)** |
|---|---|---|
| Raviraj p2 LINES | ৩২৭/৩২৭ | **৩২৭/৩২৭** (combined r15m seg-এ) |
| p2 strict (ক্যানোনিক্যাল / সংশোধিত) | ৪৪৭/৫০২ / ৪৯৮/৫০২ | **৪৪৭/৫০২ / ৪৯৮/৫০২** (R12 সূত্র: ৩২৭+১৫+১০৫ / ৩২৭+৬৬+১০৫) |
| p2 improved (ক্যানোনিক্যাল / সংশোধিত) | ৪৫১/৫০২ / ৫০২/৫০২ | **৪৫১/৫০২ / ৫০২/৫০২** |
| পূর্ণ পাতা strict (ক্যানোনিক্যাল / সংশোধিত) | ৭৮১/৮৮৬ / ৮৩২/৮৮৬ | **৭৮১/৮৮৬ / ৮৩২/৮৮৬** |
| পূর্ণ পাতা improved (ক্যানোনিক্যাল / সংশোধিত) | ৮৩৫/৮৮৬ / ৮৮৬/৮৮৬ | **৮৩৫/৮৮৬ / ৮৮৬/৮৮৬** |
| N5 strict / improved | ৭৭/৮১ / ৮১/৮১ | **৭৭/৮১ / ৮১/৮১** |
| Description (r10 GT) | ৬৯/৬৯ | **৬৯/৬৯, wrong ০** |
| redbox (r12 / R9 ক্যানোনিক্যাল) | ৬৬/৬৬ / ১৫/৬৬ | **৬৬/৬৬ / ১৫/৬৬** |
| p3 strict / improved | ৩৩৪/৩৮৪ / ৩৮৪/৩৮৪ | **৩৩৪/৩৮৪ / ৩৮৪/৩৮৪** |
| PG sample | ৫১৮/৫১৮ | **৫১৮/৫১৮, extras ০** |
| A-logo | ২৩/২৩ | **২৩/২৩** (LINES-এ অন্তর্ভুক্ত) |
| false merge | ০ | **০** |

**নতুন seg:** `seg-rav-p2-r15m.json` (**৫৫৫ শব্দ**, SHA `3762d595…`) = r14m + Track A-র ২টি বাক্স-শুধরানো + Track C-র Rule D-র ২টি মার্জ। PG seg ১৪টি ও p3 seg byte-identical r14m-পরিবারের সঙ্গে। **লাইভ পাতা promotion লাগেনি** — root SHA অপরিবর্তিত (নিচে §৫)। শেয়ার্ড DB SHA `1c065457…`, ২০টি audit entry, LSE-0001–0007 অক্ষত।

**তিন ট্র্যাকের এক-লাইন রায়:**
- **Track A — সম্পূর্ণ।** DATED ও Formerly-র verdict-বাক্স মাপা প্রমাণে ঠিক করা হয়েছে; LINES ৩২৭/৩২৭ অপরিবর্তিত।
- **Track B — নেতিবাচক ফল, প্রমাণসহ।** VALLEY + মার্জ-পাইপলাইন r14m-কে **হারাতে পারেনি** (৩২৭/৩২৭ টাই), আর ৪টি গৌণ পরীক্ষায় পিছিয়ে — প্রকাশিত স্তরে VALLEY গ্রহণ করা হবে না।
- **Track C — সম্পূর্ণ।** Rule D কাজ করে (১৪টি মার্জ, ০ false merge); SALES DEPARTMENT-এর জন্য নতুন সংকেত পাওয়া গেছে (নিয়ম-খোঁজা মাত্র, seg বদলায়নি); CC-mask inpainting প্রমাণিত (অন্য সারি ১০০% বাঁচে)।

## ১. Track A — DATED + Formerly verdict-ত্রুটি (সম্পূর্ণ)

R14 §১.৩-এর দুটি পুরনো verdict-ত্রুটি, LINES-তালিকায় প্রভাব ছিল না, কিন্তু verdict ফাইল GT-র সঙ্গে মিলছিল না।

- **DATED:** verdict-এ লেখা বাক্স `[826,598,984,623]` আসলে **CHARGES-এর বাক্স** ছিল (৭টি CC-র union হুবহু)। আসল DATED-বাক্স মাপা হয়েছে **[907,553,990,583]** — D-র stem CC (907,554,17,29, area ৩২৮) R14-র অনুমান-বাক্সের [925,553,990,581] বাইরে ছিল, তাই seg-ও বদলাতে হয়েছে। নতুন seg `seg-rav-p2-r15a.json` (৫৫৭ শব্দ, SHA `6b415dd9…`)।
- **Formerly:** verdict-বাক্স `[360,521,393,544]` শুধু "For" ঢাকত। "merly" আসল কালি — "For"-এর মতোই ধূসর (BGR mean [168.7,162.0,162.8] বনাম [161.4,154.1,155.0]); F-র stem x351, 'y'-র descender-টিপ y552। নতুন বাক্স **[351,518,458,553]**।
- **মার্জ-সিদ্ধান্ত (গুরুত্বপূর্ণ):** Formerly-র পুরনো `r11b` নোট ("fixed R11B custom extend 578") মার্জে **সরানো হয়েছে** — প্রমাণিত ভুল: ৫৭৮ হলো CHARGES-এর পুরনো known/as: বাক্সের x1, Formerly-র সঙ্গে সম্পর্ক নেই। provenance track-a-র `verdicts-r15a.json` + TRACK-A-REPORT.md §৩-এ সংরক্ষিত আছে।
- ফল: LINES ৩২৭/৩২৭ অপরিবর্তিত, ০ false merge, N5/Description/redbox/PG sample অপরিবর্তিত। CHARGES-এর entry byte-identical।

## ২. Track B — VALLEY-র আসল পরীক্ষা (নেতিবাচক ফল, প্রমাণসহ)

R14 শুধু প্রমাণ করেছিল VALLEY **কাঁচা** স্তরে সাহায্য করে। এই ট্র্যাকের প্রশ্ন ছিল: কাঁচা VALLEY + মার্জ-পাইপলাইনের post-processing (vocab-gate v3, hand-merge) একসঙ্গে চালালে কি প্রকাশিত r14m-র ৩২৭/৩২৭-কে হারানো যায়?

**উত্তর: না। টাই, হারানো যায়নি — আর ৪টি গৌণ পরীক্ষায় পিছিয়ে।**

| পরীক্ষা | r14m | **VALLEY+পাইপলাইন (r15b)** |
|---|---|---|
| p2 LINES | ৩২৭/৩২৭ | **৩২৭/৩২৭ (টাই)** |
| N5 strict | ৭৭/৮১ | **৭৬/৮১** (carrier-name: অতিরিক্ত ১ miss) |
| Description (r10 GT) | ৬৯/৬৯ | **৬৮/৬৯** (শুধু L4 '2010)' — nored ছবিতে VALLEY ভেঙেছে) |
| PG sample | ৫১৮/৫১৮ | **৫১৭/৫১৮** (aug-p3 "FOIL TEMPER" over-merge) |
| p3 strict / improved | ৩৩৪/৩৮৪ / ৩৮৪/৩৮৪ | **৩৩২/৩৮৪ / ৩৮৪/৩৮৪** |

- **FOIL TEMPER over-merge (আসল VALLEY ত্রুটি, মার্জ যাচাই করেছে):** aug-p3-তে "FOIL" [1472,1204,1544,1231] ও "TEMPER" [1553,1204,1693,1231]-এর ফাঁক **৯px**; aug-p3-তে VALLEY threshold **৯.০০** — নিয়ম `gap > thr`, ৯ > ৯ মিথ্যা → VALLEY মার্জ করে দেয় (VALLEY seg-এ একটাই বাক্স [1472,1204,1693,1231])। baseline threshold ৮.০০ — ৯ > ৮ → ভাগ করে। একই শ্রেণির ঘটনা R14B-র aug-p8 "SALES DEPARTMENT"। হাতের পাইপলাইনের কোনো op এই দুটো ঠিক করতে পারে না।
- **সবচেয়ে শক্তিশালী নিয়ন্ত্রণ:** baseline raw + একই পাইপলাইন r14m-কে **বাক্স-হুবহু** পুনরুৎপাদন করে (৫৫৭ শব্দ, ০/০ diff), r13b-কেও বাক্স-হুবহু — স্কোর পাইপলাইনের হাতের কাজ থেকে আসে, কাঁচা seg থেকে নয়।
- **দুটি আসল পাইপলাইন-ত্রুটি পাওয়া গেছে ও ঠিক করা হয়েছে** (সাধারণ, VALLEY-টিউনিং নয়): (১) R7 Z2 rescue exact set-difference ব্যবহার করত → duplicate pair (match-নিয়ম "already present" পরীক্ষায় ঠিক); (২) container cleanup ছিল না → ১৭টি contained-overlap pair (r14m-guarded final cleanup-এ ঠিক, ১৩টি non-guard বাক্স সরানো, স্কোর অপরিবর্তিত)। চূড়ান্ত r15b seg ৫৫৯ শব্দ, ০ match-duplicate, ২১টি overlapping pair (r14m-ও ২১; ২০টি অভিন্ন + ১টি নতুন ২px touch), ০ false merge।
- **সিদ্ধান্ত: প্রকাশিত স্তরে VALLEY গ্রহণ করা হবে না — r14m/r13b ক্যানোনিক্যাল থাকবে; VALLEY শুধু কাঁচা-স্তরের ডিফল্ট।** এই সিদ্ধান্ত বদলানো যায় — VALLEY-কে হারাতে হলে threshold-সীমানার over-merge ও nored-ভাগের সমাধান লাগবে।

### ২.১ Universality পুনঃগণনা — FUNSD L12 সংশোধন

Track B R14-র universality সংখ্যাগুলো নমুনা-ভিত্তিতে পুনঃগণনা করেছে। **একটি সংশোধন পাওয়া গেছে:**

- **FUNSD L12 ("This is your authorization to provide the "1601.013: The Effect of Inhalation""):** পুরনো দাবি ৪/৬ (base) ও ৬/৬ (valley) ভুল। একক-বক্স নিয়মে (x-overlap ≥০.৯০ দুই দিকেই, y ±৪px) — **base ২/২ ("to" [368,382] + "the" [465,477]), valley ২/২ ("This" [106,134] + "is" [144,157])**। চারটি নিয়ম চেষ্টা করে দেখা হয়েছে (coverage ≥০.৯০: valley ৫, base ২; ≥০.৬০: valley ৬, base ৪ — L12 মেলে কিন্তু L5 ভেঙে যায়; exact-union: valley ৪; চোখে ঢিলেভাবে: ২–৩) — **কোনো একক সামঞ্জস্যপূর্ণ নিয়মই পুরনো ৪/৬ পুনরুৎপাদন করে না**, একক-বক্স নিয়ম ছাড়া — যা চারটি লাইন হুবহু মেলায়, L12 সংশোধন করে।
- **সংশোধিত মোট:** FUNSD base **১৬/৩৮** (আগে ১৮), valley **২১/৩৮** (আগে ২৫); SROIE ৩/১৬ → ৫/১৬ অপরিবর্তিত; Tottel ১৭/২৪ অপরিবর্তিত; Shields ১২→১০ অপরিবর্তিত। **দিক অপরিবর্তিত** (valley এখনো এগিয়ে: +৫, আগে +৭ ছিল) — সংশোধন সংখ্যা কমিয়েছে, বাড়ায়নি (সৎ দিক)।
- **মার্জের নিজের যাচাই:** চারটি উদ্ধৃত বাক্স seg-ডেটায় হুবহু আছে (base "to" (368,223,382,234), "the" (465,221,477,233); valley "This" (106,225,134,236), "is" (144,225,157,236)); valley FUNSD স্ট্রিপ চোখে দেখা — "your"-এর "r" বাক্সের বাইরে কাটা, "provide"-এর "e" কাটা, "authorization" ভেঙেছে "a"+"uthorization"-এ, "1601.013:" ও "Inhalation" ভেঙেছে — পরিষ্কার একক-বাক্স শব্দ শুধু "This" + "is"; প্রতি-লাইন যোগফল মিলেছে (base ৫+৩+৩+২+৩=১৬, valley ৩+৩+৭+২+৬=২১)। **সীমা:** এটি নমুনা-ভিত্তিক পুনঃগণনা, প্রতিটি শব্দের পূর্ণ স্বাধীন পুনঃগণনা নয় (Shields L1/L2/L4 পুনরায় যাচাই করা হয়নি) — §৭ দেখুন।

## ৩. Track C — Rule D (দশমিক) + SALES DEPARTMENT + CC-mask inpainting (সম্পূর্ণ)

### ৩.১ Rule D — দশমিক/কমা মার্জ: কাজ করে, ০ false merge

ফাঁকের মাপ একা দশমিক-বিন্দুকে abbreviation-এর পিরিয়ড/কমা থেকে আলাদা করতে পারে না — Rule D সংখ্যা-প্রতিবেশী + কালির প্রমাণ ব্যবহার করে (Op A: দশমিক-বিন্দু; Op B: trailing কমা/পিরিয়ড)। **মোট ১৪টি মার্জ, ০ false merge:**

| ডকুমেন্ট | মার্জ | উদাহরণ |
|---|---|---|
| Raviraj p2 (৫৫৭→৫৫৫) | ২× Op B | "32937405," ও "07," (trailing কমা) |
| SROIE uni (১২৯→১২৩) | ৩× Op A | 4.95, $4.95, $0.00 |
| SROIE valley (১০১→৯৯) | ১× Op A | — |
| FUNSD uni (২৮২→২৭৩) | ১× Op A + ৭× Op B | "1601.013" + ৭টি trailing পিরিয়ড |
| FUNSD valley (১৯৫→১৯৫) | ০ | — |
| PG ১৪ পাতা | **০** | ৩টি candidate সঠিকভাবে প্রত্যাখ্যাত |

- **ফাঁদ সঠিকভাবে এড়ানো:** SROIE "Reg:"-এর dot colon-guard-এ আটকেছে; FUNSD "C." + "27420" জোড়া লাগেনি (gapR=১০ > G=৯); স্বাক্ষরের dot ছোঁয়া হয়নি।
- **মার্জ যাচাই:** Raviraj-এর ২টি মার্জ diff-এ হুবহু (৪টি সরানো / ২টি যোগ) + montage চোখে দেখা — "32937405," ও "07,"-র কমা স্পষ্টতই সংখ্যার অংশ (নিচে-ডানে ছোট CC)। LINES ৩২৭/৩২৭ অপরিবর্তিত (r15c-তে Track C চালিয়েছে, মার্জ combined r15m-এ পুনঃচালিয়েছে)।
- নতুন seg: `seg-rav-p2-r15c.json` (৫৫৫ শব্দ, SHA `99e2e45d…`) + SROIE/FUNSD Rule D seg ৪টি।

### ৩.২ SALES DEPARTMENT — bold-ফাঁকের টাই: নতুন সংকেত পাওয়া গেছে (নিয়ম-খোঁজা মাত্র)

aug-p8-এ "SALES DEPARTMENT" ভুলভাবে এক বাক্সে মার্জ হয়েছিল — bold অক্ষর-ফাঁক ৯px শব্দ-ফাঁকের সমান। ফাঁকের মাপ একা আলাদা করতে পারে না।

- **যে সংকেত কাজ করে:** প্রতি-লাইন normalized gap (gap ÷ লাইনের cap-height, thr ০.২৫) — SALES|DEPARTMENT **০.৪০** বনাম একই লাইনের intra সর্বোচ্চ **০.২৪**। পুরো পাতায় thr ০.২৫-এ মাত্র **৩টি ভুল** (২টি labeling artefact, ১টি আসল intra outlier ০.৩৬ = "PGFL /"-এর L/slash); আসল word-সর্বনিম্ন ০.২৮ বনাম intra সর্বোচ্চ ০.২৫ — **মার্জিন মাত্র ০.০১–০.০৩, পাতলা**।
- **যা কাজ করে না:** stroke width, অক্ষরের w/h অনুপাত, gap-column ink fraction, min(top,bot)/cap_h — সব ব্যর্থ।
- **মার্জ যাচাই:** Track C-র `measure6_out.txt` থেকে মূল সংখ্যাগুলো মিলিয়েছি (লাইন ৯: SALES|DEPARTMENT ০.৪০, intra max ০.২৪; thr ০.২৫-এ ভুলের হার)। **কোনো seg বদলায়নি — নিয়ম-খোঁজা মাত্র; বেশি পাতায় যাচাই না করে promote করা যাবে না।**

### ৩.৩ Inpainting CC-mask নিয়ম: প্রমাণিত (অন্য সারি ১০০% বাঁচে)

E-ce-র ৯টি y-overlap pair-এর সমস্যা: box-rect মোছা অন্য সারির কালি খেয়ে ফেলে। নতুন নিয়ম — শব্দের নিজের CC-mask দিয়ে মোছা (`inpaint_ccmask.py`; শেয়ার্ড `inpaint.py` ছোঁয়া হয়নি); জোড়া-লাগা blob (পাতায় ৩২টি) ysplit দিয়ে ভাগ করা হয়।

| এডিট | লক্ষ্য core মোছা | অন্য সারি বেঁচে থাকা | zone কালি (আগে→পরে) |
|---|---|---|---|
| **Bank's** (CC-mask) | **৪৫৬/৪৫৬ = ১০০%** | **১২০/১২০ = ১০০%** | — |
| Bank's (box-rect) | ১০০% | ৩৩.৩% | — |
| **Nothing's** (CC-mask) | **১৮৭০/১৮৭০ = ১০০%** | `far` ১৭৩৬→১৭৩৬ = **১০০%** | **১৬→১৬** |
| Nothing's (box-rect) | ১০০% | `far` ১৭৩৬→১৭১৮ = ৯৯.০% (−১৮px) | **১৬→০** |
| **DHAKA** (CC-mask) | **আংশিক** | Consignee ১০০% | — |

- **মার্জের চোখে যাচাই:** Bank's CC-mask-এ "Bank's" মুছে হালকা ছায়া মাত্র, "MAIN BRANCH" পুরো অক্ষত (box-rect-এ MAIN-এর ওপর কাটা); Nothing's CC-mask-এ "Nothing's" হালকা ছায়া, "too far" পুরো অক্ষত, `f`-এর ascender সম্পূর্ণ; DHAKA CC-mask-এ "DH_KA" পড়া যায় (মাঝের A মুছেছে, প্রতিযোগিতামূলক অংশ), "Consignee" পুরো অক্ষত।
- **মাপার নিয়ম (সৎ):** লক্ষ্য মোছা মাপা হয়েছে core (<১৪০) পিক্সেলে — Telea fill <২১০ হতে পারে, তাই <২১০ দিয়ে মাপলে ভুল হয়। R14-র "tone নির্ভরযোগ্য" দাবি **ভুল প্রমাণিত** — L41/L42 ধূসর overlap ১১০–১৮০; stroke/connectivity/erosion-ও আলাদা করতে পারে না।
- **সীমা (সৎ):** CC-mask dark core ১০০% মোছে, কিন্তু হালকা রঙের (নীল/ধূসর) লেখায় **হালকা ছায়া (ghost) থেকে যায়** — retype করলে নতুন লেখা ঢেকে দেয়, কিন্তু শুধু মুছে ফেললে (pure deletion) ছায়া চোখে পড়বে। DHAKA-শ্রেণির fused blob-এ CC-mask **নিরাপদ কিন্তু আংশিক** — প্রতিবেশী ১০০% বাঁচে, লক্ষ্য পুরো মোছে না। পরের ধাপ: fused blob-এর আরও ভালো ভাগ (per-column waist / আকৃতি-ভিত্তিক) বা দুই-পাস পদ্ধতি।
- **সিদ্ধান্ত:** CC আলাদা থাকলে CC-mask **পুরোপুরি কাজ করে** (Bank's, Nothing's) — এটাই live edit পথের পরের ধাপ।

## ৪. মার্জ — combined seg r15m (৫৫৫ শব্দ)

- **নির্মাণ:** r14m + Track A-র ২টি প্রতিস্থাপন + Track C-র ২টি মার্জ। diff বনাম r14m হুবহু প্রত্যাশিত **৬টি সরানো / ৪টি যোগ** (DATED, Formerly, ২টি Rule D মার্জ)। A/C-র বদলানো বাক্স পরস্পর disjoint। PG seg ১৪টি + p3 seg byte-identical (cmp দিয়ে যাচাই)।
- **নতুন মার্জ-স্কোরার** `merge-r15/scripts/rescore_lines_r15m.py` (R14 স্কোরারের একই কাঠামো; **read-only** — R14 স্কোরারের মতো verdicts ফাইল আবার লেখে না, সেই ফাঁদ এড়ানো হয়েছে):
  - diff হুবহু ৬/৪ ✓; DATED/Formerly single-box নিয়মে GT-র সঙ্গে ১/১ করে ✓; ২টি মার্জ-শব্দ coverage ১.০০০, y ±৪px-এর ভেতরে ✓; ০ false merge (new-vs-new ও new-vs-surviving — শুধু ১টি inherited Nothing's/far overlap) ✓; শুধরানো verdict-বাক্স ২/২ seg-এ আছে ✓; r14a-র সঙ্গে শুধু DATED/Formerly বদলেছে, **CHARGES byte-identical** ✓; stale r11b নোট সরানো, r15m নোট যোগ ✓।
  - **LINES ৩২৭/৩২৭ নিশ্চিত** (status: ok ২১৯ + correct ১০৮)।
- **রিগ্রেশন (combined r15m-এ মার্জ নিজে চালিয়েছে):** N5 strict ৭৭/৮১, improved ৮১/৮১ (per-line R14-র সঙ্গে হুবহু); Description r10 GT ৬৯/৬৯, wrong ০; redbox r12 ৬৬/৬৬, R9 ক্যানোনিক্যাল ১৫/৬৬; p3 strict ৩৩৪/৩৮৪, improved ৩৮৪/৩৮৪ (নিয়ন্ত্রণ পুনঃচালনা); PG sample ৫১৮/৫১৮, extras ০।
- **p2 strict-এর গাণিতিক যাচাই (R12 §১-এর সূত্র):** ক্যানোনিক্যাল ৩২৭ + ১৫ + ১০৫ = **৪৪৭** ✓; সংশোধিত ৩২৭ + ৬৬ + ১০৫ = **৪৯৮** ✓; improved ৪৫১ / ৫০২ ✓; পূর্ণ পাতা ৪৪৭+৩৩৪ = **৭৮১**, ৪৯৮+৩৩৪ = **৮৩২**, ৪৫১+৩৮৪ = **৮৩৫**, ৫০২+৩৮৪ = **৮৮৬** ✓। দুটি মার্জ-শব্দ LINES verdict-এর ভেতরে (coverage নিয়মে পাস) — সূত্রের কোনো উপাদান বদলায়নি।

## ৫. লাইভ পাতা rebuild — promotion লাগেনি (১টি diagnostic পার্থক্য সহ)

r15m builder দিয়ে ৫টি লাইভ পাতা `merge-r15/pages/`-এ পুনর্নির্মাণ করা হয়েছে (may23 builder-এ `may2` ও `may3` আলাদা করে — R13-র মতোই):

| পাতা | ফল |
|---|---|
| May p1 / p2 / p3 | **৩/৩ byte-identical** root-এর সঙ্গে |
| Aug p1 / Aug p2 | **মাত্র ১ অক্ষর করে ভিন্ন** — SHORTLIST-এ "Document DNA Regular" mean_iou **০.৬৪৪ বনাম ০.৬৪৩** (root)। বাকি ৩.৬MB-র সবকিছু (WORDS, cleans, ছবি, heading) byte-identical। |
| Heading JSON ৫টি | **৫/৫ identical** R11-র সঙ্গে |

- **১-অক্ষরের পার্থক্যের কারণ (মাপা):** rounding-সীমানার মান (~০.৬৪৩৫) — এই পরিবেশে ওপরে, R11-এ নিচে round হয়েছে। পুনর্নির্মাণ **deterministic** (২য় বার চালিয়ে ১ম বারের সঙ্গে byte-identical)। এটি diagnostic font-match স্কোর (SHORTLIST), কোনো শব্দ/বাক্স/ছবি/এডিট আচরণ নয় — কার্যকরী পার্থক্য **শূন্য**।
- **সিদ্ধান্ত: promotion নয়।** root পাতার SHA অপরিবর্তিত (Aug p1 `bce37147…`, Aug p2 `f4f72713…`, May p1 `d0948b0f…`, May p2 `539995a9…`, May p3 `8587be86…`) — শুধু diagnostic rounding-অঙ্কের জন্য SHA-ধারাবাহিকতা ভাঙা হবে না। R11-এ তৈরি root পাতাই ক্যানোনিক্যাল থাকবে।

## ৬. পূর্ণ যাচাই তালিকা (মার্জের নিজের পুনঃচালনা)

| পরীক্ষা | ফল |
|---|---|
| LINES, combined r15m (`rescore_lines_r15m.py`) | **৩২৭/৩২৭** |
| N5 strict / improved | **৭৭/৮১ / ৮১/৮১** |
| Description (r10 GT) | **৬৯/৬৯, wrong ০** |
| redbox (r12 / R9) | **৬৬/৬৬ / ১৫/৬৬** |
| p3 strict / improved | **৩৩৪/৩৮৪ / ৩৮৪/৩৮৪** |
| Track B VALLEY+পাইপলাইন LINES / N5 / Description / p3 | **৩২৭/৩২৭ / ৭৬/৮১ / ৬৮/৬৯ / ৩৩২/৩৮৪** (টাই + ৪ রিগ্রেশন — §২) |
| Track B PG FOIL/TEMPER | VALLEY-তে ১ বাক্স, baseline-এ ২ বাক্স — over-merge নিশ্চিত |
| fontfix_verify300 | **৪৩/৪৩** |
| verify_round2_300 (rebuild ধাপ RETIRED) | **১৮/১৮ × ২ বার, SHA+mtime অপরিবর্তিত** |
| repro300 | **PASS** (২টি edited span, exact text, .done, doubling নেই) |
| manual_proof300 | **১০/১০** |
| Guard check (full mode, ৫ পাতা, probe-এর আগে) | **৫/৫ PASS** (C1–C5 সব, exit ০) |
| identity probe (ফিক্সড r14m প্রোব, merge-r15 seg) | **১৫/১৫ PASS** (Lot+WIDTH+Hard × ৫; ক্লিপ চোখে যাচাই: Aug p2 WIDTH ৭৭৬.৫ পরিষ্কার, Aug p1 Lot ২০৭/৯ পরিষ্কার, May p1 Hard অছোঁয়া, May p3 WIDTH ৭৭১.৫ পরিষ্কার) |
| write-back | **৪১/৪১ + ৪০/৪০, FAILURES: none** |
| Track D staging | **৪৮/৪৮, FAILURES: none** |
| Track C (R5) staging | **৭৪/৭৪, FAILURES: none** |
| May multipage | **৫৯/৫৯, FAILURES: none** |
| May p2/p3 (r11m verifier) | **৪৩/৪৩ PASS** |
| sqlcipher_test.py | **১৫/১৫, FAILURES: none** |
| keymgmt_proof.py | **২৫/২৫, FAILURES: none** |
| save→label LIVE (১৮/পাতা × ৫) | **৯০/৯০** |
| Aug p2 (r10m verifier) | **১৬/১৬** (Hard neighbour untouched) |
| heading R1 (check_heading_r11.py) | **PASS ১৪/১৪ × ৩ family** (TITLE ১৪/১৪, H2 ১৪/১৪, control-এ H1-diff ২ প্রত্যাশিত) |
| sample rows (merge-r15 seg, r10m) | **৫১৮/৫১৮, extras ০** |
| শেয়ার্ড DB (read-only) | SHA `1c065457…`, ২০টি audit entry, LSE-0001–0007, ১৪টি edit; chain R10 write-back verifier-এ PASS |

**নোট:** Round 3-র পুরনো `verify_rebuild_300.py` এখনো তার ৪টি known ink-IoU fail দেখায় (v1 staging artifact) — superseded artifact, regression নয়; বর্তমান R10 work `verify_rebuild_300.py` ৪০/৪০ PASS (উপরে)।

## ৭. সৎ সীমা ও খোলা বিষয়

- **VALLEY নেতিবাচক ফল** — প্রকাশিত স্তরে VALLEY হারাতে পারেনি; threshold-সীমানার over-merge (ফাঁক == thr) ও nored-ভাগ অমীমাংসিত।
- **SALES DEPARTMENT নিয়মের মার্জিন পাতলা** (০.০১–০.০৩) — বেশি পাতায় যাচাই ছাড়া promote নয়। মার্জ নিজে পরিমাপ-কোড পুনঃচালায়নি, `measure6_out.txt` থেকে মূল সংখ্যা মিলিয়েছে।
- **Universality strict সংখ্যা Rule D-র পরে পুনঃমাপা হয়নি** — Track B-র পুনঃগণনা Rule D-আগের seg ব্যবহার করেছে। এটা Round 16-র কাজ।
- **FUNSD L12 সংশোধন নমুনা-ভিত্তিক** — পূর্ণ স্বাধীন পুনঃগণনা নয়; Shields L1/L2/L4 পুনরায় যাচাই করা হয়নি। তবে দিক সংরক্ষিত (+৫) ও সংশোধন রক্ষণশীল।
- **CC-mask ghost** — হালকা রঙের লেখায় হালকা ছায়া থাকে; pure deletion-এ চোখে পড়বে। DHAKA-শ্রেণির fused blob আংশিক।
- **p3 strict-এর ৫০টি miss artefact-ই** (আগের মতো) — improved-ই p3-র সৎ মাপ; median টানা হয়নি (scorer-gaming এড়াতে)।
- **Aug rebuild-এ ১-অক্ষরের diagnostic পার্থক্য** (SHORTLIST mean_iou ০.৬৪৪ বনাম ০.৬৪৩) — কার্যকরী পার্থক্য শূন্য, promotion হয়নি (§৫)।
- **এখনো খোলা (আগের মতো):** প্রিন্ট ক্যালিব্রেশন (ফ্যাক্টরি প্রিন্টার, শুধু ব্যবহারকারী পারেন), US পেটেন্ট আইনি যাচাই (আইনজীবীর কাজ), DBNet KEEP CLASSICAL (deferred), DPAPI VM-এ অপ্রমাণিত, `raviraj COA 20 micron.jpg` পাওয়া যায়নি, ২৫টি অন্যান্য PDF পাতা শুধু contact-sheet দেখা, redbox L5 'and' শুধু 'a', সাধারণ bold শ্রেণিবিন্যাস, ১৮টি borderless edge, Q-03–Q-09।

## ৮. Round 16 প্রস্তাব

1. **Rule D-র পরে universality পুনঃমাপা** — FUNSD/SROIE strict Rule D-যুক্ত seg-এ (Track B-র সংশোধিত ভিত্তি ১৬/৩৮, ২১/৩৮ থেকে)।
2. **SALES DEPARTMENT নিয়ম যাচাই** — বেশি পাতায় (বিশেষ করে bold শিরোনামে); মার্জিন ধরে রাখলে promote।
3. **CC-mask live edit পথে** — `inpaint.py`-তে CC-mask নিয়ম আনা + pure-deletion ghost-এর সমাধান (দ্বিতীয় পাস / হালকা-কালি threshold)।
4. **E-ce y-overlap এডিট-পরীক্ষা** — CC-mask দিয়ে আসল এডিট করে অন্য সারি বাঁচার প্রমাণ।
5. **redbox L5 'and'** (শুধু 'a') ও **সাধারণ bold শ্রেণিবিন্যাস**।
6. **VALLEY hybrid** — DBNet line-detection cross-check হিসেবে (DBNet swap deferred থাকে)।
7. **১৮টি borderless edge** — পণ্য-সিদ্ধান্ত (Q-09): original-এ border নেই, যোগ করা হবে কি না।

## ৯. ফাইল তালিকা

- **প্রতিবেদন:** `improve/ROUND15-REPORT.md` (+ কপি `improve/round15/merge-r15/ROUND15-REPORT.md`)
- **মার্জ ডিরেক্টরি:** `improve/round15/merge-r15/` — `segs/` (১৭টি: ১৪ PG r10m + r14m + **r15m ৫৫৫ শব্দ** + r13b p3), `gt/` (p3 GT r12, r15a GT, desc GT r10, n5 GT r10, r13a GT, redbox GT r12), `scripts/` (৪টি r15m builder + `guard_check.py` + `identity_pg.json` + `rescore_lines_r15m.py`), `verifiers/` (r11m verifier-দের কপি + `probe_identity_r14m.py` + `verify_aug2_page_r10m.py` + `check_heading_r11.py`), `pages/` (৫টি rebuild পাতা — May ৩/৩ identical, Aug ১-অক্ষর diagnostic পার্থক্য), `clips/` (১৫টি identity ক্লিপ), `cleans/` (r11m থেকে কপি) + `exemplar-pg.npy`, `heading-*-300-r11m.json` (৫টি, R11-র সঙ্গে identical), `guard-*.json` (৫টি), `verdicts-r15m.json`, `verify-logs/` (১১টি), `probe_identity_r14m.json`, `backup/` (খালি — r14m seg `segs/`-এই সংরক্ষিত)
- **Track A:** `improve/round15/track-a/` (TRACK-A-REPORT.md, seg-rav-p2-r15a.json, verdicts-r15a.json, r15a_gt.json, scripts/, clips/, checks-r15a-regression.txt)
- **Track B:** `improve/round15/track-b/` (TRACK-B-REPORT.md, build_replay.py, score_lines_r15b.py, segs/, pg/, uni-strips/, archive/)
- **Track C:** `improve/round15/track-c/` (TRACK-C-REPORT.md, rule_d.py, inpaint_ccmask.py, seg-rav-p2-r15c.json, seg-sroie-r15c.json, seg-sroie-valley-r15c.json, seg-funsd-r15c.json, seg-funsd-valley-r15c.json, verdicts-r15c.json, crops/)
- **কিছুই Google Drive-এ আপলোড করা হয়নি।** শেয়ার্ড Round 3 DB শুধু read-only যাচাই করা হয়েছে; নতুন delivery staging DB-তেই আছে।
