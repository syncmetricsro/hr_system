# Test Journal

## 2026-08-07 - CorvinumEU offer email stays narrow

- Corvinum-specific regressions prove Manager navigation and workspace access,
  403/no-link behavior for Recruiter, Coordinator and Observer, the per-person
  offer panel, absent SMS routes, SK/HU-only fictional seed templates, and an
  office-less two-recipient bulk campaign through Django's in-memory backend.
  The latter creates two `SENT` records and one batch count without touching an
  external provider.
- Installing `features.messaging` exposed six legacy SMS tests that had relied
  on the whole app being absent under Corvinum. They are now explicitly
  Jober-only; the Corvinum tests assert that the SMS route stays unmounted, and
  the focused Jober SMS module remains **9 passed**.
- Safe extraction reports **1,714 active / 1,714 translated / 0 fuzzy / 203
  obsolete** for each SK/HU/UK catalog. It added exactly one Help msgid, and a
  second extraction was byte-for-byte idempotent. PO/MO synchronization passes.
- Final lanes: **Jober 1,160 passed / 23 skipped; CorvinumEU 749 passed / 18
  skipped / 337 deselected.** Production-image/static checks, vendor integrity,
  no-Node check, Ruff lint/format, dependency direction, Django system checks,
  both migration checks, shell syntax and catalog validation passed. Browser
  tests were not run because this slice is not being deployed in this turn.

## 2026-08-06 - Finance Help names what writes and what only reports

- The Finance article regression renders the English Help page and requires the
  single-month path, its positive summary inputs, the bulk year path, annual
  workbook, two-sheet formula-free export and no-write-back boundary.
- Route metadata covers the summary, monthly workbook, annual workbook and
  project-year grid; the existing exact-topic and unsupported-client checks
  continue to keep Finance out of Corvinum.
- The targeted capture job ran both capture cases but rewrote only
  `jober/finance.webp` and its thumbnail. Both images were manually reviewed:
  fictional Slovak data only, current Workbook/CSV/Excel controls visible, and
  no credentials, logs or restricted records.
- Translation extraction reports **1,713 active / 1,713 translated / 0 fuzzy**
  for each of SK/HU/UK, with replaced Help text retained as obsolete history.
  A second extraction was idempotent and PO/MO synchronization passed.
- Full local gate: production build/static collection, dependency and vendor
  integrity, Ruff lint/format, Django checks, migration consistency, and both
  unit lanes passed: **Jober 1,159 passed / 16 skipped; CorvinumEU 737 passed /
  25 skipped / 271 deselected.** Targeted capture: **2 passed**. Before staging
  deployment, the full browser suite passed **72/72** in 176.97 seconds.

## 2026-08-06 - the Excel export is a scoped snapshot, not a calculator

- A Manager's generated workbook is opened as OOXML and asserted to contain
  exactly two translated sheets and two native chart parts, with no worksheet
  formula cells, external-link parts or VBA payload.
- Formula-like category text and URL-like project text remain shared strings;
  another office's project and office names do not enter the archive.
- Exact year-grid and January revenue/cost/net values are checked from worksheet
  XML, while an unrecorded February is an explicit zero in the twelve-month
  chart source.
- Authorization covers Manager success and Recruiter 403. The settings-aware
  route test proves the download exists for Jober and is absent for CorvinumEU.
  A browser test follows the visible year-page action and receives the expected
  `finance-2026.xlsx` filename.
- Suites: **Jober 1158 passed / 16 skipped; CorvinumEU 737 passed / 25 skipped
  / 270 deselected; browser 72 passed.** Ruff, formatting, dependency
  direction, migration, idempotent extraction, PO/MO synchronization,
  production-runtime and collected-static checks passed.

## 2026-08-06 - the annual workbook is the monthly workbook twelve times

- Two months and an adjacent-year decoy prove the annual cells sum exactly the
  requested year rather than every record for the project.
- A project with no months keeps its column and a `None` cell; blank and zero
  remain distinct.
- Office-scoping assertions cover columns, office subtotals and grand totals,
  and the view links only to in-scope project-year entry grids.
- A recruiter receives 403, while a settings-aware route test proves the URL is
  mounted for Jober and absent when Corvinum runs with profitability disabled.
- Suites: **Jober 1154 passed / 16 skipped; CorvinumEU 736 passed / 24 skipped
  / 270 deselected; browser 71 passed.** Ruff, formatting, dependency
  direction, migration and PO/MO synchronization checks passed.

## 2026-08-06 - Finance starts with no projects

- Empty-state tests reproduce the client's cleared database rather than relying
  on seeded projects.
- The manager sees the project prerequisite and creation link; an Observer sees
  the explanation without an unauthorized action.
- The year report lists eligible projects even before a financial month exists,
  while office, active-state and finance-eligibility filters remain enforced.
- The project-year grid distinguishes an expected blank year from a missing
  finance category catalogue.
- Suites: **Jober 1148 passed / 16 skipped; CorvinumEU 735 passed / 24 skipped
  / 270 deselected.** Ruff, formatting, dependency direction, migration and
  PO/MO synchronization checks passed.

## 2026-08-06 - sorting, tested where it can lie

- The fixture is three workers whose deductions **do not match** their
  alphabetical order (Alpha 300, Bravo 100, Cempty none). A fixture where the
  two orders agree would pass against a sort that does nothing.
- Empties are asserted **in both directions**, not once. That is the rule most
  likely to be "simplified" later into a plain reverse, and the plain reverse is
  wrong for exactly the question the column answers.
- The bad-key test asserts a 200 *and* that the order equals the default, so a
  fallback that silently produced some other order would still fail.
- The header test checks that `year` and `month` survive every link. A sort
  control that drops the period filter moves the reader to a different run
  without saying so, which is worse than not sorting at all.
- Suites: **Jober 1142 / CorvinumEU 735 / browser 70** (browser not re-run).

## 2026-08-05 - a test that only exists because the code is shared

- The assertion that carries this slice: **the two tables on the ledger page
  agree.** A worker's *ledger deductions* in the new overview equals the cycle
  panel's net effect for that worker, sign-flipped - 150 against -150, from
  entries of 150 + 140 deducted and 140 added back. It is only writable because
  both come from one composer; with a second bulk implementation the test would
  have been asserting that two copies of the arithmetic happened to match today.
- **Bulk equals single** guards the refactor directly: the same person's row in
  the office-wide table matches their profile table cell for cell.
- The dashes have their own test. "Every worker appears" was the owner's choice
  precisely so an omission is visible, and a table that quietly drops empty
  workers would look tidier and answer a different question.
- The period test reaches across a year boundary (January selecting 2026-01,
  2025-12, 2025-11), because month arithmetic that wraps is where this kind of
  helper breaks.
- One test premise was wrong and had to change: there is no role on CorvinumEU
  that can see the ledger but not wages - all three view actions are
  Manager+Observer, so a coordinator gets 403 on the page itself. The real case
  is a **client whose flags** mount the ledger without the wage book, which is
  what it now tests.
- Suites: **Jober 1142 / CorvinumEU 729 / browser 70** (browser not re-run).

## 2026-08-05 - testing a feature flag from the seed inward

- `tests/test_jober_checklist.py` leads with the failure that has no partial
  form: **the demo seed against its own activation gate.** It runs `seed_demo`
  and `seed_people` for real and asserts every working person came out with no
  open critical items. A unit test of the gate would have passed while the seed
  died, and the symptom of that is an empty database on a demo morning.
- A second seed test asserts the ticks carry `done_by` and `done_at`. Flipping
  the rows in a bulk update would satisfy the first test and produce a demo with
  anonymous approvals; the two together pin the intent.
- Three tests on the gate itself, chosen so the rule cannot drift: a critical
  item blocks **and the message names it**, a non-critical one does not block,
  and ticking everything clears it.
- The seed/catalog sync test reads both files with `ast` rather than importing
  them, matching the CorvinumEU one - one edited comma makes `db_trans` fall
  through to English with nothing failing.
- `test_jober_and_corvinum_still_share_their_wording` is deliberately a
  tripwire, not a rule, and its docstring says so: when the lists diverge the
  fix is to translate the new strings and relax the test, not to revert.
- Existing Jober activation tests needed no change: with no template in the
  database the gate is a no-op. Confirmed by running the lane rather than by
  reasoning about it.
- Suites: **Jober 1142 / CorvinumEU 722 / browser 70** (browser not re-run).

## 2026-08-05 - two figures, two floors

- The Ricardo fixture already pinned `2370.00  # 3240 - 330 - 540`, which is
  how the rename could be made with confidence: the arithmetic was locked down
  before the label was wrong. It now also pins `2910.00  # 3240 - 330` for the
  new net-cost figure, so the two definitions cannot drift into each other.
- One test exists purely for the asymmetry: net cost is **not** floored at
  zero. A single residence whose worker pays 250 for a 100 bed reports
  `-150.00` net and `0.00` unrecovered. Without it, someone tidying the code
  would floor both and lose a real fact.
- `DISPLAYED` in that module is a set of the keys the page renders; adding
  `net_cost` there keeps the report and the template honest about what is shown
  versus what is internal (`occupied_cost` stays deliberately unrendered).
- Suites: **Jober 1131 / CorvinumEU 722 / browser 70** (browser not re-run).

## 2026-08-05 - the suite was green and the page was empty

- The lesson of this slice: **a passing test said nothing about whether the
  page worked.** The service returned the right Decimals, the POST round-tripped,
  24 tests were green - and every input on the rendered page was blank, because
  Django localized `-2244.00` to `-2244,00` and the browser threw it away.
  Nothing in the suite looked at the rendered `value` attribute.
- The regression test now asserts the attribute itself, both ways: `value="-2244.00"`
  present and `value="-2244,00"` absent. Verified failing without `|unlocalize`
  before keeping it - a test written after a fix is worth nothing until it has
  been seen to fail.
- The other tests defend behaviour that is easy to regress into something
  plausible: an untouched column creating nothing (asserted as a `FinancialMonth`
  count), a re-save writing no audit events, a locked month skipped while the
  rest of the year saves *and named in the message*.
- The sign-rejection test asserts the **category name and month number** appear
  in the refusal, not merely that a refusal happened. The message was the defect;
  a test that only checked for an error would have passed over it.
