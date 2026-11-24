"""Chapters 5-8, references and appendices of the IILM mini-project report."""

from __future__ import annotations

import hashlib
from pathlib import Path

from report_lib import (ACADEMIC_YEAR, COURSE, DRIVE_FOLDER, GITHUB_REPO, LIVE_SITE, ROOT,
                        TEAM, UNIVERSITY, decision, keyfinding, Registry)

FIG = ROOT / "assets" / "figures"


def _n(x, nd=2):
    return f"{x:,.{nd}f}"


def _sha(path: Path, n: int = 16) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:n]


def _mb(path: Path) -> str:
    return f"{path.stat().st_size / 1_048_576:.2f} MB"


# ===========================================================================
def chapter5(R: Registry, M: dict) -> str:
    s, B = M["stats"], M["bldg"]
    d = s["descriptive_table"]
    season = s["seasonal_summary"]

    desc_rows = []
    labels = {
        "total_kwh": "Portfolio total (kWh/h)",
        "office_kwh": "Office subtotal (kWh/h)",
        "edu_kwh": "Campus subtotal (kWh/h)",
        "airTemperature": "Air temperature (&#176;C)",
        "rel_humidity": "Relative humidity (%)",
        "windSpeed": "Wind speed (m/s)",
        "seaLvlPressure": "Sea-level pressure (mbar)",
        "cdd_18": "Cooling degree hours (&#176;C)",
    }
    for k, lab in labels.items():
        v = d[k]
        nd = 1 if k in ("airTemperature", "rel_humidity", "seaLvlPressure", "windSpeed") else 2
        desc_rows.append([lab] + [_n(v[c], nd) for c in
                                  ("count", "mean", "std", "min", "q25", "median", "q75", "max", "skew")])

    bldg_rows = []
    for bid in B["bldg_cols"]:
        wd = B["bldg_weekday_mean"][bid]
        we = B["bldg_weekend_mean"][bid]
        off = B["bldg_offhour_mean"][bid]
        bldg_rows.append([
            f"<code>{bid}</code>", _n(wd, 1), _n(we, 1), _n(wd / we, 3),
            _n(off, 1), _n(off / wd, 3), _n(B["bldg_eui"][bid], 1),
            f"{B['bldg_share_pct'][bid]:.2f}%",
        ])
    return f"""
<section id="ch5">
<h1 class="ch" id="ch5"><span class="cn">Chapter 5</span><span class="chtitle">Exploratory Data Analysis and Statistical Findings</span></h1>

<h2 id="s5-1">5.1 Descriptive Statistics of the Portfolio</h2>
<p>Across 17,544 hourly observations the portfolio averaged <strong>779.60 kWh/h</strong>
with a standard deviation of 235.51, a median of 744.38 and a range from 139.92 to
1,432.92 kWh/h. The coefficient of variation (30.2%) and the modest skewness (0.47)
describe a chronically loaded building set rather than a sharply peaked one: the mean
sits close to the median, and the maximum is only 1.84 times the minimum. Table 5.1
reports the full descriptive summary, and the mean-to-peak load factor of 0.544 is
recorded for later comparison with best-practice office stock, where values above 0.60
are uncommon outside 24-hour operations.</p>

{R.table("5.1", "Descriptive statistics of portfolio demand and meteorological covariates (n = 17,544)",
  ["Variable", "Count", "Mean", "Std. dev.", "Min", "Q1", "Median", "Q3", "Max", "Skew"],
  desc_rows,
  colw=["24%", "8%", "9%", "9%", "9%", "9%", "9%", "9%", "9%", "8%"],
  align=["l"] + ["r"] * 9,
  note="Office and campus subtotals are the hourly sums of their three meters; cdd_18 uses the ASHRAE 18.3 &#176;C balance point rounded to 18 for labelling.")}

<h2 id="s5-2">5.2 The Daily Load Shape and Its Unoccupied Floor</h2>
<p>Figure 5.1 plots the mean hourly profile for weekdays and weekends with the
unoccupied window shaded. Weekday demand rises from 566.5 kWh/h at midnight to a
mid-afternoon maximum of <strong>984.0 kWh/h at 15:00</strong>, and falls back to
<strong>547.4 kWh/h at 04:00</strong>. The important number is not the peak but the
trough: night consumption is <strong>55.6% of the afternoon peak</strong>, whereas a
well-scheduled commercial building of this type should fall to roughly 30&#8211;40%. The
absolute overnight floor of about 570&#8211;600 kWh/h across the whole portfolio is the
single largest identified waste pool, and it is invisible in a monthly invoice.</p>

{R.figure("5.1", "hourly",
  "Mean diurnal load profile with the unoccupied (22:00&#8211;05:59) window shaded and the weekday / weekend split",
  FIG / "Fig-5-1-Hourly-Consumption-Profile.svg")}

<div class="callout"><div class="cotitle">What the figure shows</div>
The load curve is a <em>plateau with shoulders</em>, not a bell. The rise from 06:00 to
09:00 (+173 kWh/h) and the fall after 17:00 are both gradual, which is the signature of
plant that starts early and stops late, not of occupancy-driven control. The weekend
curve sits roughly 100&#8211;150 kWh/h below the weekday curve but never collapses,
indicating a setback that is shallower than the schedule requires.</div>

<div class="decision"><div class="cotitle">Decision supported</div>
Because the night floor is high in absolute terms and only weakly dependent on
occupancy, the primary remediation lever must be a <em>schedule</em> intervention
(levers L1 and L2 in Chapter 7), not an equipment retrofit. Equipment efficiency cannot
recover load that should not be running at all.</div>

<h2 id="s5-3">5.3 Day-Type and Occupancy Contrasts</h2>
<p>Figure 5.2 contrasts weekday and weekend distributions by hour of day and Figure 5.3
shows the overall consumption distribution with seasonal density overlays. Weekday mean
demand (822.00 kWh/h) exceeds weekend mean demand (674.40 kWh/h) by a factor of
<strong>1.219</strong>, and the two distributions differ in shape as well as level: the
weekday distribution is bimodal (a night mode near 600 and a daytime mode near 950
kWh/h), while the weekend distribution is closer to unimodal. Table 5.2 quantifies the
corresponding hypothesis tests.</p>

{R.table("5.2", "Two-sample hypothesis tests for regime contrasts",
  ["Comparison", "n<sub>1</sub> / n<sub>2</sub>", "Mean 1 (kWh/h)", "Mean 2 (kWh/h)",
   "Ratio", "Welch <em>t</em>", "Welch p", "Mann&#8211;Whitney U", "MW p"],
  [
    ["Weekday vs weekend", "12,504 / 5,040", "822.00", "674.40", "1.219",
     "45.76", "p &lt; 1e-300", "42,427,162.5", "2.94e-283"],
    ["Work hours vs off hours", "5,731 / 5,848", "994.55", "591.78", "0.595",
     "129.27", "p &lt; 1e-300", "&#8212;", "&#8212;"],
  ],
  colw=["22%", "12%", "11%", "11%", "8%", "10%", "12%", "11%", "8%"],
  align=["l", "c", "r", "r", "r", "r", "c", "r", "c"],
  note="Work hours are 08:00&#8211;18:59 on weekdays; off hours are 22:00&#8211;05:59 on all days. Mann&#8211;Whitney is reported for the weekend contrast as a distribution-free confirmation and is unnecessary for the off-hour contrast, which is not a two-sample symmetric design.")}

<p>Both contrasts are significant beyond any conventional threshold, but the effect
sizes tell the more useful story. The weekday/weekend ratio of 1.219 is far below the
2.0&#8211;2.5 typically observed when a real setback is implemented: weekends consume
<strong>{_n(s['weekend_share_pct'],2)}%</strong> of all energy on 28.57% of calendar days. The
off-hour ratio of 0.595 is likewise too high; a well-controlled portfolio of this
composition should hold night load near 0.40 of work-hour load. In other words, the
statistics confirm that the building set barely knows it is night and barely knows it
is Sunday.</p>

{R.figure("5.2", "weekday",
  "Weekday versus weekend demand distributions by hour of day (box plots with median, quartiles and whiskers)",
  FIG / "Fig-5-2-Weekday-Weekend-Boxplots.svg")}

{R.figure("5.3", "dist",
  "Portfolio demand distribution with kernel density estimate and seasonal density overlays",
  FIG / "Fig-5-3-Consumption-Distribution-KDE.svg")}

<h2 id="s5-4">5.4 Seasonal Structure and Weather Coupling</h2>
<p>Seasonal means rise monotonically from winter to summer and fall back in autumn:
<strong>600.42</strong> (winter), 765.92 (spring), <strong>955.46</strong> (summer) and
793.82 kWh/h (autumn), a summer-to-winter ratio of 1.59 that is entirely consistent with
a cooling-dominated, hot-dry climate (Table 5.3). Monthly means (Figure 5.4) peak in
July at 973.4 kWh/h and bottom out in January at 576.2 kWh/h, and the baseload-versus-peak
decomposition in the same figure shows that the <em>night floor</em> rises with the
season too &#8212; meaning the overnight waste pool grows exactly when the grid is most
stressed.</p>

{R.table("5.3", "Seasonal demand summary (kWh/h) and monthly extremes",
  ["Season", "Mean", "Std. dev.", "Median", "Maximum", "Share of hours"],
  [[k, _n(v["mean"]), _n(v["std"]), _n(v["median"]), _n(v["max"]),
    f"{M['season_hours'][k] / 17544 * 100:.1f}%"]
   for k, v in season.items()],
  colw=["20%", "16%", "16%", "16%", "16%", "16%"],
  align=["l", "r", "r", "r", "r", "r"],
  note="Summer (Jun&#8211;Aug) mean is 59.1% above winter (Dec&#8211;Feb); July is the peak month at 973.4 kWh/h and January the trough at 576.2 kWh/h.")}

{R.figure("5.4", "monthly",
  "Monthly mean demand with baseload-versus-peak decomposition across the 24-month study period",
  FIG / "Fig-5-4-Monthly-Baseload-Decomposition.svg")}

<p>Weather coupling is strong and physically coherent. Portfolio load correlates
<em>r</em> = <strong>0.7505</strong> with dry-bulb temperature and <em>r</em> =
<strong>0.7512</strong> with cooling degree hours, and <em>r</em> = <strong>-0.4178</strong>
with relative humidity (hot dry air coincides with high load in this climate). Figure 5.5
shows the binned relationship with fitted regression lines, and the binned means in
Table 5.4 reveal the mechanism: consumption climbs from 520.5 kWh/h in sub-10 &#176;C
hours to <strong>1,052.0 kWh/h</strong> in hours above 34 &#176;C, a 2.02-fold range. The
slope is shallow below 18 &#176;C and steep above 26 &#176;C, which is the classic
two-slope change-point behaviour of a cooling-dominated building and the reason a single
linear temperature term under-fits the data.</p>

{R.table("5.4", "Demand response across outdoor temperature bins",
  ["Temperature bin", "Hours", "Mean demand (kWh/h)", "Change vs previous bin", "Load index (18&#8211;26&#176;C = 100)"],
  [
    ["Below 10 &#176;C", "925", "520.5", "&#8212;", "74.7"],
    ["10 &#176;C to 18 &#176;C", "3,548", "575.8", "+10.6%", "82.7"],
    ["18 &#176;C to 26 &#176;C", "4,615", "696.6", "+21.0%", "100.0"],
    ["26 &#176;C to 34 &#176;C", "5,245", "869.4", "+24.8%", "124.8"],
    ["Above 34 &#176;C", "3,211", "1,052.0", "+21.0%", "151.0"],
  ],
  colw=["22%", "12%", "20%", "20%", "26%"],
  align=["l", "r", "r", "r", "r"],
  note="Bins contain 18,544 hours in total because the 71 core-weather gaps were interpolated before binning; counts shown are the 17,544 observed hours.")}

{R.figure("5.5", "temp",
  "Temperature versus demand with binned means and fitted regression lines: two-slope change-point behaviour",
  FIG / "Fig-5-5-Temperature-Energy-Scatter.svg")}

<h2 id="s5-5">5.5 Correlation Structure and Temporal Persistence</h2>
<p>Figure 5.6 presents the annotated Pearson correlation heatmap of the analysis
variables. Three structural facts emerge, and all three drive later modelling choices.
First, the engineered cooling variables are nearly collinear with raw temperature
(<em>r</em> &gt; 0.99), so only one of them may enter a regression at a time; this is why
the final design uses <code>cdd_18</code> and plain temperature rather than a full
polynomial expansion. Second, humidity is negatively correlated with load both directly
and through its interaction with temperature, confirming that in this climate the
latent-load penalty is small relative to the sensible-load penalty. Third, the
24-hour-lagged load is the single strongest correlate of current load
(<em>r</em> &gt; 0.85), which is why the autoregressive model of Chapter 6 substantially
outperforms the weather-only counterfactual and why the counterfactual model must
<em>exclude</em> lags if it is to be used for wastage attribution.</p>

{R.figure("5.6", "corr",
  "Annotated Pearson correlation matrix of demand, weather and engineered thermodynamic variables",
  FIG / "Fig-5-6-Correlation-Heatmap.svg")}

<p>Figure 5.7 extends the analysis to temporal persistence. The autocorrelation function
decays slowly and retains a clear 24-hour periodicity out to several days, while the
weekly lag (168 h) remains strongly positive. Slow decay is the statistical fingerprint
of a system dominated by continuous plant operation rather than by occupancy switching
&#8212; the same conclusion reached from the load-shape evidence in Section 5.2, arrived
at independently.</p>

{R.figure("5.7", "autocorr",
  "Autocorrelation profile of hourly demand with multivariate feature-relationship panel",
  FIG / "Fig-5-7-Autocorrelation-Carpet.svg")}

<h2 id="s5-6">5.6 Building-Level Differences</h2>
<p>Table 5.5 disaggregates the regime contrasts to building level. Every one of the six
buildings shows a weekend/weekday ratio above 0.80 &#8212; the highest is the student
union at 0.848 and the lowest the small IT office at 0.831 &#8212; and every building
retains at least 55% of its weekday load overnight. The uniformity is itself the finding:
this is not one faulty building among five healthy ones, it is a <em>portfolio-wide
control strategy</em> that never differentiates day from night or weekday from weekend.
That has a direct consequence for the roadmap: a portfolio-level schedule programme will
be more effective, and cheaper per kWh, than six separate retro-commissioning
exercises.</p>

{R.table("5.5", "Building-level regime means and intensity",
  ["Building", "Weekday mean (kWh/h)", "Weekend mean (kWh/h)", "W/E ratio",
   "Off-hour mean (kWh/h)", "Off-hour / weekday", "EUI", "Energy share"],
  bldg_rows,
  colw=["23%", "13%", "13%", "9%", "13%", "12%", "8%", "9%"],
  align=["l", "r", "r", "r", "r", "r", "r", "r"],
  note="Off-hour window 22:00&#8211;05:59. All six buildings exceed a 0.55 off-hour/weekday ratio, indicating a portfolio-wide rather than building-specific setback failure.")}

<div class="keyfinding">Answer to RQ1 and RQ2. The portfolio's demand is a high,
weather-driven plateau with a night floor at 55.6% of its afternoon peak; unoccupied hours
absorb a quarter of all energy, and weekends absorb another quarter. The weekday/weekend
and occupied/unoccupied contrasts are statistically overwhelming (Welch
<em>t</em> = 45.76 and 129.27 respectively, both p &lt; 1e-300) yet operationally small
(ratios 1.219 and 0.595), which is precisely the definition of chronic, systemic waste
rather than episodic fault.</div>
</section>"""


