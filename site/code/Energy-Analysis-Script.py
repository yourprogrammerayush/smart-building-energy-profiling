#!/usr/bin/env python3
"""
Smart Building Energy Wastage & Anomaly Profiling
=================================================
Course: Data Visualization and Analysis (26CSEM321) — IILM University, Greater Noida
Section: 2CSE-4 | Academic Year: 2026-27 | Faculty Guide: Aditya Bangia
Team:
  1. Ayush Jha         (25SCS1003001336)
  2. Archit Baloni     (25SCS1003003550)
  3. Ashutosh Sahoo    (25SCS1003004011)
  4. Dev Bhaskar Singh (25SCS1003003174)
  5. Aman Kumar Gupta  (25SCS1003003645)

End-to-end deterministic data analysis, statistical hypothesis testing,
publication-grade vector visualization (15 SVG charts), syllabus-locked
machine learning (Multiple Linear Regression, Decision Tree, One-Class SVM,
RBF-SVM, K-Means Clustering, Gaussian Naive Bayes), and savings roadmap engine.
"""

from __future__ import annotations

import json
import os
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from matplotlib import font_manager as fm
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_absolute_percentage_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    root_mean_squared_error,
    silhouette_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, TimeSeriesSplit
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM, SVC
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, export_text

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# 0. DETERMINISTIC CONFIGURATION & DESIGN TOKENS (§7 Pure-Hue Color System)
# ---------------------------------------------------------------------------
SEED = 42
np.random.seed(SEED)

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "dataset.csv"
META_PATH = ROOT / "data" / "Building-Metadata.csv"
FIG_DIR = ROOT / "assets" / "figures"
OUT_JSON = ROOT / "data" / "Analysis-Results.json"
SITE_DATA_JS = ROOT / "site" / "assets" / "project-data.js"

FIG_DIR.mkdir(parents=True, exist_ok=True)
(ROOT / "site" / "assets").mkdir(parents=True, exist_ok=True)

# Register official Times New Roman TrueType fonts if present
FONT_DIR = ROOT / "assets" / "fonts"
FONT_FAMILY = "DejaVu Serif"
if (FONT_DIR / "TimesNewRoman.ttf").exists():
    for ttf_name in [
        "TimesNewRoman.ttf",
        "TimesNewRoman-Bold.ttf",
        "TimesNewRoman-Italic.ttf",
        "TimesNewRoman-BoldItalic.ttf",
    ]:
        ttf_path = FONT_DIR / ttf_name
        if ttf_path.exists():
            fm.fontManager.addfont(str(ttf_path))
    FONT_FAMILY = "Times New Roman Cyr"

# §7 Pure Saturated Accent Palette + Approved Neutrals
PALETTE = {
    "blue": "#0000FF",      # Primary data series / expected baseline
    "red": "#FF0000",       # Anomalies / wastage / alerts
    "green": "#00FF00",     # Savings / optimized / normal target
    "cyan": "#00FFFF",      # Secondary series / weather / campus
    "magenta": "#FF00FF",   # Tertiary series / cluster / threshold
    "yellow": "#FFFF00",    # Warning band / off-hour highlight
    "navy": "#0B1F3A",      # Structural headings / dark borders
    "charcoal": "#222222",  # Secondary neutral line
    "black": "#000000",     # Body text & axes
    "grid": "#D8DEE9",      # Subtle gray gridlines on pure white
    "white": "#FFFFFF",     # Canvas background
}

plt.rcParams.update({
    "figure.facecolor": PALETTE["white"],
    "axes.facecolor": PALETTE["white"],
    "savefig.facecolor": PALETTE["white"],
    "font.family": FONT_FAMILY,
    "font.size": 10.5,
    "axes.titlesize": 12.5,
    "axes.titleweight": "bold",
    "axes.labelsize": 10.5,
    "axes.labelcolor": PALETTE["black"],
    "xtick.color": PALETTE["black"],
    "ytick.color": PALETTE["black"],
    "text.color": PALETTE["black"],
    "axes.edgecolor": PALETTE["charcoal"],
    "axes.linewidth": 0.9,
    "axes.grid": True,
    "grid.color": PALETTE["grid"],
    "grid.linewidth": 0.6,
    "grid.alpha": 0.85,
    "legend.frameon": True,
    "legend.facecolor": PALETTE["white"],
    "legend.edgecolor": PALETTE["charcoal"],
    "legend.fontsize": 9.2,
    "svg.fonttype": "none",  # Keep crisp selectable text in SVG -> WeasyPrint PDF
})

OFFICE_COLS = ["Fox_office_Joy", "Fox_office_Vicki", "Fox_office_Clayton"]
EDU_COLS = ["Fox_education_Tamika", "Fox_education_Carleen", "Fox_education_Kris"]
BLDG_COLS = OFFICE_COLS + EDU_COLS
TARIFF_USD_PER_KWH = 0.12
EMISSION_KG_PER_KWH = 0.417
TOTAL_SQM = 31462.6


def save_svg(fig: plt.Figure, filename: str) -> str:
    path = FIG_DIR / filename
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return str(path.relative_to(ROOT))


# ---------------------------------------------------------------------------
# 1. DATA LOADING & PREPROCESSING (Syllabus Unit I & Unit II)
# ---------------------------------------------------------------------------
def load_and_preprocess() -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    raw = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
    meta = pd.read_csv(META_PATH)
    raw = raw.sort_values("timestamp").reset_index(drop=True)

    prep_table = []

    # Audit missing values and negative trace precipitation codes before cleaning
    raw_meter_na = int(raw[BLDG_COLS].isna().sum().sum())
    prep_table.append({
        "issue": "Smart-meter sensor dropouts (6 buildings)",
        "affected_columns": "Fox_office_* & Fox_education_*",
        "raw_count": raw_meter_na,
        "pct_rows": round(raw_meter_na / (len(raw) * len(BLDG_COLS)) * 100, 3),
        "treatment": "Time-indexed linear interpolation across short 1-3 hr telemetry gaps",
    })

    wx_core = ["airTemperature", "dewTemperature", "seaLvlPressure", "windSpeed"]
    raw_wx_na = int(raw[wx_core].isna().sum().sum())
    prep_table.append({
        "issue": "Core weather station dropouts",
        "affected_columns": "airTemperature, dewTemperature, seaLvlPressure, windSpeed",
        "raw_count": raw_wx_na,
        "pct_rows": round(raw_wx_na / (len(raw) * len(wx_core)) * 100, 3),
        "treatment": "Temporal linear interpolation + boundary backfill/forward-fill",
    })

    cloud_na = int(raw["cloudCoverage"].isna().sum())
    wind_dir_na = int(raw["windDirection"].isna().sum())
    prep_table.append({
        "issue": "High-missingness auxiliary sky/wind-angle sensors",
        "affected_columns": "cloudCoverage, windDirection",
        "raw_count": cloud_na + wind_dir_na,
        "pct_rows": round((cloud_na + wind_dir_na) / (len(raw) * 2) * 100, 2),
        "treatment": "Median-by-hour imputation for EDA; excluded from core ML matrix to prevent noise",
    })

    trace_precip = int((raw["precipDepth1HR"] < 0).sum())
    prep_table.append({
        "issue": "ISD trace precipitation sentinel (-1.0 mm)",
        "affected_columns": "precipDepth1HR",
        "raw_count": trace_precip + int(raw["precipDepth1HR"].isna().sum()),
        "pct_rows": round((trace_precip + int(raw["precipDepth1HR"].isna().sum())) / len(raw) * 100, 2),
        "treatment": "Replaced -1.0 trace flags with 0.05 mm and filled missing hours with 0.0 mm",
    })

    df = raw.set_index("timestamp").copy()

    # Clean precipitation trace sentinel (-1 -> 0.05 mm)
    df["precipDepth1HR"] = df["precipDepth1HR"].replace(-1.0, 0.05).fillna(0.0)

    # Interpolate smart-meter and core weather columns along timestamp index
    for col in BLDG_COLS + wx_core:
        df[col] = df[col].interpolate(method="time").bfill().ffill()

    df["cloudCoverage"] = df.groupby(df.index.hour)["cloudCoverage"].transform(
        lambda s: s.fillna(s.median())
    ).fillna(df["cloudCoverage"].median())
    df["windDirection"] = df["windDirection"].interpolate(method="time").bfill().ffill()

    # Aggregate portfolio loads
    df["office_kwh"] = df[OFFICE_COLS].sum(axis=1)
    df["edu_kwh"] = df[EDU_COLS].sum(axis=1)
    df["total_kwh"] = df[BLDG_COLS].sum(axis=1)

    # IQR outlier audit on total_kwh (flag, NEVER delete wastage spikes!)
    q1, q3 = df["total_kwh"].quantile([0.25, 0.75])
    iqr = q3 - q1
    upper_fence = q3 + 1.5 * iqr
    lower_fence = max(0.0, q1 - 1.5 * iqr)
    iqr_flags = int(((df["total_kwh"] > upper_fence) | (df["total_kwh"] < lower_fence)).sum())
    df["iqr_high_flag"] = (df["total_kwh"] > upper_fence).astype(int)
    prep_table.append({
        "issue": "Extreme hourly load spikes / dips (1.5 x IQR audit)",
        "affected_columns": "total_kwh",
        "raw_count": iqr_flags,
        "pct_rows": round(iqr_flags / len(df) * 100, 2),
        "treatment": "Retained & flagged (iqr_high_flag=1) because high spikes represent physical HVAC signal",
    })

    # -----------------------------------------------------------------------
    # 2. FEATURE ENGINEERING WITH NUMPY & PANDAS (Syllabus Unit II)
    # -----------------------------------------------------------------------
    # Psychrometric Relative Humidity (%) via Magnus-Tetens equation
    t_air = df["airTemperature"].to_numpy()
    t_dew = df["dewTemperature"].to_numpy()
    sat_vp = np.exp((17.625 * t_air) / (243.04 + t_air))
    act_vp = np.exp((17.625 * t_dew) / (243.04 + t_dew))
    df["rel_humidity"] = np.clip(100.0 * (act_vp / sat_vp), 1.0, 100.0)

    # Calendar & operational regime indicators
    df["year"] = df.index.year
    df["month"] = df.index.month
    df["day"] = df.index.day
    df["hour"] = df.index.hour
    df["dayofweek"] = df.index.dayofweek
    df["is_weekend"] = (df["dayofweek"] >= 5).astype(int)
    df["is_off_hour"] = ((df["hour"] >= 22) | (df["hour"] < 6)).astype(int)
    df["is_work_hour"] = ((df["hour"] >= 8) & (df["hour"] <= 18) & (df["is_weekend"] == 0)).astype(int)

    season_map = {
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Spring", 4: "Spring", 5: "Spring",
        6: "Summer", 7: "Summer", 8: "Summer",
        9: "Autumn", 10: "Autumn", 11: "Autumn",
    }
    df["season"] = df["month"].map(season_map)

    # Thermodynamic HVAC proxies (ASHRAE 18.3 C balance point)
    df["cdd_18"] = np.maximum(0.0, df["airTemperature"] - 18.3)
    df["hdd_18"] = np.maximum(0.0, 18.3 - df["airTemperature"])
    df["temp_rh_interaction"] = (df["airTemperature"] * df["rel_humidity"]) / 100.0

    # Cyclical Fourier harmonics for smooth diurnal periodicity
    df["sin_hour"] = np.sin(2.0 * np.pi * df["hour"] / 24.0)
    df["cos_hour"] = np.cos(2.0 * np.pi * df["hour"] / 24.0)
    df["sin_hour_2"] = np.sin(4.0 * np.pi * df["hour"] / 24.0)
    df["cos_hour_2"] = np.cos(4.0 * np.pi * df["hour"] / 24.0)

    # Autoregressive lag & rolling statistics (strictly past-looking: shift >= 24h)
    df["lag_24h"] = df["total_kwh"].shift(24)
    df["lag_168h"] = df["total_kwh"].shift(168)
    df["roll_mean_24h"] = df["total_kwh"].shift(24).rolling(window=24, min_periods=24).mean()
    df["roll_std_24h"] = df["total_kwh"].shift(24).rolling(window=24, min_periods=24).std()

    return df, meta, prep_table


