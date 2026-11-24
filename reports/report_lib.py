"""Shared layout, styling and content primitives for the IILM mini-project report.

All prose and tables in this module are rendered through WeasyPrint with the four
user-supplied Times New Roman TrueType faces embedded as distinct @font-face rules
(TNR_Reg / TNR_Bold / TNR_Ital / TNR_BI) so that the legacy 8-bit character maps do
not collide.  Any glyph absent from those maps is expressed with HTML markup
(e.g. <sup>2</sup>) instead of a raw Unicode symbol to guarantee zero font fallback.
"""

from __future__ import annotations

import html as _html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"

COURSE = "26CSEM321"
COURSE_NAME = "Data Visualization and Analysis"
UNIVERSITY = "IILM University, Greater Noida"
DEPARTMENT = "School of Computer Science and Engineering"
SECTION = "2CSE-4"
ACADEMIC_YEAR = "2026-27"
FACULTY = "Aditya Bangia"
PROJECT_TITLE = ("Smart Building Energy Wastage &amp; Anomaly Profiling: "
                 "A Data-Driven Approach Using Smart-Meter and Weather Data")
TITLE_PLAIN = ("Smart Building Energy Wastage & Anomaly Profiling: "
               "A Data-Driven Approach Using Smart-Meter and Weather Data")
LIVE_SITE = "https://smart-building-energy-profiling.vercel.app"
DRIVE_FOLDER = ("https://drive.google.com/drive/folders/"
                "11nythpv22YAKNrwq1X8lfrp4Fq-hj01C")

TEAM = [
    ("Ayush Jha", "25SCS1003001336", "Team Lead, Data Engineering &amp; Reporting"),
    ("Archit Baloni", "25SCS1003003550", "Statistical Analysis &amp; Hypothesis Testing"),
    ("Ashutosh Sahoo", "25SCS1003004011", "Machine Learning &amp; Anomaly Detection"),
    ("Dev Bhaskar Singh", "25SCS1003003174", "Visualization Engineering &amp; Web Application"),
    ("Aman Kumar Gupta", "25SCS1003003645", "Literature Review, Validation &amp; QA"),
]


# ---------------------------------------------------------------------------
# Registry: figures / tables get numbered here while the body is assembled.
# ---------------------------------------------------------------------------
class Registry:
    def __init__(self) -> None:
        self.figures: list[dict] = []
        self.tables: list[dict] = []

    def figure(self, num: str, key: str, caption: str, path: Path,
               width: str = "100%", max_height: str | None = None) -> str:
        fid = "fig-" + num.replace(".", "-")
        self.figures.append({"num": num, "id": fid, "caption": caption, "key": key})
        style = f"width:{width};"
        if max_height:
            style += f"max-height:{max_height};"
        rel = path.relative_to(ROOT).as_posix()
        return f"""
        <figure class="fig" id="{fid}">
          <img src="{rel}" style="{style}" alt="{_html.escape(caption)}">
          <figcaption><span class="fignum">Figure {num}</span> &nbsp;{caption}</figcaption>
        </figure>"""

    def table(self, num: str, caption: str, headers: list[str], rows: list[list[str]],
              colw: list[str] | None = None, align: list[str] | None = None,
              note: str | None = None, cls: str = "data") -> str:
        tid = "tbl-" + num.replace(".", "-")
        self.tables.append({"num": num, "id": tid, "caption": caption})
        colgroup = ""
        if colw:
            colgroup = "<colgroup>" + "".join(
                f'<col style="width:{w}">' for w in colw) + "</colgroup>"
        align = align or ["left"] * len(headers)
        thead = "".join(f'<th class="{align[i]}">{h}</th>' for i, h in enumerate(headers))
        body = []
        for r in rows:
            cells = "".join(
                f'<td class="{align[i]}">{c}</td>' for i, c in enumerate(r))
            body.append(f"<tr>{cells}</tr>")
        note_html = f'<div class="tnote">{note}</div>' if note else ""
        return f"""
        <div class="tblock" id="{tid}">
          <div class="tcap"><span class="fignum">Table {num}</span> &nbsp;{caption}</div>
          <table class="{cls}">{colgroup}<thead><tr>{thead}</tr></thead>
          <tbody>{''.join(body)}</tbody></table>{note_html}
        </div>"""


def keyfinding(title: str, body: str) -> str:
    return f'<div class="callout"><div class="cotitle">{title}</div>{body}</div>'


def decision(title: str, body: str) -> str:
    return f'<div class="decision"><div class="cotitle">{title}</div>{body}</div>'


