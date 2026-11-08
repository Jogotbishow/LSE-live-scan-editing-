# LSE label — save → label (Domino)

এডিট করা স্ক্যান পাতা সেভ হলেই **সেই পাতার/প্যাকের নিজের লেবেল** তৈরি হয় —
সেই পাতারই এডিট করা মান দিয়ে। এক পাতার মান অন্য পাতার লেবেলে কখনো যায় না;
খালি ঘরে কখনো ডেমো/ভুয়া মান বসে না।

এটা প্রোটোটাইপে প্রমাণিত ওয়্যারিংয়ের স্ট্যান্ডঅ্যালোন সংস্করণ: Round 8 Track C
`save-label.js` + Round 10 ভেরিফায়ার `verify_save_label_live_r10b.py`
(৫ পাতায় ৯০/৯০) এবং Round 7 লেবেল `labels/label-lse-*.html` — একই লেআউট
পরিবার, একই নিয়ম। এখানে কোনো OCR নেই: এই মডিউল স্ক্যান পড়ে না, শুধু
কলার দেওয়া মান (ইউজার লাইভ পাতায় যা টাইপ করেছে, ইঞ্জিনের সেভ রেকর্ডে যা
এসেছে) রেন্ডার করে।

## নিয়ম

1. **এক পাতা = এক লেবেল।** `build_label` একবারে এক পাতার `edited_values`
   দেখে; অন্য পাতার মান ঢোকার রাস্তা নেই।
2. **খালি ঘর খালিই থাকে।** মান না থাকলে / ফাঁকা হলে লেবেলে লেখা থাকে
   `— পূরণ হয়নি —` (লাল), `unfilled_fields`-এ ওঠে, আর required ঘর খালি
   থাকলে `is_printable = False` হয় (ছাপার আগে পূরণ করতে হবে)।
3. **ডেমো মান কখনো চুপিসারে বসে না।** `demo_values={...}` দিলে সেই
   স্ট্রিংয়ের সমান কোনো মান এলে সেটা বাতিল হয়ে খালি ঘর হয়, আর
   `refused_demo`-তে রিপোর্ট হয়।
4. **কোনো সংখ্যা বানানো হয় না।** `label_no`, `delivery` না দিলে খালি
   দেখায়; ফাইলের নাম `page_key` দিয়ে হয়, নিজে থেকে লেবেল নম্বর বানায় না।
5. **Lot আর Batch আলাদা।** প্রোটোটাইপ এক সারিতে মিলিয়ে দেখাত; এখানে
   আলাদা সারি — একটা থাকলে অন্যটা খালি থাকে, একটার মান অন্যটায় বসে না।

## `edited_values` — ঠিক যে dict `build_label` চায়

```python
{
  "page_key": "aug-p1",          # আবশ্যক — ফাইলের নামেও এটাই
  "page_label": "Aug p.1",       # আবশ্যক — লেবেলে WIDTH সারির পাতা
  "page_no": 1,                  # ঐচ্ছিক
  "delivery": "LSE-0008",        # ঐচ্ছিক
  "delivery_id": "LSE-DEL-...",  # ঐচ্ছিক
  "label_no": "LBL-0001",        # ঐচ্ছিক; না থাকলে খালি দেখায়
  "draft": True,                 # ঐচ্ছিক, ডিফল্ট True → "খসড়া — DRAFT";
                                 # False হলে "QC PASSED" ছাপ ওঠে
  # --- মানের ঘর: প্রতিটা হয় str, নয় {"new","old","box300"} dict,
  # --- নয় None / "" / অনুপস্থিত (= খালি) ---
  "lot":       {"old": "206/7", "new": "207/9", "box300": [533, 930, 631, 966]},
  "width":     {"old": "780.0", "new": "781.5", "box300": [2088, 1282, 2178, 1310]},
  "batch":     "ACME-2026-0001",          # str-ও চলে
  "thickness": "25.2",
  "item":      "Blister Foil 25 Micron",  # "product" এর উপনাম
  "customer":  "Packfirm Limited",
  "supplier":  "ACME FOILS LTD",
  "date": "07.11.2026", "mfg_date": ..., "expiry_date": ...,
  "gross_weight": ..., "net_weight": ..., "packs": ...,
  "version": ..., "material_code": ...,
  "edits": [{"field": "lot", "old": "206/7", "new": "207/9",
             "box300": [533, 930, 631, 966]}],   # ঐচ্ছিক, অডিট লাইনে যায়
  "extra_fields": {"Roll No.": "R-12"},   # ঐচ্ছিক, অতিরিক্ত সারি
  "required": ["lot", "width"],           # ঐচ্ছিক; ডিফল্ট ("lot","width")
  "source_note": "...",                   # ঐচ্ছিক, ফুটারে যায়
}
```