- Office scope and role are tested on the **save** view separately from the read
  view. Same pk-taking boundary, different verb.
- Suites: **Jober 1130 / CorvinumEU 721 / browser 70** (browser not re-run).

## 2026-08-05 - testing an expiry gate without building a wall

- Four tests on the activation blocker, and the one that matters most is the
  **negative**: a current medical still activates. This thread began with an
  alert nobody could clear; over-correcting into a gate nobody can pass would
  be the worse bug, and it would look like success in a suite that only tests
  refusals.
- The boundary is tested from both sides at once: 400 days lapsed refuses, 350
  days does not. Compliance warns at 30 days; activation refuses only what has
  actually run out, and a test that pinned one number would not have caught the
  two rules being conflated.
- The blocker assertion checks that the **date appears in the message**, not
  just that a blocker exists. "Medical expired" with no date sends the office
  hunting.
- Alert scope is three tests because the rule is deliberately asymmetric:
  lapsed-on-a-trial-day is reported, no-medical-yet is not, and inactive is
  left alone. A single test would have let the asymmetry drift.
- The badge tests call the panel provider with a stub request rather than
  rendering a page — the icon row is built in Python and asserting on the dict
  says exactly what broke.
- `add_months` moved to `core/dates.py`; `tests/test_compliance.py` imports it
  from its new home so the test does not quietly certify a re-export.
- Suites: **Jober 1118 / CorvinumEU 716 / browser 70** (browser not re-run).

## 2026-08-05 - a render test that belonged in the other lane

- Two tests render the checklist panel, and they passed alone and failed in the
  full Jober lane. Cause: `{% url 'checklist_item_toggle' %}` only resolves for
  a client whose checklists flag was on when the URLConf loaded, so whether
  they passed depended on which test had last reloaded it. Moved into the
  corvinum-only module and skipped by flag — the feature's own lane is where a
  render test belongs.
- Rendering through the view failed differently first: the context processors
  want a session the `RequestFactory` does not build. `render_to_string` on the
  partial with the panel provider's own output is both simpler and closer to
  what is under test.
- The seed/registry sync test reads both files with `ast` instead of importing
  them. The seed module imports the whole CorvinumEU pay stack, and this check
  is worth running in Jober too — one edited comma in either file makes
  `db_trans` fall through to English with nothing failing.
- The seed-repair test builds a row the old way and reseeds: it fails against
  `get_or_create(defaults=…)` and passes against the repair. That is the
  staging case, not a hypothetical.
- Suites: **Jober 1110 / CorvinumEU 711 / browser 70** (browser not re-run).

## 2026-08-05 - local 2FA bypass with a production tripwire

- Two authentication regressions prove the local switch bypasses both halves
  of TOTP enforcement: a confirmed device no longer creates a verification
  detour, and a required manager role no longer creates an enrollment detour.
  A direct setup request redirects without creating a device.
- The Corvinum settings test executes both modules, not just source-text
  checks: `clients.corvinum_eu.local` must report the switch off, while
  `clients.corvinum_eu.production` must report it on with `manager` still in
  the required-role list. The runner is also pinned to the local module.
- Focused Corvinum regression: **23 passed**.
- Full local gate: production image/integrity checks, Ruff lint and formatting,
  both Django checks, and migration consistency passed; **Jober 1108 passed / 16
  skipped**, **CorvinumEU 706 passed / 23 skipped / 262 deselected**.
- Browser lane not run: it deliberately uses production settings and retains
  its existing TOTP coverage; the changed localhost runner is verified against
  the live local container instead. That database already held a confirmed
  manager device; the container reported the local switch off and the password
  POST redirected straight to `/sk/`.

## 2026-08-05 - testing a marker, not a colour

- `tests/test_physical_actions.py` (22 tests). The interesting decision is what
  it asserts: not that a button is amber, but that the **three parts travel
  together** - class, fixed heading, visible caption. Any one alone rots
  quietly, so the trio is the invariant, and each of the sixteen buttons is
  named individually. A future edit demoting *Mark cycle settled* back to grey
  fails by name.
- One test asserts the **stripe** specifically. A later "simplification" to a
  plain amber fill would pass every other test here and silently break the
  marker for greyscale and colour-blind users, which is the population the
  warning matters most for.
- The heading-drift test needed narrowing after it failed on its first run:
  `data-tooltip-heading` is used freely by ordinary form fields, so scanning
  every template found fourteen legitimate headings. It now scans only inside
  physical button tags.
- `test_shell.py` had the dialog's `aria-describedby` value pinned as a literal
  string, so adding the band there failed it - the right kind of failure. The
  band is described *first*: when shown it is the strongest sentence in the
  dialog.
- e2e (`test_confirm_dialog.py`) now checks the computed `::before` gradient on
  a real button and that an ordinary confirmation does not inherit the band
  from a physical one confirmed earlier in the session.
- Self-inflicted: two suites ran against the same `test_corvinum` database at
  once after a timeout killed one in the foreground but not in Docker. Six
  failures and sixteen errors, all `django_session does not exist`, none real.
  Terminate and drop before re-running; a clean rerun was green.
- Suites: **Jober 1105 / CorvinumEU 703 / browser 70** (browser not re-run).

## 2026-08-05 - nine tests for a rule with two ends

- The delete rule has two boundaries and both are tested from the refusing side:
  an included entry deletes, a `DEDUCTED` one is refused with the reversal
  instruction, and an entry that already carries a reversal is refused rather
  than cascading into it.
- The deletion audit event is asserted on its **payload**, not its existence.
  A `ledger.entry_deleted` row that does not carry the amount is worth nothing
  the day someone asks what was removed.
- The reopen tests cover the three answers separately: inside the window it
  reopens, after the window it refuses, and once anything is paid it refuses
  whatever the date. The interesting one asserts the refusal **names the next
  cycle key and its dates** - that sentence is the feature, not decoration, so
  a test that only checked for "an error" would have let it rot.
- Import slip worth remembering: the new tests used `LedgerEntry` and
  `LedgerError` without importing them, and `ruff` caught it as F821 before the
  suite did. `ruff check` on `tests/` is cheap and runs in seconds.
- Suites: **Jober 1083 / CorvinumEU 681 / browser 70** (browser not re-run;
  opt-in since 2026-08-04).

## 2026-08-05 - a test that passed only because the catalogs were stale

- Two tests for the reversal marker, and the first one **passed alone and failed
  in the full lane**. The cause is worth keeping: it asserted the English word
  "Reversed" against a page that renders in Slovak, and it passed the first time
  only because I had not compiled the catalogs yet. Once `Stornované` existed,
  the assertion was false.
- Fixed with the pattern already used in `test_wage_ledger`: compare against
  `gettext(...)` under `override(response.headers["Content-Language"])`, so the
  test reads the same language the page rendered in. `translation.override`
  around an assertion does nothing - the response was rendered before it.
- The stronger assertion is locale-independent and closer to the bug anyway:
  after a reversal the page must **not** still offer `value="reverse"` for that
  entry. Verified failing without the template fix.
- Suites: **Jober 1083 / CorvinumEU 673 / browser 70**.


## 2026-08-05 - the guard on a browser test earned its keep

- **`tests/test_entry_medical.py` is new (7 tests).** The pair that matter are
  the two holes: Medical cannot be marked complete without a date, and a
  *working* person can still have one recorded. The second exists because the
  certificate is valid 12 months, so the renewal path is not an edge case.
- `test_recording_a_medical_touches_only_the_date` guards the shape of the fix:
  it must not become a way to edit readiness after activation.
- **A required-date rule broke 11 tests and the demo seed, and every one of them
  was creating the same inconsistency the live bug came from** - Medical ticked,
  date blank. Fixed at source rather than by relaxing the rule.
- **`test_zz_card_layout` failed with "no activation card rendered, so this
  proves nothing".** That guard was added yesterday after an earlier version of
  the same test measured an empty page; today it caught a real break - the
  browser test builds its request through the readiness form, which now needs a
  medical date. Without the guard it would have passed against nothing.
- Walked into the documented Slovak-locale trap again: `pytest.raises(match=...)`
  on a translated message passes on the Jober lane and fails on CorvinumEU.
  `translation.override("en")` is the fix and is in `CLAUDE.md`.
- `test_flash_notifications_are_timed_and_shared_by_both_client_shells` kept its
  intent and changed its method: "shared" used to mean the same markup pasted
  into two files, which is shared only until someone edits one. It now asserts
  the include on each side, asserts the markup is **absent** from the shells,
  and checks the timing and dismiss control in the partial.
- Suites: **Jober 1076 / CorvinumEU 671 / browser 70**.


## 2026-08-05 - reversing two tests that asserted the wrong thing

- **Six new tests in `tests/test_pay_deductions.py`** for carry-forward, led by
  the reported case: an advance dated 25 July, the August run already gone out,
  and September collecting it. Also the catch-up across ages, `open_balance`
  falling to zero once a run has collected, a closed run refusing to absorb
  later entries, and an unrun cycle forecasting what it will take.
- **Two existing tests were reversed, and both had been mine, written the day
  before.** `test_deductions_are_grouped_by_calendar_month_not_by_cycle` and
  `test_backdating_into_a_settled_cycle_is_refused` each faithfully asserted
  behaviour that turned out to be wrong. A green test is only as good as the
  decision behind it; both now carry the reasoning for the reversal in their
  docstrings rather than being quietly rewritten.
- `cycle_is_settled` was left called only from a test after the refusal came
  out - production code alive because a test imported it. Split into a
  `cycle_key_is_settled(year, month)` primitive that both it and
  `settling_cycle_key` use, instead of the helper duplicating the query inline.
- Verified against staging before shipping rather than only in tests: forecast
  what the first carry-forward run would collect there. Four entries, all pay
  additions from yesterday's Sztornó testing.
- Suites: **Jober 1076 / CorvinumEU 665 / browser 70**.


## 2026-08-04 - four attempts before the upload test measured anything

The double-submit regression test took four rewrites, and each failure is worth
keeping because each was a different way for a browser test to look right and
assert nothing.

1. **Two clicks, no interference.** Passed with *and* without the fix: on a
   local stack the first click navigates before a second can land, so the window
   the bug needs never existed.
2. **`time.sleep` in a sync route handler** to widen that window. It blocks
   Playwright's own thread, so no assertion can run while it waits.
