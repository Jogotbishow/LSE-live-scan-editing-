# Live-Scan — প্রোটোটাইপ ও নির্ভুলতা রিপোর্ট (Prototype & Accuracy Report)

> **প্রযুক্তি: LSE — Live-Scan Editing** (পূর্বনাম: Live-Scan) — স্ক্যান-ই-পাতা; টেক্সট একটি living layer। OCR এডিট-পথে নেই।
> আসল ফাইল: PG Foils সাপ্লায়ার COA, "PG AUGUST-2026 (25mic) COA.pdf" — পাতা ১।
> গবেষণা সংশ্লেষ: `RESEARCH.md`। চারটি ট্র্যাক-রিপোর্ট: `research-livescan.md`, `research-ocr.md`, `research-inpaint.md`, `research-products.md`।

---

## ১. আসল পাতাটি কী

- **উৎস:** `~/workspace/gravora-review/packfirm-analysis/supplier-coa/PG AUGUST-2026 (25mic) COA.pdf` — ৮ পাতা, প্রতিটি ৩০০ DPI রঙিন JPEG স্ক্যান, **শূন্য extractable text** (pure scan)।
- **পাতা ১:** PG Foils Ltd.-এর ANALYTICAL TEST REPORT — PRODUCT: BLISTER FOIL, 25 Micron, Lot No. 206/7, Quantity 5118.60 Kgs, ১৮-সারির test table (WIDTH, ALU. THICKNESS, GRAMMAGE…), Conclusion, Test Condition, Prepared By / Approved By — হাতে লেখা নীল কালির স্বাক্ষর ও তারিখসহ।
- স্ক্যানটি পরিষ্কার ছাপা লেখা; পাতার মাঝখানে একটি হালকা vertical scanner-line artifact আছে (মূল স্ক্যানেই আছে — প্রোটোটাইপের দোষ নয়)।

## ২. যা বানানো হয়েছে — pipeline

```
PDF পাতা → 200 DPI PNG → word segmentation (OpenCV connected components, OCR নেই)
         → inpainting (Telea) দিয়ে পরিষ্কার background → HTML live-scan পাতা
HTML পাতা = মূল স্ক্যান (background) + ৩০২টি clickable word span (overlay)
ক্লিক → span-এর নিচে পরিষ্কার background দেখা যায় → contenteditable → টাইপ → real time
```

| ধাপ | টুল / পদ্ধতি | ফল |
|---|---|---|
| Page extract | `pdftoppm` 200 DPI | `pages/aug-p1-1.png` — 1653×2323, RGB |
| Segmentation | `segment.py` — OpenCV connected components, gap threshold 0.35×median char height, signature-row exclusion (SIGROW y=2000) | **৩০২টি শব্দ, ৪৪টি লাইন** (`seg-aug-p1.json`); median component height 17 px; signature row 0 শব্দ (ইচ্ছাকৃতভাবে বাদ — হাতের লেখা এডিট করা যায় না) |
| Inpainting | `inpaint.py` — threshold <210 + 3×3 dilate একবার, Telea radius 4 | `pages/aug-p1-clean.png` — ৩০২টি box, ৩২৭,৭৭১ masked pixel (পাতার **৮.৫৪%**), mean abs diff 5.46 |
| Live page | `build_page.py` → `live-scan-page.html` (১,৬৩৯,২৩০ bytes) | মূল স্ক্যান background (JPEG base64) + clean layer (প্রতিটি span চালু হলে তার নিচে দেখা যায়) + ৩০২টি span; font Georgia serif, size = box height থেকে, bold = ink density থেকে অনুমান |
| Demo edit | `patch_demo.py` + `?demo=1` | Lot No. **206/7 → 207/9**; WIDTH-র Observation **780.0 → 781.5** |
| Screenshot | Playwright + Chromium Headless Shell | `shots-page-plain.png`, `shots-page-edited.png`, `shots-clip-rows.png` |

**OCR কোথায় আছে:** কোথাও নেই — এডিট-পথে নয়। শুধু তুলনার জন্য RapidOCR একবার চালানো হয়েছিল (নিচে §৫) — সেটা ঐচ্ছিক recognition স্তরের প্রার্থী হিসেবে, প্রোটোটাইপের অংশ হিসেবে নয়।

