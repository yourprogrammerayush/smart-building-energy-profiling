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
# Official project identity (do not change):
#   live site  -> GitHub Pages project site
#   source     -> GitHub repository
#   archive    -> Google Drive delivery folder
LIVE_SITE = "https://yourprogrammerayush.github.io/smart-building-energy-profiling/"
GITHUB_REPO = "https://github.com/yourprogrammerayush/smart-building-energy-profiling"
LIVE_SITE_SHORT = "yourprogrammerayush.github.io/smart-building-energy-profiling/"
GITHUB_REPO_SHORT = "github.com/yourprogrammerayush/smart-building-energy-profiling"
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
        self._tn = 0          # tables seen -> drives the five-accent cycle

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
        self._tn += 1
        if cls == "data":
            # Consecutive tables cycle teal -> green -> amber -> plum -> coral so
            # that no single hue dominates the document.
            cls = f"data acc{(self._tn - 1) % 5 + 1}"
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
    """Publication stylesheet: multi-hue academic design system.

    Colour logic: body text is near-black, structure is carried by a teal-ink
    primary with four supporting accents (forest green, amber, plum, coral).
    No single hue dominates; tables cycle through the five accents so that
    consecutive tables are visually distinct without becoming noisy.
    """
    reg = (FONT_DIR / "TimesNewRoman.ttf").as_posix()
    bold = (FONT_DIR / "TimesNewRoman-Bold.ttf").as_posix()
    ital = (FONT_DIR / "TimesNewRoman-Italic.ttf").as_posix()
    bi = (FONT_DIR / "TimesNewRoman-BoldItalic.ttf").as_posix()

    css = """
@font-face { font-family: TNR_Reg;  src: url("file://__REG__");  font-weight: normal; font-style: normal; }
@font-face { font-family: TNR_Bold; src: url("file://__BOLD__"); font-weight: bold;   font-style: normal; }
@font-face { font-family: TNR_Ital; src: url("file://__ITAL__"); font-weight: normal; font-style: italic; }
@font-face { font-family: TNR_BI;   src: url("file://__BI__");   font-weight: bold;   font-style: italic; }

/* The Matplotlib SVGs name their text in the internal family of the supplied
   TrueType file; register the same quartet under those names so that vector
   figure labels use the real faces instead of a synthesised oblique. */
@font-face { font-family: "Times New Roman Cyr"; src: url("file://__REG__");  font-style: normal; font-weight: normal; }
@font-face { font-family: "Times New Roman Cyr"; src: url("file://__BOLD__"); font-style: normal; font-weight: bold; }
@font-face { font-family: "Times New Roman Cyr"; src: url("file://__ITAL__"); font-style: italic; font-weight: normal; }
@font-face { font-family: "Times New Roman Cyr"; src: url("file://__BI__");   font-style: italic; font-weight: bold; }
@font-face { font-family: "Times New Roman";     src: url("file://__REG__");  font-style: normal; font-weight: normal; }
@font-face { font-family: "Times New Roman";     src: url("file://__BOLD__"); font-style: normal; font-weight: bold; }
@font-face { font-family: "Times New Roman";     src: url("file://__ITAL__"); font-style: italic; font-weight: normal; }
@font-face { font-family: "Times New Roman";     src: url("file://__BI__");   font-style: italic; font-weight: bold; }

/* ------------------------------------------------------------------ tokens */
:root {
  --ink: #101418;        /* body text, near-black */
  --ink-soft: #39424B;   /* secondary text */
  --deep: #13303B;       /* teal-ink structure */
  --teal: #12707F;
  --green: #2F7D52;
  --amber: #B5771A;
  --plum: #5F4B8B;
  --coral: #B5462F;
  --rule: #D5D2CA;       /* warm neutral hairlines */
  --rule-cool: #CBD4DA;
  --zebra: #F7F8F8;
  --sand: #FBF7F1;
  --link: #0B3DBF;
}

/* -------------------------------------------------------------------- pages */
@page {
  size: A4;
  margin: 24mm 20mm 20mm 26mm;
  @top-right {
    content: string(chapno) ": " string(runhead);
    font-family: TNR_Ital; font-size: 8.6pt; color: var(--teal);
    margin-bottom: 2.4mm;
  }
  @top-left {
    content: "__COURSE__ Mini Project 2026-27";
    font-family: TNR_Reg; font-size: 7.8pt; color: #6B6B6B;
    margin-bottom: 2.4mm;
  }
  @bottom-center {
    content: counter(page);
    font-family: TNR_Bold; font-size: 8.8pt; color: var(--deep);
    letter-spacing: .04em;
  }
}

/* The cover gets its own, tighter geometry so the double frame can breathe. */
@page fm-first {
  margin: 13mm 15mm 12mm 15mm;
  @top-right { content: none; } @top-left { content: none; }
  @bottom-center { content: none; border: none; }
}

@page frontmatter {
  @top-right { content: none; }
  @top-left { content: none; }
  @bottom-center {
    content: counter(page, lower-roman);
    font-family: TNR_Reg; font-size: 9pt; color: var(--ink-soft);
  }
}

/* ------------------------------------------------------------------- base */
html { font-family: TNR_Reg; font-size: 11pt; color: var(--ink); }
body { margin: 0; line-height: 1.44; text-align: justify; hyphens: auto;
       hyphenate-character: "-"; }

/* ------------------------------------------------------------ front matter */
section.fm { page: frontmatter; }
section.fm.first { page: fm-first; }
.fm h1 {
  font-family: TNR_Bold; font-size: 15pt; letter-spacing: .10em;
  text-transform: uppercase; text-align: center; color: var(--deep);
  margin: 0 0 6mm 0; padding-bottom: 2.6mm;
  border-bottom: 0.9pt solid var(--deep);
}
.fm h1::after {
  content: ""; display: block; height: 1.4mm; margin: 2.2mm auto 0; width: 46mm;
  background-image: linear-gradient(90deg, #12707F 0%, #12707F 25%, #2F7D52 25%, #2F7D52 50%, #B5771A 50%, #B5771A 75%, #5F4B8B 75%, #5F4B8B 100%);
}
.fm h2 { font-family: TNR_Bold; font-size: 12pt; color: var(--deep); margin: 6mm 0 2mm; }
.fm p { margin: 0 0 3.2mm; }
.small { font-size: 9.6pt; }
.center { text-align: center; }
.eyebrow { font-family: TNR_Bold; font-size: 9pt; letter-spacing: .22em;
           text-transform: uppercase; color: var(--teal); text-align: center; }

/* ------------------------------------------------------------------ cover */
.cover { text-align: center; height: 271mm; display: flex; flex-direction: column;
         justify-content: center; }
.coverframe {
  border: 1.5pt solid var(--deep);
  padding: 2.2mm;                       /* gap between the two frame lines */
  height: 249mm; box-sizing: border-box;
}
.coverframe-inner {
  border: 0.5pt solid var(--deep);
  height: 100%; box-sizing: border-box;
  padding: 8mm 9mm 7mm;
  display: flex; flex-direction: column; justify-content: space-between;
}
.coverframe-inner > .cgroup { width: 100%; }
.cover .corner-rule { height: 0.4pt; background: var(--teal); width: 34mm;
                      margin: 0 auto; }
.cover .logo { width: 27mm; margin: 0 auto 3.4mm; display: block; }
.cover .uni { font-family: TNR_Bold; font-size: 16.5pt; color: var(--deep);
              letter-spacing: .035em; margin: 0; }
.cover .dept { font-size: 10.6pt; margin: 1.4mm 0 0; color: var(--ink-soft); }
.cover .rule {
  height: 1.1mm; margin: 4mm 0 4.6mm; border: none;
  border-top: 0.8pt solid var(--deep);
  background-image: linear-gradient(90deg, #12707F 0%, #12707F 20%, #2F7D52 20%, #2F7D52 40%, #B5771A 40%, #B5771A 60%, #5F4B8B 60%, #5F4B8B 80%, #B5462F 80%, #B5462F 100%);
}
.cover .kicker { font-size: 9.6pt; letter-spacing: .34em; text-transform: uppercase;
                 color: var(--teal); margin: 0 0 2.6mm; }
.cover .title { font-family: TNR_Bold; font-size: 19pt; line-height: 1.22;
                color: var(--deep); margin: 0 0 3.4mm; hyphens: manual;
                text-wrap: balance; }
.cover .subtitle { font-family: TNR_Ital; font-size: 10.9pt; color: var(--ink-soft);
                   margin: 0 0 4.4mm; line-height: 1.34; }
.cover .submitline { font-size: 9.5pt; margin: 0 0 3.4mm; hyphens: manual;
                     line-height: 1.38; }
.cover .metatable { width: 100%; border-collapse: collapse; font-size: 9.1pt;
                    margin: 1.6mm 0 0; }
.cover .metatable td { border: 0.5pt solid var(--rule); padding: 1.25mm 2.2mm; }
.cover .metatable td.k { background: #F1F5F6; font-family: TNR_Bold; width: 31%;
                         text-align: left; color: var(--deep); }
.cover .metatable td.v { text-align: left; }
.cover .metatable tr.accent-1 td.k { background: #EAF3F4; }
.cover .metatable tr.accent-2 td.k { background: #EDF6F0; }
.cover .metatable tr.accent-3 td.k { background: #FAF2E4; }
.cover .metatable tr.accent-4 td.k { background: #F1EEF7; }
.cover .link { font-family: TNR_Reg; color: var(--link); text-decoration: underline;
               font-size: 8.9pt; }
.cover .footerline { margin: 3mm 0 0; font-size: 9.2pt; color: var(--ink-soft);
                      letter-spacing: .02em; }
.cover .membertable { width: 100%; border-collapse: collapse; font-size: 8.3pt;
                      margin-top: 3.4mm; }
.cover .membertable th { background: var(--deep); color: #fff; font-family: TNR_Bold;
                         font-weight: normal; padding: 1.1mm 1.6mm;
                         border: 0.5pt solid var(--deep); font-size: 8.1pt; }
.cover .membertable td { padding: 0.95mm 1.6mm; border: 0.5pt solid var(--rule);
                         vertical-align: top; text-align: left; }
.cover .membertable tbody tr:nth-child(even) td { background: #F4F7F8; }

/* -------------------------------------------------------- signature blocks */
table.sign { width: 100%; border-collapse: collapse; font-size: 9.6pt; margin: 6mm 0 0; }
table.sign td { padding: 2.4mm 1.6mm; vertical-align: bottom; }
table.sign td.line { border-bottom: 0.6pt solid var(--deep); height: 12mm; }
.sigcap { font-size: 9.2pt; color: var(--ink-soft); }

/* dotted leader rows (TOC / LOF / LOT) */
/* List rows (TOC / LOF / LOT).
   A dotted leader implemented as a separate flex item is not viable here:
   WeasyPrint retains the item's bottom border when it fragments a long flex
   list, leaving rows of orphaned dots with no text below the page content box.
   Instead each row is a single flex line - title left, folio right - with a
   hairline rule that belongs to the row box itself, so nothing can survive
   without its text. */
.row { display: flex; justify-content: space-between; align-items: baseline;
       margin: 0; padding: 0; border-bottom: 0.3pt solid #ECE9E3;
       break-inside: avoid; page-break-inside: avoid; }
.row .t { flex: 1 1 auto; min-width: 0; padding-right: 3mm; }
.row .lead { display: none; }
.row .p { flex: 0 0 auto; padding-left: 3mm; font-family: TNR_Reg; text-align: right; }
.toc-l2 .row, .toc-l1 > .row { border-bottom: none; }
.toc-l1 { font-family: TNR_Bold; font-size: 9.3pt; margin: 1.3mm 0 0.3mm; }
.toc-l2 { font-size: 8.5pt; margin-left: 5mm; line-height: 1.0; }
.toc-l1 .row, .toc-l1 { color: var(--deep); }
.lof-row { font-size: 9pt; line-height: 1.16; }
.lof-row .t { font-family: TNR_Reg; }

section.fm.abstractpage { font-size: 9.85pt; line-height: 1.35; }
section.fm.abstractpage p { margin-bottom: 2.1mm; }

/* -------------------------------------------------------- body typography */
h1.ch {
  font-family: TNR_Bold; font-size: 16.2pt; color: var(--deep); text-align: left;
  margin: 0 0 6mm; padding: 0; border: none;
  break-before: page; page-break-after: avoid;
}
/* Five-hue rule under every chapter title.  Implemented as its own 1.2 mm box:
   a gradient on the tall heading box itself would flood the text (WeasyPrint
   paints gradient backgrounds across the whole element, ignoring
   background-size), so the bar must be a separate, short element. */
h1.ch::after {
  content: ""; display: block; height: 1.2mm; width: 100%; margin-top: 3mm;
  background-image: linear-gradient(90deg, #12707F 0%, #12707F 30%, #2F7D52 30%, #2F7D52 50%, #B5771A 50%, #B5771A 70%, #5F4B8B 70%, #5F4B8B 86%, #B5462F 86%, #B5462F 100%);
}
h1.ch .chtitle { string-set: runhead content(); }
h1.ch .cn {
  string-set: chapno content(); display: block; font-size: 8.8pt; letter-spacing: .3em;
  color: var(--teal); text-transform: uppercase; margin-bottom: 1.8mm;
  font-family: TNR_Bold;
}
h2 { font-family: TNR_Bold; font-size: 12.6pt; color: var(--deep);
     margin: 6.4mm 0 2.2mm; page-break-after: avoid; text-align: left;
     padding-left: 2.6mm; border-left: 2.6pt solid var(--teal); }
h3 { font-family: TNR_Bold; font-size: 11.1pt; color: var(--ink);
     margin: 4.6mm 0 1.6mm; page-break-after: avoid; text-align: left; }
h4 { font-family: TNR_BI; font-size: 10.5pt; color: var(--plum);
     margin: 3.6mm 0 1.2mm; page-break-after: avoid; text-align: left; }
p { margin: 0 0 2.7mm; orphans: 2; widows: 2; }
ul, ol { margin: 0 0 3mm 0; padding-left: 6.5mm; }
li { margin-bottom: 1.2mm; }
strong { font-family: TNR_Bold; font-weight: normal; }
em { font-family: TNR_Ital; font-style: normal; }
sup { font-size: 70%; vertical-align: super; line-height: 0; }
sub { font-size: 70%; vertical-align: sub; line-height: 0; }
.eq { font-family: TNR_Ital; text-align: center; margin: 3.4mm 0 3.4mm; font-size: 11pt;
      position: relative; padding-right: 12mm; }
.eq .n { position: absolute; right: 0; top: 0; font-family: TNR_Reg; font-style: normal; }
a { color: var(--link); text-decoration: none; }

/* --------------------------------------------------------------- figures */
/* Figures get a hairline frame so plots read as plates rather than floating. */
figure.fig { margin: 4.4mm 0 4.8mm; page-break-inside: avoid; text-align: center; }
figure.fig img { display: block; margin: 0 auto; }
figcaption { font-size: 9.3pt; line-height: 1.36; text-align: center;
             margin: 2.2mm auto 0; color: var(--ink-soft); max-width: 96%; }
.fignum { font-family: TNR_Bold; color: var(--deep); }

/* ---------------------------------------------------------------- tables */
.tblock { margin: 4.2mm 0 5.2mm; page-break-inside: avoid; }
.tcap { font-size: 9.3pt; text-align: left; margin-bottom: 1.8mm; color: var(--ink-soft);
        padding-left: 2.4mm; border-left: 2.4pt solid var(--teal); }
table.data { width: 100%; border-collapse: collapse; font-size: 8.85pt; line-height: 1.32; }
table.data th { color: #FFFFFF; font-family: TNR_Bold; font-weight: normal;
                padding: 1.6mm 1.7mm; border: 0.5pt solid rgba(0,0,0,.18);
                background: var(--teal); }
table.data td { padding: 1.3mm 1.7mm; border: 0.5pt solid var(--rule);
                vertical-align: top; }
table.data tbody tr:nth-child(even) td { background: #F4F7F8; }
table.data tbody tr.sub td { background: #E7EEF0; font-family: TNR_Bold; }

/* five complementary accents, cycled per table by the registry */
table.data.acc2 th { background: var(--green); }
table.data.acc2 tbody tr:nth-child(even) td { background: #F1F7F3; }
table.data.acc2 tbody tr.sub td { background: #E4F0E8; }
table.data.acc3 th { background: var(--amber); }
table.data.acc3 tbody tr:nth-child(even) td { background: #FBF6EC; }
table.data.acc3 tbody tr.sub td { background: #F4E9D3; }
table.data.acc4 th { background: var(--plum); }
table.data.acc4 tbody tr:nth-child(even) td { background: #F5F3F9; }
table.data.acc4 tbody tr.sub td { background: #EAE5F2; }
table.data.acc5 th { background: var(--coral); }
table.data.acc5 tbody tr:nth-child(even) td { background: #FCF3F0; }
table.data.acc5 tbody tr.sub td { background: #F7E4DE; }

.tblock:has(table.acc2) .tcap { border-left-color: var(--green); }
.tblock:has(table.acc3) .tcap { border-left-color: var(--amber); }
.tblock:has(table.acc4) .tcap { border-left-color: var(--plum); }
.tblock:has(table.acc5) .tcap { border-left-color: var(--coral); }

.c { text-align: center; } .r { text-align: right; } .l { text-align: left; }
.tnote { font-size: 8.3pt; color: var(--ink-soft); margin-top: 1.4mm; line-height: 1.34;
         text-align: left; }

/* -------------------------------------------------------------- callouts */
.callout { border-left: 3pt solid var(--teal); background: #F1F7F8;
           padding: 2.8mm 3.6mm; margin: 3.8mm 0; page-break-inside: avoid;
           font-size: 10.1pt; }
.decision { border-left: 3pt solid var(--green); background: #F2F8F4;
            padding: 2.8mm 3.6mm; margin: 3.8mm 0; page-break-inside: avoid;
            font-size: 10.1pt; }
.cotitle { font-family: TNR_Bold; font-size: 9.2pt; letter-spacing: .12em;
           text-transform: uppercase; color: var(--deep); margin-bottom: 1.2mm; }
.callout .cotitle { color: var(--teal); }
.decision .cotitle { color: var(--green); }

/* ------------------------------------------------------------------ code */
pre.code { font-family: "DejaVu Sans Mono"; font-size: 7.1pt; line-height: 1.36;
           background: #FAF8F4; border: 0.4pt solid var(--rule);
           border-left: 2.2pt solid var(--teal); padding: 2.3mm 2.7mm;
           white-space: pre-wrap; overflow-wrap: break-word;
           text-align: left; margin: 2.6mm 0 3.4mm; hyphens: none; }
code { font-family: "DejaVu Sans Mono"; font-size: 8.5pt; background: #F3F1EC;
       padding: 0 .6mm; }
pre.code .k { color: var(--plum); }

/* ------------------------------------------------------------ references */
ol.refs { padding-left: 8mm; font-size: 9.65pt; }
ol.refs li { margin-bottom: 2.1mm; text-align: left; line-height: 1.36; }

/* ------------------------------------------------------------- utilities */
.pb { break-before: page; }
.avoid { page-break-inside: avoid; }
.tiny { font-size: 8.6pt; }
.muted { color: var(--ink-soft); }
.hr { border-top: 0.5pt solid var(--rule); margin: 4mm 0; }
.kpi-grid { display: flex; gap: 3mm; margin: 3.6mm 0 4.2mm; }
.kpi { flex: 1 1 0; border: 0.5pt solid var(--rule-cool); border-top: 2.6pt solid var(--teal);
       padding: 2.5mm 2.2mm; text-align: center; background: #FCFDFD; }
.kpi:nth-child(2) { border-top-color: var(--green); }
.kpi:nth-child(3) { border-top-color: var(--amber); }
.kpi:nth-child(4) { border-top-color: var(--plum); }
.kpi:nth-child(5) { border-top-color: var(--coral); }
.kpi .v { font-family: TNR_Bold; font-size: 13.2pt; color: var(--deep); display: block; }
.kpi .lb { font-size: 8.1pt; color: var(--ink-soft); display: block; margin-top: .8mm; }
"""
    css = (css.replace("__REG__", reg).replace("__BOLD__", bold)
              .replace("__ITAL__", ital).replace("__BI__", bi)
              .replace("__COURSE__", COURSE))
    return css