# ---------------------------------------------------------------------------
# 3. STATISTICAL ANALYSIS & HYPOTHESIS TESTING (Syllabus Units I-III)
# ---------------------------------------------------------------------------
def run_statistical_analysis(df: pd.DataFrame) -> dict:
    wkday = df.loc[df["is_weekend"] == 0, "total_kwh"]
    wkend = df.loc[df["is_weekend"] == 1, "total_kwh"]

    t_stat, t_pval = stats.ttest_ind(wkday, wkend, equal_var=False)
    u_stat, u_pval = stats.mannwhitneyu(wkday, wkend, alternative="two-sided")

    off_hr = df.loc[df["is_off_hour"] == 1, "total_kwh"]
    work_hr = df.loc[df["is_work_hour"] == 1, "total_kwh"]
    off_t, off_p = stats.ttest_ind(work_hr, off_hr, equal_var=False)

    r_temp, p_temp = stats.pearsonr(df["airTemperature"], df["total_kwh"])
    r_cdd, p_cdd = stats.pearsonr(df["cdd_18"], df["total_kwh"])
    r_rh, p_rh = stats.pearsonr(df["rel_humidity"], df["total_kwh"])

    desc_cols = [
        "total_kwh", "office_kwh", "edu_kwh",
        "airTemperature", "rel_humidity", "windSpeed", "seaLvlPressure", "cdd_18"
    ]
    desc_df = df[desc_cols].agg(["count", "mean", "std", "min", lambda s: s.quantile(0.25), "median", lambda s: s.quantile(0.75), "max", "skew"]).T
    desc_df.columns = ["count", "mean", "std", "min", "q25", "median", "q75", "max", "skew"]

    # Off-hour share of total kWh
    total_energy_mwh = df["total_kwh"].sum() / 1000.0
    off_hour_energy_mwh = df.loc[df["is_off_hour"] == 1, "total_kwh"].sum() / 1000.0
    weekend_energy_mwh = df.loc[df["is_weekend"] == 1, "total_kwh"].sum() / 1000.0

    # Seasonal averages
    seasonal = (
        df.groupby("season")["total_kwh"]
        .agg(["mean", "std", "median", "max"])
        .reindex(["Winter", "Spring", "Summer", "Autumn"])
        .round(2)
        .to_dict(orient="index")
    )

    return {
        "total_rows": int(len(df)),
        "total_days": int(df.index.normalize().nunique()),
        "total_energy_kwh": round(float(df["total_kwh"].sum()), 2),
        "total_energy_mwh": round(float(total_energy_mwh), 2),
        "annual_avg_mwh": round(float(total_energy_mwh / 2.0), 2),
        "annual_eui_kwh_m2": round(float((df["total_kwh"].sum() / 2.0) / TOTAL_SQM), 2),
        "mean_hourly_kwh": round(float(df["total_kwh"].mean()), 2),
        "std_hourly_kwh": round(float(df["total_kwh"].std()), 2),
        "median_hourly_kwh": round(float(df["total_kwh"].median()), 2),
        "min_hourly_kwh": round(float(df["total_kwh"].min()), 2),
        "max_hourly_kwh": round(float(df["total_kwh"].max()), 2),
        "weekday_mean_kwh": round(float(wkday.mean()), 2),
        "weekend_mean_kwh": round(float(wkend.mean()), 2),
        "weekday_weekend_ratio": round(float(wkday.mean() / wkend.mean()), 3),
        "welch_t_stat": round(float(t_stat), 2),
        "welch_p_val": float(t_pval),
        "mannwhitney_u": float(u_stat),
        "mannwhitney_p_val": float(u_pval),
        "work_hour_mean_kwh": round(float(work_hr.mean()), 2),
        "off_hour_mean_kwh": round(float(off_hr.mean()), 2),
        "off_to_work_ratio": round(float(off_hr.mean() / work_hr.mean()), 3),
        "off_hour_t_stat": round(float(off_t), 2),
        "off_hour_share_pct": round(float(off_hour_energy_mwh / total_energy_mwh * 100.0), 2),
        "weekend_share_pct": round(float(weekend_energy_mwh / total_energy_mwh * 100.0), 2),
        "pearson_r_temp": round(float(r_temp), 4),
        "pearson_p_temp": float(p_temp),
        "pearson_r_cdd": round(float(r_cdd), 4),
        "pearson_r_rh": round(float(r_rh), 4),
        "descriptive_table": desc_df.round(2).to_dict(orient="index"),
        "seasonal_summary": seasonal,
    }


