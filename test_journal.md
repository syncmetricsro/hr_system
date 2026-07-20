# Test Journal

## 2026-07-20 — Settlement seam and ledger entry dates

- Full Jober/default unit lane: **390 passed, 2 skipped**. The new
  flag-toggle test proves bulk inclusion skips open cash advances only when
  `wage_ledger` is enabled and keeps the original behavior for a client
  running advances standalone.
- Full Corvinum-flags lane: **232 passed, 7 skipped, 139 deselected**. New
  coverage: the reworked inclusion test settles a deduction through the bulk
  path, and the ledger form round-trips a backdated post-20th entry date into
  the deferral rule, defaults to today when omitted, and rejects an
  unparseable date without creating an entry.
- Ruff clean. SK/HU/UK catalogs updated for the two new strings ("Entry
  date", the wage-aware include-cycle confirmation); both msgmerge fuzzy
  pairings per locale corrected; zero fuzzy or empty entries.
- Complete Playwright suite after the ledger-form changes: **40 passed**.

## 2026-07-19 — Advance recovery, reconciliation overview, admin sweep

- Full Jober/default unit lane: **389 passed, 2 skipped** (both skips are the
  Corvinum-only wage modules, intentionally uninstalled for Jober).
- Full Corvinum-flags lane: **230 passed, 7 skipped, 139 deselected** — +15 new
  tests. New coverage: suggested-recovery-period rule on both sides of the 20th
  including December→January, rejection of wage months earlier than the cycle
  end (later months allowed), audited assignment driving the advance's
  OPEN → INCLUDED_IN_CYCLE transition via the advances service, non-advance and
  already-assigned guards, partial-amount bounds, the one-active-recovery
  conditional constraint (inactive rows exempt), derived-net math with mixed
  DEDUCT/ADD entries and proof no net field is persisted, overview rendering
  for wage-only / advances-only / neither people, the Δ mismatch marker
  appearing only on disagreeing months, observer payslip nav + read-only page
  with manage controls hidden and POST 403, coordinator/recruiter payslip 403s
  with no nav entry, recovery-assignment view permissions, and no Django-admin
  registration for any money model (WageEntry, AdvanceRecovery, LedgerEntry,
  Payslip).
- Ruff clean; `check_dependency_direction.py` clean (no core→feature imports);
  `makemigrations --check` clean under Corvinum settings.
- SK/HU/UK catalogs re-extracted; 16 msgmerge fuzzy mispairings per locale
  corrected by hand (e.g. "Computed net" → "Dokončené"), zero fuzzy or empty
  entries remain; compiled and re-verified in both lanes.
- Complete Playwright suite: **40 passed**. The observer wage scenario now
  also asserts the Advance recoveries section is visible read-only (no assign
  forms for the observer) and scopes its table assertion to the recorded-wages
  table, since the wages page grew two recovery tables.

## 2026-07-18 — CorvinumEU gross-wage ledger

- Full Jober/default unit lane: **389 passed, 1 skipped**. The skipped module is
  the intentionally uninstalled Corvinum wage feature; Jober policy
  completeness and explicit absence of wage routes remain covered.
- Full Corvinum-flags lane: **215 passed, 7 skipped, 139 deselected**. New
  coverage verifies positive and unique wage records, append-only audit data,
  Manager write access, Observer read-only access, Coordinator/Recruiter 403s,
  duplicate form rejection, feature/permission hiding, Gross-vs-Net period
  alignment, deterministic provider order, and idempotent paired demo seeds.
- Complete Playwright suite: **40 passed**. The new browser scenario signs in
  as the Corvinum Observer, reviews seeded wages, follows Marek to the aligned
  person overview, checks translated Gross/Net columns, and confirms the wide
  table scrolls locally without causing page overflow at 375×667.
- Ruff, Django system checks, migration consistency, dependency direction,
  vendored-asset integrity, forbidden Node/npm artifacts, production-image
  runtime exclusions, translation compilation, and whitespace checks all
  passed.

## 2026-07-17 — Composite blacklist fingerprint

- Full unit suite in the pinned test container: **388 passed**, including nine
  new blacklist/intake tests. New coverage: diacritic folding with ASCII hash-stability, canonical composite
  format and token-order insensitivity, type+hash matching in `check_matches`,
  inactive-until-approved composite fingerprints with no raw maiden name
  stored, person-create composite match without an ID code, both-tier match
  reasons, locale-aware "Matched via" queue rendering, optional maiden name on
  manual proposal, and intake composite re-entry with the transient value never
  persisted as an answer.
- Corvinum-flags lane (`scripts/test_corvinum.sh`): **209 passed, 7 skipped**.
  The queue-rendering test asserts against the response's own locale because
  Corvinum ships only SK/HU.
- Ruff clean across core/features/clients/config/tests.
- The full-suite run exposed a pre-existing RBAC completeness failure
  (`person.archive` unmapped for Jober) on the base branch; fixed in this
  slice and the suite is green again.
- Complete Playwright suite after the i18n compile: **39 passed** with the new
  compiled catalogs and both client seeds.

## 2026-07-16 — In-place activation-checklist toggles

- Corvinum checklist unit slice: **8 passed**, including the existing
  full-page redirect and the new htmx fragment response with updated critical
  count, completion state, and staff attribution.
- Relevant Ruff check passed for the checklist view, unit coverage, and browser
  scenario.
- Complete Playwright suite: **39 passed**. The Corvinum browser test now
  verifies CSRF remains present, the person URL is unchanged, the updated
  checklist is rendered, and scroll position is preserved after clicking a
  checklist item.
- Public `corvinum-staging` acceptance after deploying image
  `jober-platform:corvinum-demo-6abdb56`: Dokku container checks passed, no
  migrations remained, and HTTPS health, Slovak login, and CSS routes returned
  200.

## 2026-07-15 — CorvinumEU public staging smoke verification

- Verified the fictional `corvinum-staging` deployment on syncmetric-prime:
  Gunicorn running on port 8000; HTTPS `/sk/` unauthenticated redirect to the
  Slovak login; HTTPS login `200`; secure Corvinum CSRF cookie; and static CSS
  `200 text/css`.
- Applied migrations and seeded published Recruiter intake v3 plus the
  fictional CorvinumEU scenario.
- Provider-backed staging acceptance also passed: the read-only,
  config-scoped Doppler SMTP runtime configuration delivered an encrypted
  fictional payslip PDF to the controlled test inbox. No provider credential,
  recipient, service-token value, or one-time PDF password was logged.

## 2026-07-15 — Payslip resend recipient and SMTP-error handling

- Added coverage for resending to the prior successful recipient after a
  person-email change, plus SMTP recipient rejection becoming a safe
  `PayslipError` without recording a delivery.

## 2026-07-15 — Corvinum sidebar icon-subset guard

- Added a template guard that rejects sidebar Material Symbol names absent from
  the committed self-hosted font subset, preventing raw ligature text from
  appearing in navigation.

## 2026-07-15 — Equipment catalogue permissions and workflow

- Added manager create/search/edit/deactivate coverage with audit entries and
  explicit coordinator 403 assertions for catalogue routes.

## 2026-07-15 — Optional intake email

- Added intake coverage for a valid optional email, invalid-email rejection,
  and blank-email completion; the value maps to the person email field only
  after the questionnaire is completed.

## 2026-07-15 — CorvinumEU trial-day route and policy activation

- Added Corvinum client-surface assertions for the mounted trial queue/create
  routes and scheduling/outcome grants. The client still excludes finance,
  accommodation, transport, and SMS routes.
- Focused Corvinum policy validation passed: **6 tests** plus Django system
  checks and Ruff for the changed client/test surfaces.

## 2026-07-15 — Corvinum blacklist archive and re-entry workflow

- Added coverage proving an approved case remains matchable after operational
  archive and that guided intake creates a new proposed case from the same
  transient ID without storing the raw value in IntakeAnswer.
- Focused Corvinum validation passed: **34 passed, 1 Jober-only test
  deselected**; migration consistency, Ruff for the changed surfaces, and
  whitespace checks also pass. The local production-style Corvinum image
  rebuilt successfully, applied the transient-question migration, seeded
  questionnaire v2, and returned OK from the health endpoint.

## 2026-07-15 — Corvinum Basic deployment-script contracts

- Added structural tests that require encrypted off-site PostgreSQL exports,
  prohibit Dokku-config export, lock 35-daily/12-monthly retention, enforce
  the 26-hour/60% backup-health defaults, and keep staging operations explicit
  (`start`, `stop`, `status`).
- Focused Corvinum deployment-script tests pass: **3 passed**. Shell syntax,
  Ruff for the new test, Django’s Corvinum settings check, and whitespace
  validation are clean.
- The scripts still require a real deployment host, registered SSH host key,
  imported public GPG recipient, and provider-owned infrastructure for a live
  transfer/restore drill; those checks cannot be truthfully run locally.

## 2026-07-15 — Corvinum SMTP runner boundary

- Added a regression contract proving the Corvinum demo runner keeps
  migrations/seeds on console email and supplies provider variables only to the
  long-running web container.
- Verification passed: `bash -n scripts/corvinum_app.sh`; focused Corvinum
  client suite **6 passed**; Ruff passed; the seven required variables were
  present in `hr_system/dev_corvinum_demo`; non-secret SMTP transport settings
  matched FORPSI; application health returned `ok`; and an authentication-only
  SMTP connection opened successfully. No email was sent by the connection
  check and no secret value was printed.

## 2026-07-15 — Authentication client-identity isolation

- Seven focused template/client tests pass, covering configured Corvinum name
  and logo rendering, absence of Jober from the rendered login response,
  hard-coded identity exclusion across shared pages, and shared branding on
  login plus both TOTP screens.
- The production-style Corvinum image rebuilt successfully. A live response
  check confirms the Corvinum login contains its own name and fingerprinted
  logo and no Jober text; the targeted Chromium identity scenario passes.
- Ruff and whitespace checks are clean for the changed tests. Full-suite totals
  were not rerun for this focused pre-demo correction.

## 2026-07-15 — Corvinum personnel-intake bootstrap

- Added a bootstrap-order regression requiring `seed_questionnaire` before
  `seed_corvinum_demo`, preventing a clean database from rendering an Add
  person button that cannot start intake.
- Verified the running clean Corvinum database contains the published
  questionnaire and that its authenticated intake start redirects into the
  first questionnaire panel. Full-suite totals were not rerun for this
  bootstrap-only correction.

## 2026-07-14 — Operations data-entry workspaces

- Full verification is green: **358 Jober unit tests**, **179 CorvinumEU tests**
  (**7 skipped, 135 deselected**), and **38 Chromium Playwright scenarios**.
- New coverage exercises central trial scheduling/editing, coordinator project
  scope, transport create/edit/duplicate handling, manager-only location and
  room management, occupancy safety, audit old/new values, invalid filters,
  mobile form fit, and SK/HU/UK catalogue loading.
- The idempotent fictional seed now creates a real pending trial, five transport
  weeks across multiple projects, existing room occupancy, and equipment data.
- Ruff, Django checks, migration consistency, dependency direction,
  forbidden-Node, vendor integrity, production-image contents, and whitespace
  checks are clean. The browser suite applies the new migration from an empty
  database for both clients.

## 2026-07-14 — Jober panel clearance

- Added a shell contract test ensuring adjacent operational sections receive
  the shared spacing token instead of relying on feature-panel margins.
- Full Chromium verification passes **36 scenarios**. The browser regression
  measures at least 16px between the person-detail grid and its following panel
  in Jober Light, Jober Dark, and at the 375px mobile viewport.

## 2026-07-14 — Action-oriented dashboard tooltips

- Full verification is green: **346 Jober tests**, **178 CorvinumEU tests**
  (**7 skipped, 127 deselected**), and **35 Chromium Playwright scenarios**.
- Browser coverage verifies structured heading/body content, active-project and
  inactive-reason click-through filters, Jober Light/Dark tooltip surfaces,
  mobile hover/touch behavior, and the existing Corvinum theme treatments.
- A targeted **2-test Firefox run** passes for the complete structured dashboard
  flow and the shared hover/keyboard/touch contract. Firefox exposed and now
  covers focus-induced scrolling: keyboard tooltips remain visible and are
  repositioned while pointer-only tooltips still dismiss on scroll.
- Focused filter/tooltip coverage passes **35 tests**; the final shared tooltip
  contract passes **14 tests**. SK/HU/UK compiled catalogs contain every new
  dashboard heading, description, and filter label.
- Ruff, Django checks, migration consistency, dependency direction,
  forbidden-Node, vendored-asset checksum, and whitespace checks are clean.
  Both production-style clients were rebuilt and left running locally.

## 2026-07-13 — Language-prefix switching regression

- Full verification is green: **337 Jober tests**, **169 CorvinumEU tests**
  (**7 skipped, 127 deselected**), and **34 Chromium Playwright scenarios**.
- Added unit coverage for stale/missing language-cookie disagreement, all four
  Jober language prefixes, both Corvinum prefixes, preserved query strings,
  client-specific cookies, and rejection of a forged external `next` URL.
- The browser regression starts on a Hungarian URL without a matching cookie,
  selects English, and verifies the URL, document language, selector state, and
  `jober_language` cookie all agree. The Jober and Corvinum switch scenarios
  also pass in a targeted **2-test Firefox run**.
- Ruff is clean for the touched Python files. Both production-style local
  client images rebuilt and remain available on ports 8000 and 8001.

## 2026-07-13 — Shared contextual tooltips

- Full verification is green: **333 Jober tests**, **168 CorvinumEU tests**
  (**7 skipped, 124 deselected**), and **33 Playwright E2E scenarios** across
  both client shells.
- Browser coverage verifies hover delay, keyboard association and Escape,
  tooltip hover persistence, viewport clamping/flipping at 375×667, dynamically
  inserted content, confirmation-dialog compatibility, touch actions without a
  first-tap delay, and Corvinum light/dark computed colors.
- Unit coverage verifies both shells, contextual surface declarations, removal
  of migrated native titles, EN/SK/HU/UK detail labels, reduced motion, and WCAG
  AA contrast for all four client/mode tooltip pairs.
- Visually reviewed Jober Dark and Corvinum Dark with the sidebar collapsed.
  Ruff, Django checks, migration consistency, dependency direction,
  forbidden-Node, vendored-asset checksum, and whitespace checks are clean.

## 2026-07-13 — Theme-aware Jober logo color

- Added a contract for the dark-mode hue/saturation treatment and reran the
  focused theme/navigation lane: **9 tests pass**.
- Rebuilt and visually reviewed the anonymous dark header at 1440px. The SVG
  artwork renders periwinkle with a white inset, retains its natural aspect
  ratio, and Light mode continues to use the original blue rendering.

## 2026-07-13 — Jober after-hours dark palette

- Updated the dark-token WCAG contract for the graphite/aubergine panel,
  periwinkle interaction, mint success, amber warning, and coral danger pairs;
  all primary combinations remain at or above AA contrast.
- Focused theme/navigation lane passes **9 tests**. Rebuilt and visually
  reviewed the authenticated 1440×900 dashboard with the notification control
  and SVG navigation icons; the document has no horizontal page overflow.

## 2026-07-13 — Jober navigation icons

- Added a shell contract covering all fourteen client-owned SVG symbols,
  decorative accessibility semantics, and the absence of Corvinum's icon-font
  dependency. The focused theme/navigation lane passes **9 tests**.
- Rebuilt the production-style Jober image and visually reviewed desktop and
  375×667 mobile navigation. The mobile menu exposes 44px rows and introduces
  no horizontal page overflow.

## 2026-07-13 — Client appearance themes

- Test-tooling incident: an initial host `pybabel compile` command omitted
  Django's `django` catalog domain. Babel looked for non-existent
  `locale/<language>/LC_MESSAGES/messages.po` files and Ubuntu Apport reported
  its unhandled `FileNotFoundError`. No application process crashed and no
  catalog source was lost. Host Babel is now explicitly documented as outside
  the project workflow; catalog compilation belongs to the repository's
  containerized Django helper.
- Added contracts for client defaults, the supplied Jober SVG, semantic palette
  definitions, storage failure handling, and EN/SK/HU/UK theme labels.
- Added browser scenarios for persistence, login-to-app continuity, live System
  preference changes, cross-tab synchronization, client defaults, and mobile
  logo/overflow behavior.
- Full verification is green: **322 Jober tests**, **159 CorvinumEU tests**
  (**7 skipped, 122 deselected**), and **31 Playwright E2E scenarios** across
  both client shells. The focused theme lane adds **9 passing tests**, including
  WCAG AA contrast checks for the key semantic color pairs.
- Visually reviewed settled Jober light/dark and CorvinumEU light/dark pages at
  desktop and mobile sizes. Ruff, migration consistency, dependency direction,
  forbidden-Node, vendored-asset checksum, and whitespace checks are clean.

## 2026-07-13 — Floating notification center

- Full verification is green: **315 Jober tests**, **153 CorvinumEU tests**
  (**7 skipped, 121 deselected**), and **28 Playwright E2E scenarios** across
  both client shells.
- Added unit coverage for login baselines, other-user session updates, own-event
  exclusion, role/project scoping, observer exclusion, dismissal validation,
  state-version reappearance, CSRF, and htmx refresh headers.
- Added provider coverage for compliance, equipment reviews, blacklist cases,
  feedback, and activation checklists, including destination URLs and resolved
  state disappearance.
- Added browser coverage for Jober desktop/mobile and CorvinumEU mobile layout,
  panel interaction, dismissal, links, normal/manual refresh, and absence of
  idle polling. The browser suite also caught and now covers Corvinum's active
  document language and mobile ledger overflow regressions.
- Added translation assertions for EN/SK/HU/UK.
- Ruff, migration consistency, dependency direction, forbidden-artifact,
  vendored-asset checksum, and whitespace checks are clean.

## 2026-07-13 — Corvinum language, personnel email and Reports parity

- Corvinum client contract tests pass: its language selector writes the
  `corvinum_language` cookie and redirects `/sk/...` to `/hu/...`; its person
  form includes email. The shared person-edit regression is green (**5 tests**).
- Added browser coverage for the Corvinum language switch, interactive merged
  Reports page, and email input; the official E2E image rebuild/migration run
  was started, but needs its final uninterrupted browser execution.

## 2026-07-12 — Specific activation blockers

- **16 workflow tests green** in isolated PostgreSQL. Activation failures now
  list the concrete missing requirement and Hungarian localization is asserted;
  an N/A state without its reason cannot pass readiness.

## 2026-07-12 — Readiness attention guidance

- **14 workflow tests green** in isolated PostgreSQL, including rejection of a
  future entry-medical date. The readiness form's visual attention contract is
  covered by a shell regression; SK/HU/UK catalogs compile cleanly.

## 2026-07-12 — Localized audit actions

- **14 audit tests green** in isolated PostgreSQL. They prove the immutable
  machine code remains the filter value while the action dropdown and table
  render the translated label in EN/SK/HU/UK. Catalogs compile cleanly.

## 2026-07-12 — Consolidated reports and EUR presentation

- **31 focused PostgreSQL tests green** across dashboard/reports navigation,
  report drill-down links, role-sensitive links, accommodation pricing, and
  deduction-review workflows. Ruff and migration consistency are clean.

## 2026-07-12 — Trial appointment and scheduling-role refinement

- Isolated PostgreSQL regression run is green for the trial workflow, action
  permission gates, and shared shell checks. It covers a persisted trial
  appointment, recruiter/coordinator scheduling access, manager denial, and
  the neutral outcome-action contract.
- `makemigrations projects --check --dry-run`, translation compilation
  (SK/HU/UK), Ruff, and `git diff --check` are clean.

## 2026-07-12 — Pricing, localized history, sensitive-field and toast refinement

- Added focused regressions for localized lifecycle/equipment history, clearing
  a disability type when the flag is unset, and the shared three-second flash
  notification contract. Translation catalogs compile cleanly for SK/HU/UK;
  Ruff is clean for the changed Python and tests.
- Full browser rerun is pending: the local development PostgreSQL volume no
  longer matches its local-only `.env.dev-db` credential, so it cannot create
  the temporary pytest database. The isolated E2E runner rebuilt both current
  images and reached the dual-database migration/seed stage before this session
  was interrupted; it needs one fresh uninterrupted rerun before release.

## 2026-07-12 — Corvinum test lane

- **Jober lane 283 · corvinum lane 143 (7 skipped, 100 deselected) · e2e 21**
  — all green; ruff clean.
- Marker discipline: `jober_only` = asserts Jober URLs/policies/seeds/
  languages; modules importing not-installed feature models guard with
  `pytest.skip(allow_module_level=True)` (marker can't stop collection
  imports).
- Real fix: order-dependent translation leak (thread-local active language)
  — global autouse locale-pin fixture in tests/conftest.py.

## 2026-07-12 — Observability slice

- **283 unit + 21 e2e green** (4 new: manager+observer see /audit/,
  coordinator 403, actor/action/target filters — asserted via row-only
  reason strings since the action dropdown always lists every known action —
  and the LOGGING config contract).
- Live: observer logins on both stacks render the audit page (SK/HU titles),
  39 event rows on the Jober demo; container confirms console logging.

## 2026-07-12 — Session longevity

- **279 unit + 21 e2e green** (3 new: 30d rolling policy, per-client cookie
  names, login sets `jober_sessionid` with max-age == SESSION_COOKIE_AGE;
  corvinum subprocess check asserts its names). One user-written corvinum e2e
  assertion updated from `csrftoken` → `corvinum_csrftoken` (the rename IS
  the intended change).
- Live proof: single cookie jar, logins on :8000 and :8001 — both sessions
  authenticated simultaneously; jober cookie max-age ≈ 30.0 days.

## 2026-07-12 — Corvinum shell, section rhythm, checklist + ledger regression

- **276 unit + 22 e2e green** (four new Corvinum browser regressions; the
  official E2E runner now serves both clients).
- At 1650px: sidebar is 280px; the complete `CorvinumEU PeopleOps` wordmark
  ends at x=247.94 inside it; the 1280px main column spans x=325–1605 and is
  centered at x=965 in the remaining viewport; horizontal overflow is zero.
- The same test collapses the sidebar to its 72px rail and verifies the main
  column re-centers, then switches to 375×667 and verifies full-width content
  with zero horizontal overflow.
- Project detail verifies a **16px** vertical gap from the top-level overview
  grid to the following logistics panel, preventing adjacent borders from
  visually merging.
- A coordinator opens the seeded person's checklist, verifies both the
  `csrfmiddlewaretoken` input and CSRF cookie, toggles an item through the
  rendered POST form, and confirms redirect back to the person page with no
  CSRF failure.
- Ledger coverage verifies compact labelled year/month controls, aligned action
  baseline, a 832px bounded desktop cycle summary, and a wider entries table.
  At 375px the summary and entries tables scroll locally while page-level
  horizontal overflow remains zero.
- `scripts/playwright_e2e.sh` now boots an isolated Corvinum DB/app alongside
  Jober, waits for both real health endpoints, and passes both base URLs to the
  test image. Added `-i` to the inline health-probe container so Python actually
  receives the probe script over stdin.

## 2026-07-11 — Destructive-action confirmation dialog

- **276 unit + 18 e2e green** (273/16 baseline + 3 unit + 2 browser).
- Unit coverage verifies the accessible shared dialog in the Jober shell,
  CorvinumEU template resolution/inclusion, and consequence text on both exit
  actions. The shell assertion also prevents the multi-line component comment
  from leaking into rendered page text. A production-template scan covers both
  shells and rejects multiline `{# ... #}` comments repository-wide.
- Browser coverage verifies Cancel and Escape leave server state untouched;
  Agree performs the real exit/reconciliation; native required-field
  validation runs before the modal; button-specific descriptions and the
  exact clicked submitter survive resubmission; phone actions stack and Cancel
  receives initial focus.
- Full gates: ruff clean; core→feature dependency check, no-Node artifact
  check, vendored-asset SHA-256 verification, `makemigrations --check`, and
  `git diff --check` pass.
- Browser suite ran from the current source tree with existing pinned local
  images and an internal ephemeral network; no external artifact was fetched.

## 2026-07-11 — Jober seed i18n

- **273 unit + 16 e2e green**; catalogs 680/680 (sk/hu/uk) via msgfmt.
- Note: renaming seed labels (equipment → English canon) duplicates rows on
  in-place reseed (`get_or_create` by label) — demo stacks must be rebuilt
  with down && up after such changes (documented in i18n-seeded-data.md §7).

## 2026-07-11 — i18n sweep (catalog data)

- **273 unit + 16 e2e green**; catalogs 649/649 (sk/hu/uk) via msgfmt.
- Live HU drive on :8001: checklist labels, blacklist category, and the
  seeded equipment name all render Hungarian; SK equivalents via the same
  msgids. Jober SK UI gains the same translations for the shared seeded
  blacklist categories (previously English there too).
- Locale gotcha again: the new gettext calls translated strings that three
  tests asserted in English under the SK default — fixed with the
  established `translation.override("en")` pattern, assertions unchanged.

## 2026-07-11 — Stage C8 (corvinum shell port)

- **273 unit + 16 e2e green** (no Jober-facing change; client template layer
  only). Live :8001 drive asserts: authenticated pages carry the sidebar
  shell (aside.sidebar, scrim, data-nav-toggle, icon glyphs), recruiter's
  sidebar hides manager-only items, anonymous login uses the centered
  cv-anon layout, and the vendored woff2s serve fingerprinted through the
  whitenoise manifest (relative url() in theme.css correctly rewritten).
- Catalog health check upgraded: `msgfmt --statistics` is the authoritative
  count (regex checks false-positive on wrapped msgstrs) — 634/634 in SK/HU/UK.

## 2026-07-11 — Stage C7 (QR + flash theming)

- **273 passed** (271 + 2: setup page embeds an inline `<svg` in `.qr-plate`
  with no external URLs; `_qr_svg` deterministic per URI, distinct across
  URIs) + **16 e2e**, ruff clean; catalogs recompiled, zero fuzzies.
- Live on :8001: login as hradmin → `/sk/2fa/setup/` with QR present; wrong
  code → readable `message-error`; served fingerprinted theme.css carries the
  new `-soft` tokens. Owner still to phone-scan the QR as final confirmation.

## 2026-07-11 — Stage C6 (conformance + demos)

- **271 passed** (270 + payslip-creation audit test) + **16 e2e**, ruff clean;
  SK/HU/UK catalogs compile with zero fuzzies/empties.
- Both demo stacks verified live simultaneously: Jober :8000 healthz ok;
  CorvinumEU :8001 healthz ok, SK login page 200 with brand + fingerprinted
  `corvinum/theme.css`.
- Gotchas: (1) `re.sub` replacement strings interpret `\n` — po msgstr
  patching must escape or use string ops (three catalogs briefly broke with
  raw newlines inside strings); (2) manifest static storage 500s on a static
  referenced by a client whose dir wasn't collected — client static must be
  in base's STATICFILES_DIRS, not per-client settings.

## 2026-07-11 — Stage C5 (payslips)

- **270 passed** (265 + 5: password format/alphabet/uniqueness sample,
  AES round-trip — unreadable without password, wrong password fails, right
  password extracts amount+period, email carries PDF but never the password
  (body, subject, audit all checked), send requires email on file, per-person
  period uniqueness) + **16 e2e**, ruff clean.
- Live corvinum drive: migrate → real send through locmem backend → payslips
  page renders with the sent row.
- Test image rebuilt from the updated hash-pinned test.lock (new deps).

## 2026-07-11 — Stage C4 (theme + validation; Stage C close)

- **265 unit + 16 e2e green** under Jober flags (assertions unchanged across
  all of Stage C); dep-direction check clean; smoke client green.
- **CorvinumEU live validation** in the test container against a fresh
  `corvinum` DB: migrate + seed, 2FA-setup redirect for managers on login,
  six themed pages 200, checklist panel present, open-balance arithmetic
  correct, finance/accommodation/trials/SMS URLs absent.
- C4's live drive found (and fixed) the hardcoded feature links in the shared
  nav/dashboard — a client with a flag off used to 500 on the dashboard.
  Lesson: template `{% url %}` to a flag-gated route is itself a flag
  dependency; gate with `{% flag_on %}`.

## 2026-07-11 — Stage C3 (equipment→ledger link + seeds)

- **265 passed** (261 + 4: approved charge creates the linked PAY_DEDUCTION at
  unit price × qty, waive creates nothing, advances-flag-off creates nothing,
  corvinum seed command registers under corvinum settings) + **16 e2e**, ruff
  clean. Jober assertions unchanged.

## 2026-07-11 — Stage C2 (advances ledger)

- **261 passed** (251 + 10: pay-effect mapping enforced, positive-amount rule,
  Thursday-14:00 cut-off + late-entry roll-forward, Dec→Jan cycle bounds,
  positive-magnitude netting, inclusion locks + settle, cancel-only-open,
  one-shot linked reversal, open balance), ruff clean; e2e rerun (URLs touched).

## 2026-07-11 — Stage C1 (checklists)

- **251 passed** (244 + 7: idempotent instantiation, critical-only blocking,
  audited identity capture, flag-off no-op gate, blocked→allowed activation,
  toggle view allow/deny), ruff clean. Jober assertions unchanged; e2e rerun
  with the slice (URLs touched).
- Gotcha: the checklist activation gate lazily instantiates items *inside*
  `activate_on_project`'s transaction — a blocked activation rolls those rows
  back; tests (and flows relying on persistence) must instantiate via the
  panel/service first.

## 2026-07-11 — Stage C0 (CorvinumEU scaffold)

- **244 passed** (242 baseline + 2 new: CorvinumEU client boots via
  `manage.py check`; URL surface matches the flag set — equipment/blacklist/
  compliance mounted, finance/accommodation/transport/trials absent), ruff
  clean. Jober assertions untouched.
- Infra: `jober-test:phase4` rebuilt from scratch (host lost `/var/lib/docker`);
  dev DB recreated via `dev_db.sh up` — note its env file keys are
  `POSTGRES_*`, not `DB_*` (a `DB_PASSWORD` grep silently yields an empty
  password and 217 collection errors).

## 2026-07-09 — Stage B complete (B3–B5)

- **242 unit + 16 e2e green** at close (231 baseline + smoke-client boot test +
  3 retention + 7 TOTP incl. RFC 6238 Appendix B vectors). Assertions unchanged
  across the whole extraction (Stage D bar).
- Gates passed per slice: dependency tripwire empty; `migrate --check` clean vs
  a live-DB dump (B2); `manage.py check` green under `clients._smoke.settings`
  (no features, neutral policies); production image builds from the new layout;
  demo stack rebuilt post-B5 with the scenario data intact (re-entry match,
  finance months, seeded people).
- Ops note: the host restart killed the docker stack mid-B3 — restarted the
  existing `jober-dev-db` container (data preserved) rather than recreating.

## 2026-07-08 — Stage B1c: dependency direction reaches zero

- **231 unit + 16 e2e green; tripwire allowlist EMPTY** — no core→feature imports remain (was 10 edges at B0).
- Reports page now composes feature tiles (compliance count, occupancy, equipment value) and the finance company-totals panel via the core registry; finance CSV moved to `apps/finance/exports.py` (URL/name unchanged); `seed_people` slimmed to people+projects with new `seed_logistics` + months moved into `seed_finance`; `seed_demo_scenario` relocated to the new `clients/jober/demo` app (client layer may import anything). Dockerfile gains `COPY clients`.
- Assertions unchanged throughout; the only test edit is the seed-order setup line in `test_demo_scenario`.

## 2026-07-06 — Nav active-state fix

- **Full suite: 230 passed** (up from 226: +4 nav tests), 16 e2e green.
- Bug: `base.html` hardcoded `is-active` on the Overview tab, so it stayed highlighted on every page. Fix: `{% nav_active %}` template tag (`apps/core/templatetags/nav.py`) matching `request.resolver_match.url_name` against each tab's url-name set — works under every language prefix. Detail pages map to their tab (person → People, finance month/year → Finance, etc.).
- New `tests/test_nav_active.py`: correct tab active on dashboard/people/finance-month pages; the old always-on Overview bug asserted dead; exactly one active tab across five pages. Includes an autouse `translation.override("sk")` fixture — the /en/ requests otherwise leak the active language into later Slovak-asserting tests (the known msgmerge/locale gotcha family).

## 2026-07-04 — Blacklist & HMAC matching

- **Full suite: 224 passed** (up from 202), e2e excluded, on the `jober-test` image against the dev PostgreSQL. Plus **16 e2e** (11 feature + 5 smoke) in the pinned Playwright container.
- New `tests/test_blacklist.py` (14 tests): fingerprint is deterministic + key-sensitive + format-normalized; **the raw identifier is never persisted** (asserted against every field of the row); `check_match` is company-wide, active/non-expired only, and honours `BLACKLIST_MATCHING_ENABLED`; propose→approve moves the person to BLACKLISTED + activates the fingerprint; reject is a no-op on lifecycle; remove reverts to Available + revokes; deciding a non-proposed case raises; an open case blocks `activate_on_project`; `person_create` with a matching ID creates a proposed case **without blocking creation**; RBAC (decide=manager, propose=coordinator+manager, view_reason=coordinator+manager not recruiter); the queue view is 403 for coordinator; `purge_expired` drops expired; seed categories present.
- Updated `tests/test_rbac.py` matrix for the widened `blacklist.view_reason` (coordinator now True) + `blacklist.propose`. New e2e: blacklist queue renders, manager sees the Blacklist tab, coordinator → queue 403.
- `ruff check apps config tests` clean (fixed one unused import + two E702 in the new test). Migrations `blacklist/0001` + `0002` build under pytest. SK/HU/UK catalogs recompiled (de-fuzzed the new strings; set three wrapped long warnings by hand).

## 2026-06-30 — Positive sign convention (Q4 confirmed)

- **Full suite: 207 passed** (up from 202), e2e excluded, on the `jober-test` image against the dev PostgreSQL.
- New `tests/test_positive_convention.py` (5 tests): net = revenue − cost with both stored positive (cost is `12000`, not `-12000`); negatives rejected for finance line items, monthly cost (record_financial_month), room rate, and assignment-rate override.
- `ruff check apps config tests` clean. Validator-only migrations `finance/0003` + `logistics/0007` build under pytest (MinValueValidator on all money fields; no data change).

## 2026-06-29 — Browser e2e for the sprint's feature pages

- Added `tests/e2e/test_feature_pages.py` (9 tests) + `scripts/playwright_e2e.sh` (builds the **current** app + Playwright images, seeds demo users + people + questionnaire + finance, serves the app, runs the whole `tests/e2e` suite). **14 passed** (9 feature + 5 existing shell smoke) in the pinned Playwright container.
- Coverage: finance summary → month detail, finance year page, accommodation cost report (+ "reporting only" note), equipment review queue, reports inactive-by-reason; nav gating (manager sees Reviews + Finance tabs; observer sees Finance but **not** Reviews); access gating (recruiter → accommodation costs = 403; coordinator → equipment reviews = 403).
- Assertions hit the **English URL prefix** (`/en/…`) for deterministic source-string text; the language switcher isn't used in-test because it redirects back to the `/sk/`-prefixed path (locale middleware then forces Slovak). Two first-run failures were test-only bugs (that switcher redirect + "Per-project results" being an eyebrow, not a heading, on the year page), now fixed — no app defects.

## 2026-06-29 — Reports: inactive-by-reason

- **Full suite: 202 passed** (up from 198), e2e excluded, on the `jober-test` image against the dev PostgreSQL.
- New `tests/test_inactive_report.py` (4 tests): counts group by reason most-common-first; null reasons bucket into "No reason" (asserted under `translation.override("en")` since the label is translated and tests run in the `sk` default); archived people excluded by default and included via `include_archived=True`; empty when no inactive people.
- `ruff check apps config tests` clean. No model change / no migration (read-only aggregation). SK/HU/UK catalogs recompiled.

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
- **In-app, Live credentials + approved trial recipient** → Twilio **Virtual
  Phone**: message **Delivered** (Twilio Messaging Logs) and visible in the
  Virtual Phone simulator. Phone values are intentionally not recorded.
- Verified the gated **Send SMS** panel (phone-gated, `sms.send`, coordinator-scoped) and the new **Edit-person** form used to set the recipient phone.

Conclusion: messaging works end-to-end in production form. Outstanding items are operational only (account upgrade to drop the trial prefix; public inbound webhook URL).

## 2026-07-16 — Jober staging Twilio configuration boundary (manual)

- Verified the public `jober-staging` app remained healthy after synchronizing
  only the four approved Twilio runtime keys from its separate read-only
  Doppler scope.
- A failed controlled send produced Twilio error **21266**: the selected
  recipient and configured sender were the same. This confirms the provider
  request reached Twilio; it is not an application, deployment, or CSRF
  failure.
- Acceptance prerequisite: `DEMO_SMS_PHONE` must be a distinct approved test
  recipient, and a harmless outbound SMS must be confirmed in Twilio before
  the client demonstration. No phone value, credential, or service-token value
  is recorded.

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
