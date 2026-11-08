# Live-Scan — গবেষণা সংশ্লেষ (Research Synthesis)

> **নতুন প্রযুক্তির নাম: Live-Scan (লাইভ-স্ক্যান)** — স্ক্যান-ই-পাতা, OCR-মুক্ত এডিট।
> চারটি গবেষণা ট্র্যাকের সংশ্লেষ + প্রোটোটাইপ থেকে পাওয়া প্রমাণ। প্রতিটি দাবির পাশে **[VERIFIED]** (নিজে repo README / অফিসিয়াল ডক / পেপারে দেখা) বা **[UNVERIFIED]** (দ্বিতীয় হাতের উৎস / স্নিপেট / নিজের বিচার)। কোনো ভার্সন, দাম বা নির্ভুলতার শতাংশ বানানো হয়নি।
> বিস্তারিত চারটি ট্র্যাক-রিপোর্ট: `research-livescan.md`, `research-ocr.md`, `research-inpaint.md`, `research-products.md` (একই ফোল্ডারে)।

---

## ১. প্যারাডাইম-ভাঙন — OCR কী করে, Live-Scan কী করে

| | OCR (আজকের প্রযুক্তি) | Live-Scan (নতুন প্রযুক্তি) |
|---|---|---|
| প্রথম ধাপ | পড়ে — অক্ষর চেনে | **পড়ে না** — শুধু শব্দের জায়গা খুঁজে পায় |
| এডিট | পড়া শেষ হলে, পড়া-টেক্সট বদলায় | **এডিটই প্রথম** — ক্লিক → আগের লেখা মুছে যায় → নতুন লেখা টাইপ |
| পড়া (recognition) | বাধ্যতামূলক, এডিটের আগে | **ঐচ্ছিক, আলাদা ধাপ** — শুধু automation-এর জন্য (রেকর্ড, mass-balance) |
| মূল স্ক্যান | ফেলে দিয়ে OCR-পুনর্গঠিত পেজ বানায় | **পাতাই থাকে** — background layer হিসেবে অপরিবর্তিত |

**কেন এটা সত্যিকারের ভাঙন:** Detection আর recognition যে আলাদা দুটি ধাপ, এটা প্রতিষ্ঠিত সত্য। **[VERIFIED — OnnxTR / PaddleOCR ডক: detection মডেল শুধু text region-এর bounding box দেয়, recognition আলাদা ধাপে অক্ষর পড়ে; PaddleOCR-এর তিন ধাপ: detection → orientation → recognition, প্রতিটি আলাদা ONNX ফাইল।]** অর্থাৎ "পড়া ছাড়া শব্দের জায়গা খোঁজা" কল্পনা নয় — OCR pipeline-এর প্রথম ধাপটাই তাই। Live-Scan-এর উদ্ভাবন: **সেই প্রথম ধাপেই থেমে গিয়ে, recognition-কে এডিট-পথ থেকে সম্পূর্ণ বাইরে রাখা।**

**"কেউ এটা বানায়নি" — কতটা সত্যি:** ক্লিক করে স্ক্যানের ওপরের শব্দ সরাসরি retype করা যায় — এমন OCR-মুক্ত, offline, open-source প্রোডাক্ট গবেষণায় খুঁজে পাওয়া যায়নি। **[UNVERIFIED — অনুসন্ধানে না পাওয়া; প্রমাণের অনুপস্থিতি, অস্তিত্বহীনতার প্রমাণ নয়।]** কাছাকাছি যা আছে সবই OCR-first (§৫ দেখুন)। উপাদানগুলো আছে, কিন্তু এইভাবে জোড়া দেওয়া প্রোডাক্ট নেই — এই অর্থে দাবিটা টেকে।

---

## ২. OCR-মুক্ত ডকুমেন্ট মডেল — Donut, Nougat, Vary (এডিট-পথে নয়)

সাধারণ ভুলটা প্রথমে: **এই মডেলগুলো "OCR ছাড়া পড়ে" — কিন্তু "পড়া ছাড়া শব্দের অবস্থান দেয়" না।** এডিট-পথে এদের জায়গা নেই; শুধু ঐচ্ছিক recognition ধাপে কাজে লাগতে পারে।

| মডেল | কী দেয় | word box দেয়? | বাণিজ্যিক licence | i5-8265U / 8GB-তে উপযোগী? |
|---|---|---|---|---|
| **Donut** (NAVER Clova) | ছবি থেকে structured JSON — receipt, form, DocVQA **[VERIFIED — README]** | না — শুধু text sequence / JSON **[UNVERIFIED — স্বাধীন evaluation রিপোর্ট; README-তে box-output-এর উল্লেখ পাওয়া যায়নি]** | কোড MIT **[VERIFIED]** | অজানা — মাপতে হবে; GPU-তে ০.৬–০.৭৮ সেকেন্ড/ছবি (হার্ডওয়্যার অনুল্লেখিত) |
| **Nougat** (Meta AI) | academic PDF → LaTeX-aware Markdown **[VERIFIED — README]** | না — শুধু `.mmd` text **[UNVERIFIED]** | **কোড MIT, কিন্তু model weights CC-BY-NC — বাণিজ্যিক নয় [VERIFIED — README]** | না — শুধু academic, FAQ-তে arXiv/PMC-এর বাইরে সন্দেহজনক **[VERIFIED]** |
| **Vary** (MEGVII) | dense document/chart বোঝা, OCR/markdown **[VERIFIED — পেপার/ README]** | না | **গবেষণা-মাত্র [VERIFIED — README]** | না — 7B শ্রেণি |
| **UReader** | MLLM-ভিত্তিক OCR-free understanding **[VERIFIED — arXiv 2310.05126]** | না | যাচাই হয়নি | না — MLLM, ভারী |
| **GOT-OCR2.0** | box দিলে সেই box-এর ভেতরটা পড়ে (উল্টো দিক) **[VERIFIED — arXiv 2409.01704]** | না — box ইনপুট নেয় | সাংঘর্ষিক (HF ট্যাগ apache-2.0, README-তে "research use only") **[VERIFIED]** | সন্দেহজনক — 580M |