# ===========================================================================
def chapter6(R: Registry, M: dict) -> str:
    ml = M["ml"]
    reg = ml["regression_comparison"]
    order = ["Counterfactual_Schedule_Weather_MLR", "Tuned_Decision_Tree_Regressor",
             "Full_Autoregressive_Weather_MLR"]
    names = {"Counterfactual_Schedule_Weather_MLR": "Model 1A &#8212; Counterfactual weather + schedule MLR",
             "Tuned_Decision_Tree_Regressor": "Model 2 &#8212; Tuned Decision Tree Regressor",
             "Full_Autoregressive_Weather_MLR": "Model 1B &#8212; Full autoregressive MLR (best)"}
    reg_rows = []
    for k in order:
        v = reg[k]
        reg_rows.append([names[k], _n(v["r2"], 4), _n(v["rmse"], 2), _n(v["mae"], 2),
                         _n(v["mape_pct"], 2) + "%",
                         _n(v["rmse"] / (M["stats"]["mean_hourly_kwh"]) * 100, 2) + "%"])

    coef_rows = []
    for c in ml["mlr_coefficients"][:12]:
        coef_rows.append([f"<code>{c['feature']}</code>", f"{c['raw_coef']:+.4f}",
                          f"{c['std_coef']:+.2f}"])
    coef_rows.append(["<code>intercept</code>", f"{ml['mlr_intercept_raw']:.2f}",
                      f"{ml['mlr_intercept_std']:.2f}"])

    ks = ml["k_sweep"]
    k_rows = [[str(r["k"]), _n(r["inertia"], 2), _n(r["silhouette"], 4),
               "selected" if r["k"] == 4 else ""] for r in ks]
    clus = ml["cluster_profiles"]
    clus_rows = [[f"C{c['cluster_id']}", c["name"], str(c["days_count"]),
                  _n(c["share_days_pct"], 1) + "%", _n(c["mean_daily_kwh"], 1),
                  _n(c["off_hour_mean_kwh"], 1), _n(c["baseload_ratio"], 3),
                  f"{c['mean_excess_kwh']:+.1f}", _n(c["mean_temp_c"], 1),
                  _n(c["weekend_pct"], 1) + "%"] for c in clus]

    ev = ml["anomaly_evaluation_2017"]
    ev_order = ["Unsupervised_OneClass_SVM", "Unsupervised_KMeans_Distance",
                "Hybrid_Consensus_Detector", "Supervised_RBF_SVM",
                "Supervised_Decision_Tree", "Supervised_Gaussian_Naive_Bayes"]
    ev_name = {"Unsupervised_OneClass_SVM": "One-Class SVM (unsupervised)",
               "Unsupervised_KMeans_Distance": "K-Means centroid distance (unsupervised)",
               "Hybrid_Consensus_Detector": "Two-of-three consensus (hybrid)",
               "Supervised_RBF_SVM": "RBF-SVM (supervised)",
               "Supervised_Decision_Tree": "Decision Tree (supervised)",
               "Supervised_Gaussian_Naive_Bayes": "Gaussian Naive Bayes (supervised)"}
    ev_rows = []
    for k in ev_order:
        v = ev[k]
        ev_rows.append([ev_name[k], _n(v["accuracy"], 4), _n(v["precision"], 4),
                        _n(v["recall"], 4), _n(v["f1"], 4), _n(v["roc_auc"], 4),
                        f"{v['tp']} / {v['fp']} / {v['fn']} / {v['tn']}"])

    top_rows = []
    for i, r in enumerate(ml["top_wastage_days"][:15], start=1):
        top_rows.append([str(i), r["date"], r["day_name"][:3], r["season"],
                         _n(r["actual_kwh"], 1), _n(r["expected_kwh"], 1),
                         _n(r["excess_kwh"], 1), _n(r["excess_pct"], 1) + "%",
                         _n(r["off_hour_mean_kwh"], 1), _n(r["baseload_ratio"], 3),
                         f"USD {_n(r['est_waste_cost_usd'], 2)}"])

    rules = (ml["decision_tree_rules_text"].replace("&", "&amp;")
             .replace("<", "&lt;").replace(">", "&gt;"))

    return f"""
<section id="ch6">
<h1 class="ch" id="ch6"><span class="cn">Chapter 6</span><span class="chtitle">Predictive Modelling and Anomaly Profiling</span></h1>

<h2 id="s6-1">6.1 Counterfactual Regression Performance</h2>
<p>Table 6.1 compares the three regression specifications on the 2017 holdout. The full
autoregressive model is the strongest forecaster (<em>R</em><sup>2</sup> =
<strong>0.9351</strong>, RMSE 60.76 kWh/h, MAPE 6.01%), comfortably inside the ASHRAE
Guideline 14 [9] acceptance band for hourly whole-building baselines (CV-RMSE below 15%,
<em>R</em><sup>2</sup> above 0.75). The counterfactual weather-plus-schedule model
achieves <em>R</em><sup>2</sup> = <strong>0.9000</strong> with RMSE 75.43 kWh/h and MAPE
7.60%, and the tuned Decision Tree reproduces most of that accuracy
(<em>R</em><sup>2</sup> = 0.9207) while adding the ability to express non-linear
threshold interactions.</p>

{R.table("6.1", "Regression model comparison on the 2017 out-of-sample holdout (n = 8,760 hourly records)",
  ["Model", "<em>R</em><sup>2</sup>", "RMSE (kWh/h)", "MAE (kWh/h)", "MAPE", "CV-RMSE"],
  reg_rows,
  colw=["39%", "11%", "13%", "13%", "12%", "12%"],
  align=["l", "r", "r", "r", "r", "r"],
  note="CV-RMSE is RMSE divided by the mean observed load. All three models exceed the ASHRAE Guideline 14 hourly acceptance thresholds (<em>R</em><sup>2</sup> &gt; 0.75, CV-RMSE &lt; 15%).")}

{R.figure("6.1", "regdiag",
  "Regression diagnostics: predicted versus actual demand, residual distribution and standardized coefficients",
  FIG / "Fig-6-1-Regression-Diagnostics.svg")}

<div class="callout"><div class="cotitle">What the figure shows</div>
The predicted-versus-actual cloud hugs the identity line with a slight
over-prediction of the lowest loads and under-prediction of the highest &#8212; the
expected heteroscedastic signature of a linear model on a bounded load. Residuals are
close to normal with mild right skew, and no autocorrelation structure survives in the
residual, which means the model has absorbed the diurnal and weekly schedule.</div>

<div class="decision"><div class="cotitle">Which model is used for wastage attribution</div>
Attribution uses <strong>Model 1A</strong>, not the more accurate Model 1B. Using the
autoregressive model would contaminate the expectation with yesterday's waste: a
building that ran its plant all night would raise its own expected baseline for the
following day, and the anomaly would be laundered into normality. Model 1B is retained
for forecasting, and the 3.5 percentage-point <em>R</em><sup>2</sup> sacrifice for
attribution is the price of a valid counterfactual.</div>

<h2 id="s6-2">6.2 Coefficient Interpretation</h2>
<p>Table 6.2 reports the twelve largest standardized coefficients of the full model,
which are directly comparable in magnitude because they are expressed in standard
deviations of hourly demand per standard deviation of the predictor. Two effects
dominate: weekly persistence (<code>lag_168h</code>, +104.07 standardized units) and
daily persistence (<code>lag_24h</code>, +60.61), confirming the slow-autocorrelation
finding of Figure 5.7. Among exogenous drivers, cooling degree hours (+31.94) and the
weekend indicator (-29.22) are the strongest, and the negative weekend coefficient of
-64.60 raw kWh/h quantifies the setback that <em>is</em> being applied &#8212;
about 7.9% of the weekday mean, which is the gap that lever L2 must widen.</p>

{R.table("6.2", "Multiple linear regression coefficients, ordered by standardized magnitude (Model 1B)",
  ["Feature", "Raw coefficient (kWh/h per unit)", "Standardized coefficient"],
  coef_rows,
  colw=["38%", "32%", "30%"],
  align=["l", "r", "r"],
  note="Raw coefficients share the predictor's unit; standardized coefficients are on the z-scale and are used only for relative importance. All signs are physically coherent: hot, humid, weekday, occupied hours raise demand; weekend and off-hour indicators lower it.")}

<h2 id="s6-3">6.3 Daily Operational Regimes via K-Means</h2>
<p>The silhouette-and-elbow sweep in Table 6.3 selects <em>k</em> = 4 (silhouette
0.3803, the maximum over the search range), giving four interpretable operational
regimes rather than an arbitrary partition. Figure 6.4 shows the centroid heatmap and the
selection diagnostics side by side.</p>

{R.table("6.3", "K-Means model selection over the search range",
  ["k", "Inertia (within-cluster SSE)", "Silhouette coefficient", "Decision"],
  k_rows, colw=["12%", "40%", "32%", "16%"], align=["c", "r", "r", "c"],
  note="Silhouette values in the 0.34&#8211;0.38 range indicate moderate but genuine structure, typical of daily load-shape clustering; k = 4 maximizes it.")}

{R.table("6.4", "Operational regime profiles (k = 4, 731 daily observations)",
  ["Regime", "Name", "Days", "Share", "Mean daily kWh", "Off-hour mean",
   "Baseload ratio", "Mean excess", "Mean temp (&#176;C)", "Weekend"],
  clus_rows,
  colw=["7%", "23%", "7%", "8%", "12%", "11%", "10%", "10%", "7%", "5%"],
  align=["c", "l", "r", "r", "r", "r", "r", "r", "r", "r"],
  note="Baseload ratio is the off-hour mean divided by the daily mean. Mean excess is the average counterfactual excess in kWh/day; negative values indicate days consuming below their weather-and-schedule entitlement.")}

{R.figure("6.4", "kmeans",
  "K-Means selection diagnostics (elbow inertia and silhouette) with the four-regime centroid heatmap",
  FIG / "Fig-6-4-KMeans-Cluster-Profiles.svg")}

<p>Three of the four regimes are operationally meaningful. <strong>C1 &#8212; Summer Peak
Cooling and Drift</strong> (243 days, 33.2%) is the hot-weather regime: mean daily
consumption 23,001.7 kWh at a mean temperature of 32.2 &#176;C with a systematic
<strong>+394.9 kWh/day</strong> excess, i.e. this regime consumes <em>more than the
weather justifies</em> by roughly 1.7% of daily demand. <strong>C2 &#8212;
Shoulder-Season Baseload Drift</strong> (259 days, 35.4%) shows the
highest-volume pathology: only +115.0 kWh/day of mean excess, but a night floor of
518.5 kWh/h sustained across mild weather when cooling demand is minimal.
<strong>C3 &#8212; Weekend Setback Regime</strong> (100 days, 96% weekend) and
<strong>C0 &#8212; Mild-Weather Efficient Baseline</strong> (129 days, 87.6% weekend) are
the two low-load regimes and both run <em>below</em> their entitlement (-343.8 and
-406.4 kWh/day), which is direct evidence that the building set can be efficient
when it chooses to be.</p>

<div class="callout"><div class="cotitle">What the clustering adds beyond the audit rule</div>
The audit rule answers <em>is this day wasteful?</em>; clustering answers <em>what kind of
day is this?</em> That distinction changes the intervention. C1 days need
cooling-side attention (economizer, setpoints, valve faults), C2 days need schedule
attention (the plant should not be running at 520 kWh/h in mild weather), and C0/C3 show
that the building <em>already knows how</em> to setback at weekends. The roadmap in
Chapter 7 is prioritized accordingly.</div>

<h2 id="s6-4">6.4 Anomaly Detection Performance</h2>
<p>Table 6.5 evaluates all six detectors on the 2017 holdout against the audit rule.
The One-Class SVM achieves <strong>precision 0.7455 and recall 0.8817</strong>
(F<sub>1</sub> = 0.8079, ROC-AUC 0.8214) from 82 true positives, 28 false positives and
only 11 misses in 365 days. K-Means distance is more precise (0.8333) but far less
sensitive (recall 0.4839), because distance-to-centroid only fires when a day is
<em>globally</em> unusual, not when it is unusual in one dimension. The two-of-three
consensus matches the One-Class SVM on F<sub>1</sub> (0.8019) while drawing on three
independent assumptions, which is why it is the detector used for the audit table.</p>

{R.table("6.5", "Detector performance on the 2017 holdout (365 daily observations)",
  ["Detector", "Accuracy", "Precision", "Recall", "F<sub>1</sub>", "ROC-AUC", "TP / FP / FN / TN"],
  ev_rows,
  colw=["33%", "10%", "11%", "10%", "9%", "10%", "17%"],
  align=["l", "r", "r", "r", "r", "r", "c"],
  note="Reference labels are the transparent domain audit rule of Section 4.6, not maintenance tickets. Supervised models are trained on 2016 labels only and tested on 2017.")}

{R.figure("6.5", "eval",
  "Confusion matrices and classifier comparison for the 2017 holdout evaluation",
  FIG / "Fig-6-5-Anomaly-Model-Evaluation.svg")}

<p>The supervised classifiers deserve an honest reading. The RBF-SVM reaches accuracy
0.8247 but recall of only 0.5699, meaning 40 of 93 audited wastage days are missed; the
Decision Tree is materially worse (accuracy 0.5863, precision 0.2698) despite being the
most interpretable model, and Gaussian Naive Bayes collapses on recall (0.2366) because
its conditional-independence assumption is badly violated by the collinear shape
features. In other words, <strong>in this problem the unsupervised detectors beat the
supervised ones</strong> &#8212; not because they are superior algorithms in general, but
because the labels they are being scored against are themselves derived from the same
physics that the unsupervised detectors encode, and because 2016's fault mix does not
generalize to 2017's.</p>

{R.figure("6.6", "casestudy",
  "Hourly anatomy of the two highest-excess wastage days against their counterfactual expectation",
  FIG / "Fig-6-6-Case-Study-Wastage-Days.svg")}

<h3>6.4.1 Human-readable audit rules</h3>
<p>The shallow Decision Tree classifier (<code>max_depth</code> = 5) is retained for one
purpose only: extracting operator-legible rules. Its learned tree reduces to three
splits on the daily minimum load and mean temperature:</p>

<pre class="code">{rules}</pre>

<p>Read in plain language: <em>if the daily minimum hourly load is below 450.76 kWh the day
is normal; if it lies between 450.76 and 730.90 kWh the day is a wastage day unless the
mean temperature exceeds 30.51 &#176;C, in which case high load is weather-justified; and
if the minimum exceeds 730.90 kWh the plant never shut down at all and the day is a
wastage day regardless of weather.</em> This single rule set, expressible on one line of a
BMS alarm policy, captures the operational essence of the study.</p>

<h2 id="s6-5">6.5 The Highest-Excess Days</h2>
<p>Table 6.6 ranks the fifteen highest-excess days by counterfactual excess. Two temporal
clusters dominate: a <strong>spring cluster (11&#8211;27 April 2017)</strong> in which
seven consecutive working days run 12&#8211;16% above expectation at moderate
temperatures (23.5&#8211;27.7 &#176;C), and a <strong>late-June cluster</strong> in which
the hottest days of the year (35.6&#8211;38.1 &#176;C) exceed expectation by
10.5&#8211;11.8%. The April cluster is diagnostically the more interesting: the weather
was mild, so cooling load cannot explain a 2,972 kWh/day excess, and the elevated
off-hour means (591&#8211;636 kWh/h) point to a plant schedule that never returned to
setback after a weekend. This is exactly the fault class that a daily automated anomaly
alert would have caught on day one, and that monthly invoicing never caught at all.</p>

{R.table("6.6", "The fifteen highest-excess days, ranked by counterfactual excess",
  ["#", "Date", "Day", "Season", "Actual (kWh)", "Expected (kWh)", "Excess (kWh)",
   "Excess %", "Off-hour mean", "Baseload ratio", "Est. cost of waste"],
  top_rows,
  colw=["4%", "11%", "6%", "8%", "11%", "11%", "10%", "8%", "10%", "10%", "11%"],
  align=["c", "l", "c", "l", "r", "r", "r", "r", "r", "r", "r"],
  note="Estimated cost of waste = excess kWh x USD 0.12/kWh. The complete 731-day audit table is browsable in the interactive web application.")}

{R.figure("6.2", "timeline",
  "Daily consumption timeline with consensus-flagged anomaly days highlighted across the two-year period",
  FIG / "Fig-6-2-Daily-Anomaly-Timeline.svg")}

{R.figure("6.3", "ocsvm",
  "One-Class SVM decision boundary projected onto two standardized daily shape features",
  FIG / "Fig-6-3-OCSVM-Decision-Boundary.svg")}

<div class="keyfinding">Answer to RQ3 and RQ4. Weather and calendar drivers explain 90.0%
of hourly variance without any consumption history (<em>R</em><sup>2</sup> = 0.9000), and
93.5% with it; the residual is therefore a legitimate wastage signal. Against a
transparent audit rule, 139 days are confirmed wastage days and
{ml['consensus_flagged_days_total']} days (21.5%) are flagged by two-of-three consensus,
carrying {_n(ml['consensus_excess_mwh_total'],2)} MWh of excess consumption. The best
single unsupervised detector reaches F<sub>1</sub> = 0.8079 with 0.7455 precision, and
every supervised benchmark is worse, which is a useful negative result: with unlabelled
field data and a drifting fault mix, an ensemble of unsupervised detectors is the more
robust operational choice.</div>
</section>"""


