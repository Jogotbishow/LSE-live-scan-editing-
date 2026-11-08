# LSE — Round 8 রিপোর্ট (Live-Scan Editing)

**তারিখ:** ২০২৬-১১-০৭ · **স্থিতি: সম্পূর্ণ — তিন ট্র্যাক এক v8 পাতা সেটে merge করা, পুরো suite নিজে আবার চালিয়ে যাচাই করা।**

> ⚠️ **Collision সতর্কতা (আগে পড়ুন):** এই রাউন্ডে **দুটি Round 8 coordinator সমান্তরালে চলেছে** — একটি scheduled job (`lse-round7-morning-report`, agent `76439502…`, আমার ১৯ সেকেন্ড আগে তৈরি) আর আমি (মূল agent-এর সরাসরি নির্দেশে)। তার agent-রা আমার track ডিরেক্টরিতে ফাইল লিখেছে, আমার merge ডিরেক্টরি (`improve/round8/merge/`) ০২:৩২–০২:৩৫-এ overwrite করেছে (seg, backup, verifier, live পাতা), এমনকি `_r8c` suffix নকল করে ফাইল লিখেছে। আমার তিন track-এর কাজ অক্ষত আছে (নিজের `_r8a`/`_r8b`/`_r8c` ফাইল থেকে আবার যাচাই করা); এই রিপোর্টের merge আমার নিজের agent-দের output দিয়ে করা — parallel agent-এর কোনো ফাইল promote করা হয়নি। আমার merge-এর নিরাপদ কপি `improve/round8/merge-b8f7/`-তে আছে। **Parent-কে করতে হবে:** duplicate schedule থামানো; Drive-এ কিছু আপলোড করার আগে shared tree-র SHA এই রিপোর্টের §৯-এর সঙ্গে মিলিয়ে নেওয়া। বিস্তারিত §৬-এ।

> **প্রসঙ্গ:** ব্যবহারকারী ঘুমানোর আগে (২০২৬-১১-০৬ ~২৩:০৬) LSE-র জন্য **blanket permission** দিয়েছেন — তার অনুমতির অপেক্ষায় সময় নষ্ট না করে নিজের বিচারে কাজ চালিয়ে যেতে হবে, খোলা প্রশ্ন নিজেই সিদ্ধান্ত নিতে হবে; তিনি যেকোনো সিদ্ধান্ত পরে বদলাতে পারেন। এই রাউন্ডের সিদ্ধান্তগুলো (§৫) সেই অনুমতির অধীনে নেওয়া। শারীরিকভাবে তার ছাড়া অসম্ভব দুটি কাজ আগের মতোই খোলা: print calibration (ফ্যাক্টরির প্রিন্টার), US পেটেন্টের আইনি যাচাই (উকিল)।

## ১. এক লাইনে ফল

- **Track A — DNA-glyph template matcher:** ৬টি over-split (DEPARTMENT + e-mail ×৫) **OCR-ছাড়া উদ্ধার — ৬/৬, ভুল merge ০**; আরও ৩টি অতিরিক্ত merge চোখে দেখে যাচাই করে promote করা হয়েছে (মোট **৯টি merge**)।
- **Track B — bold-rule robustness: কোনো signal-ই knife-edge সারাতে পারেনি — তবে আসল কারণ পাওয়া গেছে:** May-র WIDTH মান DNA-bold ওজনে ছাপা, DNA-regular ওজনে নয়; verifier-এর "regular" প্রত্যাশাটাই প্রশ্নের মুখে। নিয়ম বদলানো হয়নি; **৪২/৪৩ known exception হিসেবে রাখা হয়েছে** (সিদ্ধান্ত §৫.৪)।
- **Track C — save→label wiring + Description + Aug p2 পাতা:** live পাতায় save→label **৯০/৯০**; Description **১৮/৬৯ → ৩৮/৬৯ (+২০, ভুল ভাঙা ০, ভুল merge ০)** — সঙ্গে R7-এর ৩৫/৬৯ বেসলাইনের সৎ সংশোধন (§৪.২); Aug p2 live পাতা **১৬/১৬**।
- **Merge:** PG মোট বাক্স ৪২৪৬ → **৪২৩৫ (−১১)**; ৫টি live পাতা rebuild (wiring-সহ); নমুনা **৫১৮/৫১৮, অতিরিক্ত ০**; চূড়ান্ত যাচাই §৭-এ।

## ২. Track A — DNA-glyph টেমপ্লেট-ম্যাচার (রিপোর্ট: `improve/round8/track-a/track-a-report.md`)