**সিদ্ধান্ত:** Donut/Nougat/Vary দিয়ে প্রথম build শুরু করা ভুল। Nougat/Vary বাণিজ্যিকভাবে ব্যবহার করা যাবে না (licence)। এরা শুধু পরের ধাপের recognition-প্রার্থী।

---

## ৩. শব্দের জায়গা খোঁজা — recognition ছাড়া segmentation

তিনটি স্তর; সঠিক ডিজাইন এদের সংমিশ্রণ:

### স্তর ১ — Classical: connected components + projection profile
পাতা binarize → dark pixel-এর connected component → একই লাইনের component group → লাইনের ভেতরে vertical projection profile (ফাঁকার histogram) দিয়ে শব্দ আলাদা। **[VERIFIED — UW-ISL Document Image Analysis Toolbox; CEDAR historical document পেপার।]** কোনো মডেল/GPU/training লাগে না; OpenCV-তে CPU-তে মিলিসেকেন্ডে চলে; সম্পূর্ণ offline। **সীমা:** হাতের লেখা, বাঁকা লাইন, স্পর্শ করা অক্ষর, স্ট্যাম্পে ভেঙে যায়। **[VERIFIED — CEDAR পেপার: classical method মূলত machine-printed document-এর জন্য।]**
👉 **প্রোটোটাইপে এটাই ব্যবহার করা হয়েছে** — PG COA পাতা ১-এ ৩০২টি শব্দ, ৪৪টি লাইন (segment.py, OpenCV connected components, কোনো ML/OCR নেই)। মাপা নির্ভুলতা REPORT.md-তে।

### স্তর ২ — Detection-only neural: DBNet (সেরা প্রথম পছন্দ)
DBNet ছবি থেকে probability map বের করে text region-এর polygon/box বানায় — অক্ষর কী, তা একবারও বলে না। **[VERIFIED — OnnxTR ডক।]** PP-OCRv5 mobile detection ONNX **~৪.৬ MB, Apache-2.0 [VERIFIED]**। Detection-only চালানো যায় (`DetectAsync` — শুধু detection, recognition ছাড়া) **[VERIFIED — LocalAI.Ocr ডক]** — এটাই প্রমাণ যে detection-কে recognition থেকে আলাদা করে চালানো যায়। **সীমা:** DBNet সাধারণত line-level/region polygon দেয়, পরিষ্কার word-level box সবসময় নয় **[UNVERIFIED — বিচার]** — তাই box-এর ভেতরে আবার projection-profile দিয়ে word-split করতে হবে। CPU-গতি i5-তে মাপা হয়নি — spike-এ মাপতে হবে।

### স্তর ২-বিকল্প — CRAFT ও EAST
- **CRAFT:** character region + affinity heatmap → connected component দিয়ে word box। **[VERIFIED — বর্ণনা।]** ধারণাগতভাবে word-level-এর জন্য DBNet-এর চেয়ে ভালো, কিন্তু VGG16-ভিত্তিক, ভারী; licence যাচাই হয়নি **[UNVERIFIED]**।
- **EAST:** OpenCV-তে `cv2.dnn_TextDetectionModel_EAST` আছে; দ্রুত, rotated box দেয়। **[VERIFIED — OpenCV ডক।]** পুরনো (২০১৭), ঘন document text-এ DBNet-এর চেয়ে দুর্বল বলে গাইডে বলা আছে **[UNVERIFIED]**। Fallback হিসেবে রাখা যায়।

### স্তর ৩ — Layout detection (শব্দের জন্য নয়, অঞ্চলের জন্য)
**Docling Heron:** RT-DETRv2, ৪২.৯M parameter, ১৭টি class (title, paragraph, table, figure…), code MIT, weights **Apache-2.0 [VERIFIED]**। ভূমিকা: DBNet-কে বলা "এটা টেবিল, এখানে সাবধানে word-split করো" বা "এটা seal/picture, এখানে এডিট নয়"। প্রথম build-এ **ঐচ্ছিক**। **এড়িয়ে চলবেন:** DocLayout-YOLO (**AGPL-3.0** — বাণিজ্যিক সমস্যা) **[VERIFIED]**, Surya (weights OpenRAIL-M, ~$5M revenue cap) **[VERIFIED — HF model card]**, LayoutLMv3 (CC BY-NC) **[VERIFIED]**।

### সুপারিশ — Build ক্রম
1. **DBNet mobile det-only ONNX (Apache-2.0, ~৫ MB)** দিয়ে line/region box।
2. প্রতিটি line-box-এর ভেতরে **projection profile + gap threshold** দিয়ে word-split।
3. যেখানে DBNet ব্যর্থ, সেখানে **classical connected-components** fallback।
4. পরে: **CRAFT** দিয়ে word-boundary যাচাই, **Docling Heron** দিয়ে layout zone।
5. প্রতিটি শব্দে সংরক্ষণ করবেন: box (x, y, w, h, angle), baseline, উচ্চতা, গড় রং, stroke width — **অক্ষর কী, তা নয়।**

