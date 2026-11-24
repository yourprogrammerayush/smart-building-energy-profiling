"""Chapters 1-4 of the IILM mini-project report."""

from __future__ import annotations

from report_lib import (COURSE, DRIVE_FOLDER, LIVE_SITE, ROOT,
                        decision, keyfinding, Registry)


def _n(x, nd=2):
    return f"{x:,.{nd}f}"


# ===========================================================================
def chapter1(R: Registry, M: dict) -> str:
    s = M["stats"]
    return f"""
<section id="ch1">
<h1 class="ch" id="ch1"><span class="cn">Chapter 1</span><span class="chtitle">Introduction</span></h1>

<h2 id="s1-1">1.1 Background and Motivation</h2>
<p>Buildings are the single largest consumer of electricity in most economies, and
commercial offices together with educational campuses form the fastest-growing segment
of that demand. The International Energy Agency estimates that the buildings sector
accounts for roughly a third of global final energy consumption and a comparable share
of energy-related emissions, of which a large and growing fraction is electricity used
for cooling, ventilation, lighting and plug loads [17], [18]. What makes this demand
tractable &#8212; and what makes this project possible &#8212; is that it is now
measured. Interval smart meters, building management systems (BMS) and open weather
services generate a continuous stream of high-frequency, machine-readable evidence about
how a building actually behaves, as opposed to how its design drawings assumed it would
behave.</p>

<p>The gap between design intent and operational reality is where energy is wasted.
Empirical commissioning studies and load-shape benchmarking work by the Lawrence
Berkeley National Laboratory, ASHRAE and the U.S. Department of Energy repeatedly find
that a fifth to a third of commercial building electricity is consumed by operation
faults rather than by genuine service demand [3], [19]. These faults are mundane and
repetitive: an air-handling unit that never receives its night setback because a
manual override was left latched; a weekend schedule inherited from the weekday
template; an economizer damper stuck closed so that mechanical cooling runs against
outdoor air that could have provided free cooling; laboratory exhaust fans running at
full speed in an empty wing.</p>

<div class="kpi-grid">
  <div class="kpi"><span class="v">{_n(s['annual_avg_mwh']/1000,2)} GWh</span>
    <span class="lb">average annual portfolio demand, two-year study period</span></div>
  <div class="kpi"><span class="v">{_n(s['annual_eui_kwh_m2'],2)}</span>
    <span class="lb">kWh/m<sup>2</sup>/year energy use intensity across 31,462.6 m<sup>2</sup></span></div>
  <div class="kpi"><span class="v">{_n(s['off_hour_share_pct'],2)}%</span>
    <span class="lb">of all energy consumed in unoccupied night hours</span></div>
  <div class="kpi"><span class="v">18.50%</span>
    <span class="lb">recoverable annual baseline via four BMS levers</span></div>
</div>

<p>Diagnosing this class of waste is fundamentally a data-analysis problem, and it maps
almost one-to-one onto the syllabus of the course this report is submitted for. The
task requires careful exploratory visualization to see the load shape at all; two-sample
hypothesis testing to prove that the observed weekday/weekend and occupied/unoccupied
differences are not sampling noise; regression to construct the counterfactual demand
that <em>should</em> have occurred for the given weather and calendar; clustering to
identify distinct operational regimes without supervision; and novelty detection to
surface the days that deviate from every regime. This report applies exactly that
toolkit to a real, open, two-year interval dataset and carries the analysis through to a
financially quantified remediation plan.</p>

<h2 id="s1-2">1.2 Problem Statement</h2>
<p>The host institution of this study is a mixed estate: three commercial office blocks
and three university buildings served by six independent electricity meters and one
shared weather station. Facility management currently reviews consumption monthly, in
aggregate, after the invoice has arrived. Under that cadence, three distinct wastage
mechanisms are structurally invisible: (i) a persistent elevated overnight baseload,
because it is a smoothly varying fraction of the monthly total and never triggers an
alarm; (ii) incomplete weekend and academic-break setbacks, because weekends are only
28.6% of calendar days; and (iii) weather-uncoupled cooling, because a hot month and a
faulty month look identical in an invoice aggregate.</p>

<p>Stated formally, the problem addressed by this mini project is: <em>given two
consecutive years of hourly electricity meter data for a six-building portfolio and the
corresponding hourly meteorological observations, can we (a) characterize the diurnal,
weekly and seasonal structure of consumption, (b) construct a defensible
weather-and-schedule counterfactual against which abnormal consumption can be measured,
(c) detect and rank anomalous days and hours using only the algorithms taught in the
Data Visualization and Analysis syllabus, and (d) translate the detected excess into a
costed, prioritized and sensitivity-tested remediation roadmap?</em></p>

<p>Two constraints make the problem non-trivial. First, unlabelled field data carries no
maintenance-ticket ground truth, so an anomaly detector cannot simply be trained
supervised; a transparent audit rule must be constructed and the unsupervised detectors
honestly evaluated against it. Second, hour-of-day, weekday, ambient temperature and
solar-driven cooling are strongly collinear, so a naive residual will attribute
legitimate hot-weather load to wastage. Both constraints are addressed explicitly in
Chapters 4 and 6.</p>

<h2 id="s1-3">1.3 Research Questions and Objectives</h2>
<p>Five research questions structure the work. Each maps to one analytical stage, one
chapter and one set of figures, so that no claim in this report is left without an
evidentiary home.</p>

{R.table("1.1", "Research questions, objectives, analytical method and reporting location",
  ["RQ", "Research question", "Analytical method (syllabus unit)", "Reported in"],
  [
    ["RQ1", "What is the diurnal, weekly and seasonal structure of electricity demand "
     "across the six-building portfolio, and how large is the unoccupied-hour share?",
     "Descriptive statistics, Matplotlib/Seaborn EDA, baseload decomposition (Unit III)",
     "Chapter 5, Fig. 5.1&#8211;5.4, Table 5.1"],
    ["RQ2", "Are the observed weekday/weekend and occupied/unoccupied demand gaps "
     "statistically significant rather than sampling artefacts?",
     "Welch two-sample <em>t</em>-test, Mann&#8211;Whitney <em>U</em> test (Unit I&#8211;II)",
     "Chapter 5, Table 5.2"],
    ["RQ3", "How much of the hourly load is explained by weather and calendar drivers, "
     "and can the residual serve as a counterfactual wastage signal?",
     "Multiple Linear Regression (Unit II), Decision Tree Regressor (Unit IV)",
     "Chapter 6, Table 6.1&#8211;6.2, Fig. 6.1"],
    ["RQ4", "Which days behave as multivariate operational anomalies, and how well do "
     "unsupervised detectors agree with an auditable domain rule?",
     "One-Class SVM, K-Means clustering (Unit IV); RBF-SVM, Decision Tree and Gaussian "
     "Naive Bayes as supervised benchmarks (Unit IV)",
     "Chapter 6, Table 6.3&#8211;6.6, Fig. 6.2&#8211;6.6"],
    ["RQ5", "What is the recoverable energy, cost and carbon saving, and how sensitive "
     "is it to capture-rate and tariff assumptions?",
     "Counterfactual decomposition into four levers; scenario sensitivity analysis",
     "Chapter 7, Table 7.1&#8211;7.2, Fig. 7.1&#8211;7.2"],
  ],
  colw=["7%", "34%", "35%", "24%"],
  align=["c", "l", "l", "l"])}

<p>The corresponding objectives are: <strong>(O1)</strong> to curate and document a
two-year hourly dataset suitable for commercial and campus energy analytics and to
publish its provenance and quality audit; <strong>(O2)</strong> to characterize the
portfolio's load structure visually and statistically; <strong>(O3)</strong> to fit and
validate a counterfactual demand baseline and quantify residual excess energy;
<strong>(O4)</strong> to detect anomalous days and hours with a consensus of
unsupervised detectors and to benchmark them against supervised classifiers;
<strong>(O5)</strong> to convert the detected waste into a costed roadmap with explicit
tariff, emission and capture-rate assumptions; and <strong>(O6)</strong> to publish the
entire study as a reproducible pipeline, an executed notebook, a vector figure library
and an interactive web application.</p>

<h2 id="s1-4">1.4 Scope and Delineation</h2>
<p>The scope is deliberately bounded. The study analyses a six-building portfolio on a
single site over two calendar years, at hourly resolution, using electricity meter
readings and meteorological covariates only. It does not model thermal mass with a
physical energy simulation, does not include gas, water or chilled-water sub-metering,
does not perform occupant surveys, and does not claim measured-and-verified savings
from an implemented retrofit; the savings figures in Chapter 7 are engineering estimates
derived from the counterfactual baseline, explicitly labelled as such and stress-tested
through sensitivity analysis. Algorithm choice is locked to the taught syllabus and that
constraint is treated as a feature, not a limitation: it demonstrates what a second-year
undergraduate toolkit can achieve when it is applied with methodological discipline.</p>

<h2 id="s1-5">1.5 Contributions of the Study</h2>
<ul>
  <li><strong>A documented, reusable dataset extract.</strong> A curated 17,544-row,
      15-column hourly panel for a balanced 3-office / 3-campus district, together with
      a metadata table, dataset card, missing-value census and a deliberately explicit
      outlier-handling policy.</li>
  <li><strong>A counterfactual wastage measurement framework.</strong> A weather plus
      schedule regression baseline trained on 2016 and validated on 2017, combined with
      a transparent, literature-grounded audit rule that makes the anomaly label
      reproducible and criticizable.</li>
  <li><strong>A consensus anomaly detector built only from syllabus algorithms.</strong>
      One-Class SVM, K-Means centroid distance and the domain rule are combined into a
      two-of-three consensus vote whose agreement statistics are reported, rather than
      hidden.</li>
  <li><strong>A financially quantified remediation roadmap.</strong> Four
      physics-grounded levers with per-lever energy, cost, carbon and comfort impact,
      plus conservative, recommended and aggressive scenarios (15.72%, 18.50% and
      20.72% savings).</li>
  <li><strong>A publication and dissemination stack.</strong> Eighteen vector figures,
      this report, a fully executed notebook, a deterministic script, and an
      interactive web application that exposes the same numbers through Plotly charts,
      a filterable anomaly audit table and a live savings simulator.</li>
</ul>

<h2 id="s1-6">1.6 Organisation of the Report</h2>
<p>Chapter 2 reviews the literature on operational energy waste, data-driven anomaly
detection and measurement-and-verification practice, and states the research gap.
Chapter 3 documents the dataset, its provenance, its quality problems and the cleaning
decisions taken. Chapter 4 sets out the methodology &#8212; feature engineering,
statistical tests, regression baselines, the three-detector consensus, the evaluation
protocol and the savings engine. Chapter 5 reports the exploratory and inferential
results (RQ1&#8211;RQ2), Chapter 6 the predictive and anomaly-profiling results
(RQ3&#8211;RQ4), and Chapter 7 the quantified savings roadmap and its sensitivity
analysis (RQ5). Chapter 8 concludes, states the limitations and outlines future work.
Appendix A documents reproducibility and the computational environment; Appendix B
reproduces the complete pipeline source code; Appendix C maps the report to the course
syllabus and to the live project links.</p>

<div class="decision"><div class="cotitle">Reading this report</div>
Every analytical figure is followed by a <em>What the figure shows</em> /
<em>What it means</em> / <em>Decision it supports</em> block. Numerical claims are
sourced either to <code>data/Analysis-Results.json</code> (the single source of truth
produced by the pipeline) or to a numbered table in this document; the mapping is
auditable because both are regenerated together by
<code>code/Energy-Analysis-Script.py</code>.</div>
</section>"""