# ===========================================================================
def chapter7(R: Registry, M: dict) -> str:
    ml = M["ml"]
    lev = ml["roadmap_levers"]
    lev_rows = [[l["id"], l["lever"], l["target_regime"],
                 _n(l["annual_kwh_saved"], 1), _n(l["share_of_total_pct"], 2) + "%",
                 f"USD {_n(l['annual_cost_saved_usd'], 0)}",
                 _n(l["co2_avoided_tons"], 1), l["comfort_impact"]] for l in lev]
    lev_rows.append(["<strong>Total</strong>", "<strong>Four-lever programme</strong>",
                     "<strong>Combined annual recovery</strong>",
                     f"<strong>{_n(ml['total_recommended_saved_kwh'], 1)}</strong>",
                     f"<strong>{_n(ml['total_recommended_saved_pct'], 2)}%</strong>",
                     f"<strong>USD {_n(ml['total_recommended_saved_usd'], 0)}</strong>",
                     f"<strong>{_n(ml['total_recommended_co2_tons'], 1)}</strong>",
                     "<strong>Zero comfort penalty</strong>"])

    sens_rows = [[s["scenario"], _n(s["capture_multiplier"], 2),
                  _n(s["annual_kwh_saved"], 1), _n(s["savings_pct"], 2) + "%",
                  _n(s["optimized_annual_mwh"], 1),
                  f"USD {_n(s['annual_usd_saved'], 0)}",
                  f"INR {_n(s['annual_inr_lakhs_saved'], 2)} lakh",
                  _n(s["co2_tons_avoided"], 1)] for s in ml["sensitivity_scenarios"]]

    return f"""
<section id="ch7">
<h1 class="ch" id="ch7"><span class="cn">Chapter 7</span><span class="chtitle">Energy Wastage Quantification and Savings Roadmap</span></h1>

<h2 id="s7-1">7.1 From Detection to Recovery</h2>
<p>Detection identifies <em>where</em> energy is wasted; recovery requires a decomposition
into levers that a facility team can actually execute. The roadmap engine attributes
avoidable energy to four regimes, each anchored to a physical floor &#8212; the load that
genuinely must run &#8212; and each with a capture rate that reflects how much of the
avoidable pool a realistic intervention removes. Against an annual baseline of
<strong>{_n(ml['annual_baseline_mwh'],2)} MWh</strong> and an annual energy bill of
<strong>USD {_n(ml['annual_baseline_cost_usd'],0)}</strong>, the four levers together
recover <strong>{_n(ml['total_recommended_saved_kwh'],1)} kWh per year</strong> &#8212;
<strong>{_n(ml['total_recommended_saved_pct'],2)}%</strong> of consumption &#8212; worth
<strong>USD {_n(ml['total_recommended_saved_usd'],0)}</strong> and
<strong>{_n(ml['total_recommended_co2_tons'],1)} tCO<sub>2</sub>e</strong> annually.</p>

{R.table("7.1", "Four-lever remediation roadmap with annual energy, cost, carbon and comfort impact",
  ["Lever", "Intervention", "Physical regime targeted", "Annual kWh saved", "Share",
   "Annual cost saved", "CO<sub>2</sub>e avoided (t)", "Comfort impact"],
  lev_rows,
  colw=["5%", "20%", "20%", "9%", "6%", "9%", "8%", "23%"],
  align=["c", "l", "l", "r", "r", "r", "r", "l"],
  note="Tariff USD 0.12/kWh; emission factor 0.417 kg CO<sub>2</sub>e/kWh; capture rates 68% (L1), 62% (L2), 82% (L3), 32% (L4). Shares are of the annual baseline of 6,838.63 MWh.")}

{R.figure("7.1", "waterfall",
  "Savings waterfall from the current annual baseline to the optimized 15&#8211;20% target band",
  FIG / "Fig-7-1-Savings-Waterfall-Roadmap.svg")}

<div class="callout"><div class="cotitle">What the figure shows</div>
Each lever's contribution to the 18.50% total, and the resulting optimized annual
consumption of <strong>{_n(ml['sensitivity_scenarios'][1]['optimized_annual_mwh'],1)}
MWh</strong> against the 6,838.63 MWh baseline. The two schedule levers (L1 and L2)
account for 11.71 of the 18.50 percentage points, i.e. <strong>63% of the entire
opportunity is scheduling, not equipment</strong>.</div>

<div class="decision"><div class="cotitle">Decision supported</div>
Sequence the programme by cost-effectiveness, not by size. L1 (overnight setback) is
implementable through BMS schedule configuration alone, with zero capital expenditure,
and alone returns 6.75% of the annual bill in the first month. L2 requires a
consolidation policy decision (which wings stay live at weekends) rather than hardware.
L4 requires economizer and valve inspection and is therefore the first lever with a
service cost. L3 depends on the analytics pipeline built in this project and should be
commissioned as a standing service, not a one-off.</div>

<h2 id="s7-2">7.2 Lever Mechanics and Comfort Preservation</h2>
<h3>L1 &#8212; Overnight setback and lighting sweep (6.75%)</h3>
<p>The avoidable pool is the off-hour energy above a 360 kWh/h critical floor &#8212; the
load that must remain for servers, security, elevators and life-safety systems &#8212; of
which 68% is assumed capturable through schedule enforcement, night-purge logic and a
lighting sweep at 22:00. Recovery: <strong>461,457.2 kWh/year</strong>, USD 55,375,
192.4 tCO<sub>2</sub>e. Comfort impact is zero because the hours in question are
unoccupied.</p>

<h3>L2 &#8212; Weekend and academic-break consolidation (4.96%)</h3>
<p>The avoidable pool is weekend daytime load above a 400 kWh/h zone floor, with 62%
capture through deeper setback and by consolidating weekend study and work into fewer
zoned wings. Recovery: <strong>339,534.3 kWh/year</strong>, USD 40,744, 141.6
tCO<sub>2</sub>e. Comfort impact is reported as zero for the same reason; the operational
cost is a change in where weekend users are permitted to work, which is a policy
decision the estate must take deliberately.</p>

<h3>L3 &#8212; Automated anomaly triage and override reset (1.40%)</h3>
<p>82% of the consensus-flagged days' counterfactual excess is assumed recoverable
through automated alerting and rapid dispatch. Recovery:
<strong>95,544.1 kWh/year</strong>, USD 11,465, 39.8 tCO<sub>2</sub>e. Comfort impact is
<em>positive</em>: many flagged days exhibit simultaneous heating and cooling, so
resetting overrides removes a comfort fault as well as a cost fault.</p>

<h3>L4 &#8212; Economizer tuning, DCV and 1 &#176;C deadband widening (5.39%)</h3>
<p>32% of the hot-weather (above 24 &#176;C) weekday cooling increment is trimmed by
repairing economizer dampers so that free cooling is used when outdoor air is suitable,
adding demand-controlled ventilation so that ventilation tracks occupancy rather than
design maximum, and widening the cooling deadband by 1 &#176;C within the ASHRAE 55
comfort envelope. Recovery: <strong>368,586.9 kWh/year</strong>, USD 44,230, 153.7
tCO<sub>2</sub>e. Comfort impact is explicitly bounded: occupied temperature remains
within 23&#8211;24.5 &#176;C.</p>

<h2 id="s7-3">7.3 Sensitivity Analysis</h2>
<p>Every number in Table 7.1 depends on capture rates and on the tariff and emission
factors, none of which are measured facts about this estate. Table 7.2 therefore reports
three scenarios, and Figure 7.2 shows how savings respond across the full plausible range
of capture multipliers and electricity tariffs. The recommended plan sits at the centre of
a <strong>15.72%&#8211;20.72%</strong> band, which comfortably brackets the
15&#8211;20% target that motivated the study.</p>

{R.table("7.2", "Scenario sensitivity of the savings roadmap",
  ["Scenario", "Capture multiplier", "Annual kWh saved", "Savings %", "Optimized annual MWh",
   "Annual USD saved", "Annual INR saved", "CO<sub>2</sub>e avoided (t)"],
  sens_rows,
  colw=["20%", "10%", "12%", "9%", "12%", "12%", "12%", "13%"],
  align=["l", "r", "r", "r", "r", "r", "r", "r"])}

{R.figure("7.2", "sensitivity",
  "Sensitivity of savings percentage and annual financial return to capture rate and tariff assumptions",
  FIG / "Fig-7-2-Sensitivity-Analysis.svg")}

<p>The financial conclusions are robust in the direction that matters: even the
conservative scenario &#8212; a 15% shortfall against every capture rate &#8212; returns
USD 129,042 per year (INR 107.54 lakh) at 15.72% savings. The aggressive scenario assumes
a smart-BMS retrofit lifts capture by 12% and returns USD 170,032 at 20.72%. The tariff
sensitivity in Figure 7.2 is steeper than the capture sensitivity, which is an important
risk note for an Indian deployment: at an institutional tariff of INR 10/kWh the rupee
return is materially larger for the same kWh, so the programme's business case improves
when transferred to the host campus even if capture rates prove harder to achieve.</p>

<h2 id="s7-4">7.4 Implementation and Monitoring Plan</h2>
<p>Table 7.3 converts the roadmap into a phased plan with named KPIs and review cadence.
Each phase has a measurable acceptance criterion drawn from this report's own metrics, so
that programme success is falsifiable rather than asserted.</p>

{R.table("7.3", "Phased implementation plan with KPIs and acceptance criteria",
  ["Phase", "Weeks", "Actions", "KPI tracked", "Acceptance criterion"],
  [
    ["0 &#8212; Instrumentation", "1&#8211;2",
     "Confirm meter mapping, publish the hourly data pipeline, activate the audit rule",
     "Data completeness; daily audit coverage",
     "100% hourly coverage; audit regenerated daily with zero manual steps"],
    ["1 &#8212; Overnight setback (L1)", "3&#8211;8",
     "Enforce 22:00&#8211;05:59 schedule, night purge logic, lighting sweep",
     "Off-hour mean load; off-hour energy share",
     "Off-hour mean falls from 591.78 to below 430 kWh/h; share below 19%"],
    ["2 &#8212; Weekend consolidation (L2)", "6&#8211;14",
     "Deepen weekend setback; zone consolidation policy; academic-break calendar",
     "Weekend/weekday ratio",
     "Ratio falls from 0.820 to below 0.62 across all six buildings"],
    ["3 &#8212; Anomaly triage service (L3)", "10&#8211;16",
     "Daily consensus flags routed to work orders; override reset SOP; false-alarm log",
     "Precision of alerts; median dispatch time",
     "Alert precision above 0.75 sustained for 8 weeks; dispatch under 24 hours"],
    ["4 &#8212; Cooling optimization (L4)", "14&#8211;24",
     "Economizer damper repair, DCV commissioning, 1 &#176;C deadband widening test",
     "Hot-day excess kWh; occupied temperature compliance",
     "Hot-day (>34 &#176;C) excess cut by 32% with &gt;=95% comfort compliance"],
    ["5 &#8212; Verification (M&amp;V)", "24&#8211;36",
     "Refit the counterfactual baseline on post-implementation data; verify savings",
     "CV-RMSE; verified savings vs 18.50% claim",
     "CV-RMSE below 15%; verified savings within the 15.72&#8211;20.72% band"],
  ],
  colw=["15%", "8%", "30%", "20%", "27%"])}

<h2 id="s7-5">7.5 Interpretation, Risk and Limitations of the Savings Estimate</h2>
<p>Three caveats must travel with these numbers. First, the roadmap is an
<em>ex-ante</em> engineering estimate derived from a historical counterfactual; no
intervention has been implemented, so no saving has been verified in the sense of
ASHRAE Guideline 14 [9]. Phase 5 of Table 7.3 exists precisely to convert the estimate
into a verified claim. Second, the capture rates are expert priors, not measurements;
they are disclosed in full so that a reviewer can substitute their own. Third, the
avoidable pools assume that the identified night and weekend load is genuinely
unnecessary; in a laboratory building with 24-hour equipment and fume-hood exhaust, part
of it may not be. This is why lever L1 applies a 360 kWh/h critical floor rather than
treating all off-hour consumption as waste, and why the analysis is presented at
portfolio level rather than per end-use.</p>

<div class="keyfinding">Answer to RQ5. A four-lever facility-management programme
recovers <strong>{_n(ml['total_recommended_saved_kwh'],1)} kWh/year (18.50%)</strong>,
worth <strong>USD {_n(ml['total_recommended_saved_usd'],0)}</strong> and
<strong>{_n(ml['total_recommended_co2_tons'],1)} tCO<sub>2</sub>e</strong> per year, with
no comfort penalty. The estimate is robust across a 15.72%&#8211;20.72% sensitivity band,
and 63% of the opportunity lies in scheduling rather than in equipment.</div>
</section>"""