---

## ৪. পুরনো শব্দ মোছা + নতুন শব্দ বসানো

### Inpainting — তিন স্তর (একটি নয়)
| পদ্ধতি | ভালো দিক | খারাপ দিক | Licence | Offline i5-তে |
|---|---|---|---|---|
| Background-colour cover | দ্রুততম, predictable | line/texture/stamp-এ patch চোখে পড়ে | কোনো model নেই | হ্যাঁ |
| **OpenCV Telea / NS** | ছোট mask-এ ভালো, no model | বড় hole-এ blur, line পুনর্গঠন পারে না | **Apache 2.0 (4.5+) [VERIFIED]** | হ্যাঁ, সময় not verified |
| **LaMa / Big-LaMa** | বড় mask/texture-এ ভালো | blur/hallucination, **Places2 licence প্রশ্ন**, ভারী | Code Apache 2.0 **[VERIFIED]**, weights যাচাই বাকি | CPU-তে চলে **[VERIFIED]**, PG পাতায় সময় not verified |
| Diffusion (SDXL) | সবচেয়ে "কল্পনাশক্তি" | ভারী, GPU চায়, hallucination বেশি, audit-এর জন্য অনুপযুক্ত | মডেলভেদে ভিন্ন | recommend নয় |

- **LaMa:** repo `advimman/lama`, WACV 2022; 256×256-এর চেয়ে অনেক বেশি resolution (~2k)-এও generalize করে **[VERIFIED — README]**; CPU mode repo-র নিজের নির্দেশেই আছে **[VERIFIED]**। ⚠️ **Blocker:** একটি third-party notice-এ লেখা weights Places2 dataset-এ train করা, যার terms "non-commercial research and educational purposes only" — **not verified, আইনি যাচাই ছাড়া commercial bundle করা যাবে না।**
- **সবচেয়ে গুরুত্বপূর্ণ কৌশল — ink-only mask:** পুরো bounding box ভরে দিলে টেবিলের লাইন, signature-এর underline, সিলের কিনারা মুছে যায়। সঠিক পদ্ধতি: box-এর ভেতরে Otsu threshold দিয়ে শুধু **কালির pixel** mask করা, সামান্য dilate করা, তারপর inpaint করা। **[VERIFIED — dev.to-তে scanned-PDF translation নিবন্ধ: "The obvious mask is the OCR bounding box, filled solid. Don't do this… What works better is masking only the ink."]** এটা Live-Scan-এর জন্য অপরিহার্য — না হলে "১০০% same-to-same" নষ্ট হবে।
- **সাদা কাগজে LaMa লাগে না:** OpenCV inpaint (Telea/NS) বা সরল background-colour fill-ই যথেষ্ট **[UNVERIFIED — বিচার]**। ডিজাইন: **typing-এর সময় live preview হবে overlay text দিয়ে (inpaint ছাড়া), inpaint হবে save/commit-এর সময়** — এটাই real-time অনুভূতি দেবে।
- 👉 **প্রোটোটাইপে Telea ব্যবহার করা হয়েছে** (threshold <210 + 3×3 dilate একবার, radius 4) — ফল REPORT.md-তে। LaMa এখনো চালানো হয়নি।

### Font matching — হুবহু font চেনা যাবে না, কাছাকাছি মেলানো যাবে
- **সত্যিটা:** স্ক্যান থেকে font-এর নাম নিশ্চিতভাবে বের করা যায় না। fontident (PyPI) glyph-কে local font catalog-এর সঙ্গে render-compare করে — "approximate" বলে নিজেই স্বীকার করে। **[VERIFIED — pypi.org/project/fontident।]**
- Tesseract নির্ভরযোগ্যভাবে font information দেয় না। **[VERIFIED — HackerNoon screenshot-editor article।]** তাই font matching OCR-এর কাজ নয়; আলাদা estimation-এর কাজ।
- **বাস্তব পদ্ধতি:** font-এর নাম না খুঁজে **পরিমাপ** করুন — box-এর উচ্চতা থেকে point size (তারপর candidate font-এ render করে width-fit দিয়ে fine-tune), baseline থেকে অবস্থান, গড় রং থেকে ink colour, stroke width থেকে bold/regular। তারপর metric-compatible font (Arial, Times New Roman, Courier) দিয়ে render করুন; ব্যবহারকারীকে ৩–৪টি কাছাকাছি font-এর live preview দেখিয়ে বেছে নিতে দিন। COA-তে font সাধারণত ২–৩টির বেশি হয় না। **[UNVERIFIED — ডিজাইন প্রস্তাব।]**
- **সীমা:** typewriter/inkjet font-এর uneven ink clean vector font দিয়ে মেলানো যাবে না; handwriting-কে কোনো standard font মেলাতে পারে না (image হিসেবেই রাখতে হবে, অথবা "typed approximation" বলে জানাতে হবে); stamp-এর ওপর দিয়ে যাওয়া text-এর mask stamp-এর অংশও মুছে ফেলবে; underline-কে আলাদা line element হিসেবে চিহ্নিত করে নতুন text-এর নিচে আবার আঁকতে হবে। **[UNVERIFIED — বিচার; Carlito-vs-Calibri সমস্যাটি GRAVORA-র live-paper কাজে আগেই দেখা গেছে।]**
- 👉 **প্রোটোটাইপে:** font Georgia serif (metric approximation, মূল font নয়), size = box height থেকে, bold = ink density থেকে অনুমান (২২৪/৩০২ bold — সম্ভবত over-bold; REPORT.md দেখুন)।

---

