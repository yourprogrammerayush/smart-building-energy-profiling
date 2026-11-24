# Project Links — Smart Building Energy Wastage & Anomaly Profiling

**Course:** `26CSEM321` Data Visualization and Analysis · Section 2CSE-4 · AY 2026-27
**Team:** Ayush Jha (25SCS1003001336) · Archit Baloni (25SCS1003003550) ·
Ashutosh Sahoo (25SCS1003004011) · Dev Bhaskar Singh (25SCS1003003174) ·
Aman Kumar Gupta (25SCS1003003645)
**Faculty Guide:** Aditya Bangia · **Institution:** IILM University, Greater Noida

All URLs below are public (no sign-in required) and were verified with HTTP 200/206 checks
during the final quality-assurance pass (2026-11-24).

## 1. Primary deliverables

| # | Deliverable | Public URL |
|---|---|---|
| 1 | Interactive web application (charts, audit queue, savings simulator) | https://smart-building-energy-profiling.vercel.app |
| 2 | Final project report (PDF, 78 pages) | https://drive.google.com/file/d/1Fgmeblm_4hibiQqlzque6yOk12RfPkdC/view |
| 3 | Executed notebook (HTML) | https://drive.google.com/file/d/1-x3Xt8kvDKInc7wvPPYmnTjIA2vHIY8Z/view |
| 4 | Notebook source (.ipynb) | https://drive.google.com/file/d/1juwjRrv5_8cwq4m-GBpNkO1_QCTALfur/view |
| 5 | Analytical pipeline (.py) | https://drive.google.com/file/d/1_WAHattOaBqFc_xRNFKqwP_8OW9He29Q/view |
| 6 | Curated dataset (.csv, 17,544 x 15) | https://drive.google.com/file/d/1TMp_QXR5y0Ip58CRa9MvR6lYcrgDwfj2/view |
| 7 | Analysis results (.json) | https://drive.google.com/file/d/1M2QeY7CmWE0CHfLPJL-n-4OCcxdGZfwi/view |
| 8 | Full repository archive (.zip, 7.7 MB) | https://drive.google.com/file/d/1Lk0E0FaeomvBcpYwc0EjjCDTsrDaw2sl/view |
| 9 | Google Drive project folder (all of the above) | https://drive.google.com/drive/folders/11nythpv22YAKNrwq1X8lfrp4Fq-hj01C |

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
# every link above should answer 200 (Vercel) or 200/206 (Google Drive)
for u in \
  https://smart-building-energy-profiling.vercel.app \
  https://drive.google.com/file/d/1Fgmeblm_4hibiQqlzque6yOk12RfPkdC/view \
  https://drive.google.com/file/d/1-x3Xt8kvDKInc7wvPPYmnTjIA2vHIY8Z/view \
  https://drive.google.com/file/d/1juwjRrv5_8cwq4m-GBpNkO1_QCTALfur/view \
  https://drive.google.com/file/d/1_WAHattOaBqFc_xRNFKqwP_8OW9He29Q/view \
  https://drive.google.com/file/d/1TMp_QXR5y0Ip58CRa9MvR6lYcrgDwfj2/view \
  https://drive.google.com/file/d/1Lk0E0FaeomvBcpYwc0EjjCDTsrDaw2sl/view \
  https://drive.google.com/drive/folders/11nythpv22YAKNrwq1X8lfrp4Fq-hj01C ; do
  printf '%s -> ' "$u"; curl -o /dev/null -s -w '%{http_code}\n' -L "$u"
done
```

## 5. Mirroring policy

The Vercel deployment (`deploy/index.html`, one self-contained file) is the canonical entry point:
it carries the headline numbers, the interactive analysis and the audit queue, and every download
button points at the Google Drive mirror. Heavy artefacts (2.4 MB PDF, 1.0 MB notebook HTML,
1.7 MB dataset, 7.7 MB archive) are **not** bundled into the deployment — inline-only file uploads
make that impractical — so Drive is the single distribution point for files, and the site is the
single distribution point for analysis.

Both copies are generated from this repository: `python3 code/Energy-Analysis-Script.py` writes
`data/Analysis-Results.json` and the 18 SVG figures, `python3 reports/build_report.py` writes the
PDF, and the site reads the same numbers. The `README.md` in both locations records the same
SHA-256 dataset digest (`3116fd2794f8af05...`), so any divergence is detectable.
