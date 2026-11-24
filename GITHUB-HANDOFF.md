# GitHub hand-off — one prompt, done

The repository and the site address are **fixed and must not change**:

| | |
|---|---|
| Repository | `https://github.com/yourprogrammerayush/smart-building-energy-profiling` |
| Live site (GitHub Pages) | `https://yourprogrammerayush.github.io/smart-building-energy-profiling/` |
| Drive archive | `https://drive.google.com/drive/folders/11nythpv22YAKNrwq1X8lfrp4Fq-hj01C` |

Everything below is one copy-paste block for a GitHub-connected chat. It assumes the
repository above **already exists** (it does) and that the local history in the bundle is the
authoritative one — seven prior commits plus the redesign commit, head `feat(design): premium
multi-hue report, grid-behind figures, GitHub Pages site`.

---

## The prompt

```text
Push the finished redesign of my mini-project repository to GitHub and publish the site.
Do not rename the repository, do not create a new one, and do not change the URLs.

Repository (keep exactly):  https://github.com/yourprogrammerayush/smart-building-energy-profiling
Live site (keep exactly):   https://yourprogrammerayush.github.io/smart-building-energy-profiling/
Drive archive folder:       https://drive.google.com/drive/folders/11nythpv22YAKNrwq1X8lfrp4Fq-hj01C

STEP 1 — get the authoritative history
- Open the Drive folder above and download the Git bundle ("09 PROJECT GIT BUNDLE")
  to ~/Downloads, then rename it to project.bundle so the commands below need no
  escaping.
- In that same folder "08 PROJECT ARCHIVE" (a .zip) holds the full working tree
  (code, data, 18 SVG figures, notebook, 80-page PDF, deploy/ site); use it if the
  bundle route is inconvenient, but prefer the bundle because it carries the history.

STEP 2 — bring it into a clone of my existing repository
    git clone https://github.com/yourprogrammerayush/smart-building-energy-profiling.git
    cd smart-building-energy-profiling
    git fetch ~/Downloads/project.bundle main:incoming
    git checkout main
    git merge --ff-only incoming
      # if that refuses because the remote history diverged, the bundle is the
      # authoritative history, so instead run:
      #   git reset --hard incoming
    git log --oneline -3        # expect the top commit to be the redesign commit
    git status                  # expect "nothing to commit, working tree clean"

STEP 3 — push
    git push origin main
    # only if the push is rejected as non-fast-forward, and only because the bundle is
    # the complete authoritative history, use:
    #   git push --force-with-lease origin main

STEP 4 — publish GitHub Pages (once)
- Repo → Settings → Pages → Build and deployment → Source = "GitHub Actions".
- Repo → Actions → "Publish site to GitHub Pages" → Run workflow (or push any commit
  touching deploy/). The workflow publishes the deploy/ directory verbatim.
- Wait for the green check, then open
  https://yourprogrammerayush.github.io/smart-building-energy-profiling/ and confirm:
    • the hero renders with the six-tower isometric skyline,
    • the interactive load-shape chart responds to hover and to the Hour slider,
    • "Read the 80-page report" downloads the PDF from the same origin,
    • "Open the notebook" loads the executed notebook HTML,
    • no console errors, and the page works at 390 px width.

STEP 5 — repo metadata (do not change the name)
- About panel → Description: "Data-driven detection of energy wastage and anomalies in a
  six-building smart-meter portfolio (BDG2 Site Fox) — 25.30% of energy is burned while
  unoccupied."
- Website field: https://yourprogrammerayush.github.io/smart-building-energy-profiling/
- Topics: energy-analytics, anomaly-detection, smart-buildings, time-series, scikit-learn,
  matplotlib, data-visualization, building-data-genome, sustainability

STEP 6 — verify and report back
Run and paste the output:
    git log --oneline -3
    git status --short
    curl -s -o /dev/null -w '%{http_code}\n' https://yourprogrammerayush.github.io/smart-building-energy-profiling/
    curl -s -o /dev/null -w '%{http_code}\n' https://yourprogrammerayush.github.io/smart-building-energy-profiling/reports/Final-Project-Report.pdf
Report: the commit that landed, whether Pages deployed, and the two HTTP codes.
If anything cannot be done, say exactly what and why — do not substitute another host,
another URL or another repository name.

CONSTRAINTS
- No new repository, no rename, no Vercel/Netlify deployment, no custom domain.
- Do not rewrite the report content or the numbers; this is a design and packaging update.
- Do not commit the ZIP or the .bundle (they are git-ignored and live in Drive).
```

---

## What the push contains

* **`deploy/`** — the published site: `index.html` (self-contained, inline CSS/JS/SVG) plus
  same-origin copies of the report PDF, the executed notebook (HTML + `.ipynb`), the pipeline
  script, the dataset and the results JSON, and the 18 SVG figures.
* **`build_site.py`** — rebuilds `deploy/` from `data/Analysis-Results.json` and
  `data/dataset.csv`; no figure on the page is hand-typed.
* **`reports/`** — 80-page PDF plus the sources that generate it (`build_report.py`,
  `report_lib.py`, `audit_report.py`); `audit_report.py` is a hard gate and currently reports
  `ISSUES: none`.
* **`.github/workflows/pages.yml`** — publishes `deploy/` to GitHub Pages on every push to
  `main`.

## If Pages has not been enabled yet

The site 404s until *Settings → Pages → Source = GitHub Actions* is set **and** the workflow
has run once. That is a one-time switch in the repository settings; nothing in the code needs
to change.