## ৫. বিদ্যমান প্রোডাক্টগুলো আসলে কী করে

| প্রোডাক্ট | স্ক্যানের ভেতরে টেক্সট এডিট? | এডিটের পর ব্যাকগ্রাউন্ড / ফরম্যাট | মূল সীমা |
|---|---|---|---|
| **Adobe Acrobat** | হ্যাঁ — OCR-এর পর | মূল স্ক্যান-পিক্সেল থাকে না; OCR দিয়ে পুনর্গঠিত পেজ | টেবিল/গ্রাফ/ছবি এডিট করতে Adobe-ই বারণ করে; OCR ভুল থাকলে ভুলই এডিট হয় **[VERIFIED — Adobe Help]** |
| **ABBYY FineReader** | হ্যাঁ — OCR-এর পর | **ট্রেড-অফ বাধ্যতামূলক:** Exact copy = ফরম্যাট মেলে, এডিট প্রায় যায় না; Editable copy = এডিট যায়, ফরম্যাট সামান্য বদলায় | এই ট্রেড-অফটাই প্রমাণ করে — দুটো একসাথে ১০০% হয় না **[VERIFIED — ABBYY Help]** |
| **Microsoft Lens** | না — Word-এ export করে এডিট | মূল ফরম্যাট হারিয়ে Word-এ পুনর্গঠিত | **অ্যাপটি retired — ২০২৬-এ নতুন স্ক্যান বন্ধ [UNVERIFIED — অফিসিয়াল পাতা খোলা হয়নি]** |
| **Google Drive OCR** | না — নতুন Google Doc-এ টেক্সট | ফরম্যাট প্রায় পুরো হারায়; **টেবিল/কলাম ধরা পড়ে না** | ফাইল ≤২ MB; টেবিলওয়ালা COA-র জন্য অচল **[VERIFIED — Google Drive Help]** |
| **Apple Live Text** | না — শুধু select / copy | কোনো ফরম্যাটই থাকে না; plain text copy | এটা PDF এডিটরই নয় **[VERIFIED — Apple Support]** |
| **OCRmyPDF + Tesseract** | না — শুধু invisible searchable text layer | **মূল স্ক্যান চেহারা ১০০% অপরিবর্তিত** — কিন্তু এডিট করা যায় না | হাতের লেখা চেনে না; ফন্টের তথ্য দেয় না **[VERIFIED — অফিসিয়াল ডক]** |
| **LightPDF / Pixazo / Revise / Filedone** | হ্যাঁ — OCR + inpaint + replace | ব্যাকগ্রাউন্ড মোটামুটি থাকে | **সবই OCR-first, বেশিরভাগ cloud-ভিত্তিক** — "OCR দিয়ে text detect করে, তারপর মুছে, তারপর নতুন শব্দ বসায়" **[VERIFIED — নিজেদের পাতা]** |
| **DiffSTE / STEPS / STELLAR (গবেষণা)** | গবেষণা-পর্যায়ে হ্যাঁ — ছবির শব্দ mask করে inpaint করে নতুন শব্দ বসায় | ব্যাকগ্রাউন্ড মোটামুটি থাকে, কিন্তু টেক্সটের সঠিকতা ও স্টাইলে ভুল হয় | কোনো শিপ করা ডকুমেন্ট-প্রোডাক্ট নয় **[VERIFIED — arXiv abstract]** |

**সবচেয়ে কাছের দুটি** — Acrobat ও FineReader — স্ক্যানের ভেতরে এডিট দেয়, কিন্তু মূল পিক্সেল ফেলে দিয়ে OCR-পুনর্গঠিত পেজ বানায়; ABBYY নিজেই স্বীকার করে exact ফরম্যাট আর এডিট একসাথে হয় না। **OCRmyPDF** উল্টো প্রান্তে — মূল পিক্সেল ১০০% রাখে, কিন্তু এডিট দেয়ই না। **GRAVORA-র প্রস্তাব — মূল স্ক্যান-পিক্সেল ব্যাকগ্রাউন্ড হিসেবে রাখা + word-box + মূল শব্দ মুছে matching ফন্টে editable span — এই সংমিশ্রণটি কোনো শিপ করা প্রোডাক্টে পাওয়া যায়নি। [UNVERIFIED — "পাওয়া যায়নি" মানে "নেই" তার প্রমাণ নয়।]**

Adobe-ও exact font matching-এর দাবি করে না — "closest match" বলে। **[VERIFIED — Adobe Help: "Use available system font" — closest match।]** GRAVORA-কেও একই সততা রাখতে হবে।

---

## ৬. "১০০% নির্ভুল" — সৎ ভাঙন (পাঁচটি আলাদা দাবি)

একটিমাত্র "১০০%" বলে কিছু নেই। পাঁচটি আলাদা জিনিস:

