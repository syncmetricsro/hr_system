# Test Journal

## 2026-06-29 — Inactive reasons + exit recycling

- **Full suite: 198 passed** (up from 192), e2e excluded, on the `jober-test` image against the dev PostgreSQL.
- New `tests/test_inactive_recycle.py` (6 tests): the `0003` data migration seeds the Q5 placeholders; exit-to-inactive records the structured `inactive_reason` + `inactive_since`; `recycle_to_available` clears them and returns the person to Available; recycle raises for a non-Inactive person; RBAC (recruiter/coordinator/manager allowed, observer not) for `person.recycle_available`; the recycle view is 403 for observer and 302 → Available for a coordinator.
- `ruff check apps config tests` clean. Migrations `0002` (schema) + `0003` (seed) build under pytest. SK/HU/UK catalogs recompiled (de-fuzzed the new strings).

## 2026-06-29 — Phase 3 equipment deduction-review queue

- **Full suite: 192 passed** (up from 184), e2e excluded, on the `jober-test` image against the dev PostgreSQL.
- New `tests/test_equipment_review.py` (8 tests): flag snapshots the charge at `qty × unit_price` and keeps the item ISSUED; cannot flag a returned/already-flagged item; approve/waive records reviewer + note; review requires pending state + a valid decision; the pending-queue total is dynamic and excludes resolved items; `exit_person` auto-returns un-flagged items but **leaves flagged items PENDING** for the queue; manager-only RBAC; the queue view is 403 for coordinator, 200 for manager.
- `ruff check apps config tests` clean (fixed two E702 semicolon lines in the new test). Migration `0006_equipmentissue_charge_amount_and_more` builds under pytest. SK/HU/UK catalogs recompiled (de-fuzzed ~15 msgmerge mis-matches; set the wrapped long "reporting only" string by hand).

## 2026-06-29 — Phase 3 accommodation pricing

- **Full suite: 184 passed** (up from 177), e2e excluded, on the `jober-test` image against the digest-pinned dev PostgreSQL. (The dev DB/network had been torn down by a host reboot; recreated with `scripts/dev_db.sh up` and ran with those credentials.)
- New `tests/test_accommodation_pricing.py` (7 tests): `set_room_rate` persists; `effective_rate` uses the override then falls back to the room rate (and clears); the cost report computes `room_cost` (standing, all rooms) vs `assigned_cost` (Σ effective over active assignments) + company totals; released assignments drop out of occupancy/assigned cost while standing room cost remains; manager-only RBAC; the cost view is 403 for recruiter + coordinator and 200 for manager; the set-rate view persists.
- `ruff check apps config tests` clean. Migration `0005_room_monthly_rate_roomassignment_rate_override` builds under pytest. SK/HU/UK catalogs recompiled (de-fuzzed ~11 msgmerge mis-matches, e.g. "Cost report", "Room cost").

## 2026-06-29 — Phase 4 finance lock/reopen + rollups

- **Full suite: 177 passed** (up from 173), e2e excluded, on the `jober-test` image against the digest-pinned dev PostgreSQL.
- Added to `tests/test_finance_lineitems.py`: lock blocks `set_line_item`; reopen rejects a blank reason and re-enables edits; the reopen reason is written to the audit `reason` field; the save view no-ops on a locked month (302, nothing written); `project_totals`/`yearly_totals`/`company_totals` aggregate correctly incl. a year filter and an empty-year zero.
- `ruff check apps config tests` clean. No new migration (reuses `is_locked`). SK/HU/UK catalogs recompiled; removed two fuzzy mis-matches msgmerge introduced for "Lock month"/"Reopen month".

## 2026-06-29 — Phase 4 finance line items