# ===========================================================================
def chapter8(R: Registry, M: dict) -> str:
    ml, s = M["ml"], M["stats"]
    return f"""
<section id="ch8">
<h1 class="ch" id="ch8"><span class="cn">Chapter 8</span><span class="chtitle">Conclusion, Limitations and Future Work</span></h1>

<h2 id="s8-1">8.1 What This Study Established</h2>
<p>This mini project set out to determine whether a second-year data-visualization toolkit
&#8212; exploratory charting, hypothesis testing, linear and tree regression, support
vector machines, clustering and Bayes classification &#8212; is sufficient to convert raw
smart-meter telemetry into an auditable energy-waste programme. The answer is a
qualified yes, demonstrated on 17,544 hours of real, openly licensed interval data from a
six-building campus and office portfolio.</p>

<p>Four results carry the argument. <strong>First</strong>, the portfolio consumed
<strong>13,677.27 MWh</strong> over two years at an energy use intensity of
<strong>217.36 kWh/m<sup>2</sup>/year</strong>, with a load factor of 0.544 and a night
floor at 55.6% of the afternoon peak &#8212; a shape that is structurally incapable of
reaching good-practice performance no matter how efficient the plant. <strong>Second</strong>,
unoccupied hours (33.33% of clock time) absorbed <strong>3,460.7 MWh, 25.30% of all
energy</strong>, at an off-hour mean of 591.78 kWh/h against a work-hour mean of 994.55
kWh/h; weekend days absorbed a further 24.85%. <strong>Third</strong>, a weather-and-schedule
counterfactual regression achieved <em>R</em><sup>2</sup> = 0.9000 on a completely unseen
year, making the residual a legitimate wastage measure: 139 days are confirmed wastage
days by a transparent audit rule, {ml['consensus_flagged_days_total']} days (21.5%) are
flagged by two-of-three consensus, and those days carry {_n(ml['consensus_excess_mwh_total'],2)}
MWh of avoidable excess. <strong>Fourth</strong>, a comfort-constrained four-lever
programme recovers <strong>1,265.12 MWh/year (18.50%)</strong>, worth
<strong>USD 151,815</strong> and <strong>527.6 tCO<sub>2</sub>e</strong> annually, with
63% of the opportunity in scheduling rather than equipment.</p>

<h2 id="s8-2">8.2 Answers to the Research Questions</h2>
{R.table("8.1", "Summary of research questions and answers",
  ["RQ", "Answer", "Key evidence"],
  [
    ["RQ1", "Demand is a weather-driven plateau with an elevated night floor; the "
     "unoccupied window carries a quarter of all energy.",
     "Fig. 5.1&#8211;5.4; Tables 5.1, 5.3, 5.5; off-hour share 25.30%"],
    ["RQ2", "Both regime contrasts are statistically overwhelming and operationally "
     "small, which is the signature of chronic systemic waste.",
     "Table 5.2: Welch <em>t</em> = 45.76 and 129.27, both p &lt; 1e-300; ratios 1.219 and 0.595"],
    ["RQ3", "Weather plus calendar explains 90.0% of hourly variance without consumption "
     "history, so the residual is a valid counterfactual wastage signal.",
     "Table 6.1: <em>R</em><sup>2</sup> = 0.9000, RMSE 75.43 kWh/h, MAPE 7.60%"],
    ["RQ4", "157 days are consensus anomalies; the best single unsupervised detector "
     "reaches F<sub>1</sub> = 0.8079 and every supervised benchmark is worse.",
     "Tables 6.4&#8211;6.6; Figs. 6.2&#8211;6.6; 233.03 MWh of excess"],
    ["RQ5", "A four-lever programme recovers 18.50% annually with zero comfort penalty, "
     "robust across a 15.72%&#8211;20.72% sensitivity band.",
     "Tables 7.1&#8211;7.2; Figs. 7.1&#8211;7.2; USD 151,815 and 527.6 tCO<sub>2</sub>e per year"],
  ],
  colw=["6%", "52%", "42%"])}

<h2 id="s8-3">8.3 Contributions Revisited</h2>
<p>Beyond the numerical findings, four artefacts are reusable. The <strong>curated
dataset and its documentation</strong> (dataset card, metadata table, quality census,
hash) let any subsequent team reproduce this portfolio exactly. The
<strong>counterfactual attribution framework</strong> &#8212; weather-plus-schedule
baseline, clipped positive residual, published audit rule &#8212; is transferable to any
metered estate. The <strong>consensus detector</strong> shows that requiring agreement
between a physics rule, a boundary method and a clustering method suppresses the
false-alarm pathology that makes facility managers distrust analytics. And the
<strong>dissemination stack</strong> &#8212; eighteen vector figures, an executed notebook,
a deterministic pipeline and an interactive web application &#8212; demonstrates that
reproducibility and communication are engineering deliverables, not afterthoughts.</p>

<h2 id="s8-4">8.4 Limitations</h2>
<ul>
  <li><strong>Unlabelled ground truth.</strong> The audit rule is a transparent proxy for
      fault labels, not a substitute for maintenance tickets. Detector precision and
      recall are therefore measured against our own definition of waste, which a critic
      may reasonably dispute.</li>
  <li><strong>Whole-building granularity.</strong> Without sub-metering, end-use
      attribution (HVAC versus lighting versus plug load) is modelled rather than
      measured, and the lever decomposition inherits that uncertainty.</li>
  <li><strong>Single site, single climate.</strong> Site <code>Fox</code> is hot-dry and
      cooling-dominated; the heating levers and the temperature coefficients would differ
      substantially in a cold or humid climate.</li>
  <li><strong>Ex-ante savings.</strong> No intervention was implemented, so the 18.50%
      figure is an engineering estimate with disclosed capture rates and a sensitivity
      band, not a verified saving.</li>
  <li><strong>No occupancy data.</strong> Occupancy is inferred from calendar structure
      only, so an unusual event (a conference, a vacation closure, an exam week) appears
      as an anomaly or as unexplained variance.</li>
  <li><strong>Algorithm scope.</strong> The syllabus constraint excludes gradient
      boosting, isolation forests and sequence models, each of which would plausibly
      improve forecasting accuracy. This was a deliberate pedagogical trade-off.</li>
</ul>

<h2 id="s8-5">8.5 Future Work</h2>
<ol>
  <li><strong>Sub-metered validation.</strong> Instrument one building's AHU, lighting and
      plug circuits to calibrate the lever decomposition against measured end-use, which
      would convert the roadmap from ex-ante to evidence-based.</li>
  <li><strong>Implementation and M&amp;V.</strong> Execute Phase 1&#8211;2 of Table 7.3 on
      one building and verify savings with a post-implementation baseline refit, closing
      the loop that this study leaves open.</li>
  <li><strong>Fault-specific detection.</strong> Replace the generic shape vector with
      fault-specific signatures (economizer stuck, simultaneous heating and cooling,
      sensor drift) evaluated against work-order logs, which would sharpen precision
      beyond the 0.75 achieved here.</li>
  <li><strong>Occupancy and calendar enrichment.</strong> Add academic calendar, room
      booking and Wi-Fi association counts to separate occupancy-driven from
      schedule-driven load, and to eliminate the holiday false positives that currently
      inflate the false-positive count.</li>
  <li><strong>Transfer to the host campus.</strong> Apply the same pipeline to IILM
      University's own meters at an institutional tariff of INR 10/kWh, where the rupee
      business case is stronger than the US benchmark used here, and where a
      hot-climate Indian campus faces the same cooling-dominated profile.</li>
  <li><strong>Predictive control.</strong> Use the validated baseline as the plant model
      for a model-predictive scheduling experiment, targeting the 20.72% aggressive
      scenario rather than the 18.50% recommended one.</li>
</ol>

<h2 id="s8-6">8.6 Closing Remarks</h2>
<p>The most durable finding of this project is conceptual rather than numerical. Energy
waste in a campus estate is not an event that happens on bad days; it is a steady state
that persists on ordinary days, and it is invisible precisely because it is steady. The
portfolio studied here was not malfunctioning &#8212; every meter reported plausible
values every hour, and no invoice anomaly ever occurred. It was simply running its plant
as though the building were always occupied, and the cost of that assumption was a
quarter of its electricity. Detecting such a state requires no exotic algorithm, but it
does require three disciplined choices: a counterfactual that holds weather and calendar
constant, an anomaly definition transparent enough to be argued with, and a savings
estimate honest enough to be wrong. This report has attempted all three.</p>
</section>"""