1. **Background / Format Fidelity — ✅ গঠনগতভাবে (by construction) ১০০% সম্ভব, কিন্তু শুধু অন-এডিটেড অংশে।** মূল স্ক্যান-পিক্সেল ব্যাকগ্রাউন্ড layer হিসেবে অপরিবর্তিত থাকলে, যে অংশে হাত দেওয়া হয়নি, সেটা সংজ্ঞা অনুযায়ীই ১০০%। মাপার উপায়: অপরিবর্তিত অংশে pixel-diff = 0 / SSIM = 1.0। কিন্তু যেই শব্দটি এডিট করা হলো, সেই জায়গার মূল পিক্সেল আর থাকে না — **এডিট করা অংশে background fidelity কখনোই ১০০% original হতে পারে না** — সর্বোচ্চ "চোখে ধরা পড়ে না" হতে পারে।
2. **OCR Recognition Accuracy — ❌ কখনোই ১০০% গ্যারান্টি দেওয়া যায় না; শুধু মাপা যায়।** OCR একটি অনুমান, certified transcription নয়। মাপার উপায়: ground truth-এর সঙ্গে তুলনা করে CER / WER। প্রতিটি COA-র জন্য আলাদা মাপতে হবে — কোনো universal % নেই।
3. **Word-Position Accuracy — ⚠️ সহনশীলতা (tolerance) ঠিক করলে ১০০%-এর কাছাকাছি মাপা যায়, pixel-perfect নয়।** OCR-র bounding box একটি অনুমান — skew, ঘন লেখা, ছোট ফন্টে box সরে যায়। মাপার উপায়: ground-truth box-এর সঙ্গে IoU বা centre দূরত্ব; যেমন "৩০০ DPI-তে ±২ pixel-এর মধ্যে থাকলে pass" — এই tolerance GRAVORA-কে নিজে ঠিক করতে হবে।
4. **Font-Look Accuracy — ❌ সাধারণভাবে কখনোই ১০০% নয়।** স্ক্যান করা ফন্ট raster পিক্সেল — মূল ফন্ট ফাইলের নাম OCR জানে না (OCRmyPDF-র ডক নিজেই বলছে **[VERIFIED]**)। Matching font সবসময় approximation। একমাত্র ১০০% সম্ভব যদি মূল ফন্ট ফাইলটি জানা থাকে — supplier COA-তে সাধারণত জানা থাকে না।
5. **Edited-Output Accuracy — ⚠️ দুই ভাগে:**
   - **(i) এডিট করা মানটি (value):** ব্যবহারকারী যা টাইপ করলেন, সেটাই আউটপুটে থাকবে — **by construction ১০০% সম্ভব**, কারণ এখানে OCR জড়িত নয়, typed text সরাসরি বসে। এটাই GRAVORA-র সবচেয়ে শক্তিশালী দাবি।
   - **(ii) এডিটের পর পুরো পেজটি দেখতে হুবহু আগের মতো:** **কখনোই ১০০% গ্যারান্টি নয়।** নতুন শব্দ লম্বা/ছোট হলে reflow হবে; inpaint করা patch-এ কাগজের grain, noise, হালকা দাগ হুবহু ফেরানো যায় না; zoom করলে ধরা পড়তে পারে।

### কখনোই ১০০% হবে না — এমন কেস (সৎ তালিকা)
| কেস | কেন |
|---|---|
| হাতের লেখা / স্বাক্ষর | OCR হাতের লেখা নির্ভরযোগ্যভাবে চেনে না — OCRmyPDF ডক নিজেই বলছে "not capable of recognizing handwriting" **[VERIFIED]** |
| টেক্সটের ওপর স্ট্যাম্প / সিল | স্ট্যাম্পের কালি আর প্রিন্টের কালি আলাদা করা যায় না; character boundary ভেঙে যায় |
| Skew / বাঁকা স্ক্যান | লাইন segmentation ভেঙে যায় |
| Low contrast / ফিকে / blur / কম DPI | অক্ষরের আকৃতিই পিক্সেলে থাকে না; Google-র শর্তেই sharp image + even lighting + ≥১০ pixel উচ্চতা চাওয়া হয়েছে **[VERIFIED]** |
| ০/O, ১/l/I, ৫/S-এর মতো দেখতে একরকম অক্ষর | সংখ্যায় ভুল সবচেয়ে বিপজ্জনক — COA-র মান/পরিমাণে এক অক্ষরের ভুল মানে ভুল সার্টিফিকেট |
| টেবিলের লাইন ঘেঁষা / লাইনের ওপর দিয়ে যাওয়া টেক্সট | Box ঠিকমতো বসে না; Google Drive-ও টেবিল ধরে না **[VERIFIED]** |

---

## ৭. ঐচ্ছিক recognition স্তর — Domain-Constrained Verified OCR (OCR বাদ দেওয়া হয়নি, এডিট-পথ থেকে সরানো হয়েছে)

Live-Scan-এ recognition ঐচ্ছিক — শুধু automation-এর জন্য (রেকর্ড, mass-balance)। সেখানে "১০০%"-এর অর্থ: **raw OCR accuracy ১০০% নয়, verified output accuracy ১০০%** — কোনো অনিশ্চিত শব্দ যাচাই ছাড়া issued record-এ যাবে না। পাঁচটি স্তম্ভ:

