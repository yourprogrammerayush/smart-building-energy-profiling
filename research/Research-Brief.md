# Deep Research Brief: Smart Building Energy Wastage & Anomaly Profiling

**Course:** Data Visualization and Analysis (`26CSEM321`)  
**Institution:** IILM University, Greater Noida — School of Computer Science and Engineering  
**Authors:** Ayush Jha (`25SCS1003001336`), Archit Baloni (`25SCS1003003550`), Ashutosh Sahoo (`25SCS1003004011`), Dev Bhaskar Singh (`25SCS1003003174`), Aman Kumar Gupta (`25SCS1003003645`)  
**Date:** 25 November 2026

---

## 1. Domain Synthesis: Commercial & Campus Building Energy Wastage

Commercial offices and university campuses represent nearly **40% of global electricity demand**, yet empirical energy audits by Lawrence Berkeley National Laboratory (LBNL), ASHRAE, and the U.S. Department of Energy demonstrate that **15% to 30% of commercial building electricity is routinely wasted** due to invisible operational faults rather than envelope deficiencies. Because facility managers typically review only aggregated monthly utility invoices, three primary wastage vectors go undetected:

1. **Elevated Overnight Off-Hour Baseload (`22:00–05:59`):** Air-handling units (AHUs), chilled-water circulation pumps, laboratory exhaust fans, and corridor lighting left running on manual Building Management System (BMS) overrides when occupancy is near zero.
2. **Incomplete Weekend & Academic-Break Setbacks:** Buildings operating on weekday HVAC schedules across Saturdays, Sundays, and holidays, producing high weekend-to-weekday load ratios (`>0.75` instead of best-practice `0.45–0.55`).
3. **Weather-Uncoupled Cooling & Simultaneous Heating/Cooling Spikes:** Improperly calibrated economizers, stuck chilled-water valves, or aggressive thermostat setpoints causing acute consumption surges beyond what outdoor dry-bulb temperature and relative humidity physically justify.

### Core Facility-Management Key Performance Indicators (KPIs)
- **Hourly & Daily Demand (`kWh`):** Integrated electrical energy consumed per 60-minute interval or 24-hour cycle.
- **Energy Use Intensity (`EUI`, `kWh/m²/year`):** Annual consumption normalized by conditioned floor area (`31,462.6 m²` across our 6-building district).
- **Baseload-to-Peak Ratio (`BPR`):** Mean overnight off-hour demand (`22:00–05:59`) divided by daily peak hourly demand. Commercial benchmarks indicate `BPR < 0.45` reflects tight night setback, whereas `BPR > 0.60` signals persistent overnight HVAC/plug-load drift.
- **Load Factor (`LF`):** Ratio of mean daily hourly load to peak hourly load (`mean_kWh / peak_kWh`).
- **Counterfactual Excess Energy (`ΔE = E_actual - E_expected`, `kWh`):** Positive deviation above a weather-and-schedule regression baseline, isolating operational wastage from legitimate hot-weather cooling demand.

---

## 2. Dataset Landscape Evaluation & Selection

Four candidate real-world datasets were systematically evaluated against seven criteria: (i) commercial/campus relevance, (ii) sample size (`10k–50k+` rows), (iii) presence of hourly timestamps + smart-meter kWh + meteorological features, (iv) data cleanliness, (v) open license, (vi) programmatic reproducibility, and (vii) suitability for both regression and anomaly profiling.

| Candidate Dataset | Source & License | Granularity & Rows | Domain Fit | Evaluation Outcome |
|---|---|---|---|---|
| **Building Data Genome Project 2 (BDG2) — Site `Fox` Commercial & Campus District** | Kaggle (`claytonmiller/buildingdatagenomeproject2`) & GitHub (`buds-lab/building-data-genome-project-2`); *Nature Scientific Data* (CC BY-SA 4.0) | Hourly, 2 full years (`2016–2017`), **17,544 hourly rows** (105,264 meter-hours across 6 buildings; 731 days) | **Exact match:** 3 commercial offices + 3 university campus buildings (`31,462.6 m²`) + local airport weather | **SELECTED (Primary Dataset)** |
| **Appliances Energy Prediction (Candanedo et al., 2017)** | Kaggle (`loveall/appliances-energy-prediction`) & UCI ML Repo ID 374 (CC BY 4.0) | 10-min intervals, 4.5 months (`Jan–May 2016`), 19,735 rows | Single residential house in Belgium; lacks full seasonal cycle & commercial/campus HVAC schedules | **Rejected** (residential single-house scope) |
| **Smart Meter Electricity Consumption Dataset (`ziya07`)** | Kaggle (`ziya07/smart-meter-electricity-consumption-dataset`) (CC0) | 30-min intervals, 5,000 rows | Simulated residential smart meter with synthetic Isolation Forest labels | **Rejected** (simulated data, small row count) |
| **UNICON University Energy Dataset (`cdaclab/unicon`)** | Kaggle (`cdaclab/unicon`), La Trobe University | 15-min intervals (`2018–2021`), >600 MB multi-file archive | University campus meters heavily distorted by 2020–2021 COVID-19 campus lockdowns | **Rejected** (pandemic structural break & archive size) |