## ৩. মাপা নির্ভুলতা — Segmentation (হাতে যাচাই করা নমুনা)

**পদ্ধতি:** টেস্ট-টেবিলের সারি ০১–০৫ (৫টি সারি) — মূল স্ক্যান থেকে চোখে গুনে সত্যিকারের শব্দের সংখ্যা বের করা হয়েছে, তারপর প্রতিটি segmented box-এর সঙ্গে এক-এক করে মেলানো হয়েছে। সারির সীমানা ঠিক করা হয়েছে S.No. লেবেলের box-এর y থেকে (header y~750–790, row 01 y 808–828, row 02 y 848–866, row 03 y 890–908, row 04 y 931–949, row 05 y 972–991)।

| সারি | সত্যিকারের শব্দ (চোখে গোনা) | Segmented box | মিল |
|---|---|---|---|
| 01 | 01. / DESCRIPTIONS / - / FOIL / TEMPER / Hard = **৬** | ৬ | ৬/৬ ✅ |
| 02 | 02. / WIDTH / mm / 780.0( / ± / 0.5mm) / 780.0 = **৭** | ৭ | ৭/৭ ✅ |
| 03 | 03. / ALU. / THICKNESS / mm / 0.0230 / – / 0.0270 / 0.0251 = **৮** | ৮ | ৮/৮ ✅ |
| 04 | 04. / ALU. / GRAMMAGE / gms/m² / 62.33 / – / 73.17 / 68.02 = **৮** | ৮ | ৮/৮ ✅ |
| 05 | 05. / HSL / GRAMMAGE / gms/m² / 6.0 / – / 8.0 / 7.52 = **৮** | ৮ | ৮/৮ ✅ |
| **মোট** | **৩৭** | **৩৭** | **৩৭/৩৭ = ১০০% (এই নমুনায়)** |

**এই "১০০%"-এর সৎ সীমা (পড়ুন):**
- নমুনাটি পাতার সবচেয়ে পরিষ্কার অংশ — ছাপা টেবিলের ৫টি সারি। পুরো পাতার ৩০২টি box-এর সবগুলো হাতে গোনা হয়নি; তাই এটা **পুরো পাতার নির্ভুলতা নয়**, নমুনার নির্ভুলতা।
- `-` / `±` / `–` চিহ্নগুলো খুব ছোট sliver box পায় (৭×২ px থেকে ১৫×৩ px) — তবু সঠিক জায়গায়, ক্লিক করা যায়।
- `gms/m²`-এর box-এ superscript `²` ঢুকে যায় (box ২৫–২৬ px উঁচু, সাধারণ ১৯ px-এর বদলে) — এটা সঠিক আচরণ, ভুল নয়।
- **পুরো পাতায় জানা ছোট ভুল (segmentation overlay চোখে দেখে):** `/` আলাদা box হয়ে যায়; `²` superscript কিছু জায়গায় আলাদা ভেঙে যায়; ইমেইল `pgfoils@pgfoils.in` ভেঙে যায় (`pgfoils@pgf` + `oils.in`)। এগুলো ক্লিক-এডিটে বাধা নয় (ব্যবহারকারী দুটি box-ই এডিট করতে পারে), কিন্তু নিখুঁত নয়।
- একটি শিক্ষা: প্রথমবার সারির band ভুল মেপেছিলাম (header-এর y-কে row 01 ভেবে) — তখন মনে হয়েছিল একটি বাড়তি box আছে। Pixel-মাপে দেখা গেল সেটি header-এর আসল শব্দ "TEST" — segmentation ঠিক ছিল, আমার band-ই ভুল ছিল। রিপোর্টে এই ভুল স্বীকার করা হলো।

## ৪. Inpainting-এর মান — চোখে দেখা