### স্তম্ভ ১ — Closed Vocabulary (সীমিত শব্দভাণ্ডার)
- **Tesseract:** `--user-words` (নিজের শব্দ-তালিকা) ও `--user-patterns` (regex-ধরনের প্যাটার্ন) man page-তে নথিভুক্ত **[VERIFIED]**; `load_system_dawg F` দিয়ে সিস্টেম dictionary বন্ধ করা যায় **[VERIFIED]**। ⚠️ **সৎ সতর্কতা:** user-words মূলত dictionary-ভিত্তিক (legacy) পথের জন্য নথিভুক্ত — **LSTM ইঞ্জিনে এগুলো কতটা প্রভাব ফেলে, তা ডকুমেন্টেশনে স্পষ্ট নয় — যাচাই হয়নি।** Spike-এ পরীক্ষা করতে হবে।
- **PaddleOCR/RapidOCR:** `rec_char_dict_path` দিয়ে character dictionary বদলানো যায় — তবে এটা **অক্ষরের তালিকা, শব্দের তালিকা নয় [VERIFIED — PaddleOCR ডক/FAQ]**। শব্দ-level সীমাবদ্ধতা built-in নেই — fine-tuning বা post-processing lexicon দিয়ে করতে হয়।
- **গবেষণা-প্রমাণ:** arXiv 2308.09671 (custom vocabularies + CTC beam search) — word error rate-এ "substantial reduction" **[VERIFIED — পেপার আছে ও এই দাবি করে; নির্দিষ্ট শতাংশ snippet-এ দেখা যায়নি]**। Clinical lexicon গবেষণা (হাতে লেখা প্রেসক্রিপশন): কম-confidence টোকেনকে curated lexicon-এর সঙ্গে Levenshtein distance-এ মিলিয়ে WER **৮.৫% → ৩.২% [VERIFIED — abstract; সতর্কতা: ছোট গবেষণা]**। একই পেপারের সতর্কতা: lexicon-এর বাইরের শব্দকে জোর করে কাছের বৈধ শব্দে বদলালে **ভুল কিন্তু দেখতে-ঠিক** ফল হতে পারে — তাই snap শুধু দূরত্ব threshold-এর ভেতরে ও কম-confidence শব্দে। FeOCR (ধাতুবিদ্যা ডকুমেন্ট, MDPI): **শুধু rule-ভিত্তিক correction খারাপ (CER 0.944), শুধু unconstrained LLM আরও খারাপ (CER 1.226); lexicon-সীমাবদ্ধ LLM correction-ই ভালো [VERIFIED]** — খোলা LLM দিয়ে OCR ঠিক করা বিপজ্জনক।

### স্তম্ভ ২ — Template-Aware
কোনো OCR ইঞ্জিনের built-in ফিচার নয় — এটা **আমাদের সিস্টেমের স্তর** (GRAVORA-র template মডেল)। PP-StructureV3 টেবিল-সেলের coordinate দেয় **[VERIFIED — PaddleOCR README]**; docTR-এর KIE predictor key-value ফিল্ড তোলার জন্য বানানো **[VERIFIED — README]**। ফিল্ডের প্রত্যাশিত type/pattern/range দিয়ে cross-check (Batch No-তে শুধু অক্ষর+সংখ্যা, Mfg Date-তে তারিখ-প্যাটার্ন) — আমাদের লিখতে হবে; কার্যকারিতা আমাদের COA-তে মাপা হয়নি **[UNVERIFIED]**। Tesseract PSM mode: `--psm 6` uniform text block-এর জন্য, `--psm 11` ছড়ানো text-এর জন্য **[VERIFIED]**।

### স্তম্ভ ৩ — Dual-Engine Agreement (দুই ইঞ্জিন, অমিল মানেই flag)
- **Multi-layout voting (MDPI):** voting-এ PaddleOCR-এর F1 **+১.৬–২.৮ শতাংশ পয়েন্ট**, Tesseract-এর **+২–৪ শতাংশ পয়েন্ট [VERIFIED — পেপারের Table 3]**।
- **Dual VLM consensus (Zenodo, এপ্রিল ২০২৬):** দুই মডেল যেসব ফিল্ডে **একমত হয়েছে, সেগুলো ~৯৫% সঠিক**; যেখানে অমত, সেখানে ~৪০–৫০% **[VERIFIED — পেপারের ফল; সতর্কতা: VLM, টায়ার-ছবি — COA-র OCR-এ একই সংখ্যা আশা করা যাবে না; তবে "agreement ⇒ উচ্চ নির্ভুলতা, disagreement ⇒ flag" নীতির পক্ষে শক্তিশালী প্রমাণ।]**
- **Hybrid ensemble (ResearchSquare preprint):** ৮০%-এর বেশি CER কমেছে বলে দাবি **[UNVERIFIED — preprint, peer-review হয়নি]**।
- ⚠️ **সতর্কতা — naive voting ক্ষতি করতে পারে:** তিন ইঞ্জিনের majority vote-এ নির্ভুলতা **কমে গিয়েছিল**, কারণ Tesseract-এর ভুলগুলো consistent ছিল **[UNVERIFIED — ব্লগের অভিজ্ঞতা]**। শিক্ষা: **ensemble-এর জন্য ভিন্ন ভিন্ন error mode দরকার** — RapidOCR (DBNet+CRNN) ও Tesseract (LSTM) ভিন্ন আর্কিটেকচার বলে এই জোড়া উপযুক্ত।

### স্তম্ভ ৪ — Targeted Human Confirm ("3-Second Confirm") ও Confidence Score
প্রতি-শব্দ confidence: **Tesseract — প্রতি শব্দে `conf` (TSV-তে) [VERIFIED — man page]**; RapidOCR/PaddleOCR — প্রতি লাইনে `score` (শব্দে নয়) [UNVERIFIED]; docTR — প্রতি শব্দে confidence **[VERIFIED]**; EasyOCR — প্রতি box-এ **[VERIFIED — README]**; Surya 2.5 — প্রতি block-এ **[VERIFIED — README]**। **গুরুত্বপূর্ণ সতর্কতা:** confidence score **ক্যালিব্রেটেড সম্ভাবনা নয়** — উচ্চ confidence-এও ভুল হতে পারে। তাই confidence একা gate হতে পারে না; dual-agreement + template-check + lexicon-check-এর সঙ্গে মিলিয়ে flag করতে হবে। **Flag-হার** (প্রতি পৃষ্ঠায় কটি শব্দ মানুষকে দেখাতে হবে) আসল COA-তে মাপা হয়নি — এটাই "3-Second Confirm"-এর শ্রম-খরচ নির্ধারণ করবে।

