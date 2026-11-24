"""Front-matter pages: title page, certificate, declaration, acknowledgement,
abstract, table of contents, list of figures, list of tables, abbreviations."""

from __future__ import annotations

from report_lib import (ACADEMIC_YEAR, COURSE, COURSE_NAME, DEPARTMENT, DRIVE_FOLDER,
                        FACULTY, LIVE_SITE, PROJECT_TITLE, ROOT, SECTION, TEAM,
                        TITLE_PLAIN, UNIVERSITY)

LOGO = (ROOT / "assets" / "logos" / "IILM-Logo.png").as_posix()


# ---------------------------------------------------------------------------
def cover_page() -> str:
    members = "".join(
        f"<tr><td class='l'>{n}</td><td class='c'>{r}</td>"
        f"<td class='l'>{role}</td></tr>" for n, r, role in TEAM)
    return f"""
<section class="fm first">
<div class="cover">
  <img class="logo" src="{LOGO}" alt="IILM University crest">
  <p class="uni">{UNIVERSITY}</p>
  <p class="dept">{DEPARTMENT}</p>
  <div class="rule"></div>
  <p class="kicker">Mini Project Report</p>
  <p class="title">{PROJECT_TITLE}</p>
  <p class="subtitle">Quantifying operational energy wastage in a six-building
     university and commercial district using smart-meter telemetry, weather
     covariates and syllabus-locked machine learning</p>
  <p class="submitline">A mini project report submitted in partial fulfilment of the
     requirements of the course<br>
     <strong>{COURSE_NAME}</strong> ({COURSE}) &nbsp;&#183;&nbsp; B.Tech Computer
     Science and Engineering &nbsp;&#183;&nbsp; Semester III</p>
  <table class="metatable">
    <tr><td class="k">Submitted by</td><td class="v">Team {SECTION} &#8212; five members
        (see table below)</td></tr>
    <tr><td class="k">Faculty Guide</td><td class="v">{FACULTY}</td></tr>
    <tr><td class="k">Academic Year</td><td class="v">{ACADEMIC_YEAR}</td></tr>
    <tr><td class="k">Live Project Website</td><td class="v">{LIVE_SITE}</td></tr>
  </table>
  <p class="footerline">Greater Noida, Uttar Pradesh, India &nbsp;&#183;&nbsp;
     November 2026</p>
  <div class="rule" style="margin-top:4mm"></div>
  <table class="data" style="font-size:8.8pt">
    <thead><tr><th class="l">Student Name</th><th class="c">Roll Number</th>
      <th class="l">Primary Contribution</th></tr></thead>
    <tbody>{members}</tbody>
  </table>
</div>
</section>"""


# ---------------------------------------------------------------------------
def certificate_page() -> str:
    return f"""
<section class="fm">
  <h1>Certificate</h1>
  <p>This is to certify that the mini project report entitled
  <strong>&#8220;{TITLE_PLAIN}&#8221;</strong> is a bonafide record of the work carried
  out by the team of <strong>Section {SECTION}</strong> &#8212; Ayush Jha
  (25SCS1003001336), Archit Baloni (25SCS1003003550), Ashutosh Sahoo
  (25SCS1003004011), Dev Bhaskar Singh (25SCS1003003174) and Aman Kumar Gupta
  (25SCS1003003645) &#8212; submitted in partial fulfilment of the requirements for the
  award of the degree of Bachelor of Technology in Computer Science and Engineering
  of {UNIVERSITY} for the academic year {ACADEMIC_YEAR}.</p>

  <p>The work has been carried out under my supervision and guidance in the
  {DEPARTMENT}. The data acquisition, preprocessing pipeline, statistical testing,
  machine-learning modelling, visualization engineering and the interactive web
  application documented in this report are the original work of the team, built upon
  the openly licensed Building Data Genome Project 2 (CC BY-SA 4.0) benchmark, and
  have not been submitted elsewhere for the award of any other degree or diploma.</p>

  <table class="sign">
    <tr>
      <td style="width:50%"><div class="line"></div>
        <div class="sigcap"><strong>{FACULTY}</strong><br>Faculty Guide<br>
        {DEPARTMENT}</div></td>
      <td style="width:50%"><div class="line"></div>
        <div class="sigcap"><strong>Head of Department</strong><br>
        {DEPARTMENT}<br>{UNIVERSITY}</div></td>
    </tr>
  </table>

  <table class="sign" style="margin-top:12mm">
    <tr>
      <td style="width:50%"><div class="line"></div>
        <div class="sigcap"><strong>Internal Examiner</strong><br>Name and signature
        with date</div></td>
      <td style="width:50%"><div class="line"></div>
        <div class="sigcap"><strong>External Examiner</strong><br>Name and signature
        with date</div></td>
    </tr>
  </table>

  <p class="small muted" style="margin-top:10mm">Examination session: November&#8211;December
  2026 &nbsp;&#183;&nbsp; Report version 1.0 &nbsp;&#183;&nbsp; Place: Greater Noida,
  Uttar Pradesh, India.</p>
</section>"""