- **লক্ষ্য:** Round 7-এ OCR-lexicon দিয়ে যাচাই করা ৬টি over-split (DEPARTMENT ×১ + e-mail ×৫) OCR-ছাড়া উদ্ধার করা — ব্যবহারকারীর স্থায়ী নির্দেশ "OCR বাদ দিয়ে"।
- **পদ্ধতি (নিয়ম আগে ঠিক করা, তারপর মাপা):** (১) boundary white-run পরীক্ষা — টুকরোর সীমানায় সবচেয়ে লম্বা সম্পূর্ণ-সাদা কলাম-রান; (২) exemplar-ink render IoU — একই শব্দের অন্য পাতার পুরো-বাক্স কালি দিয়ে template, merged বনাম split IoU তুলনা।
- **মাপা ফল — ৬/৬, ভুল merge ০:** white-run: intra-word ০–৫ px, সত্য word-gap ৬–১৫ px (৩৯৭ জোড়ায় bimodal, পরিষ্কার); ৬ লক্ষ্য ২–৫ px-এ পাস, ৮টি সত্য দুই-শব্দ control সঠিকভাবে বাতিল (৬–১৩ px)। IoU: merged ০.৭১১–০.৮৭৩, split ০.৩৮৩–০.৪৪২, margin ০.২৭০–০.৪৫৭ (নিয়ম: ≥০.৬০ ও margin ≥০.০৫)। ৬টি merged শব্দই overlay clip-এ চোখে দেখা।
- **Cross-validation:** r8 box সেট Round 7-এর OCR-lexicon staging-এর সঙ্গে **১৪টি PG পাতায় অভিন্ন** — দুটি স্বাধীন পদ্ধতি একই জ্যামিতিতে পৌঁছেছে।
- **সৎ caveat (রান ১ বনাম রান ২):** আগে থেকে ঠিক করা may-p6 whole-box template-এ প্রথম রানে মাত্র ১/৬ (৫ e-mail IoU ০.৪৫৪–০.৫৯১) — may-p6 outlier template (median pairwise ০.৫৮৭ বনাম অন্যদের ০.৭২–০.৮০)। নিয়ম অপরিবর্তিত রেখে শুধু ত্রুটিপূর্ণ instrument বদলে leave-one-out medoid template নেওয়া হয়েছে → ৬/৬। দুই রানই JSON-এ সংরক্ষিত; revert এক লাইন।
- **DNA-ফন্ট render ব্যর্থ (diagnostic, gate নয়):** regular IoU ০.২৪০, bold ০.৩৬৪, সেরা ১২° shear ০.৪৬৩ — DNA ফন্ট upright sans clone, header italic serif; তার cmap-এ e-mail-এর ৮টি glyph নেই (p,g,f,i,l,s,n,@)। Exemplar-ink render-ই কার্যকর পরীক্ষা।
- **অতিরিক্ত সন্ধান (প্রয়োগ করা হয়নি):** DEPARTMENT aug-p1/p3/p6/p7/p8-এও ভাঙা (সব matcher-এ পাস) ও www.pgfoils.in সব may পাতায় ভাঙা (Test 1 পাস, কিন্তু কোথাও whole-box exemplar নেই বলে Test 2 অসম্ভব) — coordinator-এর জন্য রাখা (Round 9)।

## ৩. Track B — Bold-rule robustness (রিপোর্ট: `improve/round8/track-b/track-b-report-r8b.md`)

- **কাজ:** Round 7 §৬.৩-এর May-p3 WIDTH knife-edge (ratio ০.১৫৬ বনাম threshold ০.১৫৫২) ভালো boldness signal দিয়ে সারানো।
- **পরীক্ষিত signal — সব FAIL/REJECT (মাপা):** document-level median FAIL (May-p3 WIDTH bold-ই থাকে +০.০০০৯; May-তে ৭টি flip সবই আসলে bold — সংশোধন, regression নয়; Aug-এ ৩ flip, ২টি regression — "WEBSITE:" সত্যি bold → regular); DNA IoU ভোট tie ২–২; per-glyph t collapse (tight-crop distance-transform artefact ধরা পড়েছে — solid 'I' unpadded-এ ০.৫০০ বনাম padded-এ ~০.১১; শুদ্ধ reference gap মাত্র ০.০২–০.০৪); word-level t FAIL (May ink gain ~+০.০৩৩ পুরো regular→bold gap ~০.০২৭-কে ছাপিয়ে যায়); gain-calibrated t FAIL (near-regular বনাম near-bold gain সম্পূর্ণ overlap); cap-height normalisation REJECT (সব পাতায় gap negative); population median REJECT (May-p1 WIDTH bold হয়ে যায়)।
- **মূল সন্ধান — May-র WIDTH মান আসলে bold-ওজন:** same-glyph stroke (padded DT): May obs '0'/'7' ০.১৩২–০.১৪৬ (n=১৩, mean ০.১৪০), Aug **bold** glyph-এর (০.১৩৪–০.১৪১) ও DNA-bold-এর (০.১৪২) সঙ্গে মেলে — Aug regular-এর (০.১০৫–০.১১৪) বা DNA-regular-এর (০.১২১) সঙ্গে নয়। Browser side-by-side (একই string, আসল Chromium + আসল ফন্ট): Aug scan DNA-regular-এর সঙ্গে মেলে; May scan "670.0"/"770.0" DNA-bold-এর সঙ্গে মেলে। Live-render stroke: May-p1 regular render ০.১০৭ বনাম scan ০.১৫৫ (Δ −০.০৪৭, চোখে স্পষ্ট হালকা); May-p3 bold render ০.১৪৭ বনাম scan ০.১৫৬ (Δ −০.০০৯, প্রায় সঠিক)। **অর্থাৎ May p1/p2 WIDTH এখন ভুল (হালকা) ওজনে render হচ্ছে, May p3 (bold) প্রায় সঠিক — verifier-এর "regular" প্রত্যাশা উল্টো দিকে তাকিয়ে আছে।**
- **সতর্কতা:** চোখে-দেখা কিছুটা বিপরীত ইঙ্গিত দেয় (bold "771.5" ভারী লাগে — সম্ভবত '5' বনাম '0' character-mix); DNA-তে medium weight নেই — "bold বনাম medium" চূড়ান্ত নয়, কিন্তু "regular" সমর্থিত নয়।
- **কোনো নিয়ম বদলানো হয়নি, কোনো ফন্ট promote করা হয়নি, কোনো পাতা rebuild করা হয়নি (এই track-এ)।** Control reproduce: fontfix **৪৩/৪৩**, May p2/p3 **৪২/৪৩** (একমাত্র fail অপরিবর্তিত)।
- **Parallel agent-এর lead (তার ফল, আমার agent-এর নয়):** neighbourhood-mean IoU margin — একমাত্র gap-ওয়ালা signal (+০.০২৬, threshold +০.০৬৭) — Round 9-এর প্রার্থী।