# ---------------------------------------------------------------------------
# Stylesheet
# ---------------------------------------------------------------------------
def build_css() -> str:
    reg = (FONT_DIR / "TimesNewRoman.ttf").as_posix()
    bold = (FONT_DIR / "TimesNewRoman-Bold.ttf").as_posix()
    ital = (FONT_DIR / "TimesNewRoman-Italic.ttf").as_posix()
    bi = (FONT_DIR / "TimesNewRoman-BoldItalic.ttf").as_posix()
    return f"""
@font-face {{ font-family: TNR_Reg;  src: url("file://{reg}");  font-weight: normal; font-style: normal; }}
@font-face {{ font-family: TNR_Bold; src: url("file://{bold}"); font-weight: bold;   font-style: normal; }}
@font-face {{ font-family: TNR_Ital; src: url("file://{ital}"); font-weight: normal; font-style: italic; }}
@font-face {{ font-family: TNR_BI;   src: url("file://{bi}");   font-weight: bold;   font-style: italic; }}

/* The Matplotlib SVGs name their text in the internal family of the supplied
   TrueType file; register the same quartet under those names so that vector
   figure labels use the real faces instead of a synthesised oblique. */
@font-face {{ font-family: "Times New Roman Cyr"; src: url("file://{reg}");  font-style: normal; font-weight: normal; }}
@font-face {{ font-family: "Times New Roman Cyr"; src: url("file://{bold}"); font-style: normal; font-weight: bold; }}
@font-face {{ font-family: "Times New Roman Cyr"; src: url("file://{ital}"); font-style: italic; font-weight: normal; }}
@font-face {{ font-family: "Times New Roman Cyr"; src: url("file://{bi}");   font-style: italic; font-weight: bold; }}
@font-face {{ font-family: "Times New Roman";     src: url("file://{reg}");  font-style: normal; font-weight: normal; }}
@font-face {{ font-family: "Times New Roman";     src: url("file://{bold}"); font-style: normal; font-weight: bold; }}
@font-face {{ font-family: "Times New Roman";     src: url("file://{ital}"); font-style: italic; font-weight: normal; }}
@font-face {{ font-family: "Times New Roman";     src: url("file://{bi}");   font-style: italic; font-weight: bold; }}

:root {{ --navy: #0B1F3A; --ink: #000000; --rule: #B8C4D4; --zebra: #F2F5F9;
         --blue: #0000FF; --red: #CC0000; --green: #1F7A1F; --muted: #555555; }}

@page {{
  size: A4;
  margin: 24mm 20mm 20mm 26mm;
  @top-right {{ content: string(chapno) ": " string(runhead); font-family: TNR_Ital;
                font-size: 8.6pt;
                color: #555; margin-bottom: 2mm; }}
  @bottom-center {{ content: counter(page); font-family: TNR_Reg; font-size: 9.5pt;
                    color: #000; }}
  @top-left {{ content: "{COURSE} Mini Project 2026-27"; font-family: TNR_Reg;
               font-size: 7.8pt; color: #666; }}
}}
@page fm-first {{ @top-right {{ content: none; }} @top-left {{ content: none; }}
                 @bottom-center {{ content: none; }} }}

@page frontmatter {{
  @top-right {{ content: none; }}
  @top-left {{ content: none; }}
  @bottom-center {{ content: counter(page, lower-roman); font-family: TNR_Reg;
                    font-size: 9.5pt; }}
}}


html {{ font-family: TNR_Reg; font-size: 11pt; color: #000; }}
body {{ margin: 0; line-height: 1.42; text-align: justify; hyphens: auto;
        hyphenate-character: "-"; }}

/* ---------------- front matter ---------------- */
section.fm {{ page: frontmatter; }}
section.fm.first {{ page: fm-first; }}
.fm h1 {{ font-family: TNR_Bold; font-size: 15.5pt; letter-spacing: .04em;
          text-transform: uppercase; text-align: center; color: #000;
          margin: 0 0 5.5mm 0; padding-bottom: 2.4mm;
          border-bottom: 0.9pt solid #0B1F3A; }}
.fm h2 {{ font-family: TNR_Bold; font-size: 12pt; color: #0B1F3A; margin: 6mm 0 2mm; }}
.fm p {{ margin: 0 0 3.2mm; }}
.small {{ font-size: 9.6pt; }}
.center {{ text-align: center; }}
.eyebrow {{ font-family: TNR_Bold; font-size: 9pt; letter-spacing: .22em;
            text-transform: uppercase; color: #445; text-align: center; }}

/* ---------------- cover ---------------- */
.cover {{ text-align: center; }}
.cover .logo {{ width: 34mm; margin: 0 auto 4mm; display: block; }}
.cover .uni {{ font-family: TNR_Bold; font-size: 17pt; color: #0B1F3A;
               letter-spacing: .03em; margin: 0; }}
.cover .dept {{ font-size: 11pt; margin: 1.5mm 0 0; color: #222; }}
.cover .rule {{ border-top: 0.9pt solid #0B1F3A; border-bottom: 0.4pt solid #0B1F3A;
                height: 1.6mm; margin: 5mm 0 6mm; }}
.cover .kicker {{ font-size: 10pt; letter-spacing: .3em; text-transform: uppercase;
                  color: #444; margin-bottom: 3mm; }}
.cover .title {{ font-family: TNR_Bold; font-size: 20pt; line-height: 1.24;
                 color: #0B1F3A; margin: 0 0 4mm; hyphens: manual;
                 text-wrap: balance; }}
.cover .subtitle {{ font-family: TNR_Ital; font-size: 11.6pt; color: #222;
                    margin: 0 0 6mm; }}
.cover .submitline {{ font-size: 9.9pt; margin: 0 0 4mm; hyphens: manual; }}
.cover .metatable {{ width: 100%; border-collapse: collapse; font-size: 9.6pt;
                     margin: 2mm 0 0; }}
.cover .metatable td {{ border: 0.5pt solid #B8C4D4; padding: 1.6mm 2.4mm; }}
.cover .metatable td.k {{ background: #EEF2F8; font-family: TNR_Bold; width: 30%;
                          text-align: left; }}
.cover .metatable td.v {{ text-align: left; }}
.cover .footerline {{ margin-top: 5mm; font-size: 9.6pt; color: #222; }}

/* ---------------- signature blocks ---------------- */
table.sign {{ width: 100%; border-collapse: collapse; font-size: 9.6pt;
              margin: 6mm 0 0; }}
table.sign td {{ padding: 2.4mm 1.6mm; vertical-align: bottom; }}
table.sign td.line {{ border-bottom: 0.6pt solid #000; height: 12mm; }}
.sigcap {{ font-size: 9.2pt; color: #222; }}

/* dotted leader rows (TOC / LOF / LOT) */
.row {{ display: flex; align-items: baseline; gap: 0; margin: 0; }}
.row .t {{ flex: 0 1 auto; min-width: 0; padding-right: 1.5mm; }}
.row .lead {{ flex: 1 1 8mm; min-width: 4mm; border-bottom: 0.55pt dotted #8A94A6;
              margin: 0 1.6mm; position: relative; top: -1.1mm; }}
.row .p {{ flex: none; font-family: TNR_Reg; }}
.toc-l1 {{ font-family: TNR_Bold; font-size: 9.3pt; margin: 1.3mm 0 0.3mm; }}
.toc-l2 {{ font-size: 8.5pt; margin-left: 5mm; line-height: 1.0; }}
.toc-l1 .row, .toc-l1 {{ color: #0B1F3A; }}
.lof-row {{ font-size: 9.1pt; line-height: 1.2; }}
.lof-row .t {{ font-family: TNR_Reg; }}

section.fm.abstractpage {{ font-size: 9.85pt; line-height: 1.33; }}
section.fm.abstractpage p {{ margin-bottom: 2.1mm; }}

/* ---------------- body typography ---------------- */
h1.ch {{ font-family: TNR_Bold; font-size: 16.6pt; color: #0B1F3A; text-align: left;
         margin: 0 0 5mm; padding: 0 0 2.4mm; border-bottom: 1.1pt solid #0B1F3A;
         break-before: page; page-break-after: avoid; }}
h1.ch .chtitle {{ string-set: runhead content(); }}
h1.ch .cn {{ string-set: chapno content(); display: block; font-size: 9pt; letter-spacing: .28em; color: #6A7A90;
             text-transform: uppercase; margin-bottom: 1.6mm; font-family: TNR_Bold; }}
h2 {{ font-family: TNR_Bold; font-size: 12.8pt; color: #0B1F3A;
      margin: 6.5mm 0 2.2mm; page-break-after: avoid; text-align: left; }}
h3 {{ font-family: TNR_Bold; font-size: 11.2pt; color: #14213D;
      margin: 4.6mm 0 1.6mm; page-break-after: avoid; text-align: left; }}
h4 {{ font-family: TNR_BI; font-size: 10.6pt; margin: 3.6mm 0 1.2mm;
      page-break-after: avoid; text-align: left; }}
p {{ margin: 0 0 2.7mm; orphans: 2; widows: 2; }}
ul, ol {{ margin: 0 0 3mm 0; padding-left: 6.5mm; }}
li {{ margin-bottom: 1.2mm; }}
strong {{ font-family: TNR_Bold; font-weight: normal; }}
em {{ font-family: TNR_Ital; font-style: normal; }}
sup {{ font-size: 70%; vertical-align: super; line-height: 0; }}
sub {{ font-size: 70%; vertical-align: sub; line-height: 0; }}
.eq {{ font-family: TNR_Ital; text-align: center; margin: 3.4mm 0 3.4mm;
        font-size: 11pt; position: relative; padding-right: 12mm; }}
.eq .n {{ position: absolute; right: 0; top: 0; font-family: TNR_Reg;
          font-style: normal; }}
a {{ color: #0000CC; text-decoration: none; }}

/* ---------------- figures ---------------- */
figure.fig {{ margin: 4mm 0 4.6mm; page-break-inside: avoid; text-align: center; }}
figure.fig img {{ display: block; margin: 0 auto; }}
figcaption {{ font-size: 9.4pt; line-height: 1.34; text-align: center;
              margin-top: 2mm; color: #111; }}
.fignum {{ font-family: TNR_Bold; color: #0B1F3A; }}

/* ---------------- tables ---------------- */
.tblock {{ margin: 4mm 0 5mm; page-break-inside: avoid; }}
.tcap {{ font-size: 9.4pt; text-align: left; margin-bottom: 1.8mm; }}
table.data {{ width: 100%; border-collapse: collapse; font-size: 8.9pt;
              line-height: 1.3; }}
table.data th {{ background: #0B1F3A; color: #FFFFFF; font-family: TNR_Bold;
                 font-weight: normal; padding: 1.5mm 1.6mm; border: 0.5pt solid #0B1F3A; }}
table.data td {{ padding: 1.3mm 1.6mm; border: 0.5pt solid var(--rule);
                 vertical-align: top; }}
table.data tbody tr:nth-child(even) td {{ background: #F2F5F9; }}
table.data tbody tr.sub td {{ background: #E3E9F2; font-family: TNR_Bold; }}
.c {{ text-align: center; }} .r {{ text-align: right; }} .l {{ text-align: left; }}
.tnote {{ font-size: 8.4pt; color: #333; margin-top: 1.4mm; line-height: 1.3;
          text-align: left; }}

/* ---------------- callouts ---------------- */
.callout {{ border-left: 2.6pt solid #0000FF; background: #F4F6FB;
            padding: 2.6mm 3.4mm; margin: 3.6mm 0; page-break-inside: avoid;
            font-size: 10.2pt; }}
.decision {{ border-left: 2.6pt solid #1F7A1F; background: #F2F8F2;
             padding: 2.6mm 3.4mm; margin: 3.6mm 0; page-break-inside: avoid;
             font-size: 10.2pt; }}
.cotitle {{ font-family: TNR_Bold; font-size: 9.4pt; letter-spacing: .1em;
            text-transform: uppercase; color: #0B1F3A; margin-bottom: 1.2mm; }}

/* ---------------- code ---------------- */
pre.code {{ font-family: "DejaVu Sans Mono"; font-size: 7.15pt; line-height: 1.34;
            background: #F7F8FA; border: 0.4pt solid #D7DEE8;
            border-left: 2pt solid #0B1F3A; padding: 2.2mm 2.6mm;
            white-space: pre-wrap; overflow-wrap: break-word;
            text-align: left; margin: 2.6mm 0 3.4mm; hyphens: none; }}
code {{ font-family: "DejaVu Sans Mono"; font-size: 8.6pt; background: #F1F3F7;
        padding: 0 .6mm; }}
pre.code .k {{ color: #0000CC; }}

/* ---------------- references ---------------- */
ol.refs {{ padding-left: 8mm; font-size: 9.7pt; }}
ol.refs li {{ margin-bottom: 2.1mm; text-align: left; line-height: 1.34; }}

/* ---------------- appendix / utility ---------------- */
.pb {{ break-before: page; }}
.avoid {{ page-break-inside: avoid; }}
.tiny {{ font-size: 8.6pt; }}
.muted {{ color: #555; }}
.hr {{ border-top: 0.5pt solid var(--rule); margin: 4mm 0; }}
.kpi-grid {{ display: flex; gap: 3mm; margin: 3.4mm 0 4mm; }}
.kpi {{ flex: 1 1 0; border: 0.5pt solid #C9D3E0; border-top: 2.4pt solid #0B1F3A;
        padding: 2.4mm 2.2mm; text-align: center; }}
.kpi .v {{ font-family: TNR_Bold; font-size: 13.4pt; color: #0B1F3A; display: block; }}
.kpi .lb {{ font-size: 8.2pt; color: #333; display: block; margin-top: .8mm; }}
"""
