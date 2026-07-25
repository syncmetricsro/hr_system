# Test Journal

## 2026-07-25 - Office-scope badge + a leak caught by a completion sweep

- `tests/test_office_scope_badge.py` (12 tests): absent with zero offices
  (CorvinumEU), names a single office, summarises multi-office as
  `"Győr +1"` (alphabetical, so the label is stable rather than
  insertion-ordered), `"All offices"` for Observer with the unrestricted
  flag set, `"No office"` for a user belonging to none, nothing for
  anonymous; two shell-render tests through a real page; and a
  parametrized en/sk/hu/uk translation check following the repo's
  `translation.override` pattern.
- **A regression test that exists because of a real leak, not a
  hypothetical**: `test_occupancy_tile_counts_only_the_managers_own_office`
  asserts a VM manager sees `1/2` where the Observer sees `1/11`. The tile
  had been summing every office's rooms. Worth noting how it was found -
  a file-level "does this module reference user_office_scope" check
  reported `logistics/panels.py` as scoped (two of its three functions
  were); only a per-query sweep for model access lacking a *nearby* scope
  guard surfaced it. Blunt file-level greps are not sufficient evidence of
  completion.
- `test_trials_queue_project_dropdown_is_scoped_for_non_schedulers` guards
  a construction rather than a live leak, and says so in its docstring:
  today only Observer lacks `INTAKE_ASSIGN_TRIAL` and is unrestricted
  anyway, so this fails only if a future client policy drops that action
  from a scoped role.
- i18n: five slice-5 strings were shipped untranslated and had been
  fuzzy-matched to unrelated text; now translated in all three catalogs and
  verified programmatically (no fuzzy flag, no empty msgstr, placeholders
  intact) before compiling, rather than trusting `msgmerge`.
- Full verification: 626 Jober unit / 7 skipped, 417 CorvinumEU / 10
  skipped / 152 deselected, 50 Playwright e2e, ruff check + format clean.
  Two real failures along the way, both worth recording:
  - `test_production_templates_do_not_use_multiline_short_comments`
    rejected a multiline `{# #}` comment added to the CorvinumEU layout,
    which Django would have rendered as visible sidebar text.
  - **CI caught the occupancy test failing in the CorvinumEU lane** because
    `occupancy_tile` is flag-gated on `accommodation` (off there) and
    returns `None`. It had been filed under this module's "pure functions,
    run in both lanes" heading without checking that this particular
    function is client-gated. Now `jober_only` and physically moved into
    the accommodation group so the section comment stays true. The local
    run that "passed" had only exercised the Jober lane - **after adding
    tests, run both lanes before pushing**, not just the default one.

## 2026-07-25 - Office-scoped RBAC Phase B, Slice 5: equipment stock split into per-office warehouses

- `tests/test_equipment_stock_office_scoping.py` (10 tests). The two that
  carry the most weight:
  - `test_fifo_only_draws_from_the_persons_own_office` - VM holds 3 units,
    Győr holds 5 that are *newer*; a VM worker's issue must exhaust VM's lot
    and leave Győr's at 5. Under the old pooled FIFO this would have drawn
    across offices, so it fails loudly if the office filter is ever dropped.
  - `test_issue_rejects_when_own_office_is_short_despite_stock_elsewhere` -
    the no-silent-fallback guarantee: VM worker asks for 5, VM has 3, Győr
    has 5, and the call must **raise** rather than quietly consume Győr's
    stock. Also asserts the error names the office and that Győr's lot is
    untouched afterwards.
  - Plus: rejects issuing to a person with no office; balance and month
    report scoped to one office; `offices=None` unrestricted for Observer;
    adjustment confined to the named office; return restocks into the
    person's current office.
- Two dedicated no-offices cases, unmarked so they run in **both** lanes:
  `test_pooled_ledger_still_works_when_no_offices_exist` (receive → issue →
  balance with zero `Office` rows behaves exactly as before this slice) and
  `test_stock_ledger_is_disabled_for_corvinum`, which self-skips under Jober
  and was explicitly confirmed to execute for real under
  `--ds=clients.corvinum_eu.settings` (10 passed there vs. 9 passed + 1
  skipped under Jober - proving the guard gates on the settings module
  rather than always skipping).
- Regression run of every equipment-adjacent suite -
  `test_stock_ledger.py`, `test_inventory.py`, `test_equipment_review.py`,
  `test_equipment_ledger_link.py`, `test_person_card.py`, `test_exits.py`,
  `test_pills.py`, `test_demo_scenario.py` (57 tests) - all pass
  **unmodified**, confirming the new `office=None` default preserves the
  pooled behaviour rather than requiring test churn to accommodate it.
- Verified against real seeded data, not only via tests: ran the migrations
  and both seed commands against the dev database and queried the resulting
  per-office balances (VM 38/€672, GYR 23/€406, DS 15/€266) and what each
  demo account's stock page resolves to (VM-scoped manager 38, Observer
  111). The 111-vs-76 gap traced to a pre-slice-5 `office=None` receipt
  still in that long-lived dev DB - the documented "unfiltered includes
  unassigned" semantics, confirmed by querying the receipts directly rather
  than assumed.
- Full verification: 614 Jober unit / 7 skipped, 407 CorvinumEU / 10
  skipped / 150 deselected, 50 Playwright e2e, `makemigrations --check`
  clean, ruff check + format clean.

## 2026-07-25 - Office-scoped RBAC Phase B, Slice 4: Logistics (accommodation + transport) scoped

- `tests/test_logistics_office_scoping.py` (12 tests), deliberately split
  into two groups by what can actually run per client:
  - **HTTP accommodation tests** (6, `@pytest.mark.jober_only`): list
    hides/shows per scope, Observer sees all, hard 403 on cross-office
    `accommodation_detail` and `accommodation_edit`, same-office positive
    control, Observer positive control. Marked Jober-only because the
    `accommodation` feature flag is off for CorvinumEU entirely
    (`clients/corvinum_eu/settings.py`, "rejected in interview") - those
    URLs don't exist there, so a CorvinumEU-lane HTTP test would fail on
    `NoReverseMatch`, not prove anything about scoping.
  - **Pure-function tests** (6, unmarked, so they run in *both* lanes):
    `transport_projects()` and `assignable_rooms()` each get a
    manager-scoped case, an Observer-sees-all case, and a
    zero-`Office`-rows CorvinumEU case. These give real cross-client
    coverage of the scoping logic itself without depending on whether the
    corresponding *pages* are routable for that client - a better fit here
    than marking the whole file `jober_only`, which would have left the
    CorvinumEU behaviour of this slice completely untested.
- Full verification: 605 Jober unit / 6 skipped, 397 CorvinumEU / 10
  skipped / 150 deselected, 50 Playwright e2e, ruff check + format clean.
- The host OS crashed partway through the first verification pass, losing
  all containers and test logs. Every lane was re-run from scratch (new
  test databases, rebuilt images) rather than reporting the interrupted
  run's partial output; the Jober unit count reproduced identically.

## 2026-07-25 - Office-scoped RBAC Phase B, Slice 3: Compliance, Checklists, Notifications scoped

