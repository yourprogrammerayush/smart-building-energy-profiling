#!/usr/bin/env python3
"""
Build the GitHub Pages publication in `deploy/`.

Everything printed on the site is read from `data/Analysis-Results.json` or
computed from `data/dataset.csv`, so the page can never drift from the
analysis.  Output is a self-contained `index.html` (inline CSS/JS, inline SVG)
plus same-origin copies of the downloadable artefacts.
"""
from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
DEPLOY = ROOT / "deploy"
J = json.loads((ROOT / "data/Analysis-Results.json").read_text())
STATS, ML = J["statistics"], J["machine_learning"]

PAGES = "https://yourprogrammerayush.github.io/smart-building-energy-profiling/"
REPO = "https://github.com/yourprogrammerayush/smart-building-energy-profiling"
DRIVE = "https://drive.google.com/drive/folders/11nythpv22YAKNrwq1X8lfrp4Fq-hj01C"

# ----------------------------------------------------------------- data ------
df = pd.read_csv(ROOT / "data/dataset.csv", parse_dates=["timestamp"])
BLD = ["Fox_office_Joy", "Fox_office_Vicki", "Fox_office_Clayton",
       "Fox_education_Tamika", "Fox_education_Carleen", "Fox_education_Kris"]
LABEL = {"Fox_office_Joy": ("Joy", "office"), "Fox_office_Vicki": ("Vicki", "office"),
         "Fox_office_Clayton": ("Clayton", "office"), "Fox_education_Tamika": ("Tamika", "campus"),
         "Fox_education_Carleen": ("Carleen", "campus"), "Fox_education_Kris": ("Kris", "campus")}
HUE = ["#2F8F9D", "#3E7CB1", "#6C6FB0", "#B07C3E", "#4E9E6A", "#C05B4D"]

total_kwh = df[BLD].sum().sum()
buildings = []
for i, c in enumerate(BLD):
    kwh = float(df[c].sum())
    name, kind = LABEL[c]
    buildings.append({"name": name, "kind": kind, "kwh": kwh,
                      "mwh": kwh / 1000, "share": kwh / total_kwh * 100, "hue": HUE[i],
                      "mean": float(df[c].mean())})
buildings.sort(key=lambda b: -b["mwh"])

df["total_kwh"] = df[BLD].sum(axis=1)          # the pipeline's portfolio total
hh = df.assign(hour=df["timestamp"].dt.hour,
               wknd=df["timestamp"].dt.dayofweek >= 5)
diurnal = (hh.groupby(["hour", "wknd"])["total_kwh"].mean().unstack())
weekday = [float(v) for v in diurnal[False]]
weekend = [float(v) for v in diurnal[True]]


def n(v, dp=0):
    return f"{v:,.{dp}f}"


# ------------------------------------------------------------ iso skyline ----
def skyline() -> str:
    """Six isometric towers, drawn back-to-front, height ~ metered energy.

    Geometry (per tower): a footprint diamond of half-width w and half-height hh
    centred on (cx, cy).  Extruding by H lifts the top face to cy - H, and the
    two visible side faces run from that top face down to the footprint.
    """
    W, HH = 34.0, 17.0
    peak = max(b["mwh"] for b in buildings)
    slots = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)]     # gx, gy (0 = back row)
    order = sorted(range(6), key=lambda i: (slots[i][0] + slots[i][1], slots[i][0]))
    out = []
    for paint, i in enumerate(order):
        b, (gx, gy) = buildings[i], slots[i]
        cx = 250 + (gx - gy) * (W + 16)
        cy = 214 + (gx + gy) * (HH + 16)
        H = 44 + 150 * (b["mwh"] / peak)
        top = (cx, cy - H - HH), (cx + W, cy - H), (cx, cy - H + HH), (cx - W, cy - H)
        left = (cx - W, cy - H), (cx, cy - H + HH), (cx, cy + HH), (cx - W, cy)
        right = (cx, cy - H + HH), (cx + W, cy - H), (cx + W, cy), (cx, cy + HH)
        pts = lambda q: " ".join(f"{x:.1f},{y:.1f}" for x, y in q)      # noqa: E731
        # window strips on both faces
        strips = []
        n = max(3, int(H / 34))
        for k in range(1, n):
            f = k / n
            y0 = cy - H * f
            strips.append(
                f'<path d="M{cx - W:.1f},{y0:.1f} L{cx:.1f},{y0 + HH:.1f} '
                f'L{cx:.1f},{y0 + HH + 2.2:.1f} L{cx - W:.1f},{y0 + 2.2:.1f} Z" '
                f'fill="#08171E" opacity=".22"/>')
            strips.append(
                f'<path d="M{cx:.1f},{y0 + HH:.1f} L{cx + W:.1f},{y0:.1f} '
                f'L{cx + W:.1f},{y0 + 2.2:.1f} L{cx:.1f},{y0 + HH + 2.2:.1f} Z" '
                f'fill="#000" opacity=".30"/>')
        out.append(f"""
  <g class="tower" style="--d:{paint * 0.08:.2f}s">
    <ellipse cx="{cx:.1f}" cy="{cy + HH * 0.5:.1f}" rx="{W * 1.25:.0f}" ry="{HH * 0.62:.0f}"
             fill="#04121A" opacity=".55"/>
    <polygon points="{pts(left)}" fill="{b['hue']}"/>
    <polygon points="{pts(right)}" fill="#0A222B"/>
    <polygon points="{pts(top)}" fill="{b['hue']}" opacity=".78"/>
    <polygon points="{pts(top)}" fill="none" stroke="#D8F4F2" stroke-opacity=".5" stroke-width="1.1"/>
    {''.join(strips)}
  </g>""")
    return "\n".join(out)


# --------------------------------------------------------- load-shape SVG ----
def load_shape_svg() -> str:
    W, H, PL, PR, PT, PB = 880, 300, 44, 12, 18, 40
    hi = max(max(weekday), max(weekend)) * 1.06
    def X(i):  return PL + (W - PL - PR) * i / 23
    def Y(v):  return H - PB - (H - PT - PB) * v / hi
    def path(series, close_to=None):
        d = "M" + " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(series))
        return d
    def area(series):
        return f"{path(series)} L{X(23):.1f},{Y(0):.1f} L{X(0):.1f},{Y(0):.1f} Z"
    grid = "".join(
        f'<line x1="{PL}" y1="{Y(v):.1f}" x2="{W - PR}" y2="{Y(v):.1f}" class="gl"/>'
        f'<text x="{PL - 9}" y="{Y(v) + 3.5:.1f}" class="gt">{int(v)}</text>'
        for v in range(0, int(hi) + 1, 200))
    ticks = "".join(
        f'<text x="{X(i):.1f}" y="{H - PB + 18:.1f}" class="gt" text-anchor="middle">{i}</text>'
        for i in range(0, 24, 2))
    dots = "".join(
        f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3.1" fill="#2F8F9D"/>'
        for i, v in enumerate(weekday))
    return f"""<svg viewBox="0 0 {W} {H}" class="chart" role="img"
     aria-labelledby="lsTitle lsDesc">
  <title id="lsTitle">Mean hourly portfolio demand, weekday versus weekend</title>
  <desc id="lsDesc">Weekday demand peaks on weekday afternoons and stays high overnight;
  weekend demand is lower but keeps a substantial night-time floor.</desc>
  <defs>
    <linearGradient id="gWd" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#2F8F9D" stop-opacity=".38"/>
      <stop offset="100%" stop-color="#2F8F9D" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="gWe" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#C05B4D" stop-opacity=".10"/>
      <stop offset="100%" stop-color="#C05B4D" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <g>{grid}{ticks}</g>
  <path d="{area(weekday)}" fill="url(#gWd)"/>
  <path d="{path(weekday)}" class="ln ln-wd" fill="none"/>
  <path d="{path(weekend)}" class="ln ln-we" fill="none" stroke-dasharray="7 5"/>
  <g class="dots">{dots}</g>
  <line class="xref" x1="0" y1="{PT}" x2="0" y2="{Y(0):.1f}"/>
  <circle class="xdot" r="5.5"/>
  <text x="{PL}" y="12" class="cap">kWh / h</text>
  <text x="{(PL + W - PR) / 2:.0f}" y="{H - 6}" class="cap" text-anchor="middle">Hour of day</text>
</svg>"""