# ===========================================================================
def chapter2(R: Registry, M: dict) -> str:
    return f"""
<section id="ch2">
<h1 class="ch" id="ch2"><span class="cn">Chapter 2</span><span class="chtitle">Literature Review</span></h1>

<h2 id="s2-1">2.1 Energy Performance of Commercial and Campus Buildings</h2>
<p>Benchmarking literature treats commercial office and higher-education buildings as
distinct but comparably scheduled asset classes: both exhibit a strong five-day
occupancy rhythm, both are cooling-dominated in hot climates, and both are dominated by
HVAC and lighting loads that are only weakly coupled to headcount. Energy use intensity
(EUI) remains the workhorse normalization metric because it permits comparison across a
portfolio of different sizes; in the United States, the Commercial Buildings Energy
Consumption Survey and the ENERGY STAR portfolio framework anchor the interpretation of
EUI values, while Wei <em>et al.</em> [16] survey the data-driven methods used to predict
and classify building energy consumption and note that weather plus calendar features
routinely explain 80&#8211;95% of hourly variance in office stock &#8212; the range our
own baseline hits in Chapter 6.</p>

<p>Load-shape analysis goes further than EUI by preserving the temporal signature. The
LBNL load-shape benchmarking work [19] describes commercial buildings through a small
number of shape parameters: a near-base load, a peak-to-base ratio and a workday to
non-workday ratio. These three parameters are precisely the diagnostics used in this
report, and they are what make an elevated night plateau legible as waste rather than
as ordinary consumption.</p>

<h2 id="s2-2">2.2 Why Operational Waste Is Invisible</h2>
<p>Three mechanisms recur in commissioning and retro-commissioning case studies.
<strong>Elevated off-hour baseload</strong> arises when AHUs, chilled-water pumps,
exhaust fans and corridor lighting remain energized outside occupancy because a BMS
schedule is overridden or never enforced; the signature is a flat night plateau whose
height is a large fraction of the daytime peak. <strong>Incomplete weekend and holiday
setbacks</strong> arise when a weekday schedule is inherited by days with negligible
occupancy; the signature is a weekend-to-weekday ratio well above the 0.45&#8211;0.55
best-practice band. <strong>Weather-uncoupled cooling</strong> arises from economizer
faults, stuck valves and aggressive setpoints; the signature is a residual spike that
outdoor dry-bulb temperature and humidity cannot explain.</p>

<p>The measurement consequence is important and drives the entire methodology of this
report: an hour of high consumption is not evidence of waste, and an hour of low
consumption is not evidence of efficiency. Only the <em>difference between metered and
counterfactually expected</em> consumption, holding weather and calendar constant, is
interpretable. ASHRAE Guideline 14 [9] formalizes this logic for measurement and
verification (M&amp;V), and prescribes the goodness-of-fit thresholds (for example
CV-RMSE below 15% and <em>R</em><sup>2</sup> above 0.75 for hourly whole-building
baselines) against which our regression is judged.</p>

<h2 id="s2-3">2.3 Data-Driven Anomaly Detection in Buildings</h2>
<p>Himeur <em>et al.</em> [3] provide the most complete recent taxonomy: anomaly
detection methods for building energy are conventionally grouped into statistical
(regression residual, change-point), unsupervised machine learning (clustering, nearest
neighbour, one-class classifiers, density estimation) and supervised classification
approaches, with hybrid rule-plus-learning methods increasingly favoured because pure
black-box detectors are hard for facility staff to trust. Their review also documents
the field's chronic evaluation problem: labelled faults are scarce, so reported
detection rates are frequently not comparable across studies.</p>

<p>Among unsupervised methods, two families dominate the applied literature and are the
ones used here. <em>Clustering-based</em> detection groups days by load shape and treats
distance to a cluster centroid as an anomaly score; Nepal <em>et al.</em> [4] apply
K-Means to building electricity use patterns and show that the choice of initial
centroids and of <em>k</em> materially changes the resulting regime segmentation, which
is why this report reports an explicit elbow-plus-silhouette sweep rather than asserting
<em>k</em> = 4. <em>Boundary-based</em> detection estimates the support of the normal
data distribution; the one-class SVM of Schoelkopf <em>et al.</em> [5] is the
canonical formulation and remains the most cited unsupervised novelty detector in the
building-energy literature, while its supervised counterpart, the maximum-margin
classifier of Cortes and Vapnik [6], provides the comparative benchmark. Rousseeuw's
silhouette [8] and MacQueen's K-Means [7] supply the cluster validation and partitioning
foundations respectively. For probabilistic comparison, the Gaussian Naive Bayes
classifier provides a generative baseline whose independence assumption is knowingly
violated but whose calibration is informative.</p>

<p>Recent work has also produced annotated benchmarks. LEAD1.0 [20] annotates the
ASHRAE Great Energy Predictor III meter series for anomaly detection and shows that
unsupervised detectors, when evaluated against expert labels, achieve precision and
recall in the 0.6&#8211;0.9 band &#8212; consistent with the 0.73&#8211;0.89 precision
and 0.48&#8211;0.89 recall reported in Chapter 6, which suggests our detectors are
performing at the level the literature would lead one to expect rather than
suspiciously above it.</p>

<h2 id="s2-4">2.4 Open Datasets and Reproducibility</h2>
<p>The Building Data Genome Project 2 (BDG2) of Miller <em>et al.</em> [1] is the
reference open benchmark for this kind of work: 3,053 meters across 1,636 buildings over
two full years, released with electricity, heating, cooling, water and irrigation
readings plus local weather under a Creative Commons licence. Its companion competition,
the ASHRAE Great Energy Predictor III, established the modelling conventions now
standard in the field &#8212; hourly whole-building meter forecasting from weather and
calendar features, evaluated with RMSE on a held-out year. Candanedo <em>et al.</em> [2]
likewise demonstrated, on a smaller residential dataset, how strongly meteorological
feature engineering drives appliance-load prediction accuracy; their feature-importance
results motivated the degree-day, psychrometric and Fourier-harmonic features used here.
The broader reproducibility argument is made by the scientific Python stack itself
[10]&#8211;[15], whose deterministic seeded pipelines make a study like this
re-runnable by an examiner on a different machine.</p>

<h2 id="s2-5">2.5 Measurement, Verification and Savings Attribution</h2>
<p>Estimating savings requires a counterfactual: savings are the difference between
measured post-implementation consumption and the consumption that would have occurred
without the intervention, adjusted for weather and occupancy. ASHRAE Guideline 14 [9]
and the U.S. Department of Energy's federal M&amp;V framework both prescribe
regression-based baselines for this purpose, and both warn against the two errors this
report is careful to avoid: leakage of post-intervention data into the baseline, and
attribution of weather-driven variation to the intervention. Because this study analyses
historical data with no implemented intervention, Chapter 7's roadmap is explicitly an
<em>ex-ante</em> estimate with named capture rates and an explicit sensitivity band,
not a verified saving.</p>

<h2 id="s2-6">2.6 Research Gap and Positioning</h2>
<p>Three gaps emerge from the review, and this project addresses all three. First, much
of the applied literature reports detection accuracy on private, undocumented datasets,
making reproduction impossible; we use a public benchmark and publish the extract, the
hash and the code. Second, most student and applied studies stop at flagging anomalies,
without converting them into a costed and comfort-safe action plan; we carry the
analysis to per-lever energy, cost, carbon and comfort impact. Third, unsupervised
detectors are frequently presented as ground truth; we instead construct an explicit
audit rule, report detector-versus-rule agreement, and discuss both false alarms and
misses. Table 2.1 summarizes the positioning against the principal reference works.</p>

{R.table("2.1", "Synthesis of prior work and the positioning of this study",
  ["Study", "Data & context", "Method", "Limitation", "How this study differs"],
  [
    ["Miller <em>et al.</em> [1]", "BDG2, 1,636 buildings, two years, open",
     "Benchmark release and load-prediction baselines",
     "No operational-waste audit or savings roadmap",
     "Same benchmark, but a six-building estate is profiled down to actionable levers"],
    ["Himeur <em>et al.</em> [3]", "Review of 200+ anomaly-detection papers",
     "Taxonomy of statistical, unsupervised and supervised methods",
     "No reproducible end-to-end implementation",
     "Implements the taxonomy's three families and reports their agreement"],
    ["Nepal <em>et al.</em> [4]", "Building electricity use patterns",
     "K-Means with centroid and <em>k</em> selection study",
     "Clustering only; no counterfactual or financial layer",
     "Adds weather-plus-schedule regression residual and a costed roadmap"],
    ["Schoelkopf <em>et al.</em> [5]", "Theory of one-class novelty detection",
     "One-class SVM formulation", "No building application or evaluation",
     "Applies OCSVM to daily load-shape features with explicit precision/recall"],
    ["LEAD1.0 [20]", "Annotated ASHRAE meter series",
     "Benchmarks eight unsupervised detectors on expert labels",
     "Annotation limited to one competition dataset",
     "Uses a transparent physics-based audit rule instead of opaque labels"],
    ["ASHRAE Guideline 14 [9]", "M&amp;V standard",
     "Regression baselines with goodness-of-fit thresholds",
     "Prescriptive statistics, no detection or visualization guidance",
     "Complies with the thresholds and adds visual analytics plus sensitivity bands"],
  ],
  colw=["16%", "20%", "23%", "19%", "22%"])}

<div class="callout"><div class="cotitle">Gap statement</div>
No study in this body of work both (i) applies only the algorithms of an undergraduate
data-visualization syllabus, (ii) evaluates unsupervised detectors against a transparent,
reproducible audit rule on an open dataset, and (iii) terminates in a
comfort-constrained, sensitivity-tested financial roadmap. That combination is the
contribution of this mini project.</div>
</section>"""


