"""Build the final IILM mini-project report PDF.

Pipeline
--------
1.  Assemble the body (Chapters 1-8, references, appendices) as HTML.
2.  Render it with WeasyPrint; harvest the page number of every anchored element.
3.  Assemble the front matter (title, certificate, declaration, acknowledgement,
    abstract, TOC, list of figures, list of tables, abbreviations) using the
    page numbers harvested in step 2, and render it as its own document so that
    it carries lower-roman folios while the body carries arabic ones.
4.  Merge both documents with PyMuPDF, re-create the cross-document TOC links,
    write the PDF outline, metadata, and save the final PDF.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, HERE.as_posix())

from weasyprint import CSS, HTML  # noqa: E402
from weasyprint.text.fonts import FontConfiguration  # noqa: E402

import report_lib as L  # noqa: E402
import front_matter as FM  # noqa: E402
import content_a as A  # noqa: E402
import content_b as B  # noqa: E402

OUT_PDF = ROOT / "reports" / "Final-Project-Report.pdf"
TMP_FM = Path("/tmp/report_front.pdf")
TMP_BODY = Path("/tmp/report_body.pdf")
TMP_HTML = Path("/tmp/report_body.html")


# ---------------------------------------------------------------------------
def load_metrics() -> dict:
    res = json.loads((ROOT / "data" / "Analysis-Results.json").read_text())
    spec = importlib.util.spec_from_file_location(
        "easp", ROOT / "code" / "Energy-Analysis-Script.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["easp"] = mod
    spec.loader.exec_module(mod)
    df, meta, prep = mod.load_and_preprocess()

    areas = dict(zip(meta["building_id"], meta["sqm"]))
    bldg = {
        "bldg_cols": list(mod.BLDG_COLS),
        "areas": {k: float(v) for k, v in areas.items()},
        "bldg_sum_mwh": {c: round(float(df[c].sum()) / 1000.0, 1) for c in mod.BLDG_COLS},
        "bldg_mean": {c: round(float(df[c].mean()), 2) for c in mod.BLDG_COLS},
        "bldg_share_pct": {c: round(float(df[c].sum()) / float(df[mod.BLDG_COLS].sum().sum()) * 100, 2)
                           for c in mod.BLDG_COLS},
        "bldg_eui": {c: round(float(df[c].sum()) / 2.0 / areas[c], 1) for c in mod.BLDG_COLS},
        "bldg_weekday_mean": {c: round(float(df.loc[df.is_weekend == 0, c].mean()), 1)
                              for c in mod.BLDG_COLS},
        "bldg_weekend_mean": {c: round(float(df.loc[df.is_weekend == 1, c].mean()), 1)
                              for c in mod.BLDG_COLS},
        "bldg_offhour_mean": {c: round(float(df.loc[df.is_off_hour == 1, c].mean()), 1)
                              for c in mod.BLDG_COLS},
        "bldg_missing": {c: int(pd.read_csv(ROOT / "data" / "dataset.csv")[c].isna().sum())
                         for c in mod.BLDG_COLS},
    }
    season_hours = df.groupby("season").size().to_dict()
    return {"stats": res["statistics"], "ml": res["machine_learning"],
            "prep": prep, "bldg": bldg, "season_hours": season_hours}


# ---------------------------------------------------------------------------
def build_body(R: L.Registry, M: dict) -> str:
    parts = [
        A.chapter1(R, M), A.chapter2(R, M), A.chapter3(R, M), A.chapter4(R, M),
        B.chapter5(R, M), B.chapter6(R, M), B.chapter7(R, M), B.chapter8(R, M),
        B.references_section(),
        B.appendix_a(R, M), B.appendix_b(), B.appendix_c(R),
    ]
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>{L.TITLE_PLAIN}</title></head>
<body>{''.join(parts)}</body></html>"""


def page_map(doc) -> dict[str, int]:
    out = {}
    for i, page in enumerate(doc.pages):
        for anchor in page.anchors:
            out.setdefault(anchor, i + 1)
    return out


def anchors_rects(doc) -> dict[str, tuple]:
    out = {}
    for i, page in enumerate(doc.pages):
        for name, box in page.anchors.items():
            out[name] = (i, box)
    return out


H1_RE = re.compile(
    r'<h1 class="ch" id="([^"]+)"><span class="cn">([^<]*)</span>'
    r'<span class="chtitle">([^<]*)</span></h1>')
H2_RE = re.compile(r'<h2 id="([^"]+)">(.*?)</h2>', re.S)


def _clean(t: str) -> str:
    t = re.sub(r"<[^>]+>", "", t)
    t = (t.replace("&amp;", "&").replace("&#8212;", "-").replace("&#8211;", "-")
          .replace("&lt;", "<").replace("&gt;", ">").replace("&#183;", "\u00b7"))
    return " ".join(t.split())


def harvest_headings(html: str) -> list[dict]:
    """Return heading records in document order (chapters interleaved with sections)."""
    combined = re.compile(
        r'<h1 class="ch" id="([^"]+)"><span class="cn">([^<]*)</span>'
        r'<span class="chtitle">([^<]*)</span></h1>'
        r'|<h2 id="([^"]+)">(.*?)</h2>', re.S)
    entries = []
    for m in combined.finditer(html):
        if m.group(1):
            anchor, cn, title = m.group(1), _clean(m.group(2)), _clean(m.group(3))
            label = cn if cn == "References" else f"{cn}: {title}"
            entries.append({"level": 1, "anchor": anchor, "label": label, "text": title})
        else:
            entries.append({"level": 2, "anchor": m.group(4), "label": _clean(m.group(5)),
                            "text": _clean(m.group(5))})
    return entries


