# ADR 0025: Chart.js for finance and reports visualizations

Status: **Accepted**

## Context

Manual QA feedback asked for graphical (not just tabular) monthly/yearly
finance reports — "more than one graphical representation: half pies,
graphs, etc." — and a visual projects/personnel view on the Reports page.
No charting capability, client- or server-side, exists anywhere in the
repo today. Per AGENTS.md §3.2, any new frontend JS must be vendored
locally (never CDN-served at runtime), pinned, and SHA-256-verified —
the same regime already applied to htmx (ADR 0004) and Alpine.

## Decision

Vendor **Chart.js 4.5.1** (MIT) as `static/vendor/chart.min.js`, fetched
from its own published `jsdelivr`/`unpkg` entry point
(`dist/chart.umd.min.js` — a genuinely pre-minified, dependency-free UMD
build, confirmed by fetching it directly), the same acquisition pattern
already used for Alpine's manifest row. License recorded at
`static/vendor/licenses/chartjs-LICENSE`; both hashes in
`vendor/MANIFEST.md` and `scripts/verify_vendor_assets.py`.

Chart.js is loaded only on the pages that render a chart, via a new
`{% block scripts %}` in both `templates/layouts/base.html` and
`clients/corvinum_eu/templates/layouts/base.html` — never globally
alongside htmx/Alpine/app.js. A new `static/src/js/charts.js` builds
charts from data handed off via Django's `json_script` filter, reads
chart colors from CSS custom properties at render time, and rebuilds on
the existing `themechange` event so charts stay correct across the
light/dark toggle.

Alternatives rejected:
- **D3** — a rendering toolkit, not a chart library; would mean
  hand-writing and maintaining chart rendering code on a money-display
  surface, the opposite of this repo's "vetted small library over
  hand-rolled" precedent (ADR 0024, segno over a hand-rolled QR encoder).
- **ECharts / Plotly.js** — 5-15x Chart.js's size for a BI feature-set
  this app doesn't need.
- **uPlot** — excellent for dense time series, but has no doughnut/pie
  support at all, failing the explicit "half pies" ask outright.

## Consequences

- Two new `vendor/MANIFEST.md` rows; CI's existing
  `scripts/verify_vendor_assets.py` gate picks them up automatically.
- Every chart is paired with the accessible table/`dl` it's built from —
  charts are additive, never chart-only data.
- All money arithmetic stays server-side `Decimal`; `charts.js` only
  coerces already-computed, already-rounded values to JS numbers for
  pixel/angle placement, never performs financial math and never writes
  anything back.
- Chart colors are separate, validated tokens (`--chart-positive`,
  `--chart-negative`, `--chart-net`), not a blind reuse of the existing
  `--success`/`--danger` text tokens — the latter's dark-theme values
  fail categorical colorblind-safety checks (confirmed via the project's
  palette validator) and were not touched by this ADR; only the new
  chart-specific tokens were tuned to pass in both themes.
