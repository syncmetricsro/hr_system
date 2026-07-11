# Vendored assets — CorvinumEU client theme (AGENTS §3.2)

Copied 2026-07-11 from the `corvinumeu` repo, branch `peopleops-prototype`,
`peopleops-prototype/assets/` — which itself copied them from the corvinum.eu
site source (`assets/vendor/fonts/...`, provenance recorded in that repo's
`PROVENANCE.md`). No CDN or runtime fetches; upgrades happen via a deliberate
PR updating file + hash together.

| File | SHA-256 | Origin (site source path) | License |
|---|---|---|---|
| `fonts/hanken-grotesk-latin.woff2` | `e9201eddf1d41d0b62253295d869ce3cf65768f7102b797f02c7f8c876b4a9d5` | `assets/vendor/fonts/hanken-grotesk/v12/` | SIL OFL 1.1 |
| `fonts/hanken-grotesk-latin-ext.woff2` | `768af2923e0ab1549f1dfba0a5c8ea749c4c01f01d8e77ffaf7fcd12f57a0a24` | `assets/vendor/fonts/hanken-grotesk/v12/` | SIL OFL 1.1 |
| `fonts/inter-latin.woff2` | `3100e775e8616cd2611beecfa23a4263d7037586789b43f035236a2e6fbd4c62` | `assets/vendor/fonts/inter/v20/` | SIL OFL 1.1 |
| `fonts/inter-latin-ext.woff2` | `34b9c504cab7a73e37b746343a449132e56cf7b5481af2cb81dc74dcff25c956` | `assets/vendor/fonts/inter/v20/` | SIL OFL 1.1 |
| `fonts/jetbrains-mono-latin.woff2` | `cb182feeed4d798ff6961d3c79f7026279448fca0676438aaecb21f3fc39553a` | `assets/vendor/fonts/jetbrains-mono/v24/` | SIL OFL 1.1 |
| `fonts/jetbrains-mono-latin-ext.woff2` | `879df9319f1cbf633bee1dd489e376a9e1e8c458f4abddcfe381cb83b5e6b027` | `assets/vendor/fonts/jetbrains-mono/v24/` | SIL OFL 1.1 |
| `fonts/material-symbols-outlined-subset.woff2` | `8dea778c0a4314b56834c0be933d101cad134db6d0956674e37bad7c0541f7be` | `assets/vendor/fonts/material-symbols/v355/` (subset) | Apache-2.0 |
| `fonts/icon-names.txt` | `3d51d65642ca7fb7aeb7d4b3403d9a002c66066227dd1439451d3c6f088a5908` | subset manifest (names available in the icon font) | — |
| `brand/corvinum-logo-v1.webp` | `4db6d485176468e2bda23461650387201548977e332bcb65cdff4697ddba4819` | `assets/images/brand/` | CorvinumEU brand asset (client-owned) |

`theme.css` and `shell.js` are **first-party** (hand-ported from the
prototype's hand-written CSS/JS), not vendored third-party code.
