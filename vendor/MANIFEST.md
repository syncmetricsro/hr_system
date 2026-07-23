# Vendor Manifest

All runtime assets are served locally. Update this file and re-run `python3 scripts/verify_vendor_assets.py` whenever a vendored file changes.

| Asset | Version | Source | License | SHA-256 |
|---|---:|---|---|---|
| `static/vendor/htmx.min.js` | 2.0.4 | `https://raw.githubusercontent.com/bigskysoftware/htmx/v2.0.4/dist/htmx.min.js` | BSD-2-Clause, `static/vendor/licenses/htmx-LICENSE` | `e209dda5c8235479f3166defc7750e1dbcd5a5c1808b7792fc2e6733768fb447` |
| `static/vendor/alpine.min.js` | 3.15.12 | `https://cdn.jsdelivr.net/npm/alpinejs@3.15.12/dist/cdn.min.js` | MIT, `static/vendor/licenses/alpine-LICENSE.md` | `57b37d7cae9a27d965fdae4adcc844245dfdc407e655aee85dcfff3a08036a3f` |
| `static/vendor/licenses/htmx-LICENSE` | 2.0.4 | `https://raw.githubusercontent.com/bigskysoftware/htmx/v2.0.4/LICENSE` | BSD-2-Clause | `d3d2456f76414f2456104660ebd65aff1c04cd7966b942bdabd63f3cdb316a38` |
| `static/vendor/licenses/alpine-LICENSE.md` | 3.15.12 | `https://raw.githubusercontent.com/alpinejs/alpine/v3.15.12/LICENSE.md` | MIT | `08b7502da6e7aa1d0bbdc97d220fbf669b9366c61bd0f072238283c89bc4773a` |
| `static/vendor/chart.min.js` | 4.5.1 | `https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js` (upstream filename `chart.umd.min.js`; trailing `//# sourceMappingURL=chart.umd.min.js.map` comment stripped — the map itself isn't vendored, same as htmx/alpine ship no map) | MIT, `static/vendor/licenses/chartjs-LICENSE` | `84d0e233daba702b8f77d669d8c137cad36d441a10f200b6f2d3ab553bdfcf6b` |
| `static/vendor/licenses/chartjs-LICENSE` | 4.5.1 | `https://raw.githubusercontent.com/chartjs/Chart.js/v4.5.1/LICENSE.md` | MIT | `41a84aa2caba645f966a18d9c2056b73e6d3a81d80bc0046bc0011a2634d4cce` |
| `tailwindcss-linux-x64` | 4.3.0 | `https://github.com/tailwindlabs/tailwindcss/releases/download/v4.3.0/tailwindcss-linux-x64` | MIT, Tailwind Labs release asset | `73f0e5459054e5cfaa8ab6f3b940f3fbe0f13cc7fd83bc24e7c655033c203400` |
| `sha256sums.txt` | 4.3.0 | `https://github.com/tailwindlabs/tailwindcss/releases/download/v4.3.0/sha256sums.txt` | Official Tailwind Labs release checksum file | Linux x64 line recorded in `vendor/tailwind/tailwindcss-v4.3.0-linux-x64.sha256` |

Tailwind standalone CLI is intentionally not committed. The Docker build fetches it from the pinned Tailwind Labs release URL, checks the official `sha256sums.txt` value against the committed checksum file, verifies the binary hash, builds CSS, then excludes the binary from the runtime image.