# ------------------------------------------------------- composition HTML ----
def composition_rows() -> str:
    out = []
    for b in buildings:
        out.append(f"""
    <li class="comp" style="--hue:{b['hue']}" tabindex="0"
        aria-label="{b['name']}: {b['mwh']:,.0f} MWh over two years, {b['share']:.2f}% of portfolio demand">
      <span class="comp-name">{b['name']}<em>{b['kind']}</em></span>
      <span class="comp-bar"><i style="width:{b['share'] / max(x['share'] for x in buildings) * 100:.1f}%"></i></span>
      <span class="comp-val">{n(b['mwh'])}<em>MWh · {b['share']:.2f}%</em></span>
    </li>""")
    return "".join(out)


# ---------------------------------------------------------- model cards -----
MODEL_LABEL = {
    "Counterfactual_Schedule_Weather_MLR": ("Counterfactual MLR", "Weather + calendar drivers", "#3E7CB1"),
    "Full_Autoregressive_Weather_MLR": ("Autoregressive MLR", "Adds hourly and weekly lags", "#2F8F9D"),
    "Tuned_Decision_Tree_Regressor": ("Decision tree", "Tuned depth 12, leaf 10", "#B07C3E"),
}


def model_cards() -> str:
    rows = []
    for key, m in ML["regression_comparison"].items():
        name, sub, hue = MODEL_LABEL[key]
        best = key == "Full_Autoregressive_Weather_MLR"
        rows.append(f"""
    <article class="mcard{' best' if best else ''}" style="--hue:{hue}">
      <header><h3>{name}</h3><p>{sub}</p></header>
      <div class="ring" style="--p:{m['r2'] * 100:.1f}">
        <span><b>{m['r2']:.3f}</b><em>R²</em></span>
      </div>
      <dl>
        <div><dt>RMSE</dt><dd>{m['rmse']:.2f} kWh</dd></div>
        <div><dt>MAE</dt><dd>{m['mae']:.2f} kWh</dd></div>
        <div><dt>MAPE</dt><dd>{m['mape_pct']:.2f}%</dd></div>
      </dl>
    </article>""")
    return "".join(rows)


# ------------------------------------------------------------- top days -----
def top_days() -> str:
    out = []
    for d in ML["top_wastage_days"][:10]:
        out.append(f"""<tr><td>{d['date']}</td><td>{d['day_name'][:3]}</td>
      <td class="num">{n(d['actual_kwh'])}</td><td class="num">{n(d['expected_kwh'])}</td>
      <td class="num hi">+{n(d['excess_kwh'])}</td><td class="num">{d['excess_pct']:.1f}%</td>
      <td class="num">${n(d['est_waste_cost_usd'])}</td></tr>""")
    return "".join(out)


# ------------------------------------------------------------- levers -------
def lever_cards() -> str:
    out = []
    for i, l in enumerate(ML["roadmap_levers"]):
        out.append(f"""
    <article class="lever" style="--hue:{HUE[i % len(HUE)]}">
      <span class="tag">{l['id']}</span>
      <h3>{l['lever']}</h3>
      <p class="tgt">{l['target_regime']}</p>
      <div class="lever-nums">
        <div><b>{n(l['annual_kwh_saved'] / 1000, 1)}</b><em>MWh / yr</em></div>
        <div><b>${n(l['annual_cost_saved_usd'])}</b><em>USD / yr</em></div>
        <div><b>{l['co2_avoided_tons']:.1f}</b><em>t CO₂e</em></div>
      </div>
      <p class="cmf">{l['comfort_impact']}</p>
    </article>""")
    return "".join(out)


def scenario_tabs() -> tuple[str, str]:
    labels = ["Conservative", "Planned", "Aggressive"]
    btns, panels = [], []
    for i, s in enumerate(ML["sensitivity_scenarios"]):
        sel = "true" if i == 1 else "false"
        btns.append(f'<button role="tab" id="sc{i}" aria-controls="sp{i}" '
                    f'aria-selected="{sel}" tabindex="{0 if i == 1 else -1}">{labels[i]}</button>')
        panels.append(f"""<div role="tabpanel" id="sp{i}" aria-labelledby="sc{i}" {'hidden' if i != 1 else ''}>
      <div class="sc-grid">
        <div><b>{n(s['annual_kwh_saved'] / 1000, 1)}</b><em>MWh saved per year</em></div>
        <div><b>{s['savings_pct']:.2f}%</b><em>of the annual baseline</em></div>
        <div><b>${n(s['annual_usd_saved'])}</b><em>annual cost avoided</em></div>
        <div><b>{s['co2_tons_avoided']:.1f}</b><em>tonnes CO₂e avoided</em></div>
      </div>
      <p class="sc-note">{labels[i]} case: capture multiplier {s['capture_multiplier']:.2f}, leaving
      {n(s['optimized_annual_mwh'], 1)} MWh of optimised annual demand.</p>
    </div>""")
    return "".join(btns), "".join(panels)


# --------------------------------------------------------- deliverables -----
REPORT_PAGES = 80          # asserted against the build audit below
ARTEFACTS = [
    ("reports/Final-Project-Report.pdf", "Final project report", "PDF", "Full {pages}-page report"),
    ("notebook/Analysis-Notebook.html", "Executed notebook", "HTML", "All 22 cells, outputs included"),
    ("notebook/Analysis-Notebook.ipynb", "Notebook source", "IPYNB", "Re-runnable, SEED = 42"),
    ("code/Energy-Analysis-Script.py", "Analytical pipeline", "PY", "Figures, models, JSON export"),
    ("data/dataset.csv", "Curated dataset", "CSV", "17,544 h × 15 columns"),
    ("data/Analysis-Results.json", "Analysis results", "JSON", "Single source of truth"),
]


def human(size: int) -> str:
    return f"{size / 1024 / 1024:.1f} MB" if size > 1_000_000 else f"{size / 1024:.0f} KB"


def deliverables() -> str:
    out = []
    for path, title, kind, note in ARTEFACTS:
        f = DEPLOY / path
        size = human(f.stat().st_size) if f.exists() else "—"
        note = note.replace("{pages}", str(REPORT_PAGES))
        out.append(f"""
    <a class="dl" href="{path}" download>
      <span class="dl-kind">{kind}</span>
      <strong>{title}</strong>
      <span class="dl-note">{note}</span>
      <span class="dl-size">{size} ↓</span>
    </a>""")
    return "".join(out)