### স্তম্ভ ৫ — Learning (প্রতিটি সংশোধন ফিরে যায়)
- **সস্তা পথ (retraining ছাড়া):** সংশোধন → domain শব্দভাণ্ডারে যোগ → Tesseract-এর `user-words`-এ, post-processing lexicon-এ, template-এর প্রত্যাশিত প্যাটার্নে। ফাইল-ভিত্তিক, কোড বদল ছাড়া আপডেট করা যায় **[VERIFIED — user-words মেকানিজম]**।
- **দামি পথ (retraining):** PaddleOCR-এ অফিসিয়াল fine-tuning পথ আছে **[VERIFIED — ডক]**; Tesseract-এ `tesstrain` দিয়ে LSTM fine-tuning **[VERIFIED — README]**। কিন্তু labelled COA ডেটা, সময় ও পরীক্ষা লাগে — **প্রথমে সস্তা পথ, পরে প্রয়োজনে fine-tune।**
- **প্রমাণ:** 5-stream Tesseract ensemble + soft lexicon voting (LV-ROVER-MLT, DocEng 2026): baseline CER 0.0234 → ensemble-এ 0.01317 (**৪৪% কম**), সম্পূর্ণ pipeline-এ 0.00700 (**৭০% কম**) **[VERIFIED — পেপারের dev-set ফল; সতর্কতা: Maltese ভাষা, competition dev-set — আমাদের COA-তে সরাসরি প্রযোজ্য নয়।]**

### OCR ইঞ্জিন — সংক্ষিপ্ত রায় (recognition স্তরের জন্য)
| সিদ্ধান্ত | ইঞ্জিন | কেন |
|---|---|---|
| **প্রথম পছন্দ (primary)** | **RapidOCR** (PP-OCRv5/v6 English, ONNX Runtime) | CPU-তে সবচেয়ে হালকা deep-learning OCR, লাইন-box + confidence, Apache 2.0, সম্পূর্ণ offline, C++ পোর্ট আছে — Tauri sidecar হিসেবে বসানো যায় **[VERIFIED]** |
| **দ্বিতীয় ইঞ্জিন (dual-agreement + word-box উৎস)** | **Tesseract 5** | একমাত্র ইঞ্জিন যা সত্যিকারের **word-level box + প্রতি-শব্দ confidence** দেয় (TSV/hOCR), user-words/user-patterns আছে, Apache 2.0 **[VERIFIED]** |
| **ভবিষ্যৎ বিকল্প** | docTR (word-box + KIE), TrOCR (কঠিন লাইনের specialist) | docTR word-level geometry + confidence দেয় **[VERIFIED]**; TrOCR-এ detection/box কিছুই নেই **[VERIFIED]** |
| **ব্যবহার করবেন না** | Surya 2.5, EasyOCR | Surya এখন 689M VLM + সার্ভার-আর্কিটেকচার + বাণিজ্যিক মডেল-লাইসেন্স সীমা (Open Rail-M, $5M-এর ওপরে আলাদা লাইসেন্স) **[VERIFIED]**; EasyOCR PyTorch-ভারী, রক্ষণাবেক্ষণ ধীর (শেষ release 1.7.2, সেপ্টেম্বর ২০২৪) **[VERIFIED]** |

**মূল নকশা-সিদ্ধান্ত:** overlay-র জন্য word-box দরকার, কিন্তু RapidOCR/PaddleOCR দেয় **লাইন-level** box, word-level নয়। তাই দুই ইঞ্জিনের জোড়া: **Tesseract-এর word-box হবে জ্যামিতির উৎস, RapidOCR-এর লাইন-text হবে recognition-এর উৎস**, দুটো মিলিয়ে cross-check।

---

## ৮. Hard cases — যেকোনো document-এ কী হবে

| কঠিন কেস | Live-Scan-এ সমাধানযোগ্য? | কীভাবে / সীমা |
|---|---|---|
| **হাতের লেখা প্রিন্টের ওপরে** | আংশিক | DBNet হাতের লেখাও box দিতে পারে, কিন্তু শব্দ আলাদা করা কঠিন — অক্ষর জোড়া লাগে, projection profile ভেঙে যায় **[VERIFIED — CEDAR পেপার]**। সমাধান: হাতের লেখা অঞ্চলকে আলাদা class হিসেবে চিহ্নিত করে "manual box" মোড — ব্যবহারকারী নিজে box টেনে এডিট করবেন। |
| **স্ট্যাম্প / সিল লেখার ওপরে** | আংশিক — সম্পূর্ণ ঢাকা লেখা অসম্ভব | আংশিক ঢাকা: ink-only mask + colour separation দিয়ে প্রিন্টের কালি বাঁচানো যায় **[UNVERIFIED]**। সম্পূর্ণ ঢাকা লেখা: pixel-এ তথ্যই নেই — কোনো প্রযুক্তিই তা ফেরত দিতে পারে না **[VERIFIED — LlamaIndex occluded-text পাতা]**। সিল অঞ্চলকে "do-not-edit / flag" হিসেবে দেখানোই সঠিক। |
| **বাঁকা (skewed) স্ক্যান** | হ্যাঁ | Deskew প্রথম ধাপ — Hough transform বা projection-profile maximisation দিয়ে কোণ বের করে rotate করা standard practice **[UNVERIFIED]**। rotated box-এর কোণ সংরক্ষণ করতে হবে; DBNet/EAST rotated box দিতে পারে **[VERIFIED — EAST geometry map-এ rotation angle থাকে]**। |
| **নিম্ন-রেজোলিউশন স্ক্যান** | সীমা আছে | ৩০০ DPI PG COA-র মতো স্ক্যানে কাজ করবে; ১৫০ DPI-র নিচে ছোট অক্ষরের box-ই অনিশ্চিত **[UNVERIFIED — বিচার]**। সমাধান: upscaling + "low-confidence box" হিসেবে চিহ্নিত করে confirm। |
| **রঙিন কাগজ / রঙিন background** | হ্যাঁ | Ink-only mask + local background sampling; সাদা-কালো threshold-এর বদলে adaptive threshold লাগবে **[UNVERIFIED — ডিজাইন প্রস্তাব]**। |
| **ফিকে (faint) প্রিন্ট** | আংশিক | Adaptive threshold (Sauvola) দিয়ে ফিকে কালি ধরা যায় **[VERIFIED — OCR-free ToC পেপারে Sauvola-র উল্লেখ]**। খুব ফিকে হলে box-এর confidence কমবে — UI-তে দেখাতে হবে। |
| **টেবিলের লাইন লেখার গায়ে লেগে থাকা** | হ্যাঁ — ink-only mask-ই সমাধান | পুরো box মুছলে লাইন মুছে যাবে; শুধু কালির pixel মুছলে লাইন বেঁচে থাকে **[VERIFIED — dev.to নিবন্ধ]**। |

