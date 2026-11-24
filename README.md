# Smart Building Energy Wastage & Anomaly Profiling
### A Data-Driven Approach Using Smart-Meter and Weather Data

**Course:** `26CSEM321` — Data Visualization and Analysis · **B.Tech CSE, Year 2, Semester 3** · **Section 2CSE-4**
**Institution:** IILM University, Greater Noida · School of Computer Science and Engineering
**Faculty Guide:** Aditya Bangia · **Academic Year:** 2026-27

[![Live Site](https://img.shields.io/badge/Live%20Site-yourprogrammerayush.github.io-0B6E4F?style=flat-square)](https://yourprogrammerayush.github.io/smart-building-energy-profiling/)
[![Report](https://img.shields.io/badge/Report-Final--Project--Report.pdf-b31b1b?style=flat-square)](https://drive.google.com/file/d/1Fgmeblm_4hibiQqlzque6yOk12RfPkdC/view)
[![Notebook](https://img.shields.io/badge/Notebook-HTML%20%2B%20.ipynb-f37626?style=flat-square)](https://drive.google.com/file/d/1-x3Xt8kvDKInc7wvPPYmnTjIA2vHIY8Z/view)
[![Data](https://img.shields.io/badge/Data-CC%20BY--SA%204.0-4c9f70?style=flat-square)](https://drive.google.com/file/d/1TMp_QXR5y0Ip58CRa9MvR6lYcrgDwfj2/view)
[![License](https://img.shields.io/badge/Code%20License-MIT-blue?style=flat-square)](LICENSE)

---

## 1. What this project does

Commercial offices and university campuses waste a large share of the electricity they
buy, but the waste never appears as a single dramatic failure — it hides as an elevated
overnight baseload, an inherited weekday schedule running through the weekend, and cooling
that cannot be explained by the weather. This project measures that waste end-to-end on a
**real, openly licensed, two-year hourly dataset** and converts it into a **costed,
comfort-constrained remediation roadmap**.

The study uses **17,544 hourly smart-meter readings** for a six-building mixed portfolio
(3 commercial offices + 3 university buildings, **31,462.6 m²**) from the
**Building Data Genome Project 2** benchmark (Site `Fox`, Tempe, Arizona; 2016-01-01 →
2017-12-31), joined with hourly meteorological observations — and **only** the algorithms
taught in the `26CSEM321` syllabus: Multiple Linear Regression, Decision Tree, Support
Vector Machines (One-Class SVM, RBF-SVM), K-Means Clustering and Gaussian Naive Bayes.

## 2. Headline results

| Metric | Value |
|---|---|
| Total electricity consumed (2 years) | **13,677.27 MWh** (6,838.63 MWh/yr) |
| Energy Use Intensity (portfolio) | **217.36 kWh/m²/year** |
| Mean hourly portfolio load | **779.60 kWh/h** (peak 984.0 at 15:00, trough 547.4 at 04:00) |
| Energy consumed in unoccupied hours (22:00–05:59) | **3,460.7 MWh = 25.30%** of all energy, in 33.33% of clock time |
| Weekend energy share | **24.85%** on 28.57% of calendar days |
| Weekday vs weekend test | Welch **t = 45.76**, Mann-Whitney p = 2.94e-283, ratio 1.219 |
| Occupied vs unoccupied test | Welch **t = 129.27**, ratio 0.595 |
| Counterfactual baseline (weather + schedule MLR) | **R² = 0.9000**, RMSE 75.43 kWh/h, MAPE 7.60% |
| Best forecast model (full autoregressive MLR) | **R² = 0.9351**, RMSE 60.76 kWh/h, MAPE 6.01% |
| Consensus anomaly days (2-of-3 detectors) | **157 / 731 days (21.5%)**, carrying **233.03 MWh** of excess |
| Best unsupervised detector (One-Class SVM) | Precision **0.7455**, Recall **0.8817**, F1 **0.8079**, AUC 0.8214 |
| **Four-lever savings roadmap** | **1,265.12 MWh/yr = 18.50%**, **USD 151,815/yr**, **527.6 tCO₂e/yr** |
| Sensitivity band | **15.72% – 20.72%** (conservative → aggressive) |

**Answer in one line:** 63% of the recoverable waste is a *scheduling* problem, not an
equipment problem — enforcing a real night setback and consolidating weekends recovers
11.71 of the 18.50 percentage points, with zero comfort penalty.

## 3. Live deliverables

The deployment is a single-page application (one `index.html`, no build step): headline KPIs,
five interactive Plotly charts (diurnal profile, monthly means, 731-day timeline, savings waterfall,
lever ranking), the ten highest-excess audit rows and a live savings simulator. Heavy artefacts are
served from the public Google Drive mirror and are linked from every page of the site.

| Deliverable | Link |
|---|---|
| Interactive web application (charts, audit queue, savings simulator) | https://yourprogrammerayush.github.io/smart-building-energy-profiling/ |
| Final project report (PDF, 80 pages, IEEE references, code appendix) | https://drive.google.com/file/d/1Fgmeblm_4hibiQqlzque6yOk12RfPkdC/view |
| Executed notebook (HTML) | https://drive.google.com/file/d/1-x3Xt8kvDKInc7wvPPYmnTjIA2vHIY8Z/view |
| Notebook source (.ipynb) | https://drive.google.com/file/d/1juwjRrv5_8cwq4m-GBpNkO1_QCTALfur/view |
| Analytical pipeline (Python) | https://drive.google.com/file/d/1_WAHattOaBqFc_xRNFKqwP_8OW9He29Q/view |
| Curated dataset (CSV, CC BY-SA 4.0) | https://drive.google.com/file/d/1TMp_QXR5y0Ip58CRa9MvR6lYcrgDwfj2/view |
| Analysis results (JSON, single source of truth) | https://drive.google.com/file/d/1M2QeY7CmWE0CHfLPJL-n-4OCcxdGZfwi/view |
| Full repository archive (ZIP, 7.9 MB, in the Drive folder) | https://drive.google.com/drive/folders/11nythpv22YAKNrwq1X8lfrp4Fq-hj01C |
| Google Drive project folder (everything above) | https://drive.google.com/drive/folders/11nythpv22YAKNrwq1X8lfrp4Fq-hj01C |

## 4. Repository layout

```
Smart-Building-Energy-Wastage-Anomaly-Profiling-Ayush-Jha-25SCS1003001336/
├── code/
│   └── Energy-Analysis-Script.py     # deterministic pipeline: stats, ML, 18 SVGs, JSON
├── data/
│   ├── dataset.csv                   # 17,544 x 15 hourly panel (CC BY-SA 4.0)
│   ├── Building-Metadata.csv         # 6-building portfolio metadata (31,462.6 m2)
│   ├── Dataset-Card.md               # provenance, dictionary, quality census
│   └── Analysis-Results.json         # single source of truth for every number
├── notebooks/
│   └── Analysis-Notebook.ipynb       # fully executed master notebook
├── assets/
│   ├── figures/                      # 18 publication-grade SVG figures
│   ├── fonts/                        # Times New Roman quartet (embedded in PDF)
│   └── logos/                        # IILM crests (RGBA, 2160 x 2160)
├── reports/
│   ├── Final-Project-Report.pdf      # 80-page report, Roman + Arabic folios, bookmarks
│   ├── build_report.py               # HTML/CSS -> WeasyPrint -> PyMuPDF report engine
│   ├── report_lib.py                 # layout, design tokens, figure/table registry
│   ├── front_matter.py               # title, certificate, declaration, abstract, TOC...
│   ├── content_a.py                  # chapters 1-4
│   ├── content_b.py                  # chapters 5-8, references, appendices
│   ├── audit_report.py               # font / overflow / TOC / link QA audit
│   └── audit_report.json             # machine-readable audit output
├── build_site.py                     # builds deploy/ from the JSON + dataset (no hand-typed numbers)
├── deploy/                           # the published site: index.html + same-origin artefact copies
│   ├── index.html                    # self-contained page (inline CSS/JS/SVG)
│   └── reports/ notebook/ code/ data/ assets/figures/   # downloadable copies + figures
├── research/Research-Brief.md        # literature synthesis, dataset comparison matrix
├── DECISIONS.md                      # every architectural & methodological decision
├── PROJECT-LINKS.md                  # verified live URLs
├── requirements.txt
├── LICENSE                           # MIT (code); dataset remains CC BY-SA 4.0
└── README.md
```

## 5. Reproduce everything

```bash
# 1. environment
python3 -m pip install -r requirements.txt

# 2. analytics: statistics, machine learning, 18 SVG figures, JSON + web payload
python3 code/Energy-Analysis-Script.py

# 3. notebook: execute top-to-bottom and export HTML
jupyter nbconvert --execute --in-place notebooks/Analysis-Notebook.ipynb
jupyter nbconvert --to html notebooks/Analysis-Notebook.ipynb   # writes notebooks/Analysis-Notebook.html
python3 build_site.py                                              # regenerates deploy/

# 4. report: build the PDF, then audit it
python3 reports/build_report.py
python3 reports/audit_report.py

# 5. serve the web app locally
python3 -m http.server 8000 --directory site
```

**Determinism:** `SEED = 42` is fixed for NumPy, scikit-learn estimators and K-Means
(`n_init = 20`); the train/test split is strictly chronological (2016 → train, 2017 →
test), so no shuffling is involved and re-runs reproduce the reported values exactly.
`data/dataset.csv` SHA-256 begins `3116fd2794f8af05`.

## 6. Method summary

1. **Data curation & quality audit** — 15 raw columns; 51 meter gaps (0.048%), 71 core
   weather gaps (0.101%), 6,187 auxiliary sky/wind-direction values (17.63%) handled with
   documented treatments; ISD trace precipitation (`-1.0 mm`) repaired to 0.05 mm;
   **zero hours deleted** (the 1.5×IQR fence rejects no observations — waste here is
   chronic, not spiky).
2. **Feature engineering** — calendar regimes, ASHRAE 18.3 °C degree days, psychrometric
   humidity (Magnus–Tetens), second-order Fourier hour harmonics, and strictly
   backward-looking lags (24 h, 168 h, rolling 24 h mean/std).
3. **Inference** — Welch *t* + Mann-Whitney for regime contrasts; Pearson for weather
   coupling.
4. **Counterfactual modelling** — weather+schedule MLR (no consumption history, so it
   cannot launder yesterday's waste), full autoregressive MLR, tuned Decision Tree.
5. **Anomaly profiling** — 7-feature daily shape vectors, One-Class SVM (ν = 0.08),
   K-Means distance (k = 4 by elbow + silhouette), a transparent physics audit rule, and
   a 2-of-3 consensus; benchmarked against supervised RBF-SVM, Decision Tree and Gaussian
   Naive Bayes.
6. **Savings engineering** — four levers above physical standby floors (360 kWh/h night,
   400 kWh/h weekend) with explicit capture rates (68 / 62 / 82 / 32%), tariff
   USD 0.12/kWh and emission factor 0.417 kg CO₂e/kWh, stress-tested in three scenarios.

## 7. Report engineering (worth noting for reviewers)

The 80-page PDF is generated, not hand-assembled: `reports/build_report.py` renders a
body document and a front-matter document separately (so front matter carries **roman
folios i–ix** and the body **arabic 1–69**), merges them with PyMuPDF, restores 107
cross-document TOC/LOF/LOT links, writes a 79-entry outline plus PDF metadata, and then
`reports/audit_report.py` verifies that **zero font fallback** occurs (all text set in the
four supplied Times New Roman faces; code in DejaVu Sans Mono), that no span crosses the
text frame, that TOC/LOF/LOT page numbers match the body, and that every figure and live
URL is present.

## 8. Team

| Member | Roll number | Contribution |
|---|---|---|
| Ayush Jha | 25SCS1003001336 | Team lead; data engineering, pipeline, report |
| Archit Baloni | 25SCS1003003550 | Statistical analysis and hypothesis testing |
| Ashutosh Sahoo | 25SCS1003004011 | Machine learning and anomaly detection |
| Dev Bhaskar Singh | 25SCS1003003174 | Visualization engineering and web application |
| Aman Kumar Gupta | 25SCS1003003645 | Literature review, validation and QA |

## 9. Data licence and citation

The dataset is the **Building Data Genome Project 2** (Miller *et al.*, 2020,
*Scientific Data* 7:368, DOI 10.1038/s41597-020-00712-x), distributed under
**CC BY-SA 4.0**; the curated extract in `data/dataset.csv` remains under that licence and
inherits its attribution requirement. All original code, figures and text in this
repository are released under the **MIT Licence** (see `LICENSE`).

```bibtex
@article{miller2020bdg2,
  title   = {The Building Data Genome Project 2, energy meter data from the ASHRAE
             Great Energy Predictor III competition},
  author  = {Miller, Clayton and Kathirgamanathan, Anjukan and Picchetti, Bianca and others},
  journal = {Scientific Data}, volume = {7}, pages = {368}, year = {2020},
  doi     = {10.1038/s41597-020-00712-x}
}
```