# ---------------------------------------------------------------------------
def declaration_page() -> str:
    return f"""
<section class="fm">
  <h1>Declaration</h1>
  <p>We hereby declare that the mini project report entitled <strong>&#8220;{TITLE_PLAIN}&#8221;</strong>
  submitted to the {DEPARTMENT}, {UNIVERSITY}, in partial fulfilment of the
  requirements of the course <strong>{COURSE_NAME}</strong> ({COURSE}) for Semester III
  of the B.Tech Computer Science and Engineering programme, is a record of the
  original work carried out by our team.</p>

  <p>We further declare that:</p>
  <ol>
    <li>The empirical dataset used in this study is the publicly available
        <em>Building Data Genome Project 2</em> benchmark, distributed under the
        Creative Commons Attribution-ShareAlike 4.0 International licence; every
        transformation applied to it is documented in Chapter 3 and reproducible
        through the published pipeline.</li>
    <li>All statistical tests, machine-learning experiments, figures, tables and
        numerical claims reported here were produced by the deterministic
        (<code>SEED = 42</code>) pipeline shipped with this report, and not copied
        from any other student, author or institution.</li>
    <li>Wherever external material (literature, benchmark values, tariff and emission
        factors) has been consulted, it has been acknowledged in the text and cited
        in the IEEE-style reference list.</li>
    <li>This work has not been submitted previously, in part or in full, for the award
        of any degree or diploma of this or any other university.</li>
  </ol>

  <table class="sign" style="margin-top:14mm">
    <tr>
      <td style="width:33%"><div class="line"></div><div class="sigcap">
        <strong>Ayush Jha</strong><br>25SCS1003001336</div></td>
      <td style="width:33%"><div class="line"></div><div class="sigcap">
        <strong>Archit Baloni</strong><br>25SCS1003003550</div></td>
      <td style="width:33%"><div class="line"></div><div class="sigcap">
        <strong>Ashutosh Sahoo</strong><br>25SCS1003004011</div></td>
    </tr>
    <tr>
      <td><div class="line"></div><div class="sigcap">
        <strong>Dev Bhaskar Singh</strong><br>25SCS1003003174</div></td>
      <td><div class="line"></div><div class="sigcap">
        <strong>Aman Kumar Gupta</strong><br>25SCS1003003645</div></td>
      <td><div class="sigcap" style="padding-top:12mm">Date: ______________<br>
        Place: Greater Noida</div></td>
    </tr>
  </table>
</section>"""


