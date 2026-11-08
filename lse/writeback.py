"""Multi-page PDF write-back at native DPI (LSE Track C, v2.1 lineage).

Generalises the prototype's single-page native-300-DPI rebuild
(scan-paper/improve/round3/track-c/lse_writeback_300.py, build
``v2.1-300dpi``) to a WHOLE document:

STANDING LSE RULE (user, 2026-11-06): preserve the document's FULL
originality — whatever DPI the original has, work at that DPI. Never
downscale, never re-encode the background, never change the resolution.
This holds UNIVERSALLY: every document type, every DPI, every scan.

Design (this module):
  * UNTOUCHED pages are copied verbatim: ``insert_pdf`` copies the
    source page — including its image XObject streams — into the output
    document. Nothing is decoded or re-encoded. (Verified by test:
    image-stream SHA-256 identical, rendered pixels identical.)
  * EDITED pages are also copied verbatim first, then ONLY small overlay
    patches are drawn on top: each patch is the original native-DPI crop
    around one word box (+3 px), Telea-inpainted where the word was,
    Grain v2 restored, new word rendered in the Document DNA clone font.
    Nothing else on the page is touched.
  * No full-page re-encode anywhere: the background is never decoded
    and re-saved, the page is never downscaled, the resolution never
    changes. The only new raster data in the output PDF is the small
    edited-word patches.
  * Patch placement keeps the v2.1 fix: a 0.001 pt inset on the patch
    rect (without it MuPDF's float32 cm makes the device bbox 1 px too
    big and the patch renders stretched + blurred — measured in v2.1).
  * The output PDF also carries, per edited page, an UNEDITED audit copy
    of that page, a human-readable edit certificate, ``lse-edits.json``
    (the full edit list) and the original scan-image stream bytes
    verbatim (``lse-original-scan-p{n}.*``).

Geometry: seg boxes are NATIVE render coordinates — the working image
for a page is a fitz render of that page at its native DPI (image pixel
width / page width in inches), so no 200->300 affine is needed at all.
Placement ground truth stays the MEASURED ink bbox, as in v1/v2.1.

Caps (proposal B, DECISIONS.md): build_patch() NEVER squeezes or
shrinks caps. With caps_mode="strict" (default) a caps replacement
that does not fit its box raises CapsDoesNotFitError carrying the
lowercase suggestion; with caps_mode="suggest_lowercase" the suggestion
is rendered instead and recorded as such.
"""
import datetime
import hashlib
import io
import json
import os

import cv2
import fitz  # PyMuPDF
import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

LSE_VERSION = "LSE-EDITED v1"
BUILD_VERSION = "v2.1-300dpi-multipage"

LIB_SERIF_REG = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
LIB_SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"

PATCH_MARGIN_PX = 3      # == v1 ERASE_DILATE 2 px at 200 DPI, scaled x1.5
INPAINT_RADIUS = 6       # == v1 radius 4 at 200 DPI, scaled x1.5
INK_SEARCH_PX = 6        # neighbourhood around the mapped box when measuring ink
RECT_SHRINK_PT = 0.001   # patch rect inset (v2.1 fix — see module docstring)
WIDTH_FIT_TARGET = 0.97  # live-page fitWidth v6: aim at 97% of the box width
WIDTH_FIT_CLAMP = (0.75, 1.25)


class CapsDoesNotFitError(ValueError):
    """A caps replacement does not fit its word box (proposal B).

    Attributes: suggestion (lowercase form), width_px, box_w_px.
    The caller decides: render the suggestion, widen the box, or
    shorten the text. The engine never squeezes caps by itself.
    """


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def font_covers(font_path, text):
    """True if every character of text has a glyph in the font (fontTools cmap)."""
    cmap = TTFont(font_path).getBestCmap()
    return all(ord(ch) in cmap for ch in text)