## ৪. Track C — Save→label wiring + Description + Aug p2 (রিপোর্ট: `improve/round8/track-c/track-c-report-r8c.md`)

### ৪.১ Save→label wiring — DONE
- **ডিজাইন (template-patch + driver):** live পাতা static ফাইল — DB লেবেল নম্বর (LBL-xxxx) সে নিজে দিতে পারে না; নম্বর দেয় ড্রাইভার, ডেলিভারি রেকর্ড করার সময়। পাতায় "💾 সেভ করুন → লেবেল" বোতাম; সেভ করলে এই পাতার নিজের DEMO বাক্স থেকে বর্তমান Lot/WIDTH পড়ে, এই পাতার নিজের লেবেল কার্ড দেখায় (খসড়া — LBL নম্বর পরে), আর লেবেল-খসড়া HTML + এডিট JSON ডাউনলোড দেয়। `?save`-এ auto-save (headless যাচাইয়ের জন্য)। ড্রাইভার এডিট JSON পড়ে, প্রমাণিত write-back দিয়ে এডিটেড পাতার PDF বানায়, Round 7 Track A-র লেবেল টেমপ্লেটে নম্বরসহ লেবেল রেন্ডার করে, **স্টেজিং DB**-তে ডেলিভারি রেকর্ড করে। শেয়ার্ড DB কখনো লেখার জন্য খোলা হয় না।
- **প্রমাণ:** live পাতা ব্রাউজার প্রমাণ **৯০/৯০** (৫ পাতা × ১৮/১৮, Playwright) — Aug p1-এ 781.5/207/9, May p2-এ 721.5/283/7, কখনো অন্য পাতার মান নয়; leak ০; দুটি কার্ড চোখে দেখা। ড্রাইভার আউটপুট **২২/২২** (শুধু-পড়া পুনঃযাচাই) — স্টেজিং চেইন অক্ষত (২৬ এন্ট্রি), LSE-0008 (Aug p.1, LBL-0001) + LSE-0009 (May p.2, LBL-0002) v3-তে যাচাই হয়। Wired পাতায় fontfix **৪৩/৪৩**।
- **Parallel agent-এর Blob-URL ডিজাইন (৩৪/৩৪ দাবি) ব্যবহার করা হয়নি** — প্রমাণ উপরের ৯০/৯০ + ২২/২২।