# ---------------------------------------------------------------------------
def acknowledgement_page() -> str:
    return f"""
<section class="fm">
  <h1>Acknowledgement</h1>
  <p>The completion of this mini project has been a genuinely collaborative effort,
  and we are indebted to several people who made it possible.</p>

  <p>We express our sincere gratitude to <strong>{FACULTY}</strong>, our faculty guide
  for {COURSE_NAME} ({COURSE}), whose insistence on methodological rigour shaped this
  report at every stage. His repeated question &#8212; <em>&#8220;what would the
  building have consumed anyway?&#8221;</em> &#8212; is the reason this project is built
  around a counterfactual regression baseline rather than a simple
  above-average-hours chart, and his feedback on hypothesis-testing discipline
  turned a descriptive dashboard into a defensible analytical study.</p>

  <p>We are grateful to the <strong>Head of Department</strong> and the faculty and
  staff of the {DEPARTMENT}, {UNIVERSITY}, for the laboratory infrastructure,
  computational resources and academic freedom that allowed us to work with two
  complete years of hourly interval data. We thank the department for making the
  Data Visualization and Analysis course project a genuinely open-ended exercise,
  which permitted us to move beyond the classroom library of charts into reproducible
  analytics engineering.</p>

  <p>This work would not exist without the open-data community. We thank
  <strong>Miller, Kathirgamanathan, Picchetti and colleagues</strong> for publishing
  the Building Data Genome Project 2 and the ASHRAE Great Energy Predictor III
  meter data under a Creative Commons licence, and the <strong>BUDS Lab</strong> at
  the National University of Singapore for maintaining the public mirror from which
  our extract was drawn. Open benchmarks of this quality are the reason undergraduate
  teams can attempt realistic anomaly-detection work.</p>

  <p>We also acknowledge the maintainers of the scientific Python ecosystem
  &#8212; NumPy, pandas, SciPy, scikit-learn, Matplotlib, Seaborn, Jupyter,
  WeasyPrint and Plotly &#8212; whose tools carried every experiment reported here,
  and the documentation teams whose examples silently saved us many hours.</p>

  <p>Finally, we thank our families and classmates for their patience during the
  long debugging evenings of the November 2026 submission window, and our reviewers
  within the batch, whose critical reading of early drafts removed several errors
  that would otherwise have survived into this version. Any remaining mistakes are
  entirely our own.</p>

  <p style="margin-top:10mm; text-align:right"><strong>Team {SECTION}</strong><br>
  <span class="small">{UNIVERSITY}<br>November 2026</span></p>
</section>"""


