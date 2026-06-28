# Build Journal

## 2026-06-28 — Phase 3 (1/n): compliance alerts

Fulfils the manager's earlier explicit ask (alerts for missing/expiring papers); plan §3 / §11.9.

- `apps/compliance`: `Certificate` (metadata only — dates, no file storage, matching the demo decision).
- `services.compliance_alerts(viewer)`: surfaces **missing / expiring / expired** papers across workers — medical derived from the latest readiness **entry-medical date** + `MEDICAL_VALIDITY_MONTHS`; certificates by `expiry_date`; window = `COMPLIANCE_ALERT_DAYS` (the ~11/23-month pattern = ~1 month before a 12/24-month validity). Coordinator-scoped (own active-project people); managers/observers see all. `add_months` helper (no external dep).
- Compliance page on a new nav tab; certificate admin; settings `MEDICAL_VALIDITY_MONTHS` / `COMPLIANCE_ALERT_DAYS` (env-overridable). i18n SK/HU/UK.

Verification: ruff clean; **145 unit tests pass** (8 new: add_months clamping, missing medical, expired/expiring/far-future certs, valid recent medical, login required, coordinator scoping).

## 2026-06-28 — Phase 2 (6/6): approved SMS messaging (Phase 2 complete)

Twilio SMS over the **standard library** — no SDK, no new dependency (ADR 0019).

- `apps/messaging`: `MessageTemplate` (manager-managed), `OutboundMessage`, `InboundMessage`.
- `services.py`: `_twilio_send` (urllib Basic-auth POST to Twilio `Messages.json`; creds from env, `SmsNotConfigured` when unset → recorded `failed`, never faked); `send_sms` (records + audits); `verify_twilio_signature` (base64 HMAC-SHA1, `compare_digest`).
- Inbound webhook (`/webhooks/twilio/inbound/`): `csrf_exempt`, unauthenticated, **signature-verified, fails closed (403)**; stores inbound messages.
- Send gated by `sms.send`; **coordinator-scoped** (a coordinator may only message people on their own projects). Templates manager-managed. No Telegram.
- UI: a Send-SMS panel on the person card (template select or free text + recent messages). Settings: `TWILIO_ACCOUNT_SID/AUTH_TOKEN/FROM_NUMBER` from env. i18n SK/HU/UK.

Live sending requires the operator to set the Twilio env vars and expose the webhook publicly; tests mock the network call.

Verification: ruff clean; **137 unit tests pass** (9 new: sent on provider OK, fail-closed when unconfigured, signature accept/reject, webhook 403/200, RBAC, coordinator scope allow/deny); production image builds with all apps.

**Phase 2 build items complete** (person card/history/search, dashboards, project/coordinator routing, complete trials/full readiness, exports, approved SMS).

## 2026-06-28 — Phase 2 (5/n): full readiness (N/A reasons + entry-medical date)

- `ReadinessRecord`: added `accommodation_na_reason` / `transport_na_reason`.
- `update_readiness`: accommodation/transport now **require an explicit reason when marked N/A** (plan §11.6); accepts and stores the **entry-medical date**.
- Readiness panel: per-pillar N/A reason inputs + an entry-medical date field.
- i18n SK/HU/UK.

Verification: ruff clean; **128 unit tests pass** (N/A-requires-reason, entry-medical-date saved; existing readiness tests updated to supply reasons).

## 2026-06-28 — Phase 2 (4/n): project/coordinator routing

- The Trials queue and the dashboard's pending-trials list are now **scoped to a coordinator's own projects** (via `project.responsible_coordinators`); managers, observers, and recruiters still see all (broad read).