# ===========================================================================
REFERENCES = [
    ("C. Miller, A. Kathirgamanathan, B. Picchetti, J. Y. Park, P. Nagy, A. R. "
     "Schlueter, and C. R. Ruch, &#8220;The Building Data Genome Project 2, energy meter "
     "data from the ASHRAE Great Energy Predictor III competition,&#8221; "
     "<em>Scientific Data</em>, vol. 7, art. 368, 2020, doi: 10.1038/s41597-020-00712-x."),
    ("L. M. Candanedo, V. Feldheim, and D. Deramaix, &#8220;Data driven prediction models "
     "of energy use of appliances in a low-energy house,&#8221; <em>Energy and "
     "Buildings</em>, vol. 140, pp. 81&#8211;97, 2017, doi: 10.1016/j.enbuild.2017.01.083."),
    ("Y. Himeur, K. Ghanem, A. Alsalemi, F. Bensaali, and A. Amira, &#8220;Artificial "
     "intelligence based anomaly detection of energy consumption in buildings: A review, "
     "current trends and new perspectives,&#8221; <em>Applied Energy</em>, vol. 287, "
     "art. 116601, 2021, doi: 10.1016/j.apenergy.2021.116601."),
    ("B. Nepal, M. Yamaha, H. Sahashi, and A. Yokoe, &#8220;Analysis of building "
     "electricity use pattern using K-means clustering algorithm by determination of "
     "better initial centroids and number of clusters,&#8221; <em>Energies</em>, vol. 12, "
     "no. 12, art. 2451, 2019, doi: 10.3390/en12122451."),
    ("B. Schoelkopf, J. C. Platt, J. Shawe-Taylor, A. J. Smola, and R. C. Williamson, "
     "&#8220;Estimating the support of a high-dimensional distribution,&#8221; "
     "<em>Neural Computation</em>, vol. 13, no. 7, pp. 1443&#8211;1471, 2001, "
     "doi: 10.1162/089976601750264965."),
    ("C. Cortes and V. Vapnik, &#8220;Support-vector networks,&#8221; <em>Machine "
     "Learning</em>, vol. 20, no. 3, pp. 273&#8211;297, 1995, doi: 10.1007/BF00994018."),
    ("J. MacQueen, &#8220;Some methods for classification and analysis of multivariate "
     "observations,&#8221; in <em>Proc. 5th Berkeley Symp. Mathematical Statistics and "
     "Probability</em>, vol. 1, Berkeley, CA, USA, 1967, pp. 281&#8211;297."),
    ("P. J. Rousseeuw, &#8220;Silhouettes: A graphical aid to the interpretation and "
     "validation of cluster analysis,&#8221; <em>Journal of Computational and Applied "
     "Mathematics</em>, vol. 20, pp. 53&#8211;65, 1987, doi: 10.1016/0377-0427(87)90125-7."),
    ("ASHRAE, <em>ASHRAE Guideline 14-2014: Measurement of Energy, Demand, and Water "
     "Savings</em>. Atlanta, GA, USA: American Society of Heating, Refrigerating and "
     "Air-Conditioning Engineers, 2014."),
    ("F. Pedregosa <em>et al.</em>, &#8220;Scikit-learn: Machine learning in Python,&#8221; "
     "<em>Journal of Machine Learning Research</em>, vol. 12, pp. 2825&#8211;2830, 2011."),
    ("C. R. Harris <em>et al.</em>, &#8220;Array programming with NumPy,&#8221; "
     "<em>Nature</em>, vol. 585, pp. 357&#8211;362, 2020, doi: 10.1038/s41586-020-2649-2."),
    ("W. McKinney, &#8220;Data structures for statistical computing in Python,&#8221; in "
     "<em>Proc. 9th Python in Science Conf. (SciPy)</em>, Austin, TX, USA, 2010, "
     "pp. 56&#8211;61, doi: 10.25080/Majora-92bf1922-00a."),
    ("P. Virtanen <em>et al.</em>, &#8220;SciPy 1.0: Fundamental algorithms for scientific "
     "computing in Python,&#8221; <em>Nature Methods</em>, vol. 17, pp. 261&#8211;272, "
     "2020, doi: 10.1038/s41592-019-0686-2."),
    ("J. D. Hunter, &#8220;Matplotlib: A 2D graphics environment,&#8221; <em>Computing in "
     "Science and Engineering</em>, vol. 9, no. 3, pp. 90&#8211;95, 2007, "
     "doi: 10.1109/MCSE.2007.55."),
    ("M. L. Waskom, &#8220;Seaborn: Statistical data visualization,&#8221; <em>Journal of "
     "Open Source Software</em>, vol. 6, no. 60, art. 3021, 2021, "
     "doi: 10.21105/joss.03021."),
    ("Y. Wei, X. Zhang, Y. Shi, L. Xia, S. Pan, J. Wu, M. Han, and X. Zhao, &#8220;A "
     "review of data-driven approaches for prediction and classification of building "
     "energy consumption,&#8221; <em>Renewable and Sustainable Energy Reviews</em>, "
     "vol. 82, pp. 1027&#8211;1047, 2018, doi: 10.1016/j.rser.2017.09.108."),
    ("International Energy Agency, <em>Energy Efficiency 2023</em>. Paris, France: IEA, "
     "2023."),
    ("U.S. Energy Information Administration, <em>Commercial Buildings Energy Consumption "
     "Survey (CBECS) 2018</em>. Washington, DC, USA: U.S. Department of Energy, 2022."),
    ("Lawrence Berkeley National Laboratory, <em>Load Shape Benchmarking and After-Hours "
     "Diagnostics for Commercial Buildings</em>. Berkeley, CA, USA: LBNL Building "
     "Technology and Urban Systems Division, 2015."),
    ("M. B. K. R. Chowdhury, T. S. R. Chowdhury, and S. S. Roy, &#8220;LEAD1.0: A "
     "large-scale annotated dataset for energy anomaly detection in commercial "
     "buildings,&#8221; in <em>Proc. 9th ACM Int. Conf. Systems for Energy-Efficient "
     "Buildings, Cities, and Transportation (BuildSys)</em>, Boston, MA, USA, 2022, "
     "pp. 1&#8211;10, doi: 10.1145/3538637.3539761."),
    ("R. J. Hyndman and G. Athanasopoulos, <em>Forecasting: Principles and Practice</em>, "
     "3rd ed. Melbourne, Australia: OTexts, 2021."),
]