- `tests/test_compliance_office_scoping.py` (6 tests): `compliance_alerts()`
  scoped for Manager, unrestricted for Observer, and - the one that would
  have caught the calling-convention bug - unrestricted when called with
  no viewer at all (`compliance_alerts()`, matching several pre-existing
  tests' calling convention); page-level scoping; CorvinumEU-lane (no
  marker) unaffected-with-zero-offices case.
- `tests/test_notifications_office_scoping.py` (7 tests): routine-update
  feed hides a cross-office record and still shows a record with no
  resolvable office at all; `_core_alerts`' trial-outcome and readiness
  alerts scoped to the manager's office; a checklist-notification test
  that self-skips when `checklists` isn't enabled for the client (Jober)
  and was explicitly verified to run for real under `--ds=clients.
  corvinum_eu.settings` (11 passed there, vs. 10 passed + 1 skipped under
  default Jober settings - confirms the skip guard actually gates on the
  feature flag, not just always skipping); CorvinumEU-lane core-alerts
  case with zero `Office` rows.
- Regression run: `tests/test_compliance.py`, `tests/test_notifications.py`,
  `tests/test_checklists.py`, `tests/test_demo_scenario.py`,
  `tests/test_pills.py` - all pass unchanged, including the several
  `compliance_alerts()` no-viewer calls that would have broken without
  the calling-convention fix.
- Full verification: 593 Jober unit / 6 skipped, 391 CorvinumEU / 10
  skipped / 144 deselected, 50 Playwright e2e, ruff check + format clean.

## 2026-07-25 - Office-scoped RBAC Phase B, Slice 2: People, Projects, Reports, Exports scoped + detail-view 403s

- `tests/test_people_office_scoping.py` (9 tests): list hides/shows per
  scope, Observer sees all, hard 403 on cross-office `person_detail` /
  `archive_person` / `recycle_person`, positive controls, CSV export
  scoped, CorvinumEU-lane (no marker) proving the list is unaffected with
  zero `Office` rows.
- `tests/test_projects_office_scoping.py` (17 tests): list/detail/CSV
  export scoping mirroring the people tests; `operable_projects()`
  excludes another office even for Manager; trials queue hides another
  office's pending trial (asserted against `resp.context["trials"]`, not
  the raw HTML body, since the shared notification panel also surfaces
  person names and would give a false pass/fail); hard 403 on
  `trial_outcome`, `assign_trial`, `readiness_update`, `exit_person`,
  `activate_person` for a cross-office person/project.
- `tests/test_reports_office_scoping.py` (3 tests): reports page scoped
  for Manager, full for Observer, unaffected for CorvinumEU.
- **e2e caught two real issues, not test-infrastructure noise**:
  `test_dashboard_tooltips_...` failed because the demo's only INACTIVE
  person (Bohdan) was seeded in Dunajská Streda, invisible to the
  VM-scoped demo manager, so the tooltip's inactive-reason link no longer
  existed on the page - fixed by reseeding Bohdan into VM (a real demo-
  data decision, not a workaround: the seeded staff accounts are all
  VM-scoped, so VM needs its own inactive-person example). `test_jober_
  notification_center_...` failed because `person_detail`'s trial-
  assignment project `<select>` was still built from every active project
  unfiltered - the browser's default (first) selection was a project
  outside the manager's scope, and the now-correct 403 broke a flow that
  used to silently succeed cross-office. Fixed by scoping that dropdown
  through `operable_projects()`, the same helper `_trial_queue_context`
  already used - a real UX bug the browser test caught that no unit test
  would have (unit tests choose the project explicitly; the browser
  submits whatever `<option>` is first).
- Full verification: 583 Jober unit / 5 skipped, 380 CorvinumEU / 10
  skipped / 144 deselected, 50 Playwright e2e (green after the two fixes
  above), ruff check + format clean.

## 2026-07-25 - Office-scoped RBAC Phase B, Slice 1: `Person.office`/`Accommodation.office` schema + CorvinumEU-safety fix