**সবচেয়ে কঠিন তিনটি (সততার সঙ্গে):** (১) সম্পূর্ণ ঢাকা/অদৃশ্য লেখা — তথ্যই নেই; (২) হাতের লেখার word-split — নির্ভরযোগ্য নয়; (৩) হুবহু font মেলানো — approximate-ই থাকবে। এগুলোকে "সীমা" হিসেবে পণ্যে লিখতে হবে, "শীঘ্রই ঠিক হবে" বলে লুকানো যাবে না।

---

## ৯. সতর্কতা — Audit ও জালিয়াতি

Supplier COA-র মতো document এডিট করা মানে **মূল নথি বদলে ফেলার ক্ষমতা**। Live-Scan-এ মূল স্ক্যানকে immutable রাখতে হবে — এডিট শুধু overlay layer-এ, প্রতিটি এডিটের version + audit trail সহ, আর exported ফাইলে "edited" চিহ্ন থাকা উচিত। নইলে এই প্রযুক্তি জালিয়াতির হাতিয়ার হয়ে যাবে। **[UNVERIFIED — সুপারিশ, কোনো সোর্সের দাবি নয়; কিন্তু GRAVORA-র QC/audit প্রেক্ষাপটে অপরিহার্য।]** এছাড়া inpainted জায়গাটি "অনুমান", "আসল" নয় — COA-র মতো audit document-এ এটি একটি সততার সীমা।

---

## ১০. কী করবেন প্রথমে — Build ক্রম

1. **Spike ১ (১–২ দিন):** PG COA-র একটি পাতায় PP-OCRv5 mobile det-only ONNX চালিয়ে box বের করুন; i5-8265U-তে সময় মাপুন; line-box → projection-profile word-split-এর নির্ভুলতা চোখে দেখুন। এটাই go/no-go পরীক্ষা। *(প্রোটোটাইপে classical পথ দিয়ে ইতিমধ্যে করা হয়েছে — REPORT.md দেখুন।)*
2. **Spike ২:** একটি শব্দে ক্লিক → ink-only mask (Otsu) → OpenCV inpaint → metric font-এ নতুন লেখা render → আগের background-এর ওপরে বসানো। সাদা কাগজে এটা দিয়েই ১০০%-এর কাছাকাছি দেখাবে কিনা যাচাই করুন। *(প্রোটোটাইপে Telea দিয়ে করা হয়েছে — REPORT.md দেখুন।)*
3. **তারপর:** LaMa ONNX (textured background-এর জন্য; licence যাচাইয়ের পর), Docling Heron (layout zone), font shortlist UI, multi-page, save/export।
4. **Recognition (Donut/GOT/RapidOCR+Tesseract dual) পরে, আলাদা ধাপে** — শুধু automation-এর জন্য, এডিট-পথে নয়। Nougat/Vary বাণিজ্যিকভাবে ব্যবহার করবেন না (licence)।
5. **Spike-এ মাপার তালিকা:** Telea vs NS (PG পাতায় চোখে দেখে); LaMa ONNX crop — সময়, RAM, Telea-র সঙ্গে visual তুলনা; background-colour cover vs Telea; font size অনুমান (bbox-height vs width-fit); stamp/underline/handwriting word-এ mask-এর ক্ষতি — "do not auto-edit" তালিকা।

## ১১. চূড়ান্ত কথা

**Paradigm সঠিক।** Detection আর recognition আলাদা — এটা প্রমাণিত। স্ক্যানকে background রেখে তার ওপরে live text layer বসানো — এটার উপাদান (DBNet detection-only, ink-only mask, LaMa inpainting, font পরিমাপ) সবই আছে, কিন্তু এইভাবে জোড়া দেওয়া, OCR-মুক্ত, offline প্রোডাক্ট গবেষণায় খুঁজে পাওয়া যায়নি। **প্রথম build DBNet-mobile + projection-profile দিয়ে শুরু করুন; Donut/Nougat/Vary দিয়ে নয়।** কঠিন কেসগুলোর মধ্যে স্ট্যাম্পের নিচের অদৃশ্য লেখা ও হাতের লেখার word-split — এ দুটোকে স্পষ্ট সীমা হিসেবে স্বীকার করুন, বাকিগুলো engineering দিয়ে সমাধানযোগ্য।