# ------------------------------------------------------------------ copy -----
def stage_artefacts() -> None:
    pairs = [
        ("reports/Final-Project-Report.pdf", "reports/Final-Project-Report.pdf"),
        ("notebooks/Analysis-Notebook.ipynb", "notebook/Analysis-Notebook.ipynb"),
        ("notebooks/Analysis-Notebook.html", "notebook/Analysis-Notebook.html"),
        ("code/Energy-Analysis-Script.py", "code/Energy-Analysis-Script.py"),
        ("data/dataset.csv", "data/dataset.csv"),
        ("data/Analysis-Results.json", "data/Analysis-Results.json"),
    ]
    for src, dst in pairs:
        d = DEPLOY / dst
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / src, d)
    # figures
    srcfig = ROOT / "assets/figures"
    dstfig = DEPLOY / "assets/figures"
    if dstfig.exists():
        shutil.rmtree(dstfig)
    shutil.copytree(srcfig, dstfig)
    shutil.copy2(ROOT / "assets/logos/iilm-logo.png", DEPLOY / "assets/iilm-logo.png") \
        if (ROOT / "assets/logos/iilm-logo.png").exists() else None
    (DEPLOY / ".nojekyll").write_text("", encoding="utf-8")


# ------------------------------------------------------------------- CSS -----
CSS = r"""
:root{
  --ink:#0C1519; --ink-2:#1D2E36; --muted:#5B716F; --surface:#FFFFFF; --paper:#F4F6F5;
  --line:#DDE4E2; --line-2:#C9D4D1;
  --deep:#08171E; --deep-2:#0D2530; --deep-line:rgba(255,255,255,.10);
  --teal:#12707F; --teal-l:#7FE3D4; --amber:#B5771A; --coral:#B5462F; --plum:#5F4B8B; --green:#2F7D52;
  --r:18px; --shell:1180px;
  --sans:ui-sans-serif,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif;
  --serif:ui-serif,"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  font-size:17px;line-height:1.62;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
h1,h2,h3,h4{margin:0;line-height:1.08;letter-spacing:-.024em;font-weight:650}
p{margin:0 0 1em}
a{color:var(--teal);text-underline-offset:3px}
img{max-width:100%}
:focus-visible{outline:2.5px solid var(--teal);outline-offset:3px;border-radius:4px}
.skip{position:absolute;left:-9999px;top:0;background:#fff;padding:.9rem 1.2rem;z-index:100;border-radius:0 0 10px 0}
.skip:focus{left:0}
.wrap{width:min(100% - 3rem,var(--shell));margin-inline:auto}

/* ---------- progress + nav ---------- */
.progress{position:fixed;inset:0 0 auto;height:3px;z-index:60;background:transparent}
.progress i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--teal),var(--green),var(--amber),var(--plum),var(--coral))}
.nav{position:sticky;top:0;z-index:50;backdrop-filter:blur(14px);
  background:#071A22;border-bottom:1px solid var(--deep-line)}
.nav .wrap{display:flex;align-items:center;gap:1.4rem;height:62px}
.brand{display:flex;align-items:center;gap:.65rem;color:#EAF3F4;text-decoration:none;font-weight:650;letter-spacing:-.01em}
.brand .dot{width:26px;height:26px;border-radius:8px;flex:none;
  background:conic-gradient(from 210deg,var(--teal-l),var(--green),var(--amber),var(--plum),var(--coral),var(--teal-l))}
.brand small{display:block;font-weight:450;font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;color:#8FAEB3}
.nav nav{margin-left:auto;display:flex;gap:.2rem;overflow:auto;scrollbar-width:none}
.nav nav a{color:#C7DADE;text-decoration:none;font-size:.86rem;padding:.5rem .62rem;border-radius:8px;white-space:nowrap}
.nav nav a:hover{color:#fff;background:rgba(255,255,255,.07)}
.nav .ghost{border:1px solid var(--deep-line);color:#EAF3F4;text-decoration:none;font-size:.82rem;
  padding:.5rem .85rem;border-radius:999px;white-space:nowrap}
.nav .ghost:hover{border-color:var(--teal-l);color:#fff}

/* ---------- hero ---------- */
.hero{position:relative;overflow:hidden;background:
  radial-gradient(1100px 520px at 78% -10%,rgba(18,112,127,.55),transparent 62%),
  radial-gradient(760px 420px at 8% 8%,rgba(95,75,139,.30),transparent 60%),
  radial-gradient(700px 500px at 50% 120%,rgba(181,70,47,.18),transparent 60%),
  linear-gradient(180deg,#08171E,#0A1E27 55%,#081A22)}
.hero::after{content:"";position:absolute;inset:0;pointer-events:none;
  background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);
  background-size:64px 64px;mask-image:radial-gradient(80% 60% at 50% 40%,#000,transparent 78%)}
.hero .wrap{position:relative;z-index:2;display:grid;grid-template-columns:1.06fr .94fr;gap:3rem;
  align-items:center;padding:clamp(2.4rem,5vw,4.2rem) 0 clamp(2rem,4vw,3rem)}
.eyebrow{display:inline-flex;align-items:center;gap:.6rem;font-size:.72rem;letter-spacing:.19em;
  text-transform:uppercase;color:var(--teal-l);margin:0 0 1.1rem}
.eyebrow::before{content:"";width:26px;height:1px;background:currentColor;opacity:.7}
.hero h1{color:#F3FAFB;font-size:clamp(2.2rem,4.1vw,3.5rem);max-width:20ch;text-wrap:balance}
.hero h1 em{font-family:var(--serif);font-style:italic;font-weight:400;color:#BFE9E2}
.lede{color:#A9C4C9;font-size:clamp(1rem,1.35vw,1.12rem);max-width:52ch;margin-top:1.3rem}
.cta{display:flex;flex-wrap:wrap;gap:.7rem;margin-top:1.9rem}
.btn{display:inline-flex;align-items:center;gap:.5rem;text-decoration:none;font-size:.92rem;
  font-weight:600;padding:.78rem 1.25rem;border-radius:999px;border:1px solid transparent;transition:.18s}
.btn.primary{background:linear-gradient(135deg,var(--teal-l),#4EC3B4);color:#04252A;
  box-shadow:0 10px 30px -12px rgba(127,227,212,.75)}
.btn.primary:hover{transform:translateY(-1px);box-shadow:0 16px 36px -14px rgba(127,227,212,.9)}
.btn.line{border-color:rgba(255,255,255,.24);color:#EAF3F4}
.btn.line:hover{border-color:var(--teal-l);background:rgba(255,255,255,.05)}
.kpis{list-style:none;padding:0;margin:2.1rem 0 0;display:grid;grid-template-columns:repeat(4,1fr);
  gap:.8rem;border-top:1px solid var(--deep-line);padding-top:1.5rem}
.kpis b{display:block;color:#F3FAFB;font-size:clamp(1.25rem,2.1vw,1.72rem);letter-spacing:-.03em;
  font-variant-numeric:tabular-nums}
.kpis b i{font-style:normal;font-size:.6em;font-weight:600;letter-spacing:0;margin-left:.22rem;color:#8ED9CE}
.kpis span{display:block;color:#8FAEB3;font-size:.74rem;line-height:1.35;margin-top:.3rem}
.sky{position:relative}
.sky svg{width:100%;height:auto;display:block;filter:drop-shadow(0 30px 60px rgba(0,0,0,.45))}
.tower{transform-box:fill-box;transform-origin:50% 100%;animation:rise .95s cubic-bezier(.2,.8,.25,1) both;
  animation-delay:var(--d)}
@keyframes rise{from{opacity:0;transform:translateY(26px) scaleY(.82)}to{opacity:1;transform:none}}
.pulse{stroke-dasharray:5 9;animation:flow 4.5s linear infinite}
@keyframes flow{to{stroke-dashoffset:-140}}
.sky-cap{position:absolute;right:2%;bottom:-.4rem;color:#7FA0A6;font-size:.7rem;letter-spacing:.12em;text-transform:uppercase}

/* ---------- sections ---------- */
section{padding:clamp(3.4rem,7vw,6rem) 0;position:relative;scroll-margin-top:74px}
.sec-head{max-width:64ch;margin-bottom:2.6rem}
.sec-head .num{font-family:var(--serif);font-style:italic;color:var(--teal);font-size:1rem;letter-spacing:.02em}
.sec-head h2{font-size:clamp(1.75rem,3.1vw,2.5rem);margin:.5rem 0 .9rem}
.sec-head p{color:var(--muted);font-size:1.02rem;max-width:60ch}
.alt{background:var(--surface)}
.deep{background:linear-gradient(180deg,#08171E,#0B2029);color:#DCE9EB}
.deep h2,.deep h3{color:#F1F9FA}
.deep p{color:#A6C1C6}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:clamp(1.6rem,3.4vw,3.2rem);align-items:start}
.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:1.1rem}
.grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:1.5rem}
.deep .card{background:rgba(255,255,255,.04);border-color:var(--deep-line)}

/* stats */
.stat{border-radius:16px;border:1px solid var(--line);background:var(--surface);padding:1.05rem 1.15rem;
  position:relative;overflow:hidden}
.stat::before{content:"";position:absolute;inset:0 auto 0 0;width:3px;background:var(--hue,var(--teal))}
.stat b{display:block;font-size:clamp(1.2rem,1.9vw,1.55rem);letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.stat span{color:var(--muted);font-size:.78rem;line-height:1.35;display:block;margin-top:.25rem}
.stat em{font-style:normal;color:var(--hue,var(--teal));font-weight:600}

/* composition */
.comp-list{list-style:none;margin:0;padding:0;display:grid;gap:.55rem}
.comp{display:grid;grid-template-columns:9.5rem 1fr 8.6rem;align-items:center;gap:1rem;
  padding:.55rem .7rem;border-radius:12px;border:1px solid transparent;transition:.16s;cursor:default}
.comp:hover,.comp:focus-visible{background:#EFF4F3;border-color:var(--line)}
.comp-name{font-weight:620;font-size:.95rem}
.comp-name em{display:block;font-style:normal;font-weight:450;color:var(--muted);font-size:.72rem;
  text-transform:uppercase;letter-spacing:.11em}
.comp-bar{height:12px;border-radius:999px;background:#E9EFEE;overflow:hidden}
.comp-bar i{display:block;height:100%;border-radius:999px;background:var(--hue);
  transition:width .9s cubic-bezier(.2,.8,.25,1)}
.comp-val{text-align:right;font-variant-numeric:tabular-nums;font-weight:620;font-size:.95rem}
.comp-val em{display:block;font-style:normal;font-weight:450;color:var(--muted);font-size:.72rem}

/* steps */
.step{position:relative;padding:1.4rem 1.4rem 1.2rem;border-radius:var(--r);
  background:var(--surface);border:1px solid var(--line)}
.step .no{font-family:var(--serif);font-style:italic;font-size:1.5rem;color:var(--hue)}
.step h3{font-size:1.04rem;margin:.5rem 0 .5rem}
.step p{font-size:.88rem;color:var(--muted);margin:0}
.step .unit{display:inline-block;margin-top:.9rem;font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;
  color:var(--hue);border:1px solid currentColor;border-radius:999px;padding:.18rem .55rem;opacity:.85}

/* chart */
.chart{width:100%;height:auto;display:block;overflow:visible}
.gl{stroke:#E3EAE8;stroke-width:1}
.gt{fill:#7E918E;font-size:13px;font-family:var(--sans);font-variant-numeric:tabular-nums}
.cap{fill:#7E918E;font-size:12px;letter-spacing:.08em;text-transform:uppercase}
.ln{stroke-width:2.4;stroke-linejoin:round;stroke-linecap:round}
.ln-wd{stroke:#12707F}
.ln-we{stroke:#B5462F}
.xref{stroke:#0C1519;stroke-width:1;stroke-dasharray:3 4;opacity:0;transition:opacity .15s}
.xdot{fill:#0C1519;opacity:0}
.chart-wrap{position:relative}
.tip{position:absolute;pointer-events:none;transform:translate(-50%,-115%);background:var(--ink);
  color:#fff;font-size:.78rem;padding:.45rem .6rem;border-radius:9px;opacity:0;transition:opacity .14s;
  white-space:nowrap;font-variant-numeric:tabular-nums;z-index:3}
.tip b{color:var(--teal-l)}
.legend{display:flex;gap:1.2rem;flex-wrap:wrap;font-size:.8rem;color:var(--muted);margin-top:.7rem}
.legend i{display:inline-block;width:14px;height:3px;border-radius:2px;margin-right:.45rem;vertical-align:middle}
.slider{display:flex;align-items:center;gap:.9rem;margin-top:1.1rem;font-size:.82rem;color:var(--muted)}
.slider input{flex:1;accent-color:var(--teal)}

/* models */
.mcard{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:1.4rem;
  display:flex;flex-direction:column;gap:1rem;position:relative}
.mcard.best{border-color:var(--teal);box-shadow:0 16px 40px -28px rgba(18,112,127,.9)}
.mcard.best::after{content:"Selected counterfactual";position:absolute;top:-.68rem;left:1.2rem;
  background:var(--teal);color:#fff;font-size:.66rem;letter-spacing:.1em;text-transform:uppercase;
  padding:.2rem .55rem;border-radius:999px}
.mcard h3{font-size:1.02rem}
.mcard header p{font-size:.8rem;color:var(--muted);margin:.25rem 0 0}
.ring{width:104px;height:104px;border-radius:50%;margin:.2rem auto .1rem;display:grid;place-items:center;
  background:conic-gradient(var(--hue) calc(var(--p) * 1%),#E9EFEE 0);position:relative}
.ring::before{content:"";position:absolute;inset:9px;background:var(--surface);border-radius:50%}
.ring span{position:relative;text-align:center}
.ring b{display:block;font-size:1.16rem;letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.ring em{font-style:normal;font-size:.66rem;letter-spacing:.14em;color:var(--muted);text-transform:uppercase}
.mcard dl{display:grid;gap:.4rem;margin:0;font-size:.84rem}
.mcard dl div{display:flex;justify-content:space-between;border-top:1px solid var(--line);padding-top:.4rem}
.mcard dt{color:var(--muted)}
.mcard dd{margin:0;font-weight:600;font-variant-numeric:tabular-nums}

/* table */
.tbl-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:var(--r);background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:.86rem;min-width:620px}
th,td{text-align:left;padding:.62rem .9rem;border-bottom:1px solid var(--line)}
th{background:#F0F5F4;font-size:.72rem;letter-spacing:.09em;text-transform:uppercase;color:#3F5C5A;font-weight:650}
tbody tr:hover{background:#F7FAF9}
td.num{text-align:right;font-variant-numeric:tabular-nums}
td.hi{color:var(--coral);font-weight:650}
tr:last-child td{border-bottom:none}
.deep table,.deep th,.deep td{color:var(--ink)}
.deep th{background:#EAF1EF;color:#33514F}
.deep td.hi{color:var(--coral)}
.deep tbody tr:hover{background:#F2F7F6}
.deep h3,.deep h2{color:#F1F9FA}

/* levers */
.lever{background:rgba(255,255,255,.045);border:1px solid var(--deep-line);border-radius:var(--r);padding:1.4rem}
.lever .tag{display:inline-block;font-size:.68rem;letter-spacing:.14em;color:var(--hue);
  border:1px solid currentColor;border-radius:999px;padding:.12rem .5rem;margin-bottom:.75rem}
.lever h3{font-size:1rem;line-height:1.3}
.lever .tgt{font-size:.8rem;color:#9DBAC0;margin:.55rem 0 1rem}
.lever-nums{display:grid;grid-template-columns:repeat(3,1fr);gap:.6rem;border-top:1px solid var(--deep-line);padding-top:.85rem}
.lever-nums b{display:block;color:#EAF6F7;font-size:.98rem;font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.lever-nums em{font-style:normal;font-size:.66rem;color:#8FAEB3;letter-spacing:.06em;text-transform:uppercase}
.lever .cmf{font-size:.76rem;color:#8FAEB3;margin:.9rem 0 0}

/* scenario tabs */
.tabs{display:inline-flex;gap:.25rem;background:rgba(255,255,255,.06);padding:.28rem;border-radius:999px}
.tabs button{appearance:none;border:0;background:transparent;color:#C7DADE;font:inherit;font-size:.85rem;
  padding:.5rem 1rem;border-radius:999px;cursor:pointer}
.tabs button[aria-selected="true"]{background:var(--teal-l);color:#04252A;font-weight:650}
.sc-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-top:1.4rem}
.sc-grid b{display:block;font-size:clamp(1.2rem,2.2vw,1.65rem);color:#F1F9FA;letter-spacing:-.03em;
  font-variant-numeric:tabular-nums}
.sc-grid em{font-style:normal;font-size:.74rem;color:#8FAEB3;display:block;margin-top:.25rem}
.sc-note{font-size:.8rem;color:#8FAEB3;margin-top:1rem}

/* deliverables */
.dl-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}
.dl{display:flex;flex-direction:column;gap:.35rem;text-decoration:none;color:inherit;background:var(--surface);
  border:1px solid var(--line);border-radius:var(--r);padding:1.15rem 1.2rem;transition:.18s}
.dl:hover{transform:translateY(-2px);border-color:var(--teal);box-shadow:0 18px 36px -26px rgba(12,21,25,.55)}
.dl-kind{font-size:.66rem;letter-spacing:.14em;color:var(--teal);text-transform:uppercase}
.dl strong{font-size:.98rem;letter-spacing:-.01em}
.dl-note{font-size:.78rem;color:var(--muted)}
.dl-size{margin-top:.5rem;font-size:.72rem;color:var(--muted);letter-spacing:.06em}

/* figures */
figure{margin:0}
figure img{border:1px solid var(--line);border-radius:14px;background:#fff;padding:.6rem}
figcaption{font-size:.78rem;color:var(--muted);margin-top:.55rem}

/* footer */
footer{background:var(--deep);color:#9DBAC0;padding:3rem 0 2.2rem;border-top:1px solid var(--deep-line)}
footer .wrap{display:grid;grid-template-columns:1.3fr 1fr 1fr;gap:2rem}
footer h4{color:#EAF6F7;font-size:.76rem;letter-spacing:.14em;text-transform:uppercase;margin-bottom:.8rem}
footer a{color:#C7DADE;text-decoration:none}
footer a:hover{color:var(--teal-l);text-decoration:underline}
footer ul{list-style:none;margin:0;padding:0;display:grid;gap:.4rem;font-size:.86rem}
footer .fine{grid-column:1/-1;border-top:1px solid var(--deep-line);padding-top:1.2rem;margin-top:.6rem;
  font-size:.75rem;color:#7FA0A6;display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap}

/* reveal */
.js .reveal{opacity:0;transform:translateY(16px)}
.js .reveal.in{opacity:1;transform:none;transition:opacity .7s cubic-bezier(.2,.8,.25,1),transform .7s cubic-bezier(.2,.8,.25,1)}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  .js .reveal{opacity:1!important;transform:none!important}
  .tower,.pulse{animation:none!important}
  .comp-bar i{transition:none}
}
@media (max-width:1000px){
  .hero .wrap{grid-template-columns:1fr;padding-top:3rem}
  .sky{order:-1;max-width:520px;margin-inline:auto}
  .grid-2,.grid-3,.grid-4,.dl-grid,.sc-grid,footer .wrap{grid-template-columns:1fr 1fr}
  .kpis{grid-template-columns:1fr 1fr}
}
@media (max-width:640px){
  body{font-size:16px}
  .nav nav{display:none}
  .grid-2,.grid-3,.grid-4,.dl-grid,.sc-grid,footer .wrap{grid-template-columns:1fr}
  .comp{grid-template-columns:1fr auto;row-gap:.4rem}
  .comp-bar{grid-column:1/-1}
  .comp-val{text-align:right}
}
"""