# ---------------------------------------------------------------------------
def abstract_page() -> str:
    return f"""
<section class="fm abstractpage">
  <h1>Abstract</h1>
  <p>Commercial offices and university campuses waste a substantial share of the
  electricity they purchase, yet the waste is almost invisible in monthly utility
  invoices: it appears as elevated overnight baseload, incomplete weekend setbacks and
  weather-uncoupled cooling spikes rather than as a single dramatic failure. This
  report presents an end-to-end, reproducible data-driven study of that phenomenon for
  a real six-building mixed portfolio &#8212; three commercial offices and three
  university buildings totalling 31,462.6 m<sup>2</sup> &#8212; using 17,544 hourly
  smart-meter readings from the openly licensed Building Data Genome Project 2
  (Site <em>Fox</em>, Tempe, Arizona; 1 January 2016 to 31 December 2017) joined with
  hourly airport weather observations.</p>

  <p>The methodology follows the Data Visualization and Analysis syllabus
  ({COURSE}): exploratory data analysis with Matplotlib and Seaborn; two-sample
  hypothesis testing; Multiple Linear Regression, Decision Trees, Support Vector
  Machines, K-Means clustering and Gaussian Naive Bayes &#8212; and no algorithm
  outside that taught set. After a documented preprocessing pass (0.048% meter
  dropouts, 0.101% core weather dropouts, trace-precipitation sentinel repair and a
  deliberate decision to <em>retain</em> load spikes), the portfolio was profiled and
  a counterfactual weather-plus-schedule regression baseline was fitted on 2016 and
  tested out-of-sample on 2017.</p>

  <p>Four findings dominate. First, the portfolio consumed <strong>13,677.27 MWh</strong>
  over the two years (<strong>6,838.63 MWh/year</strong>, an Energy Use Intensity of
  <strong>217.36 kWh/m<sup>2</sup>/year</strong>) at a mean load of 779.60 kWh/h.
  Second, the daily load is a plateau, not a peak: the 04:00 trough averages
  547.4 kWh/h, i.e. 55.6% of the 15:00 peak of 984.0 kWh/h, and the 5,848
  unoccupied night hours (33.33% of clock time) still absorb
  <strong>3,460.7 MWh &#8212; 25.30% of all energy</strong>, at an off-hour mean of
  591.78 kWh/h against a work-hour mean of 994.55 kWh/h (Welch
  <em>t</em> = 129.27). Third, the autoregressive weather-and-calendar regression
  reaches <em>R</em><sup>2</sup> = 0.9351 (RMSE 60.76 kWh/h, MAPE 6.01%) on the 2017
  holdout, which makes the residual a usable wastage signal: against a transparent,
  physics-grounded audit rule, <strong>157 of 731 days (21.5%)</strong> are flagged by
  the consensus of the domain rule, a One-Class SVM and K-Means distance, carrying
  <strong>233.03 MWh</strong> of excess consumption (USD 27,964). Fourth, a
  quantified four-lever facility-management roadmap &#8212; overnight setback, weekend
  consolidation, anomaly triage and economizer/deadband tuning &#8212; recovers
  <strong>1,265.12 MWh per year (18.50% of baseline)</strong>, worth
  <strong>USD 151,815</strong> and <strong>527.6 tCO<sub>2</sub>e</strong> annually,
  with a conservative-to-aggressive band of 15.72%&#8211;20.72% under sensitivity
  analysis.</p>

  <p>The deliverables comprise this report, a fully executed Jupyter notebook,
  eighteen publication-grade vector figures, an eighteen-figure interactive Plotly
  web application with a live savings simulator, and the deterministic pipeline that
  regenerates every number in this document. The study demonstrates that a
  syllabus-bounded machine-learning toolkit, applied to openly licensed interval data
  with a disciplined counterfactual baseline, is sufficient to convert raw
  smart-meter telemetry into an auditable, financially quantified energy-waste
  programme for a campus estate.</p>

  <p><strong>Keywords:</strong> smart-meter analytics; building energy wastage;
  anomaly detection; one-class SVM; K-Means clustering; multiple linear regression;
  counterfactual baseline; measurement and verification; energy use intensity;
  visual analytics; data visualization; sustainability.</p>
</section>"""


# ---------------------------------------------------------------------------
def _row(rid: str, text: str, page, cls: str = "") -> str:
    pnum = "&#8212;" if page is None else str(page)
    return (f'<div class="row {cls}" id="{rid}"><span class="t">{text}</span>'
            f'<span class="lead"></span><span class="p">{pnum}</span></div>')


def contents_page(toc: list[dict]) -> tuple[str, list[tuple[str, str]]]:
    """toc entries: {'level':1|2,'text':..,'anchor':..,'page':int|None}"""
    rows, links = [], []
    for i, e in enumerate(toc):
        rid = f"tocref-{i}"
        if e["level"] == 1:
            rows.append(f'<div class="toc-l1">{_row(rid, e["text"], e["page"])}</div>')
        else:
            rows.append(f'<div class="toc-l2">{_row(rid, e["text"], e["page"])}</div>')
        links.append((rid, e["anchor"]))
    html = f"""
<section class="fm">
  <h1>Table of Contents</h1>
  {''.join(rows)}
</section>"""
    return html, links