### ৪.২ Description — ১৮/৬৯ → ৩৮/৬৯, সঙ্গে R7-এর বেসলাইন সংশোধন
- **বেসলাইন সংশোধন (সৎ):** কঠোর scorer + নিজের গ্রাউন্ড-ট্রুথে r7 seg-এর বেসলাইন **১৮/৬৯**, R7-এর দাবি করা **৩৫/৬৯ নয়** — ৩৫ কোনো seg-এ, কোনো নিয়মে পুনরুৎপাদন হয় না (কঠোর নিয়মে ১৮, ঢিলা নিয়মে ৫৭); R7-এর ৩৫-এর কোনো গোনার স্ক্রিপ্ট নেই (সম্ভবত render দেখে হাতে গোনার ভুল — R7 নিজেই পুরনো "৪/৬৯" গোনাটিকে একই ভুল বলেছিল)। পুরনো seg-ও ০ নয়, **৭/৬৯**। এই রাউন্ডের বেসলাইন ১৮/৬৯ — এখান থেকেই উন্নতি মাপা হয়েছে।
- **জয়ী নিয়ম (মাপা):** লম্বা বাক্স y-তে ভাগ + component gap ≥৫-এ x-ভাগ + <২০px টুকরো বড় gap-এর দিকে জোড়া। **১৮/৬৯ → ৩৮/৬৯ (+২০), ভুল ভাঙা ০, ভুল merge ০।** PG no-regression **৫১৮/৫১৮**।
- **R7-এর আরও দুটি সংশোধন:** SB লাইন ("SB NO 5773912 DTD 08/08/26") — R7 বলেছিল দুই seg-এই কোনো বাক্স নেই; **ভুল — তিনটি seg-এই বাক্স আছে** (SB/NO সঠিক; MEGA বাক্সে ৩ শব্দ); বেসলাইনে SB লাইন **২/৫** (০/৫ নয়)। N5 উপ-গোনা "SB/NO/CARRIER/NAME ৪" — r7 seg-এ চারটিই সঠিক (**৪/৪**) — R7-এর ≤২৩ সংশোধন ভুল ভিত্তিতে করা; **২৬ বনাম ৩১ অসঙ্গতি এখনো অমীমাংসিত** (পূর্ণ গ্রাউন্ড-ট্রুথ নেই)।
- **সীমা (মাপা):** দশমিক-জোড়া (56775.21) gap দিয়ে অসম্ভব — G=৩-এ ১৪টি, G=৮-এ ৪৯টি সত্য শব্দ-জোড়া ভুল merge হতো; বাকি **৩১ শব্দের** জন্য অক্ষর-পরিচয় (DNA-glyph matcher) লাগবে — gap-পদ্ধতির সীমা মাপা শেষ।

### ৪.৩ Aug p2 live পাতা — DONE (১৬/১৬)
- উৎস `improve/round7/merge/segs/seg-aug-p2-r7m.json` (৩০১ শব্দ); বিল্ডারে আসল বাগ ধরা পড়ে ঠিক করা হয়েছে (`__PAGE_META__` placeholder ভরত না — এখন ভরে)। যাচাই **১৬/১৬** (১৫ + ১ wiring চেক) — Lot 207/9 + WIDTH 776.5, Hard অক্ষত, চোখে দেখা ৩টি ক্লিপ, মূল ছবি byte-identical (SHA `11c3aacf…`)।

### ৪.৪ LBL-0002 নম্বর-সংঘাত → সিরিয়াল নিয়ম (সিদ্ধান্ত §৫.৩)
- স্টেজিং DB-র লেবেল সিরিয়াল নতুন করে শুরু হয় বলে Track C staging-এ LSE-0009 (May পা.২)-এর লেবেল **LBL-0002**; কিন্তু Round 7 Track A-র `labels/`-এ LBL-0002 হলো **Aug পা.২**-এর লেবেল ফাইল। একই নম্বর, ভিন্ন পাতা। DB-তে সংঘাত নেই (স্টেজিং DB আলাদা), কিন্তু নম্বর-নেমস্পেসে আছে।

## ৫. Merge — কী promote করা হয়েছে, কী সিদ্ধান্ত নেওয়া হয়েছে

### ৫.১ Promote করা হয়েছে (r8m seg সেট)
- **PG seg (r8m):** Track A-র ৬ লক্ষ্য + নিচের ৩টি অতিরিক্ত — মোট **৯টি merge**; PG মোট ৪২৪৬ → **৪২৩৫ (−১১)**। Live পাতার শব্দ: aug-p1 ৩০৫ → **৩০৪**, may-p1 ৩০৬ → **৩০৪**, may-p2 ৩০৬ → **৩০৫**, may-p3 ৩০৪ → **৩০৩**, aug-p2 ৩০১ (অপরিবর্তিত — aug-p2-র e-mail লেজ সৎ miss হিসেবে রয়ে গেছে)।
- **Raviraj seg (r8m):** Track C-র Description seg — ৫৭৪ → **৫৯৭** বাক্স, Description **৩৮/৬৯**।
- **৫টি live পাতা rebuild** (Round 6 ফন্ট, FIT_TARGET ০.৯৮ অপরিবর্তিত; save→label wiring-সহ): Aug `047a6d6b…`, Aug p2 `aced12fc…`, May `8944d835…`, May p2 `82ab16d0…`, May p3 `db72deaa…`।
- **Verifier expectation আপডেট (মাপা নতুন সংখ্যা, Round 6/7-এর নিয়ম অনুযায়ী):** fontfix/verify_round2-তে Aug মোট ৩০৫ → ৩০৪, May মোট ৩০৬ → ৩০৪; verify_may23-তে p2/p3 মোট ৩০৬/৩০৪ → ৩০৫/৩০৩।
- **অপরিবর্তিত:** শেয়ার্ড Round 3 DB (`1c065457…`, ২০ entry, LSE-0001–0007, chain linked); DNA ফন্ট (`187b2dfe…` / `33583cf2…`); `REPORT.md` / `REPORT-MAY.md` / `ROUND2–7-REPORT.md`; Drive-এ কিছু আপলোড করা হয়নি।