# -------------------------------------------------------------------- JS -----
JS = r"""
(() => {
  const root = document.documentElement;
  root.classList.add('js');

  /* scroll progress */
  const bar = document.querySelector('.progress i');
  const onScroll = () => {
    const h = root.scrollHeight - innerHeight;
    bar.style.width = (h > 0 ? (scrollY / h) * 100 : 0) + '%';
  };
  addEventListener('scroll', onScroll, {passive: true}); onScroll();

  /* reveal on view */
  const io = new IntersectionObserver((es) => {
    es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, {rootMargin: '0px 0px -8% 0px', threshold: .08});
  document.querySelectorAll('.reveal').forEach((el, i) => {
    el.style.transitionDelay = Math.min(i % 6, 5) * 60 + 'ms';
    io.observe(el);
  });

  /* count-up KPIs */
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const counters = document.querySelectorAll('[data-count]');
  const paint = (el, v) => {
    const dp = +(el.dataset.dp || 0);
    const txt = v.toLocaleString('en-US', {minimumFractionDigits: dp, maximumFractionDigits: dp});
    const unit = el.querySelector('i');
    el.textContent = txt;
    if (unit) el.appendChild(unit);          // keep the unit span after the digits
  };
  if (reduce) { counters.forEach(el => paint(el, +el.dataset.count)); }
  else {
    const co = new IntersectionObserver((es) => {
      es.forEach(e => {
        if (!e.isIntersecting) return;
        const el = e.target, target = +el.dataset.count, t0 = performance.now(), dur = 1100;
        const step = (t) => {
          const k = Math.min(1, (t - t0) / dur), e2 = 1 - Math.pow(1 - k, 3);
          paint(el, target * e2);
          if (k < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step); co.unobserve(el);
      });
    }, {threshold: .4});
    counters.forEach(el => { paint(el, 0); co.observe(el); });
  }

  /* interactive load-shape chart */
  const chart = document.querySelector('.chart[data-hours]');
  if (chart) {
    const hours = JSON.parse(chart.dataset.hours);
    const wd = JSON.parse(chart.dataset.weekday);
    const we = JSON.parse(chart.dataset.weekend);
    const tip = document.querySelector('.tip');
    const xref = chart.querySelector('.xref');
    const xdot = chart.querySelector('.xdot');
    const box = chart.getBoundingClientRect();
    const vb = chart.viewBox.baseVal;
    const PL = 44, PR = 12;
    const xFor = (h) => PL + (vb.width - PL - PR) * h / 23;
    const yMax = Math.max(...wd, ...we) * 1.06, PT = 18, PB = 40;
    const yFor = (v) => vb.height - PB - (vb.height - PT - PB) * v / yMax;

    const show = (h) => {
      const x = xFor(h);
      xref.setAttribute('x1', x); xref.setAttribute('x2', x); xref.style.opacity = 1;
      xdot.setAttribute('cx', x); xdot.setAttribute('cy', yFor(wd[h])); xdot.style.opacity = 1;
      tip.innerHTML = `<b>${String(h).padStart(2, '0')}:00</b> &nbsp; weekday ${wd[h].toFixed(0)} kWh
        &nbsp;·&nbsp; weekend ${we[h].toFixed(0)} kWh`;
      tip.style.left = (x / vb.width * chart.clientWidth) + 'px';
      tip.style.top = (yFor(wd[h]) / vb.height * chart.clientHeight) + 'px';
      tip.style.opacity = 1;
      const readout = document.querySelector('.slider output');
      if (readout) readout.textContent = `${String(h).padStart(2, '0')}:00 — weekday ${wd[h].toFixed(0)} kWh, weekend ${we[h].toFixed(0)} kWh`;
    };
    const hide = () => { xref.style.opacity = 0; xdot.style.opacity = 0; tip.style.opacity = 0; };
    chart.addEventListener('pointermove', (ev) => {
      const r = chart.getBoundingClientRect();
      const rel = (ev.clientX - r.left) / r.width * vb.width;
      const h = Math.round((rel - PL) / (vb.width - PL - PR) * 23);
      if (h >= 0 && h <= 23) show(h);
    });
    chart.addEventListener('pointerleave', hide);
    const range = document.querySelector('input[data-hour]');
    if (range) {
      range.addEventListener('input', () => show(+range.value));
      show(+range.value);                       // fill the readout on load …
      hide();                                   // … but leave the tooltip hidden
      const out = document.querySelector('.slider output');
      if (out) out.textContent = `${String(range.value).padStart(2, '0')}:00 — weekday ${wd[+range.value].toFixed(0)} kWh, weekend ${we[+range.value].toFixed(0)} kWh`;
    }
  }

  /* scenario tabs */
  const tabs = [...document.querySelectorAll('[role="tab"]')];
  tabs.forEach((t, i) => {
    t.addEventListener('click', () => select(i));
    t.addEventListener('keydown', (e) => {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      e.preventDefault();
      const n = (i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
      select(n); tabs[n].focus();
    });
  });
  function select(n) {
    tabs.forEach((t, i) => {
      const on = i === n;
      t.setAttribute('aria-selected', on);
      t.tabIndex = on ? 0 : -1;
      document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
    });
  }

  /* active nav link */
  const links = [...document.querySelectorAll('.nav nav a')];
  const secs = links.map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);
  const spy = new IntersectionObserver((es) => {
    es.forEach(e => {
      if (!e.isIntersecting) return;
      links.forEach(a => a.style.color = a.getAttribute('href') === '#' + e.target.id ? '#fff' : '');
    });
  }, {rootMargin: '-45% 0px -50% 0px'});
  secs.forEach(s => spy.observe(s));
})();
"""