3. **`route.abort()`** to stop the navigation. Chromium replaces the page with a
   network-error page, so the form was gone before anything could be asserted
   about it - `document.querySelector('main form.stack')` returned null.
4. **`route.fulfill(status=204)`**, which keeps the page exactly where it is.

Only then did the test measure the actual thing: **how many create requests the
interface allows**. Without the guard, 2. With it, 1. That number is the bug, so
that number is the assertion.

- Also corrected during this: the helper clicked through the person page to
  reach the form, which stops being reliable once earlier tests have added
  certificates. It now reads the person id and navigates straight to the add
  URL.
- The button-state test asserts `to_be_disabled` and the notice visible, both
  scoped inside the form, because the person page it would otherwise land on
  carries four more `form.stack` panels and the locator silently re-resolves.
- Suites: **Jober 1076 / CorvinumEU 658 / browser 70**. The guard touches every
  POST form, so the full browser suite mattered here more than usual - the
  confirm-dialog flow in particular re-submits through `requestSubmit`, and a
  guard that engaged on the first, prevented submit would have blocked every
  confirmed action in the product.


## 2026-08-04 - measuring a layout bug instead of eyeballing it

- **`tests/e2e/test_zz_card_layout.py` is new (2 tests)**, and the first thing
  it does is assert `cards >= 1`. Without that it is worthless: neither browser
  stack seeds a pending activation approval, so the queue is empty and every
  measurement passes trivially. The first draft did exactly that and "passed"
  against the broken CSS - the same trap as the 2026-08-03 button-clearance
  sweep, hit again.
- The test therefore **builds the request through the UI** - waive the trial,
  complete readiness, request activation, all as one manager - which also
  reproduces the reported card exactly, including the long requester value that
  overflowed.
- **Proved the test fails without the fix**, by stashing the CSS and re-running:
  `reason input is 99px at 1280px`. A layout test that has never failed is a
  layout test that is not measuring anything.
- The numbers, since a screenshot is not a regression test: input width
  **99px -> 320px** at 1280px; page overflow 0 at 375px and 1280px; zero values
  rendering left of their own label.
- **What did not reproduce:** the mobile overflow from the second screenshot.
  With seeded data the card is 359px in a 375px viewport, before and after. The
  test asserts the property anyway - it is cheap and it is the thing that would
  regress - but the entry says plainly that this half is a guard rather than a
  reproduction.
- `tests/e2e/corvinum_auth.py` is new: `test_z_certificate_uploads` and this
  test drive the same 2FA-enforced manager, and only the first login sees the
  enrolment secret, so whichever ran second failed on a page it never reached.
  Renaming files to force an order was the first attempt and it only moved the
  failure; caching the secret in the shared process removes the ordering
  dependency instead of encoding it in filenames.
- Suites: **Jober 1076 / CorvinumEU 658 / browser 67**. Two unrelated browser
  flakes (`test_finance_charts`, `test_themes`) appeared in one run and passed
  on rerun; they run before the new tests and are unaffected by them.


## 2026-08-04 - the CorvinumEU pre-demo batch

- **`tests/test_pay_deductions.py` is new (11 tests)** and exists mostly to
  defend what the derived column is *not*. `test_gross_minus_ledger_deductions_is_shown`
  is the runbook walkthrough as a test — 1800 gross, 250 deducted, 1550 after —
  and it asserts the recorded payslip stays `1512.40` and is **not** overwritten
  by the derived figure. The gap between them is statutory, and the day someone
  "helpfully" reconciles the two is the day the product starts lying about pay.
- `test_the_derived_column_is_absent_without_a_gross_figure` covers the case
  that would otherwise print a negative: deductions with no wage recorded. Empty
  is not zero.
- `test_deductions_are_grouped_by_calendar_month_not_by_cycle` pins the join
  key. The settlement cycle runs 21st-to-20th, the other three columns are
  calendar months, and an entry dated the 25th proves the table does not mix the
  two.
- `test_backdating_into_a_settled_cycle_is_refused` is the one that found a real
  hazard rather than confirming an intention: `include_cycle` sweeps a window
  once and the windows are disjoint, so an entry backdated into a swept window
  would be created OPEN and never swept again. Paired with
  `test_a_reversal_is_never_blocked_by_the_settled_guard`, because a guard that
  also caught reversals would leave a settled cycle with no correction path.
- **`tests/test_office_field_absent.py` (7 tests) tests both directions on
  purpose.** Four assert the field disappears with no offices; three assert it
  returns and still scopes the moment one exists. The second half is the whole
  proof that this is data-driven and not a client special case — without it the
  test suite would be satisfied by an `if client == "corvinum"`.
- **`tests/test_date_input_bounds.py` (8 tests) is a sweep, not a unit test.**
  The failure mode is *someone adds one more input later*, which a per-widget
  test passes straight over. One test walks every template and fails with the
  offending tags listed.
  - Worth recording: Django's `Input.__init__` **pops** `type` out of `attrs`
    into `input_type`, so `widget.attrs["type"]` is a `KeyError` and asserting on
    it tests nothing. The rendered tag comes from `input_type`.
- **Two existing tests were reversed, not deleted**, and two were made
  policy-driven rather than role-hardcoded:
  - the office-form tests asserted the field "stays present but offers nothing";
    they now assert it is gone, with the old behaviour named in the docstring;
  - `test_managers_and_observers_can_view` became
    `test_exactly_the_roles_the_policy_allows_can_view`, asserting 200/403 from
    `can(user, Action.AUDIT_VIEW)`. A hard-coded role list could only ever be
    right for one client; this way each lane tests its own answer **and** that
    the answer is enforced. Same treatment for the staff-activity page tests,
    which moved to the Observer fixture that holds the action in both clients.
- `test_help_translations.py`'s msgid canary went 210 -> 263. It is a canary,
  not a target: it fails when help text is added so the translations cannot be
  quietly skipped, and it did exactly that here.
- Suites: **Jober 1076 passed / 16 skipped**, **CorvinumEU 658 passed / 23
  skipped**. ruff and `check_dependency_direction.py` clean — the last one
  matters here, since the deduction provider must not reach into
  `features/wage_ledger`.
- **E2E not run**, per the workflow agreed earlier today. This batch touches
  many templates, so it is a reasonable one to request before a staging deploy.


## 2026-08-04 - the e2e suite leaves the per-commit gate

- **`scripts/playwright_e2e.sh` is no longer run per slice, and CI no longer
  runs it at all on its own.** The `browser` job moved to `browser-e2e.yml`
  behind `workflow_dispatch`. Run it before a staging deploy — that is now
  rollout step 0 in `docs/deployment/deployment-plan.md` — and when asked.
- **What covers that ground now:** ruff, `manage.py check` and
  `makemigrations --check` under both settings modules, and both unit lanes —
  roughly **1018 Jober + 620 CorvinumEU**. That is the gate, and with pull
  requests gone it is the *only* gate: CI reports on `main` after the push
  rather than blocking a merge, and `main` is unprotected.
- **What is genuinely less covered.** The unit lanes exercise views through the
  Django test client, so URL/permission/template-context regressions still fail
  fast. What stops being caught per-commit is the browser-only class: Alpine
  interactions, the confirm dialog, theme switching, tooltip and button-clearance
  geometry, and real navigation across both client shells. The last two exist
  *because* they were found by eye and not by a unit test — so a UI-heavy slice
  is a reasonable place to ask for an e2e run even outside a deploy.
- No test code changed here; this entry records where the boundary moved.

## 2026-08-04 - safe translation extraction

- Added focused coverage for wrapped/context/plural parsing, fuzzy and obsolete
  classification, exact translation preservation, rename behavior, language
  set divergence, incomplete plurals, deterministic MO checks, and the
  compile-test fixtures staying out of real catalogs.
- The removal guard is tested as a transaction: snapshot three catalogs,
  simulate an active translation becoming obsolete, require refusal, restore,
  and compare the original text exactly. A separate case proves explicit
  approval retains the obsolete translation.
- The actual containerized `--extract` failure path was also exercised against
  the real repository: **122 newly obsolete listed, 0 added, 0 revived, 0
  fuzzy; 1542 active and translated per language**. It exited 1 and restored
  all three PO files byte-for-byte.
- The approved refresh retained **165 obsolete** entries per language. A second
  extraction in a later minute reported zero semantic changes and was
  byte-identical; `--check` then verified all three deterministic MO files.
- Final gate: production and test images rebuilt; dependency/vendor/no-Node,
  production-image, Ruff, formatting, migration and both-client system checks
  green. **Jober 1029 passed / 15 skipped; CorvinumEU 631 passed / 21 skipped /
  261 deselected; Playwright 65 passed.**

## 2026-08-04 - activation without a trial day, and self-approval

- **`tests/test_trial_waiver.py` is new (9 tests).** The one that earns its
  keep is `test_a_manager_activates_without_any_trial`: the full route by one
  person — waive, complete readiness, request, approve — which only passes if
  *both* halves of ADR 0031 are in. It also asserts no `TrialAssignment` row was
  invented along the way, so a future "trial pass rate" is not diluted by trials
  that never happened.
- `test_readiness_still_gates_a_waived_activation` is the one guarding the
  distinction the whole ADR rests on: the **trial** is waived, the four pillars
  are not. Incomplete medical must still refuse. Easy thing to lose quietly.
- Authorisation is tested through the URL, not the button: a coordinator POSTing
  to `readiness_waive_trial` gets 403, and a manager gets 403 both for another
  office's project and for another office's person. Hiding a control is
  presentation; these are the control.
- `test_exiting_clears_the_waiver` covers the state bug this design creates:
  the flag keeps the readiness panel open for an *Available* person, so without
  clearing it a recycled worker reappears in readiness on a finished record.
- **Two tests reversed, not deleted.**
  `test_self_approval_is_blocked_at_the_service_not_just_the_view` and
  `test_a_manager_cannot_decide_their_own_request` are now
  `test_a_self_approval_says_so_in_the_audit_log` and
  `test_a_manager_can_decide_their_own_request`. Allowing the thing is only
  defensible if it is visible afterwards, so the replacement asserts the audit
  metadata rather than just the happy path — plus
  `test_an_ordinary_approval_carries_no_self_approved_marker`, because a marker
  present on every row is a marker that finds nothing.