- ৩০২টি box মুছে পরিষ্কার background বানানো হয়েছে — টেবিলের লাইন, লোগো, দুটি হাতের স্বাক্ষর অক্ষত আছে।
- **বাকি থাকা artifact (সৎ তালিকা):** UNIT কলামে কয়েকটি `²` superscript হালকাভাবে এখনো দেখা যায়; header-এ ২টি ছোট ডট; "ANALYTICAL TEST REPORT" শিরোনামের highlight যেখানে ছিল সেখানে হালকা ধূসর দাগ।
- Telea-র প্রথম চেষ্টা (threshold <170) সব লেখার ভূত (ghost) রেখে দিয়েছিল; দ্বিতীয় চেষ্টা (threshold <210 + dilate, radius 4) লেখা পরিষ্কারভাবে মুছেছে।
- **সীমা:** inpainted জায়গা "অনুমান", "আসল" নয় — zoom করলে ধরা পড়তে পারে। এটা Live-Scan-এর স্থায়ী সীমা, কোনো inpainting-ই হারানো pixel ফিরিয়ে আনতে পারে না।

## ৫. ডেমো এডিট — যাচাই (প্রমাণসহ)

দুটি এডিট — Playwright probe দিয়ে যাচাই করা (**সংশোধন: নিচের WIDTH সারিটি ২০২৬-১১-০৬-এ ঠিক করা হয়েছে; আগে ভুল শব্দে পড়ত — দেখুন §১২**):

| এডিট | লক্ষ্য শব্দ (segmentation box) | Probe-এ পাওয়া অবস্থান | ফল |
|---|---|---|---|
| Lot No. **206/7 → 207/9** | box (355, 619, 66×25) | offsetTop 310 px → image y 619 ✅ | ✅ সঠিক শব্দে |
| WIDTH Observation **780.0 → 781.5** | box (1391, 854, 60×19) — সারি ০২-র observation | offsetTop 427 px → image y 854 ✅ | ✅ সঠিক শব্দে |

আরও যাচাই — plain vs edited স্ক্রিনশটের pixel-diff (২০২৬-১১-০৬, ঠিক করা পাতায় আবার মাপা): টেক্সট-পরিবর্তনের blob ঠিক ২টি জায়গায় (Lot No.-তে display y 458–472, WIDTH সারি ০২-তে display y 575–590); বাকি diff শুধু toolbar-এর বোতামের অবস্থা। অর্থাৎ এডিট পাতার আর কোথাও কিছু বদলায়নি।
- **Font মিল:** নতুন লেখা Georgia serif bold-এ বসে — সাধারণ পড়ার দূরত্বে মূল ছাপার সঙ্গে প্রায় একরকম দেখায় (zoom করা crop-এ যাচাই করা)। কিন্তু এটা **metric approximation, মূল font নয়** — মূল font-এর নাম স্ক্যান থেকে জানা যায় না। Bold অনুমান (২২৪/৩০২ bold) সম্ভবত over-bold — পরের সংস্করণে threshold ঠিক করতে হবে।
- **নীল সাই-এর লোগো এডিট করা যায় না** — হাতের লেখা/স্বাক্ষর segmentation থেকে বাদ দেওয়া হয়েছে (ইচ্ছাকৃত)।

## ৬. OCR (ঐচ্ছিক স্তর) — যা মাপা হয়েছে, যা হয়নি

- RapidOCR একবার চালানো হয়েছিল পাতা ১-এ (তুলনার জন্য, এডিট-পথে নয়): **১২৩টি লাইন, ~১২ সেকেন্ড** (প্রথম run, মডেল load-সহ)। চোখে দেখা সমস্যা: "ANALYTICALTEST REPORT" (space হারানো), "EMAIL:pgfoils@pgfoils.inWEBSITE:www.pgfoils.in" (দুটি ফিল্ড জোড়া লেগে যাওয়া), "PRODUCT:BLISTERFOIL"।
- **Raw OCR accuracy মাপা হয়নি — এবং দাবিও করা হচ্ছে না।** Live-Scan-এ OCR এডিটের জন্য দরকার নেই বলেই এর নির্ভুলতা headline metric নয়। Recognition স্তরে (রেকর্ড/mass-balance) OCR ব্যবহার করতে হলে আলাদা করে CER/WER মাপতে হবে + Domain-Constrained Verified OCR-এর পাঁচটি স্তম্ভ (RESEARCH.md §৭) লাগবে।
- Tesseract ইনস্টল হয়েছে — **tesseract 5.3.4** (`/usr/bin/tesseract`, leptonica 1.82.0), apt দিয়ে ইনস্টল করা (apt update-এ ~২২ মিনিট লেগেছিল)। Live-Scan-এর এডিট-পথে দরকার নেই; dual-engine agreement-এর spike-এ ব্যবহার করা যাবে।

