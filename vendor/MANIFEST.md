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
| `vendor/fonts/DejaVuSans.ttf` | 2.37 | `https://sourceforge.net/projects/dejavu/files/dejavu/2.37/dejavu-fonts-ttf-2.37.tar.bz2` (extracted `ttf/DejaVuSans.ttf`) | Bitstream Vera + public domain, `vendor/fonts/dejavu-LICENSE` | `7da195a74c55bef988d0d48f9508bd5d849425c1770dba5d7bfc6ce9ed848954` |
| `vendor/fonts/DejaVuSans-Bold.ttf` | 2.37 | same archive, `ttf/DejaVuSans-Bold.ttf` | Bitstream Vera + public domain, `vendor/fonts/dejavu-LICENSE` | `e6476c1b80502924294eed40894c5b18e06c181444ca953e5334262df9c27724` |
| `vendor/fonts/dejavu-LICENSE` | 2.37 | same archive, `LICENSE` | Bitstream Vera + public domain | `7a083b136e64d064794c3419751e5c7dd10d2f64c108fe5ba161eae5e5958a93` |
| `clients/corvinum_eu/static/corvinum/fonts/material-symbols-outlined-subset.woff2` | Material Symbols Outlined (2026-07-24 regeneration, 49 icons) | `https://github.com/google/material-design-icons/raw/master/variablefont/MaterialSymbolsOutlined%5BFILL%2CGRAD%2Copsz%2Cwght%5D.ttf`, instanced + pruned + subsetted by `scripts/subset_corvinum_icons.py` (not a straight file copy — see that script's docstring for why a plain `fonttools subset --text=` pass isn't enough for this font's GSUB structure) | Apache-2.0 (`https://github.com/google/material-design-icons/blob/master/LICENSE`) | `c001760477fca76d60185e50923d6b9f4bb0f1e91af38cf3843b5801571ebfa1` |

Tailwind standalone CLI is intentionally not committed. The Docker build fetches it from the pinned Tailwind Labs release URL, checks the official `sha256sums.txt` value against the committed checksum file, verifies the binary hash, builds CSS, then excludes the binary from the runtime image.

The DejaVu fonts (docs/product/feedback-flyer-design.md — Cyrillic-capable PDF text embedding via `fpdf2`) are needed at **runtime**, not just build time, so unlike Tailwind they're committed like htmx/alpine/Chart.js. Archive integrity was verified against the official release's published MD5
(`d0efec10b9f110a32e9b8f796e21782c` for the `.tar.bz2`, matched exactly) before extracting; the SHA-256 values above were computed directly from the extracted files, not copied from a third party.