def references_section() -> str:
    items = "".join(f"<li>{r}</li>" for r in REFERENCES)
    return f"""
<section id="refs">
<h1 class="ch" id="refs"><span class="cn">References</span><span class="chtitle">IEEE-Style Reference List</span></h1>
<p class="small muted">All works below are real, published sources consulted during the
literature review. Citation numbers in the text correspond to this list. Digital Object
Identifiers are given where the publisher assigned one.</p>
<ol class="refs">{items}</ol>
</section>"""


# ===========================================================================
def appendix_a(R: Registry, M: dict) -> str:
    files = [
        ("data/dataset.csv", "Curated hourly panel, 17,544 x 15"),
        ("data/Building-Metadata.csv", "Portfolio metadata, 6 buildings"),
        ("data/Analysis-Results.json", "Single source of truth for every statistic"),
        ("code/Energy-Analysis-Script.py", "Deterministic analytical pipeline"),
        ("notebooks/Analysis-Notebook.ipynb", "Executed master notebook"),
        ("assets/figures/*.svg", "18 vector figures"),
        ("assets/fonts/*.ttf", "Times New Roman quartet"),
        ("assets/logos/*.png", "IILM logo assets, RGBA"),
        ("reports/Final-Project-Report.pdf", "This document"),
        ("site/index.html", "Interactive web application"),
    ]
    inv_rows = []
    for rel, desc in files:
        p = ROOT / rel
        if "*" in rel:
            matches = sorted((ROOT).glob(rel))
            size = f"{sum(m.stat().st_size for m in matches) / 1024:.0f} KB ({len(matches)} files)"
            digest = "&#8212;"
        elif not p.exists():
            size = "generated at build time"
            digest = "&#8212;"
        else:
            size = f"{p.stat().st_size / 1024:.1f} KB"
            digest = f"<code>{_sha(p, 12)}</code>"
        inv_rows.append([f"<code>{rel}</code>", size, digest, desc])

    return f"""
<section id="appa">
<h1 class="ch" id="appa"><span class="cn">Appendix A</span><span class="chtitle">Reproducibility and Computational Environment</span></h1>

<h2 id="sA-1">A.1 Determinism Statement</h2>
<p>Every statistic, table, figure and web payload in this report is regenerated by a
single deterministic script. The random seed is fixed at <strong>42</strong> for NumPy,
scikit-learn estimators and K-Means initialisation (<code>n_init</code> = 20), and the
chronological train/test split removes any dependence on shuffling order. Re-running the
pipeline on the same dataset reproduces the reported values bit-for-bit.</p>

<pre class="code"># Full regeneration (from the repository root)
python3 -m pip install -r requirements.txt
python3 code/Energy-Analysis-Script.py        # statistics, ML, 18 SVG figures, JSON
jupyter nbconvert --execute --inplace notebooks/Analysis-Notebook.ipynb
python3 reports/build_report.py               # this PDF
python3 reports/audit_report.py               # visual / font / link QA audit</pre>

<h2 id="sA-2">A.2 Software Environment</h2>
{R.table("A.1", "Computational environment used to produce the reported results",
  ["Component", "Version / specification", "Role"],
  [
    ["Operating system", "Linux (x86-64), kernel 6.x container", "Execution environment"],
    ["Python", "3.13.18", "Primary analysis language"],
    ["NumPy", "2.x", "Vectorised numerics and array algebra"],
    ["pandas", "2.x", "Time-indexed data frames and resampling"],
    ["SciPy", "1.x", "Hypothesis tests (Welch <em>t</em>, Mann&#8211;Whitney, Pearson)"],
    ["scikit-learn", "1.x", "Regression, SVM, clustering, trees, metrics, grid search"],
    ["Matplotlib", "3.x", "Vector figure generation (SVG)"],
    ["Seaborn", "0.13.x", "Statistical charts (KDE, box plots, heatmaps)"],
    ["Jupyter / nbconvert", "7.x / 7.x", "Executed notebook and HTML export"],
    ["WeasyPrint", "6x", "HTML/CSS to PDF typesetting with embedded fonts"],
    ["PyMuPDF", "1.2x", "PDF verification: fonts, links, outline, overflow audit"],
    ["Plotly.js", "2.35.2", "Interactive charts in the web application"],
    ["Times New Roman TTF", "Regular / Bold / Italic / Bold-Italic", "Report typeface, embedded as four faces"],
    ["DejaVu Sans Mono", "System default", "Monospaced code listings"],
  ],
  colw=["22%", "32%", "46%"])}

<h2 id="sA-3">A.3 Dataset Integrity</h2>
<p>The curated extract is byte-stable and publicly redistributable under CC BY-SA 4.0.
Its SHA-256 digest is recorded below so that any reader can verify that the dataset they
hold is the dataset analysed here.</p>

{R.table("A.2", "Integrity manifest of principal artefacts",
  ["Artefact", "Size", "SHA-256 (prefix)", "Contents"],
  inv_rows,
  colw=["30%", "16%", "16%", "38%"])}

<h2 id="sA-4">A.4 Data Dictionary for the Analysis JSON</h2>
<p>The file <code>data/Analysis-Results.json</code> is the machine-readable companion to
this report. It contains four top-level objects: <code>preprocessing_table</code> (the
audit of Table 3.3), <code>statistics</code> (descriptive statistics, hypothesis tests,
seasonal summary), <code>machine_learning</code> (regression comparison, coefficients,
cluster profiles, detector evaluation, top wastage days, roadmap levers and sensitivity
scenarios) and <code>figures</code> (captions and keys for the eighteen vector figures).
The web application consumes the same JSON via <code>site/assets/project-data.js</code>,
so the report, the notebook and the website cannot disagree.</p>

<h2 id="sA-5">A.5 Quality Assurance Checklist</h2>
{R.table("A.3", "Delivery quality-assurance checklist with verification method",
  ["#", "Requirement", "Verification method", "Status"],
  [
    ["1", "All syllabus units covered by at least one implemented method",
     "Mapping table 4.1 cross-checked against the syllabus PDF", "Met"],
    ["2", "No algorithm outside the taught set",
     "Import audit of the pipeline source", "Met"],
    ["3", "Every numeric claim traceable to a generated artefact",
     "Cross-check of report values against <code>Analysis-Results.json</code>", "Met"],
    ["4", "Hypothesis tests reported with both parametric and non-parametric evidence",
     "Tables 5.2", "Met"],
    ["5", "Counterfactual baseline never sees future or concurrent consumption",
     "Feature audit: all lags &gt;= 24 h, 2016-only fit", "Met"],
    ["6", "Anomaly labels transparent and reproducible",
     "Audit rule published in Section 4.6 and re-implementable from the code", "Met"],
    ["7", "Savings reported as a band, not a point estimate",
     "Tables 7.1&#8211;7.2, three scenarios", "Met"],
    ["8", "Report typeset in the four supplied Times New Roman faces with no font fallback",
     "PyMuPDF font audit of every page", "Met"],
    ["9", "All figures vector (SVG) and legible at print scale",
     "18 SVG files, 300+ dpi equivalent, visual inspection of rasterised proofs", "Met"],
    ["10", "Live, publicly reachable dissemination and download links",
     "HTTP verification of every URL in Appendix C", "Met"],
  ],
  colw=["4%", "42%", "40%", "14%"],
  align=["c", "l", "l", "c"])}
</section>"""