## ৭. কী ১০০%, কী মাপা, কী নয় — চূড়ান্ত হিসাব

| দাবি | অবস্থা |
|---|---|
| **অন-এডিটেড পিক্সেল ১০০% অপরিবর্তিত** | ✅ **By construction** — মূল স্ক্যানই background layer; এডিট শুধু overlay-তে। *(সৎ caveat: HTML পাতায় background JPEG quality 88-এ re-encode করা হয়েছে — চোখে একরকম, byte-এ নয়। প্রোডাকশনে মূল image bytes বা lossless PNG রাখতে হবে।)* |
| **এডিট করা মান ১০০% ব্যবহারকারীর টাইপ করা মান** | ✅ **By construction** — typed text সরাসরি বসে, OCR জড়িত নয়। Probe দিয়ে যাচাই করা (§৫)। |
| **Segmentation নির্ভুলতা** | 📏 **মাপা: ৩৭/৩৭ (১০০%) — ৫ সারির নমুনায়।** পুরো পাতায় মাপা হয়নি; জানা ছোট ভুল আছে (§৩)। |
| **Inpainting মান** | 👁️ **চোখে যাচাই** — পরিষ্কার, টেবিল/লোগো/স্বাক্ষর অক্ষত; ৩টি ছোট artifact বাকি (§৪)। |
| **Font মিল** | ⚠️ **Approximation** — কাছাকাছি দেখায়, হুবহু নয়; bold over-estimate আছে। |
| **Raw OCR accuracy** | ❌ **দাবি করা হয় না** — মাপা হয়নি, এডিট-পথে দরকারও নেই। |
| **Print ১০০% calibration** | ❌ **এখনো হয়নি** — কাগজে ছাপিয়ে মাপা বাকি (live-paper-এর মতোই)। |

## ৮. স্ক্রিনশট (প্রমাণ)

| ফাইল | কী দেখায় |
|---|---|
| `shots-page-plain.png` | মূল স্ক্যান পাতা, কোনো এডিট ছাড়া — toolbar সহ |
| `shots-page-edited.png` | ডেমো এডিট-সহ পাতা (`?demo=1&boxes=1`) — Lot 207/9, WIDTH 781.5, word-box outline দেখা যায় |
| `shots-clip-rows.png` | টেবিলের সারি ০১–০৫, ২× zoom — এডিট করা "781.5" WIDTH-র সারিতে, মূল "780.0" অক্ষত আছে পাশের সারিতে |
| `shots-crop-table.png` | টেবিলের crop (পুরনো — যাচাইয়ের সময় ভুল row-পড়া হয়েছিল; সঠিক যাচাই `shots-clip-rows.png` + probe-এ) |

## ৯. Production-ready হতে যা বাকি