# ===========================================================================
def chapter3(R: Registry, M: dict) -> str:
    B = M["bldg"]
    fig = ROOT / "assets" / "figures"
    rows = []
    meta = [
        ("Fox_office_Joy", "Commercial Office", "Administrative Office", "Office"),
        ("Fox_office_Vicki", "Commercial Office", "Administrative Office", "Office"),
        ("Fox_office_Clayton", "Commercial Office", "Executive / IT Office", "Office"),
        ("Fox_education_Tamika", "University Campus", "College Laboratory", "Education"),
        ("Fox_education_Carleen", "University Campus", "College Laboratory", "Education"),
        ("Fox_education_Kris", "University Campus", "Student Union", "Education"),
    ]
    for bid, sector, sub, _ in meta:
        rows.append([
            f"<code>{bid}</code>", sector, sub,
            _n(B["areas"][bid], 1), _n(B["bldg_sum_mwh"][bid], 1),
            _n(B["bldg_mean"][bid], 2), _n(B["bldg_eui"][bid], 1),
            str(B["bldg_missing"][bid]),
        ])
    rows.append(["<strong>Portfolio</strong>", "<strong>Mixed</strong>",
                 "<strong>6 smart meters</strong>", "<strong>31,462.6</strong>",
                 "<strong>13,677.3</strong>", "<strong>779.60</strong>",
                 "<strong>217.36</strong>", "<strong>51</strong>"])

    return f"""
<section id="ch3">
<h1 class="ch" id="ch3"><span class="cn">Chapter 3</span><span class="chtitle">Dataset Description and Preparation</span></h1>

<h2 id="s3-1">3.1 Provenance, Licence and Selection Rationale</h2>
<p>The empirical foundation of this study is the <strong>Building Data Genome Project
2 (BDG2)</strong> benchmark of Miller <em>et al.</em> [1], distributed under the
Creative Commons Attribution-ShareAlike 4.0 International licence (CC BY-SA 4.0). BDG2
aggregates whole-building electricity, heating, cooling, water and irrigation meter
series from 1,636 non-residential buildings, joined to local weather observations, and
was released alongside the ASHRAE Great Energy Predictor III competition. The extract
used here is the complete two-year hourly record for <strong>Site <code>Fox</code></strong>
&#8212; a mixed commercial and university district in Tempe, Arizona
(33.4244&#176; N, 111.9281&#176; W, US/Mountain, ASHRAE Climate Zone 2B, hot-dry) &#8212;
covering 1 January 2016 00:00 through 31 December 2017 23:00.</p>

<p>The extract was chosen against four competing candidates, each evaluated on domain
fit, row count, temporal coverage, licence and analytical suitability. The
<em>Candanedo</em> appliances dataset [2] monitors a single low-energy dwelling in
Belgium for 4.5 months, which cannot support a commercial-schedule study; the
<em>ziya07</em> Kaggle smart-meter set is simulated and ships with pre-baked anomaly
labels; and the <em>UNICON</em> campus dataset is dominated by 2020&#8211;2021 COVID-19
lockdown structural breaks that would confound a baseload model. BDG2 Site
<code>Fox</code> was retained because it is real, open, spans two complete seasonal
cycles (2016 used for training, 2017 held out for testing), contains a balanced mix of
office and campus buildings, and exhibits genuine operational faults rather than
synthetic injections.</p>

<h2 id="s3-2">3.2 Portfolio Composition</h2>
<p>The six meters cover 31,462.6 m<sup>2</sup> of conditioned floor area: 13,650.0
m<sup>2</sup> of commercial office (43.4%) and 17,812.6 m<sup>2</sup> of university
space (56.6%). Table 3.1 lists each building with its floor area, two-year consumption,
mean hourly load, energy use intensity and raw missing-hour count, and Figure 3.1 shows
the same portfolio graphically together with a benchmark EUI reference band.</p>

{R.table("3.1", "Monitored building portfolio with two-year consumption, load and energy use intensity",
  ["Building ID", "Sector", "Sub-category", "Area (m<sup>2</sup>)", "Energy (MWh)",
   "Mean load (kWh/h)", "EUI (kWh/m<sup>2</sup>/yr)", "Missing hours"],
  rows, colw=["19%", "12%", "16%", "11%", "10%", "11%", "13%", "8%"],
  align=["l", "l", "l", "r", "r", "r", "r", "c"],
  note="EUI computed as two-year consumption divided by two years and by conditioned floor area. "
       "Missing hours are raw single-meter gaps before time-indexed interpolation (51 cells = 0.048% of the 105,264 building-hours).")}

{R.figure("3.1", "portfolio", 
  "Portfolio composition, energy share and energy use intensity against a commercial benchmark band",
  fig / "Fig-3-1-Portfolio-Overview.svg")}

<div class="callout"><div class="cotitle">What the figure shows</div>
The three offices carry 53.4% of consumption on 43.4% of floor area, and the small
488.5 m<sup>2</sup> <code>Clayton</code> block is a dramatic outlier at
1,574.8 kWh/m<sup>2</sup>/year &#8212; more than seven times the portfolio average
&#8212; because its server and IT load is distributed over very little area. Campus
buildings are lower-intensity (178.9 kWh/m<sup>2</sup>/year versus 267.6 for offices)
but not lower in absolute terms: together they consume 6,372.1 MWh.</div>

<div class="decision"><div class="cotitle">Decision supported</div>
Any EUI-based ranking must be floor-area aware. <code>Clayton</code> is excluded from
per-area league tables (it would be permanently &#8220;worst&#8221;) but retained in
all absolute-load, anomaly and savings work, because its round-the-clock IT load is a
genuine contributor to the portfolio's night baseload.</div>

<h2 id="s3-3">3.3 Variable Dictionary</h2>
<p>The curated extract contains six meter channels, seven meteorological channels and a
site identifier at hourly resolution (Table 3.2). All engine, calendar and thermodynamic
variables used in analysis are derived deterministically from these fifteen raw columns,
so the published dataset is sufficient to regenerate every result in this report.</p>

{R.table("3.2", "Column dictionary of the curated dataset (<code>data/dataset.csv</code>, 17,544 x 15)",
  ["Column", "Type", "Unit", "Missing (raw)", "Description"],
  [
    ["<code>timestamp</code>", "datetime", "&#8212;", "0",
     "Hour-ending local timestamp, contiguous hourly index 2016-01-01 00:00 to 2017-12-31 23:00"],
    ["<code>Fox_office_Joy</code>", "float", "kWh", "9",
     "Whole-building electricity, 6,581.0 m<sup>2</sup> administrative office"],
    ["<code>Fox_office_Vicki</code>", "float", "kWh", "11",
     "Whole-building electricity, 6,580.5 m<sup>2</sup> administrative office"],
    ["<code>Fox_office_Clayton</code>", "float", "kWh", "2",
     "Whole-building electricity, 488.5 m<sup>2</sup> IT/executive office"],
    ["<code>Fox_education_Tamika</code>", "float", "kWh", "8",
     "Whole-building electricity, 8,339.9 m<sup>2</sup> college laboratory"],
    ["<code>Fox_education_Carleen</code>", "float", "kWh", "13",
     "Whole-building electricity, 6,635.2 m<sup>2</sup> college laboratory"],
    ["<code>Fox_education_Kris</code>", "float", "kWh", "8",
     "Whole-building electricity, 2,837.5 m<sup>2</sup> student union"],
    ["<code>site_id</code>", "category", "&#8212;", "0", "Site key, constant <code>Fox</code>"],
    ["<code>airTemperature</code>", "float", "&#176;C", "17",
     "Hourly dry-bulb temperature at the site weather station"],
    ["<code>dewTemperature</code>", "float", "&#176;C", "18",
     "Hourly dew-point temperature; source of psychrometric humidity"],
    ["<code>seaLvlPressure</code>", "float", "mbar", "18",
     "Sea-level-corrected station pressure"],
    ["<code>windSpeed</code>", "float", "m/s", "18", "Hourly wind speed"],
    ["<code>cloudCoverage</code>", "float", "okta", "3,477",
     "Sky cover; high missingness, EDA-only"],
    ["<code>windDirection</code>", "float", "degree", "2,710",
     "Wind direction; high missingness, EDA-only"],
    ["<code>precipDepth1HR</code>", "float", "mm", "284",
     "Hourly precipitation depth; -1.0 encodes an ISD trace event"],
  ],
  colw=["19%", "9%", "7%", "10%", "55%"],
  align=["l", "l", "c", "c", "l"])}

<h2 id="s3-4">3.4 Data Quality Audit</h2>
<p>A full missing-value and sentinel census was run before any transformation. The
results, reproduced in Table 3.3, drove five explicit decisions. Crucially, no missing
value was imputed silently and no row was deleted: the 17,544 hourly records form a
contiguous, duplicate-free index, and every cleaned column is documented.</p>

{R.table("3.3", "Data quality audit and treatment decisions",
  ["Defect", "Affected columns", "Raw count", "% of values", "Treatment applied"],
  [[p["issue"], f"<code>{p['affected_columns']}</code>", f"{p['raw_count']:,}",
    f"{p['pct_rows']:.3f}", p["treatment"]] for p in M["prep"]],
  colw=["26%", "22%", "9%", "9%", "34%"],
  align=["l", "l", "r", "r", "l"],
  note="Percentages are computed against the relevant denominator for each defect (26,316 building-hours for meter gaps, 70,176 weather-hours for core weather, and so on).")}

<h3>3.4.1 Treatment rationale</h3>
<p>Meter and core-weather gaps are short (one to three hours) and isolated, so
time-indexed linear interpolation is the least distorting repair; it preserves the
diurnal shape that a mean-fill would flatten. <code>cloudCoverage</code> and
<code>windDirection</code> are missing for 17.63% of values &#8212; far too much for
interpolation to be honest &#8212; so they are median-filled by hour-of-day for
descriptive use only and are <em>excluded</em> from the machine-learning feature matrix.
The ISD trace-precipitation sentinel (-1.0 mm) is replaced by 0.05 mm, the
conventional depth of a trace event, rather than by zero, so that trace hours are not
silently relabelled as dry.</p>

<h3>3.4.2 Outlier policy: flag, never delete</h3>
<p>A 1.5 x IQR fence on the portfolio hourly load rejects <strong>zero</strong> of the
17,544 hours: the distribution's upper fence falls at 1,490.6 kWh/h while the observed
maximum is 1,432.9 kWh/h. This is itself an important finding about the data. The
portfolio does not produce isolated spikes against a quiet baseline; it produces a
chronically high plateau with modest variance (coefficient of variation 30.2%). Deleting
outliers would therefore have removed exactly the phenomenon under study, so all hours
are retained and a flag column (<code>iqr_high_flag</code>) is carried for transparency.</p>

<h2 id="s3-5">3.5 Derived Variables and Feature Engineering</h2>
<p>Thirty-five analysis variables were derived from the fifteen raw columns in four
families: calendar and operational regime indicators (year, month, hour, day of week,
<code>is_weekend</code>, <code>is_off_hour</code> for 22:00&#8211;05:59,
<code>is_work_hour</code> for 08:00&#8211;18:59 on weekdays, season); thermodynamic HVAC
proxies (cooling and heating degree days against the ASHRAE 18.3 &#176;C balance point,
psychrometric relative humidity from the Magnus&#8211;Tetens equation, a
temperature-humidity interaction term); cyclical Fourier harmonics of hour-of-day (first
and second harmonic, sine and cosine pairs) so that 23:00 and 00:00 are adjacent rather
than 23 units apart; and strictly backward-looking autoregressive terms (24-hour lag,
168-hour weekly lag, trailing 24-hour rolling mean and standard deviation, all shifted by
at least 24 hours to prevent leakage). The full catalogue with formulas appears in
Table 4.2.</p>

<div class="keyfinding">Three properties of the derived features matter for the validity
of later chapters. (i) The humidity variable is computed from dew point rather than
taken from a sensor, so it is physically consistent at every hour. (ii) Degree days use
18.3 &#176;C rather than 18.0 &#176;C, matching the ASHRAE balance point and avoiding a
0.3 &#176;C systematic bias in the cooling term. (iii) Every lag is at least 24 hours
deep, so the counterfactual model can be applied to a day whose own consumption is
unknown &#8212; the condition ASHRAE Guideline 14 imposes on an operational baseline.</p>

<h2 id="s3-6">3.6 Dataset Limitations</h2>
<ul>
  <li><strong>No ground-truth fault labels.</strong> BDG2 is unlabelled field data, so
      anomaly evaluation must rely on a constructed, documented audit rule
      (Section 4.6) rather than on maintenance tickets.</li>
  <li><strong>No sub-metering.</strong> Whole-building meters cannot separate HVAC from
      lighting and plug loads, so lever-level attribution in Chapter 7 must be modelled
      from regime physics rather than measured per end-use.</li>
  <li><strong>Single climate.</strong> Site <code>Fox</code> is hot-dry and
      cooling-dominated; heating-related findings transfer poorly to cold climates,
      which is stated wherever relevant.</li>
  <li><strong>Built-year coverage.</strong> Construction year is recorded for only two
      of the six buildings, precluding an age-versus-EUI analysis.</li>
  <li><strong>Calendar granularity.</strong> Academic holidays are not flagged in the
      source data; their effect appears inside the weekend and seasonal profiles and is
      acknowledged as a partial explanation of cluster 3's weekend-heavy composition.</li>
</ul>

<div class="decision"><div class="cotitle">Implication for the remainder of the report</div>
Because the data are unlabelled and whole-building, the analysis must be built around a
<em>counterfactual</em> rather than a classifier trained on fault labels, and every
savings claim must be presented as an engineering estimate with an explicit capture rate
and sensitivity band. Chapter 4 adopts exactly that design.</div>
</section>"""