- Suites: **Jober 1018 passed / 15 skipped**, **CorvinumEU 620 passed / 21
  skipped**, **e2e 65 passed**. ruff and `check_dependency_direction.py` clean.
- **Two process notes worth more than the tests.**
  1. Killing a timed-out pytest run leaves `test_jober` behind with a live
     session, and the next run reports **827 errors** that are all
     `DuplicateDatabase`. It looks like catastrophe and is housekeeping:
     `pg_terminate_backend` + `DROP DATABASE` and rerun. The full Jober suite
     takes ~7 minutes, so it needs a real timeout, not the 2-minute default.
  2. `.po` files still cannot be measured with line-oriented tools (see the
     2026-08-03 correction). The follow-up semantic parser established that
     extraction moved 122 dead-source entries into obsolete history rather than
     erasing 111 translations; the unsafe parts were fixture extraction and
     fuzzy guessing.
## 2026-08-04 - profitability grids and the real workbook

- **31 new tests**: 13 for the two grids, 18 for the importer, reader and CSV.
  All `jober_only` — profitability is OFF for CorvinumEU and its routes stay
  unmounted, which the corvinum lane proves by still passing.
- The importer tests use a deterministic workbook generated with the standard
  library. The client's `docs/examples/HV 202510.xlsx` remains gitignored, so
  CI cannot and must not depend on it. The generated archive reproduces the
  observed unnamed and non-project columns, `škoda` in both sign blocks,
  `-18676.900000000001`, the short formula and both stale cached totals without
  carrying client data in Git.
- Two failures were mine and both are recorded because they are the interesting
  part:
  - **The shared-database run caught a real bug.** Cells were assigned via a
    dict keyed by project id but indexed by month id. Those sequences coincide
    on a fresh test database, so it passed in isolation and failed seven tests
    in the full suite. The new test burns project ids first, so the mix-up now
    fails every time instead of when the ids happen to diverge.
  - **A CSV test asserted nothing while appearing to pass.** Its manager
    belonged to no office, so `user_office_scope` returned an empty queryset,
    the export was correctly empty, and every assertion about cost rows ran
    over an empty list. Membership added.
- The CSV test now checks that **every row is the same width including the
  summaries** — the previous export had an 8-column header and 10-column
  summary rows, which no assertion had ever looked at.
- Safe extraction after the rebase found **14 added / 0 newly obsolete / 0
  revived / 0 fuzzy** messages. SK/HU/UK each validate at **1556 active / 1556
  translated / 0 fuzzy**; `--check` passes and the second extraction is
  byte-identical.
- Final full gate: fresh production and test images; ruff, ruff format and the
  dependency-direction tripwire clean; `check` and `makemigrations --check`
  green under both settings modules; **1061 passed / 15 skipped** in Jober,
  **631 passed / 23 skipped / 261 deselected** in CorvinumEU, and **65 passed**
  in Playwright.
- A later GitHub rerun exposed a notification test race: the mobile test read
  the popover geometry immediately after clicking, while the two adjacent
  notification scenarios already waited for Alpine to make it visible. The
  same explicit visible-state wait now guards the mobile assertion; its focused
  container run passed.

## 2026-08-03 - button clearance sweep

- One browser test walking **nine pages at 1280px and 375px**, asserting that no
  button sits within 12px of whatever renders directly beneath it. The sweep is
  the deliverable: the report said not every instance had been found, so the
  test's failure output *is* the instance list.
- Run against unfixed CSS it named six offenders — three pages at two widths,
  all `[Filter] -> p.muted gap=0px`, all the same cause. After the fix, green.
- **The first version of this test passed against the broken CSS**, which is
  the part worth remembering. It compared each button only against top-level
  `.app-shell` children, and the actual defect is a button and a caption inside
  the *same* panel, so it stepped straight over it. The probe now compares
  against the nearest element anywhere below that overlaps the button's column.
- It also excludes the button's own ancestors on purpose: `.page-head` supplies
  its separation with `padding-bottom`, which sits inside its bounding box, so
  a naive comparison reads 0px there and would fail on correct markup. That
  false positive appears in the raw block-gap measurements and is not a defect.
- Intermediate result kept as a caution: the first fix moved the caption from
  0px to 8px, still under the bar, because the caption lives outside the form
  and the grid gap never reached it. The threshold caught what a screenshot
  would have called fixed.
- Full browser suite green: **57 passed**, both clients.

## 2026-08-03 - mobile nav toggle clearance

- Two browser tests in `tests/e2e/test_shell_smoke.py`, written to fail first:
  the reproduction returned the exact overlapping rectangles, which is what
  identified the fixed-position notification centre as the cause rather than
  anything in the header itself.
- The geometry test measures the toggle against the bell, the brand lockup and
  the account row, at **375px and 320px**. Both widths matter: the first fix
  passed at 375 and failed at 320 by roughly one pixel, so a single-width test
  would have shipped it.
- It also requires **8px of real separation** rather than mere non-overlap - two
  44px tap targets sharing an edge are still mis-tappable, and a hairline gap
  would have satisfied a naive assertion.
- A second test clicks the toggle and waits for the menu, because the original
  defect was that the control could not be activated. An assertion that only
  checked position would have passed against a button nothing could press.
- Full browser suite green on the fix branch: **58 passed**. On
  `feat/offer-emails`, which carries six extra specs, **64 passed**.

## 2026-08-03 - payslip office scoping

- **11 tests** in `tests/test_payslip_office_scoping.py`, deliberately **not**
  `jober_only`: `features.payslips` is installed for both clients and the
  corvinum lane is where the feature is actually mounted, so that is the lane
  that matters. The UI cases carry the same `payslip_ui` flag gate
  `tests/test_payslips.py` already uses; the form cases need no URL and run
  everywhere.
- Request-level through `client` rather than unit tests on the helpers, for the
  reason `test_object_view_office_scoping.py` records: the guards existed and
  were correct, what was missing was the call.
- Four cases per surface rather than one - cross-office refused, **own-office
  still allowed**, unrestricted role unaffected, and a negative side-effect
  assertion. An account seeing less proves nothing on its own.
- The send case additionally monkeypatches `build_encrypted_pdf` to raise,
  proving the boundary check runs before anything is generated. Without that
  ordering a refused request would still mint a one-time password.
- The list cases assert on `response.context["payslips"]` so they fail on a
  leaked row even when the template happens not to render it.
- Full gate: ruff, ruff format and the dependency-direction tripwire clean;
  `manage.py check` green under both settings modules; **931 passed / 14
  skipped** in Jober and **585 passed / 17 skipped / 257 deselected** in
  CorvinumEU.

## 2026-08-03 - i18n catalogs: the claim, not the catalogs, was broken

- No code change; recording a measurement that overturned an earlier one.
- `msgfmt --statistics` on `main`: **1576 translated, 0 untranslated, 0 fuzzy**
  in sk, hu and uk. The catalogs are complete.
- The earlier "~110 untranslated" and "~250 msgid churn" figures came from
  `grep -c '^msgstr ""$'`. That counts the **wrapped** form, where `msgstr ""`
  is followed by continuation lines — which is a translated long string. Two
  independently written parsers agreed with `msgfmt` at zero before the claim
  was withdrawn.
- Worth keeping as a rule: `.po` files are not line-oriented, so line-oriented
  greps do not measure them. `msgfmt --statistics` is the only count to quote.
- Consequence: a re-extract would drop obsolete entries and raise ~44 genuine
  fuzzy matches for review — work created, nothing fixed. The proposed i18n
  slice is cancelled and the claim removed from the offer-email design doc.

## 2026-08-03 - provider-backed send, and two bugs the suite could not see

- **First real-SMTP run** of the payslip path, against `smtp.forpsi.com` with a
  disposable relay address allowlisted. Both directions were exercised, which is
  the only thing that makes it evidence rather than a demo:
  - a **non-allowlisted** recipient was refused **with live credentials
    loaded** - `sent_at` untouched, `sent_to` empty, one `payslip.send_blocked`
    audit event, zero `payslip.sent`, nothing left the box. A broken guard here
    would have sent a real email rather than raising, which is why this case
    matters more than the happy path.
  - the **allowlisted** recipient arrived, and the encrypted PDF opened with the
    one-time password and showed the expected period and net amount.
  - the password appeared in **no** `payslip.*` audit row - ADR 0023's invariant
    re-proved on a real send rather than against a mock.
- **`mail.W001` proved by hand** under `clients.corvinum_eu.settings` with SMTP
  configured and no allowlist: it fires, naming `payslips`. The superseded
  `messaging.W001` could not have, being gated on `offer_emails`, which is False
  for that client. Automated coverage exists too, but the manual run is what
  showed the warning reaching the client that needed it.
- **Four new `core/mail` tests** for the two config-honesty bugs: an empty
  backend and a whitespace-only backend are unconfigured, the default
  `localhost` host is unconfigured, and an explicit local MTA (`127.0.0.1`)
  still counts as configured - the last one so the localhost rule cannot lock
  out a legitimate relay.
- Neither bug was reachable from the suite as written, because both are about
  what an environment supplies rather than what the code does. They were found
  by reading deployment config. Recorded because "the tests were green" was
  true and irrelevant.
- Final gate on the branch tip: ruff, ruff format and the dependency-direction
  tripwire clean; `check` and `makemigrations --check` green under both settings
  modules; **1004 passed / 9 skipped** in Jober and **604 passed / 21 skipped /
  257 deselected** in CorvinumEU; **62/62** e2e. CI green on PR #157.

## 2026-08-03 - worker email allowlist, both senders

- **20 new tests** across two modules, and neither carries `jober_only` — that
  is the point. `core.mail` is installed everywhere and `features.payslips` is
  installed for both clients, so both modules run in the corvinum lane, which is
  the lane that actually exercises payslip delivery.
- `tests/test_core_mail.py` pins the allowlist semantics once, where the code now
  lives: empty means unrestricted (production's setting, and an unset variable
  must not take email down), case- and whitespace-insensitive matching, a blank
  address refused when a list exists, and `email_configured` across console,
  locmem and SMTP backends.
- The `mail.W001` cases include the regression that prompted the move: the check
  fires for `payslips` alone, with `offer_emails` explicitly False. It stays
  quiet on a console backend and under DEBUG, so the warning that matters is not
  buried in noise on every developer machine.