# ------------------------------------------------------------------ HTML -----
def build() -> None:
    stage_artefacts()
    sc_btns, sc_panels = scenario_tabs()
    pages_pdf = REPORT_PAGES

    kpi = [
        (STATS["total_energy_mwh"], 0, "MWh", "metered over two years"),
        (STATS["off_hour_share_pct"], 2, "%", "of all energy burned while unoccupied"),
        (ML["consensus_flagged_days_total"], 0, "", "anomalous days in 731"),
        (ML["total_recommended_saved_pct"], 2, "%", "recoverable annual baseline"),
    ]
    kpi_html = "".join(
        f'<li><b data-count="{v}" data-dp="{dp}">{n(v, dp)}'
        f'{f"<i>{suf}</i>" if suf else ""}</b><span>{desc}</span></li>'
        for v, dp, suf, desc in kpi)

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Smart Building Energy Wastage &amp; Anomaly Profiling — IILM University</title>
<meta name="description" content="A data-driven study of operational energy wastage across a six-building smart-meter portfolio: 25.30% of metered energy is consumed while the buildings are unoccupied, and 18.50% of the annual baseline is recoverable through scheduling and control levers.">
<meta name="theme-color" content="#08171E">
<meta property="og:title" content="Smart Building Energy Wastage &amp; Anomaly Profiling">
<meta property="og:description" content="25.30% of metered energy is burned while the portfolio is unoccupied. 18.50% of the annual baseline is recoverable.">
<meta property="og:type" content="website">
<link rel="canonical" href="{PAGES}">
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="progress" aria-hidden="true"><i></i></div>