def list_page(title: str, entries: list[dict], kind: str) -> tuple[str, list[tuple[str, str]]]:
    """entries: {'id':..,'label':..,'text':..,'page':int|None}"""
    rows, links = [], []
    for i, e in enumerate(entries):
        rid = f"{kind}ref-{i}"
        text = f'<span class="fignum">{e["label"]}</span>&nbsp; {e["text"]}'
        rows.append(_row(rid, text, e["page"], "lof-row"))
        links.append((rid, e["id"]))
    html = f"""
<section class="fm">
  <h1>{title}</h1>
  {''.join(rows)}
</section>"""
    return html, links


ABBREVIATIONS = [
    ("AC", "Alternating Current"), ("AHU", "Air Handling Unit"),
    ("ASHRAE", "American Society of Heating, Refrigerating and Air-Conditioning Engineers"),
    ("AR", "Autoregressive"), ("AUC", "Area Under the Receiver Operating Characteristic Curve"),
    ("BDG2", "Building Data Genome Project 2"), ("BMS", "Building Management System"),
    ("BPR", "Baseload-to-Peak Ratio"), ("CC BY-SA", "Creative Commons Attribution-ShareAlike"),
    ("CDD", "Cooling Degree Day"), ("CO<sub>2</sub>e", "Carbon Dioxide Equivalent"),
    ("CV-RMSE", "Coefficient of Variation of the Root Mean Square Error"),
    ("DCV", "Demand-Controlled Ventilation"), ("DT", "Decision Tree"),
    ("EDA", "Exploratory Data Analysis"), ("EUI", "Energy Use Intensity (kWh/m<sup>2</sup>/year)"),
    ("GNB", "Gaussian Naive Bayes"), ("HDD", "Heating Degree Day"),
    ("HVAC", "Heating, Ventilation and Air-Conditioning"),
    ("IEA", "International Energy Agency"), ("IQR", "Interquartile Range"),
    ("ISD", "Integrated Surface Database (NOAA)"), ("JSON", "JavaScript Object Notation"),
    ("KDE", "Kernel Density Estimate"), ("KPI", "Key Performance Indicator"),
    ("LBNL", "Lawrence Berkeley National Laboratory"), ("LF", "Load Factor"),
    ("LOF", "Local Outlier Factor"), ("MAE", "Mean Absolute Error"),
    ("MAPE", "Mean Absolute Percentage Error"), ("M&amp;V", "Measurement and Verification"),
    ("MLR", "Multiple Linear Regression"), ("MWh", "Megawatt-hour"),
    ("OCSVM", "One-Class Support Vector Machine"), ("PDF", "Portable Document Format"),
    ("RBF", "Radial Basis Function"), ("RMSE", "Root Mean Square Error"),
    ("ROC", "Receiver Operating Characteristic"), ("RQ", "Research Question"),
    ("SVM", "Support Vector Machine"), ("SVG", "Scalable Vector Graphics"),
    ("tCO<sub>2</sub>e", "Tonnes of Carbon Dioxide Equivalent"),
    ("UI", "User Interface"), ("URL", "Uniform Resource Locator"),
    ("VIF", "Variance Inflation Factor"), ("WS", "Weather Station"),
]


def abbreviations_page() -> str:
    half = (len(ABBREVIATIONS) + 1) // 2
    left, right = ABBREVIATIONS[:half], ABBREVIATIONS[half:]
    rows = []
    for i in range(half):
        a = left[i]
        b = right[i] if i < len(right) else ("", "")
        rows.append(f"<tr><td class='l'><strong>{a[0]}</strong></td><td class='l'>{a[1]}</td>"
                    f"<td class='l' style='width:12%'><strong>{b[0]}</strong></td>"
                    f"<td class='l'>{b[1]}</td></tr>")
    return f"""
<section class="fm">
  <h1>List of Abbreviations</h1>
  <table class="data" style="font-size:8.6pt">
    <colgroup><col style="width:11%"><col style="width:39%"><col style="width:11%">
      <col style="width:39%"></colgroup>
    <thead><tr><th class="l">Abbrev.</th><th class="l">Expansion</th>
      <th class="l">Abbrev.</th><th class="l">Expansion</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</section>"""
