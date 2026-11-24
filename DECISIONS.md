# Architectural, Analytical & Engineering Decisions Log (`DECISIONS.md`)

**Project:** Smart Building Energy Wastage & Anomaly Profiling: A Data-Driven Approach Using Smart-Meter and Weather Data  
**Course:** Data Visualization and Analysis (`26CSEM321`) — B.Tech CSE, Year 2, Semester 3, Section 2CSE-4  
**Institution:** IILM University, Greater Noida  
**Lead Repository Name:** `Smart-Building-Energy-Wastage-Anomaly-Profiling-Ayush-Jha-25SCS1003001336`  
**Date:** 25 November 2026

---

## 1. Dataset Selection Decision

- **Chosen Primary Dataset:** **Building Data Genome Project 2 (BDG2)** — published in *Nature Scientific Data* (Miller et al., 2020; DOI: `10.1038/s41597-020-00712-x`) and hosted on Kaggle (`claytonmiller/buildingdatagenomeproject2`) and GitHub (`buds-lab/building-data-genome-project-2`), licensed under **CC BY-SA 4.0**.
- **Analytical Scope (Campus & Commercial Sub-Portfolio):** We extract the two-year hourly smart-meter and meteorological time series (`2016-01-01 00:00:00` to `2017-12-31 23:00:00`, **17,544 hourly records**, 731 calendar days) for a balanced 6-building commercial-and-university district on **Site `Fox`** (Tempe, Arizona metropolitan university & commercial district, ASHRAE Climate Zone 2B, `US/Mountain`):
  1. `Fox_office_Joy` — Commercial / Administrative Office (`6,581.0 m²`)
  2. `Fox_office_Vicki` — Commercial / Administrative Office (`6,580.5 m²`)
  3. `Fox_office_Clayton` — Commercial / Administrative Office (`488.5 m²`)
  4. `Fox_education_Tamika` — University College Laboratory (`8,339.9 m²`)
  5. `Fox_education_Carleen` — University College Laboratory (`6,635.2 m²`)
  6. `Fox_education_Kris` — University Student Union (`2,837.5 m²`)
- **Rationale:**
  - Directly satisfies the problem statement's exact domain: *"a data-driven study of commercial offices and university campuses using smart-meter and weather data"*.
  - Contains **17,544 hourly observations** across two complete seasonal cycles (2016 for baseline training / Year 1, 2017 for out-of-sample testing / Year 2) and **731 daily profiles**, comfortably in the 10k–50k row sweet spot.
  - Strong physical weather-load coupling (`r = 0.751` with outdoor air temperature), clear weekday-vs-weekend occupancy drop, and real operational anomalies (overnight HVAC overrides, weekend cooling spikes, holiday baseload drift).
  - Raw missingness is tiny (<0.08% per smart meter, <0.31% sea-level pressure) yet non-zero, enabling genuine preprocessing documentation without fabricating missing values.
- **Rejected Alternatives:**
  1. *UCI / Kaggle Appliances Energy Prediction (`loveall/appliances-energy-prediction`, Candanedo et al., 2017; 19,735 rows):* Monitored a single residential house in Belgium over 4.5 months rather than commercial offices and university campus buildings; lacks multi-season annual coverage and shows low weekday/weekend commercial schedule contrast.
  2. *Kaggle Simulated Smart Meter Dataset (`ziya07/smart-meter-electricity-consumption-dataset`; 5,000 rows):* Synthetically simulated residential meter with pre-baked Isolation Forest labels; rejected because real-world empirical data with 10k+ rows is required.
  3. *UNICON University Utility Dataset (`cdaclab/unicon`):* Multi-hundred-megabyte raw archive spanning COVID-19 campus lockdowns (2020–2021), which confounds normal occupancy baseload modelling with pandemic shutdowns.

---

## 2. Syllabus-Locked Machine Learning Architecture

Per `Data Visualization and Analysis Syllabus (2).pdf` (`26CSEM321`), ONLY algorithms explicitly taught in **Unit II** and **Unit IV** are used as core models:
1. **Multiple Linear Regression (Unit II — Regression):**
   - *Model 1A (Counterfactual Weather-Schedule Baseline MLR):* Predicts expected normal hourly demand from meteorological drivers (`airTemperature`, `rel_humidity`, `windSpeed`, `seaLvlPressure`, `cdd`, `hdd`, `temp_hum_inter`) and calendar schedule regimes (`hour × is_weekend`, `month`). Used to quantify abnormal excess kWh (`actual - expected`) without letting yesterday's wastage leak into today's expected baseline.
   - *Model 1B (Autoregressive Short-Term Forecasting MLR):* Adds 24-hour lag (`lag_24h`), 168-hour weekly lag (`lag_168h`), and 24-hour rolling mean (`roll_24h`) for operational day-ahead load forecasting.