---

## 3. Literature Review & Academic References Plan

1. **Miller, C. et al. (2020)** — *The Building Data Genome Project 2, energy meter data from the ASHRAE Great Energy Predictor III competition*, *Scientific Data* (Nature), 7, 368. Establishes the BDG2 benchmark dataset for commercial/campus load prediction and M&V.
2. **Candanedo, L. M., Feldheim, V., & Deramaix, D. (2017)** — *Data driven prediction models of energy use of appliances in a low-energy house*, *Energy and Buildings*, 140, 81–97. Demonstrates weather-and-sensor feature engineering and meteorological importance in building load regression.
3. **Luo, X., Oyedele, L. O., Ajayi, A. O., et al. (2020) / LBNL Load-Shape Benchmarking (2015)** — Lawrence Berkeley National Laboratory commercial load-shape parameters (near-base load, peak-to-base ratio, workday/non-workday ratio) for diagnosing after-hours HVAC waste.
4. **Himeur, Y., Ghanem, K., Alsalemi, A., Bensaali, F., & Amira, A. (2021)** — *Artificial intelligence based anomaly detection of energy consumption in buildings: A review, current trends and new perspectives*, *Applied Energy*, 287, 116601. Comprehensive taxonomy of unsupervised One-Class SVM, clustering, and rule-assisted anomaly detection in smart buildings.
5. **Nepal, B., Yamaha, M., Yokoe, A., & Yamaji, T. (2019)** — *Electricity load pattern analysis and anomaly detection in school buildings using K-means clustering*, *Energies*, 12(12), 2451. Validates two-stage K-Means load-shape clustering + outlier flagging in educational buildings.
6. **Schölkopf, B., Platt, J. C., Shawe-Taylor, J., Smola, A. J., & Williamson, R. C. (2001)** — *Estimating the support of a high-dimensional distribution*, *Neural Computation*, 13(7), 1443–1471. Foundational formulation of One-Class Support Vector Machines (`ν`-OCSVM) for unsupervised novelty/anomaly detection.
7. **Cortes, C., & Vapnik, V. (1995)** — *Support-vector networks*, *Machine Learning*, 20(3), 273–297. Supervised maximum-margin hyperplanes and kernel classification.
8. **MacQueen, J. (1967) & Rousseeuw, P. J. (1987)** — K-Means partitioning (*5th Berkeley Symposium*) and Silhouette cluster validation (*J. Comput. Appl. Math.*, 20, 53–65).
9. **U.S. DOE / ENERGY STAR Portfolio Manager & ASHRAE Guideline 14 (2014/2023)** — Measurement of Energy, Demand, and Water Savings; counterfactual baseline regression (`R²`, `RMSE`, `CV-RMSE`, `MAPE`) for quantifying retrofit and operational schedule savings of 15–20%.
10. **Core Scientific Python Ecosystem Citations** — Pedregosa et al. (2011, *Scikit-learn*), Harris et al. (2020, *NumPy*, *Nature*), McKinney (2010, *Pandas*), Virtanen et al. (2020, *SciPy*, *Nature Methods*), Hunter (2007, *Matplotlib*), Waskom (2021, *Seaborn*).

---

## 4. Reference Report Critique & Quality Upgrade Plan

Inspection of the 49-page classmate reference report (`DVA project_ Greatest Of modern era (football edition) complete analysis.pdf`) revealed structural strengths we preserve and weaknesses we decisively surpass:

| Dimension | Classmate Reference Report | Our Flagship Upgrade |
|---|---|---|
| **Front Matter & Structure** | Cover, Certificate, Acknowledgement w/ signature table, Abstract, TOC, LoF, LoT, LoCL, 8 Chapters + Refs + Appendix A | Exact structural mirror **plus** Syllabus Coverage Mapping table, Project Links table, and **Appendix B (Full Plain-Text Source Code)** |
| **ML Syllabus Alignment** | Used Random Forest, KNN, Gradient Boosting (outside `26CSEM321` syllabus) | **100% Syllabus-Locked Core:** Multiple Linear Regression (Unit II), One-Class SVM & RBF-SVM (Unit IV), K-Means Clustering (Unit IV), Decision Tree & Naive Bayes (Unit IV) |
| **Code Completeness** | Truncated snippets (`# ... remaining plotting lines omitted`) | Zero omitted code: inline chapter listings **plus** complete plain-text working pipeline in Appendix B |
| **Visual & Typography Polish** | Plain black-and-white default LaTeX/HTML look, no logo on cover, sparse prose on several pages | Embedded official `Times New Roman` TTF quartet, transparent IILM crest on Cover, pure saturated `#0000FF / #FF0000 / #00FF00 / #00FFFF / #FF00FF / #FFFF00` accent system on crisp white pages, 15 vector SVG charts, and structured *"What It Shows → What It Means → Decision Impact"* blocks after every figure |
| **Interactive Web Experience** | Static nbconvert HTML dump only | **Both** a SaaS-grade interactive Plotly.js analytics web app (with light/dark theme toggle, interactive filters, anomaly explorer, savings calculator) **and** the full rendered HTML notebook |