# ---------------------------------------------------------------------------
def main() -> None:
    M = load_metrics()
    R = L.Registry()
    body_html = build_body(R, M)
    TMP_HTML.write_text(body_html, encoding="utf-8")

    css = L.build_css()
    fc = FontConfiguration()
    body_doc = HTML(string=body_html, base_url=ROOT.as_posix()).render(
        stylesheets=[CSS(string=css, font_config=fc)], font_config=fc)
    body_doc.write_pdf(TMP_BODY)
    bmap = page_map(body_doc)
    print(f"body pages: {len(body_doc.pages)}")

    # ---- front matter content -------------------------------------------
    heads = harvest_headings(body_html)
    toc = [{"level": h["level"], "text": h["label"], "anchor": h["anchor"],
            "page": bmap.get(h["anchor"])} for h in heads
           if not h["anchor"].startswith(("sA-", "sC-"))]

    contents_html, toc_links = FM.contents_page(toc)

    fig_entries = [{"id": f["id"], "label": f"Figure {f['num']}", "text": f["caption"],
                    "page": bmap.get(f["id"])} for f in R.figures]
    tab_entries = [{"id": t["id"], "label": f"Table {t['num']}", "text": t["caption"],
                    "page": bmap.get(t["id"])} for t in R.tables]
    lof_html, lof_links = FM.list_page("List of Figures", fig_entries, "lof")
    lot_html, lot_links = FM.list_page("List of Tables", tab_entries, "lot")

    fm_html = (FM.cover_page() + FM.certificate_page() + FM.declaration_page()
               + FM.acknowledgement_page() + FM.abstract_page() + contents_html
               + lof_html + lot_html + FM.abbreviations_page())
    fm_html = fm_html.replace('<section class="fm">',
                              '<section class="fm" style="break-before:page">')
    fm_html = (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
               f'<title>{L.TITLE_PLAIN}</title></head><body>{fm_html}</body></html>')

    fm_doc = HTML(string=fm_html, base_url=ROOT.as_posix()).render(
        stylesheets=[CSS(string=css, font_config=fc)], font_config=fc)
    fm_doc.write_pdf(TMP_FM)
    fm_pages = len(fm_doc.pages)
    print(f"front matter pages: {fm_pages}")
    if fm_pages != 9:
        print("WARNING: front matter is not 9 pages (expected roman i-ix)")

    fm_rects = anchors_rects(fm_doc)

    # ---- merge -----------------------------------------------------------
    import fitz  # PyMuPDF

    merged = fitz.open()
    front = fitz.open(TMP_FM)
    body = fitz.open(TMP_BODY)
    merged.insert_pdf(front)
    merged.insert_pdf(body)

    # cross-document TOC links (front-matter rows -> body pages)
    link_count = 0
    for rid, target in (toc_links + lof_links + lot_links):
        if rid not in fm_rects or target not in bmap:
            continue
        fpage, box = fm_rects[rid]
        rect = fitz.Rect(box[0], box[1], box[2], box[3])
        merged[fpage].insert_link({
            "kind": fitz.LINK_GOTO,
            "from": rect,
            "page": fm_pages + bmap[target] - 1,
            "to": fitz.Point(0, 0),
        })
        link_count += 1
    print(f"internal TOC links restored: {link_count}")

    # ---- outline ---------------------------------------------------------
    outline = [[1, "Title Page", 1], [1, "Certificate", 2], [1, "Declaration", 3],
               [1, "Acknowledgement", 4], [1, "Abstract", 5],
               [1, "Table of Contents", 6], [1, "List of Figures", 7],
               [1, "List of Tables", 8], [1, "List of Abbreviations", 9]]
    for h in heads:
        if h["anchor"] not in bmap:
            continue
        pg = fm_pages + bmap[h["anchor"]]
        if h["level"] == 1:
            outline.append([1, h["label"], pg])
        elif h["level"] == 2:
            outline.append([2, h["label"], pg])
    merged.set_toc(outline)
    print(f"outline entries: {len(outline)}")

    meta = {
        "title": L.TITLE_PLAIN,
        "author": "; ".join(f"{n} ({r})" for n, r, _ in L.TEAM),
        "subject": (f"Mini Project Report - {L.COURSE} {L.COURSE_NAME}, "
                    f"B.Tech CSE Semester III, {L.UNIVERSITY}, {L.ACADEMIC_YEAR}"),
        "keywords": ("smart meter analytics, building energy wastage, anomaly detection, "
                     "one-class SVM, K-Means, multiple linear regression, data visualization, "
                     "sustainability, IILM University"),
        "creator": "WeasyPrint 6x (HTML/CSS to PDF) + PyMuPDF",
        "producer": "WeasyPrint / PyMuPDF",
        "creationDate": "D:20261125090000+05'30'",
        "modDate": "D:20261125090000+05'30'",
    }
    merged.set_metadata(meta)
    merged.save(OUT_PDF, garbage=4, deflate=True, clean=True)
    merged.close()
    front.close()
    body.close()

    size_mb = OUT_PDF.stat().st_size / 1024 / 1024
    print(f"written: {OUT_PDF}  ({size_mb:.2f} MB, {fm_pages + len(body_doc.pages)} pages)")

    # persist the page map for the audit script
    (HERE / "page_map.json").write_text(json.dumps(
        {"front_pages": fm_pages, "body_pages": len(body_doc.pages),
         "toc": [{**t, "body_page": t["page"]} for t in toc],
         "figures": fig_entries, "tables": tab_entries}, indent=1))


if __name__ == "__main__":
    main()
