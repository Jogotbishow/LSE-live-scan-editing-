"""SQLite record for edited scan deliveries — schema v3 (clean).

Ported from the GRAVORA prototype Round 3 (scan-paper/improve/round3/
track-c/lse_db.py, schema v1) + Round 7 Track A (lse_db3.py, schema v3:
one packing label PER PAGE). The prototype reached v3 by migration
(v1 -> v2 -> v3); this package ships the v3 schema directly, so no
migration runs. Hash formulas are UNCHANGED from the prototype:

  audit_log.entry_hash = digest({"prev_hash": <previous entry_hash,
    or "0"*64 for genesis>, "event_id", "at", "actor", "action",
    "subject_id", "detail"}) — hash-chained, append-only. Any change
    to any field of any row breaks the chain at that row.
  deliveries.delivery_hash (v3) = digest of the delivery fields +
    per-page list + per-page labels list (see _delivery_hash_v3).
  labels.label_hash = the FROZEN v2 formula (covers the v2 columns
    only), so a label still verifies the same way it did in v2.

Immutability: triggers ABORT UPDATE/DELETE on issued deliveries,
delivery_pages, labels, lse_edits and audit_log (same pattern as
prism_qc_core.py). A supersede never touches the old row — it appends
a hash-chained ``lse.delivery.superseded`` audit event.

Labels are one per page (Round 7 decision b1+c3): deliveries.label_ref
keeps its v2 meaning — the FIRST page's (p.1) label — for backward
compatibility. Per-page resolution goes through
resolve_label_for_page() / resolve_labels_for_delivery().
"""
import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone

GENESIS_PREV_HASH = "0" * 64
LSE_VERSION = "LSE-EDITED v1"

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS counters(name TEXT PRIMARY KEY, value INTEGER NOT NULL CHECK(value>=1));
CREATE TABLE IF NOT EXISTS deliveries(
  id TEXT PRIMARY KEY, serial INTEGER NOT NULL UNIQUE, number TEXT NOT NULL UNIQUE,
  client TEXT NOT NULL, item TEXT NOT NULL, document_type TEXT NOT NULL,
  source_document TEXT NOT NULL, source_page INTEGER NOT NULL,
  source_sha256 TEXT NOT NULL, output_pdf_name TEXT NOT NULL,
  output_pdf_sha256 TEXT NOT NULL, lse_version TEXT NOT NULL,
  edited_fields_json TEXT NOT NULL, delivery_hash TEXT NOT NULL,
  label_ref TEXT, created_at TEXT NOT NULL, created_by TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('issued')));
CREATE TABLE IF NOT EXISTS delivery_pages(
  id TEXT PRIMARY KEY, delivery_id TEXT NOT NULL REFERENCES deliveries(id),
  page_no INTEGER NOT NULL, source_page INTEGER NOT NULL,
  source_document TEXT NOT NULL, source_sha256 TEXT NOT NULL,
  output_pdf_name TEXT NOT NULL, page_pdf_sha256 TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(delivery_id, page_no));
CREATE TABLE IF NOT EXISTS labels(
  id TEXT PRIMARY KEY, number TEXT NOT NULL UNIQUE,
  delivery_id TEXT NOT NULL REFERENCES deliveries(id),
  source_delivery_number TEXT NOT NULL,
  item TEXT NOT NULL, customer TEXT NOT NULL,
  batch_no TEXT, width_mm TEXT,
  label_html_name TEXT, label_pdf_name TEXT, label_pdf_sha256 TEXT,
  label_hash TEXT NOT NULL, created_at TEXT NOT NULL, created_by TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('issued')),
  page_no INTEGER, source_page INTEGER, source_document TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS idx_labels_delivery_page
  ON labels(delivery_id, page_no);