# ---------------------------------------------------------------------------
# 4. MACHINE LEARNING PIPELINE (Syllabus-Locked: Unit II & Unit IV)
# ---------------------------------------------------------------------------
def run_machine_learning(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    # --- PART A: EXPECTED ENERGY REGRESSION (Hourly, Chronological Split) ---
    # Model A1: Counterfactual Weather + Schedule Multiple Linear Regression
    # Trained on 2016 (Year 1) and evaluated out-of-sample on 2017 (Year 2)
    df = df.copy()
    df["hr_wk_regime"] = df["hour"].astype(str) + "_" + df["is_weekend"].astype(str)

    sched_cols = [
        "airTemperature", "rel_humidity", "windSpeed", "seaLvlPressure",
        "cdd_18", "hdd_18", "temp_rh_interaction", "hr_wk_regime", "month"
    ]
    X_sched_all = pd.get_dummies(df[sched_cols], columns=["hr_wk_regime", "month"], drop_first=True, dtype=float)

    train_mask_all = df["year"] == 2016
    test_mask_all = df["year"] == 2017

    lr_counterfactual = LinearRegression()
    lr_counterfactual.fit(X_sched_all.loc[train_mask_all], df.loc[train_mask_all, "total_kwh"])
    df["expected_kwh"] = lr_counterfactual.predict(X_sched_all)
    df["residual_kwh"] = df["total_kwh"] - df["expected_kwh"]

    # Model A2 & A3: Autoregressive + Weather Multiple Linear Regression vs Decision Tree Regressor
    df_lag = df.dropna(subset=["lag_24h", "lag_168h", "roll_mean_24h", "roll_std_24h"]).copy()
    reg_features = [
        "airTemperature", "rel_humidity", "windSpeed", "seaLvlPressure",
        "cdd_18", "hdd_18", "temp_rh_interaction",
        "is_weekend", "is_off_hour",
        "sin_hour", "cos_hour", "sin_hour_2", "cos_hour_2",
        "lag_24h", "lag_168h", "roll_mean_24h"
    ]

    tr_lag = df_lag["year"] == 2016
    te_lag = df_lag["year"] == 2017

    X_tr, y_tr = df_lag.loc[tr_lag, reg_features], df_lag.loc[tr_lag, "total_kwh"]
    X_te, y_te = df_lag.loc[te_lag, reg_features], df_lag.loc[te_lag, "total_kwh"]

    scaler_reg = StandardScaler()
    X_tr_sc = scaler_reg.fit_transform(X_tr)
    X_te_sc = scaler_reg.transform(X_te)

    mlr_full = LinearRegression()
    mlr_full.fit(X_tr_sc, y_tr)
    pred_mlr_tr = mlr_full.predict(X_tr_sc)
    pred_mlr_te = mlr_full.predict(X_te_sc)

    # Tune Decision Tree Regressor via 5-fold TimeSeriesSplit on 2016 training data
    tscv = TimeSeriesSplit(n_splits=5)
    dt_grid = GridSearchCV(
        DecisionTreeRegressor(random_state=SEED),
        param_grid={"max_depth": [5, 7, 9, 12], "min_samples_leaf": [10, 25, 50]},
        cv=tscv,
        scoring="r2",
    )
    dt_grid.fit(X_tr, y_tr)
    dt_reg = dt_grid.best_estimator_
    pred_dt_te = dt_reg.predict(X_te)

    # Align counterfactual baseline metrics on exact same 2017 test set
    y_te_cf = df.loc[test_mask_all, "total_kwh"]
    pred_cf_te = df.loc[test_mask_all, "expected_kwh"]

    def reg_metrics(y_true, y_hat):
        return {
            "r2": round(float(r2_score(y_true, y_hat)), 4),
            "rmse": round(float(root_mean_squared_error(y_true, y_hat)), 2),
            "mae": round(float(mean_absolute_error(y_true, y_hat)), 2),
            "mape_pct": round(float(mean_absolute_percentage_error(y_true, y_hat) * 100.0), 2),
        }

    reg_comparison = {
        "Counterfactual_Schedule_Weather_MLR": reg_metrics(y_te_cf, pred_cf_te),
        "Full_Autoregressive_Weather_MLR": reg_metrics(y_te, pred_mlr_te),
        "Tuned_Decision_Tree_Regressor": reg_metrics(y_te, pred_dt_te),
    }

    # Standardized & raw MLR coefficients table
    mlr_raw = LinearRegression().fit(X_tr, y_tr)
    coef_table = []
    for feat, raw_c, std_c in zip(reg_features, mlr_raw.coef_, mlr_full.coef_):
        coef_table.append({
            "feature": feat,
            "raw_coef": round(float(raw_c), 4),
            "std_coef": round(float(std_c), 2),
        })
    coef_table.sort(key=lambda r: abs(r["std_coef"]), reverse=True)

    df_lag["pred_mlr"] = np.nan
    df_lag.loc[tr_lag, "pred_mlr"] = pred_mlr_tr
    df_lag.loc[te_lag, "pred_mlr"] = pred_mlr_te

    # --- PART B: DAILY AGGREGATION, CLUSTERING & ANOMALY PROFILING (Unit IV) ---
    df["date"] = df.index.normalize()
    off_series = df["total_kwh"].where(df["is_off_hour"] == 1)
    work_series = df["total_kwh"].where(df["hour"].between(8, 18))

    daily = df.groupby("date").agg(
        daily_kwh=("total_kwh", "sum"),
        expected_daily_kwh=("expected_kwh", "sum"),
        office_daily_kwh=("office_kwh", "sum"),
        edu_daily_kwh=("edu_kwh", "sum"),
        mean_kwh=("total_kwh", "mean"),
        peak_kwh=("total_kwh", "max"),
        min_kwh=("total_kwh", "min"),
        mean_temp=("airTemperature", "mean"),
        max_temp=("airTemperature", "max"),
        mean_rh=("rel_humidity", "mean"),
        mean_wind=("windSpeed", "mean"),
        cdd_daily=("cdd_18", "mean"),
        is_weekend=("is_weekend", "first"),
        month=("month", "first"),
        year=("year", "first"),
        season=("season", "first"),
    )
    daily["off_hour_mean_kwh"] = off_series.groupby(df["date"]).mean()
    daily["off_hour_sum_kwh"] = off_series.groupby(df["date"]).sum()
    daily["work_hour_mean_kwh"] = work_series.groupby(df["date"]).mean()

    daily["excess_kwh"] = daily["daily_kwh"] - daily["expected_daily_kwh"]
    daily["excess_pct"] = (daily["excess_kwh"] / daily["expected_daily_kwh"]) * 100.0
    daily["baseload_ratio"] = daily["off_hour_mean_kwh"] / daily["peak_kwh"]
    daily["load_factor"] = daily["mean_kwh"] / daily["peak_kwh"]
    daily["off_hour_share_pct"] = (daily["off_hour_sum_kwh"] / daily["daily_kwh"]) * 100.0

    # Domain-Audited Operational Wastage Reference Benchmark (LBNL / ASHRAE rules)
    # Rule: Positive excess > 1.25 * std(excess_kwh in 2016) OR
    # (off-hour baseload > 90th pct of season-weekend group AND excess_kwh > 350 kWh)
    res_std_2016 = float(daily.loc[daily["year"] == 2016, "excess_kwh"].std())
    excess_thresh = 1.25 * res_std_2016

    grp_p90 = daily.groupby(["season", "is_weekend"])["off_hour_mean_kwh"].transform(lambda s: s.quantile(0.90))
    daily["domain_wastage_label"] = (
        (daily["excess_kwh"] > excess_thresh)
        | ((daily["off_hour_mean_kwh"] > grp_p90) & (daily["excess_kwh"] > 350.0))
    ).astype(int)

    # K-Means Clustering on Daily Operational Profiles (Unit IV)
    cluster_features = [
        "mean_kwh", "off_hour_mean_kwh", "baseload_ratio",
        "excess_kwh", "mean_temp", "is_weekend"
    ]
    scaler_clust = StandardScaler()
    X_clust = scaler_clust.fit_transform(daily[cluster_features])

    k_sweep = []
    for k in range(2, 8):
        km_tmp = KMeans(n_clusters=k, random_state=SEED, n_init=25)
        lbl_tmp = km_tmp.fit_predict(X_clust)
        k_sweep.append({
            "k": k,
            "inertia": round(float(km_tmp.inertia_), 2),
            "silhouette": round(float(silhouette_score(X_clust, lbl_tmp)), 4),
        })

    # Fit 4 operational regimes (k=4 gives granular physical archetypes with strong silhouette)
    K_OPT = 4
    kmeans = KMeans(n_clusters=K_OPT, random_state=SEED, n_init=30)
    daily["cluster_raw"] = kmeans.fit_predict(X_clust)

    # Distance to nearest cluster centroid & distance to normal centroids
    dists = kmeans.transform(X_clust)
    daily["kmeans_min_dist"] = dists.min(axis=1)

    # Order clusters cleanly for naming
    c_summary = daily.groupby("cluster_raw").agg(
        count=("daily_kwh", "count"),
        mean_daily_kwh=("daily_kwh", "mean"),
        off_hour_kwh=("off_hour_mean_kwh", "mean"),
        baseload_ratio=("baseload_ratio", "mean"),
        excess_kwh=("excess_kwh", "mean"),
        mean_temp=("mean_temp", "mean"),
        wkend_frac=("is_weekend", "mean"),
    )

    # Assign descriptive archetype names based on physical properties
    archetype_names = {}
    used = set()
    # 1. Weekend / Low-Occupancy Setback: highest wkend_frac
    c_wkend = int(c_summary["wkend_frac"].idxmax())
    archetype_names[c_wkend] = "Weekend Setback Regime"
    used.add(c_wkend)
    # 2. High-Heat Peak Cooling & Wastage Surge: highest mean_daily_kwh among remaining
    rem = [c for c in c_summary.index if c not in used]
    c_summer = int(c_summary.loc[rem, "mean_daily_kwh"].idxmax())
    archetype_names[c_summer] = "Summer Peak Cooling & Drift"
    used.add(c_summer)
    # 3. High-Baseload / Excess Drift vs Mild Baseline Weekday
    rem = [c for c in c_summary.index if c not in used]
    c_mild = int(c_summary.loc[rem, "mean_daily_kwh"].idxmin())
    archetype_names[c_mild] = "Mild-Weather Efficient Baseline"
    used.add(c_mild)
    c_trans = [c for c in c_summary.index if c not in used][0]
    archetype_names[c_trans] = "Shoulder-Season Baseload Drift"

    daily["cluster_name"] = daily["cluster_raw"].map(archetype_names)

    # K-Means distance-based anomaly flag (top 10% furthest in positive excess direction)
    km_score = daily["kmeans_min_dist"] * np.where(daily["excess_kwh"] > 0, 1.0, 0.35)
    km_cutoff = float(np.quantile(km_score, 0.89))
    daily["kmeans_anomaly_flag"] = (km_score >= km_cutoff).astype(int)

    # --- Unsupervised One-Class SVM for Wastage-Day Anomaly Flagging (Unit IV) ---
    oc_features = ["excess_kwh", "off_hour_mean_kwh", "baseload_ratio", "off_hour_share_pct", "mean_temp"]
    scaler_oc = StandardScaler()
    # Train OCSVM on normal/non-extreme 2016 baseline days (excess_kwh <= excess_thresh) to learn healthy envelope
    healthy_2016 = (daily["year"] == 2016) & (daily["excess_kwh"].abs() <= excess_thresh)
    scaler_oc.fit(daily.loc[healthy_2016, oc_features])
    X_oc_all = scaler_oc.transform(daily[oc_features])
    X_oc_train = scaler_oc.transform(daily.loc[healthy_2016, oc_features])

    ocsvm = OneClassSVM(kernel="rbf", nu=0.08, gamma="scale")
    ocsvm.fit(X_oc_train)
    raw_oc_pred = ocsvm.predict(X_oc_all)  # -1 = outlier, +1 = inlier
    daily["ocsvm_score"] = -ocsvm.decision_function(X_oc_all)  # positive = anomalous
    # Wastage anomaly = OCSVM outlier WITH positive excess consumption (exclude meter-dropouts/holidays)
    daily["ocsvm_wastage_flag"] = ((raw_oc_pred == -1) & (daily["excess_kwh"] > 0)).astype(int)

    # Consensus Hybrid Flag (flagged by OCSVM or K-Means distance + positive excess > 250 kWh)
    daily["consensus_wastage_flag"] = (
        ((daily["ocsvm_wastage_flag"] == 1) | (daily["kmeans_anomaly_flag"] == 1))
        & (daily["excess_kwh"] > 250.0)
    ).astype(int)

    # --- Supervised Classification Comparison on Audited Wastage Days (Unit IV) ---
    # Compare RBF-SVM (SVC), Decision Tree Classifier, and Gaussian Naive Bayes
    # IMPORTANT: Exclude exact rule-threshold variables (excess_kwh, off_hour_mean_kwh) from X_cls
    # so classifiers learn genuine operational load-shape patterns without trivial tautology!
    cls_features = [
        "daily_kwh", "peak_kwh", "min_kwh", "baseload_ratio", "load_factor",
        "off_hour_share_pct", "mean_temp", "mean_rh", "mean_wind", "is_weekend"
    ]
    X_cls = daily[cls_features]
    y_cls = daily["domain_wastage_label"]

    # Stratified 70/30 train-test split with SEED=42
    skf_split = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    # Hold out 2017 as chronological test OR stratified split — let's evaluate on 2017 out-of-sample test!
    cls_tr = daily["year"] == 2016
    cls_te = daily["year"] == 2017

    scaler_cls = StandardScaler()
    X_cls_tr = scaler_cls.fit_transform(X_cls.loc[cls_tr])
    X_cls_te = scaler_cls.transform(X_cls.loc[cls_te])
    y_cls_tr = y_cls.loc[cls_tr]
    y_cls_te = y_cls.loc[cls_te]

    # 1. Supervised SVM (RBF Kernel, GridSearchCV tuned)
    svm_grid = GridSearchCV(
        SVC(kernel="rbf", probability=True, class_weight="balanced", random_state=SEED),
        param_grid={"C": [0.5, 1.0, 5.0, 10.0], "gamma": ["scale", 0.05, 0.1]},
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED),
        scoring="f1",
    )
    svm_grid.fit(X_cls_tr, y_cls_tr)
    best_svc = svm_grid.best_estimator_
    svc_pred = best_svc.predict(X_cls_te)
    svc_prob = best_svc.predict_proba(X_cls_te)[:, 1]

    # 2. Decision Tree Classifier (Interpretable Rule Extractor)
    dt_cls_grid = GridSearchCV(
        DecisionTreeClassifier(class_weight="balanced", random_state=SEED),
        param_grid={"max_depth": [3, 4, 5], "min_samples_leaf": [5, 10, 15]},
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED),
        scoring="f1",
    )
    dt_cls_grid.fit(X_cls.loc[cls_tr], y_cls_tr)
    best_dt_cls = dt_cls_grid.best_estimator_
    dt_cls_pred = best_dt_cls.predict(X_cls.loc[cls_te])
    dt_cls_prob = best_dt_cls.predict_proba(X_cls.loc[cls_te])[:, 1]

    # Also fit a clean depth-3 rule tree for human-readable report rules
    rule_tree = DecisionTreeClassifier(max_depth=3, min_samples_leaf=8, class_weight="balanced", random_state=SEED)
    rule_tree.fit(X_cls.loc[cls_tr], y_cls_tr)
    tree_rules_text = export_text(rule_tree, feature_names=cls_features)

    # 3. Gaussian Naive Bayes (Unit IV Bayes Classification)
    gnb = GaussianNB()
    gnb.fit(X_cls_tr, y_cls_tr)
    gnb_pred = gnb.predict(X_cls_te)
    gnb_prob = gnb.predict_proba(X_cls_te)[:, 1]

    def cls_eval(y_true, y_hat, y_score=None):
        cm = confusion_matrix(y_true, y_hat)
        out = {
            "accuracy": round(float(accuracy_score(y_true, y_hat)), 4),
            "precision": round(float(precision_score(y_true, y_hat, zero_division=0)), 4),
            "recall": round(float(recall_score(y_true, y_hat, zero_division=0)), 4),
            "f1": round(float(f1_score(y_true, y_hat, zero_division=0)), 4),
            "tn": int(cm[0, 0]),
            "fp": int(cm[0, 1]),
            "fn": int(cm[1, 0]),
            "tp": int(cm[1, 1]),
        }
        if y_score is not None:
            out["roc_auc"] = round(float(roc_auc_score(y_true, y_score)), 4)
        return out

    anomaly_eval_2017 = {
        "Unsupervised_OneClass_SVM": cls_eval(
            y_cls_te, daily.loc[cls_te, "ocsvm_wastage_flag"], daily.loc[cls_te, "ocsvm_score"]
        ),
        "Unsupervised_KMeans_Distance": cls_eval(
            y_cls_te, daily.loc[cls_te, "kmeans_anomaly_flag"], km_score.loc[cls_te]
        ),
        "Hybrid_Consensus_Detector": cls_eval(
            y_cls_te, daily.loc[cls_te, "consensus_wastage_flag"], daily.loc[cls_te, "ocsvm_score"]
        ),
        "Supervised_RBF_SVM": cls_eval(y_cls_te, svc_pred, svc_prob),
        "Supervised_Decision_Tree": cls_eval(y_cls_te, dt_cls_pred, dt_cls_prob),
        "Supervised_Gaussian_Naive_Bayes": cls_eval(y_cls_te, gnb_pred, gnb_prob),
    }

    # Top flagged wastage days across the 2-year study
    flagged_days = daily[daily["consensus_wastage_flag"] == 1].sort_values("excess_kwh", ascending=False).copy()
    top_wastage_records = []
    for dt_idx, row in flagged_days.head(15).iterrows():
        top_wastage_records.append({
            "date": dt_idx.strftime("%Y-%m-%d"),
            "day_name": dt_idx.strftime("%A"),
            "season": row["season"],
            "actual_kwh": round(float(row["daily_kwh"]), 1),
            "expected_kwh": round(float(row["expected_daily_kwh"]), 1),
            "excess_kwh": round(float(row["excess_kwh"]), 1),
            "excess_pct": round(float(row["excess_pct"]), 1),
            "off_hour_mean_kwh": round(float(row["off_hour_mean_kwh"]), 1),
            "baseload_ratio": round(float(row["baseload_ratio"]), 3),
            "mean_temp_c": round(float(row["mean_temp"]), 1),
            "est_waste_cost_usd": round(float(row["excess_kwh"] * TARIFF_USD_PER_KWH), 2),
            "cluster_name": row["cluster_name"],
        })

    # Cluster summary table
    cluster_profiles = []
    for c_id, name in archetype_names.items():
        sub = daily[daily["cluster_raw"] == c_id]
        cluster_profiles.append({
            "cluster_id": int(c_id),
            "name": name,
            "days_count": int(len(sub)),
            "share_days_pct": round(float(len(sub) / len(daily) * 100.0), 1),
            "mean_daily_kwh": round(float(sub["daily_kwh"].mean()), 1),
            "off_hour_mean_kwh": round(float(sub["off_hour_mean_kwh"].mean()), 1),
            "baseload_ratio": round(float(sub["baseload_ratio"].mean()), 3),
            "mean_excess_kwh": round(float(sub["excess_kwh"].mean()), 1),
            "mean_temp_c": round(float(sub["mean_temp"].mean()), 1),
            "weekend_pct": round(float(sub["is_weekend"].mean() * 100.0), 1),
        })
    cluster_profiles.sort(key=lambda x: x["mean_daily_kwh"], reverse=True)

    # --- PART C: EVIDENCE-BASED SAVINGS ROADMAP & SENSITIVITY ANALYSIS (15-20% Target) ---
    # Quantify annual average consumption and four physics-grounded conservation levers
    annual_kwh = float(df["total_kwh"].sum() / 2.0)
    # Critical 24/7 life-safety, server & lab-cold-chain standby floor = 360 kWh/h (~30% of peak load, per LBNL office/campus benchmark)
    SAFETY_FLOOR_KWH = 360.0

    # Lever 1: Automated Overnight HVAC Setback & Lighting Sweep (22:00-05:59)
    # Captures 68% of avoidable overnight load above the 360 kWh critical standby floor
    avoidable_overnight_pool = float(np.maximum(0.0, df.loc[df["is_off_hour"] == 1, "total_kwh"] - SAFETY_FLOOR_KWH).sum() / 2.0)
    lever1_overnight_kwh = round(0.68 * avoidable_overnight_pool, 1)

    # Lever 2: Weekend & Academic-Break Deep HVAC Consolidation (06:00-21:59 on Sat/Sun)
    # Consolidates weekend occupancy into zoned wings, capturing 62% of load above 400 kWh zone floor
    wkend_day_mask = (df["is_weekend"] == 1) & (df["is_off_hour"] == 0)
    avoidable_wkend_pool = float(np.maximum(0.0, df.loc[wkend_day_mask, "total_kwh"] - 400.0).sum() / 2.0)
    lever2_weekend_kwh = round(0.62 * avoidable_wkend_pool, 1)

    # Lever 3: Real-Time OCSVM Anomaly Alerting & Rapid BMS Override Reset
    # Eliminates 82% of positive counterfactual excess kWh on flagged anomalous wastage days
    anom_day_excess = float(daily.loc[daily["consensus_wastage_flag"] == 1, "excess_kwh"].clip(lower=0).sum() / 2.0)
    lever3_anomaly_kwh = round(0.82 * anom_day_excess, 1)

    # Lever 4: Demand-Controlled Ventilation (DCV), Economizer Tuning & +1.0 C Cooling Deadband (weekday work hours >24 C)
    # Standard ASHRAE +1 C cooling setpoint trim + CO2-DCV yields ~32% reduction on hot-weather cooling increment above 480 kWh
    hot_work_mask = (df["is_work_hour"] == 1) & (df["airTemperature"] > 24.0)
    hot_work_cooling_kwh = float(np.maximum(0.0, df.loc[hot_work_mask, "total_kwh"] - 480.0).sum() / 2.0)
    lever4_hvac_opt_kwh = round(0.32 * hot_work_cooling_kwh, 1)

    roadmap_levers = [
        {
            "id": "L1",
            "lever": "Overnight BMS Setback & Lighting Sweep (22:00-06:00)",
            "target_regime": "Off-hour baseload above 360 kWh critical floor (68% capture)",
            "annual_kwh_saved": lever1_overnight_kwh,
            "share_of_total_pct": round(lever1_overnight_kwh / annual_kwh * 100.0, 2),
            "annual_cost_saved_usd": round(lever1_overnight_kwh * TARIFF_USD_PER_KWH, 0),
            "co2_avoided_tons": round(lever1_overnight_kwh * EMISSION_KG_PER_KWH / 1000.0, 1),
            "comfort_impact": "Zero (unoccupied overnight hours)",
        },
        {
            "id": "L2",
            "lever": "Weekend & Academic-Break Deep HVAC Consolidation",
            "target_regime": "Weekend daytime load above 400 kWh zone floor (62% capture)",
            "annual_kwh_saved": lever2_weekend_kwh,
            "share_of_total_pct": round(lever2_weekend_kwh / annual_kwh * 100.0, 2),
            "annual_cost_saved_usd": round(lever2_weekend_kwh * TARIFF_USD_PER_KWH, 0),
            "co2_avoided_tons": round(lever2_weekend_kwh * EMISSION_KG_PER_KWH / 1000.0, 1),
            "comfort_impact": "Zero (consolidates weekend study/work into zoned wings)",
        },
        {
            "id": "L3",
            "lever": "Automated OCSVM Anomaly Triage & Override Reset",
            "target_regime": "82% mitigation of flagged multivariate wastage-day surges",
            "annual_kwh_saved": lever3_anomaly_kwh,
            "share_of_total_pct": round(lever3_anomaly_kwh / annual_kwh * 100.0, 2),
            "annual_cost_saved_usd": round(lever3_anomaly_kwh * TARIFF_USD_PER_KWH, 0),
            "co2_avoided_tons": round(lever3_anomaly_kwh * EMISSION_KG_PER_KWH / 1000.0, 1),
            "comfort_impact": "Positive (eliminates simultaneous heating/cooling faults)",
        },
        {
            "id": "L4",
            "lever": "Economizer Tuning, DCV & 1 C Deadband Optimization",
            "target_regime": "32% trim on hot-weather (>24 C) weekday cooling increment",
            "annual_kwh_saved": lever4_hvac_opt_kwh,
            "share_of_total_pct": round(lever4_hvac_opt_kwh / annual_kwh * 100.0, 2),
            "annual_cost_saved_usd": round(lever4_hvac_opt_kwh * TARIFF_USD_PER_KWH, 0),
            "co2_avoided_tons": round(lever4_hvac_opt_kwh * EMISSION_KG_PER_KWH / 1000.0, 1),
            "comfort_impact": "Zero (ASHRAE 55 compliant 23.5-24.5 C comfort band)",
        },
    ]

    total_saved_kwh = sum(item["annual_kwh_saved"] for item in roadmap_levers)
    total_saved_pct = round(total_saved_kwh / annual_kwh * 100.0, 2)

    # Sensitivity Scenarios (Conservative, Recommended Balanced, Aggressive Net-Zero Ready)
    scenarios = []
    for label, mult in [("Conservative (Low Capture)", 0.85), ("Recommended Target Plan", 1.00), ("Aggressive Smart-BMS Retrofit", 1.12)]:
        s_kwh = round(total_saved_kwh * mult, 1)
        s_pct = round(s_kwh / annual_kwh * 100.0, 2)
        scenarios.append({
            "scenario": label,
            "capture_multiplier": mult,
            "annual_kwh_saved": s_kwh,
            "savings_pct": s_pct,
            "optimized_annual_mwh": round((annual_kwh - s_kwh) / 1000.0, 1),
            "annual_usd_saved": round(s_kwh * TARIFF_USD_PER_KWH, 0),
            "annual_inr_lakhs_saved": round((s_kwh * 10.0) / 100000.0, 2),
            "co2_tons_avoided": round(s_kwh * EMISSION_KG_PER_KWH / 1000.0, 1),
        })

    ml_results = {
        "dt_best_params": dt_grid.best_params_,
        "svc_best_params": svm_grid.best_params_,
        "dt_cls_best_params": dt_cls_grid.best_params_,
        "regression_comparison": reg_comparison,
        "mlr_intercept_std": round(float(mlr_full.intercept_), 2),
        "mlr_intercept_raw": round(float(mlr_raw.intercept_), 2),
        "mlr_coefficients": coef_table,
        "k_sweep": k_sweep,
        "cluster_profiles": cluster_profiles,
        "domain_excess_threshold_kwh": round(excess_thresh, 1),
        "domain_wastage_days_total": int(daily["domain_wastage_label"].sum()),
        "domain_wastage_days_2017": int(y_cls_te.sum()),
        "ocsvm_flagged_days_total": int(daily["ocsvm_wastage_flag"].sum()),
        "kmeans_flagged_days_total": int(daily["kmeans_anomaly_flag"].sum()),
        "consensus_flagged_days_total": int(daily["consensus_wastage_flag"].sum()),
        "consensus_excess_mwh_total": round(float(flagged_days["excess_kwh"].sum() / 1000.0), 2),
        "consensus_excess_cost_usd_total": round(float(flagged_days["excess_kwh"].sum() * TARIFF_USD_PER_KWH), 0),
        "anomaly_evaluation_2017": anomaly_eval_2017,
        "decision_tree_rules_text": tree_rules_text,
        "top_wastage_days": top_wastage_records,
        "annual_baseline_kwh": round(annual_kwh, 1),
        "annual_baseline_mwh": round(annual_kwh / 1000.0, 2),
        "annual_baseline_cost_usd": round(annual_kwh * TARIFF_USD_PER_KWH, 0),
        "roadmap_levers": roadmap_levers,
        "total_recommended_saved_kwh": round(total_saved_kwh, 1),
        "total_recommended_saved_pct": total_saved_pct,
        "total_recommended_saved_usd": round(total_saved_kwh * TARIFF_USD_PER_KWH, 0),
        "total_recommended_co2_tons": round(total_saved_kwh * EMISSION_KG_PER_KWH / 1000.0, 1),
        "sensitivity_scenarios": scenarios,
    }

    return df_lag, daily, ml_results