### ৫.২ ৩টি অতিরিক্ত merge — আমি নিজে যাচাই করে promote করেছি
Parallel agent-এর matcher-ও একই ৩টি merge-এ পৌঁছেছিল (তার "false_merge: 3" আসলে কঠোর ৬-লক্ষ্য গণনার লেবেল — সে নিজেই এগুলোকে চোখে-দেখে সঠিক বলেছে)। আমি নিজে যাচাই করেছি, তার দাবি বিশ্বাস করে নয়:
- **White-run পরীক্ষা (আমার agent-এর Test 1, নিজে চালানো):** aug-p1 লেজ gap ৩৩ → white run **৪**; aug-p3 পুরো e-mail gap ১৫ → **৪**; aug-p4 লেজ gap ৩৫ → **৫** — তিনটিই ≤৫, PASS।
- **চোখে দেখা:** `verify-X1/X2/X3` clip — aug-p3-এ "pgfoils@pgfoils.in" একটানা, aug-p1/p4-এ "pgfoils.in" একটানা।
- **Exemplar:** aug-p8-এর একক-বাক্স [1124,404,1272,434] r7m seg-এ আছে (যাচাই করা)।
- **সিদ্ধান্ত: ৩টি promote করা হয়েছে।** BY SALES সঠিকভাবে KEEP আছে (S_w ০.৮৯৩ সত্ত্বেও — exemplar-লাইব্রেরি দূষণ: aug-p5-এর exemplar নিজেই দুই শব্দ; wordlist veto-তে বেঁচেছে — এই শিক্ষা merge-এ নেওয়া হয়েছে)। aug-p2 e-mail লেজ সৎ miss হিসেবে রয়ে গেছে (exemplar-নির্বাচনের দুর্বলতা — Round 9)।

### ৫.৩ LBL সিরিয়াল নিয়ম (সিদ্ধান্ত — blanket permission-এর অধীনে)
**নিয়ম: লেবেল সিরিয়াল কেন্দ্রীয়ভাবে শেয়ার্ড DB থেকে issue-র সময় বরাদ্দ হয় — বিশ্বজুড়ে unique, কখনো restart নয়।** Staging DB-তে restart হওয়া শুধু staging artifact; production-এ LBL-0002 একবারই থাকবে। Track C staging-এর LBL-0002 (May পা.২) ও Round 7-এর LBL-0002 ফাইল (Aug পা.২) — দুটি আলাদা staging DB-র test নম্বর, production ডেটা নয়; merge-এ কোনো ফাইল rename করা হয়নি, শুধু নিয়ম লেখা হয়েছে।

### ৫.৪ May WIDTH প্রত্যাশা — সিদ্ধান্ত: ৪২/৪৩-ই থাকবে, প্রত্যাশা বদলানো হবে না (এই রাউন্ডে)
Track B-র মাপ বলছে May WIDTH আসল bold-ওজন (§৩) — কিন্তু কোনো নিয়ম May p1/p2-কে পরিষ্কারভাবে bold বলতে পারে না (DNA IoU tie, gain overlap), আর চোখে-দেখা কিছুটা বিপরীত ইঙ্গিত দেয় ('5' বনাম '0' mix)। প্রত্যাশা bold-এ বদলালে p1/p2-ও bold করতে হয় — নিয়ম ছাড়া সেটা শুধু verifier-এর fail এক জায়গা থেকে আরেক জায়গায় সরানো। **তাই: নিয়ম অপরিবর্তিত, প্রত্যাশা regular-ই আছে, May-p3 WIDTH ৪২/৪৩-এর একমাত্র fail হিসেবে known exception হিসেবে রয়ে গেছে।** Parallel agent-এর IoU-margin lead (একমাত্র gap-ওয়ালা signal, +০.০২৬) Round 9-এর প্রার্থী — glyph identification + বড় probe সেট লাগবে।

### ৫.৫ Description seg — সিদ্ধান্ত: আমার agent-এর ৩৮/৬৯ promote, parallel ৪৪/৬৯ নয়
Parallel agent-এর Description seg আমার agent-এর কঠোর scorer-এ **৪৪/৬৯** পায় (৩৮-এর চেয়ে ৬ বেশি) — কিন্তু **TOTAL ভেঙেছে** (তার হাতের TOTAL বাক্স VALUE-র "V" পর্যন্ত চলে গেছে — প্রমাণিত false merge), আর তার নিজের ৬৩/৬৮ দাবি ঢিলা নিয়ম + বদলানো গ্রাউন্ড-ট্রুথে। **সিদ্ধান্ত: ০ ভুল merge-এর ৩৮/৬৯ promote করা হয়েছে; ৪৪/৬৯ নয়।** দুটি পদ্ধতি মিলিয়ে (তার component-পুনর্নির্মাণ + কঠোর যাচাই + TOTAL ঠিক করা) ~৪৫–৪৬/৬৯ সম্ভব — Round 9-এর কাজ।