- `tests/test_payslip_email_safety.py` covers the refusal end to end: no mail, no
  `sent_at`, a `payslip.send_blocked` audit event and no `payslip.sent`, and an
  explode-guard monkeypatching `build_encrypted_pdf` proving **no PDF and no
  password** are produced for a blocked recipient. The resend case is separate
  and deliberate — `send_payslip` prefers `sent_to` over `person.email`, so a
  payslip delivered before the guard existed carries an address that was never
  checked; correcting the person's address must not launder it.
- Proven by running the check by hand under `clients.corvinum_eu.settings` with
  SMTP configured and no allowlist: `mail.W001` fires, naming `payslips`.
- `tests/test_offer_email_safety.py` lost the moved tests and kept its
  transport-specific one. Its behaviour assertions are unchanged, which is the
  point of a move.
- Full gate green: Ruff clean, dependency-direction tripwire clean, `check` and
  `makemigrations --check` under both settings modules, **1000 passed / 9
  skipped** in Jober and **600 passed / 21 skipped / 257 deselected** in
  CorvinumEU, and **62/62** e2e after the payslip template change. (Branch tip
  is now 1004 / 604 — the two config-honesty fixes in the entry above added
  four more tests.)

## 2026-08-02 - offer emails

- **54 new unit tests** across four modules, all `jober_only` and behind the
  usual `is_installed("features.messaging")` module skip.
- `test_offer_email_safety.py` is the important one. Opt-out, blacklisted, no
  address, and a non-allowlisted address each produce `BLOCKED` with an empty
  `mail.outbox`; an explode-guard monkeypatching `EmailMessage.send` proves the
  mail server is never reached for a blocked recipient. Allowlist matching is
  case-insensitive, an empty allowlist stays unrestricted (production's
  setting), a console/locmem backend counts as configured, and unconfigured
  SMTP records FAILED rather than pretending to send. The `messaging.W001`
  deploy check is covered both ways.
- `test_offer_emails.py` pins language selection and its two fallbacks -
  including an unusable `preferred_language`, since that column is a free
  CharField with no choices validation and would otherwise 500 in front of a
  manager. Also: an unknown `$token` survives substitution, optional fields
  render blank rather than "None", a capped batch stops at the limit, and one
  blocked recipient does not stop the other sends.
- One of those tests exists because the full suite caught a real bug the
  focused run had not: `get_wage_unit_display()` resolves against the *active*
  locale, so a Ukrainian worker's offer rendered "8.50 EUR za hodinu" —
  Ukrainian body, Slovak wage unit — whenever the sender was working in
  Slovak. Placeholder building is now wrapped in `translation.override` on the
  chosen template's language, and the test asserts it from a Slovak sender.
- `test_offer_email_office_scoping.py` is request-level through `client`, four
  cases per guarded view, and covers the shape a unit test cannot: that bulk
  **execution** is scoped and not only the preview. Also asserts a recruiter
  cannot bulk-send or author, and that Observer - the one cross-office role -
  cannot send at all.
- `test_offer_email_seed.py` pins idempotency, that reseeding repairs a
  hand-edited body, that every kind and all three worker languages are covered,
  and that a seeded offer always carries an office. That last test exists
  because its absence is what made the first e2e run fail.
- **e2e: 6 new specs, 62/62 passing.** They cover what only a browser catches -
  the panel actually rendering, the Offers tab present for a manager and absent
  for a recruiter, and the bulk page showing its confirm box. Fixing them
  required adding `seed_messaging` and `seed_offer_emails` to the e2e seed
  order, which had never run either.
- Full gate green: Ruff clean, `manage.py check` and `makemigrations --check`
  under both settings modules, **980 passed / 8 skipped** in Jober and
  **575 passed / 21 skipped / 257 deselected** in CorvinumEU.

## 2026-08-02 - Help card icon containment regression

- The focused two-client Help browser slice passed **4/4** after adding the
  missing shared `icon-lg` rule.
- The desktop test measures all 12 card icons for Jober and all 12 for
  CorvinumEU. Every glyph must be 23–25px in both dimensions and its four edges
  must remain within the corresponding 44×44 tile.
- This directly covers Jober's SVG sprite backend and CorvinumEU's Material
  Symbols backend, so a future fallback to intrinsic SVG dimensions or a font
  sizing regression fails the browser suite.
- The complete quality gate passed: supply-chain and production-image/static
  checks, Ruff, both Django system and migration checks, **927 passed / 8
  skipped** in Jober, and **575 passed / 17 skipped / 257 deselected** in
  CorvinumEU.
- The final complete two-client Chromium suite passed **56/56**, including the
  new icon geometry assertions plus the existing desktop/mobile, theme,
  navigation, upload and feature-workflow coverage.

## 2026-08-01 - complete Help release gate

- Focused Help tests passed under both settings modules: 50 Jober tests and 49
  CorvinumEU tests plus one expected Jober-only deselection. They pin the exact
  12-topic sets, unsupported 404s, legacy Logistics redirect, card metadata,
  route coverage, conditional Equipment/Readiness content, client asset
  isolation, static asset discovery, shared article anatomy, and all-role read
  access.
- The Help source contains 210 translatable messages. Catalog checks prove SK,
  HU and UK each has a reviewed non-empty entry, with only the intentionally
  shared term `Audit` unchanged in SK/HU. The standard-library PO compiler
  round-trip test covers context, plural forms, and fuzzy-entry rejection.
- The capture job passed for both seeded clients and produced 48 WebPs. All 24
  primary images are 1280×720, all 24 thumbnails are 640×360, every file
  decodes as WebP, and none contains EXIF. Contact-sheet review confirmed
  Slovak Jober, Hungarian CorvinumEU, fictional data, Audit without event rows,
  and Payslips without a password or send-result screen.
- The Help browser slice passed 4/4 after correcting its group-row assertion.
  The complete two-client Chromium suite then passed **56/56**, including
  desktop and mobile card layout, all visible links, keyboard/click navigation,
  primary and thumbnail dimensions, article anchors and callouts, and light/
  dark legibility.
- The complete quality gate passed: no forbidden Node artifacts; vendored
  checksums valid; production image and collected static files valid; Ruff and
  changed-file formatting green; both Django system and migration checks green;
  **927 passed / 8 skipped** in Jober and **575 passed / 17 skipped / 257
  deselected** in CorvinumEU.

## 2026-08-01 - localization leak regression coverage

- The compiled SK/HU/UK catalogs now translate all three canonical occupational
  certificate names and the three previously empty Staff activity explanations.
- Page-level tests prove canonical Crane badge tooltips contain no English name
  under SK, HU or UK; arbitrary operator-entered certificate names retain their
  existing pass-through behavior.
- Page-level tests prove the People inactive-reason selector renders the seeded
  `Sick` label as `Choroba`, `Beteg` and `Хвороба` in the respective locales.
- A static template regression rejects untranslated literal tooltip,
  placeholder, title and `aria-label` attributes while allowing translated and
  deliberately dynamic values.
- Final focused result: 106 tests passed across `test_pills.py`,
  `test_people_views.py`, `test_staff_activity.py`, `test_i18n_catalog.py` and
  `test_tooltips.py`. Ruff lint passed; Ruff formatting was applied and then
  verified for the touched Python files.
- The complete Jober unit lane passed with exit code 0. The complete CorvinumEU
  lane passed with 555 tests, 17 expected skips and 280 Jober-only tests
  deselected; page-level Ukrainian cases skip there because CorvinumEU exposes
  SK/HU only, while Jober and direct catalog tests continue to cover Ukrainian.
- Django system checks passed for both client settings and migration generation
  reported no model changes. The standalone CorvinumEU history check warned
  that the optional `corvinum` base development database was absent; its full
  pytest lane nevertheless created and validated the dedicated test database.

## 2026-08-01 - manual Jober certificate positive paths

- The fictional forklift card saved on staging, and the standard Edit flow
  corrected its metadata and added the initially omitted back image without
  losing the front. Both file links rendered afterward.
- The fictional crane certificate saved as a single PDF and rendered Valid.
- The fictional welding certificate saved as a single image and rendered
  Welding, `Testovia Welding School`, the expected dates and Valid.
- This completes the positive file-shape matrix only. Authorization, Audit,
  archive/renewal, purge and the optional mislabel probe remain separate
  acceptance steps and are not claimed by these screenshots.

## 2026-08-01 - portable manual-upload fixture verification

- `sha256sum --check tests/fixtures/manual_uploads/SHA256SUMS` passed for all
  15 portable binary files: six valid avatars, two avatar rejects, four
  allowed certificate files, and three prohibited-document boundary files.
- The real avatar processor accepted all six valid JPEG/PNG/WebP sources and
  produced 512×512 WebPs with zero EXIF. It rejected both the text-disguised-as
  JPEG and the SVG without creating output.
- Mira's new synthetic 1254×1254 PNG contains no EXIF and processed to a
  28,256-byte 512×512 WebP with no EXIF. No real-person reference was supplied;
  the asset is restricted to the fictional under-18 staging row.
- The real certificate sanitizer successfully decoded/rebuilt all seven
  curated certificate files. Structural acceptance of the three prohibited
  specimens is expected: the category allowlist rejects `HEALTH`/`OTHER`, while
  the byte sanitizer deliberately does not perform OCR or infer document type.
- Metadata inspection found only the intentional harmless avatar EXIF
  (`Synthetic avatar fixture`, `FICTIONAL TEST CAMERA`), empty EXIF on the
  other images, and fictional title/timestamp metadata on the PDFs. No real
  person reference, credential, local path, or secret was present.
- The curated directory is not ignored, totals approximately 15 MB, and omits
  originals, previews, duplicate document variants, contact sheets, and ZIPs.
  Documentation references now resolve to the tracked directory. Markdown
  whitespace validation remains part of final handoff.

## 2026-08-01 - staging upload-proxy regression check

- Both `jober-staging` and `corvinum-staging` generated nginx configurations
  passed Dokku validation and exposed `client_max_body_size 25m;` after the
  explicit proxy-config rebuild.
- All four generated fictional PNG originals used in the manual Jober pass
  uploaded successfully after the change. Their resulting avatars rendered in
  the person detail, People list, and bottom-right quick-access worker panel.