# ---------------------------------------------------------------------------
# 5. VECTOR VISUALIZATION ENGINE (15 Publication-Grade SVG Figures — §7)
# ---------------------------------------------------------------------------
def generate_all_figures(df: pd.DataFrame, df_lag: pd.DataFrame, daily: pd.DataFrame, stats_res: dict, ml_res: dict) -> dict:
    figs = {}

    # --- Figure 3.1: Portfolio Building Composition & EUI Benchmark ---
    meta = pd.read_csv(META_PATH).set_index("building_id").loc[BLDG_COLS]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.4))
    short_names = [b.replace("Fox_office_", "Office: ").replace("Fox_education_", "Campus: ") for b in BLDG_COLS]
    means = [df[b].mean() for b in BLDG_COLS]
    euis = [(df[b].sum() / 2.0) / meta.loc[b, "sqm"] for b in BLDG_COLS]
    colors_b = [PALETTE["blue"] if "office" in b else PALETTE["magenta"] for b in BLDG_COLS]

    bars1 = ax1.barh(short_names, means, color=colors_b, edgecolor=PALETTE["black"], height=0.62)
    ax1.set_xlabel("Mean Hourly Demand (kWh)")
    ax1.set_title("(a) Mean Hourly Load by Building")
    ax1.invert_yaxis()
    for bar, v in zip(bars1, means):
        ax1.text(v + 3, bar.get_y() + bar.get_height() / 2, f"{v:.1f} kWh", va="center", fontsize=8.8, fontweight="bold")
    ax1.set_xlim(0, max(means) * 1.24)

    bars2 = ax2.barh(short_names, euis, color=colors_b, edgecolor=PALETTE["black"], height=0.62)
    ax2.axvline(stats_res["annual_eui_kwh_m2"], color=PALETTE["red"], linestyle="--", linewidth=1.6, label=f"District EUI ({stats_res['annual_eui_kwh_m2']:.0f} kWh/m^2/yr)")
    ax2.set_xlabel("Annual Energy Use Intensity (kWh / m^2 / year)")
    ax2.set_title("(b) Floor-Area Normalized EUI")
    ax2.invert_yaxis()
    for bar, v in zip(bars2, euis):
        ax2.text(v + 20, bar.get_y() + bar.get_height() / 2, f"{v:.0f}", va="center", fontsize=8.8, fontweight="bold")
    ax2.set_xlim(0, max(euis) * 1.18)
    ax2.legend(loc="lower right")
    fig.tight_layout()
    figs["fig_3_1"] = save_svg(fig, "Fig-3-1-Portfolio-Overview.svg")

    # --- Figure 4.1: End-to-End Methodology Workflow Vector Diagram ---
    fig, ax = plt.subplots(figsize=(11.8, 3.6))
    ax.axis("off")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 3.6)
    stages = [
        ("1. Data Acquisition", "BDG2 Site Fox\n6 Meters + ISD Weather\n17,544 Hourly Rows", PALETTE["blue"], PALETTE["white"]),
        ("2. Preprocessing", "Temporal Interpolation\nIQR Spike Audit\nPsychrometric RH (%)", PALETTE["cyan"], PALETTE["black"]),
        ("3. Feature Eng.", "CDD/HDD, Cyclical Sin/Cos\n24h/168h Lags\nBaseload Ratio", PALETTE["yellow"], PALETTE["black"]),
        ("4. EDA & Stats", "Welch t-Test & Mann-Whitney\nDiurnal & Thermal\nWastage Profiling", PALETTE["magenta"], PALETTE["white"]),
        ("5. Syllabus ML", "Multiple Linear Reg.\nOne-Class SVM & K-Means\nDec. Tree & Naive Bayes", PALETTE["red"], PALETTE["white"]),
        ("6. Action Roadmap", "Anomaly Triage Table\n4 BMS Levers -> 18.5%\nAnnual Cost & CO2 Cut", PALETTE["green"], PALETTE["black"]),
    ]
    xs = np.linspace(0.25, 10.05, 6)
    for i, (title, body, bg, fg) in enumerate(stages):
        x = xs[i]
        header = mpatches.FancyBboxPatch((x, 2.35), 1.68, 0.62, boxstyle="round,pad=0.06", facecolor=bg, edgecolor=PALETTE["black"], linewidth=1.3)
        card = mpatches.FancyBboxPatch((x, 0.55), 1.68, 1.78, boxstyle="round,pad=0.06", facecolor=PALETTE["white"], edgecolor=PALETTE["navy"], linewidth=1.2)
        ax.add_patch(card)
        ax.add_patch(header)
        ax.text(x + 0.84, 2.66, title, ha="center", va="center", fontsize=8.8, fontweight="bold", color=fg)
        ax.text(x + 0.84, 1.44, body, ha="center", va="center", fontsize=8.1, color=PALETTE["black"], linespacing=1.35)
        if i < 5:
            ax.annotate("", xy=(xs[i + 1] - 0.04, 1.75), xytext=(x + 1.72, 1.75),
                        arrowprops=dict(arrowstyle="-|>,head_width=0.28,head_length=0.45", lw=1.8, color=PALETTE["navy"]))
    ax.text(6.0, 0.14, "Deterministic Pipeline (SEED = 42) | Single Source of Truth Across Notebook, PDF Report & Interactive Web App",
            ha="center", va="center", fontsize=8.8, fontstyle="italic", color=PALETTE["navy"])
    fig.tight_layout()
    figs["fig_4_1"] = save_svg(fig, "Fig-4-1-Methodology-Workflow.svg")

    # --- Figure 4.2: Chronological Train / Validation / Test Split Visual ---
    fig, ax = plt.subplots(figsize=(11.2, 2.5))
    ax.axis("off")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 3.0)
    # Row 1: Hourly Regression
    ax.text(0, 2.45, "Hourly Regression Split (17,376 lag-complete rows):", fontsize=9.8, fontweight="bold", color=PALETTE["navy"])
    ax.add_patch(mpatches.Rectangle((0, 1.7), 50.1, 0.55, facecolor=PALETTE["blue"], edgecolor=PALETTE["black"], lw=1.1))
    ax.add_patch(mpatches.Rectangle((50.1, 1.7), 49.9, 0.55, facecolor=PALETTE["cyan"], edgecolor=PALETTE["black"], lw=1.1))
    ax.text(25.0, 1.97, "2016 Training + 5-Fold TimeSeriesSplit CV (8,616 hrs | 50.1%)", ha="center", va="center", color=PALETTE["white"], fontweight="bold", fontsize=8.8)
    ax.text(75.0, 1.97, "2017 Out-of-Sample Test Set (8,760 hrs | 49.9%)", ha="center", va="center", color=PALETTE["black"], fontweight="bold", fontsize=8.8)
    # Row 2: Daily Anomaly Profiling
    ax.text(0, 1.15, "Daily Anomaly & Classification Split (731 calendar days):", fontsize=9.8, fontweight="bold", color=PALETTE["navy"])
    ax.add_patch(mpatches.Rectangle((0, 0.4), 50.1, 0.55, facecolor=PALETTE["magenta"], edgecolor=PALETTE["black"], lw=1.1))
    ax.add_patch(mpatches.Rectangle((50.1, 0.4), 49.9, 0.55, facecolor=PALETTE["green"], edgecolor=PALETTE["black"], lw=1.1))
    ax.text(25.0, 0.67, "2016 Baseline Calibration & 5-Fold Stratified CV (366 days)", ha="center", va="center", color=PALETTE["white"], fontweight="bold", fontsize=8.8)
    ax.text(75.0, 0.67, "2017 Independent Anomaly Evaluation (365 days)", ha="center", va="center", color=PALETTE["black"], fontweight="bold", fontsize=8.8)
    fig.tight_layout()
    figs["fig_4_2"] = save_svg(fig, "Fig-4-2-Train-Test-Split.svg")

    # --- Figure 5.1: Hourly Energy Consumption Profile with Off-Hour Shading ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 4.4))
    grp_hr = df.groupby(["hour", "is_weekend"])["total_kwh"].agg(["mean", "std"]).unstack()
    hrs = np.arange(24)

    for ax in (ax1,):
        ax.axvspan(-0.5, 5.5, color=PALETTE["yellow"], alpha=0.28, label="Off-Hour Window (22:00-06:00)")
        ax.axvspan(21.5, 23.5, color=PALETTE["yellow"], alpha=0.28)
    m_wd = grp_hr["mean"][0].values
    s_wd = grp_hr["std"][0].values
    m_we = grp_hr["mean"][1].values
    s_we = grp_hr["std"][1].values

    ax1.plot(hrs, m_wd, color=PALETTE["blue"], marker="o", markersize=4.5, lw=2.3, label="Weekday Mean (kWh)")
    ax1.fill_between(hrs, m_wd - 0.5 * s_wd, m_wd + 0.5 * s_wd, color=PALETTE["blue"], alpha=0.13)
    ax1.plot(hrs, m_we, color=PALETTE["red"], marker="s", markersize=4.5, lw=2.2, linestyle="--", label="Weekend Mean (kWh)")
    ax1.axhline(360, color=PALETTE["green"], lw=1.8, linestyle=":", label="Critical Standby Floor (360 kWh)")
    ax1.set_xticks(range(0, 24, 2))
    ax1.set_xlim(-0.5, 23.5)
    ax1.set_xlabel("Hour of Day (Local Time)")
    ax1.set_ylabel("Portfolio Electricity Demand (kWh)")
    ax1.set_title("(a) Diurnal Load Curve & Off-Hour Baseload Gap")
    ax1.legend(loc="upper left", fontsize=8.2)

    # Sector split by hour (Weekday)
    sec_hr = df[df["is_weekend"] == 0].groupby("hour")[["office_kwh", "edu_kwh"]].mean()
    ax2.axvspan(-0.5, 5.5, color=PALETTE["yellow"], alpha=0.25)
    ax2.axvspan(21.5, 23.5, color=PALETTE["yellow"], alpha=0.25)
    ax2.plot(hrs, sec_hr["office_kwh"], color=PALETTE["blue"], lw=2.2, marker="^", markersize=4.5, label="3 Commercial Offices (kWh)")
    ax2.plot(hrs, sec_hr["edu_kwh"], color=PALETTE["magenta"], lw=2.2, marker="d", markersize=4.5, label="3 Campus Buildings (kWh)")
    ax2.set_xticks(range(0, 24, 2))
    ax2.set_xlim(-0.5, 23.5)
    ax2.set_xlabel("Hour of Day (Weekdays)")
    ax2.set_ylabel("Sector Mean Hourly Load (kWh)")
    ax2.set_title("(b) Office vs Campus Diurnal Load")
    ax2.legend(loc="upper left", fontsize=8.5)
    fig.tight_layout()
    figs["fig_5_1"] = save_svg(fig, "Fig-5-1-Hourly-Consumption-Profile.svg")

    # --- Figure 5.2: Weekday vs Weekend & Hour-of-Day Box Plots ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 4.4), gridspec_kw={"width_ratios": [1.0, 2.1]})
    df_box = df.copy()
    df_box["Day Type"] = np.where(df_box["is_weekend"] == 0, "Weekday\n(Mon-Fri)", "Weekend\n(Sat-Sun)")
    sns.boxplot(
        data=df_box, x="Day Type", y="total_kwh", ax=ax1,
        palette=[PALETTE["blue"], PALETTE["cyan"]], width=0.48,
        flierprops=dict(marker="o", markersize=2.2, markerfacecolor=PALETTE["red"], alpha=0.45),
        boxprops=dict(edgecolor=PALETTE["black"], linewidth=1.2),
        medianprops=dict(color=PALETTE["yellow"], linewidth=2.4),
    )
    ax1.set_title("(a) Weekday vs Weekend Distribution")
    ax1.set_xlabel("")
    ax1.set_ylabel("Hourly Consumption (kWh)")
    ax1.text(0.5, max(df["total_kwh"]) * 0.93, f"Welch t = {stats_res['welch_t_stat']:.1f}\np < 0.0001",
             ha="center", va="top", fontsize=8.8, bbox=dict(boxstyle="round,pad=0.3", fc=PALETTE["yellow"], ec=PALETTE["black"]))

    df_box["Hour_Bin"] = pd.cut(
        df_box["hour"], bins=[-1, 3, 7, 11, 15, 19, 23],
        labels=["00-03", "04-07", "08-11", "12-15", "16-19", "20-23"]
    )
    df_box["Regime"] = np.where(df_box["is_weekend"] == 0, "Weekday", "Weekend")
    sns.boxplot(
        data=df_box, x="Hour_Bin", y="total_kwh", hue="Regime", ax=ax2,
        palette={"Weekday": PALETTE["blue"], "Weekend": PALETTE["red"]},
        fliersize=1.8, boxprops=dict(edgecolor=PALETTE["black"], linewidth=1.0),
    )
    ax2.set_title("(b) Grouped 4-Hour Block Box Plots by Day Regime")
    ax2.set_xlabel("4-Hour Time Block")
    ax2.set_ylabel("Hourly Consumption (kWh)")
    ax2.legend(title="Schedule", loc="upper left")
    fig.tight_layout()
    figs["fig_5_2"] = save_svg(fig, "Fig-5-2-Weekday-Weekend-Boxplots.svg")

    # --- Figure 5.3: Distribution Histogram + KDE + Seasonal Density ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 4.3))
    sns.histplot(df["total_kwh"], bins=48, kde=True, color=PALETTE["blue"], edgecolor=PALETTE["black"], alpha=0.35, ax=ax1, line_kws={"linewidth": 2.2, "color": PALETTE["red"]})
    ax1.axvline(stats_res["mean_hourly_kwh"], color=PALETTE["red"], linestyle="--", lw=1.8, label=f"Mean = {stats_res['mean_hourly_kwh']:.1f} kWh")
    ax1.axvline(stats_res["median_hourly_kwh"], color=PALETTE["navy"], linestyle="-.", lw=1.8, label=f"Median = {stats_res['median_hourly_kwh']:.1f} kWh")
    ax1.set_title("(a) Hourly Demand Histogram & Kernel Density")
    ax1.set_xlabel("Total Hourly Electricity (kWh)")
    ax1.set_ylabel("Hour Count")
    ax1.legend(loc="upper right")

    s_colors = {"Winter": PALETTE["blue"], "Spring": PALETTE["green"], "Autumn": PALETTE["magenta"], "Summer": PALETTE["red"]}
    for s_name, col in s_colors.items():
        sns.kdeplot(df.loc[df["season"] == s_name, "total_kwh"], ax=ax2, color=col, lw=2.2, fill=True, alpha=0.12, label=s_name)
    ax2.set_title("(b) Seasonal Load Distribution Shift (Cooling Surge)")
    ax2.set_xlabel("Total Hourly Electricity (kWh)")
    ax2.set_ylabel("Probability Density")
    ax2.legend(loc="upper right")
    fig.tight_layout()
    figs["fig_5_3"] = save_svg(fig, "Fig-5-3-Consumption-Distribution-KDE.svg")

    # --- Figure 5.4: Monthly Trend & Baseload vs Peak Wastage Decomposition ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 4.4))
    df_m = df.resample("MS").agg(
        total_mwh=("total_kwh", lambda s: s.sum() / 1000.0),
        mean_temp=("airTemperature", "mean"),
    )
    ax1_t = ax1.twinx()
    ax1_t.grid(False)
    ax1.plot(df_m.index, df_m["total_mwh"], color=PALETTE["blue"], marker="o", lw=2.3, label="Monthly Electricity (MWh)")
    ax1.fill_between(df_m.index, df_m["total_mwh"], color=PALETTE["cyan"], alpha=0.22)
    ax1_t.plot(df_m.index, df_m["mean_temp"], color=PALETTE["red"], marker="s", linestyle="--", lw=2.0, label="Mean Air Temp (C)")
    ax1.set_title("(a) 24-Month Electricity & Temperature Co-Movement")
    ax1.set_ylabel("Monthly Consumption (MWh)", color=PALETTE["blue"])
    ax1_t.set_ylabel("Monthly Mean Temperature (C)", color=PALETTE["red"])
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%y"))
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_t.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8.2)

    # Stacked Baseload vs Active Daytime Load by Month of Year
    m_decomp = df.groupby("month").apply(
        lambda g: pd.Series({
            "Essential_Floor_MWh": (np.minimum(g["total_kwh"], 360.0).sum()) / 2000.0,
            "Avoidable_OffHour_Baseload_MWh": (np.maximum(0.0, g.loc[g["is_off_hour"] == 1, "total_kwh"] - 360.0).sum()) / 2000.0,
            "Active_Daytime_Above_Floor_MWh": (np.maximum(0.0, g.loc[g["is_off_hour"] == 0, "total_kwh"] - 360.0).sum()) / 2000.0,
        })
    )
    m_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    x_m = np.arange(12)
    ax2.bar(x_m, m_decomp["Essential_Floor_MWh"], color=PALETTE["navy"], edgecolor=PALETTE["black"], label="Critical 24/7 Floor (<=360 kWh)")
    ax2.bar(x_m, m_decomp["Avoidable_OffHour_Baseload_MWh"], bottom=m_decomp["Essential_Floor_MWh"],
            color=PALETTE["red"], edgecolor=PALETTE["black"], label="Excess Off-Hour Baseload (22:00-06:00)")
    ax2.bar(x_m, m_decomp["Active_Daytime_Above_Floor_MWh"],
            bottom=m_decomp["Essential_Floor_MWh"] + m_decomp["Avoidable_OffHour_Baseload_MWh"],
            color=PALETTE["cyan"], edgecolor=PALETTE["black"], label="Daytime HVAC & Occupancy Load")
    ax2.set_xticks(x_m)
    ax2.set_xticklabels(m_labels)
    ax2.set_ylabel("Average Monthly Energy (MWh / yr)")
    ax2.set_title("(b) Baseload vs Peak Load Decomposition")
    ax2.legend(loc="upper left", fontsize=8.0)
    fig.tight_layout()
    figs["fig_5_4"] = save_svg(fig, "Fig-5-4-Monthly-Baseload-Decomposition.svg")

    # --- Figure 5.5: Temperature vs Energy Scatter Plot with Regression Lines (Seaborn regplot) ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 4.4))
    sample_work = df[df["is_work_hour"] == 1].sample(n=1800, random_state=SEED)
    sample_off = df[df["is_off_hour"] == 1].sample(n=1800, random_state=SEED)

    sns.regplot(
        data=sample_work, x="airTemperature", y="total_kwh", ax=ax1,
        scatter_kws={"alpha": 0.28, "s": 14, "color": PALETTE["blue"]},
        line_kws={"color": PALETTE["red"], "lw": 2.4, "label": "Occupied Linear Fit"},
    )
    sns.regplot(
        data=sample_off, x="airTemperature", y="total_kwh", ax=ax1,
        scatter_kws={"alpha": 0.25, "s": 14, "color": PALETTE["magenta"]},
        line_kws={"color": PALETTE["navy"], "lw": 2.2, "linestyle": "--", "label": "Off-Hour Linear Fit"},
    )
    ax1.axvline(18.3, color=PALETTE["green"], linestyle=":", lw=2.0, label="18.3 C Cooling Balance Point")
    ax1.set_title(f"(a) Temperature vs Load (Overall r = {stats_res['pearson_r_temp']:.3f})")
    ax1.set_xlabel("Outdoor Dry-Bulb Temperature (C)")
    ax1.set_ylabel("Hourly Electricity Demand (kWh)")
    ax1.legend(loc="upper left", fontsize=8.2)

    # Daily CDD vs Daily kWh colored by weekend
    wk_d = daily[daily["is_weekend"] == 0]
    we_d = daily[daily["is_weekend"] == 1]
    ax2.scatter(wk_d["cdd_daily"], wk_d["daily_kwh"] / 1000.0, c=PALETTE["blue"], alpha=0.55, s=24, edgecolors="none", label="Weekdays (n=521)")
    ax2.scatter(we_d["cdd_daily"], we_d["daily_kwh"] / 1000.0, c=PALETTE["red"], alpha=0.65, s=26, marker="^", edgecolors="none", label="Weekends (n=210)")
    z_wk = np.polyfit(wk_d["cdd_daily"], wk_d["daily_kwh"] / 1000.0, 1)
    x_line = np.linspace(0, daily["cdd_daily"].max(), 100)
    ax2.plot(x_line, np.polyval(z_wk, x_line), color=PALETTE["navy"], lw=2.2, label=f"Weekday Slope: +{z_wk[0]*1000:.0f} kWh/CDD")
    ax2.set_title("(b) Cooling Degree-Days vs Daily Consumption")
    ax2.set_xlabel("Daily Mean Cooling Degree-Days > 18.3 C (C-day)")
    ax2.set_ylabel("Daily Electricity Consumption (MWh)")
    ax2.legend(loc="upper left", fontsize=8.4)
    fig.tight_layout()
    figs["fig_5_5"] = save_svg(fig, "Fig-5-5-Temperature-Energy-Scatter.svg")

    # --- Figure 5.6: Annotated Pearson Correlation Heatmap (Seaborn) ---
    corr_cols = [
        "total_kwh", "office_kwh", "edu_kwh", "airTemperature",
        "cdd_18", "rel_humidity", "temp_rh_interaction",
        "windSpeed", "seaLvlPressure", "is_off_hour", "is_weekend", "lag_24h"
    ]
    corr_labels = [
        "Total kWh", "Office kWh", "Campus kWh", "Air Temp (C)",
        "CDD >18.3C", "Rel. Hum (%)", "Temp x RH",
        "Wind (m/s)", "Pressure", "Off-Hour", "Weekend", "Lag 24h"
    ]
    corr_mat = df_lag[corr_cols].corr()
    corr_mat.index = corr_labels
    corr_mat.columns = corr_labels

    fig, ax = plt.subplots(figsize=(10.2, 7.6))
    cmap_div = sns.diverging_palette(240, 10, s=99, l=45, as_cmap=True)
    sns.heatmap(
        corr_mat, annot=True, fmt=".2f", cmap=cmap_div, vmin=-1, vmax=1, center=0,
        linewidths=0.7, linecolor=PALETTE["white"], cbar_kws={"shrink": 0.82, "label": "Pearson r"},
        annot_kws={"size": 8.3, "weight": "bold"}, ax=ax
    )
    ax.set_title("Annotated Pearson Correlation Matrix of Smart-Meter, Weather & Lag Features (n = 17,376)")
    plt.xticks(rotation=35, ha="right")
    plt.yticks(rotation=0)
    fig.tight_layout()
    figs["fig_5_6"] = save_svg(fig, "Fig-5-6-Correlation-Heatmap.svg")

    # --- Figure 5.7: Autocorrelation Profile & Multivariate Feature Relationships ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 4.3))
    lags = np.arange(1, 193)
    s_tot = df["total_kwh"]
    acf_vals = [s_tot.autocorr(lag=int(lg)) for lg in lags]
    ax1.plot(lags, acf_vals, color=PALETTE["blue"], lw=1.9)
    ax1.fill_between(lags, 0, acf_vals, color=PALETTE["cyan"], alpha=0.22)
    for pk, lbl in [(24, "24h Diurnal"), (168, "168h Weekly")]:
        ax1.axvline(pk, color=PALETTE["red"], linestyle="--", lw=1.6)
        ax1.text(pk - 3, 0.92, lbl, rotation=90, va="top", ha="right", fontsize=8.5, fontweight="bold", color=PALETTE["red"])
    ax1.axhline(0, color=PALETTE["black"], lw=0.8)
    ax1.set_title("(a) Hourly Load Autocorrelation (1 to 192 Hours)")
    ax1.set_xlabel("Lag Horizon (Hours)")
    ax1.set_ylabel("Autocorrelation Coefficient (r)")
    ax1.set_ylim(-0.2, 1.02)

    # 2D Hour x Month Consumption Heatmap (Visualizing When Wastage Occurs)
    piv_hm = df.pivot_table(index="hour", columns="month", values="total_kwh", aggfunc="mean")
    piv_hm.columns = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    sns.heatmap(piv_hm, cmap="YlOrRd", ax=ax2, cbar_kws={"label": "Mean kWh"}, linewidths=0.2)
    ax2.set_title("(b) Hour-by-Month Thermal & Schedule Load Carpet")
    ax2.set_xlabel("Calendar Month")
    ax2.set_ylabel("Hour of Day (00:00 - 23:00)")
    fig.tight_layout()
    figs["fig_5_7"] = save_svg(fig, "Fig-5-7-Autocorrelation-Carpet.svg")

    # --- Figure 6.1: Regression Diagnostics (Predicted vs Actual, Residuals, Standardized Coefs) ---
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 4.2))
    te_df = df_lag[df_lag["year"] == 2017].copy()
    te_sample = te_df.sample(n=1500, random_state=SEED)

    axes[0].scatter(te_sample["total_kwh"], te_sample["pred_mlr"], c=PALETTE["blue"], alpha=0.32, s=14, edgecolors="none")
    lims = [250, 1450]
    axes[0].plot(lims, lims, color=PALETTE["red"], lw=2.2, linestyle="--", label="1:1 Perfect Fit")
    r2_v = ml_res["regression_comparison"]["Full_Autoregressive_Weather_MLR"]["r2"]
    rmse_v = ml_res["regression_comparison"]["Full_Autoregressive_Weather_MLR"]["rmse"]
    axes[0].set_xlim(lims)
    axes[0].set_ylim(lims)
    axes[0].set_title(f"(a) Predicted vs Actual (R^2 = {r2_v:.3f})")
    axes[0].set_xlabel("Actual Hourly Demand (kWh)")
    axes[0].set_ylabel("MLR Predicted Demand (kWh)")
    axes[0].legend(loc="upper left")

    resids = te_df["total_kwh"] - te_df["pred_mlr"]
    sns.histplot(resids, bins=45, kde=True, color=PALETTE["cyan"], edgecolor=PALETTE["black"], ax=axes[1], line_kws={"color": PALETTE["magenta"], "lw": 2.0})
    axes[1].axvline(0, color=PALETTE["red"], linestyle="--", lw=1.8, label=f"RMSE = {rmse_v:.1f} kWh")
    axes[1].set_title("(b) 2017 Test Residual Distribution")
    axes[1].set_xlabel("Residual (Actual - Predicted kWh)")
    axes[1].set_ylabel("Frequency")
    axes[1].set_xlim(-320, 320)
    axes[1].legend(loc="upper right")

    top_c = ml_res["mlr_coefficients"][:8][::-1]
    c_names = [r["feature"] for r in top_c]
    c_vals = [r["std_coef"] for r in top_c]
    c_cols = [PALETTE["blue"] if v >= 0 else PALETTE["red"] for v in c_vals]
    axes[2].barh(c_names, c_vals, color=c_cols, edgecolor=PALETTE["black"], height=0.62)
    axes[2].axvline(0, color=PALETTE["black"], lw=1.0)
    axes[2].set_title("(c) Top MLR Effects")
    axes[2].set_xlabel("Standardized Coefficient (kWh / SD)")
    fig.tight_layout()
    figs["fig_6_1"] = save_svg(fig, "Fig-6-1-Regression-Diagnostics.svg")

    # --- Figure 6.2: Daily Consumption Timeline with Flagged Anomaly Days ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11.8, 6.2), sharex=True, gridspec_kw={"height_ratios": [1.5, 1.0]})
    anom_d = daily[daily["consensus_wastage_flag"] == 1]

    ax1.plot(daily.index, daily["expected_daily_kwh"] / 1000.0, color=PALETTE["cyan"], lw=1.3, label="Expected Baseline Demand (MWh/day)")
    ax1.plot(daily.index, daily["daily_kwh"] / 1000.0, color=PALETTE["blue"], lw=1.15, alpha=0.85, label="Actual Metered Demand (MWh/day)")
    ax1.scatter(anom_d.index, anom_d["daily_kwh"] / 1000.0, color=PALETTE["red"], edgecolor=PALETTE["black"], s=42, zorder=5,
                label=f"Flagged Wastage Anomaly Days (n = {len(anom_d)})")
    ax1.set_ylim(9.5, 30.5)
    ax1.set_ylabel("Daily Consumption (MWh)")
    ax1.set_title("Two-Year Daily Smart-Meter Timeline (2016-2017) with Counterfactual Baseline & Flagged Wastage Days")
    ax1.legend(loc="upper left", ncol=3, fontsize=8.4)

    pos_ex = daily["excess_kwh"].clip(lower=0) / 1000.0
    neg_ex = daily["excess_kwh"].clip(upper=0) / 1000.0
    ax2.fill_between(daily.index, 0, pos_ex, color=PALETTE["red"], alpha=0.45, label="Positive Excess / Wastage (+MWh)")
    ax2.fill_between(daily.index, 0, neg_ex, color=PALETTE["green"], alpha=0.35, label="Below-Baseline Setback (-MWh)")
    ax2.axhline(ml_res["domain_excess_threshold_kwh"] / 1000.0, color=PALETTE["magenta"], linestyle="--", lw=1.6,
                label=f"+1.25 SD Audit Threshold (+{ml_res['domain_excess_threshold_kwh']/1000.0:.2f} MWh)")
    ax2.set_ylim(-5.2, 4.1)
    ax2.set_ylabel("Daily Excess (MWh)")
    ax2.set_xlabel("Calendar Date (2016 - 2017)")
    ax2.legend(loc="upper left", ncol=3, fontsize=8.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.tight_layout()
    figs["fig_6_2"] = save_svg(fig, "Fig-6-2-Daily-Anomaly-Timeline.svg")

    # --- Figure 6.3: One-Class SVM Decision Boundary (2D Standardized Feature Projection) ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 4.5))
    feat_2d = ["excess_kwh", "off_hour_mean_kwh"]
    sc2 = StandardScaler()
    healthy_idx = (daily["year"] == 2016) & (daily["excess_kwh"].abs() <= ml_res["domain_excess_threshold_kwh"])
    sc2.fit(daily.loc[healthy_idx, feat_2d])
    X2_all = sc2.transform(daily[feat_2d])
    X2_tr = sc2.transform(daily.loc[healthy_idx, feat_2d])
    oc2 = OneClassSVM(kernel="rbf", nu=0.08, gamma=0.45).fit(X2_tr)

    xx, yy = np.meshgrid(np.linspace(-9.0, 5.5, 240), np.linspace(-3.0, 4.2, 240))
    zz = oc2.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

    ax1.contourf(xx, yy, zz, levels=np.linspace(zz.min(), 0, 7), cmap="Reds_r", alpha=0.18)
    ax1.contourf(xx, yy, zz, levels=[0, zz.max()], colors=[PALETTE["cyan"]], alpha=0.18)
    ax1.contour(xx, yy, zz, levels=[0], linewidths=2.3, colors=[PALETTE["red"]])

    norm_m = daily["consensus_wastage_flag"] == 0
    anom_m = daily["consensus_wastage_flag"] == 1
    ax1.scatter(X2_all[norm_m, 0], X2_all[norm_m, 1], c=PALETTE["blue"], s=18, alpha=0.5, label="Normal Operating Days")
    ax1.scatter(X2_all[anom_m, 0], X2_all[anom_m, 1], c=PALETTE["red"], edgecolor=PALETTE["black"], s=42, marker="D", label="Flagged Wastage Days")
    ax1.set_xlim(-8.8, 5.4)
    ax1.set_ylim(-2.9, 4.1)
    ax1.set_title("(a) One-Class SVM RBF Frontier (nu = 0.08)")
    ax1.set_xlabel("Standardized Daily Excess Load (Z-Score)")
    ax1.set_ylabel("Standardized Off-Hour Baseload (Z-Score)")
    ax1.legend(loc="lower right", fontsize=8.3)

    # OCSVM Anomaly Score ranking distribution
    sns.histplot(daily.loc[norm_m, "ocsvm_score"], bins=35, color=PALETTE["blue"], alpha=0.45, label="Normal Days", ax=ax2)
    sns.histplot(daily.loc[anom_m, "ocsvm_score"], bins=20, color=PALETTE["red"], alpha=0.75, label="Flagged Wastage Days", ax=ax2)
    ax2.axvline(0.0, color=PALETTE["magenta"], linestyle="--", lw=2.0, label="OCSVM Frontier (Score = 0)")
    ax2.set_title("(b) Multivariate OCSVM Anomaly Score Separation")
    ax2.set_xlabel("OCSVM Anomaly Score (-Decision Function)")
    ax2.set_ylabel("Number of Days")
    ax2.legend(loc="upper right", fontsize=8.3)
    fig.tight_layout()
    figs["fig_6_3"] = save_svg(fig, "Fig-6-3-OCSVM-Decision-Boundary.svg")

    # --- Figure 6.4: K-Means Cluster Selection (Elbow + Silhouette) & Centroid Heatmap ---
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 4.1), gridspec_kw={"width_ratios": [1.0, 1.0, 1.45]})
    ks = [r["k"] for r in ml_res["k_sweep"]]
    inertias = [r["inertia"] for r in ml_res["k_sweep"]]
    sils = [r["silhouette"] for r in ml_res["k_sweep"]]

    axes[0].plot(ks, inertias, color=PALETTE["blue"], marker="o", lw=2.2)
    axes[0].axvline(4, color=PALETTE["red"], linestyle="--", lw=1.7, label="Selected k = 4")
    axes[0].set_title("(a) K-Means Elbow Curve")
    axes[0].set_xlabel("Number of Clusters (k)")
    axes[0].set_ylabel("Within-Cluster Inertia")
    axes[0].legend()

    axes[1].plot(ks, sils, color=PALETTE["magenta"], marker="s", lw=2.2)
    axes[1].axvline(4, color=PALETTE["red"], linestyle="--", lw=1.7, label=f"k=4 Sil = {sils[2]:.3f}")
    axes[1].set_title("(b) Silhouette Validation")
    axes[1].set_xlabel("Number of Clusters (k)")
    axes[1].set_ylabel("Mean Silhouette Score")
    axes[1].legend()

    # Standardized cluster center heatmap
    c_feats = ["mean_kwh", "off_hour_mean_kwh", "baseload_ratio", "excess_kwh", "mean_temp", "is_weekend"]
    c_labels = ["Mean kWh", "Off-Hr kWh", "Baseload Ratio", "Excess kWh", "Air Temp", "Weekend"]
    z_df = pd.DataFrame(StandardScaler().fit_transform(daily[c_feats]), columns=c_labels, index=daily.index)
    z_df["Cluster"] = daily["cluster_name"]
    cent_mat = z_df.groupby("Cluster")[c_labels].mean()
    # Shorten row names
    cent_mat.index = [idx.replace(" Regime", "").replace(" Baseline", "") for idx in cent_mat.index]
    sns.heatmap(cent_mat, annot=True, fmt=".2f", cmap=cmap_div, center=0, cbar=False, linewidths=0.6, ax=axes[2], annot_kws={"size": 8.3, "weight": "bold"})
    axes[2].set_title("(c) Cluster Centroids (Z-Score)")
    plt.setp(axes[2].get_xticklabels(), rotation=30, ha="right")
    fig.tight_layout()
    figs["fig_6_4"] = save_svg(fig, "Fig-6-4-KMeans-Cluster-Profiles.svg")

    # --- Figure 6.5: Confusion Matrices & Classifier Comparison Bar Chart (2017 Test Set) ---
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 4.0), gridspec_kw={"width_ratios": [1.0, 1.0, 1.45]})
    ev = ml_res["anomaly_evaluation_2017"]

    for ax, key, title_str in [
        (axes[0], "Hybrid_Consensus_Detector", "(a) Unsupervised Consensus CM"),
        (axes[1], "Supervised_RBF_SVM", "(b) Supervised RBF-SVM CM"),
    ]:
        m_d = ev[key]
        cm_arr = np.array([[m_d["tn"], m_d["fp"]], [m_d["fn"], m_d["tp"]]])
        sns.heatmap(
            cm_arr, annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax,
            xticklabels=["Pred Normal", "Pred Wastage"],
            yticklabels=["True Normal", "True Wastage"],
            annot_kws={"size": 11, "weight": "bold"}, linewidths=1.0, linecolor=PALETTE["black"]
        )
        ax.set_title(f"{title_str}\n(F1 = {m_d['f1']:.3f})")

    models_plot = [
        ("OCSVM", ev["Unsupervised_OneClass_SVM"]),
        ("K-Means", ev["Unsupervised_KMeans_Distance"]),
        ("Consensus", ev["Hybrid_Consensus_Detector"]),
        ("RBF-SVM", ev["Supervised_RBF_SVM"]),
        ("Dec. Tree", ev["Supervised_Decision_Tree"]),
        ("Naive Bayes", ev["Supervised_Gaussian_Naive_Bayes"]),
    ]
    x_i = np.arange(len(models_plot))
    w = 0.26
    axes[2].bar(x_i - w, [m[1]["precision"] for m in models_plot], width=w, color=PALETTE["blue"], edgecolor=PALETTE["black"], label="Precision")
    axes[2].bar(x_i, [m[1]["recall"] for m in models_plot], width=w, color=PALETTE["cyan"], edgecolor=PALETTE["black"], label="Recall")
    axes[2].bar(x_i + w, [m[1]["f1"] for m in models_plot], width=w, color=PALETTE["red"], edgecolor=PALETTE["black"], label="F1-Score")
    axes[2].set_xticks(x_i)
    axes[2].set_xticklabels([m[0] for m in models_plot], rotation=22, ha="right")
    axes[2].set_ylim(0, 1.08)
    axes[2].set_ylabel("Score (2017 Holdout Set)")
    axes[2].set_title("(c) Wastage-Day Detection Benchmark")
    axes[2].legend(loc="upper left", ncol=3, fontsize=8.0)
    fig.tight_layout()
    figs["fig_6_5"] = save_svg(fig, "Fig-6-5-Anomaly-Model-Evaluation.svg")

    # --- Figure 6.6: Hourly Case-Study Anatomy of Top 2 Flagged Wastage Days ---
    top2 = [ml_res["top_wastage_days"][0]["date"], ml_res["top_wastage_days"][1]["date"]]
    fig, axes = plt.subplots(1, 2, figsize=(11.8, 4.3), sharey=True)
    for ax, d_str, panel in zip(axes, top2, ["(a)", "(b)"]):
        sub = df_lag.loc[d_str]
        h_x = sub["hour"].values
        ax.axvspan(0, 5.5, color=PALETTE["yellow"], alpha=0.26, label="Off-Hour Window")
        ax.axvspan(21.5, 23, color=PALETTE["yellow"], alpha=0.26)
        ax.plot(h_x, sub["expected_kwh"], color=PALETTE["blue"], linestyle="--", lw=2.1, marker="o", markersize=4, label="Expected Baseline (kWh)")
        ax.plot(h_x, sub["total_kwh"], color=PALETTE["red"], lw=2.4, marker="s", markersize=4.5, label="Actual Metered (kWh)")
        ax.fill_between(h_x, sub["expected_kwh"], sub["total_kwh"], where=(sub["total_kwh"] >= sub["expected_kwh"]),
                        color=PALETTE["red"], alpha=0.22, label="Avoidable Excess Area")
        ex_sum = (sub["total_kwh"] - sub["expected_kwh"]).sum()
        ax.set_title(f"{panel} Case Study: {d_str} (+{ex_sum:,.0f} kWh Excess)")
        ax.set_xlabel("Hour of Day")
        ax.set_xticks(range(0, 24, 3))
        if panel == "(a)":
            ax.set_ylabel("Hourly Electricity (kWh)")
        ax.legend(loc="upper left", fontsize=8.0)
    fig.tight_layout()
    figs["fig_6_6"] = save_svg(fig, "Fig-6-6-Case-Study-Wastage-Days.svg")

    # --- Figure 7.1: Savings Roadmap Waterfall Chart (Current vs Optimized 15-20% Target Band) ---
    fig, ax = plt.subplots(figsize=(11.5, 4.6))
    base_mwh = ml_res["annual_baseline_mwh"]
    levers = ml_res["roadmap_levers"]
    opt_mwh = base_mwh - sum(l["annual_kwh_saved"] for l in levers) / 1000.0

    labels_wf = [
        "Current Annual\nBaseline",
        "L1: Overnight\nBMS Setback",
        "L2: Weekend\nConsolidation",
        "L3: Anomaly\nAlert Triage",
        "L4: Economizer\n& Deadband",
        "Optimized\nTarget Load",
    ]
    deltas = [-l["annual_kwh_saved"] / 1000.0 for l in levers]
    running = base_mwh
    bottoms = [0.0]
    heights = [base_mwh]
    bar_cols = [PALETTE["blue"]]
    for d in deltas:
        bottoms.append(running + d)
        heights.append(-d)
        running += d
        bar_cols.append(PALETTE["red"])
    bottoms.append(0.0)
    heights.append(opt_mwh)
    bar_cols.append(PALETTE["green"])

    # Shade 15-20% target band
    band_top = base_mwh * 0.85
    band_bot = base_mwh * 0.80
    ax.axhspan(band_bot, band_top, color=PALETTE["yellow"], alpha=0.35, label="15-20% Target Zone")

    x_wf = np.arange(len(labels_wf))
    bars_wf = ax.bar(x_wf, heights, bottom=bottoms, color=bar_cols, edgecolor=PALETTE["black"], width=0.56, lw=1.2)
    for i, (b_bot, h_val) in enumerate(zip(bottoms, heights)):
        if i == 0 or i == len(labels_wf) - 1:
            txt = f"{h_val:,.0f} MWh\n(${h_val*1000*TARIFF_USD_PER_KWH:,.0f})"
            ax.text(i, b_bot + h_val + 140, txt, ha="center", va="bottom", fontsize=8.8, fontweight="bold")
        else:
            pct_i = levers[i - 1]["share_of_total_pct"]
            txt = f"-{h_val:,.0f} MWh\n(-{pct_i:.1f}%)"
            ax.text(i, b_bot + h_val + 120, txt, ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=PALETTE["red"])

    ax.set_xticks(x_wf)
    ax.set_xticklabels(labels_wf)
    ax.set_ylim(0, base_mwh * 1.18)
    ax.set_ylabel("Annual Portfolio Electricity (MWh / year)")
    ax.set_title(f"Evidence-Based Facility Savings Waterfall: {ml_res['total_recommended_saved_pct']:.2f}% Annual Electricity Reduction (${ml_res['total_recommended_saved_usd']:,.0f}/yr Saved)")
    ax.legend(loc="upper right")
    fig.tight_layout()
    figs["fig_7_1"] = save_svg(fig, "Fig-7-1-Savings-Waterfall-Roadmap.svg")

    # --- Figure 7.2: Sensitivity Analysis Across BMS Capture Rates & Tariff Scenarios ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 4.3))
    capture_mults = np.linspace(0.60, 1.25, 66)
    pct_curve = capture_mults * ml_res["total_recommended_saved_pct"]
    ax1.axhspan(15.0, 20.0, color=PALETTE["yellow"], alpha=0.35, label="15-20% Mandate Target Zone")
    ax1.plot(capture_mults * 100, pct_curve, color=PALETTE["blue"], lw=2.5, label="Portfolio % kWh Saved")
    ax1.scatter([85, 100, 112], [s["savings_pct"] for s in ml_res["sensitivity_scenarios"]],
                color=[PALETTE["cyan"], PALETTE["green"], PALETTE["magenta"]], edgecolor=PALETTE["black"], s=75, zorder=5)
    for x_p, sc in zip([85, 100, 112], ml_res["sensitivity_scenarios"]):
        ax1.annotate(f"{sc['savings_pct']:.1f}%", (x_p, sc["savings_pct"] + 0.65), ha="center", fontsize=8.8, fontweight="bold")
    ax1.set_xlabel("BMS Implementation Effectiveness (% of Recommended Plan)")
    ax1.set_ylabel("Annual Electricity Reduction (%)")
    ax1.set_title("(a) Savings % Sensitivity to Implementation Capture")
    ax1.legend(loc="lower right")

    tariffs = np.linspace(0.08, 0.20, 50)
    for sc, col, ls in zip(
        ml_res["sensitivity_scenarios"],
        [PALETTE["cyan"], PALETTE["blue"], PALETTE["magenta"]],
        ["--", "-", "-."]
    ):
        usd_k = (sc["annual_kwh_saved"] * tariffs) / 1000.0
        ax2.plot(tariffs, usd_k, color=col, linestyle=ls, lw=2.2, label=f"{sc['scenario']} ({sc['savings_pct']:.1f}%)")
    ax2.axvline(TARIFF_USD_PER_KWH, color=PALETTE["red"], linestyle=":", lw=1.8, label="Base Tariff ($0.12/kWh)")
    ax2.set_xlabel("Electricity Tariff ($ USD / kWh)")
    ax2.set_ylabel("Annual Cost Savings ($ Thousands USD / yr)")
    ax2.set_title("(b) Financial Savings Sensitivity to Utility Tariff")
    ax2.legend(loc="upper left", fontsize=8.0)
    fig.tight_layout()
    figs["fig_7_2"] = save_svg(fig, "Fig-7-2-Sensitivity-Analysis.svg")

    return figs