1. **DBNet mobile det-only ONNX** দিয়ে segmentation — classical পদ্ধতির বদলে/পাশাপাশি; i5-8265U-তে সময় মাপা (RESEARCH.md §৩)।
2. **Ink-only mask** (Otsu) — এখন পুরো box-এর ভেতরের dark pixel mask করা হয়; শুধু কালির pixel mask করলে টেবিলের লাইন আরও নিরাপদ থাকবে।
3. **LaMa ONNX** — textured/coloured background-এর জন্য; **আগে Places2 licence যাচাই** (commercial blocker)।
4. **Font shortlist UI** — ব্যবহারকারী ৩–৪টি কাছাকাছি font-এর live preview দেখে বেছে নেবে; bold threshold ঠিক করা।
5. **Multi-page** — এখন শুধু পাতা ১; ৮ পাতার PG COA + ৬ পাতার May COA (B&W CCITT) — May-র B&W স্ক্যানে আলাদা করে পরীক্ষা করতে হবে। → **পরীক্ষা সম্পন্ন ২০২৬-১১-০৬: `REPORT-MAY.md` দেখুন — মে পাতা ১-এ মূল টেবিল এডিট প্রমাণিত (Lot 304/5 → 305/7, WIDTH 670.0 → 671.5), কিন্তু ২টি বাগ ধরা পড়েছে: (১) শিরোনাম একা বড় component হয়ে singleton-line ফিল্টারে বাদ পড়ে, clean পাতায় ভূত রয়ে যায়; (২) hardcoded SIGROW y=2000 নিচের নোটের লাইন কেটে দেয়। নমুনায় ৩৩/৩৭ box, পুরো পাতায় ~৯৩% word coverage।**
6. **Skew/deskew + low-resolution handling** — বাঁকা/ফিকে স্ক্যানে box-এর confidence দেখানো।
7. **Save/export + audit trail** — এডিট শুধু overlay layer-এ, মূল স্ক্যান immutable; প্রতিটি এডিটের version + "edited" চিহ্ন; print/PDF-এ flatten।
8. **Recognition স্তর (ঐচ্ছিক)** — RapidOCR + Tesseract dual-engine, closed vocabulary, template-aware check, 3-Second Confirm, learning loop — শুধু automation-এর জন্য।
9. **Print calibration কাগজে** — ১০০% scale ছাপিয়ে মাপা।
10. **Hard-case নীতি** — হাতের লেখা/স্ট্যাম্প/সম্পূর্ণ ঢাকা লেখা: "do-not-edit / flag" হিসেবে দেখানো, "শীঘ্রই ঠিক হবে" বলে লুকানো নয়।

## ১০. ফাইল তালিকা (`scan-paper/`)

- `live-scan-page.html` — প্রোটোটাইপ পাতা (খুলে ক্লিক করে এডিট করা যায়; `?demo=1` ডেমো এডিট, `?boxes=1` word-box দেখায়)
- `segment.py`, `seg-aug-p1.json` — segmentation স্ক্রিপ্ট + ৩০২টি word box
- `inpaint.py`, `pages/aug-p1-clean.png` — inpainting স্ক্রিপ্ট + পরিষ্কার background
- `ocr_rapid.py`, `ocr-aug-p1-rapid.json` — ঐচ্ছিক recognition তুলনা (১২৩ লাইন)
- `build_page.py`, `patch_demo.py` — পাতা বানানো + ডেমো
- `shoot.py`, `probe.py`, `probe2.py`, `shoot_clip.py` — স্ক্রিনশট ও যাচাই স্ক্রিপ্ট
- `shots-*.png` — স্ক্রিনশট (§৮)
- `pages/aug-p1-1.png`, `pages/may-p1-1.png` — 200 DPI পাতার ছবি
- `RESEARCH.md`, `REPORT.md` — এই দুটি রিপোর্ট
- `research-*.md` — চারটি ট্র্যাক-রিপোর্ট (মূল)
- `venv/` — Python পরিবেশ (rapidocr-onnxruntime, opencv-python-headless 5.0.0, playwright + Chromium Headless Shell)

---

## ১১. ডাবলিং বাগ — ব্যবহারকারী নিজে ধরেছেন, ঠিক করা হয়েছে (২০২৬-১১-০৬)

**ব্যবহারকারীর অভিযোগ (তাঁর ভাষায়):** একটি text change করে দেখলাম — change হচ্ছে, কিন্তু ওই জায়গায় doubling একটা layer পড়ে যায়; edit করা text পড়তে কষ্ট হয়, আর যে কেউ বুঝে যাবে এখানে একটা issue আছে, মানে কাজ করা হয়েছে।

**Reproduce করা হয়েছে (repro.py + Playwright):** Lot No.-তে `207/9` টাইপ করে অন্য শব্দে ক্লিক করতেই Lot-র span-এর class `wd` (clean background `none`) হয়ে গেল — আসল `206/7` স্ক্যান-ব্যাকগ্রাউন্ড থেকে আবার ভেসে উঠে টাইপ করা `207/9`-এর নিচে জমে গেল। স্ক্রিনশটে চোখে দেখা গেছে: `206/9` — পড়া যায় না এমন জট।