### ৫.৬ Merge-এ ধরা পড়া বিষয়
1. **আমার নিজের ভুল (ধরা পড়েছে, ঠিক করা হয়েছে):** প্রথম identity-probe ক্লিপে ভুল coordinate ব্যবহার করেছিলাম (WORDS coordinate-কে CSS ধরে — পাতার ~১৫০px offset বাদ গিয়েছিল), ক্লিপে WIDTH সারির বদলে header দেখা গিয়েছিল। Round 7-এর merge-ও ঠিক এই ভুল করেছিল। চোখে দেখেই ধরা পড়েছে; bounding-rect দিয়ে আবার নেওয়া হয়েছে — প্রক্রিয়াটাই কাজ করেছে। Probe-এর PASS/FAIL দাবি (element geometry দিয়ে) সবসময় সঠিক ছিল — শুধু clip-গুলো ভুল জায়গার ছিল।
2. **Aug p2 পাতার alt নিয়ে Track C-র দাবি ভুল ছিল:** শেয়ার্ড-রুটের aug-p2 পাতা "page 1" বলে নয় — বর্তমান ফাইল byte-identical (diff ০ লাইন), alt "page 2" সঠিক।

## ৬. Collision — Duplicate coordinator-এর পূর্ণ বিবরণ (parent-এর জন্য)

**কী ঘটেছে:** ২০২৬-১১-০৭ ০৬:৫৯:৩২ +০৬-এ scheduled job `lse-round7-morning-report` থেকে একটি Round 8 coordinator তৈরি হয়েছে (`76439502…`, parent `37340aa3…`) — আমার (মূল agent-এর সরাসরি নির্দেশে তৈরি, `b8f723ce…`) **১৯ সেকেন্ড আগে**। দুজনে একই কাজ, একই ডিরেক্টরি, একই ফাইলনামে।

**Timeline (UTC):**
- ০১:০২–০১:৩৬: দুই Track A agent একই ডিরেক্টরিতে — আমার agent (`_r8a` ফাইল, ৬/৬ ০ false merge), parallel agent (`dna_matcher.py`, `evaluate.py`, ৫৪ MB `exemplar-library.pkl`, ৬/৬ + ৩ অতিরিক্ত)।
- ০১:১৮–০১:১৯: ৪টি live পাতা rebuild (parallel agent-এর merge-এর অংশ বলে মনে হয়) + নতুন Aug p2 পাতা।
- ০২:১২: parallel agent `_r8c` suffix-ও নকল করে ফাইল লিখতে শুরু করে (`desc_recover.py`, `seg-rav-p2-r8c-desc.json`) — suffix আর লেখক চেনায় না।
- ০২:৩২:৫১: parallel merge আমার `improve/round8/merge/segs/`-এর **১৫টি ফাইলই** overwrite করে (তার r8 seg দিয়ে)।
- ০২:৩৩:০৬: parallel merge আমার `improve/round8/merge/backup/`-ও overwrite করে।
- ০২:৩৪:৩৯: শেয়ার্ড `seg-aug-p1-300.json` overwrite (৩০৪ → ৩০৫)।
- ০২:৩৫:১০–২৯: ৫টি live পাতা rebuild (তার r8 seg দিয়ে — May পাতাগুলো byte-identical, Aug p1-এ আমার অতিরিক্ত merge নেই)।
- এরপর: শেয়ার্ড verifier-দের expectation-ও তার সংখ্যায় বদলে দেয় (fontfix/verify_round2-তে Aug ৩০৪ → ৩০৫; verify_may23-তে তার comment "3 extras NOT applied")।

**আমি কী করেছি:** আমার তিন track-এর output অক্ষত আছে কি না যাচাই করেছি (track-a/b/c-র `_r8a`/`_r8b`/`_r8c` ফাইল + JSON — সব intact); merge-কে **নিরাপদ private ডিরেক্টরি `improve/round8/merge-b8f7/`-তে** আবার বানিয়েছি (আমার agent-দের intact ফাইল + ৩ extras, আবার যাচাই: sample ৫১৮/৫১৮, title ১৪/১৪, H2 ১৪/১৪, Description ৩৮/৬৯); Aug p1 পাতা আবার build করে SHA মিলিয়েছি (`047a6d6b…` — deterministic, byte-identical); শেয়ার্ড tree-কে আমার verified merge অবস্থায় ফিরিয়েছি (seg ৩০৪, পাতা ৫টি, verifier expectation ৩০৪); এই রিপোর্ট লিখেছি + private কপি রেখেছি।