def pick_font(text, bold, dna_regular=None, dna_bold=None):
    """DNA clone first (the document's own glyphs); whole-word fallback
    to weight-matched Liberation Serif if any character is missing from
    the clone, or when no DNA font path is given. Per-character mixed
    rendering is a future step, not done here."""
    dna = dna_bold if bold else dna_regular
    if dna and os.path.exists(dna) and font_covers(dna, text):
        return dna, ("Document DNA Bold" if bold else "Document DNA Regular")
    lib = LIB_SERIF_BOLD if bold else LIB_SERIF_REG
    return lib, ("Liberation Serif Bold" if bold else "Liberation Serif Regular")


def render_word_layer(text, font_path, fs_px, ink_rgb):
    """Render text on a transparent RGBA layer; return (layer, ink_bbox)
    where ink_bbox is the tight alpha bbox in layer coords."""
    font = ImageFont.truetype(font_path, size=int(round(fs_px)))
    layer = Image.new("RGBA", (1800, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ink = tuple(int(round(v)) for v in ink_rgb) + (255,)
    d.text((10, 10), text, font=font, fill=ink)
    alpha = np.array(layer.split()[3])
    ys, xs = np.where(alpha > 10)
    if len(xs) == 0:
        return layer, None
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    return layer, bbox


def fit_font_size(text, font_path, fs0, box_w):
    """Mirror live-page fitWidth v6: scale so the rendered width is 97% of
    the box width, clamped to [0.75, 1.25] x fs0. Returns (fs_used, width)."""
    font = ImageFont.truetype(font_path, size=int(round(fs0)))
    w0 = font.getlength(text)
    if w0 <= 0:
        return fs0, 0.0
    fs = fs0 * (WIDTH_FIT_TARGET * box_w) / w0
    fs = max(WIDTH_FIT_CLAMP[0] * fs0, min(WIDTH_FIT_CLAMP[1] * fs0, fs))
    font2 = ImageFont.truetype(font_path, size=int(round(fs)))
    return fs, font2.getlength(text)


def grain_v2(orig_bgr, result_bgr, mask, tile=16, ring=24, seed=7):
    """Per-region paper grain, Round 2 step 6a (copied from inpaint.py
    v4, patch-crop scale). Telea leaves patches too smooth; per-tile
    sigma from the tile's ring in the ORIGINAL restores the paper noise.
    Grey tiles and flat paper get none."""
    import numpy as _np
    _rng = _np.random.default_rng(seed)
    gray = cv2.cvtColor(orig_bgr, cv2.COLOR_BGR2GRAY)
    res = result_bgr.astype(_np.float32)
    h, w = gray.shape
    m = mask > 0
    for ty in range(0, h, tile):
        for tx in range(0, w, tile):
            th = min(tile, h - ty)
            tw = min(tile, w - tx)
            tmask = m[ty:ty + th, tx:tx + tw]
            if not tmask.any():
                continue
            rx0, ry0 = max(0, tx - ring), max(0, ty - ring)
            rx1, ry1 = min(w, tx + tile + ring), min(h, ty + tile + ring)
            ring_g = gray[ry0:ry1, rx0:rx1].astype(_np.float32)
            ring_m = mask[ry0:ry1, rx0:rx1] == 0
            if not ring_m.any() or float(_np.median(ring_g[ring_m])) < 220:
                continue
            paper = ring_g[ring_m]
            paper = paper[paper > 200]
            if len(paper) < 20:
                continue
            sig_paper = float(paper.std())
            if sig_paper < 0.5:
                continue
            res_gray_tile = cv2.cvtColor(
                result_bgr[ty:ty + th, tx:tx + tw],
                cv2.COLOR_BGR2GRAY).astype(_np.float32)
            sig_res = float(res_gray_tile[tmask].std()) if tmask.sum() > 5 else 0.0
            sig_add = float(_np.sqrt(max(0.0, sig_paper ** 2 - sig_res ** 2)))
            if sig_add < 0.5:
                continue
            p1, p99 = float(_np.percentile(paper, 1)), float(_np.percentile(paper, 99))
            noise = _rng.normal(0, sig_add, (th, tw)).astype(_np.float32)
            sub = res[ty:ty + th, tx:tx + tw]
            add = _np.zeros((th, tw, 1), _np.float32)
            add[:, :, 0] = noise
            sub2 = sub + add * tmask[..., None]
            lo = _np.full((th, tw, 1), p1, _np.float32)
            hi = _np.full((th, tw, 1), p99, _np.float32)
            sub2 = _np.where(tmask[..., None] > 0, _np.clip(sub2, lo, hi), sub)
            res[ty:ty + th, tx:tx + tw] = sub2
    return _np.clip(res, 0, 255).astype(_np.uint8)


def measure_ink_bbox(gray, box, search=INK_SEARCH_PX):
    """Tight ink bbox of the word at native DPI, measured in the ORIGINAL
    render. Connected components in a small search window around the box;
    long thin rules and oversize blobs are excluded (same filters as
    segment.py, scaled x1.5); only components overlapping the box count.
    Returns (bbox, touched_edge) or (None, False)."""
    h, w = gray.shape
    x0, y0, x1, y1 = box
    sx0, sy0 = max(0, x0 - search), max(0, y0 - search)
    sx1, sy1 = min(w, x1 + search), min(h, y1 + search)
    crop = gray[sy0:sy1, sx0:sx1]
    thr, _ = cv2.threshold(crop, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Otsu returns 0 on pure 1-bit (0/255) images — clamp to a usable range.
    thr = float(min(max(thr, 64), 210))
    ink = (crop < thr).astype(np.uint8)
    num, _labels, stats, _cent = cv2.connectedComponentsWithStats(ink, connectivity=8)
    kept = []
    for i in range(1, num):
        cx, cy, cw, ch, area = [int(v) for v in stats[i]]
        if area < 6:
            continue
        if (cw > 375 and ch < 9) or (ch > 180 and cw < 9):
            continue  # rule / line, not a glyph
        if cw > 900 or ch > 180:
            continue
        bx0, by0, bx1, by1 = sx0 + cx, sy0 + cy, sx0 + cx + cw, sy0 + cy + ch
        if bx1 < x0 - 1 or bx0 > x1 + 1 or by1 < y0 - 1 or by0 > y1 + 1:
            continue
        kept.append((bx0, by0, bx1, by1))
    if not kept:
        return None, False
    bbox = [min(k[0] for k in kept), min(k[1] for k in kept),
            max(k[2] for k in kept), max(k[3] for k in kept)]
    touched = (bbox[0] <= x0 + 1 or bbox[1] <= y0 + 1
               or bbox[2] >= x1 - 1 or bbox[3] >= y1 - 1)
    return bbox, touched


def build_patch(upright_rgb, gray, box, edit, dna_regular=None,
                dna_bold=None, caps_mode="strict"):
    """One edit patch at native DPI: original crop, Telea-inpaint the old
    word out, Grain v2, render the new word in DNA clone at the measured
    ink bbox. ``box`` is the word box in native render coordinates.
    Returns (patch PIL RGB, clean_patch PIL RGB, record).

    Caps (proposal B): when the replacement is all-caps and does not fit
    the box, caps_mode="strict" raises CapsDoesNotFitError (with the
    lowercase suggestion attached); caps_mode="suggest_lowercase"
    renders the suggestion instead and records caps_action.
    """
    from .caps import fit_caps
    x0, y0, x1, y1 = [int(v) for v in box]
    h, w = y1 - y0, x1 - x0
    bold = bool(edit.get("bold", False))
    px0, py0 = max(0, x0 - PATCH_MARGIN_PX), max(0, y0 - PATCH_MARGIN_PX)
    px1, py1 = min(upright_rgb.width, x1 + PATCH_MARGIN_PX), min(upright_rgb.height, y1 + PATCH_MARGIN_PX)
    crop_rgb = upright_rgb.crop((px0, py0, px1, py1))
    crop_gray = gray[py0:py1, px0:px1]
    mask = np.zeros(crop_gray.shape, dtype=np.uint8)
    mx0, my0 = x0 - px0, y0 - py0
    mx1, my1 = x1 - px0, y1 - py0
    mask[my0:my1, mx0:mx1] = (crop_gray[my0:my1, mx0:mx1] < 210).astype(np.uint8) * 255
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
    crop_bgr = cv2.cvtColor(np.array(crop_rgb), cv2.COLOR_RGB2BGR)
    clean_bgr = cv2.inpaint(crop_bgr, mask, INPAINT_RADIUS, cv2.INPAINT_TELEA)
    clean_bgr = grain_v2(crop_bgr, clean_bgr, mask)
    clean_patch = Image.fromarray(cv2.cvtColor(clean_bgr, cv2.COLOR_BGR2RGB))
    ink_rgb = [int(round(v)) for v in edit.get("ink_rgb") or [0, 0, 0]]
    orig_bbox, touched = measure_ink_bbox(gray, [x0, y0, x1, y1])
    if orig_bbox is None:
        raise ValueError(f"no ink found for edit {edit} at native box {[x0, y0, x1, y1]}")
    new_text = edit["new_text"]
    font_path, font_name = pick_font(new_text, bold, dna_regular, dna_bold)
    fs0 = round(h / 0.85, 1)
    # Caps rule (proposal B) is enforced on the FITTED size: the live
    # page fits the width to 97% of the box, clamped to [0.75, 1.25] x
    # fs0 — a caps word that only fits by shrinking its cap height
    # below fs0 is NOT a fit. So the caps check runs at fs0, before
    # width-fitting, and the fitted size may never go below fs0 for caps.
    caps_decision = fit_caps(new_text, font_path, fs0, w)
    caps_action = caps_decision["action"]
    if caps_decision["action"] == "suggest_lowercase" and caps_decision["suggestion"]:
        if caps_mode == "strict":
            err = CapsDoesNotFitError(
                f"caps {new_text!r} ({caps_decision['width_px']}px) does not "
                f"fit a {w}px box at {fs0}px; suggestion: "
                f"{caps_decision['suggestion']!r} — never squeezed, never shrunk")
            err.suggestion = caps_decision["suggestion"]
            err.width_px = caps_decision["width_px"]
            err.box_w_px = w
            raise err
        new_text = caps_decision["suggestion"]
        font_path, font_name = pick_font(new_text, bold, dna_regular, dna_bold)
    fs_used, rendered_w = fit_font_size(new_text, font_path, fs0, w)
    if caps_decision["action"] in ("caps", "caps_widened_slot") and fs_used < fs0:
        # A caps word must never be shrunk below its cap-height size to
        # fit: that is shrink-to-fit by another name (R18: cap height
        # 37 -> 19.4 px). Re-check at fs0 and refuse instead.
        fs_used, rendered_w = fs0, measure_width_at(new_text, font_path, fs0)
        if rendered_w > w:
            err = CapsDoesNotFitError(
                f"caps {new_text!r} ({rendered_w:.0f}px) does not fit a {w}px "
                f"box at cap-height size {fs0}px; suggestion: "
                f"{new_text.lower()!r}")
            err.suggestion = new_text.lower()
            err.width_px = rendered_w
            err.box_w_px = w
            raise err
    layer, ink_bbox = render_word_layer(new_text, font_path, fs_used, ink_rgb)
    if ink_bbox is None:
        raise ValueError(f"cannot render edit {edit}")
    page = clean_patch.copy()
    lx = orig_bbox[0] - px0 - ink_bbox[0]
    ly = orig_bbox[1] - py0 - ink_bbox[1]
    page.paste(layer, (lx, ly), layer)
    record = {
        "box": [x0, y0, x1, y1], "row_label": edit.get("row_label", ""),
        "line": edit.get("line"), "old_text": edit.get("old_text", ""),
        "new_text": new_text, "typed_text": edit["new_text"],
        "caps_action": caps_action, "bold": bold,
        "font": font_name, "font_file": os.path.basename(font_path),
        "font_size_px": fs_used, "font_size_fs0_px": fs0,
        "rendered_width_px": round(rendered_w, 2),
        "ink_rgb": ink_rgb,
        "orig_ink_bbox": list(orig_bbox),
        "ink_touched_mapped_box_edge": touched,
        "new_ink_bbox": [orig_bbox[0], orig_bbox[1],
                         orig_bbox[0] + (ink_bbox[2] - ink_bbox[0]),
                         orig_bbox[1] + (ink_bbox[3] - ink_bbox[1])],
        "patch_rect": [px0, py0, px1, py1],
        "erase_box": [x0, y0, x1, y1],
    }
    return page, clean_patch, record


def measure_width_at(text, font_path, fs_px):
    font = ImageFont.truetype(font_path, size=int(round(fs_px)))
    return float(font.getlength(text))


def composite_patches_for_page(upright_rgb, gray, edits, dna_regular=None,
                               dna_bold=None, caps_mode="strict"):
    """Build one overlay patch per edit at native DPI.
    Returns (patches, clean_patches, records) — PIL RGB images + records."""
    patches, cleans, records = [], [], []
    for e in edits:
        patch, clean, rec = build_patch(upright_rgb, gray, e["box"], e,
                                        dna_regular=dna_regular,
                                        dna_bold=dna_bold,
                                        caps_mode=caps_mode)
        patches.append(patch)
        cleans.append(clean)
        records.append(rec)
    return patches, cleans, records


# ---- source-document introspection (no modification, read-only) ----

def page_image_info(doc, pageno):
    """The page's images: [{xref, width, height, filter, stream_sha256,
    ext}]. ``ext`` is the verbatim-stream file suffix (jpg for
    DCTDecode, ccitt for CCITTFaxDecode, png otherwise)."""
    page = doc[pageno]
    out = []
    for img in page.get_images(full=True):
        xref = img[0]
        try:
            filt = doc.xref_get_key(xref, "Filter")
            filt = filt[1] if isinstance(filt, tuple) else str(filt)
        except Exception:
            filt = ""
        stream = doc.xref_stream(xref)
        if "DCTDecode" in filt:
            ext = "jpg"
        elif "CCITTFaxDecode" in filt:
            ext = "ccitt"
        else:
            ext = "png"
        out.append({"xref": xref, "width": img[2], "height": img[3],
                    "filter": filt, "stream_sha256": sha256_bytes(stream),
                    "ext": ext, "stream": stream})
    return out


def native_dpi(doc, pageno, default=300):
    """Native DPI of a page: its (first) image's pixel width / page width
    in inches. Falls back to ``default`` when the page has no image."""
    page = doc[pageno]
    w_pt = page.rect.width
    if w_pt <= 0:
        return default
    imgs = page_image_info(doc, pageno)
    if not imgs:
        return default
    return int(round(imgs[0]["width"] / (w_pt / 72.0)))


def render_page(doc, pageno, dpi=None):
    """Render one page at its native DPI (fitz honours the page's own
    rotation / image matrices, so the pixmap is upright as displayed).
    Returns (PIL RGB image, grayscale numpy array, dpi)."""
    if dpi is None:
        dpi = native_dpi(doc, pageno)
    page = doc[pageno]
    zoom = dpi / 72.0
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    gray = np.array(img.convert("L"))
    return img, gray, dpi


def display_to_page_point(x_d, y_d, page_w_pt, page_h_pt, rotation, zoom):
    """Map a point in DISPLAY (pixmap) coordinates to unrotated PDF page
    coordinates (points). The pixmap is the page as displayed (rotation
    applied); insert_image() takes unrotated page coordinates, so edited
    patches must be mapped back. rotation is the page's /Rotate (0/90/
    180/270, clockwise). zoom = dpi/72 of the render."""
    x_pt, y_pt = x_d / zoom, y_d / zoom
    if rotation == 0:
        return x_pt, y_pt
    if rotation == 90:
        return y_pt, page_h_pt - x_pt
    if rotation == 180:
        return page_w_pt - x_pt, page_h_pt - y_pt
    if rotation == 270:
        return page_w_pt - y_pt, x_pt
    raise ValueError(f"unsupported rotation {rotation}")


def build_edited_pdf(source_pdf_path, pages_edits, out_path, delivery_id,
                     source_label=None, actor="qc", created_at=None,
                     dna_regular=None, dna_bold=None, caps_mode="strict"):
    """Assemble the multi-page edited PDF.

    ``pages_edits``: {source_page_no (0-based): {"image": PIL RGB,
    "gray": numpy array, "dpi": int, "edits": [edit dicts]}} — only
    edited pages need entries; untouched pages are copied verbatim.
    Returns a manifest dict (hashes, sizes, per-page records).

    Output layout: [edited + untouched source pages, in order]
    + [one unedited audit copy per edited page] + [edit certificate].
    Attachments: lse-edits.json + verbatim original scan-image streams.
    """
    if created_at is None:
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    src = fitz.open(source_pdf_path)
    n_src = len(src)
    try:
        out = fitz.open()
        all_records = []       # (source_page_no, record)
        audit_pages = []       # source page numbers with edits
        attachments = {}
        for pageno in range(n_src):
            page = src[pageno]
            info = pages_edits.get(pageno)
            out.insert_pdf(src, from_page=pageno, to_page=pageno)
            new_page = out[len(out) - 1]
            if not info or not info["edits"]:
                continue
            audit_pages.append(pageno)
            patches, _cleans, records = composite_patches_for_page(
                info["image"], info["gray"], info["edits"],
                dna_regular=dna_regular, dna_bold=dna_bold,
                caps_mode=caps_mode)
            dpi = info["dpi"]
            zoom = dpi / 72.0
            rotation = page.rotation
            w_pt, h_pt = page.rect.width, page.rect.height
            for patch, rec in zip(patches, records):
                buf = io.BytesIO()
                patch.save(buf, format="PNG")
                x0, y0, x1, y1 = rec["patch_rect"]
                # patch corners in display coords -> unrotated page coords
                ax, ay = display_to_page_point(x0, y0, w_pt, h_pt, rotation, zoom)
                bx, by = display_to_page_point(x1, y1, w_pt, h_pt, rotation, zoom)
                rx0, ry0 = min(ax, bx), min(ay, by)
                rx1, ry1 = max(ax, bx), max(ay, by)
                r = fitz.Rect(rx0 + RECT_SHRINK_PT, ry0 + RECT_SHRINK_PT,
                              rx1 - RECT_SHRINK_PT, ry1 - RECT_SHRINK_PT)
                new_page.insert_image(r, stream=buf.getvalue())
                all_records.append((pageno, rec))
            mark = (f"{LSE_VERSION}  |  {len(records)} edit(s)  |  "
                    f"delivery {delivery_id}  |  see certificate")
            new_page.add_freetext_annot(
                fitz.Rect(w_pt - 265, 6, w_pt - 6, 26), mark,
                fontsize=8, fontname="helv", text_color=(0.62, 0, 0),
                fill_color=(1, 1, 1))
            # verbatim original scan-image stream(s) for this page
            for ii, im in enumerate(page_image_info(src, pageno)):
                key = f"lse-original-scan-p{pageno + 1}.{im['ext']}"
                if ii:
                    key = f"lse-original-scan-p{pageno + 1}-{ii}.{im['ext']}"
                attachments[key] = im["stream"]
        # ---- audit copies (unedited) ----
        for pageno in audit_pages:
            out.insert_pdf(src, from_page=pageno, to_page=pageno)
        # ---- certificate ----
        w_pt = max((src[i].rect.width for i in range(n_src)), default=595.0)
        h_pt = max((src[i].rect.height for i in range(n_src)), default=842.0)
        cert = out.new_page(width=w_pt, height=h_pt)
        label = source_label or os.path.basename(source_pdf_path)
        src_sha = sha256_file(source_pdf_path)
        lines = [
            "LSE - Live-Scan Editing  |  EDIT CERTIFICATE",
            "",
            f"Version: {LSE_VERSION}",
            f"Build: {BUILD_VERSION} (native-DPI multi-page write-back)",
            f"Delivery: {delivery_id}",
            f"Source document: {label}",
            f"Source PDF SHA-256: {src_sha}",
            f"Source pages: {n_src} (edited: "
            f"{sorted(p + 1 for p in audit_pages) or 'none'}; "
            f"untouched pages copied verbatim, byte-identical)",
            f"Edited by: {actor}   |   Edited at (UTC): {created_at}",
            "Working resolution: native DPI per page (no downscale, no "
            "re-encode of the background; the original scan bytes are "
            "the page background).",
            f"Edits: {len(all_records)}",
            "",
        ]
        for pageno, r in all_records:
            lines.append(
                f"p.{pageno + 1} [{r['row_label']}] box {r['box']}: "
                f"'{r['old_text']}' -> '{r['new_text']}'"
                + (f" (typed {r['typed_text']!r}, caps: {r['caps_action']})"
                   if r['typed_text'] != r['new_text'] else "")
                + f"  ({r['font']}, {r['font_size_px']} px, ink {r['ink_rgb']})")
        lines += [
            "",
            "The edited pages are the source pages with only small overlay",
            "patches where words were retyped. The audit copies after them",
            "show the ORIGINAL pages. The original scan-image bytes are",
            "embedded in this PDF verbatim (lse-original-scan-p*. *), and",
            "the same edit list is embedded as lse-edits.json and recorded",
            "in the database with a hash-chained audit log.",
            "",
            "Honest limits: for JPEG sources, different JPEG decoders",
            "render the same bytes with tiny differences (measured on the",
            "prototype: MuPDF vs PIL differ on ~5.7% of pixels, mean 0.09,",
            "max 34 — almost all by 1-2 levels). The PDF carries the",
            "original JPEG bytes unchanged. Patches are placed",
            "pixel-aligned (0.001 pt inset avoids a float-rounding",
            "stretch). Print calibration on paper is still open (factory",
            "test print).",
        ]
        cert.insert_textbox(fitz.Rect(48, 48, w_pt - 48, h_pt - 48),
                            "\n".join(lines), fontsize=10.5, fontname="helv",
                            color=(0, 0, 0))
        # ---- attachments + metadata ----
        attachment = {
            "lse_version": LSE_VERSION, "build": BUILD_VERSION,
            "delivery_id": delivery_id,
            "source_document": label, "source_pdf_sha256": src_sha,
            "source_pages": n_src,
            "edited_pages": sorted(p + 1 for p in audit_pages),
            "actor": actor, "created_at_utc": created_at,
            "edits": [{"page": p + 1, **r} for p, r in all_records],
        }
        att_bytes = json.dumps(attachment, ensure_ascii=False, sort_keys=True,
                               indent=2).encode("utf-8")
        out.embfile_add("lse-edits.json", att_bytes,
                        filename="lse-edits.json",
                        desc="LSE edit list for this delivery (JSON)")
        for name, stream in attachments.items():
            out.embfile_add(name, stream, filename=name,
                            desc="Original scan-image stream, byte-identical")
        out.set_metadata({
            "title": f"{LSE_VERSION} - {label} (edited, {BUILD_VERSION})",
            "author": "GRAVORA LSE",
            "subject": f"Edited scan document at native DPI; original kept as audit copy; delivery {delivery_id}",
            "keywords": f"LSE, Live-Scan Editing, {LSE_VERSION}, {BUILD_VERSION}, {delivery_id}",
            "creator": f"GRAVORA LSE - lse.writeback ({BUILD_VERSION}, PyMuPDF)",
            "producer": f"PyMuPDF {fitz.__version__}",
            "creationDate": "D:" + created_at.replace("-", "").replace(":", "").replace("T", "")[:14] + "+06'00'",
            "modDate": "D:" + created_at.replace("-", "").replace(":", "").replace("T", "")[:14] + "+06'00'",
        })
        out.save(out_path, garbage=4, deflate=True)
        n_out = len(out)
        out.close()
    finally:
        src.close()
    pdf_sha = sha256_file(out_path)
    return {
        "pdf_path": out_path, "pdf_sha256": pdf_sha,
        "pdf_bytes": os.path.getsize(out_path),
        "pages": n_out, "source_pages": n_src,
        "edited_pages": sorted(p + 1 for p in audit_pages),
        "audit_pages": len(audit_pages),
        "source_pdf_sha256": src_sha,
        "attachment_sha256": sha256_bytes(att_bytes),
        "created_at_utc": created_at, "lse_version": LSE_VERSION,
        "build": BUILD_VERSION,
        "edits": [{"page": p + 1, **r} for p, r in all_records],
    }
