# Publishing this project to GitHub

Everything on the Git side is **already done** — the repository is initialised, committed and
clean. Only the final `push` needs your GitHub account, because this workspace has no GitHub
app, token or `gh` CLI available (the Arena GitHub connector reports `unsupported`, and the
sandbox has no credentials). Nothing else is missing or blocked.

---

## 1. What is already prepared

| Item | State |
|---|---|
| Branch | `main`, linear history, one commit per work phase |
| Working tree | clean (`git status` returns nothing) |
| Tracked files | 61 — code, data, 18 SVG figures, fonts, logos, notebook, report, site, docs |
| Largest file | 2.5 MB (`Final-Project-Report.pdf`) — well under GitHub's 100 MB hard limit |
| Repository size | ~4.9 MB of Git history (61 files, largest 2.5 MB) |
| Archives | `*.zip` and `*.bundle` are **git-ignored** and purged from history (the 8 MB archive is published on Drive, not in Git) |
| Ready-to-serve site | `deploy/` — published to GitHub Pages by `.github/workflows/pages.yml` |
| GitHub Pages workflow | `.github/workflows/pages.yml` (optional, see §5) |
| Line endings / binary rules | `.gitattributes` |

Commit history:

```
chore(github): gitattributes, optional Pages workflow and push handoff guide
Point archive links at the stable Drive folder; refresh ZIP (76 files) and docs after the live deploy
Deploy single-file web application to Vercel; point all download links at the public Drive mirror
feat(report,site): 78-page report with audit gate and interactive dashboard
feat(assets,notebook): 18 SVG figures, TNR fonts, logos, executed notebook
feat(analysis): deterministic pipeline over the BDG2 Site Fox extract
chore: scaffold repository, licence and dependency manifest
```

---

## 2. Fastest path — GitHub CLI

```bash
cd Smart-Building-Energy-Wastage-Anomaly-Profiling-Ayush-Jha-25SCS1003001336

gh auth login                                   # once per machine
gh repo create smart-building-energy-profiling \
   --public --source=. --remote=origin --push \
   --description "Data-driven detection of energy wastage and anomalies in a six-building smart-meter portfolio (BDG2 Site Fox): 25.30% of energy burned unoccupied, 157 anomaly days, 18.50% savings roadmap."
```

## 3. Path without the CLI — web UI + HTTPS

1. Create an empty repository at <https://github.com/new>:
   - **Name:** `smart-building-energy-profiling`
   - **Visibility:** Public
   - Do **not** add a README, `.gitignore` or licence — the repo already has all three.
2. Push from inside the project folder:

```bash
cd Smart-Building-Energy-Wastage-Anomaly-Profiling-Ayush-Jha-25SCS1003001336

git remote add origin https://github.com/<your-username>/smart-building-energy-profiling.git
git branch -M main
git push -u origin main
```

When Git asks for a password, paste a **Personal Access Token** (GitHub → Settings →
Developer settings → Personal access tokens → *Tokens (classic)* → scope `repo`). A password
will not work; GitHub removed password authentication for Git in 2021.

### SSH variant

```bash
git remote add origin git@github.com:<your-username>/smart-building-energy-profiling.git
git push -u origin main
```

## 4. Pushing from a different machine

`Smart-Building-Energy-Wastage-Anomaly-Profiling-Ayush-Jha-25SCS1003001336.bundle` (in this
workspace) is a single-file copy of the whole repository **including history**. On any machine
with Git:

```bash
git clone Smart-Building-Energy-Wastage-Anomaly-Profiling-Ayush-Jha-25SCS1003001336.bundle repo
cd repo
git remote set-url origin https://github.com/<your-username>/smart-building-energy-profiling.git
git push -u origin main
```

Verify the bundle before trusting it: `git bundle verify <file>.bundle`.

---

## 5. Repository settings worth setting (2 minutes)

**About panel** (top-right of the repo page → gear icon)

- *Description:* Data-driven detection of energy wastage and anomalies in a six-building
  smart-meter portfolio (BDG2 Site Fox) — 25.30% of energy is burned while unoccupied.
- *Website:* `https://yourprogrammerayush.github.io/smart-building-energy-profiling/`
- *Topics:* `energy-analytics` `anomaly-detection` `smart-buildings` `time-series`
  `scikit-learn` `plotly` `data-visualization` `building-data-genome` `sustainability`

**GitHub Pages — the canonical publication**

The workflow in `.github/workflows/pages.yml` publishes `deploy/` to Pages on every push to
`main`. Switch it on once: *Settings → Pages → Build and deployment → Source = **GitHub
Actions***, then re-run the workflow. The site then answers at

    https://yourprogrammerayush.github.io/smart-building-energy-profiling/

`deploy/` contains `index.html` plus the copies it links to (report PDF, executed notebook,
dataset, pipeline script, figures), so every download is same-origin and needs no third-party
host. Keep the workflow path at `deploy`; it is rebuilt from `build_site.py`, which reads the
JSON results and the dataset directly.

**Optional — pin the repo** on your profile and add the link to the submission sheet.

---

## 6. Post-push checklist

- [ ] `git push -u origin main` completes without errors
- [ ] Repository page shows the README with the six shields.io badges rendering
- [ ] `deploy/index.html` renders in the repo's *Preview* tab or via Pages (§5)
- [ ] PDF, notebook and dataset links in the README open (they point at the public Drive folder)
- [ ] Licence reads MIT for code and CC BY-SA 4.0 for the dataset extract
- [ ] Confirm the Repository and Live Site URLs in `PROJECT-LINKS.md` answer 200, then
      `git commit -am "docs: verify publication" && git push`

---

## 7. If you ever need to add the archive to Git

Don't. The 8 MB archive contains a copy of the repository itself, so committing it means every
clone downloads two copies of everything. It is published at the public Drive folder and the
`*.zip` ignore rule keeps it out of Git. If a grader explicitly asks for a repository-internal
archive, use a Git **tag** plus GitHub's "Download ZIP" button instead — that is generated on
demand and stores nothing extra.