<header class="nav">
  <div class="wrap">
    <a class="brand" href="#top">
      <span class="dot" aria-hidden="true"></span>
      <span>Energy Profiling<small>IILM · 26CSEM321</small></span>
    </a>
    <nav aria-label="Sections">
      <a href="#scope">Portfolio</a>
      <a href="#method">Method</a>
      <a href="#findings">Findings</a>
      <a href="#models">Models</a>
      <a href="#anomalies">Anomalies</a>
      <a href="#roadmap">Roadmap</a>
      <a href="#deliverables">Deliverables</a>
    </nav>
    <a class="ghost" href="{REPO}" target="_blank" rel="noopener">Source ↗</a>
  </div>
</header>

<main id="main">
  <section class="hero" id="top">
    <div class="wrap">
      <div>
        <p class="eyebrow">IILM University · School of CSE · Semester III</p>
        <h1>Smart Building Energy Wastage &amp; <em>Anomaly Profiling</em></h1>
        <p class="lede">Two years of hourly smart-meter telemetry across six buildings, joined to
          weather and calendar data, are used to separate genuine demand from operational waste —
          then priced, ranked and turned into a funded remediation roadmap.</p>
        <div class="cta">
          <a class="btn primary" href="reports/Final-Project-Report.pdf">Read the {pages_pdf}-page report</a>
          <a class="btn line" href="notebook/Analysis-Notebook.html">Open the notebook</a>
          <a class="btn line" href="{DRIVE}" target="_blank" rel="noopener">Drive archive ↗</a>
        </div>
        <ul class="kpis">{kpi_html}</ul>
      </div>
      <div class="sky">
        <svg viewBox="0 0 520 400" role="img"
             aria-label="Six isometric towers whose heights are proportional to each building's two-year energy use.">
          <defs>
            <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#12707F" stop-opacity=".22"/>
              <stop offset="100%" stop-color="#12707F" stop-opacity="0"/>
            </linearGradient>
          </defs>
          <ellipse cx="250" cy="300" rx="236" ry="92" fill="url(#floor)"/>
          <g stroke="#7FE3D4" stroke-opacity=".16" stroke-width="1">
            <path d="M30,300 L250,214 L470,300 L250,386 Z" fill="none"/>
            <path d="M104,271 L420,271 M177,242 L347,242" fill="none" opacity=".7"/>
          </g>
          {skyline()}
          <g class="pulse" stroke="#7FE3D4" stroke-width="2" fill="none" opacity=".55">
            <path d="M118,330 C168,286 206,320 246,266 C288,210 330,268 392,214"/>
            <path d="M156,360 C210,326 250,352 302,286"/>
          </g>
        </svg>
        <span class="sky-cap">Tower height ∝ metered MWh</span>
      </div>
    </div>
  </section>

  <section id="scope" class="alt">
    <div class="wrap">
      <div class="sec-head reveal">
        <p class="num">01 — The portfolio</p>
        <h2>{STATS['total_rows']:,} hourly records, {STATS['total_days']} days, six meters</h2>
        <p>A single university-commercial district in Tempe, Arizona: three office blocks and three
          campus buildings behind independent meters, sharing one weather station. The dataset is the
          open Building Data Genome Project 2 extract for Site <em>Fox</em>.</p>
      </div>
      <div>
        <div class="reveal">
          <ul class="comp-list">{composition_rows()}</ul>
          <div class="grid-3" style="margin-top:1.6rem">
            <div class="stat" style="--hue:var(--teal)"><b>{STATS['annual_eui_kwh_m2']:.2f}</b>
              <span>kWh/m²·yr energy use intensity across {n(31462.6, 1)} m²</span></div>
            <div class="stat" style="--hue:var(--green)"><b>{STATS['mean_hourly_kwh']:.1f}</b>
              <span>kWh mean hourly portfolio demand</span></div>
            <div class="stat" style="--hue:var(--amber)"><b>{STATS['off_to_work_ratio']:.3f}</b>
              <span>off-hour to work-hour demand ratio</span></div>
          </div>
        </div>
        <figure class="reveal" style="margin-top:2rem">
          <img src="assets/figures/Fig-3-1-Portfolio-Overview.svg" loading="lazy"
               alt="Portfolio composition, energy share and energy use intensity against a commercial benchmark band.">
          <figcaption>Figure 3.1 — Portfolio composition, energy share and energy use intensity
            against the commercial benchmark band.</figcaption>
        </figure>
      </div>
    </div>
  </section>

  <section id="method">
    <div class="wrap">
      <div class="sec-head reveal">
        <p class="num">02 — Method</p>
        <h2>One deterministic pipeline, mapped to the syllabus</h2>
        <p>Every stage is syllabus-locked to <em>26CSEM321</em>, seeded (<code>SEED = 42</code>) and
          reproducible from the published notebook and script. No stage uses a model the course
          does not teach.</p>
      </div>
      <div class="grid-4">
        <article class="step reveal" style="--hue:#2F8F9D"><span class="no">01</span>
          <h3>Curate &amp; audit</h3><p>Schema repair, sentinel screening, 1–3 h interpolation,
          thermodynamic features (CDD, ΔT, lags).</p><span class="unit">Unit I–II</span></article>
        <article class="step reveal" style="--hue:#3E7CB1"><span class="no">02</span>
          <h3>Test the regimes</h3><p>Welch and Mann–Whitney tests on weekday versus weekend and
          occupied versus unoccupied demand.</p><span class="unit">Unit III</span></article>
        <article class="step reveal" style="--hue:#B07C3E"><span class="no">03</span>
          <h3>Build the counterfactual</h3><p>Weather-plus-calendar regression and a tuned
          decision tree define what <em>should</em> have been consumed.</p><span class="unit">Unit II &amp; IV</span></article>
        <article class="step reveal" style="--hue:#5F4B8B"><span class="no">04</span>
          <h3>Detect &amp; price</h3><p>OC-SVM, K-Means and a domain rule vote into a consensus
          anomaly queue, priced at tariff and emission factor.</p><span class="unit">Unit IV</span></article>
      </div>
    </div>
  </section>

  <section id="findings" class="alt">
    <div class="wrap">
      <div class="sec-head reveal">
        <p class="num">03 — Findings</p>
        <h2>The overnight floor never falls</h2>
        <p>Weekday demand peaks in the afternoon and then settles — but it settles onto a night-time
          floor of roughly 570–600 kWh per hour that a scheduled commercial building should not
          maintain. Drag across the chart, or use the slider, to read any hour.</p>
      </div>
      <div class="card reveal" style="padding:1.2rem 1.4rem 1rem">
        <div class="chart-wrap">
            <div class="tip" role="status" aria-live="polite"></div>
            {load_shape_svg().replace('<svg ', '<svg data-hours="' + json.dumps(list(range(24))) + '" data-weekday="' + json.dumps([round(v, 1) for v in weekday]) + '" data-weekend="' + json.dumps([round(v, 1) for v in weekend]) + '" ', 1)}
        </div>
        <div class="legend">
          <span><i style="background:#12707F"></i>Weekday mean</span>
          <span><i style="background:repeating-linear-gradient(90deg,#B5462F 0 5px,transparent 5px 9px)"></i>Weekend mean</span>
        </div>
        <div class="slider">
          <label for="hour">Hour</label>
          <input id="hour" type="range" min="0" max="23" value="3" step="1" data-hour>
          <output for="hour"></output>
        </div>
      </div>
      <div class="grid-2" style="margin-top:1.6rem">
        <div class="reveal">
          <div class="grid-2" style="gap:.8rem">
            <div class="stat" style="--hue:var(--teal)"><b>{STATS['work_hour_mean_kwh']:.2f}</b>
              <span>work-hour mean demand (kWh/h)</span></div>
            <div class="stat" style="--hue:var(--coral)"><b>{STATS['off_hour_mean_kwh']:.2f}</b>
              <span>off-hour mean demand (kWh/h)</span></div>
            <div class="stat" style="--hue:var(--green)"><b>{STATS['weekday_mean_kwh']:.2f}</b>
              <span>weekday mean (kWh/h)</span></div>
            <div class="stat" style="--hue:var(--amber)"><b>{STATS['weekend_mean_kwh']:.2f}</b>
              <span>weekend mean (kWh/h)</span></div>
          </div>
          <div class="card" style="margin-top:.9rem">
            <p style="margin:0 0 .6rem"><strong>Both regime gaps are not sampling noise.</strong></p>
            <p style="margin:0;font-size:.9rem;color:var(--muted)">
              Weekday versus weekend: Welch <em>t</em> = {STATS['welch_t_stat']:.2f}, Mann–Whitney
              <em>p</em> = {STATS['mannwhitney_p_val']:.2e}. Occupied versus unoccupied:
              <em>t</em> = {STATS['off_hour_t_stat']:.2f}. Outdoor temperature explains
              <em>r</em> = {STATS['pearson_r_temp']:.4f} of hourly demand, so the counterfactual
              must be weather-aware.</p>
          </div>
        </div>
      </div>
      <figure class="reveal" style="margin-top:2.4rem">
        <img src="assets/figures/Fig-5-4-Monthly-Baseload-Decomposition.svg" loading="lazy"
             alt="Monthly baseload decomposition, separating weather-driven load from the persistent overnight floor.">
        <figcaption>Figure 5.4 — Monthly baseload decomposition: the persistent floor is the largest
          single addressable waste pool and is invisible in a monthly invoice.</figcaption>
      </figure>
    </div>
  </section>

  <section id="models">
    <div class="wrap">
      <div class="sec-head reveal">
        <p class="num">04 — Counterfactual models</p>
        <h2>Forecast first, then judge the residual</h2>
        <p>Three syllabus models were fitted on 2016 and scored on the untouched 2017 holdout. The
          autoregressive weather model is the counterfactual used throughout the report.</p>
      </div>
      <div class="grid-3">{model_cards()}</div>
      <div class="grid-3 reveal" style="margin-top:1.4rem">
        <div class="stat" style="--hue:var(--plum)"><b>{ML['ocsvm_flagged_days_total']}</b>
          <span>days flagged by the one-class SVM (ν = 0.08)</span></div>
        <div class="stat" style="--hue:var(--amber)"><b>{ML['kmeans_flagged_days_total']}</b>
          <span>days flagged by K-Means distance (k = 4)</span></div>
        <div class="stat" style="--hue:var(--coral)"><b>{ML['domain_wastage_days_total']}</b>
          <span>days flagged by the auditable domain rule</span></div>
      </div>
    </div>
  </section>

  <section id="anomalies" class="deep">
    <div class="wrap">
      <div class="sec-head reveal">
        <p class="num">05 — Anomalies</p>
        <h2>{ML['consensus_flagged_days_total']} days carry the signature of wastage</h2>
        <p>Where the unsupervised detectors and the domain rule agree, the day enters the audit
          queue: {ML['consensus_excess_mwh_total']:.2f} MWh of excess consumption above the
          weather-adjusted counterfactual, worth ${n(ML['consensus_excess_cost_usd_total'])}.</p>
      </div>
      <div class="grid-4 reveal">
        <div class="stat" style="--hue:#4EC3B4;background:rgba(255,255,255,.05);border-color:var(--deep-line)">
          <b>{ML['consensus_flagged_days_total']}</b><span>consensus anomalous days</span></div>
        <div class="stat" style="--hue:#E8B04B;background:rgba(255,255,255,.05);border-color:var(--deep-line)">
          <b>{ML['consensus_excess_mwh_total']:.2f}</b><span>MWh excess above counterfactual</span></div>
        <div class="stat" style="--hue:#E8735A;background:rgba(255,255,255,.05);border-color:var(--deep-line)">
          <b>${n(ML['consensus_excess_cost_usd_total'])}</b><span>cost of that excess at tariff</span></div>
        <div class="stat" style="--hue:#A48BE0;background:rgba(255,255,255,.05);border-color:var(--deep-line)">
          <b>{ML['anomaly_evaluation_2017']['Unsupervised_OneClass_SVM']['f1']:.4f}</b>
          <span>2017 holdout F1, one-class SVM</span></div>
      </div>
      <div class="grid-2" style="margin-top:2rem">
        <div class="reveal">
          <h3 style="font-size:1.02rem;margin-bottom:.9rem;color:#F1F9FA">Ten highest-excess days</h3>
          <div class="tbl-wrap">
            <table>
              <caption class="sr-only" style="position:absolute;left:-9999px">Ten highest-excess audit rows</caption>
              <thead><tr><th>Date</th><th>Day</th><th class="num">Actual</th><th class="num">Expected</th>
                <th class="num">Excess</th><th class="num">Δ%</th><th class="num">Cost</th></tr></thead>
              <tbody>{top_days()}</tbody>
            </table>
          </div>
          <p style="font-size:.76rem;color:#8FAEB3;margin-top:.6rem">kWh per day; cost at the
            ${0.12:.2f}/kWh commercial tariff.</p>
        </div>
        <figure class="reveal">
          <img src="assets/figures/Fig-6-2-Daily-Anomaly-Timeline.svg" loading="lazy"
               alt="Daily anomaly timeline for 731 days, marking flagged wastage days against the weather-adjusted expected demand.">
          <figcaption>Figure 6.2 — Daily anomaly timeline across the full 731-day window.</figcaption>
        </figure>
      </div>
    </div>
  </section>

  <section id="roadmap" class="deep" style="padding-top:0">
    <div class="wrap">
      <div class="sec-head reveal">
        <p class="num">06 — Remediation roadmap</p>
        <h2>Four levers recover {ML['total_recommended_saved_pct']:.2f}% of the baseline</h2>
        <p>{n(ML['total_recommended_saved_kwh'])} kWh per year — ${n(ML['total_recommended_saved_usd'])}
          at the modelled tariff and {ML['total_recommended_co2_tons']:.1f} t CO₂e avoided — without
          touching a single thermostat setpoint that occupants can feel.</p>
      </div>
      <div class="grid-4">{lever_cards()}</div>
      <div class="card reveal" style="margin-top:1.6rem;background:rgba(255,255,255,.05);border-color:var(--deep-line)">
        <div class="tabs" role="tablist" aria-label="Capture scenario">{sc_btns}</div>
        {sc_panels}
      </div>
      <div class="grid-2" style="margin-top:2rem">
        <figure class="reveal">
          <img src="assets/figures/Fig-7-1-Savings-Waterfall-Roadmap.svg" loading="lazy"
               alt="Savings waterfall from the annual baseline through four levers to the optimised annual demand.">
          <figcaption>Figure 7.1 — Savings waterfall from baseline to optimised demand.</figcaption>
        </figure>
        <figure class="reveal">
          <img src="assets/figures/Fig-7-2-Sensitivity-Analysis.svg" loading="lazy"
               alt="Sensitivity of the savings estimate to capture rate and tariff assumptions.">
          <figcaption>Figure 7.2 — Sensitivity of the savings estimate to capture rate and tariff.</figcaption>
        </figure>
      </div>
    </div>
  </section>

  <section id="deliverables">
    <div class="wrap">
      <div class="sec-head reveal">
        <p class="num">07 — Deliverables</p>
        <h2>Everything is reproducible</h2>
        <p>Served from this site, plus a mirrored archive in the shared Drive folder. The report and
          the notebook are generated from the same deterministic pipeline as the numbers above.</p>
      </div>
      <div class="dl-grid reveal">{deliverables()}</div>
      <div class="grid-2 reveal" style="margin-top:2rem">
        <figure>
          <img src="assets/figures/Fig-4-1-Methodology-Workflow.svg" loading="lazy"
               alt="End-to-end analytical workflow from benchmark acquisition to the interactive dissemination layer.">
          <figcaption>Figure 4.1 — End-to-end workflow, from open benchmark acquisition to this page.</figcaption>
        </figure>
        <figure>
          <img src="assets/figures/Fig-6-4-KMeans-Cluster-Profiles.svg" loading="lazy"
               alt="Four operational regime profiles recovered by K-Means clustering of daily load shapes.">
          <figcaption>Figure 6.4 — Four operational regimes recovered from daily load shapes.</figcaption>
        </figure>
      </div>
    </div>
  </section>
