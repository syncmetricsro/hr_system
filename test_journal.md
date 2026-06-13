# Test Journal

## 2026-06-13

Checks run:
- `node --check demo/app.js` passed.
- Parsed `demo/index.html` with Python `html.parser`; passed.
- Scanned `demo/index.html`, `demo/app.js`, and `demo/styles.css` for `localStorage`, `sessionStorage`, remote URLs, `@import`, and remote script/style references; no matches.
- Opened `demo/index.html` directly in headless Chromium; the app rendered.
- Ran a Chromium DevTools Protocol interaction check through the full guided path:
  - sign in to dashboard;
  - decision 1 pauses Next until selected;
  - blacklist risk flag saves;
  - Tran hire approval records;
  - Olha shift and transport assignment records;
  - fake SMS sent state records;
  - second shift records;
  - sick leave changes Olha to Inactive;
  - Farrukh forklift assignment hard-stops;
  - mobile field view renders;
  - Jober switch reveals Accommodation, Equipment, and Pohoda nav;
  - Observer role shows disabled actions.
- Captured and reviewed desktop dashboard, Jober finale, and mobile field-view screenshots.
- Ran a one-shot Python static server and fetched `index.html`; passed.

Known issues:
- Headless Chromium emits a VM-level VAAPI/GPU warning. No app console errors or runtime exceptions were detected.

Manual acceptance status:
- Demo lives inside `demo/`, with only the required root journals added.
- No dependencies, backend, persistence, remote runtime code, or media assets were added.
- Cyrillic and Central-Asian names render in the app screens.
- Both hire status and availability badges appear consistently wherever worker rows or headers are shown.

## 2026-06-13

Responsive retrofit checks.

Static checks run:
- `node --check demo/app.js` passed.
- `node --check tests/responsive.spec.js` passed.
- `node --check playwright.config.js` passed.
- Parsed `demo/index.html` with Python `html.parser`; passed.
- Scanned `demo/index.html`, `demo/app.js`, and `demo/styles.css` for persistence APIs and remote runtime code; no matches.

Playwright container setup:
- Base image verified and pinned: `mcr.microsoft.com/playwright:v1.60.0-noble@sha256:9bd26ad900bb5e0f4dee75839e957a89ae89c2b7ab1e76050e559790e946b948`.
- `@playwright/test` pinned to `1.60.0`.
- Built local disposable test image with `docker build -f Dockerfile.playwright -t hr-system-playwright-tests:1.60.0 .`.
- Ran with `demo/` mounted read-only, `test-artifacts/` mounted writable, and `--network none`.

Playwright results:
- `responsive shell works at phone width` passed at 375px.
- `responsive shell works at tablet width` passed at 768px.
- `responsive shell works at desktop width` passed at 1440px.
- `phone width restacks tables, decisions, and field view` passed.

Verified behavior:
- No horizontal scroll at tested widths.
- Mobile/tablet nav opens and closes.
- Mobile/tablet manifest strip expands/collapses and exposes all 12 stops.
- Guided Back/Next works from the mobile manifest.
- Phone tables render as labelled cards.
- Phone decisions stack vertically.
- Phone manager field view uses the native phone layout.
- CorvinumEU/Jober switch works at tested widths.
- Role switch and Observer disabled-action state work at tested widths.
- No console/runtime errors were detected by Playwright.

Known issues:
- `test-artifacts/playwright-report/index.html` and `test-artifacts/playwright-output/.last-run.json` are generated test artifacts.

## 2026-06-13

Desktop spacing regression checks.

Static checks run:
- `node --check demo/app.js` passed.
- `node --check tests/responsive.spec.js` passed.
- Parsed `demo/index.html` with Python `html.parser`; passed.
- Scanned `demo/index.html`, `demo/app.js`, and `demo/styles.css` for persistence APIs, remote script/style URLs, remote URLs, and CSS `@import`; no matches.