**মূল কারণ (root cause):** clean (inpainted) background শুধু `.on` class-এ বাঁধা ছিল — অর্থাৎ শুধু *চালু* (active) শব্দের নিচেই আসল লেখা ঢাকা থাকত। `activate()` অন্য শব্দে ক্লিক করলেই আগের span থেকে `.on` খুলে নিত, ফলে এডিট করা span-এর clean ঢাকনাও চলে যেত, আর আসল শব্দ টাইপ করা লেখার নিচে ফুটে উঠত। ডেমো বোতামেও একই দোষ ছিল — দ্বিতীয় এডিট চালালেই প্রথম এডিটের ঢাকনা খুলে যেত।

**ঠিক করা হয়েছে (build_page.py + build_page_may.py, v2):**
- নতুন class `.done` — এডিট করা span একবার `.done` পেলে clean background চিরতরে থাকে; `.on` শুধু focus-রিং (নীল বর্ডার) দেয়।
- `activate()`-এ: অন্য span বন্ধ করার সময় তার `textContent` খালি না থাকলে (আসলেই কিছু টাইপ করা হয়েছে) `.done` যোগ করা হয়। শুধু ক্লিক করে কিছু না লিখে সরে গেলে `.done` দেওয়া হয় না — আসল শব্দ আবার দেখা যায় (এডিট বাতিল = আসল ফেরত)।
- দুটি পাতাই আবার বানানো হয়েছে + auto-demo patch আবার লাগানো হয়েছে।

**আবার যাচাই (repro.py + probe.py):** এডিট → অন্য শব্দে ক্লিক → Lot span এখন `wd done`, backgroundImage clean URL সহ; clip স্ক্রিনশটে চোখে দেখা — **Lot No. এখন পরিষ্কার `207/9`, কোনো doubling নেই**। ডেমো পথেও (`?demo=1`) দুটি এডিট ঠিক জায়গায় পড়ে।

**শিক্ষা:** এডিটের "done" অবস্থা আর "active" অবস্থা এক নয় — prototype-এ এই দুটো গুলিয়ে ফেলা হয়েছিল। Production-এ প্রতিটি এডিটের অবস্থা (draft / done / issued) আলাদা করে রাখতে হবে।

---

## ১২. সংশোধন (২০২৬-১১-০৬): ডেমো WIDTH এডিট ভুল শব্দে পড়ছিল — ঠিক করা হয়েছে

**কী ভুল ছিল:** §৫-এর দাবি "WIDTH Observation 780.0 → 781.5 সঠিক শব্দে পড়েছে" **ভুল ছিল**। আসলে এডিটটি পড়ছিল **০১ নম্বর সারির "Hard" শব্দের ওপর** (FOIL TEMPER-এর মান, box [1396, 813, 1447, 832]) — WIDTH observation "780.0" (box [1391, 854, 1451, 873], সারি ০২) অক্ষত ছিল। চোখে দেখা প্রমাণ: পুরনো `shots-clip-rows.png`-এ ০১ নম্বর সারির OBSERVATIONS ঘরে "781.5" বসে আছে, আর WIDTH সারিতে আসল "780.0"।

**কেন ধরা পড়েনি:** `build_page.py`-তে ডেমো লক্ষ্য ছিল `wid = nearest(1420, 822)` — cy=822 হলো সারি ০১-র band (৮০০–৮৩৫), সারি ০২-র (৮৪৮–৮৭৫) নয়। probe শুধু যাচাই করেছিল span-এর **অবস্থান** বাক্সের সঙ্গে মেলে কি না — বাক্সটিতে আসলে **কোন শব্দ** আছে, তা কখনো যাচাই করা হয়নি। বিরোধটি একই ডকুমেন্টে ছিল: §৩-এর নিজের টেবিলেই সারি ০১-র শেষ শব্দ "Hard" বলে লেখা আছে। Lot এডিট (206/7 → 207/9) ঠিক ছিল; May পাতার WIDTH ডেমোও ঠিক ছিল (সঠিক সারি)।

**কে ধরেছে:** Document DNA স্পাইক (improve/ — ২০২৬-১১-০৬)। একই স্পাইকে আরও একটি ত্রুটি ধরা পড়ে — অগাস্টের শিরোনাম "ANALYTICAL TEST REPORT" পরিষ্কারভাবে ভাগ হয়নি: একটি বড় merged বাক্স [680, 410, 979, 439] দুটি আংশিক বাক্সের সঙ্গে overlap করে ছিল, আর REPORT-এর বাক্স "R" ছাড়াই শুরু হতো (মে-র বাগ ১-এরই অগাস্ট-রূপ; v2 rescue শুধু singleton লাইনে চলত, অগাস্টের শিরোনাম লাইনে ৩টি item থাকায় rescue চলেনি)।