2. **Decision Tree Regressor & Classifier (Unit IV — Decision Tree):**
   - *Decision Tree Regressor:* Non-linear interpretable benchmark against MLR on the chronological test split.
   - *Decision Tree Classifier (`max_depth=3`):* Extracts human-readable audit rules (`IF excess_kwh > X AND off_hour_kwh > Y THEN Wastage Day`) for facility operators.
3. **Support Vector Machines (Unit IV — Support Vector Machines):**
   - *One-Class SVM (RBF kernel):* Unsupervised anomaly detector trained on standardized daily load-shape features (`excess_kwh`, `off_hour_share`, `baseload_ratio`, `work_wkend_dev`, `mean_temp`) to flag multivariate anomalous wastage days.
   - *Supervised RBF-SVM Classifier (`SVC`):* Evaluates classification boundaries on domain-audited wastage labels with 5-fold cross-validation.
4. **Clustering Techniques (Unit IV — Clustering Techniques):**
   - *K-Means Clustering:* Partitions the 731 daily load profiles into distinct operational regimes (chosen via Elbow inertia + Silhouette coefficient), isolating a high-intensity wastage cluster and computing Euclidean centroid distance as a complementary anomaly score.
5. **Bayes Classification (Unit IV — Bayes Classification):**
   - *Gaussian Naive Bayes:* Probabilistic supplementary classifier benchmarked alongside Decision Tree and SVM on wastage-day detection.

No Random Forest, XGBoost, Gradient Boosting, Isolation Forest, or Neural Networks are used as core models.

---

## 3. Transparent Domain Wastage Rule & Financial Assumptions

- **Domain Reference Benchmark for Anomaly Evaluation:** Because BDG2 (like real-world unlabelled utility telemetry) does not ship with maintenance-ticket ground-truth labels, we define an explicit, physics-based **Operational Wastage Audit Rule** grounded in ASHRAE / Lawrence Berkeley National Laboratory (LBNL) load-shape benchmarking literature:
  - A day is audited as a **Confirmed Wastage Anomaly** if its positive counterfactual consumption excess exceeds `+1.25 σ` of baseline daily residuals **OR** its overnight off-hour baseload (`22:00–05:59`) exceeds the seasonal-schedule 90th-percentile threshold while total daily consumption exceeds expected demand.
  - Unsupervised models (**One-Class SVM** and **K-Means cluster distance**) are evaluated transparently against this audited benchmark using Precision, Recall, F1-score, and Confusion Matrices, with full disclosure of how the reference labels are constructed.
- **Tariff & Carbon Factors (Explicitly Disclosed):**
  - Commercial/ institutional electricity tariff: **$0.12 / kWh** (U.S. EIA commercial sector benchmark for Arizona/Mountain commercial accounts; equivalent ₹10.0 / kWh institutional tariff note included for Indian campus context).
  - Grid emission factor: **0.417 kg CO₂e / kWh** (U.S. EPA eGRID regional benchmark).
  - Savings roadmap decomposes recoverable wastage into four actionable facility-management levers (Off-Hour HVAC Setback Automation, Weekend Deep Shutdown Scheduling, Anomaly Alert Rapid Dispatch, and Economizer / Cooling Setpoint Trim) targeting the **15–20% savings band** without occupant comfort loss (`23–24 °C` occupied setpoint preserved).

---

## 4. Typography, Color System & PDF Engineering Decisions

- **Typeface:** The four user-supplied TrueType font files (`times new roman*.txt` → renamed `.ttf`) have slightly inconsistent internal OpenType family name strings (`Times New Roman Cyr`, `Times New Roman`, `Times`). To prevent font-matching collisions, we register them under explicit CSS `@font-face` descriptors in **WeasyPrint** and explicit `FontProperties` in **Matplotlib**, embedding all four faces cleanly in the final PDF. For mathematical superscripts/symbols absent from the legacy 8-bit TTF character map (such as `²` in `R²`), semantic `<sup>2</sup>` HTML markup is used in prose so `TimesNewRoman` renders every glyph natively without fallback font substitution.
- **Color System (§7 Strict Compliance):**
  - Page background: Pure White (`#FFFFFF`); primary body text: Pure Black (`#000000`).
  - Structural dark neutral: Deep Navy (`#0B1F3A`) and Charcoal (`#222222`) for headings/table headers.
  - Accent & Data Series Palette (100% pure saturated hues): Pure Blue (`#0000FF`), Pure Red (`#FF0000`), Pure Green (`#00FF00`), Pure Cyan (`#00FFFF`), Pure Magenta (`#FF00FF`), Pure Yellow (`#FFFF00`), paired with strict WCAG luminance-checked foreground text (white text on `#0000FF`/`#FF0000`/`#FF00FF`/`#0B1F3A`; black text on `#FFFF00`/`#00FF00`/`#00FFFF`).