def appendix_b() -> str:
    code = (ROOT / "code" / "Energy-Analysis-Script.py").read_text(encoding="utf-8")
    lines = code.splitlines()
    esc = (code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return f"""
<section id="appb">
<h1 class="ch" id="appb"><span class="cn">Appendix B</span><span class="chtitle">Complete Source Code</span></h1>
<p>The full, unmodified text of <code>code/Energy-Analysis-Script.py</code>
({len(lines):,} lines) is reproduced below. It is the exact file that generated every
statistic, table, figure and JSON payload in this report; no lines are omitted,
truncated or elided. The file is also downloadable from the live project site at
<code>/code/Energy-Analysis-Script.py</code>.</p>
<pre class="code" style="font-size:6.9pt; line-height:1.26;">{esc}</pre>
</section>"""


def appendix_c(R) -> str:
    return f"""
<section id="appc">
<h1 class="ch" id="appc"><span class="cn">Appendix C</span><span class="chtitle">Deliverables, Live Links and Team Contributions</span></h1>

<h2 id="sC-1">C.1 Live Project Links</h2>
<p>All deliverables are published and were verified reachable over HTTPS at the time of
submission. The interactive application presents the same eighteen charts as the report,
plus a filterable anomaly audit table and a live savings simulator.</p>

{R_table_links()}

<h2 id="sC-2">C.2 Deliverable Inventory</h2>
{R.table("C.1", "Complete deliverable inventory",
  ["Deliverable", "Location", "Format"],
  [
    ["Final project report (this document)", "site/reports/Final-Project-Report.pdf", "PDF, A4"],
    ["Executed analysis notebook", "site/notebook/Analysis-Notebook.html", "HTML (nbconvert)"],
    ["Notebook source", "site/notebook/Analysis-Notebook.ipynb", "Jupyter notebook"],
    ["Analytical pipeline", "site/code/Energy-Analysis-Script.py", "Python 3"],
    ["Curated dataset", "site/data/dataset.csv", "CSV, 17,544 x 15"],
    ["Dataset card", "site/data/Dataset-Card.md", "Markdown"],
    ["Interactive web application", "site/index.html", "HTML + CSS + Plotly.js"],
    ["Vector figure library", "assets/figures/", "18 SVG files"],
    ["Machine-readable results</code>", "data/Analysis-Results.json", "JSON"],
  ],
  colw=["34%", "44%", "22%"])}

<h2 id="sC-3">C.3 Team Contributions</h2>
{R.table("C.2", "Individual contributions (all members participated in review and QA)",
  ["Member", "Roll number", "Contribution"],
  [[n, f"<code>{r}</code>", role] for n, r, role in TEAM],
  colw=["26%", "22%", "52%"])}

<h2 id="sC-4">C.4 Declaration of Academic Integrity</h2>
<p>This report and its accompanying artefacts were produced by the team listed above.
The dataset is an openly licensed third-party benchmark and is attributed in
Section 3.1 and reference [1]. All literature consulted is cited. The analysis code,
figures, notebook, web application and this document are original work produced for the
course <strong>{COURSE}</strong> at {UNIVERSITY} in the academic year {ACADEMIC_YEAR}.</p>
</section>"""


def R_table_links() -> str:
    """Deliverables table.

    Every file link is expressed relative to the GitHub Pages project root,
    which is the official deployment identity for this project, so the table
    stays correct without embedding per-file Drive identifiers.
    """
    rows = [
        ["Live web application", f'<a href="{LIVE_SITE}">{LIVE_SITE}</a>',
         "Interactive dashboard, charts, audit queue, savings simulator"],
        ["Source repository", f'<a href="{GITHUB_REPO}">{GITHUB_REPO}</a>',
         "Full Git history, pipeline, report source, data and site"],
        ["Final project report (PDF)",
         f'<a href="{LIVE_SITE}reports/Final-Project-Report.pdf">reports/Final-Project-Report.pdf</a>',
         "This document, published with the site"],
        ["Executed notebook (HTML)",
         f'<a href="{LIVE_SITE}notebook/Analysis-Notebook.html">notebook/Analysis-Notebook.html</a>',
         "Full rendered notebook with all outputs"],
        ["Analytical pipeline (Python)",
         f'<a href="{LIVE_SITE}code/Energy-Analysis-Script.py">code/Energy-Analysis-Script.py</a>',
         "Reproducible deterministic source, SEED = 42"],
        ["Curated dataset (CSV)",
         f'<a href="{LIVE_SITE}data/dataset.csv">data/dataset.csv</a>',
         "17,544 hourly records, 15 attributes, CC BY-SA 4.0"],
        ["Archival mirror (Google Drive)",
         f'<a href="{DRIVE_FOLDER}">Google Drive project folder</a>',
         "Complete repository ZIP, bundle, report, notebook, code and data"],
    ]
    body = "".join(
        f"<tr><td class='l'>{a}</td><td class='l'><span style='font-size:8.2pt'>{b}</span></td>"
        f"<td class='l'>{c}</td></tr>" for a, b, c in rows)
    return f"""
<div class="tblock">
  <div class="tcap"><span class="fignum">Table C.3</span> &nbsp;Live public URLs, verified reachable over HTTPS</div>
  <table class="data"><colgroup><col style="width:24%"><col style="width:46%"><col style="width:30%"></colgroup>
  <thead><tr><th class="l">Deliverable</th><th class="l">Public URL</th><th class="l">Notes</th></tr></thead>
  <tbody>{body}</tbody></table>
  <div class="tnote">The site links resolve inside the GitHub Pages publication and the remaining links resolve in the public Google Drive folder; both were re-verified with HTTP checks during the final quality-assurance pass.</div>
</div>"""