**এখনো ঝুঁকি:** parallel coordinator শেষ চেকের সময়ও **running** ছিল (last activity ১৫ সেকেন্ড আগে) — সে তার নিজের ROUND8-REPORT.md লিখতে পারে এবং এই রিপোর্ট বা শেয়ার্ড পাতা আবার overwrite করতে পারে। **Parent-কে করতে হবে:** (১) `lse-round7-morning-report` schedule-টি থামানো/ঠিক করা — একই কাজ দুবার চলছে; (২) Drive-এ কিছু আপলোড করার আগে শেয়ার্ড tree-র SHA §৯-এর সঙ্গে মিলিয়ে নেওয়া; (৩) এই রিপোর্টের SHA মিলিয়ে নেওয়া (নিচে)। আমার merge-এর নিরাপদ কপি `improve/round8/merge-b8f7/`-তে আছে — সেখান থেকে যেকোনো সময় পুনরুদ্ধার করা যায়।

## ৭. চূড়ান্ত যাচাই টেবিল (merge-এর নিজের re-run — সব সংখ্যা এই রাউন্ডে চালিয়ে মাপা)

| যাচাই | ফল (Round 8 merge) | Round 7 |
|---|---|---|
| fontfix_verify300 | **৪৩/৪৩** | 43/43 |
| verify_round2_300 | **১৮/১৮** | 18/18 |
| repro300 (doubling) | **PASS** | PASS |
| manual_proof300 | **১০/১০** | 10/10 |
| Identity probe (Lot+WIDTH+Hard, ৫টি live পাতা) | **১৫/১৫** (চোখে দেখা — Lot পরিষ্কার, WIDTH পরিষ্কার, "Hard" অক্ষত, doubling নেই) | 8/8 (৪ পাতা) |
| Write-back | **৪১/৪১, FAILURES: none** | 41/41 |
| Track D staging | **৪৮/৪৮** | 48/48 |
| Track C staging | **৭৪/৭৪** | 74/74 |
| May multipage | **৫৯/৫৯** | 59/59 |
| May p2/p3 | **৪২/৪৩** — ১ fail: May-p3 WIDTH obs regular (weight=700), knife-edge (§৩, §৫.৪) | 42/43 |
| sqlcipher | **১৫/১৫** | 15/15 |
| keymgmt | **২৫/২৫** | 25/25 |
| Save→label live (৫ পাতা) | **৯০/৯০** | — (নতুন) |
| Aug p2 live পাতা | **১৬/১৬** | — (নতুন) |
| PG sample (r8m seg) | **৫১৮/৫১৮, অতিরিক্ত ০**; টাইটেল ১৪/১৪, H2 ১৪/১৪ | 518/518 |
| Description (r8m seg, কঠোর scorer) | **৩৮/৬৯** (বেসলাইন ১৮/৬৯; R7-এর ৩৫/৬৯ সংশোধিত) | 35/69 (সংশোধিত: ১৮) |
| Raviraj (whole-page recount) | **পুনর্গোনা হয়নি** — +২০ Description-শব্দের পর পূর্ণ-পাতা সংখ্যা Round 9-এ মাপতে হবে (R7: ৩৪৬/৩৯৪ = ৮৭.৮%) | 346/394 = 87.8% |

**নোট:** fontfix/verify_round2/repro/manual/identity — চূড়ান্ত shared-tree অবস্থায় আবার চালানো হয়েছে (parallel overwrite-এর পর পুনঃস্থাপন করে)। Write-back/Track D/Track C/multipage/sqlcipher/keymgmt — staging DB/ফাইলে চলে, পাতা-overwrite-এর প্রভাব নেই। Save→label/Aug-p2 — আমার build-এ চালানো (পাতাগুলো byte-identical বলে এখনো বৈধ)।

## ৮. সৎ সীমা — এখনো যা সম্পূর্ণ নয় (Round 9-এর প্রার্থী)

1. **May WIDTH প্রত্যাশা** (§৩, §৫.৪) — bold নাকি regular, তা ঠিক করা + parallel agent-এর IoU-margin lead (gap +০.০২৬) যাচাই (glyph identification + বড় probe সেট লাগবে)।
2. **DNA-glyph matcher-এর বাকি:** aug-p2 e-mail লেজ (সৎ miss — exemplar-নির্বাচন), DEPARTMENT অন্য পাতায় (aug-p1/p3/p6/p7/p8), www.pgfoils.in (কোথাও whole-box exemplar নেই)।
3. **Description-এর বাকি ৩১ শব্দ** — gap-পদ্ধতির সীমা মাপা শেষ; DNA-glyph matcher ছাড়া এগোবে না। Raviraj whole-page পুনর্গোনা বাকি।
4. **N5 ২৬ বনাম ৩১ অসঙ্গতি** — এখনো অমীমাংসিত (পূর্ণ গ্রাউন্ড-ট্রুথ নেই)।
5. **০.৯৮ margin মাত্র ২%** — ttfautohint আসল সমাধান নয় (Round 7-এ প্রমাণিত); পরের ধারণা Track B রিপোর্ট §৭-এ।
6. **LBL সিরিয়াল নিয়ম** (§৫.৩) — শেয়ার্ড DB-তে কেন্দ্রীয় বরাদ্দ বাস্তবায়ন বাকি (এই রাউন্ডে শুধু নিয়ম লেখা হয়েছে)।
7. আগের মতোই খোলা (ব্যবহারকারী/আইনজীবী ছাড়া অসম্ভব): print calibration (ফ্যাক্টরির প্রিন্টার), US পেটেন্টের আইনি যাচাই। DBNet swap স্থগিত; DPAPI VM-এ অপ্রমাণিত। Round 4-এর পুরনো built পাতায় fontfix ৩৮/৩৯ (May Lot typed ratio ১.০৭ বনাম সীমা ১.০৫) — আগের থেকেই marginal fail, regression নয়।

