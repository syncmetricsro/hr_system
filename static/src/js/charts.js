/* Finance/Reports chart builders (ADR 0025). Loaded only on pages with a
   canvas[data-chart] (see the per-template {% block scripts %}). Colors are
   read from CSS custom properties at build time and re-read on the shared
   "themechange" event (static/src/js/theme.js) — Chart.js doesn't repaint
   on a CSS change by itself, so tracked charts are destroyed and rebuilt
   rather than mutated in place. */
(function () {
  "use strict";

  var tracked = []; // [{canvas, build}] — build(colors) returns a live Chart

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function getThemeColors() {
    return {
      grid: cssVar("--n200"),
      tick: cssVar("--muted"),
      text: cssVar("--ink"),
      surface: cssVar("--panel"),
      track: cssVar("--n200"),
      positive: cssVar("--chart-positive"),
      negative: cssVar("--chart-negative"),
      net: cssVar("--chart-net"),
      font: cssVar("--font-body"),
    };
  }

  function readChartData(elementId) {
    var el = document.getElementById(elementId);
    if (!el) return null;
    try {
      return JSON.parse(el.textContent);
    } catch (_error) {
      return null;
    }
  }

  function toNumber(value) {
    return typeof value === "string" ? Number(value) : value;
  }

  function toNumbers(values) {
    return (values || []).map(toNumber);
  }

  // Direct labels need room past the longest bar/last point or they overlap
  // the axis (negative extreme) or clip at the canvas edge (positive extreme)
  // — headroom beyond the actual data range, not just a fixed pixel pad.
  function paddedRange(values, headroom) {
    var max = Math.max(0, Math.max.apply(null, values));
    var min = Math.min(0, Math.min.apply(null, values));
    var span = Math.max(max - min, 1);
    return { min: min - span * headroom, max: max + span * headroom };
  }

  function formatEur(value) {
    var sign = value < 0 ? "−" : "";
    return sign + Math.abs(value).toLocaleString(undefined, { maximumFractionDigits: 0 }) + " €";
  }

  // Direct labels: bars get a value at every tip (few discrete categories —
  // this is the normal case a bar chart labels, not the "number on every
  // point" a dense line chart should avoid); lines get the end value only.
  var valueLabelsPlugin = {
    id: "valueLabels",
    afterDatasetsDraw: function (chart, _args, opts) {
      if (!opts || !opts.mode) return;
      var ctx = chart.ctx;
      var format = opts.formatter || formatEur;
      ctx.save();
      ctx.font = "600 12px " + (opts.font || "sans-serif");
      ctx.fillStyle = opts.color || "#000";
      ctx.textBaseline = "middle";

      if (opts.mode === "bar-tip") {
        chart.data.datasets.forEach(function (dataset, di) {
          var meta = chart.getDatasetMeta(di);
          meta.data.forEach(function (bar, i) {
            var value = toNumber(dataset.data[i]);
            var label = format(value);
            var x = bar.x + (value >= 0 ? 6 : -6);
            ctx.textAlign = value >= 0 ? "left" : "right";
            ctx.fillText(label, x, bar.y);
          });
        });
      } else if (opts.mode === "line-end") {
        chart.data.datasets.forEach(function (dataset, di) {
          var meta = chart.getDatasetMeta(di);
          if (!meta.data.length) return;
          var last = meta.data[meta.data.length - 1];
          var value = toNumber(dataset.data[dataset.data.length - 1]);
          ctx.fillStyle = dataset.borderColor || opts.color;
          ctx.textAlign = "left";
          ctx.fillText(formatEur(value), last.x + 8, last.y);
        });
      }
      ctx.restore();
    },
  };
  Chart.register(valueLabelsPlugin);

  function baseOptions(colors) {
    return {
      responsive: true,
      maintainAspectRatio: false,
      layout: { padding: { right: 12 } },
      scales: {
        x: {
          grid: { color: colors.grid, drawTicks: false },
          ticks: { color: colors.tick, font: { family: colors.font } },
        },
        y: {
          grid: { color: colors.grid, drawTicks: false },
          ticks: { color: colors.tick, font: { family: colors.font } },
        },
      },
      plugins: {
        legend: {
          labels: { color: colors.text, font: { family: colors.font }, boxWidth: 16, boxHeight: 2 },
        },
        tooltip: {
          backgroundColor: cssVar("--tooltip-bg"),
          titleColor: cssVar("--tooltip-ink"),
          bodyColor: cssVar("--tooltip-ink"),
          borderColor: cssVar("--tooltip-line"),
          borderWidth: 1,
          padding: 10,
          cornerRadius: 6,
          titleFont: { family: colors.font },
          bodyFont: { family: colors.font },
        },
      },
    };
  }

  function buildTrendChart(canvas, data, colors) {
    var labels = data.labels || [];
    var opts = baseOptions(colors);
    opts.plugins.valueLabels = { mode: "line-end", font: colors.font, color: colors.text };
    opts.plugins.legend.display = true;
    opts.interaction = { mode: "index", intersect: false };
    opts.elements = { point: { radius: 4, hoverRadius: 6, borderWidth: 2, borderColor: colors.surface } };
    // The end-of-line label always sits at the rightmost category (a "so
    // far" trend), so it always needs canvas room past the last point —
    // unlike a numeric scale, a category x-axis has no % headroom to add.
    opts.layout.padding.right = 90;
    return new Chart(canvas, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          { label: canvas.dataset.labelRevenue || "Revenue", data: toNumbers(data.revenue), borderColor: colors.positive, backgroundColor: colors.positive, borderWidth: 2, tension: 0.15 },
          { label: canvas.dataset.labelCost || "Cost", data: toNumbers(data.cost), borderColor: colors.negative, backgroundColor: colors.negative, borderWidth: 2, tension: 0.15 },
          { label: canvas.dataset.labelNet || "Net", data: toNumbers(data.net), borderColor: colors.net, backgroundColor: colors.net, borderWidth: 2, tension: 0.15 },
        ],
      },
      options: opts,
    });
  }

  function buildDivergingBarChart(canvas, data, colors) {
    var netValues = toNumbers(data.net);
    var opts = baseOptions(colors);
    opts.indexAxis = "y";
    opts.plugins.legend.display = false;
    opts.plugins.valueLabels = { mode: "bar-tip", font: colors.font, color: colors.text };
    opts.plugins.tooltip.callbacks = {
      label: function (ctx) { return formatEur(toNumber(ctx.raw)); },
    };
    opts.scales.x.grid.color = colors.grid;
    var range = paddedRange(netValues, 0.35);
    opts.scales.x.min = range.min;
    opts.scales.x.max = range.max;
    return new Chart(canvas, {
      type: "bar",
      data: {
        labels: data.labels || [],
        datasets: [{
          data: netValues,
          maxBarThickness: 24,
          borderRadius: 4,
          borderSkipped: function (ctx) {
            var value = netValues[ctx.dataIndex];
            return value >= 0 ? "left" : "right";
          },
          backgroundColor: netValues.map(function (v) {
            return v >= 0 ? colors.positive : colors.negative;
          }),
        }],
      },
      options: opts,
    });
  }

  function buildMagnitudeBarChart(canvas, data, colors) {
    var opts = baseOptions(colors);
    opts.indexAxis = "y";
    opts.plugins.legend.display = false;
    opts.plugins.valueLabels = {
      mode: "bar-tip", font: colors.font, color: colors.text,
      formatter: function (value) { return String(value); },
    };
    opts.plugins.tooltip.callbacks = {
      label: function (ctx) { return String(ctx.raw); },
    };
    var headcounts = (data.headcount || []).map(toNumber);
    // Headcount is never negative — pad the max only, and force integer
    // ticks (Chart.js otherwise generates decimal steps like 0.2/0.4 for a
    // small max).
    opts.scales.x.ticks.stepSize = 1;
    opts.scales.x.ticks.precision = 0;
    opts.scales.x.min = 0;
    opts.scales.x.max = paddedRange(headcounts, 0.35).max;
    return new Chart(canvas, {
      type: "bar",
      data: {
        labels: data.labels || [],
        datasets: [{
          data: headcounts,
          maxBarThickness: 24,
          borderRadius: 4,
          borderSkipped: "left",
          backgroundColor: colors.net,
        }],
      },
      options: opts,
    });
  }

  function buildGaugeChart(canvas, data, colors) {
    var net = toNumber(data.net);
    var marginPct = toNumber(data.margin_pct);
    // A half-doughnut only has one fill direction (0-100%); a negative
    // margin has no proportional arc to show, so it reads as a full arc in
    // the negative color instead — an unambiguous "this is a loss" signal.
    // The exact signed percentage is always in the tooltip and template text.
    var fraction = marginPct >= 0 ? Math.max(0, Math.min(1, marginPct / 100)) : 1;
    var fillColor = net >= 0 ? colors.positive : colors.negative;
    var opts = {
      responsive: true,
      maintainAspectRatio: false,
      circumference: 180,
      rotation: 270,
      cutout: "72%",
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function () {
              return (canvas.dataset.labelMargin || "Margin") + ": " + marginPct.toFixed(1) + "%";
            },
          },
          backgroundColor: cssVar("--tooltip-bg"),
          titleColor: cssVar("--tooltip-ink"),
          bodyColor: cssVar("--tooltip-ink"),
        },
      },
    };
    return new Chart(canvas, {
      type: "doughnut",
      data: {
        labels: [canvas.dataset.labelMargin || "Margin", ""],
        datasets: [{
          data: [fraction, 1 - fraction],
          backgroundColor: [fillColor, colors.track],
          borderWidth: 0,
        }],
      },
      options: opts,
    });
  }

  var builders = {
    trend: buildTrendChart,
    gauge: buildGaugeChart,
    diverging: buildDivergingBarChart,
    magnitude: buildMagnitudeBarChart,
  };

  function buildOne(canvas) {
    var kind = canvas.dataset.chart;
    var builder = builders[kind];
    if (!builder) return;
    var dataId = canvas.dataset.chartData;
    var data = readChartData(dataId);
    if (!data) return;
    var colors = getThemeColors();
    var chart = builder(canvas, data, colors);
    tracked.push({ canvas: canvas, build: function () { return builder(canvas, data, getThemeColors()); } });
    return chart;
  }

  function initChartsOnPage() {
    document.querySelectorAll("canvas[data-chart]").forEach(buildOne);
  }

  function rebuildAllTracked() {
    tracked.forEach(function (entry) {
      var existing = Chart.getChart(entry.canvas);
      if (existing) existing.destroy();
      entry.build();
    });
  }

  document.addEventListener("DOMContentLoaded", initChartsOnPage);
  document.addEventListener("themechange", rebuildAllTracked);
})();
