# Dataset Card — Building Data Genome Project 2 (Site `Fox` Commercial & University Campus Portfolio)

## 1. Provenance & Licensing
- **Primary Source Name:** Building Data Genome Project 2 (BDG2) — ASHRAE Great Energy Predictor III Open Benchmark
- **Kaggle Repository:** [Building Data Genome Project 2 on Kaggle](https://www.kaggle.com/datasets/claytonmiller/buildingdatagenomeproject2)
- **Official GitHub Mirror:** [BUDS Lab BDG2 GitHub Repository](https://github.com/buds-lab/building-data-genome-project-2)
- **Peer-Reviewed Publication:** Miller, C., Kathirgamanathan, A., Picchetti, B., et al. (2020). *The Building Data Genome Project 2, energy meter data from the ASHRAE Great Energy Predictor III competition*. **Scientific Data (Nature)**, 7, 368. DOI: [10.1038/s41597-020-00712-x](https://doi.org/10.1038/s41597-020-00712-x)
- **License:** Creative Commons Attribution-ShareAlike 4.0 International (**CC BY-SA 4.0**) — permits academic redistribution, transformation, and commercial/non-commercial sharing with attribution.

---

## 2. Dataset Dimensions & Temporal Coverage
- **Workspace File:** `data/dataset.csv` (`1.65 MB`, SHA-256 prefix `3116fd2794f8af05`)
- **Companion Metadata File:** `data/Building-Metadata.csv`
- **Observation Count:** **17,544 hourly records** (`105,264` individual building-meter hourly readings across 6 buildings)
- **Daily Aggregation Count:** **731 complete calendar days** (`366` days in leap year 2016 + `365` days in 2017)
- **Time Span:** `2016-01-01 00:00:00` through `2017-12-31 23:00:00` (100% contiguous hourly index, `0` duplicate timestamps)
- **Geographic & Climate Context:** Site `Fox` — Tempe / Phoenix Metropolitan University & Commercial District, Arizona (`33.4244° N, 111.9281° W`, `US/Mountain` timezone, ASHRAE Climate Zone `2B` Hot-Dry, strong cooling-dominated HVAC regime similar to North Indian summer/monsoon cooling loads).
- **Total Conditioned Floor Area:** **31,462.6 m²** (`338,661 sq ft`), balanced across **3 Commercial Offices** (`13,650.0 m²`) and **3 University Campus Buildings** (`17,812.6 m²`).

---

## 3. Monitored Building Portfolio (`data/Building-Metadata.csv`)

| Building ID | Sector | Sub-Category | Floor Area (`m²`) | Floor Area (`sq ft`) | Raw Missing Hours | Mean Hourly Load (`kWh`) |
|---|---|---|---:|---:|---:|---:|
| `Fox_office_Joy` | Commercial Office | Administrative Office | 6,581.0 | 70,837 | 9 (0.05%) | 182.0 |
| `Fox_office_Vicki` | Commercial Office | Administrative Office | 6,580.5 | 70,832 | 11 (0.06%) | 146.8 |
| `Fox_office_Clayton` | Commercial Office | Executive / IT Office | 488.5 | 5,258 | 2 (0.01%) | 87.7 |
| `Fox_education_Tamika` | University Campus | College Laboratory | 8,339.9 | 89,770 | 8 (0.05%) | 150.8 |
| `Fox_education_Carleen` | University Campus | College Laboratory | 6,635.2 | 71,421 | 13 (0.07%) | 105.7 |
| `Fox_education_Kris` | University Campus | Student Union | 2,837.5 | 30,543 | 8 (0.05%) | 106.8 |
| **District Total** | **Mixed Commercial + Campus** | **6 Smart Meters** | **31,462.6** | **338,661** | **51 meter-cells** | **779.6** |

---

## 4. Column Dictionary (`data/dataset.csv`)

| Column Name | Attribute Type (Syllabus Unit I) | Physical Unit | Raw Missing Count | Description |
|---|---|---|---:|---|
| `timestamp` | Temporal (Ordinal / Continuous Index) | Local `YYYY-MM-DD HH:MM:SS` | 0 | Hourly smart-meter interval start timestamp (`US/Mountain`) |
| `site_id` | Nominal Categorical | String (`Fox`) | 0 | BDG2 campus/district identifier |
| `Fox_office_Joy` | Numeric Continuous (Ratio) | `kWh` | 9 | Whole-building hourly electricity consumption — Office Joy |
| `Fox_office_Vicki` | Numeric Continuous (Ratio) | `kWh` | 11 | Whole-building hourly electricity consumption — Office Vicki |
| `Fox_office_Clayton` | Numeric Continuous (Ratio) | `kWh` | 2 | Whole-building hourly electricity consumption — Office Clayton |
| `Fox_education_Tamika` | Numeric Continuous (Ratio) | `kWh` | 8 | Whole-building hourly electricity consumption — Lab Tamika |
| `Fox_education_Carleen` | Numeric Continuous (Ratio) | `kWh` | 13 | Whole-building hourly electricity consumption — Lab Carleen |
| `Fox_education_Kris` | Numeric Continuous (Ratio) | `kWh` | 8 | Whole-building hourly electricity consumption — Student Union Kris |
| `airTemperature` | Numeric Continuous (Interval) | `°C` | 2 | Outdoor dry-bulb air temperature from nearest ISD airport station |
| `dewTemperature` | Numeric Continuous (Interval) | `°C` | 2 | Outdoor dew-point temperature (used with `airTemperature` to compute relative humidity `%`) |
| `seaLvlPressure` | Numeric Continuous (Ratio) | `hPa` (`mbar`) | 54 | Atmospheric sea-level barometric pressure |
| `windSpeed` | Numeric Continuous (Ratio) | `m/s` | 13 | Surface horizontal wind speed |
| `windDirection` | Numeric Continuous (Cyclic) | `Degrees (0–360°)` | 1,216 | Compass wind direction |
| `cloudCoverage` | Ordinal / Discrete | `Oktas (0–8)` | 4,971 | Sky cloud cover fraction |
| `precipDepth1HR` | Numeric Continuous | `mm` | 72 | One-hour liquid precipitation depth (`-1` trace indicator cleaned in preprocessing) |