Verification: ruff clean; **126 unit tests pass** (2 new: coordinator sees only their projects' trials; manager sees all).

## 2026-06-28 — Phase 2 (3/n): permission-controlled CSV exports

- `apps/core/exports.py`: `people_csv`, `projects_csv` (gated `export.approved` — manager + observer) and `finance_csv` (gated `finance.view_summary`). Clean non-prefixed download URLs.
- Exports deliberately **exclude bulk sensitive fields** (DOB, disability, identifiers); those stay on the per-person card behind `can_view_sensitive`.
- Gated **Export** buttons on the People, Projects, and Finance pages. i18n SK/HU/UK.

Verification: ruff clean; **124 unit tests pass** (6 new: CSV content + content-type for manager/observer, 403 for recruiter, anonymous redirect).

## 2026-06-28 — Phase 2 (2/n): real dashboard

Replaced the Phase 0 mock dashboard (hardcoded 8/14/6 + mock field panel) with live aggregates.

- `apps/core/views.dashboard`: real counts — active projects, available, working, trials awaiting outcome — plus a list of pending trials.
- `dashboard.html`: clickable metric cards (link to the filtered People list / Projects / Trials) and a real pending-trials panel.
- Retired the mock `field_queue` view/route/partial and `PROJECT_CARDS`; updated the e2e smoke (it asserted the old mock) to check the real metric cards.
- i18n: "Awaiting outcome" (SK/HU/UK).

Verification: ruff clean; **118 unit tests pass** (1 new: dashboard shows real metrics + pending trial); **Playwright smoke 5 pass**; dashboard screenshot reviewed (live counts + pending trial).

## 2026-06-28 — Phase 2 (1/n): person card history + search filter

First Phase 2 slice (full person card / history / search).

- `apps/people/services.py` `person_history(person)`: a newest-first unified timeline assembled from trials (scheduled + outcome), project assignments, room assignments, equipment issues, readiness submissions, intake completion, and the append-only audit log's lifecycle changes.
- Person card: a **History** panel rendering that timeline.
- People list: a **lifecycle-status filter** alongside the existing name search.
- i18n SK/HU/UK for the new strings.

Verification: ruff clean; **117 unit tests pass** (2 new: history is newest-first and covers the key event types; the status filter narrows the list). Browser-reviewed the card history + filtered list.

## 2026-06-28 (later) — Hard-gated intake engine (Phase 1 complete)

Replaces intake-lite with the real questionnaire engine (§11.3 / §12.1). This was the last open Phase 1 build item.

- `apps/intake`: versioned questionnaire (`IntakeQuestionnaireVersion → IntakePanel → IntakeQuestion`) and `RecruitmentIntake → IntakeAnswer`.
- Engine (`services.py`): `start_intake`, `save_panel`, `complete_intake`.
  - **Sequential, server-driven panels** — `save_panel` always acts on `intake.current_panel_order`, so panels can't be bypassed by URL/forged POST.
  - **Required** answers enforced server-side; **typed-negative** questions reject a blank field (no checkbox bypass) and recognise accepted "no/none" words (normalized); **conditional** questions are required only when their parent answer is positive.
  - Completion maps stable_keys → Person fields and creates an `AVAILABLE` Person owned by the recruiter; audited.
- Seed `seed_questionnaire` (published "Recruiter intake" v1: Identity / Contact / Compliance with a typed-negative disability question + conditional disability type). `dev_app.sh up` seeds it.
- UI: `intake_start` → sequential `intake_panel` wizard (step X/Y, prefilled, per-field errors); "Add person" now starts the real intake. Admin for questionnaire authoring. i18n SK/HU/UK.

Verification: ruff clean; **93 unit tests pass** (6 new: required blocks advance, typed-negative can't be blank, accepted-negative skips the conditional + completes, positive requires the conditional, full completion creates an Available person, completed intake rejects further panels). Browser walkthrough of the wizard reviewed.

Phase 1 status: **all build items complete.** (Questionnaire *content* + per-language typed-negative phrases remain configurable/Tier-2; the manager-approval→coordinator-activation change is ADR 0018.)

## 2026-06-28 (later) — Minimal financial month (Phase 1)

Completes the deferred peripheral modules. Sign convention flagged as an
assumption (Phase 4 blocker).

- `apps/finance`: `FinancialMonth` (project/year/month, revenue, cost, lock; unique per project-month). `net = revenue - cost` documented as an **assumption** to confirm from one filled month (open-decisions). `company_totals` sums **dynamically** over all projects/months — never hardcoded — to avoid the manager's spreadsheet bugs.
- Services `record_financial_month` (update_or_create; rejects edits to a locked month) and `company_totals`.
- UI: a Finance summary page (totals + months + record form), gated `finance.view_summary` (manager + observer); the nav tab and record form are role-gated; `finance.manage` for writes. Admin; `seed_people` seeds two months. i18n SK/HU/UK.

Verification: ruff clean; **87 unit tests pass** (5 new: net, dynamic totals, idempotent month, locked-month rejection, RBAC).

## 2026-06-28 (later) — Weekly transport reporting (Phase 1)

- `apps/logistics`: `TransportWeek` (project + week_start + headcount; unique per project/week).
- Service `record_transport_week` (update_or_create, audited).
- UI: a Weekly transport panel on the project detail — recent weeks + a record form, gated by `transport.record`. Admin. i18n SK/HU/UK.

Verification: ruff clean; **82 unit tests pass** (3 new: create, idempotent per week, RBAC).

## 2026-06-28 (later) — Minimal inventory / equipment (Phase 1)

- `apps/logistics`: `EquipmentItem` catalog (name/size; no valuation — Phase 3) and `EquipmentIssue` (quantity, issued/returned).
- Services `issue_equipment` / `return_equipment` (audited).
- UI: an Equipment panel on the person hub — issue (item + quantity) and return, gated by `equipment.issue_return` (coordinator + manager).
- Admin; `seed_people` seeds a small catalog. i18n SK/HU/UK.

Verification: ruff clean; **79 unit tests pass** (3 new: issue, return, RBAC).

## 2026-06-28 (later) — Minimal accommodation (Phase 1)

First of the deferred peripheral modules. Minimal per Phase 1 (no rates/valuation; those are Phase 3, open-decisions).

- `apps/logistics`: `Accommodation`, `Room` (capacity + occupancy/is_full), `RoomAssignment` with a DB one-active-room-per-person constraint.
- Services `assign_room` (capacity-enforced, closes prior active room, audited) / `release_room`.
- UI: Accommodation list/detail (occupancy) on a new nav tab; an assign/release-room panel on the person hub, gated by `room.assign` (coordinator + manager).
- Admin for all three; `seed_people` now also creates an accommodation with rooms and houses the Working seed person.
- i18n: logistics strings translated SK/HU/UK and compiled.

Verification: ruff clean; **76 unit tests pass** (5 new: occupancy, capacity enforcement, one-active-room reassignment, release, RBAC).

## 2026-06-28 (later) — Core Phase 1 workflow (demo cut)

Made the intake → trial → readiness → activation vertical clickable end-to-end
for tomorrow's customer demo. Deferred the peripheral minimal modules (room,
inventory, transport, finance).

What changed:
- **Trials** (`apps/projects`): `TrialAssignment` (§11.5, append-preserving) + `schedule_trial` (handoff, requires Available → Trial day) and `record_trial_outcome` (pass keeps Trial day; fail/no-show recycles to Available, §12.3).
- **Readiness + activation**: `ReadinessRecord` (four pillars; medical+gear required, accommodation/transport may be N/A; `is_ready`); `update_readiness` (rejects medical/gear N/A) and `activate_from_readiness` — the **system-enforced** coordinator activation (ADR 0018); CARGO/manager override still possible via direct `activate_on_project`.
- **Intake-lite**: recruiter `PersonForm` + `person_create` (gated `intake.create_edit`), "Add person" on the People list.
- **UI**: the person detail is now a **state-driven workflow hub** (assign-trial → record-outcome → readiness pillars → activate), a coordinator **Trials** queue wired to the Field nav, and a shell messages region. All actions gated with `require_action` + `{% can %}`.
- i18n: translated all new workflow/readiness/intake strings (SK/HU/UK) and recompiled.
- `scripts/dev_app.sh up` now also runs `seed_people` so the demo stack is populated.

Verification: ruff clean; **71 unit tests pass** (11 new workflow tests incl. the full path to Working); **Playwright drove the entire demo path** (add person → trial → fail/recycle → re-trial → pass → readiness → activate → Working) and screenshots were reviewed — all in Slovak.

Demo path: log in (manager does everything) → People → Add person → Schedule trial → Fail (recycles) → Schedule trial → Pass → Four-pillar readiness → Activate → Working on project.

## 2026-06-28 (later) — Project UI

Read-only Project list + detail, mirroring the People pattern.

What changed:
- `apps/projects/views.py`: `project_list` and `project_detail` (login-gated). Detail shows code/partner/office/responsible coordinators/financial-reporting eligibility plus the active **Workers** on the project, each linked to their person page.
- Templates `pages/project_list.html` + `pages/project_detail.html`; wired the **Projects** nav tab to the route and added `/projects/`, `/projects/<id>/`. Small `.plain-list` CSS.
- i18n: translated the new project UI strings (SK/HU/UK) and recompiled.
- Verified live (manager): list shows the three seeded projects with active status; DHL Bratislava detail lists the assigned worker linked back to People.

Verification: ruff clean; **60 unit tests pass** (3 new project view tests); screenshots reviewed.

## 2026-06-28 (later) — People UI

Surfaced the Person spine in the app (read-only), the lowest-hanging next slice.

What changed:
- `apps/people/views.py`: `people_list` (login-gated broad read, name search) and `person_detail`, which renders sensitive fields (DOB, place of birth, disability) only when `can_view_sensitive` allows (Q4); otherwise a restricted note.
- Templates `pages/people_list.html` + `pages/person_detail.html` reusing the existing panel/field-card CSS; added a **People** nav tab and `/people/`, `/people/<id>/` routes.
- Small CSS: `.people-search`, `.person-row`, `.detail-grid`.
- i18n: translated the new operational UI strings (lifecycle status labels + People page) in SK/HU/UK and recompiled; admin-only model field labels fall back to English for now.
- Verified live (manager): list shows seeded people with translated statuses; detail shows the restricted panel with disability for a permitted viewer.

Verification: ruff clean; **57 unit tests pass** (5 new view tests incl. sensitive masking); screenshots of list + detail reviewed.

Next step:
- Recruiter intake (hard-gated) or trials + the readiness gate (which activates ADR 0018 enforcement).

## 2026-06-28

Phase 1 business spine — Person + lifecycle + project administration.

What changed:
- Added `apps/people`: `Person` with the canonical 5-state lifecycle (`AVAILABLE / TRIAL_DAY / WORKING / INACTIVE / BLACKLISTED`, plan §9.1), validated transition helper `set_status` (audited), search-normalized name, archive, **disability as a flag only** (no documents, Q1), and `owning_recruiter`.
- Added `apps/projects`: `Project` (project↔coordinator many-to-many) and `ProjectAssignment` with a DB-level **one-active-assignment-per-person** constraint (§11.4); placement service `activate_on_project` / `end_assignment` (atomic, audited, history-preserving).
- **Sensitive-field visibility** (`apps/people/permissions.can_view_sensitive`, Q4): DOB/place-of-birth/disability visible to managers, observers, owning recruiter, and responsible coordinator(s); hidden from unconnected recruiters/coordinators.
- RBAC: added `project.assign` (coordinator + manager, Q2); updated `permission-matrix.md`.
- Admin for Person/Project/ProjectAssignment; fictional `seed_people` (3 projects, 5 people, one Working via assignment; no real PII).
- ADR 0018: coordinator-activated, **system-enforced** readiness gate replaces the §11.6/§12.4 manager-approval step (CARGO override retained). Readiness-gate enforcement + alert layer attach with `ReadinessRecord` (next slice).

Decisions baked in: phase1-open-questions Q1–Q4 + the activation-gate answer.

Verification: ruff clean; **52 unit tests pass** (lifecycle transitions, one-active-assignment + history, sensitive visibility, placement RBAC); migrate + seed_demo + seed_people run clean on pinned PostgreSQL.

Next step:
- Recruiter intake (hard-gated, typed-negative) and the Person card/list UI; then trials and the readiness gate + manager alerts.

## 2026-06-21

Phase 1 — foundation slice: authentication, four-role RBAC, localization, append-only audit.

What changed:
- Added `apps/accounts` with a custom `User` (email login, custom manager, removed `username`) carrying a single fixed `role` field (`Role`: recruiter/coordinator/manager/observer). Set `AUTH_USER_MODEL = "accounts.User"` before any business migration.
- Added action-gated RBAC in `apps/accounts/permissions.py`: an `Action` enum, an `ACTION_ROLES` map derived literally from plan §8.2–8.5 (with the inverse `ROLE_ACTIONS`), `can()`, a `require_action()` view decorator (redirect anonymous, 403 authenticated-but-denied), and a `{% can %}` template tag so hidden buttons are backed by real server checks.
- Kept reads broad by default behind a single `BROAD_INTERNAL_READS` switch (env `JOBER_BROAD_INTERNAL_READS`) so the still-open GDPR recruiter/coordinator read-scope decision is not hardcoded (open-decisions.md).
- Added `apps/audit`: append-only `AuditEvent` (immutable `save()` on update, `delete()` raises) and `record_event()` as the single write path; wired into login/logout. Read-only admin.
- Replaced the static login view with real email/password auth (`apps/accounts/views.py`), gated `dashboard`/`field_queue` with `login_required`, added a logout button and a language switcher to the base template.
- Wrapped app routes in `i18n_patterns` and added the `set_language` route; `healthz/` stays unprefixed.
- Added `seed_demo`/`reset_demo` management commands creating one fictional user per role on the `demo.jober.test` domain (no real PII; asserted).
- Added `docs/permissions/permission-matrix.md` (mirrors `ACTION_ROLES`) and ADR 0015 (custom user model).
- Generated `accounts`/`audit` initial migrations inside the digest-pinned image.
- Made `SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE` env-overridable (secure by default) so the HTTP-only internal smoke network can exercise authenticated flows; `playwright_smoke.sh` now seeds demo users and the smoke suite logs in.

Decisions made:
- Custom user model introduced now while the DB held only contrib migrations — the last cheap moment (ADR 0015).
- No business modules (Person, intake, trials) in this slice; the permission matrix is authored ahead so future views adopt the correct gate from day one.

Deferred:
- Translation catalogs (`.po`/`.mo`) are not generated/compiled in this slice: `msgfmt`/`xgettext` are absent on the host and gettext is not in the hardened image, and all source UI strings are already Slovak (the default locale), so non-default languages fall back to Slovak msgids. The i18n machinery (prefixes, `set_language`, switcher) is fully wired and tested. Generating + compiling catalogs is a follow-up once gettext tooling is approved in the toolchain.

Follow-up (2026-06-21) — static serving fix:
- Manual browser testing surfaced an unstyled shell: the production image (gunicorn) served no static files, so CSS/htmx/Alpine/app.js all returned the HTML 404 page (`text/html`, blocked by nosniff). Phase 0 smoke never requested an asset, so it was hidden.
- Adopted WhiteNoise 6.12.0 (ADR 0016): `whitenoise.middleware.WhiteNoiseMiddleware` after SecurityMiddleware + `CompressedManifestStaticFilesStorage`, enabled in production settings only (local runserver/tests don't need it). Hash-pinned in `runtime.lock` and `test.lock`; pinned `certifi`/`greenlet` back to vetted versions so the lock diff is WhiteNoise-only (no cooldown-window pulls).
- Made `SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE` env-overridable (secure by default) so the HTTP-only smoke network can run authenticated flows.
- Added a Playwright regression (`test_static_css_is_served`) asserting the stylesheet serves `200 text/css`. Verified the live image serves `app.css` fingerprinted as `200 text/css`.

Follow-up (2026-06-21) — production admin path:
- Added `manage.py ensure_superuser`: idempotent, env-driven (`DJANGO_SUPERUSER_EMAIL`/`DJANGO_SUPERUSER_PASSWORD`) Manager/Administrator superuser for non-interactive Dokku deploys; audited; `--skip-if-unset` for optional release steps. Created if absent, flags repaired if demoted, password left untouched on redeploy.
- Wired into the Dokku release steps (`docs/deployment/dokku-staging.md`); marked the admin gate Ready in the production-readiness journal. `seed_demo` stays fictional/staging only.
- Verified all paths (create / idempotent / repair / skip) in the production image.

Follow-up (2026-06-23) — internationalization:
- Switched the codebase base language to **English** while keeping **Slovak as the visible default** (`LANGUAGE_CODE=sk`, ADR 0017). Rewrote all template/Python `gettext` source strings (and CLI/exception/dev messages) from Slovak to English.
- Added English to the switcher (now EN/SK/HU/UK). Authored full **SK/HU/UK** catalogs (`locale/<lang>/LC_MESSAGES/django.po`) and compiled `.mo`; the SK catalog reproduces the previous Slovak text exactly, so the default rendering and existing tests are unchanged. HU/UK + revised SK are AI-authored, pending fluent-speaker review.
- gettext is not in the runtime/test images; `scripts/compile_messages.sh` runs the app image with gettext apt-installed to extract/compile. Runtime image now `COPY`s `locale/`.
- Regenerated the `accounts`/`audit` initial migrations (verbose-name/choice-label changes). Added `tests/test_i18n.py` (renders EN/SK/HU/UK + default redirect). Verified all four languages live on the login page.

Next step:
- Phase 1 business spine: project administration and the Person model + lifecycle-status state machine, then hard-gated intake.

What changed:
- Removed tracked Node/PNPM/JavaScript Playwright artifacts from the production tree: `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `Dockerfile.playwright`, `playwright.config.js`, and the old JS Playwright spec.
- Added an npm-free Django skeleton: `manage.py`, `config/`, `apps/core/`, templates, static source files, and a health endpoint.
- Added a Jober-only server-rendered shell with folder-tab navigation, Slovak UI strings, local asset references, and a mobile coordinator htmx interaction that also works as a normal full-page request.
- Vendored htmx `2.0.4` and Alpine `3.15.12` as local static assets with licenses and SHA-256 checksums.
- Added supply-chain scripts:
  - `scripts/check_no_node_artifacts.py`
  - `scripts/verify_vendor_assets.py`
  - `scripts/build_tailwind.sh`
- Added the Tailwind standalone CLI v4.3.0 provenance manifest and local convenience request.
- Added Phase 0 product docs: source register, open decisions, demo inventory, removed-feature inventory, demo-to-Django map, risk/blocker list, and Dokku staging skeleton.
- Added the required Phase 0 ADR set for scope, architecture, htmx/Alpine, Tailwind, npm exclusion, Python Playwright, RBAC, demo reuse, project assignment, and Pohoda exclusion.

Decisions made:
- The old static demo stays in the repo as a design reference, but the new production skeleton does not import Corvinum, shared-client structure, shifts, sick leave, worker portal, or Pohoda.
- Docker is intentionally not completed in this slice because base-image digests must come from trusted/human-approved sources before execution or commit.
- Python dependencies were not installed on the host. The hash-pinned lock remains a Phase 0 blocker until generated in an approved container/CI workflow.

Next step:
- Resolve base-image digests and the Python dependency lock, then add the Docker/CI path and run the Django shell against PostgreSQL.

Follow-up:
- Verified the local Tailwind standalone CLI at `/home/disane/.local/bin/tailwindcss`.
- Confirmed it reports v4.3.0 and observed SHA-256 `73f0e5459054e5cfaa8ab6f3b940f3fbe0f13cc7fd83bc24e7c655033c203400`.
- Ran `scripts/build_tailwind.sh`; it built `static/dist/css/app.css` successfully.
- Updated the base template to load the compiled CSS output.

Infrastructure follow-up:
- Resolved Python base image digest: `python@sha256:d764629ce0ddd8c71fd371e9901efb324a95789d2315a47db7e4d27e78f1b0e9`.
- Resolved PostgreSQL test image digest: `postgres@sha256:2203e6282d9e7de7c24d7da234e2a744fb325df366a3fd8ed940e8abbee39527`.
- Added `requirements/runtime.in`, `requirements/test.in`, and generated hash-pinned `requirements/runtime.lock` / `requirements/test.lock` inside the digest-pinned Python container.
- Added `Dockerfile`, `Procfile`, and `pytest.ini`.
- Built `jober-platform:phase0` successfully; Docker build installs runtime dependencies from hash-pinned wheels and runs `collectstatic`.
- Verified Django migrations against a temporary digest-pinned PostgreSQL 17 container and checked `/healthz/` from the running image.
- Added Django smoke tests in `tests/test_shell.py`.
- Tried Playwright-Python browser smoke; package install and Chromium download worked, but browser launch failed in the slim Python image because `libglib-2.0.so.0` is missing. Documented the decision in `docs/product/playwright-test-environment-note.md`.
- Resolved the browser-test blocker by pinning the official Playwright Python test image:
  `mcr.microsoft.com/playwright/python:v1.60.0-noble@sha256:8ff591d613b01c884cc488339ed4318b4513eaf0c57a164a878ba49e70e3f384`.
- Confirmed the image has no `node`, `npm`, `pnpm`, or `yarn` on `PATH`.
- Added `scripts/playwright_smoke.sh` and wired it into `scripts/ci_phase0.sh`.
- Added `Dockerfile.playwright-python` to build a test-only runner image that installs `requirements/test.lock` with hash enforcement and runs as a non-root user.
- Playwright browser smoke now runs app, PostgreSQL, and test runner on an internal-only Docker network. The browser reaches the app at `http://jober-phase0-app:8000`.
- Playwright browser smoke passed against a temporary digest-pinned PostgreSQL 17 container and the built production app image.

Local development database follow-up:
- Added `scripts/dev_db.sh` for workstation PostgreSQL without host installation.
- The script uses digest-pinned PostgreSQL 17, an internal Docker network, a named Docker volume, a containerized `psql` helper, and a generated gitignored `.env.dev-db`.
- Verification showed a loopback DB port is not reachable from the host when this Docker daemon attaches the container only to an internal network, so the helper intentionally keeps PostgreSQL off the host network.
- Added `docs/deployment/local-dev-db.md`.
- Updated the open-decision register to keep recruiter/coordinator read scopes configurable until Jober answers the GDPR visibility question.

Tailwind provenance follow-up:
- Confirmed the exact workstation version is `tailwindcss v4.3.0`.
- Confirmed official Tailwind Labs release `https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.3.0` exists.
- Pulled the official release `sha256sums.txt` and found the Linux x64 line:
  `73f0e5459054e5cfaa8ab6f3b940f3fbe0f13cc7fd83bc24e7c655033c203400  ./tailwindcss-linux-x64`.
- Confirmed the existing local binary matches the official checksum.
- Added `vendor/tailwind/tailwindcss-v4.3.0-linux-x64.sha256`.
- Added `scripts/fetch_tailwind.py`, `scripts/check_production_image.sh`, and `scripts/ci_phase0.sh`.
- Updated the Dockerfile so the `tailwind` build stage fetches the pinned official binary, verifies the official checksum before execution, builds CSS, and excludes the binary from the final runtime image.
- Added ADR 0013 documenting why the expected checksum comes from the vendor's `sha256sums.txt`, not from a self-derived local hash.

## 2026-06-13

Built the v1 static HR operations demo inside `demo/`.

What changed:
- Added `demo/index.html`, `demo/styles.css`, and `demo/app.js`.
- Implemented the CorvinumEU default theme and live Jober theme switch with CSS custom properties.
- Implemented the global top bar, role switch, client switch, sidebar, guided manifest rail, and decision capture panel.
- Implemented the full guided sequence: sign in, dashboard, staffing decision, blacklist risk check, work test approval, shift and transport decision, fake SMS, second shift, sick leave, certificate hard-stop, mobile manager view, and Jober module reveal.
- Added Jober-only Accommodation, Equipment, and Pohoda dashboard screens.
- Kept all demo state in plain in-memory JavaScript. No persistence APIs, backend, dependencies, remote scripts, remote styles, or media assets were added.

Design decisions:
- Followed the local `demo/frontend-design/SKILL.md` direction by grounding the interface in workforce logistics: manifests, rosters, risk gates, shifts, buses, and document stops.
- Used the manifest rail as the single aesthetic risk. It works as both guided stepper and operational route strip, so the memorable visual device carries product meaning instead of decoration.
- Used the approved token palettes from the plan for CorvinumEU and Jober.
- Used Option A typography: system stacks that prefer Michroma, Noto Sans, and JetBrains Mono only when already present on the machine.
- Self-critique outcome: removed the narrow-layout promotion of the manifest rail after screenshot review because it hid the active screen on mobile. The mobile layout now places the active screen first.

Deferred:
- No real media assets or font files. Option B self-hosted fonts can be added only if the human delivers the files and licenses.
- No real SMS, authentication, database, or Pohoda connection.

Next step:
- Review the demo in a normal browser window before the meeting and tune copy or screen density if the presenter wants a different walkthrough rhythm.

## 2026-06-13

Responsive retrofit and spec filename fix.

What changed:
- Renamed `demo/demo_prototype_build_specs.md` to the canonical `demo/demo_prototype_build_spec.md` so the file on disk matches `AGENTS.md` / `CLAUDE.md` references.
- Retrofitted the shell for tablet and phone without rebuilding the demo: desktop keeps the three-column layout above 1024px.
- Added a hamburger drawer for tablet/phone navigation and moved mobile Client / Role controls into that drawer.
- Converted the right Live manifest rail into a collapsible top progress strip below 1024px, with all 12 stops reachable.
- Restacked dense tables into labelled cards at phone width.
- Made decision cards stack vertically on phone.
- Made the manager field view read as a phone-native screen at phone width rather than a desktop page containing a heavy phone mockup.
- Added spacing and tap-target CSS tokens so controls have more consistent gaps and phone buttons are easier to hit.
- Added isolated Playwright test tooling at the repo root, outside `demo/`, using the pinned Docker workflow.

Decisions made:
- Used a hamburger drawer instead of bottom tabs because Jober adds too many nav items for a reliable thumb tab bar.
- Used 1024px as the shell breakpoint and 640px as the phone/card breakpoint.
- Kept the manifest as the signature element by adapting it to a mobile progress strip instead of hiding it.
- Used Playwright, not Puppeteer, because repo policy defines a specific Playwright-in-Docker workflow.

Deferred:
- No new media, fonts, framework, runtime dependency, backend, or production scaffold.

Next step:
- Review the responsive demo manually on the actual presentation phone and laptop for meeting-specific pacing and density.

## 2026-06-13

Desktop spacing and tap-target cleanup.

What changed:
- Tightened the shared spacing system in `demo/styles.css` with reusable control, action-row, and stack-gap tokens.
- Increased shared buttons and segmented switch buttons to a 44px minimum hit target.
- Added consistent separation after form grids, status badges, alert/callout blocks, message boxes, and action rows so buttons no longer sit flush against nearby content.
- Increased decision-card padding/gaps and form-field gutters to keep dense screens readable without changing the desktop shell.
- Added a Playwright regression check that verifies visible button height and control spacing across the desktop walkthrough screens.

Decisions made:
- Fixed the issue at the component spacing layer instead of tuning each screen separately, because the cramped controls came from repeated action-row and callout patterns.
- Kept the existing desktop information architecture and responsive breakpoints intact.

Next step:
- Review the updated pages on the presentation laptop to confirm the spacing matches the desired meeting-room density.

## 2026-06-13

Split the demo into internal, CorvinumEU-only, and Jober-only builds.

What changed:
- Moved the existing combined demo unchanged into `demo/internal/`.
- Created `demo/corvinum/` as a CorvinumEU-only static build with its own `index.html`, `styles.css`, and `app.js`.
- Created `demo/jober/` as a Jober-only static build with its own `index.html`, `styles.css`, and `app.js`.
- Removed the client switch from both client-facing builds.
- Removed all Jober-only strings/modules/data from the CorvinumEU build source.
- Removed all CorvinumEU references from the Jober build source.
- Gave Jober a different primary IA: folder-style tabs for Operations, People, Compliance, Logistics, Accounting, and Reports; nested sections live under each folder.
- Replaced Jober's right-side manifest rail with a slim numbered step bar under the folder tabs.
- Made Accommodation, Equipment, and Pohoda normal Jober tabs rather than licensed extras.
- Updated `AGENTS.md`, `demo/demo_prototype_build_spec.md`, `deployment_journal.md`, and the Playwright suite for the three-build structure.

Decisions made:
- Kept CorvinumEU close to the original operational rail/sidebar layout because that is the requested client-facing shape.
- Treated Demand as an Operations sub-section in Jober because the guided story needs the staffing decision before dispatch planning.
- Kept the internal build as the only place where the platform/resale client switch is visible.

Verification:
- `grep -ri jober demo/corvinum/` returned no output.
- `grep -ri corvinum demo/jober/` returned no output.
- The pinned Docker Playwright suite passed with 8 tests across phone, tablet, and desktop.
- Visual screenshots were reviewed for CorvinumEU and Jober at desktop and 375px.

Next step:
- Open the two client builds on the actual meeting laptop/phone and decide whether Jober's Demand sub-section should stay under Operations or move elsewhere.

## 2026-06-13

Added English, Slovak, and Hungarian language switching to all demo builds.

What changed:
- Added an in-memory EN / SK / HU language switch to `demo/internal/`, `demo/corvinum/`, and `demo/jober/`.
- Wired the switch through primary navigation, role labels, guided controls, decision labels, page headings, table headers, and status badges.
- Kept the language choice intentionally non-persistent; it resets on reload like the other demo state.
- Kept the Jober folder-tab grouping data-driven while translating labels at render time.
- Updated `AGENTS.md`, `demo/demo_prototype_build_spec.md`, and the Playwright suite to cover language switching.

Decisions made:
- Mock names, company names, phone numbers, dates, and most audit/demo data remain fixed source data for now; the language layer focuses on the UI and presentation surface.
- CorvinumEU keeps the language switch inside the mobile drawer, alongside Role. Jober shows Role and Language directly in the mobile top area because it has no drawer.

Verification:
- `grep -ri jober demo/corvinum/` returned no output.
- `grep -ri corvinum demo/jober/` returned no output.
- The pinned Docker Playwright suite passed with 9 tests, including language switching in all three builds.

Next step:
- Review Slovak and Hungarian wording with a fluent speaker before client presentation if exact business terminology matters.

## 2026-06-13

Expanded Slovak and Hungarian coverage for the client demos.

What changed:
- Added the missing Slovak/Hungarian strings for the CorvinumEU-only and Jober-only builds across story callouts, audit rows, mobile card labels, table values, document states, and action labels.
- Added a small render-time localization pass in both client builds so existing literal panels and `data-label` values localize without refactoring every template.
- Localized Jober-only Logistics and Accounting surfaces, including Accommodation, Equipment, sizes, and Pohoda metrics.
- Updated the language spec to require client-facing callout prose, audit lines, mobile labels, and module labels to translate.
- Added a Playwright regression that checks deeper translated screens, not only the dashboard heading.

Decisions made:
- Names, company names, phone numbers, and fixed dates remain unchanged mock data.
- The internal combined demo was left as-is for this pass because the request targeted the two client-facing demos.

Verification:
- `grep -ri jober demo/corvinum/` returned no output.
- `grep -ri corvinum demo/jober/` returned no output.
- The pinned Docker Playwright suite passed with 10 tests, including the deeper Slovak/Hungarian coverage check.

Next step:
- Have a Slovak/Hungarian speaker review business terminology before presenting if exact wording matters.

## 2026-06-14

Coordinator role and answered product decisions.

What changed:
- Added the distinct Coordinator role to `demo/internal/`, `demo/corvinum/`, and `demo/jober/`.
- Enforced Coordinator as a real logistics-only permission boundary: CorvinumEU exposes only transport logistics; Jober exposes transport, accommodation, and equipment logistics.
- Filtered Coordinator navigation and guided steps so HR-only screens are not reachable.
- Removed HR/approval data from Coordinator-rendered DOM, including hire status, blacklist status, documents/certificates, work-test/approval content, and audit history.
- Updated the shift flow to be shifts-first: once Hired, a worker is directly shift-eligible, with no contract/signing step.
- Changed transport capacity from an open A/B decision to an answered client decision: vehicle-specific capacity is enforced and full vehicles block future assignments.
- Changed certificate storage from an open A/B decision to metadata only: type, issue date, expiry date, and valid/invalid status; no file upload or retention.
- Kept Demand model as the only open interactive A/B gate.
- Tightened the internal top bar so the added Coordinator role does not cause desktop overflow after switching the internal build to Jober.
- Updated `AGENTS.md`, `demo/demo_prototype_build_spec.md`, and the Playwright suite.

Decisions made:
- Treated Coordinator as not having dashboard access because the current dashboards contain HR/approval metrics. Coordinator defaults to the logistics shift/dispatch view instead.
- Kept Jober Coordinator Logistics access data-driven through the existing folder/tab configuration.
- Applied the pasted clarification because `shared_hr_platform_architecture.md` is referenced by the task/spec but is not present on disk.

Verification:
- `grep -ri jober demo/corvinum/` returned no output.
- `grep -ri corvinum demo/jober/` returned no output.
- The pinned Docker Playwright suite passed with 11 tests, including a Coordinator DOM-absence test across internal, CorvinumEU, and Jober at 375px and desktop.
- Coordinator screenshots were generated for internal, CorvinumEU, and Jober at phone and desktop widths.

Next step:
- Confirm with the clients whether Coordinator should remain dashboard-free or receive a separate logistics-only dashboard later.

## 2026-06-14

Decision drawer regression added.

What changed:
- Added an explicit Playwright regression that opens the decision drawer in internal, CorvinumEU, and Jober and verifies:
  - Demand model is still unanswered.
  - Transport capacity is answered as `A - Enforce capacity`.
  - Certificate storage is answered as `B - Dates only`.

Verification:
- The pinned Docker Playwright suite passed with 12 tests.