## ৯. ফাইল তালিকা ও SHA (যাচাইয়ের জন্য)

**এই রাউন্ড (`improve/round8/`):**
- `ROUND8-REPORT.md` — এই রিপোর্ট (এখন `improve/`-তে; নিরাপদ কপি `improve/round8/merge-b8f7/ROUND8-REPORT.md`-তেও আছে)
- `track-a/track-a-report.md` + `track-a-report-dna.md` (parallel agent-এর — তুলনার জন্য রাখা, promote করা হয়নি) + `scripts/dna_matcher_r8a.py`, `apply_r8.py`, `check_regression_r8.py`, `segs/seg-*-r8.json` (১৫টি), `matcher-results-r8a.json`, `clips/overlay-*.png`
- `track-b/track-b-report-r8b.md` + `track-b-report.md` (parallel agent-এর — তুলনার জন্য রাখা) + `measure_ratios.py`, `dna_*.py`, `fontfix_verify300_r8b.py`, `verify_may23_pages_r8b.py`
- `track-c/track-c-report-r8c.md` + `scripts/*_r8c.py`, `segs/seg-rav-p2-r8.json`, `staging/live-scan-page-aug-p2-300-r8c.html`, `staging/lse_gravora_r8c.db`
- `merge-b8f7/` — **আমার merge-এর নিরাপদ কপি:** `segs/seg-*-r8m.json` (১৫টি, PG ৪২৩৫ + Rav ৫৯৭), `pages/live-scan-page-aug-300-r8m.html`, `sample_rows_r8m.py`, `check_titles_h2_r8m.py`, `probe_identity_r8m.py`, `backup/` (merge-আগের shared state)
- `merge/` — ⚠️ **parallel agent-এর overwrite করা ডিরেক্টরি — ব্যবহার করবেন না** (তার r8 seg দিয়ে ভরা; আমার আসল merge ফাইলগুলো `merge-b8f7/`-তে)

**Shared tree-তে promote করা (merge-এর, চূড়ান্ত অবস্থা):**
- `seg-aug-p1-300.json` (৩০৪), `seg-may-p1-300.json` (৩০৪), `improve/round4/merge/segs/seg-may-p2-300m.json` (৩০৫), `improve/round4/merge/segs/seg-may-p3-300m.json` (৩০৩), `improve/round7/merge/segs/seg-rav-p2-r8m.json` (৫৯৭)
- `live-scan-page-aug-300.html` (`047a6d6b…`, ৩০৪ শব্দ), `live-scan-page-may-300.html` (`8944d835…`, ৩০৪), `live-scan-page-may-p2-300.html` (`82ab16d0…`, ৩০৫), `live-scan-page-may-p3-300.html` (`db72deaa…`, ৩০৩), `live-scan-page-aug-p2-300.html` (`aced12fc…`, ৩০১)
- `fontfix_verify300.py` (Aug মোট ৩০৪, May মোট ৩০৪), `verify_round2_300.py` (Aug ৩০৪, May ৩০৪), `improve/round6/track-c/scripts/verify_may23_pages.py` (p2/p3 মোট ৩০৫/৩০৩)
- **অপরিবর্তিত:** শেয়ার্ড Round 3 DB (`1c065457…`, ২০ entry, LSE-0001–0007), DNA ফন্ট (`187b2dfe…` / `33583cf2…`), `REPORT.md` / `REPORT-MAY.md` / `ROUND2–7-REPORT.md`, Drive-এ কিছু আপলোড করা হয়নি।

---

*সব সংখ্যা merge-এর নিজের চালানো — যা চালানো হয়নি তা দাবি করা হয়নি। চোখে দেখার দাবি সব clip-এ যাচাই করা। পরিচয় যাচাই row label + box দিয়ে, অবস্থান দিয়ে নয়। Parallel agent-এর কোনো সংখ্যা এই রিপোর্টের দাবি হিসেবে ব্যবহার করা হয়নি — শুধু তুলনা/সতর্কতা হিসেবে উল্লেখ করা হয়েছে।*