Playwright results:
- Built the pinned Docker image with `docker build -f Dockerfile.playwright -t hr-system-playwright-tests:1.60.0 .`.
- Ran the suite with `demo/` mounted read-only and network disabled.
- `responsive shell works at phone width` passed at 375px.
- `responsive shell works at tablet width` passed at 768px.
- `responsive shell works at desktop width` passed at 1440px.
- `phone width restacks tables, decisions, and field view` passed.
- `desktop controls keep spacing and tap targets` passed at 1365px.

Verified behavior:
- Visible buttons meet the 44px minimum target in the tested desktop walkthrough screens.
- Action rows keep at least 16px row and column gaps.
- Desktop top-bar control groups keep at least 12px separation.
- No horizontal scroll or console/runtime errors were detected.

## 2026-06-13

Three-build split checks.

Static checks run:
- `node --check demo/internal/app.js` passed.
- `node --check demo/corvinum/app.js` passed.
- `node --check demo/jober/app.js` passed.
- `node --check tests/responsive.spec.js` passed.
- `node --check playwright.config.js` passed.
- Parsed `demo/internal/index.html`, `demo/corvinum/index.html`, and `demo/jober/index.html` with Python `html.parser`; passed.
- Scanned `demo/internal`, `demo/corvinum`, and `demo/jober` for persistence APIs, remote script/style URLs, remote URLs, and CSS `@import`; no matches.

Source separation:
- `grep -ri jober demo/corvinum/` returned no output.
- `grep -ri corvinum demo/jober/` returned no output.

Playwright results:
- Built the pinned Docker image with `docker build -f Dockerfile.playwright -t hr-system-playwright-tests:1.60.0 .`.
- Ran the suite with `demo/` mounted read-only, `test-artifacts/` writable, and network disabled.
- `client builds have source-level name separation` passed.
- CorvinumEU build passed at 375px, 768px, and 1440px.
- Jober build passed at 375px, 768px, and 1440px.
- Phone-width table/card and decision-stack behavior passed in both client builds.

Visual review:
- Reviewed `test-artifacts/corvinum-desktop.png`.
- Reviewed `test-artifacts/corvinum-phone.png`.
- Reviewed `test-artifacts/jober-desktop.png`.
- Reviewed `test-artifacts/jober-phone.png`.

Known issues:
- `test-artifacts/` contains generated screenshots, Playwright report files, and failure artifacts from an earlier failed run before the Jober role strip/layout fix. The final run passed.

## 2026-06-13

Language switch checks.

Static checks run:
- `node --check demo/internal/app.js` passed.
- `node --check demo/corvinum/app.js` passed.
- `node --check demo/jober/app.js` passed.
- `node --check tests/responsive.spec.js` passed.
- Parsed all three build `index.html` files with Python `html.parser`; passed.
- Scanned `demo/internal`, `demo/corvinum`, and `demo/jober` for persistence APIs, remote script/style URLs, remote URLs, and CSS `@import`; no matches.

Source separation:
- `grep -ri jober demo/corvinum/` returned no output.
- `grep -ri corvinum demo/jober/` returned no output.

Playwright results:
- Built the pinned Docker image with `docker build -f Dockerfile.playwright -t hr-system-playwright-tests:1.60.0 .`.
- Ran the suite with `demo/` mounted read-only, `test-artifacts/` writable, and network disabled.
- `language switch works in all builds` passed: internal, CorvinumEU, and Jober each switched to Slovak and Hungarian and showed translated primary headings.
- Full suite result: 9 passed.

Visual review:
- Re-opened the generated CorvinumEU and Jober desktop/phone screenshots after adding language controls.
- Confirmed no top-bar overflow in desktop screenshots.
- Confirmed Jober phone exposes Language directly; CorvinumEU phone keeps Language reachable through the menu drawer.

Known issues:
- Some deeper mock data/audit prose remains English by design. The spec now records that mock names, company names, dates, phone numbers, and audit data may remain fixed unless explicitly localized later.