CREATE TABLE IF NOT EXISTS lse_edits(
  id TEXT PRIMARY KEY, delivery_id TEXT NOT NULL REFERENCES deliveries(id),
  page INTEGER NOT NULL, word_index INTEGER NOT NULL,
  box_json TEXT NOT NULL, row_label TEXT NOT NULL,
  old_text TEXT NOT NULL, new_text TEXT NOT NULL,
  font TEXT NOT NULL, font_size_px REAL NOT NULL, ink_rgb_json TEXT NOT NULL,
  created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit_log(
  id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL UNIQUE,
  at TEXT NOT NULL, actor TEXT NOT NULL, action TEXT NOT NULL,
  subject_id TEXT NOT NULL, detail_json TEXT NOT NULL,
  prev_hash TEXT NOT NULL, entry_hash TEXT NOT NULL);
CREATE TRIGGER IF NOT EXISTS immutable_delivery_update BEFORE UPDATE ON deliveries
  BEGIN SELECT RAISE(ABORT,'issued delivery is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_delivery_delete BEFORE DELETE ON deliveries
  BEGIN SELECT RAISE(ABORT,'issued delivery is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_delivery_page_update BEFORE UPDATE ON delivery_pages
  BEGIN SELECT RAISE(ABORT,'issued delivery page is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_delivery_page_delete BEFORE DELETE ON delivery_pages
  BEGIN SELECT RAISE(ABORT,'issued delivery page is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_label_update BEFORE UPDATE ON labels
  BEGIN SELECT RAISE(ABORT,'issued label is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_label_delete BEFORE DELETE ON labels
  BEGIN SELECT RAISE(ABORT,'issued label is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_lse_edit_update BEFORE UPDATE ON lse_edits
  BEGIN SELECT RAISE(ABORT,'issued edit record is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_lse_edit_delete BEFORE DELETE ON lse_edits
  BEGIN SELECT RAISE(ABORT,'issued edit record is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_audit_update BEFORE UPDATE ON audit_log
  BEGIN SELECT RAISE(ABORT,'audit is append only'); END;
CREATE TRIGGER IF NOT EXISTS immutable_audit_delete BEFORE DELETE ON audit_log
  BEGIN SELECT RAISE(ABORT,'audit is append only'); END;
"""


def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def new_id(prefix):
    return prefix + "-" + uuid.uuid4().hex


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def connect(path):
    c = sqlite3.connect(path, timeout=15, isolation_level=None)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c


def init_db(path):
    """Create (or open) the database at ``path``; seed counters + meta."""
    c = connect(path)
    c.executescript(SCHEMA)
    c.execute("BEGIN")
    try:
        c.execute("INSERT OR IGNORE INTO counters(name, value) VALUES('delivery_serial', 1)")
        c.execute("INSERT OR IGNORE INTO counters(name, value) VALUES('label_serial', 1)")
        c.execute("INSERT OR IGNORE INTO meta(key, value) VALUES('schema_version', '3')")
        c.execute("INSERT OR IGNORE INTO meta(key, value) VALUES('module', 'LSE — pdf write-back + db record (schema v3, one label per page)')")
        c.execute("COMMIT")
    except Exception:
        c.execute("ROLLBACK")
        raise
    return c


def _last_entry_hash(c):
    row = c.execute("SELECT entry_hash FROM audit_log ORDER BY id DESC LIMIT 1").fetchone()
    return row["entry_hash"] if row else GENESIS_PREV_HASH


def _audit(c, action, actor, subject_id, detail):
    """Append one hash-chained audit event. Must be called inside a txn."""
    event_id = new_id("EVT")
    at = utcnow()
    prev_hash = _last_entry_hash(c)
    entry_hash = digest({"prev_hash": prev_hash, "event_id": event_id, "at": at,
                         "actor": actor, "action": action, "subject_id": subject_id,
                         "detail": detail})
    c.execute(
        "INSERT INTO audit_log(event_id, at, actor, action, subject_id,"
        " detail_json, prev_hash, entry_hash) VALUES(?,?,?,?,?,?,?,?)",
        (event_id, at, actor, action, subject_id, canonical(detail),
         prev_hash, entry_hash))
    return event_id


def _label_hash(label_id, label_number, delivery_id, number, lab, created_at, actor):
    """FROZEN v2 label-hash formula (covers the v2 columns only)."""
    return digest({
        "id": label_id, "number": label_number, "delivery_id": delivery_id,
        "source_delivery_number": number, "item": lab["item"],
        "customer": lab["customer"], "batch_no": lab["batch_no"],
        "width_mm": lab.get("width_mm"),
        "label_html_name": lab["label_html_name"],
        "label_pdf_name": lab["label_pdf_name"],
        "label_pdf_sha256": lab["label_pdf_sha256"],
        "created_at": created_at, "created_by": actor, "status": "issued"})


def _labels_list_v3(c, delivery_id):
    rows = c.execute(
        "SELECT * FROM labels WHERE delivery_id = ? ORDER BY page_no",
        (delivery_id,)).fetchall()
    return [{"number": r["number"], "page_no": r["page_no"],
             "source_page": r["source_page"], "batch_no": r["batch_no"],
             "width_mm": r["width_mm"], "label_id": r["id"]} for r in rows]


def _delivery_hash_v3(delivery_id, number, delivery, pages, labels_list,
                      label_ref, created_at, actor):
    return digest({
        "id": delivery_id, "number": number, "client": delivery["client"],
        "item": delivery["item"], "document_type": delivery["document_type"],
        "source_document": delivery["source_document"],
        "source_page": delivery["source_page"],
        "source_sha256": delivery["source_sha256"],
        "output_pdf_name": delivery["output_pdf_name"],
        "output_pdf_sha256": delivery["output_pdf_sha256"],
        "lse_version": delivery["lse_version"],
        "edited_fields": [e for p in pages for e in p["edited_fields"]],
        "pages": pages, "labels": labels_list, "label_ref": label_ref,
        "created_at": created_at, "created_by": actor, "status": "issued"})


def record_delivery(c, delivery, edits, actor="qc", audit_extra=None):
    """Record one single-page delivery + its word edits + audit events.

    ``delivery``: client, item, document_type, source_document,
    source_page, source_sha256, output_pdf_name, output_pdf_sha256,
    lse_version, label_ref (or None). ``edits``: edit records as
    returned by writeback (row_label, box, old_text, new_text, font,
    font_size_px, ink_rgb). Returns the delivery id. (v1 contract,
    kept for single-page callers; multi-page callers use
    record_multipage_delivery().)
    """
    c.execute("BEGIN")
    try:
        row = c.execute("SELECT value FROM counters WHERE name='delivery_serial'").fetchone()
        serial = int(row["value"])
        c.execute("UPDATE counters SET value = value + 1 WHERE name='delivery_serial'")
        delivery_id = delivery.get("id") or new_id("LSE-DEL")
        number = f"LSE-{serial:04d}"
        created_at = utcnow()
        edited_fields = [{"row_label": e["row_label"], "box": e["box"],
                          "old_text": e["old_text"], "new_text": e["new_text"],
                          "font": e["font"], "font_size_px": e["font_size_px"]}
                         for e in edits]
        delivery_hash = digest({
            "id": delivery_id, "number": number, "client": delivery["client"],
            "item": delivery["item"], "document_type": delivery["document_type"],
            "source_document": delivery["source_document"],
            "source_page": delivery["source_page"],
            "source_sha256": delivery["source_sha256"],
            "output_pdf_name": delivery["output_pdf_name"],
            "output_pdf_sha256": delivery["output_pdf_sha256"],
            "lse_version": delivery["lse_version"],
            "edited_fields": edited_fields, "label_ref": delivery.get("label_ref"),
            "created_at": created_at, "created_by": actor, "status": "issued"})
        c.execute(
            "INSERT INTO deliveries(id, serial, number, client, item, document_type,"
            " source_document, source_page, source_sha256, output_pdf_name,"
            " output_pdf_sha256, lse_version, edited_fields_json, delivery_hash,"
            " label_ref, created_at, created_by, status)"
            " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'issued')",
            (delivery_id, serial, number, delivery["client"], delivery["item"],
             delivery["document_type"], delivery["source_document"],
             delivery["source_page"], delivery["source_sha256"],
             delivery["output_pdf_name"], delivery["output_pdf_sha256"],
             delivery["lse_version"], canonical(edited_fields), delivery_hash,
             delivery.get("label_ref"), created_at, actor))
        for i, e in enumerate(edits):
            c.execute(
                "INSERT INTO lse_edits(id, delivery_id, page, word_index, box_json,"
                " row_label, old_text, new_text, font, font_size_px, ink_rgb_json,"
                " created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (new_id("LSE-EDT"), delivery_id, delivery["source_page"], i,
                 canonical(e["box"]), e["row_label"], e["old_text"], e["new_text"],
                 e["font"], e["font_size_px"], canonical(e["ink_rgb"]), created_at))
        rec_detail = {"number": number, "source_document": delivery["source_document"],
                      "source_sha256": delivery["source_sha256"],
                      "output_pdf_name": delivery["output_pdf_name"],
                      "output_pdf_sha256": delivery["output_pdf_sha256"],
                      "edits": edited_fields}
        if audit_extra:
            rec_detail.update(audit_extra)
        _audit(c, "lse.delivery.recorded", actor, delivery_id, rec_detail)
        _audit(c, "lse.pdf.issued", actor, delivery_id,
               {"output_pdf_name": delivery["output_pdf_name"],
                "output_pdf_sha256": delivery["output_pdf_sha256"],
                "lse_version": delivery["lse_version"]})
        c.execute("COMMIT")
    except Exception:
        c.execute("ROLLBACK")
        raise
    return delivery_id


def record_multipage_delivery(c, delivery, pages, labels, actor="qc",
                              audit_extra=None):
    """Record one multi-page delivery + its pages + edits + ONE LABEL
    PER PAGE + hash-chained audit events, in a single transaction.

    ``delivery``: same fields as record_delivery() (source_* describe
    page 1 / the document as a whole). ``pages``: list, in page order,
    of {page_no, source_page, source_document, source_sha256,
    output_pdf_name, page_pdf_sha256, edits: [edit records]}.
    ``labels``: list, one per page IN PAGE ORDER, each {page_no,
    source_page, source_document, item, customer, batch_no, width_mm,
    label_html_name, label_pdf_name, label_pdf_sha256} (batch_no /
    width_mm may be None when the page has no Lot/WIDTH edit).
    deliveries.label_ref = labels[0].id (the p.1 label).
    Returns (delivery_id, number, [label_numbers in page order]).
    """
    assert labels, "v3 delivery needs at least one per-page label"
    assert [l["page_no"] for l in labels] == [p["page_no"] for p in pages], \
        "labels must be one per page, in page order"
    assert all(l.get("page_no") is not None and l.get("source_page") is not None
               for l in labels), "each label needs page_no + source_page"
    c.execute("BEGIN")
    try:
        row = c.execute("SELECT value FROM counters WHERE name='delivery_serial'").fetchone()
        serial = int(row["value"])
        c.execute("UPDATE counters SET value = value + 1 WHERE name='delivery_serial'")
        delivery_id = delivery.get("id") or new_id("LSE-DEL")
        number = f"LSE-{serial:04d}"
        created_at = utcnow()

        # Insert order matters: labels.delivery_id is a FOREIGN KEY to
        # deliveries(id), and FK enforcement is ON (connect() sets
        # PRAGMA foreign_keys = ON). The prototype's v3 function
        # inserted labels FIRST and got away with it only because its
        # connection did not enforce the FK. Here the delivery row is
        # inserted first; the label ids/numbers/hashes are all computed
        # up-front (they need no DB reads), so the hash formulas are
        # unchanged — only the INSERT order changes.
        label_ids, label_numbers, label_rows = [], [], []
        for lab in labels:
            lrow = c.execute("SELECT value FROM counters WHERE name='label_serial'").fetchone()
            lserial = int(lrow["value"])
            c.execute("UPDATE counters SET value = value + 1 WHERE name='label_serial'")
            label_id = lab.get("id") or new_id("LBL")
            label_number = f"LBL-{lserial:04d}"
            label_hash = _label_hash(label_id, label_number, delivery_id,
                                     number, lab, created_at, actor)
            label_ids.append(label_id)
            label_numbers.append(label_number)
            label_rows.append((label_id, label_number, delivery_id, number,
                               lab["item"], lab["customer"], lab.get("batch_no"),
                               lab.get("width_mm"), lab["label_html_name"],
                               lab["label_pdf_name"], lab["label_pdf_sha256"],
                               label_hash, created_at, actor, lab["page_no"],
                               lab["source_page"], lab.get("source_document")))

        label_ref = label_ids[0]  # p.1 label: backward-compatible primary
        pages_h = []
        for pg in pages:
            ef = [{"row_label": e["row_label"], "box": e["box"],
                   "old_text": e["old_text"], "new_text": e["new_text"],
                   "font": e["font"], "font_size_px": e["font_size_px"]}
                  for e in pg["edits"]]
            pages_h.append({
                "page_no": pg["page_no"], "source_page": pg["source_page"],
                "source_document": pg["source_document"],
                "source_sha256": pg["source_sha256"],
                "output_pdf_name": pg["output_pdf_name"],
                "page_pdf_sha256": pg["page_pdf_sha256"],
                "edited_fields": ef})
        labels_list = [{"number": ln, "page_no": lab["page_no"],
                        "source_page": lab["source_page"],
                        "batch_no": lab.get("batch_no"),
                        "width_mm": lab.get("width_mm"),
                        "label_id": lid}
                       for ln, lab, lid in zip(label_numbers, labels, label_ids)]
        delivery_hash = _delivery_hash_v3(
            delivery_id, number, delivery, pages_h, labels_list, label_ref,
            created_at, actor)
        all_ef = [e for p in pages_h for e in p["edited_fields"]]
        c.execute(
            "INSERT INTO deliveries(id, serial, number, client, item, document_type,"
            " source_document, source_page, source_sha256, output_pdf_name,"
            " output_pdf_sha256, lse_version, edited_fields_json, delivery_hash,"
            " label_ref, created_at, created_by, status)"
            " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'issued')",
            (delivery_id, serial, number, delivery["client"], delivery["item"],
             delivery["document_type"], delivery["source_document"],
             delivery["source_page"], delivery["source_sha256"],
             delivery["output_pdf_name"], delivery["output_pdf_sha256"],
             delivery["lse_version"], canonical(all_ef), delivery_hash,
             label_ref, created_at, actor))
        # The delivery row exists now, so the labels' FK is satisfied.
        for row in label_rows:
            c.execute(
                "INSERT INTO labels(id, number, delivery_id, source_delivery_number,"
                " item, customer, batch_no, width_mm, label_html_name,"
                " label_pdf_name, label_pdf_sha256, label_hash, created_at,"
                " created_by, status, page_no, source_page, source_document)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'issued', ?, ?, ?)",
                row)
        for pg, pgh in zip(pages, pages_h):
            c.execute(
                "INSERT INTO delivery_pages(id, delivery_id, page_no, source_page,"
                " source_document, source_sha256, output_pdf_name, page_pdf_sha256,"
                " created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                (new_id("LSE-PG"), delivery_id, pg["page_no"],
                 pg["source_page"], pg["source_document"], pg["source_sha256"],
                 pg["output_pdf_name"], pg["page_pdf_sha256"], created_at))
            for i, e in enumerate(pg["edits"]):
                c.execute(
                    "INSERT INTO lse_edits(id, delivery_id, page, word_index, box_json,"
                    " row_label, old_text, new_text, font, font_size_px, ink_rgb_json,"
                    " created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    (new_id("LSE-EDT"), delivery_id, pg["source_page"], i,
                     canonical(e["box"]), e["row_label"], e["old_text"],
                     e["new_text"], e["font"], e["font_size_px"],
                     canonical(e["ink_rgb"]), created_at))
        rec_detail = {"number": number,
                      "source_document": delivery["source_document"],
                      "source_sha256": delivery["source_sha256"],
                      "output_pdf_name": delivery["output_pdf_name"],
                      "output_pdf_sha256": delivery["output_pdf_sha256"],
                      "pages": [{"page_no": p["page_no"],
                                 "source_page": p["source_page"],
                                 "source_document": p["source_document"],
                                 "source_sha256": p["source_sha256"],
                                 "output_pdf_name": p["output_pdf_name"],
                                 "page_pdf_sha256": p["page_pdf_sha256"],
                                 "edits": p["edited_fields"]} for p in pages_h],
                      "label_ref": label_ref,
                      "labels": labels_list}
        if audit_extra:
            rec_detail.update(audit_extra)
        _audit(c, "lse.delivery.recorded", actor, delivery_id, rec_detail)
        _audit(c, "lse.pdf.issued", actor, delivery_id,
               {"output_pdf_name": delivery["output_pdf_name"],
                "output_pdf_sha256": delivery["output_pdf_sha256"],
                "lse_version": delivery["lse_version"],
                "pages": len(pages)})
        for lab, ln, lid in zip(labels, label_numbers, label_ids):
            _audit(c, "lse.label.linked", actor, delivery_id,
                   {"label_id": lid, "label_number": ln,
                    "page_no": lab["page_no"],
                    "source_page": lab["source_page"],
                    "batch_no": lab.get("batch_no"),
                    "width_mm": lab.get("width_mm"),
                    "item": lab["item"]})
        c.execute("COMMIT")
    except Exception:
        c.execute("ROLLBACK")
        raise
    return delivery_id, number, label_numbers


def record_supersede(c, old_delivery_id, new_delivery_id, new_number,
                     reason, actor="qc"):
    """Append a hash-chained event marking an older delivery superseded.
    The old delivery row itself is never touched (immutable trigger)."""
    c.execute("BEGIN")
    try:
        old = c.execute("SELECT number, output_pdf_name FROM deliveries WHERE id = ?",
                        (old_delivery_id,)).fetchone()
        detail = {"superseded_delivery_id": old_delivery_id,
                  "superseded_number": old["number"] if old else None,
                  "superseded_output_pdf_name": old["output_pdf_name"] if old else None,
                  "superseded_by_delivery_id": new_delivery_id,
                  "superseded_by_number": new_number,
                  "reason": reason}
        event_id = _audit(c, "lse.delivery.superseded", actor,
                          old_delivery_id, detail)
        c.execute("COMMIT")
    except Exception:
        c.execute("ROLLBACK")
        raise
    return event_id


def get_delivery(c, delivery_id):
    row = c.execute("SELECT * FROM deliveries WHERE id = ?", (delivery_id,)).fetchone()
    if row is None:
        return None
    d = dict(row)
    d["edited_fields"] = json.loads(d["edited_fields_json"])
    d["edits"] = [dict(r) for r in c.execute(
        "SELECT * FROM lse_edits WHERE delivery_id = ? ORDER BY page, word_index",
        (delivery_id,)).fetchall()]
    d["pages"] = [dict(r) for r in c.execute(
        "SELECT * FROM delivery_pages WHERE delivery_id = ? ORDER BY page_no",
        (delivery_id,)).fetchall()]
    d["labels"] = resolve_labels_for_delivery(c, delivery_id)
    return d


def resolve_labels_for_delivery(c, delivery_id):
    """All labels of a delivery, in page order."""
    rows = c.execute(
        "SELECT * FROM labels WHERE delivery_id = ? ORDER BY page_no",
        (delivery_id,)).fetchall()
    return [dict(r) for r in rows]


def resolve_label_for_page(c, delivery_id, page_no):
    """The ONE label for one page — the domino lookup (c3)."""
    r = c.execute(
        "SELECT * FROM labels WHERE delivery_id = ? AND page_no = ?",
        (delivery_id, page_no)).fetchone()
    return dict(r) if r else None


def verify_chain(c):
    """Recompute every audit entry hash in order. Returns
    (ok, checked_count, first_bad_id_or_None)."""
    rows = c.execute("SELECT * FROM audit_log ORDER BY id").fetchall()
    prev = GENESIS_PREV_HASH
    for r in rows:
        if r["prev_hash"] != prev:
            return False, len(rows), r["id"]
        expect = digest({"prev_hash": r["prev_hash"], "event_id": r["event_id"],
                         "at": r["at"], "actor": r["actor"], "action": r["action"],
                         "subject_id": r["subject_id"],
                         "detail": json.loads(r["detail_json"])})
        if expect != r["entry_hash"]:
            return False, len(rows), r["id"]
        prev = r["entry_hash"]
    return True, len(rows), None


def verify_delivery(c, delivery_id):
    """Recompute a v1 single-page delivery_hash from the row's fields."""
    row = c.execute("SELECT * FROM deliveries WHERE id = ?", (delivery_id,)).fetchone()
    if row is None:
        return False, "delivery not found"
    expect = digest({
        "id": row["id"], "number": row["number"], "client": row["client"],
        "item": row["item"], "document_type": row["document_type"],
        "source_document": row["source_document"],
        "source_page": row["source_page"],
        "source_sha256": row["source_sha256"],
        "output_pdf_name": row["output_pdf_name"],
        "output_pdf_sha256": row["output_pdf_sha256"],
        "lse_version": row["lse_version"],
        "edited_fields": json.loads(row["edited_fields_json"]),
        "label_ref": row["label_ref"],
        "created_at": row["created_at"], "created_by": row["created_by"],
        "status": row["status"]})
    if expect != row["delivery_hash"]:
        return False, "delivery_hash mismatch"
    return True, "ok"


def verify_delivery3(c, delivery_id):
    """Recompute a v3 multi-page delivery_hash from row + pages + labels."""
    row = c.execute("SELECT * FROM deliveries WHERE id = ?", (delivery_id,)).fetchone()
    if row is None:
        return False, "delivery not found"
    pages = c.execute(
        "SELECT * FROM delivery_pages WHERE delivery_id = ? ORDER BY page_no",
        (delivery_id,)).fetchall()
    edits = c.execute(
        "SELECT * FROM lse_edits WHERE delivery_id = ? ORDER BY page, word_index",
        (delivery_id,)).fetchall()
    pages_h = []
    for p in pages:
        pe = [e for e in edits if e["page"] == p["source_page"]]
        ef = [{"row_label": e["row_label"], "box": json.loads(e["box_json"]),
               "old_text": e["old_text"], "new_text": e["new_text"],
               "font": e["font"], "font_size_px": e["font_size_px"]} for e in pe]
        pages_h.append({
            "page_no": p["page_no"], "source_page": p["source_page"],
            "source_document": p["source_document"],
            "source_sha256": p["source_sha256"],
            "output_pdf_name": p["output_pdf_name"],
            "page_pdf_sha256": p["page_pdf_sha256"],
            "edited_fields": ef})
    labels_list = _labels_list_v3(c, delivery_id)
    expect = _delivery_hash_v3(
        row["id"], row["number"],
        {"client": row["client"], "item": row["item"],
         "document_type": row["document_type"],
         "source_document": row["source_document"],
         "source_page": row["source_page"],
         "source_sha256": row["source_sha256"],
         "output_pdf_name": row["output_pdf_name"],
         "output_pdf_sha256": row["output_pdf_sha256"],
         "lse_version": row["lse_version"]},
        pages_h, labels_list, row["label_ref"],
        row["created_at"], row["created_by"])
    if expect != row["delivery_hash"]:
        return False, "delivery_hash mismatch (v3)"
    return True, "ok"