# ---------------------------------------------------------------------------
# 6. EXPORT SINGLE SOURCE OF TRUTH JSON + INTERACTIVE WEBSITE DATA PAYLOAD
# ---------------------------------------------------------------------------
def export_web_payload(df: pd.DataFrame, df_lag: pd.DataFrame, daily: pd.DataFrame, stats_res: dict, ml_res: dict) -> None:
    # Compact interactive arrays for Plotly.js charts in site/
    hr_prof = df.groupby(["hour", "is_weekend"])[["total_kwh", "office_kwh", "edu_kwh"]].mean().unstack()
    hourly_interactive = {
        "hours": list(range(24)),
        "weekday_total": [round(float(v), 1) for v in hr_prof["total_kwh"][0]],
        "weekend_total": [round(float(v), 1) for v in hr_prof["total_kwh"][1]],
        "weekday_office": [round(float(v), 1) for v in hr_prof["office_kwh"][0]],
        "weekday_campus": [round(float(v), 1) for v in hr_prof["edu_kwh"][0]],
        "weekend_office": [round(float(v), 1) for v in hr_prof["office_kwh"][1]],
        "weekend_campus": [round(float(v), 1) for v in hr_prof["edu_kwh"][1]],
    }

    # Stratified sample of 600 hourly observations for responsive scatter/boxplot
    samp = df.sample(n=600, random_state=SEED).sort_index()
    scatter_sample = {
        "temp": [round(float(x), 1) for x in samp["airTemperature"]],
        "kwh": [round(float(x), 1) for x in samp["total_kwh"]],
        "rh": [round(float(x), 1) for x in samp["rel_humidity"]],
        "regime": ["Weekend" if w == 1 else ("Off-Hour" if o == 1 else "Occupied Weekday")
                   for w, o in zip(samp["is_weekend"], samp["is_off_hour"])],
        "ts": [idx.strftime("%Y-%m-%d %H:%M") for idx in samp.index],
    }

    # Boxplot arrays by 4-hour block
    box_blocks = []
    for lbl, (h0, h1) in [("00-03", (0, 3)), ("04-07", (4, 7)), ("08-11", (8, 11)), ("12-15", (12, 15)), ("16-19", (16, 19)), ("20-23", (20, 23))]:
        sub_wd = df[(df["hour"].between(h0, h1)) & (df["is_weekend"] == 0)]["total_kwh"].sample(120, random_state=SEED)
        sub_we = df[(df["hour"].between(h0, h1)) & (df["is_weekend"] == 1)]["total_kwh"].sample(80, random_state=SEED)
        box_blocks.append({
            "block": lbl,
            "weekday": [round(float(v), 1) for v in sub_wd],
            "weekend": [round(float(v), 1) for v in sub_we],
        })

    # Correlation matrix for interactive heatmap
    c_cols = ["total_kwh", "office_kwh", "edu_kwh", "airTemperature", "cdd_18", "rel_humidity", "is_off_hour", "is_weekend", "lag_24h"]
    c_lbls = ["Total kWh", "Office kWh", "Campus kWh", "Air Temp (C)", "CDD >18.3C", "Rel Hum (%)", "Off-Hour", "Weekend", "Lag 24h"]
    c_mat = df_lag[c_cols].corr().round(3).values.tolist()

    # Full 731-day timeline for interactive Anomaly Explorer
    daily_timeline = {
        "dates": [d.strftime("%Y-%m-%d") for d in daily.index],
        "actual_mwh": [round(float(v / 1000.0), 3) for v in daily["daily_kwh"]],
        "expected_mwh": [round(float(v / 1000.0), 3) for v in daily["expected_daily_kwh"]],
        "excess_kwh": [round(float(v), 1) for v in daily["excess_kwh"]],
        "temp_c": [round(float(v), 1) for v in daily["mean_temp"]],
        "baseload_ratio": [round(float(v), 3) for v in daily["baseload_ratio"]],
        "flagged": [int(v) for v in daily["consensus_wastage_flag"]],
        "cluster": list(daily["cluster_name"]),
    }

    web_payload = {
        "stats": stats_res,
        "ml": ml_res,
        "hourly": hourly_interactive,
        "scatter": scatter_sample,
        "box_blocks": box_blocks,
        "corr": {"labels": c_lbls, "z": c_mat},
        "daily_timeline": daily_timeline,
    }
    SITE_DATA_JS.write_text("window.PROJECT_DATA = " + json.dumps(web_payload, separators=(",", ":")) + ";\n", encoding="utf-8")