- A read-only inspection of the mounted staging media then found exactly four
  avatar files. Every file had a UUID `.webp` name, decoded as WebP at 512×512,
  contained no EXIF, and matched a database avatar reference; there were no
  unreferenced files and no references with a missing file. The four source
  PNGs totalled 7,770,049 bytes while the stored WebPs totalled 77,042 bytes,
  approximately a 99.0% reduction (about 101× smaller). No uploaded PNG
  original remained in the avatar media tree.
- JPEG, WebP and portrait-source coverage was already exercised by the local
  five-file processor check and automated sanitizer tests; this live manual
  pass specifically proves the four large PNG sources visible in staging.
- Corvinum's active proxy setting was verified, but this manual retest did not
  claim a second Corvinum UI upload. Application sanitizer coverage remains in
  `tests/test_avatars.py` and `tests/test_certificates.py` for both client
  settings.
- This was an operational configuration and documentation change only; no
  application test suite rerun was required.

## 2026-08-01 - certificate upload and language-boundary runbook check

- Runtime form inspection confirmed Jober's manual categories render as
  Forklift/Crane/Welding in EN, SK, HU and UK, while CorvinumEU exposes the SK
  and HU variants configured for that client.
- Code inspection reconfirmed that `process_certificate_document` performs
  format, size, dimension, EXIF and PDF-safety processing only. It has no OCR,
  language classifier, translation, or document-type inference.
- The local generated pack's 8 PNGs and 3 PDF variants passed the real
  certificate sanitizer. The complete `tests/test_certificates.py` suite then
  passed under both Jober and CorvinumEU (22 tests each), including allowed
  front/back, allowed PDF and disallowed HEALTH/OTHER request coverage.
- Documentation-only runbook changes add no new runtime test surface; Markdown
  whitespace and links are checked separately before handoff.

## 2026-08-01 - goods-receipt office tests pin their reporting month

- `tests/test_goods_receipt_log.py` now gives the manager and Observer office-
  visibility requests an explicit July 2026 period.
- Root cause: their July fixtures were hidden when the view correctly defaulted
  to August on 1 August; this was a date-dependent test defect, not a product
  regression.
- The focused file passes with the real current date before the full two-client
  CI gate is rerun.

## 2026-07-31 - occupational certificate storage boundary

- `tests/test_certificates.py` (22) covers image aspect ratio/EXIF removal,
  PDF rebuilding and rejection of interactive/oversized PDFs, front/back and
  single-PDF creation, the three-category allowlist, required primary files,
  relationship-scoped writes, renewal/supersession, archive retention,
  manager-only purge, old/new audit snapshots, and active-vs-history panels.
- `tests/test_certificate_storage_policy.py` (3) proves the migration-audit
  command reports first, refuses an unconfirmed purge, then deletes disallowed
  fictional file bytes and records an audit event.
- `tests/test_media_serving.py` now checks the primary and back endpoints
  separately through the existing office plus `can_view_sensitive` boundary.
- `tests/e2e/test_z_certificate_uploads.py` drives the same front/back-card form
  through Jober and CorvinumEU, then opens both permission-checked files. The
  bytes are generated in memory; no demo document is committed. The Corvinum
  case completes required HR Admin TOTP setup first.
- Full results: 908 passed / 8 skipped (Jober), 538 passed / 15 skipped / 277
  deselected (CorvinumEU), 52 passed (Playwright chromium).

## 2026-07-28 - tests/test_sms_templates_seed.py (4)

- `test_a_reseed_repairs_an_edited_body` pins `update_or_create` on `name`.
  The alternative - matching on nothing, or on body - silently accumulates
  near-duplicate templates every time staging is reseeded, and the picker grows
  a little longer each deploy.
- `test_seeding_is_idempotent` for the same reason, stated as a count.
- Module-skips when messaging is not installed, so the CorvinumEU lane does not
  fail on a feature it does not have.

## 2026-07-28 - tests/test_project_management.py (18)

- `test_a_manager_cannot_post_another_office_either` is the one that matters.
  Narrowing a picker is presentation; the queryset is the validation, and only
  a posted pk proves it.
- `test_coordinators_from_another_office_are_rejected` guards against
  reintroducing by hand the bug the demo seed had until 2026-07-26.
- `test_a_duplicate_code_is_a_field_error_not_a_500` - `code` is unique, and a
  hand-built form is where that becomes an IntegrityError.
- `test_a_manager_can_edit_their_own_offices_project` pairs with the 403 test;
  a blanket 403 satisfies the first alone.
- `test_the_overview_page_offers_a_create_link` had to be rewritten mid-build:
  it targeted `dashboard.html`, which no view renders. The failure is how that
  was discovered.

## 2026-07-28 - tests/test_equipment_returns_flag.py (7)

- `test_jober_has_no_return_route_at_all` asserts `NoReverseMatch`, not a 403.
  The distinction is the point: the route is gone, not guarded.
- `test_a_client_that_keeps_returns_still_has_the_route` is the mirror, and the
  one that matters. A global removal passes every Jober assertion in this file
  while silently breaking CorvinumEU; this is what catches that, and it is why
  the CorvinumEU count moved 518 -> 519.
- `test_the_return_form_is_not_rendered` exists because a removed route plus a
  template that still links it is worse than either alone - the page raises
  `NoReverseMatch` instead of quietly omitting a button.
- `test_jober_still_issues_equipment` and `test_jober_keeps_the_stock_correction_path`
  guard the opposite failure: with returns gone, correction is the only way to
  put quantity back.
- `test_history_is_preserved_not_deleted` pins that this is a retirement, not a
  deletion.

## 2026-07-28 - tests/test_staff_activity.py (16, was 14)

- `test_the_demo_seed_spreads_registrations_across_recruiters` guards a demo
  property: the report is technically correct with one recruiter owning
  everything, and useless.
- `test_reseeding_repairs_an_existing_databases_attribution` collapses every
  person onto one recruiter, asserts that state, then reseeds and asserts it is
  undone. Without the first assertion the test would pass on a database that
  was never broken.

## 2026-07-28 - tests/test_help_visual_aids.py extended (20)

- `test_every_referenced_asset_is_discoverable_by_staticfiles` uses `find()`,
  not a URL string. `{% static %}` happily returns a URL for a file nothing
  will ever serve, which is how the avatars shipped 404s with a green suite.
- `test_the_help_static_directory_is_copied_into_the_image` asserts a
  Dockerfile line. Unusual for a test, but the failure it prevents - files
  present in git and absent in the image - is invisible until production.
- `test_every_help_image_has_translatable_alt_text` requires the alt to contain
  a template tag, not merely to be non-empty: hardcoded alt text ships English
  to a Slovak reader, which is the exact failure this area already had.
- All of these pass with zero images on purpose, so the pipeline can land
  before the assets and fail loudly the moment a bad one is added.
- What no test caught: the rail toggle covering the Search button. Only the
  screenshot did.

## 2026-07-28 - tests/test_worker_status_rail.py (10)

- `test_the_cost_does_not_grow_with_headcount` replaced a first draft that
  asserted exactly one query and failed at two. The second query was the office
  scope - constant, not an N+1 - so the exact number was testing the wrong
  thing. Comparing the count at one worker and at twenty tests the property the
  brief actually names.
- `test_an_ordinary_page_does_not_render_the_rail_contents` asserts both
  halves: the shell present, a worker's name absent. Only checking the shell
  would pass if the rail were inlined into every response, which is the
  regression that matters.
- `test_the_status_counts_narrow_with_the_list` exists because a scoped list
  with an unscoped summary above it has now shipped three times.
- `test_statuses_are_not_a_working_not_working_split` seeds four different
  lifecycle statuses; a hardcoded two-state rail passes every other test here.
- `test_statuses_nobody_holds_are_not_listed` pins the opposite: the counts are
  a glance, not a full enumeration of the enum.
- The layout was settled by e2e, not by unit tests: a fixed overlay intercepted
  a click in CorvinumEU, and the gutter that fixed it then failed a test
  pinning CorvinumEU's content width. Neither failure was reachable from the
  Python suite, which is the argument for the browser lane existing.

## 2026-07-28 - tests/test_help_gating.py (9), tests/test_help.py updated

- `test_a_hidden_article_is_not_reachable_by_url` is the one that matters: an
  index that stops linking an article is not a gate while the URL still serves
  it.
- `test_an_available_article_still_opens` names a *flagged* article on purpose
  and is Jober-only. An always-available one would pass even if the gate
  rejected everything flagged, which is the failure it guards.
- `test_documentation_is_still_not_role_gated` pins a design decision: the flag
  gate must not drift into a permission gate.
- The `flags_off` fixture patches the flag lookup rather than
  `settings.FEATURE_FLAGS`, because changing that setting rebuilds the URLconf
  and unregisters unrelated routes. The first draft did it the other way and
  failed in a different module entirely.
- `test_each_help_article_renders` now asserts 200 *or* 404 by availability
  rather than 200 unconditionally, so a broken template still shows up while a
  correctly-gated article does not read as a failure.


## 2026-07-28 - tests/test_staff_activity.py (14)

- `test_a_recruiter_who_registered_nobody_is_still_listed` pins the property the
  feature exists for. Every other test here passes if zero rows are dropped,
  and dropping them is what a naive `annotate().filter()` does.
- `test_a_gapped_period_skips_the_month_between` seeds a February registration
  that must not be counted, so a start..end reading of "January and March"
  fails it.
- `test_a_first_placement_is_not_counted_as_a_transfer` asserts the empty case
  *before* the move as well as the single row after it; without the first half
  it would pass even if every placement counted.
- Role tests cover recruiter and coordinator separately rather than assuming
  one implies the other - they are distinct grants in the matrix.
- The issuance test needed real stock received into the worker's own office
  first. That is not incidental: issuance draws from the person's office, so a
  test that skipped it was asserting against a path that cannot happen.

## 2026-07-28 - tests/test_goods_receipt_log.py (13)

- `test_totals_are_summed_from_the_lines_not_stored` uses two lines with
  different values, so a single-line fixture cannot accidentally pass.
- `test_a_manager_cannot_open_another_offices_receipt_by_pk` and
  `test_a_manager_can_still_open_their_own` are a pair on purpose. The first
  alone is satisfied by a blanket 403.