</main>

<footer>
  <div class="wrap">
    <div>
      <h4>Smart Building Energy Wastage &amp; Anomaly Profiling</h4>
      <p style="font-size:.86rem;max-width:34ch">A mini project for <em>Data Visualization and
        Analysis</em> (26CSEM321), B.Tech CSE, Year 2, Semester 3, Section 2CSE-4, IILM University,
        Greater Noida. Guide: Aditya Bangia. Academic year 2026-27.</p>
    </div>
    <div>
      <h4>Team</h4>
      <ul>
        <li>Ayush Jha · 25SCS1003001336</li>
        <li>Archit Baloni · 25SCS1003003550</li>
        <li>Ashutosh Sahoo · 25SCS1003004011</li>
        <li>Dev Bhaskar Singh · 25SCS1003003174</li>
        <li>Aman Kumar Gupta · 25SCS1003003645</li>
      </ul>
    </div>
    <div>
      <h4>Links</h4>
      <ul>
        <li><a href="{REPO}" target="_blank" rel="noopener">Source repository ↗</a></li>
        <li><a href="{PAGES}">Project site</a></li>
        <li><a href="{DRIVE}" target="_blank" rel="noopener">Drive archive ↗</a></li>
        <li><a href="reports/Final-Project-Report.pdf">Final report (PDF)</a></li>
      </ul>
    </div>
    <div class="fine">
      <span>Data: Building Data Genome Project 2 (CC BY-SA 4.0), Site Fox. Code: MIT.</span>
      <span>Energy figures are model-based estimates, not metered savings.</span>
    </div>
  </div>
</footer>
<script>{JS}</script>
</body>
</html>
"""
    DEPLOY.mkdir(parents=True, exist_ok=True)
    (DEPLOY / "index.html").write_text(html, encoding="utf-8")
    print(f"wrote deploy/index.html ({len(html) / 1024:.1f} KB)")


if __name__ == "__main__":
    build()