- Built a `jober-test` image from the hash-pinned `requirements/test.lock` (Python 3.12, to match the lock's wheel hashes) and ran pytest against the digest-pinned dev PostgreSQL over the internal `jober-dev-net`.
- **Full suite: 173 passed** (up from 166), e2e Playwright excluded (those run via the dedicated Playwright image).
- New `tests/test_finance_lineitems.py` (7 tests): `recompute_month` sums by kind; **dynamic recompute covers every cost row** (guards the spreadsheet off-by-one); `set_line_item` updates in place; locked month blocks `set_line_item` + `recompute_month`; `group_breakdown` nets revenue−cost per group; save view persists + recomputes; detail view returns 403 to recruiters.
- `ruff check apps config tests` clean. Migration `0002_financecategory_financelineitem` builds under pytest; SK/HU/UK catalogs recompiled.

## 2026-06-29 — Twilio SMS live verification (manual)

Manual end-to-end check of the messaging slice against real Twilio, secrets via Doppler.

- **Auth isolation:** `doppler run -- curl … Messages.json` returned **401** with a mismatched SID/token pair, then **201** after correcting the pair in Doppler — confirming the failure was credentials, not the app.
- **In-app, Test credentials + magic number** (`+15005550006`): Send SMS recorded **Sent** (fail-closed when unconfigured was also observed first — correct behaviour).
- **In-app, Live credentials + trial number** (`+1928…`) → Twilio **Virtual Phone** (`+18777804236`): message **Delivered** (Twilio Messaging Logs) and visible in the Virtual Phone simulator.
- Verified the gated **Send SMS** panel (phone-gated, `sms.send`, coordinator-scoped) and the new **Edit-person** form used to set the recipient phone.

Conclusion: messaging works end-to-end in production form. Outstanding items are operational only (account upgrade to drop the trial prefix; public inbound webhook URL).

## 2026-06-28 (later) — Per-view RBAC gating

- `tests/test_view_gating.py`: parametrized over every gated write/read endpoint (assign_trial, trial_outcome, readiness_update, activate_person, assign_room, issue_equipment, return_equipment, record_transport, finance_record, finance_summary, intake_start) — a denied role gets **403** and anonymous is **redirected to login**. Closes the gap where the new POST endpoints were only covered by the generic `require_action` test.
- **Full unit suite: 115 passed**; ruff clean.

## 2026-06-28 (later) — Phase 1 peripheral modules + hard-gated intake

Added across the accommodation, inventory, transport, finance, and intake slices; figures are cumulative as each landed.

- `tests/test_logistics.py` (rooms): capacity enforcement, occupancy, one-active-room reassignment, release, RBAC.
- `tests/test_inventory.py`: issue, return, RBAC.
- `tests/test_transport.py`: weekly record, idempotent per week, RBAC.
- `tests/test_finance.py`: net, dynamic company totals across projects, idempotent month, locked-month rejection, RBAC.
- `tests/test_intake.py`: required blocks advance, typed-negative can't be blank, accepted-negative word completes + skips the conditional, positive answer requires the conditional, full completion creates an Available person, completed intake rejects further panels.
- **Full unit suite: 93 passed**; ruff clean; all SK/HU/UK catalogs compile.
- Production image rebuilt with all six business apps; migrations apply cleanly (pytest builds the test DB from them). Browser walkthroughs reviewed: full activation path, accommodation/finance pages, and the intake wizard.

## 2026-06-28 (later) — Core Phase 1 workflow

- Generated `projects` migration 0002 (TrialAssignment + ReadinessRecord).
- Added `tests/test_workflow.py` (11): trial schedule sets Trial day; schedule requires Available; fail/no-show recycle; pass keeps Trial day + Completed; second trial keeps history; double outcome rejected; readiness ready only when required complete + optional complete/N/A; medical cannot be N/A; activation blocked until ready; **full path to Working**.
- Translated + recompiled all new workflow/readiness/intake strings (SK/HU/UK); catalogs compile cleanly.
- **Full unit suite: 71 passed** (was 60); ruff clean.
- **End-to-end browser walkthrough** (Playwright, manager) of the whole demo path succeeded: add person → schedule trial → fail (recycle) → schedule trial → pass → readiness (medical+gear complete, accommodation/transport N/A) → activate → Working on DHL Bratislava. Readiness + Working screenshots reviewed (Slovak).

## 2026-06-28 (later) — Project UI

- Added `tests/test_project_views.py` (3): list requires login; list shows a project; detail lists assigned workers.
- Translated + recompiled new project UI strings (SK/HU/UK), no duplicate-msgid errors.
- **Full unit suite: 60 passed** (was 57); ruff clean.
- Live check: `/projects/` and `/projects/<id>/` render in Slovak; DHL Bratislava detail lists the assigned worker linked to their person page. Screenshots reviewed.

## 2026-06-28 (later) — People UI

- Added `tests/test_people_views.py` (5): list requires login; list shows a person; detail shows sensitive data to a manager and to the owning recruiter; detail hides it from an unconnected recruiter.
- Extracted + translated new UI strings (SK/HU/UK) and recompiled `.mo` cleanly (no duplicate-msgid errors).
- **Full unit suite: 57 passed** (was 52); ruff clean.
- Live check on the rebuilt image: `/people/` and `/people/<id>/` render in Slovak with translated lifecycle statuses; manager sees the restricted personal-data panel (disability shown). Screenshots reviewed.

## 2026-06-28

Phase 1 spine — Person + lifecycle + projects.

- Generated `people` / `projects` initial migrations in the digest-pinned image.
- Added `tests/test_people.py` (15 tests): search-name normalization; valid transition audited + invalid transition raises `LifecycleError`; activation creates one active assignment and sets `WORKING`; reassignment keeps exactly one active and retains history; DB unique-active constraint rejects a second active assignment (`IntegrityError`); `end_assignment` returns to `AVAILABLE`; sensitive-field visibility for oversight/owner/responsible-coordinator vs unconnected; `project.assign` role mapping.
- **Full unit suite: 52 passed** (was 37); ruff clean.
- End-to-end on pinned PostgreSQL: `migrate` + `seed_demo` + `seed_people` (3 projects, 5 people, one Working via assignment) all clean.

## 2026-06-21

Phase 1 foundation slice checks (auth, RBAC, localization, audit).

Checks run:
- Generated `accounts`/`audit` migrations via `manage.py makemigrations` inside the digest-pinned app image (no models missed; both `0001_initial` created).
- `ruff check apps config scripts tests manage.py` passed in the hash-pinned test image (with `RUFF_CACHE_DIR=/tmp/ruff`).
- `pytest tests/test_shell.py tests/test_rbac.py tests/test_auth.py tests/test_audit.py` — **32 passed** against a digest-pinned PostgreSQL 17 container using the hash-pinned test lock, settings `config.settings.local`.
  - RBAC: `can()` matches the matrix per role/action; anonymous denied all; `ROLE_ACTIONS` is the consistent inverse of `ACTION_ROLES`; every `Action` is mapped; `require_action` redirects anonymous, raises `PermissionDenied` for the wrong role, allows the permitted role.
  - Auth: login success/failure, logout redirect, login writes an `auth.login` audit event, manager sees the gated "Spravovať projekty" button while observer does not, language switch resolves the `/hu/` prefix, dashboard requires login.
  - Audit: `record_event` writes rows (actor/target/metadata); anonymous actor stored as `None`; updating an existing `AuditEvent` and deleting one both raise `AuditError`.
- `docker build -t jober-platform:phase1 .` passed (collectstatic ran with the new apps/templates).
- `scripts/check_no_node_artifacts.py` passed; `scripts/check_production_image.sh jober-platform:phase1` passed (no Node/Tailwind binary in runtime).
- `scripts/playwright_smoke.sh` (APP_IMAGE=jober-platform:phase1) — **4 passed**: it now seeds demo users, the mobile shell logs in then loads the field queue, the health endpoint returns `ok`, the login page renders, and the app root bounces unauthenticated visitors to login. App container ran with `DJANGO_SESSION_COOKIE_SECURE=0`/`DJANGO_CSRF_COOKIE_SECURE=0` because the internal smoke network is HTTP-only.
- Verified seed data is fictional only (`@demo.jober.test`); no real PII.

Follow-up (2026-06-21) — static serving fix:
- Regenerated `runtime.lock` and `test.lock` in the digest-pinned Python image with `whitenoise==6.12.0` (transitive `certifi`/`greenlet` pinned back so the diff is WhiteNoise-only).
- Rebuilt `jober-platform:phase1` and `jober-platform-playwright:phase1`.
- `ruff check` clean; **unit tests 32 passed** (no warnings after moving WhiteNoise to production-only settings).
- **Playwright smoke 5 passed**, including the new `test_static_css_is_served` (stylesheet returns `200 text/css`).
- `check_no_node_artifacts.py` and `check_production_image.sh jober-platform:phase1` passed.
- Verified against the live local stack: `app.css` serves `200 text/css` with a fingerprinted (manifest) filename.

Follow-up (2026-06-21) — production admin path:
- Added `tests/test_ensure_superuser.py` (create, idempotent re-run, repair of a demoted account, error when env unset, `--skip-if-unset`). **Full unit suite 37 passed**; ruff clean.
- Verified `ensure_superuser` in the rebuilt production image: create → "Vytvorený superuser", re-run → "už existuje a je v poriadku", no-env `--skip-if-unset` → skipped cleanly.

Follow-up (2026-06-23) — internationalization:
- Regenerated migrations + extracted/compiled catalogs in the app image with gettext (via `scripts/compile_messages.sh`).
- Added `tests/test_i18n.py`: dashboard renders the expected string in EN/SK/HU/UK and the unprefixed root redirects to `/sk/`. **Full unit suite 42 passed**; ruff clean.
- Rebuilt `jober-platform:phase1` (now ships compiled `.mo`); **Playwright smoke 5 passed** (SK default unchanged).
- Verified live: login `<h1>` renders correctly per prefix — EN "Sign in to the Jober team", SK "Prihlásenie tímu Jober", HU "Bejelentkezés a Jober csapatba", UK "Вхід до команди Jober".

Expected current gaps:
- HU/UK + revised SK translations are AI-authored, pending fluent-speaker review.
- Dokku staging still pending external server/domain/DB-service details.

## 2026-06-17

Phase 0 static/supply-chain checks.

Checks run:
- `python3 scripts/check_no_node_artifacts.py`
- `python3 scripts/verify_vendor_assets.py`
- `python3 -m py_compile manage.py config/asgi.py config/wsgi.py config/urls.py config/settings/base.py config/settings/local.py config/settings/production.py apps/core/apps.py apps/core/views.py scripts/check_no_node_artifacts.py scripts/verify_vendor_assets.py`
- `git diff --check`
- `TAILWIND_BIN=/home/disane/.local/bin/tailwindcss TAILWIND_SHA256=73f0e5459054e5cfaa8ab6f3b940f3fbe0f13cc7fd83bc24e7c655033c203400 scripts/build_tailwind.sh`
- Official Tailwind Labs `v4.3.0` `sha256sums.txt` was checked. The local `tailwindcss-linux-x64` binary matched the official SHA-256.
- Docker Tailwind build-stage verification passed during image build.
- `scripts/check_production_image.sh jober-platform:phase0` passed, confirming no Tailwind binary or Node/npm artifacts in the runtime image.
- `scripts/ci_phase0.sh` passed. This runs the no-Node scan, vendor checksum verification, Python syntax checks, `docker build --no-cache`, and runtime image artifact check. The no-cache build exercised the Tailwind official-checksum verification stage.
- `scripts/playwright_smoke.sh` passed. It uses `mcr.microsoft.com/playwright/python:v1.60.0-noble@sha256:8ff591d613b01c884cc488339ed4318b4513eaf0c57a164a878ba49e70e3f384`, verifies no Node/npm-family binary on `PATH`, verifies `playwright==1.60.0` in the hash-pinned test lock, builds a non-root test-runner image, starts production app + PostgreSQL + browser runner on an internal-only Docker network, and runs `tests/e2e/test_shell_smoke.py` with Chromium.
- Negative guard check passed: `scripts/check_production_image.sh` exits non-zero against the digest-pinned Playwright Python test image and reports forbidden `/ms-playwright` browser files. The same script remains green against `jober-platform:phase0`.
- `scripts/dev_db.sh up`, `status`, `url`, `psql`, `reset --yes`, and `down` passed. The script created an internal Docker network, generated gitignored local credentials, kept PostgreSQL off the host network, provided containerized `psql` access, and used the digest-pinned PostgreSQL image.
- A loopback DB port was tested and removed from the helper because it was not reachable while the DB container was attached only to an internal Docker network.
- Runtime lock generated in Docker and verified with `pip install --require-hashes -r requirements/runtime.lock`.
- Test lock generated in Docker and verified with `pip install --require-hashes -r requirements/test.lock`.
- `docker build -t jober-platform:phase0 .` passed.
- `docker run --rm ... jober-platform:phase0 python manage.py check` passed.
- Temporary PostgreSQL 17 container accepted `python manage.py migrate --noinput` from the app image.
- Running app container returned `ok` from `/healthz/`.
- `pytest tests/test_shell.py` passed inside the digest-pinned Python container with the hash-pinned test lock.
- `ruff check apps config scripts tests manage.py` passed inside the digest-pinned Python container with the hash-pinned test lock.

Expected current gaps:
- Dokku staging remains pending until the staging app/domain/PostgreSQL service details are available.

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

## 2026-06-13

Client translation coverage retrofit.

Static checks run:
- `node --check demo/corvinum/app.js` passed.
- `node --check demo/jober/app.js` passed.
- `node --check tests/responsive.spec.js` passed.
- Parsed `demo/corvinum/index.html` and `demo/jober/index.html` with Python `html.parser`; passed.
- Scanned `demo/corvinum` and `demo/jober` for persistence APIs; no matches.
- Scanned `demo/corvinum` and `demo/jober` for remote URLs and CSS `@import`; no matches.

Source separation:
- `grep -ri jober demo/corvinum/` returned no output.
- `grep -ri corvinum demo/jober/` returned no output.

Playwright results:
- Built the pinned Docker image with `docker build -f Dockerfile.playwright -t hr-system-playwright-tests:1.60.0 .`.
- Ran the suite with `demo/` mounted read-only, `test-artifacts/` writable, and network disabled.
- `client language switch covers deeper operational screens` passed for CorvinumEU and Jober in Slovak and Hungarian.
- Full suite result: 10 passed.

Known issues:
- Names, company names, phone numbers, and fixed dates intentionally remain unchanged mock data. Client-facing UI prose, callouts, audit text, mobile labels, and module labels now translate in the two client builds.

## 2026-06-14

Coordinator role and answered-decision regression checks.

Static checks run:
- `node --check demo/internal/app.js` passed.
- `node --check demo/corvinum/app.js` passed.
- `node --check demo/jober/app.js` passed.
- `node --check tests/responsive.spec.js` passed.
- `node --check playwright.config.js` passed.
- Parsed `demo/internal/index.html`, `demo/corvinum/index.html`, and `demo/jober/index.html` with Python `html.parser`; passed.
- Scanned all three builds for persistence APIs, remote script/style URLs, remote URLs, CSS `@import`, `fetch`, `XMLHttpRequest`, and `sendBeacon`; no matches.

Source separation:
- `grep -ri jober demo/corvinum/` returned no output.
- `grep -ri corvinum demo/jober/` returned no output.

Playwright results:
- Built the pinned Docker image with `docker build -f Dockerfile.playwright -t hr-system-playwright-tests:1.60.0 .`.
- Ran with `demo/` mounted read-only, `test-artifacts/` writable, and `--network none`.
- Full suite result: 11 passed.
- New regression passed: Coordinator role removes HR/approval data from the DOM across internal, CorvinumEU, and Jober at 375px and desktop.

Verified behavior:
- Coordinator defaults to logistics views, not HR dashboards.
- CorvinumEU Coordinator exposes transport logistics only.
- Jober Coordinator exposes Operations logistics plus Accommodation and Equipment.
- Coordinator DOM does not include HR/approval screens or text such as blacklist, work test, manager approval, document queue, certificate metadata, Pohoda, hire status, or approval history.
- Transport capacity shows Enforce as the answered decision and blocks full vehicles.
- Certificate storage shows Dates only / metadata only as the answered decision.
- Demand model remains the only interactive A/B decision.
- No horizontal scroll at the tested widths; internal Jober/Coordinator was additionally checked at 1365px and 1440px.
- No console/runtime errors were detected by Playwright.

Visual review artifacts:
- `test-artifacts/internal-phone-coordinator.png`
- `test-artifacts/internal-desktop-coordinator.png`
- `test-artifacts/corvinum-phone-coordinator.png`
- `test-artifacts/corvinum-desktop-coordinator.png`
- `test-artifacts/jober-phone-coordinator.png`
- `test-artifacts/jober-desktop-coordinator.png`

Known issues:
- `shared_hr_platform_architecture.md` is still absent from the repo, so this implementation followed the pasted clarification.

## 2026-06-14

Decision drawer answered-state regression.

Additional check added:
- `answered product decisions appear in the decision drawer` verifies all three builds show Demand as unanswered, Transport capacity as `A - Enforce capacity`, and Certificate storage as `B - Dates only`.

Playwright result:
- Rebuilt the pinned Docker image and reran the suite with `demo/` read-only, `test-artifacts/` writable, and `--network none`.
- Full suite result: 12 passed.