- `test_a_manager_sees_only_their_own_offices_receipts` also asserts the
  headline *total*, not just the row list - scoping a list and leaving its
  summary unscoped is the precise bug this week produced three times.
- `test_a_gapped_period_excludes_the_months_between` seeds a July receipt that
  is not selected, so a span-based reading of "several months" fails it.
- `test_the_demo_seed_spreads_receipts_across_months` guards a demo property
  rather than a code path: with every seeded receipt in one month, the period
  filter looks broken instead of empty.
- `test_the_seed_is_idempotent` because seeds are re-run on every staging
  deploy and a duplicating top-up would inflate warehouse figures each time.


## 2026-07-28 - tests/test_audit_person_backfill.py (9)

Every test blanks attribution first (`_as_legacy()`) to reproduce what a
pre-migration database looks like, because the bug is invisible on data created
through `record_event` - which is precisely why the original test suite passed
while staging stayed broken.

- `test_the_person_filter_finds_history_after_the_backfill` asserts **0 before
  and 1 after**, through the real view. Without the "before" assertion the test
  would pass even if the filter had never been broken.
- `test_attributes_an_event_whose_target_merely_hangs_off_a_person` is the class
  the migration missed entirely and the reason this command exists.
- `test_never_reattributes_an_already_attributed_event` protects a manual
  correction from being overwritten on the next run.
- `test_a_deleted_person_is_not_resurrected_by_primary_key` guards the failure
  that would be worst if it happened: attributing an old event to whoever now
  holds that pk.
- `test_an_event_about_nobody_stays_unattributed` pins the decision not to
  guess; configuration events carry no worker's data.


## 2026-07-28 - period filter: 3 files, 53 tests

`tests/test_reporting_periods.py` (34) and `tests/test_reporting_controls.py`
(11) need no database at all - the resolver is pure date arithmetic, which is
why three surfaces can share it without sharing a query.

- `test_a_gapped_selection_stays_gapped` is the one that matters. Everything
  else in the resolver would pass if a gapped selection were quietly widened
  into a span, and the widened version is easier to write.
- `test_filter_q_has_one_clause_per_range` pins the merge: adjacent months must
  collapse to one clause, gapped ones must not.
- The bad-input parametrization includes `2026-02-30` and `2026-W99` - values
  that parse structurally and are still not dates.
- `test_the_grid_opens_on_the_year_that_was_selected` covers a silent failure:
  selecting months in 2025 and getting a 2026 grid back hides the user's own
  selection while looking fine.
- `test_params_round_trip` feeds a period's own `params` back through the
  resolver, which is exactly what the rendered control does on every submit.

`tests/test_equipment_stock_period.py` (9) covers the page.

- `test_several_months_report_as_one_period` seeds a July receipt that is *not*
  selected, so a from/to span implementation fails it. Without that third
  receipt the test would pass either way.
- `test_the_hungarian_page_does_not_print_the_raw_enum_key` loads the real page
  in the client's own language. It asserts both directions - the label present
  and the raw key absent - because asserting only the label would pass while
  both were rendered.
- Writing it exposed that the language comes from the URL prefix, not
  `HTTP_ACCEPT_LANGUAGE`; the header version silently rendered Slovak and the
  assertion failed for the wrong reason.

## 2026-07-28 - tests/test_office_scoped_aggregates.py (8, new file)

A dedicated file rather than tests scattered into each feature's suite,
because the thing being tested is a *class* of bug that crosses features. When
the fourth aggregate leak appears, this is where its regression test goes.

- Every test here was written against the unfixed code and observed to fail
  first. `test_a_manager_cannot_decide_another_offices_deduction` is the one
  that mattered: it posted another office's issue pk and watched the review
  status change from pending to decided.
- `test_a_manager_can_still_decide_their_own_offices_deduction` guards the
  opposite failure. A blanket 403 would satisfy the leak test while breaking
  the feature, and nothing else in the suite would have noticed.
- `test_the_queue_total_narrows_with_the_queue` covers the aggregate
  separately from the rows. Scoping a list and forgetting its total is the
  exact shape of the bug this file exists for.
- `test_finance_renders_on_a_tenant_with_no_offices` asserts a 200, not an
  absence of rows. It is a crash test wearing a scoping test's clothes: the
  `None` sentinel has two meanings and only one was handled.
- Observer counterparts throughout, so a future "fix" that scopes everyone
  into blindness fails here rather than in a demo.

## 2026-07-28 - tests/test_accommodation_month_report.py (11, was 1)

- `test_client_acceptance_fixture` is the client's own worked example, kept
  verbatim so the numbers in the repo and the numbers he quoted are the same
  numbers. It asserts the internal occupied-cost term too, even though the page
  does not show it, because it is the term the loss formula turns on.
- `test_the_bed_a_worker_pays_extra_for_is_not_counted_as_occupied` pins a
  *definition* the client may yet change his mind about. If he does, this test
  is the one that should fail first and loudest.
- `test_a_full_house_reports_no_empty_bed_loss_rather_than_a_negative_one`
  covers the case his formula does not: applied literally it yields -payments
  when every bed is filled. Without this test the zero floor looks like an
  unexplained deviation from the spec.
- `test_margin_is_gone` asserts an absence. Removals regress silently - the
  figure comes back in a merge and no test notices - so the removal is pinned
  rather than assumed.
- `test_a_manager_sees_only_their_own_offices_residences` was verified by
  deleting the scope filter and confirming it fails; the other ten still passed
  without it, which is exactly how the leak survived this long.
- `test_a_worker_who_changes_room_mid_month_still_occupies_one_bed` found a
  constraint I had not accounted for: `unique_active_room_per_person` means the
  old assignment must be ended first, so the head count is over people with any
  overlapping assignment, not over assignment rows.
- e2e now asserts *Margin* and *Occupied cost* appear zero times on the page,
  not merely that the five wanted figures are present.

## 2026-07-27 - tests/test_audit_person_filter.py (16)

- `test_finds_events_whose_target_is_not_the_person` is the defect itself: two
  events about one worker, one targeting the Person and one targeting a
  Certificate, and the filter must return both. Under the old code it returned
  one, which is why the client called it broken rather than incomplete.
- The diacritic parametrization includes `horvat` deliberately - unaccented
  typing is the normal case for these names, not an edge case.
- `test_a_non_matching_name_still_returns_nothing` guards the opposite failure:
  folding that matches everything would pass every other test in the file.
- `test_unattributed_events_stay_visible` pins a *decision*, not a behaviour.
  Scoping unattributed events away would look like a tightening in review while
  quietly removing a manager's view of their own configuration history.
- `test_recording_an_event_never_fails_on_an_unresolvable_target` exists
  because attribution runs inside every business transaction; a raise here
  would turn an audit detail into a failed activation or issue.
- Backfill verified separately against legacy-shaped rows before shipping:
  0 matches before, 2 after, unattributable rows untouched.
- Jober **734 passed**, CorvinumEU **441 passed**, Playwright **50 passed**.

## 2026-07-27 - tests/test_activation_approval.py (13)

- `test_requesting_does_not_activate` is the load-bearing one: if a request
  activated, the second pair of eyes would be decorative and every other test
  here would still pass.
- `test_a_manager_cannot_decide_their_own_request` (HTTP) and
  `test_self_approval_is_blocked_at_the_service_not_just_the_view` (service)
  are deliberately both present. The first proves the endpoint refuses; the
  second proves the *rule* holds for any caller, which is what moving it out of
  the view bought.
- `test_approval_rechecks_readiness` and `test_snapshot_records_what_was_asked_for`
  cover the same underlying fact from both directions - readiness is mutable
  between request and decision - because one guards correctness and the other
  guards what the manager is shown.
- `test_workflow.py::test_full_path_to_working` was rewritten rather than
  deleted: it now walks trial -> readiness -> request -> manager approves, and
  asserts the person is *not* Working after the request. That intermediate
  assertion is the regression that would otherwise be silent.
- Jober **717 passed**, CorvinumEU **441 passed**, Playwright **50 passed**.

## 2026-07-27 - tests/test_help_visual_aids.py (7)

- Diagrams assert things prose does not have to. "There is a Field tab" is
  checkable, and nothing checked it, so a confident picture of the wrong
  product reached staging. These tests check the checkable claims: the tab
  names against the real shell, the absence of cities that are not offices,
  the wordmark coming from `BRAND_NAME`, and the boundary diagram hiding when
  `OFFICES_IN_USE` is false.
- Verified by restoring the original template from `7552c6d`: **four of the
  seven fail**. The three translation tests pass against it, because they
  assert on the *catalog* rather than the template - worth knowing, since it
  means they guard the cycle being skipped, not the template being wrong.
- The suite also caught a regression in the fix itself: evaluating
  `Office.objects.exists()` eagerly in the context processor put a query on
  every anonymous response and broke four database-free rendering tests.
- Jober **705 passed**, CorvinumEU **432 passed, 14 skipped**, Playwright
  **50 passed**.

## 2026-07-26 - tests/test_demo_office_staffing.py (6)

- `test_the_boundary_is_reciprocal` is the one that carries the demo: it
  asserts the VM manager gets 200/403 on the VM/Gyor projects **and** that the
  Gyor manager gets exactly the mirror. A single-direction assertion cannot
  distinguish a boundary from one restricted account.
- `test_reseeding_does_not_multiply_office_membership` guards a silent failure
  rather than a loud one. If `set()` were ever changed to `add()`, memberships
  would accumulate across reseeds until every account saw every office - no
  error, no broken page, just a demo that quietly stops proving anything.
- `test_observer_holds_no_office_membership` pins the *mechanism*, not the
  outcome: granting the Observer all three offices would look identical on
  screen while making a `user_office_scope` regression undetectable.
- `test_each_project_is_run_by_a_coordinator_of_its_own_office` catches the
  bug this slice found - six projects all assigned to one office's
  coordinator, four of which they get a 403 on.
- Jober **698 passed**, CorvinumEU **432 passed, 14 skipped**, Playwright
  **50 passed**.

## 2026-07-26 - tests/test_corvinum_deployment_scripts.py (5, was 3)

- `test_offsite_backup_prunes_only_its_own_prefix` is the one that matters. The
  retention pass runs on the *remote* host and deletes files; widening its glob
  from `corvinum-*` to `*` while generalising the script would have read as a
  harmless cleanup and would have deleted another app's backup history.
