# Project Links — Smart Building Energy Wastage & Anomaly Profiling

**Course:** `26CSEM321` Data Visualization and Analysis · Section 2CSE-4 · AY 2026-27
**Team:** Ayush Jha (25SCS1003001336) · Archit Baloni (25SCS1003003550) ·
Ashutosh Sahoo (25SCS1003004011) · Dev Bhaskar Singh (25SCS1003003174) ·
Aman Kumar Gupta (25SCS1003003645)
**Faculty Guide:** Aditya Bangia · **Institution:** IILM University, Greater Noida

All URLs below are public (no sign-in required) and were verified with HTTP 200 checks
during the final quality-assurance pass.

## 1. Primary deliverables

| # | Deliverable | Public URL |
|---|---|---|
| 1 | Interactive web application (landing page) | https://smart-building-energy-profiling.vercel.app |
| 2 | Final project report (PDF, 78 pages) | https://smart-building-energy-profiling.vercel.app/reports/Final-Project-Report.pdf |
| 3 | Executed notebook (HTML) | https://smart-building-energy-profiling.vercel.app/notebook/Analysis-Notebook.html |
| 4 | Notebook source (.ipynb) | https://smart-building-energy-profiling.vercel.app/notebook/Analysis-Notebook.ipynb |
| 5 | Analytical pipeline (.py) | https://smart-building-energy-profiling.vercel.app/code/Energy-Analysis-Script.py |
| 6 | Curated dataset (.csv, 17,544 x 15) | https://smart-building-energy-profiling.vercel.app/data/dataset.csv |
| 7 | Dataset card (.md) | https://smart-building-energy-profiling.vercel.app/data/Dataset-Card.md |
| 8 | Full repository archive (ZIP + mirrored deliverables) | https://drive.google.com/drive/folders/11nythpv22YAKNrwq1X8lfrp4Fq-hj01C |

## 2. Google Drive repository folder

**Folder:** `Smart-Building-Energy-Wastage-Anomaly-Profiling-Ayush-Jha-25SCS1003001336`
**Link:** https://drive.google.com/drive/folders/11nythpv22YAKNrwq1X8lfrp4Fq-hj01C
**Sharing:** anyone with the link — viewer (public, file discovery disabled)

Contents uploaded to this folder:

- `Final-Project-Report.pdf` — the 78-page report
- `Analysis-Notebook.ipynb` — executed notebook source
- `Analysis-Notebook.html` — rendered notebook with all outputs
- `Energy-Analysis-Script.py` — deterministic analytical pipeline
- `dataset.csv` — curated hourly dataset (CC BY-SA 4.0)
- `README.md` — repository overview and reproduction instructions
- `Smart-Building-Energy-Wastage-Anomaly-Profiling-Ayush-Jha-25SCS1003001336.zip` — complete repository archive

## 3. Upstream data sources (third-party, openly licensed)

| Source | Link | Licence |
|---|---|---|
| Building Data Genome Project 2 — Kaggle | https://www.kaggle.com/datasets/claytonmiller/buildingdatagenomeproject2 | CC BY-SA 4.0 |
| Building Data Genome Project 2 — GitHub mirror (BUDS Lab) | https://github.com/buds-lab/building-data-genome-project-2 | CC BY-SA 4.0 |
| BDG2 reference publication (Scientific Data 7:368) | https://doi.org/10.1038/s41597-020-00712-x | Open access |

## 4. How to verify the deployment

```bash
# every link above should answer 200
for u in \
  https://smart-building-energy-profiling.vercel.app \
  https://smart-building-energy-profiling.vercel.app/reports/Final-Project-Report.pdf \
  https://smart-building-energy-profiling.vercel.app/notebook/Analysis-Notebook.html \
  https://smart-building-energy-profiling.vercel.app/notebook/Analysis-Notebook.ipynb \
  https://smart-building-energy-profiling.vercel.app/code/Energy-Analysis-Script.py \
  https://smart-building-energy-profiling.vercel.app/data/dataset.csv \
  https://drive.google.com/drive/folders/11nythpv22YAKNrwq1X8lfrp4Fq-hj01C ; do
  printf '%s -> ' "$u"; curl -o /dev/null -s -w '%{http_code}\n' -L "$u"
done
```

## 5. Mirroring policy

The Vercel deployment is the canonical, always-current copy of every artefact (the site is
rebuilt from this repository). The Google Drive folder is the archival mirror used for
submission and team distribution. The report, notebook, pipeline and dataset are identical
in both locations — the `README.md` in each records the same SHA-256 dataset digest
(`3116fd2794f8af05…`).
