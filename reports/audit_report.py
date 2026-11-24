"""Visual, typographic and structural QA audit of reports/Final-Project-Report.pdf."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "reports" / "Final-Project-Report.pdf"
MAP = ROOT / "reports" / "page_map.json"

MM = 72.0 / 25.4
MARGIN_L, MARGIN_R, MARGIN_T, MARGIN_B = 26, 20, 24, 20

ALLOWED_MONO = {"DejaVu-Sans-Mono", "DejaVu-Sans-Mono-Bold"}


def allowed(name: str) -> bool:
    """Faces we register ourselves (Times quartet) plus the mono face for code."""
    return (name.startswith("TNR_") or name.startswith("Times-New-Roman")
            or name in ALLOWED_MONO)


def norm_font(name: str) -> str:
    """Strip subset prefixes and style suffixes so faces can be grouped."""
    n = re.sub(r"^[A-Z]{6}\+", "", name)
    n = n.replace(" ", "").replace(",", "-")
    n = n.replace("TimesNewRomanCyr", "TimesNewRoman")
    return n


def main() -> int:
    doc = pymupdf.open(PDF)
    pm = json.loads(MAP.read_text())
    front_pages = pm["front_pages"]
    issues: list[str] = []
    report: dict = {}

    size_mb = PDF.stat().st_size / 1024 / 1024
    report["file"] = {"path": str(PDF.relative_to(ROOT)), "size_mb": round(size_mb, 3),
                      "pages": len(doc), "front_pages": front_pages,
                      "body_pages": len(doc) - front_pages}
    if size_mb > 10:
        issues.append(f"file size {size_mb:.2f} MB exceeds 10 MB")
    if size_mb > 8:
        issues.append(f"file size {size_mb:.2f} MB above the 8 MB target")

    # ---------------- page geometry ----------------
    geo = Counter()
    for p in doc:
        geo[(round(p.rect.width, 1), round(p.rect.height, 1))] += 1
    report["page_sizes"] = {f"{k[0]}x{k[1]}pt": v for k, v in geo.items()}
    a4 = [(595.3, 841.9), (595.0, 842.0), (595.28, 841.89)]
    if not all(min(abs(w - a[0]) for a in a4) < 1.5 and min(abs(h - a[1]) for a in a4) < 1.5
               for w, h in geo):
        issues.append(f"non-A4 page size present: {list(geo)}")

    # ---------------- fonts ----------------
    font_pages: dict[str, set[int]] = defaultdict(set)
    font_usage = Counter()
    for p in doc:
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if not s["text"].strip():
                        continue
                    f = norm_font(s["font"])
                    font_usage[f] += len(s["text"])
                    font_pages[f].add(p.number)
    report["fonts"] = {f: {"pages": len(pg), "chars": font_usage[f]}
                       for f, pg in sorted(font_pages.items())}
    unexpected = [f for f in font_pages if not allowed(f)]
    if unexpected:
        issues.append(f"unexpected fonts (fallback): {unexpected}")

    # mono usage should be confined to code listings
    mono_pages = sorted(font_pages.get("DejaVu-Sans-Mono", set())
                        | font_pages.get("DejaVu-Sans-Mono-Bold", set()))
    report["mono_pages"] = mono_pages

    # ---------------- overflows / clipping ----------------
    over = []
    for p in doc:
        W, H = p.rect.width, p.rect.height
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if not s["text"].strip():
                        continue
                    x0, y0, x1, y1 = s["bbox"]
                    if x1 > W - MARGIN_R * MM + 1.5 or x0 < MARGIN_L * MM - 2.0:
                        over.append({"page": p.number + 1, "text": s["text"][:60],
                                     "x0": round(x0, 1), "x1": round(x1, 1)})
                    if y1 > H - 8 * MM:
                        over.append({"page": p.number + 1, "text": s["text"][:60],
                                     "y1": round(y1, 1)})
    report["overflow_count"] = len(over)
    report["overflow_sample"] = over[:12]
    if over:
        issues.append(f"{len(over)} text spans cross the text frame")

    # ---------------- headings stranded at page foot ----------------
    stranded = []
    for p in doc:
        W, H = p.rect.width, p.rect.height
        spans = []
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if s["text"].strip():
                        spans.append(s)
        body = [s for s in spans if s["bbox"][1] > MARGIN_T * MM - 6]
        if not body:
            continue
        body.sort(key=lambda s: s["bbox"][1])
        last = body[-1]
        if last["size"] >= 12.5 and "Bold" in norm_font(last["font"]):
            stranded.append({"page": p.number + 1, "text": last["text"][:70],
                             "y": round(last["bbox"][1], 1)})
    report["stranded_headings"] = stranded
    if stranded:
        issues.append(f"{len(stranded)} heading(s) sitting alone at page bottom")

    # ---------------- images / logos ----------------
    img_info = Counter()
    for p in doc:
        for img in p.get_images(full=True):
            xref = img[0]
            info = doc.extract_image(xref)
            img_info[f"{info['width']}x{info['height']}"] += 1
    report["images"] = dict(img_info)

    figure_pages = sorted({fm_["page"] for fm_ in pm["figures"] if fm_["page"]})
    figs_with_drawings = []
    for f in pm["figures"]:
        pno = front_pages + f["page"] - 1
        if 0 <= pno < len(doc):
            page = doc[pno]
            n_draw = len(page.get_drawings())
            n_img = len(page.get_images(full=True))
            figs_with_drawings.append({"fig": f["label"], "page": pno + 1,
                                       "vector_ops": n_draw, "images": n_img})
    missing = [x for x in figs_with_drawings if x["vector_ops"] < 5 and x["images"] == 0]
    report["figure_presence"] = figs_with_drawings
    if missing:
        issues.append(f"{len(missing)} figure(s) appear empty on their page: "
                      f"{[m['fig'] for m in missing]}")

    # ---------------- TOC / LOF / LOT alignment ----------------
    def page_number_map(idx: int) -> dict[str, str]:
        """Parse 'label<tab/newline>number' pairs from a list page."""
        txt = doc[idx].get_text("text")
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        out = {}
        i = 0
        while i < len(lines) - 1:
            if re.fullmatch(r"\d{1,3}", lines[i + 1]):
                out[lines[i]] = lines[i + 1]
                i += 2
            else:
                i += 1
        return out

    toc_printed = page_number_map(front_pages - 4)   # TOC page = vi
    lof_printed = page_number_map(front_pages - 3)   # vii
    lot_printed = page_number_map(front_pages - 2)   # viii

    def compare(printed: dict, entries: list[dict], key_label: str) -> list[dict]:
        bad = []
        for e in entries:
            if e.get("page") is None:
                continue
            want = str(e["page"])
            got = printed.get(e["text"].strip())
            if got is None:
                # fuzzy: find printed key containing the text
                for k, v in printed.items():
                    if k.startswith(e["text"].strip()[:40]):
                        got = v
                        break
            if got is not None and got != want:
                bad.append({"entry": e["text"][:60], "printed": got, "actual": want})
        return bad

    toc_bad = compare(toc_printed, pm["toc"], "toc")
    lof_bad = compare(lof_printed, pm["figures"], "lof")
    lot_bad = compare(lot_printed, pm["tables"], "lot")
    report["toc_entries_parsed"] = len(toc_printed)
    report["toc_mismatches"] = toc_bad
    report["lof_mismatches"] = lof_bad
    report["lot_mismatches"] = lot_bad
    if toc_bad:
        issues.append(f"{len(toc_bad)} TOC page numbers disagree with the body")
    if lof_bad:
        issues.append(f"{len(lof_bad)} List-of-Figures page numbers disagree")
    if lot_bad:
        issues.append(f"{len(lot_bad)} List-of-Tables page numbers disagree")

    # ---------------- links & outline ----------------
    uri_links, internal = [], 0
    for p in doc:
        for l in p.get_links():
            if l["kind"] == pymupdf.LINK_URI:
                uri_links.append(l["uri"])
            elif l["kind"] == pymupdf.LINK_GOTO:
                internal += 1
    report["links"] = {"uri": sorted(set(uri_links)), "uri_count": len(uri_links),
                       "internal_goto": internal}
    if not uri_links:
        issues.append("no external URI links present")

    toc_outline = doc.get_toc(simple=True)
    report["outline_entries"] = len(toc_outline)
    report["outline_sample"] = toc_outline[:6]
    if len(toc_outline) < 20:
        issues.append("PDF outline is too small")
    bad_outline = [t for t in toc_outline if not (1 <= t[2] <= len(doc))]
    if bad_outline:
        issues.append(f"{len(bad_outline)} outline entries point outside the document")

    # ---------------- metadata ----------------
    report["metadata"] = {k: v for k, v in doc.metadata.items() if v}
    for key in ("title", "author", "subject", "keywords"):
        if not doc.metadata.get(key):
            issues.append(f"missing PDF metadata field: {key}")

    # ---------------- folio numbering ----------------
    folios = []
    for p in doc:
        spans = []
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if s["text"].strip():
                        spans.append(s)
        spans.sort(key=lambda s: s["bbox"][3])
        folios.append(spans[-1]["text"].strip() if spans else "")
    roman_ok = [folios[i] for i in range(1, front_pages)]
    expected_roman = ["ii", "iii", "iv", "v", "vi", "vii", "viii", "ix"][: front_pages - 1]
    report["roman_folios"] = roman_ok
    if roman_ok != expected_roman:
        issues.append(f"roman folios {roman_ok} != {expected_roman}")
    first_body_folio = folios[front_pages]
    if first_body_folio != "1":
        issues.append(f"first body folio is {first_body_folio!r}, expected '1'")

    # ---------------- page count sanity ----------------
    if len(doc) < 40:
        issues.append(f"document is only {len(doc)} pages")

    report["issues"] = issues
    report["status"] = "PASS" if not issues else "REVIEW"

    out = ROOT / "reports" / "audit_report.json"
    out.write_text(json.dumps(report, indent=1))

    print(json.dumps({k: report[k] for k in (
        "file", "page_sizes", "fonts", "overflow_count", "stranded_headings",
        "toc_mismatches", "lof_mismatches", "lot_mismatches", "links",
        "outline_entries", "roman_folios", "status")}, indent=1))
    print("\nISSUES:")
    for i in issues or ["none"]:
        print(" -", i)
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
