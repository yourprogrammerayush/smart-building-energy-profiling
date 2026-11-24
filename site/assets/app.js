/* ==========================================================================
   Smart Building Energy Wastage & Anomaly Profiling — Interactive App Logic
   Reads single-source-of-truth metrics from window.PROJECT_DATA (SEED = 42)
   ========================================================================== */

(function () {
  "use strict";

  const state = {
    theme: localStorage.getItem("iilm_energy_theme") || "light",
    sector: "total",
    timelineYear: "all",
    clusterFilter: "all",
  };

  // Base annual reducible kWh pools (exact mathematical match to Python pipeline)
  const BASE_ANNUAL_KWH = 6838632.78;
  const BASE_POOLS = {
    l1_raw: 461457.16 / 0.68,
    l2_raw: 339534.26 / 0.62,
    l3_raw: 95544.07 / 0.82,
    l4_raw: 368586.94 / 0.32,
  };

  function applyTheme(theme) {
    state.theme = theme;
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("iilm_energy_theme", theme);
    const icon = document.getElementById("themeIcon");
    const label = document.getElementById("themeLabel");
    if (icon && label) {
      if (theme === "dark") {
        icon.innerHTML = "&#9728;";
        label.textContent = "Light";
      } else {
        icon.innerHTML = "&#9790;";
        label.textContent = "Dark";
      }
    }
    if (window.Plotly && window.PROJECT_DATA) {
      renderAllCharts();
    }
  }

  function plotlyLayoutBase(extra) {
    const isDark = state.theme === "dark";
    const base = {
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      font: {
        family: "Inter, -apple-system, sans-serif",
        color: isDark ? "#e2e8f0" : "#0b1f3a",
        size: 12,
      },
      margin: { t: 22, r: 18, b: 46, l: 54 },
      xaxis: {
        gridcolor: isDark ? "#1e293b" : "#e2e8f0",
        zerolinecolor: isDark ? "#334155" : "#cbd5e1",
      },
      yaxis: {
        gridcolor: isDark ? "#1e293b" : "#e2e8f0",
        zerolinecolor: isDark ? "#334155" : "#cbd5e1",
      },
      legend: {
        orientation: "h",
        yanchor: "bottom",
        y: 1.02,
        xanchor: "left",
        x: 0,
        font: { size: 11 },
      },
    };
    return Object.assign({}, base, extra || {});
  }

  const PLOT_CFG = { responsive: true, displaylogo: false, modeBarButtonsToRemove: ["lasso2d", "select2d"] };

  // 1. Diurnal Load Profile
  function renderDiurnal() {
    const d = window.PROJECT_DATA.hourly;
    let wd, we, floorVal, yTitle;
    if (state.sector === "office") {
      wd = d.weekday_office;
      we = d.weekend_office;
      floorVal = 175;
      yTitle = "3 Offices Mean Load (kWh)";
    } else if (state.sector === "campus") {
      wd = d.weekday_campus;
      we = d.weekend_campus;
      floorVal = 185;
      yTitle = "3 Campus Bldgs Mean Load (kWh)";
    } else {
      wd = d.weekday_total;
      we = d.weekend_total;
      floorVal = 360;
      yTitle = "Portfolio Mean Load (kWh)";
    }

    const traces = [
      {
        x: d.hours,
        y: wd,
        mode: "lines+markers",
        name: "Weekday Mean",
        line: { color: "#0044ff", width: 3 },
        marker: { size: 6 },
      },
      {
        x: d.hours,
        y: we,
        mode: "lines+markers",
        name: "Weekend Mean",
        line: { color: "#ff0000", width: 2.5, dash: "dash" },
        marker: { size: 6, symbol: "square" },
      },
      {
        x: [0, 23],
        y: [floorVal, floorVal],
        mode: "lines",
        name: "Critical Standby Floor (" + floorVal + " kWh)",
        line: { color: "#059669", width: 2.2, dash: "dot" },
      },
    ];

    const layout = plotlyLayoutBase({
      xaxis: Object.assign({}, plotlyLayoutBase().xaxis, { title: "Hour of Day (00:00 – 23:00)", dtick: 3 }),
      yaxis: Object.assign({}, plotlyLayoutBase().yaxis, { title: yTitle }),
      shapes: [
        { type: "rect", xref: "x", yref: "paper", x0: 0, x1: 5.5, y0: 0, y1: 1, fillcolor: "rgba(255, 225, 0, 0.16)", line: { width: 0 } },
        { type: "rect", xref: "x", yref: "paper", x0: 21.5, x1: 23, y0: 0, y1: 1, fillcolor: "rgba(255, 225, 0, 0.16)", line: { width: 0 } },
      ],
    });
    Plotly.react("chartDiurnal", traces, layout, PLOT_CFG);
  }

  // 2. Temperature vs Load Scatter
  function renderTempScatter() {
    const s = window.PROJECT_DATA.scatter;
    const occX = [], occY = [], offX = [], offY = [];
    for (let i = 0; i < s.temp.length; i++) {
      if (s.regime[i] === "Occupied") {
        occX.push(s.temp[i]);
        occY.push(s.kwh[i]);
      } else if (s.regime[i] === "Off-Hour") {
        offX.push(s.temp[i]);
        offY.push(s.kwh[i]);
      }
    }

    const traces = [
      {
        x: occX,
        y: occY,
        mode: "markers",
        type: "scattergl",
        name: "Occupied Work Hours",
        marker: { color: "#0044ff", size: 5.5, opacity: 0.45 },
      },
      {
        x: offX,
        y: offY,
        mode: "markers",
        type: "scattergl",
        name: "Overnight Off-Hours (22–06)",
        marker: { color: "#d946ef", size: 5.5, opacity: 0.48 },
      },
      {
        x: [18.3, 18.3],
        y: [250, 1450],
        mode: "lines",
        name: "18.3 °C Balance Point",
        line: { color: "#059669", width: 2.2, dash: "dot" },
      },
    ];

    const layout = plotlyLayoutBase({
      xaxis: Object.assign({}, plotlyLayoutBase().xaxis, { title: "Outdoor Dry-Bulb Temperature (°C)" }),
      yaxis: Object.assign({}, plotlyLayoutBase().yaxis, { title: "Hourly Electricity (kWh)" }),
    });
    Plotly.react("chartTempScatter", traces, layout, PLOT_CFG);
  }

  // 3. 4-Hour Block Quartile Comparison
  function renderBoxBlocks() {
    const blocks = window.PROJECT_DATA.box_blocks;
    const xLbl = blocks.map((b) => b.block);
    const wdMed = blocks.map((b) => b.weekday[2]);
    const weMed = blocks.map((b) => b.weekend[2]);
    const wdErrTop = blocks.map((b) => b.weekday[3] - b.weekday[2]);
    const wdErrBot = blocks.map((b) => b.weekday[2] - b.weekday[1]);
    const weErrTop = blocks.map((b) => b.weekend[3] - b.weekend[2]);
    const weErrBot = blocks.map((b) => b.weekend[2] - b.weekend[1]);

    const traces = [
      {
        x: xLbl,
        y: wdMed,
        type: "bar",
        name: "Weekday Median (with IQR)",
        marker: { color: "#0044ff" },
        error_y: { type: "data", symmetric: false, array: wdErrTop, arrayminus: wdErrBot, visible: true, thickness: 1.6 },
      },
      {
        x: xLbl,
        y: weMed,
        type: "bar",
        name: "Weekend Median (with IQR)",
        marker: { color: "#ff0000" },
        error_y: { type: "data", symmetric: false, array: weErrTop, arrayminus: weErrBot, visible: true, thickness: 1.6 },
      },
    ];

    const layout = plotlyLayoutBase({
      barmode: "group",
      xaxis: Object.assign({}, plotlyLayoutBase().xaxis, { title: "4-Hour Diurnal Window" }),
      yaxis: Object.assign({}, plotlyLayoutBase().yaxis, { title: "Median Demand & Interquartile Range (kWh)" }),
    });
    Plotly.react("chartBoxBlocks", traces, layout, PLOT_CFG);
  }

  // 4. Correlation Heatmap
  function renderCorrHeatmap() {
    const c = window.PROJECT_DATA.corr;
    const shortLabels = [
      "Total kWh", "Office kWh", "Campus kWh", "Air Temp", "CDD >18C",
      "Rel. Hum.", "Temp*RH", "Wind Spd", "Pressure", "Off-Hour", "Weekend", "24h Lag"
    ];
    const trace = {
      z: c.z,
      x: shortLabels,
      y: shortLabels,
      type: "heatmap",
      zmin: -1,
      zmax: 1,
      colorscale: [
        [0.0, "#0044ff"],
        [0.5, "#ffffff"],
        [1.0, "#ff0000"],
      ],
      hovertemplate: "%{y} vs %{x}: r = %{z:.2f}<extra></extra>",
    };

    const layout = plotlyLayoutBase({
      margin: { t: 16, r: 16, b: 78, l: 82 },
      xaxis: { tickangle: -35 },
      yaxis: { autorange: "reversed" },
    });
    Plotly.react("chartCorrHeatmap", [trace], layout, PLOT_CFG);
  }

  // 5. Model Benchmark Bar Chart
  function renderModelBench() {
    const ev = window.PROJECT_DATA.ml.anomaly_evaluation_2017;
    const keys = [
      ["Unsupervised_OneClass_SVM", "OCSVM (Unit IV)"],
      ["Hybrid_Consensus_Detector", "Hybrid Consensus"],
      ["Supervised_RBF_SVM", "RBF-SVM (Unit IV)"],
      ["Unsupervised_KMeans_Distance", "K-Means Dist."],
      ["Supervised_Gaussian_Naive_Bayes", "Naive Bayes"],
      ["Supervised_Decision_Tree", "Decision Tree"],
    ];

    const names = keys.map((k) => k[1]);
    const accs = keys.map((k) => +(ev[k[0]].accuracy * 100).toFixed(1));
    const f1s = keys.map((k) => +(ev[k[0]].f1 * 100).toFixed(1));
    const recs = keys.map((k) => +(ev[k[0]].recall * 100).toFixed(1));

    const traces = [
      { x: names, y: accs, type: "bar", name: "Accuracy (%)", marker: { color: "#0044ff" } },
      { x: names, y: recs, type: "bar", name: "Wastage Recall (%)", marker: { color: "#0891b2" } },
      { x: names, y: f1s, type: "bar", name: "F1 Score (%)", marker: { color: "#ff0000" } },
    ];

    const layout = plotlyLayoutBase({
      barmode: "group",
      xaxis: Object.assign({}, plotlyLayoutBase().xaxis, { tickangle: -18 }),
      yaxis: Object.assign({}, plotlyLayoutBase().yaxis, { title: "2017 Holdout Score (%)", range: [0, 102] }),
    });
    Plotly.react("chartModelBench", traces, layout, PLOT_CFG);
  }

  // 6. K-Means Cluster Scatter
  function renderClusterScatter() {
    const dt = window.PROJECT_DATA.daily_timeline;
    const groups = {};
    for (let i = 0; i < dt.dates.length; i++) {
      const cl = dt.cluster[i];
      if (!groups[cl]) groups[cl] = { x: [], y: [], text: [] };
      groups[cl].x.push(dt.temp_c[i]);
      groups[cl].y.push(dt.excess_kwh[i]);
      groups[cl].text.push(dt.dates[i] + " | Actual: " + dt.actual_mwh[i] + " MWh");
    }

    const paletteMap = {
      "Shoulder-Season Baseload Drift Regime": "#ff0000",
      "Summer Peak Cooling & Drift Regime": "#d946ef",
      "Mild-Weather Efficient Baseline": "#0044ff",
      "Weekend & Academic Setback Regime": "#059669",
    };

    const traces = Object.keys(groups).map((cl) => ({
      x: groups[cl].x,
      y: groups[cl].y,
      text: groups[cl].text,
      mode: "markers",
      type: "scatter",
      name: cl.replace(" Regime", "").replace(" Baseline", ""),
      marker: { color: paletteMap[cl] || "#64748b", size: 7, opacity: 0.78 },
      hovertemplate: "<b>%{text}</b><br>Temp: %{x}°C | Excess: %{y:.0f} kWh<extra></extra>",
    }));

    const layout = plotlyLayoutBase({
      xaxis: Object.assign({}, plotlyLayoutBase().xaxis, { title: "Daily Mean Outdoor Temperature (°C)" }),
      yaxis: Object.assign({}, plotlyLayoutBase().yaxis, { title: "Daily Excess vs Expected Baseline (kWh)" }),
    });
    Plotly.react("chartClusterScatter", traces, layout, PLOT_CFG);
  }

  // 7. Interactive 2-Year Daily Timeline
  function renderTimeline() {
    const dt = window.PROJECT_DATA.daily_timeline;
    const x = [], act = [], exp = [], ax = [], ay = [], aTxt = [];

    for (let i = 0; i < dt.dates.length; i++) {
      const yr = dt.dates[i].slice(0, 4);
      if (state.timelineYear !== "all" && yr !== state.timelineYear) continue;
      x.push(dt.dates[i]);
      act.push(dt.actual_mwh[i]);
      exp.push(dt.expected_mwh[i]);
      if (dt.flagged[i] === 1) {
        ax.push(dt.dates[i]);
        ay.push(dt.actual_mwh[i]);
        aTxt.push(
          dt.dates[i] +
          "<br>Actual: " + dt.actual_mwh[i] + " MWh" +
          "<br>Expected: " + dt.expected_mwh[i] + " MWh" +
          "<br>Excess: +" + dt.excess_kwh[i] + " kWh ($" + (dt.excess_kwh[i] * 0.12).toFixed(0) + ")"
        );
      }
    }

    const traces = [
      {
        x: x,
        y: exp,
        mode: "lines",
        name: "Counterfactual Expected Baseline (MWh)",
        line: { color: "#0891b2", width: 1.7 },
      },
      {
        x: x,
        y: act,
        mode: "lines",
        name: "Actual Metered Demand (MWh)",
        line: { color: "#0044ff", width: 1.5 },
      },
      {
        x: ax,
        y: ay,
        text: aTxt,
        mode: "markers",
        name: "Flagged Wastage Days (n = " + ax.length + ")",
        marker: { color: "#ff0000", size: 8, line: { color: "#000000", width: 1 } },
        hovertemplate: "%{text}<extra></extra>",
      },
    ];

    const layout = plotlyLayoutBase({
      xaxis: Object.assign({}, plotlyLayoutBase().xaxis, { title: "Calendar Date" }),
      yaxis: Object.assign({}, plotlyLayoutBase().yaxis, { title: "Daily Portfolio Electricity (MWh / day)" }),
    });
    Plotly.react("chartTimeline", traces, layout, PLOT_CFG);
  }

  // 8. Populate Top Anomaly Table
  function renderAnomalyTable() {
    const rows = window.PROJECT_DATA.ml.top_15_anomaly_days || [];
    const tbody = document.getElementById("anomalyTableBody");
    if (!tbody) return;

    const filtered = rows.filter((r) => {
      if (state.clusterFilter === "all") return true;
      return r.cluster.indexOf(state.clusterFilter) !== -1;
    });

    tbody.innerHTML = filtered
      .map(
        (r, idx) =>
          "<tr>" +
          "<td><strong>#" + (idx + 1) + "</strong></td>" +
          "<td><code>" + r.date + "</code></td>" +
          "<td>" + r.daily_kwh.toLocaleString() + "</td>" +
          "<td>" + r.expected_kwh.toLocaleString() + "</td>" +
          "<td><span class='tag-anom'>+" + r.excess_kwh.toLocaleString() + " kWh</span></td>" +
          "<td>" + r.off_hour_mean_kwh.toFixed(1) + " kWh/h</td>" +
          "<td>" + r.baseload_ratio.toFixed(3) + "</td>" +
          "<td>" + r.mean_temp_c.toFixed(1) + " &deg;C</td>" +
          "<td>" + r.cluster.replace(" Regime", "") + "</td>" +
          "<td><strong>$" + r.estimated_waste_usd.toFixed(2) + "</strong></td>" +
          "</tr>"
      )
      .join("");
  }

  // 9. Interactive BMS Savings Simulator + Waterfall
  function updateSimulator() {
    const p1 = parseFloat(document.getElementById("simL1").value) / 100;
    const p2 = parseFloat(document.getElementById("simL2").value) / 100;
    const p3 = parseFloat(document.getElementById("simL3").value) / 100;
    const p4 = parseFloat(document.getElementById("simL4").value) / 100;
    const tariff = parseFloat(document.getElementById("simTariff").value);

    document.getElementById("lblL1").textContent = Math.round(p1 * 100) + "% Capture";
    document.getElementById("lblL2").textContent = Math.round(p2 * 100) + "% Capture";
    document.getElementById("lblL3").textContent = Math.round(p3 * 100) + "% Mitigation";
    document.getElementById("lblL4").textContent = Math.round(p4 * 100) + "% Trim";
    document.getElementById("lblTariff").textContent = "$" + tariff.toFixed(2) + " / kWh";

    const s1 = BASE_POOLS.l1_raw * p1;
    const s2 = BASE_POOLS.l2_raw * p2;
    const s3 = BASE_POOLS.l3_raw * p3;
    const s4 = BASE_POOLS.l4_raw * p4;
    const totalSaved = s1 + s2 + s3 + s4;
    const pct = (totalSaved / BASE_ANNUAL_KWH) * 100;
    const usd = totalSaved * tariff;
    const inrLakhs = (usd * 83.3333) / 100000;
    const co2 = (totalSaved * 0.417) / 1000;

    const pctEl = document.getElementById("simPctOut");
    pctEl.textContent = pct.toFixed(2) + "%";
    pctEl.style.color = pct >= 15 && pct <= 20.5 ? "var(--accent-green)" : "var(--accent-amber)";

    document.getElementById("simKwhOut").textContent = Math.round(totalSaved).toLocaleString() + " kWh/yr";
    document.getElementById("simUsdOut").textContent = "$" + Math.round(usd).toLocaleString() + " / yr";
    document.getElementById("simInrOut").textContent = "Rs. " + inrLakhs.toFixed(2) + " Lakhs/yr";
    document.getElementById("simCo2Out").textContent = co2.toFixed(1) + " tCO2e / yr";

    const baseMwh = BASE_ANNUAL_KWH / 1000;
    const m1 = s1 / 1000, m2 = s2 / 1000, m3 = s3 / 1000, m4 = s4 / 1000;
    const optMwh = baseMwh - (m1 + m2 + m3 + m4);

    const trace = {
      type: "waterfall",
      orientation: "v",
      measure: ["absolute", "relative", "relative", "relative", "relative", "total"],
      x: [
        "Current Baseline",
        "L1: Night Setback",
        "L2: Weekend Cut",
        "L3: OCSVM Triage",
        "L4: HVAC Deadband",
        "Optimized Load",
      ],
      y: [baseMwh, -m1, -m2, -m3, -m4, optMwh],
      text: [
        baseMwh.toFixed(0) + " MWh",
        "-" + m1.toFixed(0) + " MWh",
        "-" + m2.toFixed(0) + " MWh",
        "-" + m3.toFixed(0) + " MWh",
        "-" + m4.toFixed(0) + " MWh",
        optMwh.toFixed(0) + " MWh",
      ],
      textposition: "outside",
      connector: { line: { color: "#94a3b8", dash: "dot" } },
      decreasing: { marker: { color: "#ff0000" } },
      increasing: { marker: { color: "#0044ff" } },
      totals: { marker: { color: "#059669" } },
    };

    const layout = plotlyLayoutBase({
      showlegend: false,
      yaxis: Object.assign({}, plotlyLayoutBase().yaxis, { title: "Annual Electricity (MWh / yr)", range: [0, 7900] }),
      shapes: [
        {
          type: "rect",
          xref: "paper",
          yref: "y",
          x0: 0,
          x1: 1,
          y0: baseMwh * 0.80,
          y1: baseMwh * 0.85,
          fillcolor: "rgba(5, 150, 105, 0.14)",
          line: { color: "rgba(5, 150, 105, 0.45)", width: 1, dash: "dash" },
        },
      ],
    });
    Plotly.react("chartWaterfall", [trace], layout, PLOT_CFG);
  }

  function renderAllCharts() {
    renderDiurnal();
    renderTempScatter();
    renderBoxBlocks();
    renderCorrHeatmap();
    renderModelBench();
    renderClusterScatter();
    renderTimeline();
    updateSimulator();
  }

  // Animated KPI Counters
  function initCounters() {
    const els = document.querySelectorAll(".kpi-num[data-count]");
    els.forEach((el) => {
      const target = parseFloat(el.getAttribute("data-count"));
      const decimals = parseInt(el.getAttribute("data-decimals") || "0", 10);
      const prefix = el.getAttribute("data-prefix") || "";
      const suffix = el.getAttribute("data-suffix") || "";
      const dur = 950;
      const start = performance.now();

      function tick(now) {
        const p = Math.min(1, (now - start) / dur);
        const eased = 1 - Math.pow(1 - p, 3);
        const val = target * eased;
        const formatted =
          decimals === 0
            ? Math.round(val).toLocaleString()
            : val.toFixed(decimals);
        el.textContent = prefix + formatted + suffix;
        if (p < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    applyTheme(state.theme);
    initCounters();

    const themeBtn = document.getElementById("themeToggle");
    if (themeBtn) {
      themeBtn.addEventListener("click", function () {
        applyTheme(state.theme === "dark" ? "light" : "dark");
      });
    }

    const menuBtn = document.getElementById("mobileMenuBtn");
    const navLinks = document.getElementById("navLinks");
    if (menuBtn && navLinks) {
      menuBtn.addEventListener("click", function () {
        navLinks.classList.toggle("open");
      });
      navLinks.querySelectorAll("a").forEach((a) =>
        a.addEventListener("click", () => navLinks.classList.remove("open"))
      );
    }

    document.querySelectorAll("#diurnalSectorToggle .seg-btn").forEach((btn) => {
      btn.addEventListener("click", function () {
        document.querySelectorAll("#diurnalSectorToggle .seg-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        state.sector = btn.getAttribute("data-sector");
        renderDiurnal();
      });
    });

    document.querySelectorAll("#timelineYearFilter .seg-btn").forEach((btn) => {
      btn.addEventListener("click", function () {
        document.querySelectorAll("#timelineYearFilter .seg-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        state.timelineYear = btn.getAttribute("data-yr");
        renderTimeline();
      });
    });

    const clSel = document.getElementById("clusterFilterSelect");
    if (clSel) {
      clSel.addEventListener("change", function () {
        state.clusterFilter = clSel.value;
        renderAnomalyTable();
      });
    }

    ["simL1", "simL2", "simL3", "simL4", "simTariff"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.addEventListener("input", updateSimulator);
    });

    const resetBtn = document.getElementById("simResetBtn");
    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        document.getElementById("simL1").value = 68;
        document.getElementById("simL2").value = 62;
        document.getElementById("simL3").value = 82;
        document.getElementById("simL4").value = 32;
        document.getElementById("simTariff").value = 0.12;
        updateSimulator();
      });
    }

    if (window.PROJECT_DATA) {
      renderAnomalyTable();
      renderAllCharts();
    }
  });
})();