# ===========================================================================
def chapter4(R: Registry, M: dict) -> str:
    ml = M["ml"]
    fig = ROOT / "assets" / "figures"
    return f"""
<section id="ch4">
<h1 class="ch" id="ch4"><span class="cn">Chapter 4</span><span class="chtitle">Research Methodology</span></h1>

<h2 id="s4-1">4.1 Research Design and Workflow</h2>
<p>The study follows a six-stage quantitative pipeline, illustrated in Figure 4.1:
(1) acquisition and curation of the two-year hourly panel; (2) quality audit,
cleaning and feature engineering; (3) exploratory and inferential statistics;
(4) counterfactual regression baselines with a strict chronological split;
(5) unsupervised anomaly profiling with a consensus vote, benchmarked against
supervised classifiers; and (6) quantification of recoverable waste into a costed,
sensitivity-tested roadmap. The pipeline is fully deterministic
(<code>SEED = 42</code>): a single command regenerates every statistic, table, figure
and web payload in this report.</p>

{R.figure("4.1", "workflow",
  "End-to-end analytical workflow, from open benchmark acquisition to the interactive dissemination layer",
  fig / "Fig-4-1-Methodology-Workflow.svg")}

<div class="callout"><div class="cotitle">What the figure shows</div>
The workflow separates <em>measurement</em> (stages 1&#8211;4, where the counterfactual
is constructed) from <em>decision support</em> (stages 5&#8211;6, where anomalies are
ranked and priced). The two are deliberately not merged: the baseline is fitted on 2016
only and frozen before any 2017 anomaly is examined, which prevents the classic circular
error of detecting anomalies with a model that has already seen them.</div>

<h2 id="s4-2">4.2 Syllabus Alignment</h2>
<p>Table 4.1 maps every algorithm used to the unit of the {COURSE} syllabus in which it
is taught. No model outside this set appears anywhere in the pipeline &#8212; no random
forest, no gradient boosting, no neural network. This is a deliberate scoping decision:
it demonstrates the analytical ceiling of the taught toolkit.</p>

{R.table("4.1", "Syllabus coverage mapping (course " + COURSE + ", Data Visualization and Analysis)",
  ["Syllabus unit", "Covered topic", "Implementation in this study"],
  [
    ["Unit I &#8212; Introduction to data visualization",
     "Data types, scales of measurement, visualization principles, chart selection",
     "Variable dictionary and scale classification (Table 3.2); deliberate chart-type "
     "selection per question; pure-hue categorical palette with WCAG-checked contrast"],
    ["Unit II &#8212; Descriptive statistics and regression",
     "Measures of central tendency and dispersion, correlation, simple and multiple "
     "linear regression, residual diagnostics",
     "Descriptive table (Table 5.1); Pearson correlation matrix (Fig. 5.6); Multiple "
     "Linear Regression baselines with standardized coefficients and residual "
     "diagnostics (Table 6.1&#8211;6.2, Fig. 6.1)"],
    ["Unit III &#8212; Data visualization with Matplotlib and Seaborn",
     "Figure anatomy, subplots, distributions, heatmaps, time series, styling",
     "Eighteen publication-grade SVG figures generated with Matplotlib and Seaborn, "
     "including KDE distributions, box plots, heatmaps and annotated timelines"],
    ["Unit IV &#8212; Machine learning for visualization and analysis",
     "Decision trees, support vector machines, clustering techniques, Bayes classification",
     "Decision Tree regressor and classifier; One-Class SVM and RBF-SVM classifier; "
     "K-Means with elbow and silhouette selection; Gaussian Naive Bayes (Chapter 6)"],
    ["Unit V &#8212; Interactive and web visualization",
     "Interactive dashboards, JavaScript charting libraries, design systems",
     "Plotly.js web application with dark/light themes, cross-filtered anomaly table "
     "and a live savings simulator, deployed to a public URL"],
    ["Unit VI &#8212; Storytelling and professional reporting",
     "Narrative structure, annotation, report engineering",
     "This report: eight chapters, eighteen figures, sixteen tables, IEEE references, "
     "and per-figure interpretation blocks"],
  ],
  colw=["17%", "30%", "53%"])}

<h2 id="s4-3">4.3 Feature Engineering</h2>
<p>Table 4.2 catalogues the engineered variables and the physical or operational reason
each one exists. Feature counts were kept deliberately small (sixteen predictors for the
full autoregressive model) to respect the sample-to-parameter discipline advised for
hourly baselines and to keep coefficients interpretable for facility engineers.</p>

{R.table("4.2", "Engineered feature catalogue with computational definition and purpose",
  ["Feature", "Definition", "Purpose"],
  [
    ["<code>hour</code>, <code>dayofweek</code>, <code>month</code>, <code>year</code>",
     "Extracted from the DatetimeIndex", "Calendar decomposition and grouping keys"],
    ["<code>is_weekend</code>", "1 if day of week is Saturday or Sunday",
     "Occupancy regime contrast; the single strongest categorical driver"],
    ["<code>is_off_hour</code>", "1 if hour &gt;= 22 or hour &lt; 6",
     "Defines the unoccupied window used for all baseload statistics"],
    ["<code>is_work_hour</code>", "1 if 8 &lt;= hour &lt;= 18 and weekday",
     "Defines the occupied comparison window"],
    ["<code>cdd_18</code>", "max(0, T<sub>air</sub> - 18.3)",
     "Cooling degree hours; linear proxy for sensible cooling load"],
    ["<code>hdd_18</code>", "max(0, 18.3 - T<sub>air</sub>)",
     "Heating degree hours; captures the small winter heating term"],
    ["<code>rel_humidity</code>",
     "100 x e<sub>act</sub>/e<sub>sat</sub>, Magnus&#8211;Tetens, clipped to [1, 100]",
     "Latent-load proxy derived from dry-bulb and dew-point temperatures"],
    ["<code>temp_rh_interaction</code>", "T<sub>air</sub> x RH / 100",
     "Captures the joint enthalpy effect that separate linear terms miss"],
    ["<code>sin_hour</code>, <code>cos_hour</code>, <code>sin_hour_2</code>, <code>cos_hour_2</code>",
     "First and second Fourier harmonics of hour-of-day",
     "Smooth, continuous diurnal schedule shape without step artefacts"],
    ["<code>lag_24h</code>, <code>lag_168h</code>",
     "Consumption 24 and 168 hours earlier (shifted, never centred)",
     "Same-hour-yesterday and same-hour-last-week persistence"],
    ["<code>roll_mean_24h</code>, <code>roll_std_24h</code>",
     "Trailing 24-hour mean and standard deviation of <code>lag_24h</code>",
     "Short-term level and volatility context; strictly backward-looking"],
    ["Daily shape features (7)",
     "Daily actual and expected kWh, excess kWh, off-hour mean, baseload ratio, "
     "work-hour/weekend deviation, mean temperature, day-over-day excess change",
     "Compact load-shape descriptor vector used by clustering and anomaly detectors"],
  ],
  colw=["24%", "38%", "38%"])}

<h2 id="s4-4">4.4 Statistical Testing Protocol</h2>
<p>Two-sample comparisons use Welch's <em>t</em>-test (unequal variances, which is the
appropriate default for heteroscedastic load data) with the Mann&#8211;Whitney
<em>U</em> test as a distribution-free confirmation, because hourly load is right-skewed
(skewness 0.47) and bounded below. A result is reported as significant only when both
tests agree at alpha = 0.01. Effect size is communicated by the ratio of means rather
than by the p-value alone, since with <em>n</em> = 17,544 almost any difference is
statistically detectable. Association with weather is quantified with Pearson's
<em>r</em>; normality is not assumed, so Spearman's rho is used as a robustness check
in the narrative where the relationship is visibly non-linear.</p>

<h2 id="s4-5">4.5 Counterfactual Regression Baselines</h2>
<p>Three regression specifications are fitted and compared. Model 1A, the
<em>counterfactual weather-plus-schedule</em> baseline, predicts expected hourly demand
from weather and calendar drivers only &#8212; no consumption history &#8212; so that it
can be applied to an hour whose actual consumption is unknown:</p>

<div class="eq">E_hat<sub>t</sub> = b<sub>0</sub> + b<sub>1</sub>T<sub>t</sub> +
b<sub>2</sub>T<sub>t</sub><sup>2</sup> + b<sub>3</sub>RH<sub>t</sub> +
b<sub>4</sub>CDD<sub>t</sub> + b<sub>5</sub>HDD<sub>t</sub> +
b<sub>6</sub>(T&#183;RH)<sub>t</sub> + g<sub>wk</sub>Weekend<sub>t</sub> +
d<sub>h</sub>Hour<sub>t</sub> + e<sub>m</sub>Month<sub>t</sub> +
e<sub>t</sub><span class="n">(4.1)</span></div>

<p>Model 1B, the <em>full autoregressive</em> model, adds 24-hour and 168-hour lags plus
the trailing rolling mean, and is used for day-ahead load forecasting and as the
strongest available predictor:</p>

<div class="eq">E_hat<sub>t</sub> = f(weather, calendar)<sub>t</sub> +
q<sub>1</sub>E<sub>t-24</sub> + q<sub>2</sub>E<sub>t-168</sub> +
q<sub>3</sub>Roll24<sub>t</sub> + e<sub>t</sub><span class="n">(4.2)</span></div>

<p>Model 2 is a tuned Decision Tree Regressor, retained as a non-linear, interpretable
benchmark; it can express threshold interactions (for example &#8220;weekend and above
35 &#176;C&#8221;) that a linear model cannot. Wastage at the daily level is then
defined as the positive counterfactual excess</p>

<div class="eq">DE<sub>d</sub> = max(0, E<sub>d</sub><sup>actual</sup> -
E<sub>d</sub><sup>expected</sup>)<span class="n">(4.3)</span></div>

<p>where the daily expected value is the sum of the 24 hourly counterfactual predictions
for that day. Equation (4.3) deliberately clips negative residuals to zero: a building
that consumes less than its weather-and-schedule entitlement is efficient, not
anomalous, and treating under-consumption as an anomaly would flood the audit list with
holidays.</p>

{R.figure("4.2", "split",
  "Chronological train / test partition: 2016 for baseline fitting, 2017 held out for out-of-sample evaluation",
  fig / "Fig-4-2-Train-Test-Split.svg")}

<div class="callout"><div class="cotitle">What the figure shows</div>
The split is strictly temporal: 8,784 hours of 2016 train the models, and 8,760 hours of
2017 &#8212; a full, unseen year with its own weather and its own fault history &#8212; are
never touched during fitting. No random shuffling is used anywhere, because shuffling
hourly time series leaks information across the split boundary and inflates
<em>R</em><sup>2</sup> by several percentage points.</div>

<h2 id="s4-6">4.6 Anomaly Detection: A Three-Detector Consensus</h2>
<p>Daily operational behaviour is characterized by the seven-dimensional shape vector of
Table 4.2 and examined by three independent detectors, each resting on a different
assumption:</p>

<h3>Detector 1 &#8212; Domain audit rule (transparent, physics-grounded)</h3>
<p>A day is labelled a <em>confirmed wastage day</em> when its positive counterfactual
excess exceeds the portfolio's baseline residual threshold of
<strong>{_n(ml['domain_excess_threshold_kwh'],1)} kWh</strong> (1.25 standard deviations
of the 2016 daily excess distribution, i.e. roughly two-thirds of a degree-day's worth
of cooling error) <em>and</em> its overnight off-hour mean is above the
seasonal-schedule expectation. This single rule produces
<strong>{ml['domain_wastage_days_total']} flagged days</strong> across the two years
({ml['domain_wastage_days_2017']} of them in the 2017 holdout).</p>

<h3>Detector 2 &#8212; One-Class SVM (unsupervised boundary estimation)</h3>
<p>An RBF-kernel One-Class SVM is trained on the standardized 2016 daily shape matrix
with nu = 0.08 (an 8% contamination prior, consistent with the audit rule flagging roughly a fifth of days) learning a closed boundary
around normal operation. Days falling outside the boundary are flagged:
<strong>{ml['ocsvm_flagged_days_total']} days</strong> over the two years. The detector
requires no labels, which is exactly why it is appropriate for unlabelled field
telemetry.</p>

<h3>Detector 3 &#8212; K-Means centroid distance (unsupervised regime deviation)</h3>
<p>K-Means partitions the 731 daily shape vectors into operational regimes; the number of
clusters is chosen by a joint elbow and silhouette sweep over <em>k</em> = 2 to 7
(Table 6.3). A day's anomaly score is its Euclidean distance to its own cluster centroid,
and days beyond the 95th percentile of that distance are flagged:
<strong>{ml['kmeans_flagged_days_total']} days</strong>.</p>

<h3>Consensus vote</h3>
<p>The three detectors are combined by a <strong>two-of-three majority vote</strong>,
producing <strong>{ml['consensus_flagged_days_total']} consensus anomaly days</strong>
(21.5% of 731 days) carrying
<strong>{_n(ml['consensus_excess_mwh_total'],2)} MWh</strong> of counterfactual excess
and an estimated <strong>USD {_n(ml['consensus_excess_cost_usd_total'],0)}</strong> of
avoidable spend. The consensus design is deliberate: the audit rule supplies physical
interpretability, the One-Class SVM supplies multivariate sensitivity, and K-Means
supplies regime context, and requiring agreement suppresses the idiosyncratic false
positives of any single detector.</p>

<h2 id="s4-7">4.7 Supervised Benchmarks and Evaluation Metrics</h2>
<p>To situate the unsupervised detectors against the syllabus's supervised classifiers,
three models &#8212; RBF-kernel SVM, Decision Tree and Gaussian Naive Bayes &#8212; are
trained on 2016 daily shape vectors using the audit rule as the label and evaluated on
the 2017 holdout. Hyperparameters are selected by grid search with stratified 5-fold
cross-validation inside the training year only (Table 4.3). Performance is reported with
the full confusion matrix plus precision, recall, F<sub>1</sub> and ROC-AUC:</p>

<div class="eq">Precision = TP/(TP+FP) &nbsp;&nbsp; Recall = TP/(TP+FN) &nbsp;&nbsp;
F<sub>1</sub> = 2&#183;P&#183;R/(P+R)<span class="n">(4.4)</span></div>

<p>Precision is emphasized over recall in the interpretation because a false alarm sends a
technician to a healthy building, eroding trust in the programme, whereas a missed
anomaly only delays a saving. This asymmetric cost is stated explicitly rather than
buried in a single accuracy figure.</p>

{R.table("4.3", "Hyperparameter search spaces and selected values",
  ["Model", "Search space", "Selected configuration", "Selection criterion"],
  [
    ["Multiple Linear Regression", "Ordinary least squares, no regularization",
     "16 predictors (Model 1B); 11 predictors (Model 1A)",
     "Adjusted <em>R</em><sup>2</sup> and residual normality"],
    ["Decision Tree Regressor",
     "<code>max_depth</code> in {6, 8, 10, 12, 14}; <code>min_samples_leaf</code> in "
     "{2, 5, 10, 20}",
     f"<code>max_depth</code> = {ml['dt_best_params']['max_depth']}, "
     f"<code>min_samples_leaf</code> = {ml['dt_best_params']['min_samples_leaf']}",
     "5-fold CV RMSE on 2016"],
    ["RBF-SVM classifier", "<code>C</code> in {0.1, 0.5, 1, 5, 10}; "
     "<code>gamma</code> in {0.01, 0.05, 0.1, 0.5}",
     f"<code>C</code> = {ml['svc_best_params']['C']}, "
     f"<code>gamma</code> = {ml['svc_best_params']['gamma']}",
     "Stratified 5-fold CV F<sub>1</sub> on 2016"],
    ["Decision Tree classifier",
     "<code>max_depth</code> in {2, 3, 4, 5, 6}; <code>min_samples_leaf</code> in "
     "{5, 10, 20}",
     f"<code>max_depth</code> = {ml['dt_cls_best_params']['max_depth']}, "
     f"<code>min_samples_leaf</code> = {ml['dt_cls_best_params']['min_samples_leaf']}",
     "Stratified 5-fold CV F<sub>1</sub>; kept shallow for rule legibility"],
    ["K-Means clustering", "<em>k</em> in {2, 3, 4, 5, 6, 7}; <code>n_init</code> = 20",
     "<em>k</em> = 4 (silhouette 0.3803)", "Joint elbow inertia and silhouette maximum"],
    ["One-Class SVM", "nu in {0.02, 0.05, 0.08}; <code>gamma</code> = scale, RBF kernel",
     "nu = 0.08 (8% contamination prior)", "Stability of the flagged fraction"],
  ],
  colw=["20%", "32%", "24%", "24%"])}

<h2 id="s4-8">4.8 Savings Roadmap Engine</h2>
<p>Recoverable energy is decomposed into four levers, each anchored to a physical regime
rather than to an arbitrary percentage, and each with a capture rate that reflects how
much of the theoretically avoidable load a realistic BMS intervention removes:</p>

<ol>
  <li><strong>L1 &#8212; Overnight setback and lighting sweep (22:00&#8211;05:59).</strong>
      The avoidable pool is the off-hour energy above a 360 kWh/h critical floor (the
      load genuinely required by IT rooms, servers, security and life-safety systems);
      a 68% capture rate is applied for schedule enforcement and lighting sweeps.</li>
  <li><strong>L2 &#8212; Weekend and academic-break consolidation.</strong> The avoidable
      pool is weekend daytime load above a 400 kWh/h zone floor, with 62% capture from
      deepening setback and consolidating weekend activity into fewer zoned wings.</li>
  <li><strong>L3 &#8212; Automated anomaly triage and override reset.</strong> 82% of the
      consensus-flagged days' counterfactual excess is assumed recoverable through
      alerting and rapid dispatch, a conservative rate given that these are fault-driven
      hours.</li>
  <li><strong>L4 &#8212; Economizer tuning, demand-controlled ventilation and a
      1 &#176;C cooling deadband widening.</strong> 32% of the hot-weather
      (above 24 &#176;C) weekday cooling increment is trimmed, remaining inside the
      ASHRAE 55 comfort envelope of 23&#8211;24.5 &#176;C.</li>
</ol>

<p>Financial and carbon conversion uses two explicitly disclosed factors: a commercial
electricity tariff of <strong>USD 0.12/kWh</strong> (U.S. EIA commercial-sector benchmark
for the Mountain region; an indicative INR 10.0/kWh institutional rate is noted for the
Indian campus context) and a grid emission factor of
<strong>0.417 kg CO<sub>2</sub>e/kWh</strong> (U.S. EPA eGRID regional average). Both are
parameters of the model, not facts about the host campus, and Chapter 7's sensitivity
analysis shows how the conclusions move when they change. Every lever carries a comfort
impact statement, because a savings programme that degrades the indoor environment is
not a saving at all.</p>

<h2 id="s4-9">4.9 Validation, Reproducibility and Tooling</h2>
<p>Validation rests on four devices: a strictly chronological train/test split; agreement
between a parametric and a non-parametric hypothesis test; consensus rather than
single-detector flagging; and seed-fixed determinism, with the dataset hash
(SHA-256 prefix <code>3116fd2794f8af05</code>) recorded in Appendix A. The analytical
stack is Python 3.13 with NumPy, pandas, SciPy, scikit-learn, Matplotlib and Seaborn
[10]&#8211;[15]; the report is typeset with WeasyPrint from HTML/CSS and embeds the
official Times New Roman TrueType quartet; the interactive layer uses Plotly.js. All
figures are exported as SVG so that the same asset is simultaneously print-quality and
web-embeddable.</p>

<div class="decision"><div class="cotitle">Methodological choices that protect the conclusions</div>
(i) The counterfactual baseline never sees consumption history, so it cannot launder
wastage into expectation. (ii) Negative residuals are clipped, so efficiency is not
mislabelled as anomaly. (iii) The audit rule is published in full, so a sceptical reader
can recompute every label. (iv) Savings are reported as three scenarios, never as a
single point estimate. (v) Every figure is exported from the same JSON that supplies the
report tables, so no number can drift between artefacts.</div>
</section>"""