- `tests/test_office_scope_helper.py` (2 tests, no client marker — must
  pass identically under Jober and CorvinumEU settings): proves the fixed
  `user_office_scope()` is unrestricted (`None`) when zero `Office` rows
  exist anywhere (CorvinumEU's permanent condition), and still correctly
  fail-closed (empty queryset, not `None`) for a Jober user genuinely
  belonging to zero of the offices that do exist.
- `tests/test_person_office.py` (7 tests): `PersonForm`'s office field
  defaults to the user's single office, offers only the user's offices
  when they have several, offers every office to Observer, stays
  optional/empty with no Office rows at all (CorvinumEU case); intake
  completion sets `Person.office` from an unambiguous single-office
  recruiter and leaves it unset for a multi-office one.
- `tests/test_accommodation_office.py` (3 tests): the equivalent
  `AccommodationForm` scoping/default/CorvinumEU-empty cases.
- Regression run: `tests/test_intake.py`, `tests/test_person_edit.py`,
  `tests/test_person_card.py`, `tests/test_accommodation_month_report.py`,
  `tests/test_accommodation_pricing.py`, `tests/test_demo_scenario.py` —
  all pass unchanged with the new nullable fields and form `user=` kwarg.
- Full verification: 554 Jober unit / 5 skipped (+12 net-new vs. the
  543-test baseline before this slice — `test_office_scoping.py`'s
  existing 8 plus the three new files' 12 minus overlap), 351 CorvinumEU
  lane / 10 skipped / 144 deselected (the new office-scoping tests carry
  no `jober_only` marker and run for real there, proving the fix works —
  not just "the CorvinumEU lane still passes because nothing touched it"),
  50 Playwright e2e (both demo apps rebuilt from a fresh image and
  reseeded, confirming the seed-script changes work against a real build,
  not just the dev bind-mount), `manage.py makemigrations --check`
  clean, ruff check + format clean.

## 2026-07-25 - Audit `reason` translation gap closed for fixed-vocabulary literals

- `tests/test_audit_log_page.py`: added
  `test_audit_reason_labels_cover_all_ui_languages` (parametrized en/sk/hu/uk,
  checks `audit_reason_label("activation")` against the real translated
  string in each catalog), `test_audit_reason_label_passes_through_unknown_
  free_text_unchanged` (confirms genuine free text is never mangled — the
  function must not attempt a readable-fallback transform the way
  `audit_action_label` does for unknown codes, since almost all reasons are
  real free text, not stale data), and
  `test_audit_log_page_translates_known_reason_but_not_free_text` (full
  page-render check: a fixed-literal reason ("activation") renders
  translated in the `uk` locale, a free-text reason ("Called in sick
  today") renders byte-for-byte unchanged, and the raw untranslated English
  literal never leaks into the response).
- Also verified (not just assumed) that the 12 previously-missing
  `AUDIT_ACTION_LABELS` entries added this slice have real translations in
  all three catalogs — no fuzzy flags, no blank `msgstr`, no accidental
  reuse of an unrelated `msgmerge` fuzzy match — via a one-off script over
  the compiled `.po` files before compiling, in addition to the existing
  `test_audit_action_labels_cover_all_ui_languages` parametrized test.
- Full verification against the real dev Postgres:
  - Ruff check + `ruff format --check`: both clean (the two touched `.py`
    files, `core/audit/views.py` and `tests/test_audit_log_page.py`, needed
    an actual `ruff format` pass — CI's format gate now fails on drift, not
    just `ruff check`).
  - Full Jober unit lane: **543 passed, 5 skipped**.
  - CorvinumEU feature-isolation lane: **340 passed, 10 skipped, 144
    deselected**.
  - Full Playwright e2e lane (both clients): **50 passed** — re-run since
    `templates/pages/audit_log.html` changed (the reason column now renders
    `reason_label` instead of the raw field).

## 2026-07-25 - Illustrated default avatar art landed (avatar-design.md §1)

- `tests/test_avatars.py`: replaced the single placeholder test with 10
  tests covering the new behavior - worker default renders for a `Person`
  with no photo; each of the 4 admin roles renders its own matching
  default for a `User` with no photo (parametrized); and, the important
  one, a new `test_default_avatar_file_is_actually_discoverable_by_
  staticfiles` (parametrized over all 5 roles) that calls Django's real
  `staticfiles.finders.find()` instead of only checking that `{% static %}`
  produced a URL string.
- **This is the test that would have caught the real deployment bug this
  slice found, if it had existed first**: the files were initially placed
  at `core/static/core/avatars/` (matching this doc's own original,
  never-verified spec), which `STATICFILES_DIRS` never scans. `{% static
  %}` doesn't check file existence, so the first version of these tests
  passed cleanly - `find()` correctly returned `None` for the wrong path
  once added, catching it immediately. Files moved to `static/avatars/`,
  test re-confirmed with `find()` returning a real path, and independently
  reconfirmed by inspecting the actual built Docker image's filesystem
  (not the bind-mounted dev container).
- Full verification against the real dev Postgres:
  - Ruff: clean.
  - `manage.py check`: clean (no model changes this slice).
  - Full Jober unit lane: **537 passed, 5 skipped** (532 baseline + 5 new
    discoverability tests; the earlier 528→532 delta was the placeholder-
    test replacement itself).
  - CorvinumEU feature-isolation lane: **335 passed, 10 skipped, 143
    deselected** (+5 vs. baseline - the new tests are all client-agnostic).
  - Full Playwright e2e lane (both clients): **50 passed** - re-run since
    the navbar avatar renders on every page in both shells.
  - Live verification against the actual rebuilt (non-bind-mounted)
    runtime image: `docker exec` confirmed all 5 `.webp` files present
    under `/app/static/avatars/` and correctly fingerprinted by
    `collectstatic` into `/app/staticfiles/`; real Playwright screenshots
    confirmed the worker default renders on every worker-list row on both
    clients, and each of the four admin-role navbar avatars shows its own
    distinct, correct color when logged in as that role.

## 2026-07-25 - GitHub application CI gate

- Added a containerized GitHub gate with separate `Quality and unit tests` and
  `Browser end-to-end tests` jobs. The quality runner exercises vendor hashes,
  no-Node policy, full-codebase Ruff lint plus changed-file formatting, both
  Django/client settings, migrations, both unit lanes, and the production-image
  boundary; browser coverage reuses the full two-client Playwright script.
- Local gate development caught two runner assumptions before publication:
  Ruff formatting initially tried to create a cache in the non-root
  bind-mounted workspace, and upload tests initially tried to write to that
  read-only bind mount. Formatting now runs without cache, and each Django test
  container receives an ephemeral no-exec `/app/media` tmpfs.
- Full local result: vendor/no-Node and production-image checks passed; Ruff
  lint passed; no Python files changed in this slice, so the incremental format
  set was empty; both Django checks and both migration checks passed; Jober
  **528 passed, 5 skipped**; CorvinumEU **326 passed, 10 skipped, 143
  deselected**; full two-client Playwright **50 passed**.
- The GitHub run remains the final proof because the defect being fixed is the
  absence of a repository-hosted gate.

## 2026-07-24 - In-app Help area (help-area-design.md)

- New `tests/test_help.py` (24 tests, 2 marked `jober_only` for the
  uk-specific assertions - CorvinumEU's `LANGUAGES` doesn't include
  Ukrainian at all, a pre-existing client policy unrelated to this
  feature, not something to work around): the index requires login but is
  visible to every one of the four roles with no RBAC distinction; the
  index links every group and every article; **every one of the 9 article
  slugs actually renders** (parametrized over `ARTICLE_TEMPLATES`, so a
  future article added to the registry without a matching template fails
  immediately instead of silently 404ing); an unknown slug is a real 404;
  the nav tab appears on an ordinary page for every role; translated
  titles/group-labels render correctly in SK, HU, and (Jober-only) UK; a
  sanity check that English content stays in English under
  `translation.override("en")` (this repo's tests default to Slovak).
- **Real test bug found and fixed, not a fluke**: the first version
  hardcoded `/uk/help/...` paths in two tests without considering that
  CorvinumEU's `LANGUAGES` setting only offers sk/hu - those two tests
  passed under the Jober lane but 404'd under `scripts/test_corvinum.sh`.
  Fixed by splitting the uk-specific assertions into their own
  `@pytest.mark.jober_only` tests, keeping the shared sk/hu checks
  unmarked so they still verify cross-client correctness.
- Full verification against the real dev Postgres:
  - Ruff: clean.
  - `manage.py check` / `makemigrations --check --dry-run`: clean (no
    model changes - this feature has no database model at all).
  - Full Jober unit lane: **528 passed, 5 skipped** (504 pill-system-Phase-2
    baseline + 24 new tests in `tests/test_help.py`).
  - CorvinumEU feature-isolation lane: **326 passed, 10 skipped, 143
    deselected** (+22 vs. the pill-system-Phase-2 baseline of 304 - 24 new
    tests minus the 2 correctly-deselected `jober_only` ones).
  - Full Playwright e2e lane (both clients): **50 passed** - re-run since
    this slice added a nav tab rendered on every single page in both
    shells.
  - Live verification via real Playwright screenshots: the English Help
    index (3×3 topic grid) and a full article page; a complete Ukrainian
    article page end to end (nav, breadcrumb, heading, and body prose all
    correctly translated, not just the title); the CorvinumEU sidebar's
    Slovak Help entry with the reused `info` icon rendering correctly via
    the previously-regenerated font subset.

## 2026-07-24 - Certificate-validity icons — pill system Phase 2 (pill-system-design.md §2)

- `tests/test_pills.py` grew from 19 to 29 tests: `most_relevant_certificate`
  (soonest-expiring valid wins; falls back to most-expired when nothing's
  valid; a no-expiry certificate counts as valid but a genuinely soon-
  expiring dated one still wins over it); `certificate_badges` (none when
  no certificates, groups by category with correct per-category severity,
  picks the renewed row over an old one in the same category); the generic
  `register_person_badges`/`person_badges` registry in isolation; end-to-
  end rendering on both the worker list and person-detail page, including
  a person with zero certificates showing no badge markup at all.
- New `test_icons_dict_material_names_are_all_in_the_corvinum_subset`
  (`tests/test_corvinum_client.py`) - checks every `core/ui/icons.py`
  `ICONS` entry's `"material"` value against `icon-names.txt`, not just
  hardcoded `base.html` usages the pre-existing test covered. This is the
  test that would have caught the whole feature shipping broken on
  CorvinumEU if the font subset hadn't actually been expanded.
  `tests/test_theme.py`'s hardcoded nav-icon-sprite symbol count updated
  29 → 34 for the 5 new Jober SVG symbols (an expected, deliberate bump,
  not a regression).
- **Real test-isolation bug found and fixed during this slice, not
  pre-existing**: the first version of the new registry test called
  `register_person_badges(...)` directly with no cleanup, permanently
  polluting the module-level list for the rest of the pytest process -
  `test_no_certificate_badges_shown_when_person_has_none` failed only when
  run *after* the polluting test in full-file order (passed in isolation,
  which is what made it non-obvious at first). Root-caused by comparing
  isolated-test vs. full-file-order runs, not guessed at. Fixed with
  `monkeypatch.setattr(registry_module, "_person_badges", [])` to scope the
  test's registration; confirmed fixed by re-running the full file twice.
- Full verification against the real dev Postgres:
  - Ruff: clean (including catching and fixing one genuine unused-variable
    lint in a new test, unrelated to the isolation bug).
  - `manage.py check` / `makemigrations --check --dry-run`: clean.
  - Full Jober unit lane: **504 passed, 5 skipped** (493 baseline + 11 net
    new: 10 in `test_pills.py`, 1 in `test_corvinum_client.py`).
  - CorvinumEU feature-isolation lane: **304 passed, 10 skipped, 141
    deselected** (+11 vs. baseline - the new tests are all client-agnostic
    core/registry behavior, none `jober_only`).
  - Full Playwright e2e lane (both clients): **50 passed** - re-run twice
    this slice (once after the initial code changes, once after the font
    subset regeneration), since both touched shared templates/assets
    rendered on every page.
  - `python3 scripts/verify_vendor_assets.py`: passes with the new
    CorvinumEU font-subset hash entry.
  - Live verification against freshly rebuilt (non-bind-mounted) images on
    **both** clients via real Playwright screenshots: zoomed crops
    confirmed Available (blue) vs. Working (green) status dots and
    expired (red) vs. expiring (amber) certificate icons are genuinely
    distinguishable at actual worker-list size; a temporary CorvinumEU
    certificate (inserted via `manage.py shell`, cleaned up after)
    confirmed the regenerated font subset renders `forklift` and
    `medical_services` as correctly-shaped, correctly-tinted glyphs in a
    real browser - not just verified by glyph count, by actually looking
    at the rendered icon.

## 2026-07-24 - Downloadable feedback PDF+QR flyer (feedback-flyer-design.md, ADR 0028)

- New tests added to `tests/test_feedback.py` (11 total in the file now, 6
  new; the file already module-skips under CorvinumEU since `feedback` isn't
  installed there, so only the 4 view-level tests are marked `jober_only`
  for clarity - the 2 `qr_pdf()`-only unit tests don't touch RBAC/client
  policy and would pass under either client if the module weren't already
  skipped): `qr_pdf()` produces a genuine single-page PDF with a Cyrillic
  label that round-trips through `pypdf.extract_text()` as real characters
  (not tofu/garbage - a meaningful assertion given the whole point of ADR
  0028 was Cyrillic support); renders correctly with an empty label; the
  view - manager 200 with correct `Content-Type`/`Content-Disposition`
  headers (token-based filename), recruiter 403, anonymous redirected; the
  inbox template includes the new download link.
- Full verification against the real dev Postgres:
  - Ruff: clean.
  - `manage.py check` / `makemigrations --check --dry-run`: clean (no
    model changes this slice).
  - Full Jober unit lane: **493 passed, 5 skipped** (487 baseline + 6 new
    tests in `tests/test_feedback.py`).
  - CorvinumEU feature-isolation lane: **293 passed, 10 skipped, 141
    deselected** - unchanged from baseline, correctly: the whole
    `test_feedback.py` module skips under CorvinumEU (feature flag off),
    so neither a regression nor new coverage was expected there.
  - Full Playwright e2e lane (both clients): **50 passed** - re-run because
    this slice edited the production `Dockerfile` (new `COPY vendor/fonts`
    line), not because of template/nav surface (no existing e2e spec
    touches `feedback_inbox.html`).
  - `scripts/verify_vendor_assets.py`: passes with the three new
    `vendor/fonts/*` entries.
  - Live end-to-end verification against the actual built runtime image
    (`scripts/dev_app.sh rebuild`, not a bind-mounted dev override) caught
    a real gap before it shipped: `qr_pdf()` initially failed inside the
    container because the `Dockerfile` never copied `vendor/fonts/` into
    the runtime image (it copies specific named directories, no wildcard) -
    unit tests never would have caught this since they bind-mount the
    whole repo. Fixed, rebuilt, reconfirmed via `docker exec` calling
    `qr_pdf()` directly, then via a full Playwright browser download
    against the real running app, rendered to PNG with `pdftoppm` for a
    visual check of both the QR code and the Cyrillic label text.

## 2026-07-24 - Status pills + nav attention badges (pill-system-design.md §1/§3)

- New `tests/test_pills.py` (19 tests, none `jober_only` — status tones and
  badge logic are all client-agnostic core/registry behavior): `{% status_pill
  %}` tone mapping parametrized across all 5 `LifecycleStatus` values (dot
  variant) plus the label variant's visible text (under `translation.override
  ("en")` - Slovak is the test default per this repo's known gotcha);
  `compliance_badge`/`reviews_badge` providers directly - no alerts, alerts
  present (severe vs. amber), anonymous request (the regression this slice
  found - asserts `None`, not a crash), and RBAC gating (coordinator lacks
  `equipment.review_deduction`); the generic `register_nav_badge`/`nav_badge`
  registry functions in isolation (first non-`None` provider wins, unknown
  slot returns `None`); end-to-end page rendering - person-detail shows the
  labeled pill, worker-list shows the dot, nav shows/hides the compliance
  badge based on real alert state, and the anonymous login page renders
  clean with no badge markup and no DB error.
- Full verification against the real dev Postgres:
  - Ruff: clean.
  - `makemigrations --check --dry-run`: no changes (this slice is
    template/CSS/registry only, no model changes).
  - Full Jober unit lane: **487 passed, 5 skipped** (468 baseline + 19 new).
  - CorvinumEU feature-isolation lane: **293 passed, 10 skipped, 141
    deselected** (+19 vs. baseline - all 19 new tests run and pass under
    CorvinumEU too, confirming the feature is genuinely core/shared, not
    accidentally Jober-only).
  - Full Playwright e2e lane (`scripts/playwright_e2e.sh`, both clients):
    **50 passed** - re-run in full (not skipped) since this slice touched
    both `layouts/base.html` files, unlike the certificate slice which
    didn't touch shared nav markup.
  - Live visual verification via Playwright screenshots against the
    rebuilt dev app (not just automated assertions): status-pill dot color
    genuinely distinguishes Available (blue) from Working (green) at real
    worker-list size, zoomed crop inspected pixel-by-pixel; person-detail
    labeled pill readable in both light and dark theme via the app's own
    theme picker (not a hand-rolled class flip); CorvinumEU sidebar badge
    correctly absent with the demo's real zero-alert data, then correctly
    present and properly corner-positioned (including rail/icon-only mode
    reasoning) after inserting one test person directly and cleaning it up
    afterward.

## 2026-07-24 - Certificate document uploads implemented (certificate-upload-design.md)

- New `tests/test_certificates.py` (19 tests, only 3 marked `jober_only` —
  the recruiter/coordinator/observer RBAC cases that assert against
  Jober's specific role grants; the rest run and pass under both clients):
  `process_certificate_document` downscales oversized images while
  preserving aspect ratio (no center-crop, unlike avatars — asserted with a
  3200×2000 source scaled to 2000×1250, not just "doesn't crash"), leaves
  small images untouched, accepts a real minimal PDF (built with
  `features.payslips.services._simple_pdf`, the same hand-rolled-PDF helper
  already used for payslip tests) and rejects a garbage one, rejects
  non-image/non-PDF bytes/SVG/oversized input, and genuinely strips
  embedded EXIF; create/edit/delete RBAC (recruiter and coordinator 302,
  observer 403); upload with no document is allowed; an invalid document
  shows a form error and persists nothing (not a partial row); document
  replace via edit; audit-event sequencing (`certificate.uploaded` then
  `certificate.replaced`) and delete-event metadata (person/category/name
  survive even though the row itself is gone by the time the event is
  written); the person-detail panel renders a certificate's name and hides
  the "Add certificate" control from an observer.
- Full verification against the real dev Postgres:
  - Ruff: clean.
  - `makemigrations compliance`: one clean migration, no unexpected diffs.
  - Full Jober unit lane: **468 passed, 5 skipped** (449 baseline + 19 new).
  - CorvinumEU feature-isolation lane (`scripts/test_corvinum.sh`): **274
    passed, 10 skipped, 141 deselected** (+16 passed vs. the avatar-slice
    baseline of 258 — the non-`jober_only` certificate tests, plus a couple
    of non-`jober_only` avatar tests not previously counted, run and pass
    under CorvinumEU too).
  - `scripts/dev_app.sh rebuild`: migration applied cleanly against the
    live dev DB, demo scenario seeded without error; spot-checked via
    `manage.py shell` that the seeded certificate row exists with the
    expected person/name.
  - e2e not re-run this slice — no template/URL surface touched that the
    existing Playwright specs assert on beyond what unit/view tests already
    cover (person-detail panel rendering, RBAC-gated button visibility).

## 2026-07-24 - Avatar system implemented (ADR 0027 + avatar-design.md)

- New `tests/test_avatars.py` (15 tests, not `jober_only` except the 3
  worker-avatar RBAC tests which assert against Jober's specific role
  grants): `process_avatar_upload` re-encodes to a 512×512 WebP, rejects
  non-image bytes/SVG/oversized input, and genuinely strips embedded EXIF
  (a real `Image.Exif()` tag was set and confirmed gone, not just assumed
  absent); own-avatar upload/remove including an anonymous-user rejection
  case and audit-event ordering (`user.avatar_added` then
  `user.avatar_replaced` on a second upload); worker-avatar RBAC
  (recruiter/manager 302, coordinator 403); the `{% avatar %}` tag's two
  render branches (placeholder vs. `<img>`).
- **Real regression caught by the full e2e run, not by the new unit
  tests**: `test_jober_notification_center_fits_phone_viewport` failed
  after the navbar avatar addition (`scrollWidth` 405 vs expected 375).
  Root-caused with a live Playwright diagnostic script against the
  running dev app (walked every element's bounding rect at 375px width)
  rather than guessing from the CSS alone — found `.header-account`'s
  pre-existing `flex-shrink: 0` had no mobile override, so it never
  shrank to the viewport once the avatar elements added enough width to
  cross the threshold. Fixed with a scoped mobile-only override, verified
  fixed with the same diagnostic script before re-running the suite.
- Full verification, pinned test container + rebuilt `jober-test:phase4`
  (now has Pillow importable) against a real dev Postgres:
  - Ruff: clean.
  - `python manage.py check` / `makemigrations --check --dry-run`: clean.
  - Full Jober unit lane: **449 passed, 5 skipped** (434 baseline + 15
    new).
  - CorvinumEU feature-isolation lane: **258 passed, 10 skipped, 138
    deselected** (+12 passed vs. baseline — the non-`jober_only` avatar
    tests run and pass under CorvinumEU too, confirming the feature is
    genuinely core, not accidentally Jober-only).
  - Full Playwright e2e lane: **50 passed** after the mobile-overflow fix
    (same count as the prior slice — no new e2e tests added here; the
    regression was in an existing test, not a coverage gap).

## 2026-07-24 - Richer finance demo data (Jan-Jul 2026); three new design docs

- No new tests — this slice only touched a demo-data seed command and
  documentation. Verified directly instead:
  - Ran `python manage.py seed_finance` against the dev database and
    queried `finance_financialmonth` directly: CARGO now has 7 rows
    (2026-01 through 2026-07, previously zero), DHLBA and WEB each have 8
    (the original Nov 2025 row plus the new 7-month 2026 series).
  - Ruff: clean.
  - Full Jober unit lane: **434 passed, 5 skipped** (unchanged — no test
    fixtures reference the demo seed command).
  - CorvinumEU feature-isolation lane: **246 passed, 10 skipped, 135
    deselected** (unaffected, as expected — CorvinumEU doesn't install
    `features.finance`).

## 2026-07-24 - Office-scoped finance RBAC + executive dashboard (ADR 0026 Phase A)

- New `tests/test_office_scoping.py` (9 tests): `user_office_scope()`
  returns `None` for Observer and the right queryset for a scoped manager;
  a manager's Finance page shows only their office (verified both via
  rendered HTML and the underlying scoped service call, not just page
  text); Observer's executive page shows all offices and the multi-series
  trend chart's series match every office; a manager gets 403 viewing or
  recording against another office's month/project by direct
  URL/POST, and 200 for their own; Observer can view any office's month
  detail; `offices=None` genuinely means unfiltered — a project with no
  office assigned still appears for Observer, confirming it isn't treated
  as "all offices" (which would incorrectly exclude it).
- `tests/e2e/test_finance_charts.py`: two new tests — Observer sees the
  `office-trend` canvas and a live Chart.js instance attached to it; a
  manager's rendered Finance page contains their own office's name but
  not the other two.
- Fixed collateral fallout from the new office-scope guard (expected,
  not regressions): `test_finance_charts.py`, `test_finance_lineitems.py`,
  `test_finance_workbook.py` (also renamed its `regional_totals` import/
  assertions to `office_totals`), and `test_nav_active.py`'s
  `test_finance_tab_active_on_month_detail` all created bare `Project`/
  manager fixtures with no office — each now creates a real `Office` and
  assigns the actor to it, rather than weakening the guard.
- `test_corvinum_client.py::test_corvinum_client_boots` and
  `test_smoke_client.py::test_core_boots_without_any_feature_or_client`
  caught a real omission on first run: `core.offices` was added to
  `config/settings/base.py`'s `INSTALLED_APPS` but not to
  `clients/corvinum_eu/settings.py` or `clients/_smoke/settings.py`, both
  of which fully replace the base list rather than extend it (same
  pattern as `core.people`/`core.projects`). Fixed by adding it to both;
  these two tests are exactly why that gap didn't ship silently.
- A second real e2e failure caught on first run:
  `test_feature_pages.py::test_finance_summary_and_month_detail` waited on
  a "Profit/loss by region" heading that no longer exists — updated to
  "Profit/loss by office" alongside the earlier rename.
- Full verification, pinned test container against a real dev Postgres:
  - Ruff: clean.
  - `python manage.py check` and `makemigrations --check --dry-run`:
    clean (no missing migrations after all model changes).
  - Full Jober unit lane: **434 passed, 5 skipped** (425 baseline + 9 new
    `test_office_scoping.py` tests, no regressions).
  - CorvinumEU feature-isolation lane: **246 passed, 10 skipped, 135
    deselected** (+1 skip vs. baseline — the new office-scoping test file
    correctly self-skips, `features.finance` isn't installed for
    CorvinumEU).
  - Full Playwright e2e lane: **50 passed** (48 baseline + 2 new tests in
    `test_finance_charts.py`) after the heading-text fix above.

## 2026-07-24 - Move regional finance chart from Reports to Finance; correct §8.1

- `tests/test_reports.py`: `test_finance_section_visible_to_observer`
  renamed to `test_finance_section_not_shown_to_observer_either` and its
  assertion flipped (finance content no longer appears on Reports for
  *any* role, including Observer) — the old assertion's premise became
  false once the panel was deleted, not a regression.
  `test_finance_section_hidden_from_recruiter` kept as-is (still true) but
  its comment updated to reflect the real reason (moved away entirely,
  not role-gated).
- `tests/test_finance_charts.py`: extended
  `test_finance_summary_renders_expected_canvases_and_trend_data` with an
  assertion that the new `chart-data-finance-summary-regional` json_script
  renders with the expected aggregated region/net values, confirming the
  move landed rather than the data just disappearing.
- `tests/e2e/test_finance_charts.py`: fixed a real strict-mode Playwright
  failure caught during verification — `test_finance_summary_renders_
  all_three_chart_types` used an unqualified
  `canvas[data-chart="diverging"]` locator, which now matches *two*
  canvases on the Finance page (group breakdown + the newly-added
  regional chart) and fails Playwright's strict-mode uniqueness check.
  Switched to `data-chart-data`-qualified locators for both.
- Full verification in the pinned test container against a real dev
  Postgres:
  - Ruff (`core features clients config templates tests`): clean.
  - Full Jober unit lane: **425 passed, 5 skipped** (same count as before
    — one test removed/renamed, one assertion added elsewhere, net zero).
  - CorvinumEU feature-isolation lane: **246 passed, 9 skipped, 135
    deselected** — identical to the pre-change baseline, confirming no
    cross-client impact.
  - Full Playwright e2e lane: **48 passed** after the locator fix above.

## 2026-07-24 - Shared icon system + expanded tooltip coverage

- Updated `tests/test_theme.py::test_jober_navigation_uses_accessible_client_owned_icons`:
  the sprite's expected `<symbol id="nav-icon-...">` count went from 14 to
  29 (14 nav icons + 15 new action icons) — an intentional expansion, not
  a regression; the test's other assertions (specific known icons present,
  no Material Symbols leakage into Jober's markup) were left unchanged and
  still pass.
- Full verification run against a real dev Postgres container:
  - Ruff (`core features clients config templates`): clean.
  - `python manage.py check`: no issues.
  - Full Jober unit lane: **425 passed, 5 skipped** (was 1 failed before
    the test-count fix above; no other regressions).
  - CorvinumEU feature-isolation lane: **246 passed, 9 skipped,
    135 deselected**.
  - Full Playwright e2e lane: **48 passed**, including
    `tests/e2e/test_tooltips.py` (3 passed) and the CorvinumEU shell suite
    — confirms both clients render correctly with the new icon backend
    live.
- No new tests added for the icon tag itself beyond the existing sprite
  regression guard above — the rollout is presentation-only (markup/CSS),
  and existing view tests already exercise every changed template's
  render path.

## 2026-07-23 - Hungarian payslip terminology

- Added parameterized catalog assertions for `Payslips`, `Record payslip`,
  `Payslip date (optional)`, and `Recorded payslips`.
- Reconciled-backlog verification from the exact pre-merge worktree:
  - Full Jober unit lane: **425 passed, 5 skipped**.
  - CorvinumEU feature-isolation lane: **246 passed, 9 skipped,
    135 deselected**.
  - Full Playwright lane: **48 passed**.
  - Ruff: clean; no-Node policy check: passed; vendor SHA-256 verification:
    passed.
  - Migration consistency: no changes detected under both client settings;
    Django system checks: clean under both settings.
  - Production image build and clean-database migration/seed completed as
    part of `scripts/playwright_e2e.sh`.

## 2026-07-23 - Finance + Reports: charts (backlog slice 8/9, expanded scope)

- `tests/test_finance.py`: 5 new tests for `monthly_totals()` — cross-project
  aggregation, ascending order (explicitly asserted, distinct from
  `yearly_totals`), `financial_reporting_eligible=False` exclusion,
  `year=` scoping, `all_locked` true only when every contributing row is
  locked.
- New `tests/test_finance_charts.py` (4 tests): renders `finance_summary`/
  `finance_year`/`finance_month_detail` via the test client, asserts
  `<canvas data-chart="...">` presence per expected chart type, and
  regex-extracts + JSON-parses each `json_script` block to check the
  actual payload values (no HTML-parsing lib added — matches this repo's
  existing stdlib-only test conventions). Also asserts the trend chart is
  entirely absent (not just empty) on a year with zero financial months.
- `tests/test_reports.py`: 1 new test for the projects/personnel section
  (headcount, assigned person name, canvas presence, `json_script`
  payload correctness). **First attempt failed under the corvinum-flags
  lane** (404 — CorvinumEU's `LANGUAGES` has no "en", only sk/hu, so a
  hardcoded `translation.override("en")` broke language-prefixed
  routing); fixed by reusing the existing conditional-language fallback
  already established elsewhere in the same file, then reran both lanes
  to confirm.
- New `tests/e2e/test_finance_charts.py` (5 tests): canvas presence for
  all four chart archetypes across the four chart-bearing pages, plus a
  genuine (not brittle) theme-toggle check reading a live Chart.js
  instance's dataset color via `Chart.getChart(canvas)` before/after
  `page.select_option("[data-theme-select]", "dark")` — proves the
  `themechange` destroy-and-rebuild logic actually recolors a running
  chart, not just that a canvas exists.
- Full unit suite: **421 passed, 5 skipped** (was 411 — 10 new tests).
  Ruff (`core features clients config tests`): clean.
  `tests/test_dependency_direction.py` (already in the suite) confirms
  the new `core/ui/chart_data.py` feature→core import direction is clean.
- Corvinum-flags lane: **242 passed, 9 skipped, 135 deselected** (after
  the language-fallback fix above; first run had 1 failure).
- Full Playwright e2e suite: **48 passed** (was 43 — the 5 new chart
  tests), including the live theme-color-change assertion.
- `scripts/verify_vendor_assets.py` run directly (not just via CI):
  passed, confirming the recorded Chart.js hash matches the committed
  file before either ever reaches CI.
- Manual verification beyond automated tests: full-page screenshots of
  the finance summary and reports pages in both light and dark theme:
  found and fixed 2 real rendering bugs neither the unit nor e2e
  assertions would have caught — (1) `collectstatic`/whitenoise failing
  the Docker build entirely over Chart.js's dangling sourcemap reference,
  and (2) direct value-labels overlapping axis text / clipping at the
  canvas edge for values near the auto-scaled extreme. Both confirmed
  fixed via before/after screenshots, not just re-reading the code.

## 2026-07-23 - Apartments: base cost + capacity at creation (backlog slice 7/9)

- Added 2 tests to `tests/test_operations_workspaces.py`: both-fields-filled
  records a cost period with the right capacity/amount; only-one-filled
  is rejected with no accommodation created (form re-render, not a 500).
- Full unit suite: **411 passed, 5 skipped** (was 409 — the 2 new tests).
  Ruff: clean.
- Corvinum-flags lane: **241 passed, 8 skipped, 135 deselected** (was 133
  deselected — the 2 new tests are in a `jober_only`-marked file, correctly
  excluded from this lane, same as every other test in that file).
- Manual functional verification against the dev app via Playwright
  (not just unit tests): both-filled → cost period appears on the
  accommodation detail page; only-one-filled → validation error shown,
  Playwright confirms via `Accommodation.objects.filter(...).exists()`
  is False; edit form confirmed to omit both fields.

## 2026-07-23 - Warehouse equipment issuing runbook scenario (backlog slice 6/9)

- No code changed, no tests run — this slice only adds a presenter runbook
  section (`docs/deployment/jober-demo-runbook.md`). Cross-checked every
  UI label it references against the live templates instead (see
  BUILD_JOURNAL entry).

## 2026-07-23 - Warehouse: better visual for "Issue" (backlog slice 5/9)

- No new automated test added (CSS/template-only, no new Python logic;
  existing `test_equipment_review.py`/`test_equipment_ledger_link.py`
  cover the underlying service behavior and don't assert on markup).
- Full unit suite: **409 passed, 5 skipped** (unchanged count — confirms
  nothing broke). Ruff: clean. Corvinum-flags lane: **241 passed, 8
  skipped, 133 deselected** (unchanged).
- Manually verified with a real Playwright screenshot against the dev app
  (logged in as manager, person-detail page) with three issued items
  covering all three badge states simultaneously — confirms the visual
  distinction the slice was meant to deliver, not just that markup is
  well-formed.

## 2026-07-23 - Audit log: filter by target worker (backlog slice 4/9)

- Added `test_filters_by_target_worker` to `tests/test_audit_log_page.py`:
  creates a second `Person` + audit event, asserts `?worker=` narrows to
  only the matching person's row in both directions (not marked
  `jober_only` — audit filtering is shared platform behavior).
- Full unit suite in the test container: **409 passed, 5 skipped** (was
  408 — the one new test). Ruff (`core features clients config tests`):
  clean.
- Corvinum-flags lane (`scripts/test_corvinum.sh`): **241 passed, 8
  skipped, 133 deselected** (was 240 — the new test runs there too).
- Manually verified against the dev app (not just the unit test) with real
  seeded data: `?worker=Kovalenko` returned exactly the one audit row for
  that person and none of another seeded person's rows, and vice versa
  with `?worker=Tashkentov`.

## 2026-07-23 - Fixed pre-existing CorvinumEU ledger e2e failure

- No new test added — this fixes production seed behavior
  (`seed_corvinum_demo.py`), covered by the existing e2e assertion rather
  than a new one.
- Full Playwright e2e suite (`scripts/playwright_e2e.sh`): **43 passed**
  (was 42 passed/1 failed before the fix). Confirmed the fix by inspecting
  live `LedgerEntry.created_at` values and the rendered ledger page via
  `scripts/corvinum_app.sh` before and after, not just by rerunning e2e.
- Corvinum/advances/ledger-focused unit slice
  (`pytest -k "corvinum or advances or ledger"`): **30 passed, 2 skipped**
  — confirms the `created_at` backdate in the seed doesn't break any
  existing advances-ledger assertion (cutoff/cycle/inclusion/reversal
  tests all still pass against the adjusted timestamp).

## 2026-07-23 - Feedback form language picker + desktop layout/copy (backlog slices 2-3/9)

- No new automated tests added for these two slices (language switch reuses
  the already-tested `set_language` view; layout/copy changes are static
  markup). Verified manually instead: a real POST-based language switch
  against the running dev app (cookie jar round-trip confirmed `hu`
  persists and renders correctly), plus Playwright screenshots at 1440px
  and 390px viewports for the layout/copy changes.
- Full unit suite + ruff + corvinum-flags lane not re-run separately for
  these two slices (template/CSS/copy-only changes, no Python logic
  touched); will re-run the complete set once all 9 backlog slices are
  done, per the user's request to hold off on committing until then.

## 2026-07-23 - Feedback invitation QR code (backlog slice 1/9)

- Updated `tests/test_totp.py::test_qr_svg_helper_is_deterministic_per_uri`
  to import the relocated `core.ui.qr.qr_svg` (was
  `core.accounts.views._qr_svg`) — same assertions, no behavior change.
- Full unit suite in the test container: **408 passed, 5 skipped**. Ruff
  (`core features clients config tests`): clean.
- Corvinum-flags lane (`scripts/test_corvinum.sh`): **240 passed, 8
  skipped, 133 deselected**.
- Full Playwright e2e suite (`scripts/playwright_e2e.sh`): **42 passed, 1
  failed** (run twice, same result both times). The failure —
  `test_corvinum_shell.py::test_corvinum_ledger_groups_controls_and_keeps_tables_aligned`
  — reproduces identically on a clean `main` worktree with none of this
  slice's changes applied, so it's a pre-existing issue unrelated to
  feedback/QR work, not a regression from this slice. Not investigated
  further here — flagged for its own fix.

## 2026-07-21 - Hungarian catalog fuzzy-match cleanup + panel help text

- Added `tests/test_i18n_catalog.py`: 14 regression assertions (not
  jober_only — catalog content is shared) asserting the corrected Hungarian
  text for the must-fix bucket of the 47 formerly-fuzzy entries via
  `translation.override("hu")`/`gettext`, plus a dedicated check that
  `EquipmentStockLot`'s initial/remaining quantity and value fields no
  longer collapse to the same Hungarian word, and that the 2 new panel
  help-text strings translate to non-empty text. Focused run: **14 passed**.
- Full unit suite in the test container: **408 passed, 5 skipped**. Ruff
  (`core features clients config tests`): clean. `git diff --check`: clean.
- Corvinum-flags lane (`scripts/test_corvinum.sh`, `-m "not jober_only"`
  against the `corvinum` DB): **240 passed, 8 skipped, 133 deselected**.
- Catalog health: `grep -c '^#, fuzzy' locale/hu/LC_MESSAGES/django.po` → 0
  (was 47). `scripts/compile_messages.sh --extract` diff confirmed 0 msgids
  removed across hu/sk/uk, only the 2 new help-text msgids added — all other
  churn was `#:` source-line-comment reordering. `.mo` files recompiled and
  committed alongside `.po`. sk/uk each still carry their own independent
  47-entry fuzzy backlog (same upstream bug, not fixed here — see
  BUILD_JOURNAL follow-up note).

## 2026-07-21 - Corvinum ledger panel-order correction

- Updated the Manager render regression to require Record entry and Cycle in
  the same workspace, followed by the combined Thursday summary + Entries
  panel. Focused advance-ledger slice: **11 passed**.
- Browser coverage now asserts the Cycle card is inside and above the activity
  panel, while summary/Entries remain merged and Entries remain outside Cycle.
  Complete isolated Playwright suite: **43 passed** at desktop and mobile.
- Ruff and `git diff --check` pass. This correction is template-only and adds
  no schema, service, dependency, or translation change.

## 2026-07-21 - Corvinum ledger workspace layout

- Added a Manager render regression proving the compact entry form precedes a
  single activity panel containing Entries, with the cycle card following as a
  separate section. Focused advance-ledger slice: **11 passed**.
- Updated the Corvinum desktop/mobile browser regression to verify Thursday
  summary and Entries share one panel, Entries no longer belongs to the cycle
  panel, table alignment is preserved, mobile entry scrolling remains local,
  and document overflow remains zero.
- Complete isolated Playwright suite: **43 passed**. Ruff and
  `git diff --check` pass; no model, migration, service, or translation change
  was required for this presentation-only adjustment.

## 2026-07-21 - Corvinum payslip issue date

- Added coverage for explicit, blank-default, out-of-period, and future issue
  dates; malformed form input; Bratislava-local legacy-date conversion;
  structured audit metadata; Manager/Observer rendering; RBAC isolation; and
  deterministic idempotent Corvinum fixtures.
- Focused Corvinum payslip/wage slice: **18 passed**. Complete Corvinum lane:
  **225 passed, 8 skipped, 133 deselected**. Complete Jober lane: **394 passed,
  4 skipped**; the three payslip UI cases skip because Jober does not mount the
  disabled feature, while shared model/service coverage remains active.
- Complete isolated Playwright suite: **43 passed**. The Corvinum 375x667
  scenario verifies both fictional issue dates, five observer-visible columns,
  panel-owned horizontal scrolling, and no document-level overflow.
- Ruff, `git diff --check`, Python compilation, migration consistency under
  both client settings, and SK/HU/UK catalog loading pass. Catalogs were built
  dependency-free in the pinned test image because the available images lack
  `msgfmt` and current repository policy forbids ad-hoc OS package installs.

## 2026-07-20 - Corvinum wage/payslip reconciliation

- Added unit coverage for positive Decimal validation, person/month uniqueness,
  audit attribution, role enforcement, independently persisted gross/net
  sources, missing-series rendering, exact idempotent seed values, and absence
  of unsupported computed-net or mismatch presentation.
- Added a 375x667 Corvinum browser regression for the gross-wage list and the
  period-aligned person overview. The 14-step HTTP walkthrough checker now
  verifies the four fictional source values for Manager and Observer.
- Focused Corvinum wage/client/routing/audit slice: **23 passed, 4 deselected**.
  Full Corvinum lane: **220 passed, 8 skipped, 133 deselected**. Full Jober
  unit lane: **392 passed, 1 skipped**.
- Complete isolated Playwright suite: **43 passed** after rebuilding, migrating,
  and seeding both clients. The new 375x667 scenario verifies all four localized
  fixture amounts, three aligned source columns, panel-owned horizontal scroll,
  and no document-level overflow.
- Ruff and migration consistency pass. The 14-step HTTP checker was expanded
  but not run against persistent staging because it creates fictional workflow
  records; provider-backed email was intentionally not repeated.
- Staging-fixture follow-up: **5 focused wage tests passed** and the complete
  Playwright suite passed again (**43 passed**) with the deterministic source
  rows assigned to Eszter Varga. The ledger layout test now derives the active
  21st-to-20th cycle in Europe/Bratislava instead of hardcoding July; this was
  exposed when local time crossed midnight to July 21 during deployment.

## 2026-07-20 - Shared audit-table layout

- Corvinum-settings audit page slice: **8 passed**. Manager/Observer access now
  also asserts the responsive wrapper, shared table class, and timestamp cell
  marker; coordinator denial and localized filters remain green.
- Complete isolated Playwright suite: **42 passed**. The new Corvinum mobile
  regression verifies five aligned columns, panel-owned horizontal scrolling,
  no document-level overflow at 375x667, and non-wrapping timestamps.

## 2026-07-20 - Corvinum presenter walkthrough reconciliation

- Human-supplied verification evidence records that the earlier ten-section
  walkthrough passed against local rehearsal and public fictional staging,
  including one controlled encrypted-payslip SMTP delivery. The evidence was
  sanitized so it contains no one-time password or TOTP material.
- The replacement checker compiles with Python 3.12, passes Ruff in the pinned
  `jober-test:phase4` image, and exposes the expected guarded CLI. A targeted
  secret-material scan and `git diff --check` pass for the changed artifacts.
- The new 13-section checker was not executed in this documentation pass: the
  existing local database contains the user's completed manual-test state, and
  provider-backed delivery was intentionally not repeated. Run local and
  staging acceptance again before recording the expanded route as passed.

## 2026-07-20 — Jober second-interview headline demo

- Focused service/view coverage passes for age boundaries and htmx auth, FIFO
  mixed-price allocation and residual value, receipt idempotency, atomic
  overdraw rollback, immutable stock movements, restock versus retire,
  Corvinum policy isolation, leap-month accommodation proration, signed finance
  validation, regional opt-out, extraordinary-row totals, and unmounted Jober
  transport routes.
- The fictional demo scenario passes three tests, including repeated seed
  execution, warehouse movement examples, partial-month accommodation payment,
  under-18 seed data, and two-region finance data.
- Full Jober unit suite: **390 passed**. Corvinum flags lane: **215 passed,
  8 skipped, 132 deselected**. Complete Playwright workflow after rebuilding,
  migrating, and seeding both clients: **41 passed** at desktop and 375×667.
- After the full run, the finance multi-line save was made atomic and its
  rollback regression was verified in the final **24-test finance slice**.
- Ruff, Django system checks, migration consistency, dependency direction,
  no-Node artifact scan, vendored-asset checksums, compiled translations, and
  the production runtime-image artifact check all pass.

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