`{"new","old","box300"}` আকারটা ইচ্ছা করেই প্রোটোটাইপের সেভ রেকর্ডের
(`lse-edits-<page>.json`: `page_key`, `lot`/`width` `{old,new,box300}`,
`edits` লিস্ট) মতো — ইঞ্জিনের সেভ আউটপুট সরাসরি ঢোকে। `box300` হলো শব্দের
বাক্স নেটিভ DPI-তে; অডিট লাইনে `old → new` দেখাতে ব্যবহৃত হয়।

## API

```python
from label import build_label, build_label_html, build_label_pdf
from label import save_with_label, build_labels_for_pages
from label import edited_values_from_save_record

res = build_label(edited_values)          # LabelResult
res.html            # লেবেল HTML (stdlib-ই যথেষ্ট)
res.unfilled_fields # ['expiry_date', ...]
res.refused_demo    # ডেমো মান বাতিল হলে এখানে
res.is_printable    # required ঘর সব ভরা + label_no আছে কি না
res.is_draft        # True → "খসড়া — DRAFT" ব্যানার; False → QC PASSED
res.to_dict()       # JSON-যোগ্য সারাংশ

html = build_label_html(edited_values)
pdf_bytes = build_label_pdf(edited_values)   # 100mm x 160mm, PyMuPDF লাগে;
                                             # না থাকলে পরিষ্কার RuntimeError

# Domino: ইঞ্জিন এডিট করা PDF সেভ করার পর, প্রতি পাতায় একবার —
manifest = save_with_label(edited_values, out_dir,
                           edited_pdf_path="/path/to/edited.pdf")
# লেখে: label-<page_key>.html, label-<page_key>.pdf, label-<page_key>.json
# (manifest-এ edited_values যেমন এসেছে, resolved fields, unfilled,
#  edited PDF-র SHA-256; এডিট করা PDF কপি/সরানো হয় না)

manifests = build_labels_for_pages([page1_values, page2_values], out_dir)

# প্রোটোটাইপ/ইঞ্জিনের সেভ রেকর্ড সরাসরি নেওয়া যায়
# (camelCase pageKey/pageLabel/labelNo/deliveryId-ও চলে):
values = edited_values_from_save_record(save_record)
```

## যাচাই (নিজের চালানো সংখ্যা)

`tests/test_label.py` — `python -m unittest discover -s tests -v` (stdlib
unittest; PDF টেস্ট PyMuPDF না থাকলে skip হয়)।

`verify_label.py` — end-to-end (ACME সিনথেটিক + আসল PG Aug পাতা ১;
আসল PDF শুধু পড়া হয়, `/tmp`-এ কাজ হয়, রেপোতে কপি হয় না):

- ACME: Lot `ACME-LOT-77 → ACME-LOT-78`, Batch `ACME-2026-0001 →
  ACME-2026-0002`, Thickness `25.2 → 25.4` এডিট করে লেবেল — লেবেলে
  এডিট করা মানই আছে, পুরনো মান শুধু অডিট লাইনে (`old → new`)।
- PG Aug p.1 (আসল স্ক্যান, ৮ পাতার PDF-র পাতা ১): Lot `206/7 → 207/9`,
  WIDTH `780.0 → 781.5 mm`, `LBL-0001`, `LSE-0008` — May পাতার কোনো
  মান (305/7, 671.5 …) লেবেলে নেই।

ফলাফল `verify-out/`-এ: `label-acme-p1.*`, `label-aug-p1.*`।

## যা যাচাই হয়নি

- ইঞ্জিনের মাল্টি-পেজ সেভ ফ্লোতে আসল ওয়্যারিং (ইঞ্জিন এজেন্টের কাজ;
  কো-অর্ডিনেটর পরে `save_with_label` জুড়বে) — এখানে সেভ রেকর্ডের আকার
  ধরে নিয়ে অ্যাডাপ্টারসহ যাচাই করা হয়েছে।
- প্রিন্ট ক্যালিব্রেশন (আসল প্রিন্টার লাগে — ইউজারের কাজ, পরে)।
- পেটেন্ট যাচাই (ইউজার নিজে করবেন)।
```

## সীমা

- টেমপ্লেট একটাই: `supplier-foil` (প্রোটোটাইপের লেবেল পরিবার)।
- PDF বানাতে PyMuPDF লাগে; না থাকলে শুধু HTML পাওয়া যায়।
- `label_no` নিজে থেকে বানায় না — কলারকে দিতে হয়, নইলে খালি দেখায়।