- **Graphics Format:** All 18 report figures (Fig. 3.1 through Fig. 7.2) are exported from Python as crisp scalable **SVG** vector graphics and embedded directly into the WeasyPrint HTML→PDF pipeline. Both official IILM logos (`IILM-Logo.png` and `IILM-Logo-Standard.png`) retain their native `2160×2160` RGBA transparency and locked 1:1 aspect ratio.
- **Watermark:** No "PDF Making Guidelines" watermark specification file was attached; per §7 (*"otherwise use NO watermark at all"*), zero watermarks are used, maximizing contrast and academic legibility.

- **Report engine (final implementation):** The PDF is produced by `reports/build_report.py`
  in four stages: (i) the body (Chapters 1–8, IEEE references, Appendices A–C) is rendered
  as its own WeasyPrint document so it can carry arabic folios 1–69; (ii) the page number of
  every anchored heading, figure and table is harvested from the rendered page tree and
  injected into the Table of Contents, List of Figures and List of Tables, which are then
  rendered as a separate front-matter document carrying roman folios i–ix (title page
  unnumbered); (iii) both documents are merged with PyMuPDF and the 107 cross-document TOC
  links are re-created as explicit `/GoTo` annotations, because a link that points from the
  front-matter PDF into the body PDF cannot survive a naive merge; (iv) a 79-entry PDF
  outline and the document metadata are written before saving with deflate + object-stream
  garbage collection.
- **Font configuration decision:** WeasyPrint 70 ignores `@font-face` rules unless the
  *same* `FontConfiguration` object is passed both to `CSS(...)` and to
  `HTML(...).render(...)`. Without it the report silently fell back to DejaVu Sans for
  100% of the text. The engine now shares one `FontConfiguration` across both documents,
  and `reports/audit_report.py` fails the build if any span is set in a face that is not
  one of the four supplied Times New Roman files (or DejaVu Sans Mono inside code blocks).
- **Glyph-map discipline:** the supplied TrueType files are legacy 8-bit fonts whose cmaps
  lack `²`, `×`, `÷`, `≤`, `≥`, `σ`, `μ`, `Δ`, `→`, `−` and `ö`. Prose therefore uses HTML
  markup (`<sup>2</sup>`, `<=`, `>=`) instead of raw symbols; Matplotlib is configured with
  `axes.unicode_minus = False` so chart tick labels use the ASCII hyphen; and author names
  such as Schölkopf are transliterated. The audit verifies that zero characters are drawn
  with a fallback font.
- **Synthetic-style elimination:** Matplotlib SVGs name their text in the internal family
  of the supplied file (`Times New Roman Cyr`). Registering that family name (and
  `Times New Roman`) as four explicit `@font-face` faces prevents WeasyPrint from
  synthesising an oblique/bold variant of the regular face inside figures.
- **QA automation:** `reports/audit_report.py` is a hard gate, not a checklist: it asserts
  A4 geometry on every page, whitelists fonts, detects any span crossing the text frame,
  detects headings stranded at a page foot, verifies TOC/LOF/LOT printed page numbers
  against the harvested body pages, verifies roman and arabic folio sequences, verifies the
  presence of vector content on every figure page, and lists every URI link and outline
  entry. Final state: **80 pages, 2.44 MB, 0 font fallbacks, 0 overflows, 0 stranded
  headings, 0 TOC/LOF/LOT mismatches, 107 internal links, 6 external URLs, 79 bookmarks.**

---

## 5. Deployment & Hosting Architecture

- **Canonical publication — GitHub Pages:** the project site is published from the `deploy/`
  directory by `.github/workflows/pages.yml` and answers at
  `https://yourprogrammerayush.github.io/smart-building-energy-profiling/`. It is self-contained: `index.html` plus same-origin copies of the report PDF, the
  executed notebook, the dataset and the pipeline script, so no third-party host is needed.
- **Source repository:** `https://github.com/yourprogrammerayush/smart-building-energy-profiling` (public, branch `main`).
- **Retired preview host:** an earlier Vercel preview (`smart-building-energy-profiling.vercel.app`)
  was used only to inspect the single-file build while the GitHub repository was being created.
  It is **not** referenced anywhere in the deliverable and is not a publication target.
- **Google Drive mirror:** the complete, publicly readable submission package lives in
  `https://drive.google.com/drive/folders/11nythpv22YAKNrwq1X8lfrp4Fq-hj01C`
  (role *reader*, link sharing enabled, file discovery disabled).
- **Repository & automation boundary:** in this environment the `github` connector returns
  `status: unsupported` and no GitHub personal-access token exists, so the repository was
  prepared as a complete, committed Git history (branch `main`, 61 tracked files, a verified
  `.bundle`) and handed over with one copy-paste execution prompt rather than pushed from here.
  Publication is therefore performed by the repository owner with a single `git push`, after
  which `.github/workflows/pages.yml` publishes `deploy/` to GitHub Pages.
- **Delivery back-up:** the complete submission package is mirrored in the user's Google Drive
  project folder for team distribution and archival, using the original filenames.