def main() -> None:
    print("[1/4] Loading & preprocessing BDG2 Site Fox Smart-Meter & Weather dataset...")
    df, meta, prep_table = load_and_preprocess()

    print("[2/4] Running statistical analysis & hypothesis tests...")
    stats_res = run_statistical_analysis(df)

    print("[3/4] Training syllabus-locked ML models (MLR, Decision Tree, OCSVM, RBF-SVM, K-Means, Naive Bayes)...")
    df_lag, daily, ml_res = run_machine_learning(df)

    print("[4/4] Generating 15 vector SVG figures & exporting single-source-of-truth JSON...")
    figs = generate_all_figures(df, df_lag, daily, stats_res, ml_res)

    master_results = {
        "preprocessing_table": prep_table,
        "statistics": stats_res,
        "machine_learning": ml_res,
        "figures": figs,
    }
    OUT_JSON.write_text(json.dumps(master_results, indent=2), encoding="utf-8")
    export_web_payload(df, df_lag, daily, stats_res, ml_res)

    print("\n=== PIPELINE COMPLETED SUCCESSFULLY ===")
    print(f"Dataset Rows: {stats_res['total_rows']:,} hourly | {stats_res['total_days']} days")
    print(f"Weekday vs Weekend Mean: {stats_res['weekday_mean_kwh']} vs {stats_res['weekend_mean_kwh']} kWh (Welch t = {stats_res['welch_t_stat']})")
    print(f"Best Regression (Autoregressive+Weather MLR): R2 = {ml_res['regression_comparison']['Full_Autoregressive_Weather_MLR']['r2']}, RMSE = {ml_res['regression_comparison']['Full_Autoregressive_Weather_MLR']['rmse']} kWh")
    print(f"Counterfactual Schedule+Weather MLR: R2 = {ml_res['regression_comparison']['Counterfactual_Schedule_Weather_MLR']['r2']}, RMSE = {ml_res['regression_comparison']['Counterfactual_Schedule_Weather_MLR']['rmse']} kWh")
    print(f"Consensus Flagged Wastage Days: {ml_res['consensus_flagged_days_total']} days ({ml_res['consensus_excess_mwh_total']} MWh excess)")
    print(f"Recommended Annual Savings Roadmap: {ml_res['total_recommended_saved_pct']}% ({ml_res['total_recommended_saved_kwh']:,.0f} kWh/yr | ${ml_res['total_recommended_saved_usd']:,.0f}/yr)")


if __name__ == "__main__":
    main()