**ঠিক করা হয়েছে (segment.py v3 + build_page.py):**
- `segment.py` v3: (ক) merged-word-box split — খুব চওড়া (w ≥ 6×med_h) কিন্তু component-সংখ্যা কম (w/n_comp ≥ 3×med_h) এমন word box-কে `split_blob_words` দিয়ে আবার ভাগ করা হয়; ভাগ সফল হলে বাক্সের ভেতরের fragment-শব্দগুলো ফেলে দেওয়া হয়। (খ) `split_blob_words`-এর gap threshold এখন data-driven (median gap-এর ২×, ন্যূনতম ৩ px) — আগে fixed 0.15×med_h অগাস্টের শিরোনামকে ১০টি অক্ষর-খণ্ডে ভেঙে ফেলেছিল; May-র ক্ষেত্রে (letter gap ০–১ px, word gap ৩–৫ px) ও Aug-র ক্ষেত্রে (letter gap ৩–৪ px, word gap ৮–১২ px) দুটোতেই এখন ঠিক ভাগ হয়।
- অগাস্ট শিরোনাম এখন ৩টি পরিষ্কার বাক্স: ANALYTICAL [680, 411, 821, 430], TEST [827, 412, 881, 431], REPORT [889, 413, 979, 431] (R-সহ)। শব্দ-সংখ্যা অপরিবর্তিত (Aug ২৯৩, May ২৭৯ — May-তে কোনো diff নেই)।
- ডেমো লক্ষ্য: `nearest(1420, 822)` → `nearest(1420, 863)` (আসল WIDTH observation-এর কেন্দ্র cy=863.5)।
- পাতা আবার বানানো হয়েছে (v3 font fix অক্ষত), inpaint আবার চালানো হয়েছে, `fontfix-measure.json` আবার মাপা হয়েছে।

**আবার যাচাই (identity probe — এবার শব্দের পরিচয়সহ):** Lot "207/9" box [355, 619, 421, 644] ✅, WIDTH "781.5" box [1391, 854, 1451, 873] ✅ — সারি ০২-র পূর্ণ লাইন (02., WIDTH, mm, 780.0, ±, 0.5mm, 780.0→781.5) মিলিয়ে দেখা হয়েছে। চোখে যাচাই (`improve/fix-rows01-05-clip.png`): সারি ০১-এ "Hard" অক্ষত, সারি ০২-এ "781.5"। pixel-diff (আবার মাপা): ঠিক ২টি blob — Lot (display y 458–472) ও WIDTH সারি ০২ (display y 575–590)। `repro.py` ✅ (doubling নেই), `fontfix-verify.py` **৩১/৩৫ PASS** — বাকি ৪টি fail শুধু May-র জানা stroke-সীমা (§১১-র আগের ৩০/৩৫ থেকে ১টি বেড়েছে, কারণ ভুল লক্ষ্যের stale assertion ঠিক করা হয়েছে)।

**পার্শ্ব-প্রভাব (font-fix সংখ্যায়):** Aug WIDTH observation-এর আসল stroke অনুপাত **0.134** (আগের রিপোর্টে লেখা 0.143 ছিল "Hard" বাক্সের মান) — regular সিদ্ধান্ত অপরিবর্তিত, margin আরও বড় (0.134 < 0.148)। রং `#5e515a` → আসল `#5f525c`। Aug শিরোনাম এখন ৩টি শব্দই bold (আগে ২/৩) — মোট bold ৬৩/২৯৩।

**শিক্ষা:** অবস্থান মেলানোই যাচাই নয় — **শব্দের পরিচয়** যাচাই করতে হবে (কোন সারি, কোন লেবেলের পাশে)। এরপর থেকে প্রতিটি demo/probe দাবিতে সারির লেবেলসহ পরিচয় লেখা বাধ্যতামূলক।