- It asserts the prefix reaches the remote shell as a positional argument
  (`prefix="$4"`) rather than by interpolation into the heredoc body, so the
  value cannot rewrite the remote script, and that it is constrained to
  `[A-Za-z0-9._-]+` so it cannot change what the glob matches.
- Also verified outside pytest, because a string assertion cannot prove
  behaviour: seeded a directory with 40 `jober-staging-*` and 5
  `corvinum-staging-*` archives, ran the prune body with the Jober prefix, and
  confirmed 40 -> 35 Jober with CorvinumEU untouched and the orphaned
  `.sha256` siblings removed.

## 2026-07-26 - tests/test_media_hygiene.py (6)

- `test_oversized_dimensions_are_rejected_before_decoding` monkeypatches
  `PIL.Image.Image.load` to raise, so it asserts **nothing was decoded** rather
  than "the right error came back". Under the old ordering the exception
  message was already correct - the bug was purely *when* the check ran, which
  a message assertion cannot see.
- `test_a_first_upload_deletes_nothing` guards the off-by-one in the other
  direction: a helper that deletes too eagerly would remove the file it just
  stored, and every other test here would still pass.
- The `django_capture_on_commit_callbacks` wrapper is load-bearing, not
  ceremony. The cleanup is deliberately deferred to commit; pytest-django
  rolls every test back, so without executing the callbacks these tests would
  pass while asserting nothing.
- Jober **682 passed**, CorvinumEU **430 passed, 12 skipped**.

## 2026-07-26 - tests/test_sms_safety.py (8)

- `test_allowlist_blocks_an_unlisted_recipient` monkeypatches `_twilio_send`
  to raise, so the assertion is "the provider was never called" rather than
  "the status looks right". Verified by deleting the guard: the test fails
  with exactly that message.
- `test_empty_allowlist_is_unrestricted` guards the inverse mistake, which is
  the one that would actually hurt: reading an empty list as "block
  everything" would silently disable messaging in production the moment the
  variable is unset.
- `test_allowlist_matches_regardless_of_formatting` exists because a
  format-sensitive allowlist fails in the most confusing possible way - the
  entry is visibly correct and the send is still blocked.
- Jober **684 passed**, CorvinumEU **425 passed, 13 skipped**.

## 2026-07-26 - tests/test_media_serving.py (9)

- Covers the three permission shapes and, separately, that `/media/` resolves
  to **404 in every environment**. That last one is the regression guard that
  matters: the failure mode here is not a broken view, it is someone "fixing"
  broken images later by adding an nginx alias.
- `test_certificate_document_hidden_from_unconnected_recruiter` is the test
  that encodes the actual decision - same office, no relationship to the
  person, sees the certificate row, 403 on the scan. Without it the
  `can_view_sensitive` call reads as redundant next to the office guard and
  would be a tempting simplification.
- `test_missing_file_404s_rather_than_500s` deletes the file from storage
  behind the model's back, which is exactly the state a DB restore without the
  media volume produces.
- One existing test had to change: `test_avatar_tag_renders_image_when_photo_present`
  asserted `user.avatar.url in html`, encoding the behaviour being removed. It
  now asserts the permission-checked route *and* that the raw storage URL is
  absent.
- Jober **676 passed**, CorvinumEU **425 passed**, Playwright **50 passed**.

## 2026-07-26 - tests/test_object_view_office_scoping.py (9) + test_blacklist_stays_company_wide.py (2)

- **Verified by breaking it, not by watching it pass.** A security test that
  passes proves nothing until it has been shown to fail: with the new guards
  commented out, exactly the four cross-office assertions failed and the two
  "still works inside my own office" assertions kept passing. That is the
  evidence the tests detect the actual vulnerability rather than the happy path.
- One test premise was wrong on the first run and is worth recording: Observer
  cannot be used to prove "unrestricted roles bypass the office guard" on
  `send_sms`, because Observer is denied `sms.send` by the *action* gate, so
  its 403 says nothing about offices. Switched to a superuser, which is the
  other unrestricted case, and said so in the test.
- The blacklist file asserts the *negative* - that a Velky Meder manager still
  sees and can decide a Gyor case. It guards a plausible future mistake: a
  consistency sweep adding a guard there would read as an improvement in review
  while removing the point of the feature.
- Jober **667 passed**, CorvinumEU **425 passed, 12 skipped**.

## 2026-07-26 - tests/test_seed_demo_passwords.py (4 tests)

Covers a silent-revert risk rather than a calculation: `seed_demo` reset every
account's password on every run, so re-seeding staging would have republished
the password this public repo prints, with no error and no output saying it had
happened.

- `test_reseeding_keeps_a_rotated_password` is the regression itself.
- `test_reseeding_still_repairs_everything_else` guards the *other* direction,
  and is the more valuable of the two: "don't touch existing users' passwords"
  is one plausible edit away from "skip existing users entirely", which would
  quietly stop the seed from repairing roles and reactivating accounts. It
  asserts role, name and `is_active` are still corrected while the password is
  preserved.
- `test_reset_passwords_flag_forces_the_builtin_password_back` keeps the escape
  hatch honest.
- Module-skipped when `clients.jober.demo` is not installed, and marked
  `jober_only`, following the pattern established after
  `tests/test_finance_seed_splits.py` aborted the whole CorvinumEU lane during
  collection. Confirmed on both lanes this time rather than assumed: Jober
  **658 passed** (654 + 4), CorvinumEU **425 passed, 12 skipped** (the extra
  skip is this file).

## 2026-07-26 - i18n verified by rendering, not by reading the catalog

- The catalog said the office/finance strings existed; the *app* said
  otherwise. The check that found the gap was requesting `/sk/finance/` on
  live staging as `manazer@` and `pozorovatel@` and reading back the `<h2>`
  text - two headings came back in English inside an otherwise Slovak page.
  Grepping the `.po` would not have shown this, because the entries were
  present and fuzzy, and fuzzy entries compile away silently.
- Added no new test file. The guard that matters here is procedural and now
  recorded in the build journal: after `--extract`, count fuzzy and empty
  entries per catalog and require zero before compiling. Both counts are
  cheap to compute and would have caught this at any point in the last month.
- Full Jober unit lane and the CorvinumEU flag lane both run for this slice
  even though it changes no Python, because it changes templates that both
  clients render.

## 2026-07-25 - Guarding the finance seed's split invariant

- Two real breaks found while verifying the seed expansion, neither of them
  in the changed code's own tests:
  - `tests/test_finance_seed_splits.py` imported the seed command at module
    level, so on the **CorvinumEU lane** - which does not install
    `features.profitability` - it failed during *collection* and aborted all 425
    tests rather than skipping one file. `tests/test_office_scoping.py`
    already had the right pattern (`django_apps.is_installed` +
    `allow_module_level=True`); copied it.
  - `test_demo_scenario` asserted `month.cost == Decimal("9530")`, a figure
    baked in from the old hand-written 2025 stub. Rather than swap one magic
    number for another, it now asserts the invariant the code actually
    guarantees - month totals equal the sum of their line items, net is the
    difference - plus a `>= 8` line-item floor so the 2025 tail cannot
    silently regress to a stub again.

- `tests/test_finance_seed_splits.py` (15 tests) pins something that fails
  silently: `recompute_month()` derives a month's revenue/cost **from its line
  items**, so the figures in the monthly tables are only the initial record.
  A split summing to 0.98 raises nothing - it just seeds every month 2%
  cheaper than the table claims, and the demo shows numbers nobody wrote.
  Each per-project cost and revenue split is asserted to sum to exactly
  `Decimal("1.00")`.
- Also pinned: every seeded project has both splits (a missing one is a
  KeyError at seed time - better caught here than in front of the client);
  2025 and 2026 cover the same six projects, since the year-on-year
  comparison is only honest if they do; and each project's Dec-2025 figure
  sits below its Jan-2026 one so the trend reads as growth - with RLS 067
  excepted, as the deliberately declining contract.

## 2026-07-25 - Office badge overflowed the phone viewport (caught by a docs-only PR)

- `test_jober_notification_center_fits_phone_viewport` failed on a
  **Markdown-only** PR, where the code was byte-identical to `main` - which is
  what made it obvious the bug was already merged rather than introduced by
  that change.
- Cause: `static/src/css/app.css` hides `.account-role` at two breakpoints
  (<=1520px and mobile) because the role pill costs more header room than it
  earns. The office badge added in the visibility slice sat next to it but was
  never added to those rules, so at 375px it overflowed the header, forced
  horizontal scroll, and pushed the notification popover out of the viewport
  (`bounding_box()` returned `None`).
- Why every earlier run passed: exactly one e2e test uses a phone viewport,
  and it had not tripped in the orderings run during the badge slice or its CI.
  A desktop-only check would never have caught this.
- Fix: both breakpoints now hide `.account-role, .account-office` together,
  with a comment recording that the badge follows the role pill's rule.
- Verified: full Playwright e2e 50 passed, including the previously failing
  phone-viewport case.

## 2026-07-25 - Office-less people belong to their owning recruiter

- `tests/test_unassigned_people_scoping.py` (11 tests) pins each edge of the
  new rule rather than just the happy path: the owning recruiter sees their
  office-less person; **another recruiter in the same office does not**
  (ownership, not office membership, is what grants access); a manager does
  not; Observer does; and - the regression that matters most - a person who
  *has* an office is still governed by office alone, so the exception cannot
  be used to widen normal access. Queryset and object-level paths are
  asserted to agree, and a no-offices case proves CorvinumEU is unaffected.
- One existing test failed, correctly:
  `test_routine_update_shown_when_record_has_no_office` from slice 3 pinned
  the older fail-open behaviour in the notification feed. Rewritten rather
  than deleted - it now asserts both sides of the new rule (manager does not
  see it, owning recruiter does) with a docstring recording what it
  supersedes and why.
- Full verification: 639 Jober unit / 7 skipped, 425 CorvinumEU / 10 skipped
  / 157 deselected, 50 Playwright e2e, ruff check + format clean. Both lanes
  were run on the new test file before pushing this time, per the lesson from
  the previous slice.

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
    `features.profitability`).

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
    correctly self-skips, `features.profitability` isn't installed for
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
