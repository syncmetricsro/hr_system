# Build Journal

## 2026-07-11 — Stage C0: CorvinumEU thin-client scaffold (ADR 0022)

Stage C activated by the owner (2026-07-11). ADR 0022 records the scope
mapping — reuse `features/{logistics(equipment),blacklist,compliance,intake}`;
build `features/checklists` + `features/advances`; `fuel_costs` NOT built
(design-doc A1: unconfirmed, secondhand); deployment deferred (no server
names). `clients/corvinum_eu/` lands: explicit INSTALLED_APPS (no finance/
messaging/feedback apps), CorvinumEU flag set, SK/HU, 2FA required for
managers, CE branding, trial-less lifecycle + grants in `policies.py`.
Unconfirmed client decisions build against recorded defaults —
`docs/product/corvinum-open-questions.md` (C-Q1…C-Q14).

Ops: the host lost `/var/lib/docker` (external deletion while the daemon ran)
— all images/volumes destroyed; daemon reset, test image rebuilt from the
hash-pinned `requirements/test.lock` on the digest-pinned Python base, dev DB
recreated. The accounting-project Postgres volume was unrecoverable (dead
before salvage was possible); Jober data was all re-seedable.


## 2026-07-09 — STAGE B COMPLETE: shared core + thin-client architecture

ADR 0021 executed end-to-end (PRs #36–#45), assertions unchanged throughout.

- **B-1/B0**: governance (owner waiver recorded), `pre-stage-b` tag,
  FEATURE_FLAGS + CLIENT_POLICIES, dependency tripwire (debt enumerated: 10).
- **B1 (a–c)**: decoupling — activation/exit hooks, the surface registry
  (person panels/banners/form-extensions/exit-relevance, report tiles/panels),
  per-feature exports and seeds, `clients/jober/demo`. **Debt 10 → 0.**
- **B2**: `git mv` reshape to `core/{accounts,audit,people,projects,ui,retention}`
  + `features/{7 apps}`; basenames kept ⇒ labels/tables/FKs untouched;
  `migrate --check` clean against a live-DB dump.
- **B3**: client policy layer — grants/lifecycle/sensitive-visibility moved
  verbatim to `clients/jober/policies.py`, neutral deny-by-default core
  fallbacks, flag-gated URLconf, brand context, `clients/_smoke` proves the
  core boots with zero features/client.
- **B4**: `core/retention` (registry + `run_retention`) and **stdlib TOTP 2FA**
  (RFC 6238 vectors tested; `TWO_FACTOR_REQUIRED_ROLES=[]` for Jober ⇒ zero
  behavior change). Demo seeds moved fully into `clients/jober/demo`.
- **B5**: Stage D sweep green — dep direction clean, `core/` free of client
  conditionals, smoke client passes checks, **242 unit + 16 e2e**, demo stack
  rebuilt on the extracted architecture with the scenario intact.

Stage C (CorvinumEU thin client) now starts from `clients/corvinum_eu/` +
feature flags + the design prototype — configuration and theming, not a rebuild.


## 2026-07-08 — PROGRESS REPORT (owner-requested snapshot)

**Where we are in one sentence:** the Jober product is feature-complete and
demo-ready; all five client questions are answered and implemented; the
platform extraction (Stage B) is activated and ~40% executed, with the
dependency debt already down from 10 edges to 6.

### Jober product (Phases 0–5)
- **Phases 0–4: DONE** — foundation/supply-chain, auth/RBAC/i18n/audit, the
  full workforce core (people, intake, trials, readiness, dashboards, SMS),
  logistics (rooms+pricing Q1, equipment+deduction review Q2, transport),
  compliance alerts, feedback, exit/recycle+inactive reasons Q5, the blacklist
  with HMAC matching Q3 (execution gated on the pending LIA/written text), and
  finance with the confirmed positive convention Q4 (line items, lock/reopen,
  rollups).
- **Quality layer:** full UI redesign ("calm industrial"), nav active-state
  fix, i18n gap audit (no user-facing gaps), internal security review (no
  high/medium findings), 16-test browser e2e suite, demo scenario seed +
  presenter runbook (SMS live; Telegram re-ask scripted).
- **Phase 5 (pilot): NOT STARTED, by design** — gated on the customer demo →
  acceptance → real-data/legal gate. External items outstanding: blacklist
  LIA + written contract text, one filled finance month (label reconciliation),
  Dokku staging names, Twilio account upgrade, native translation review.

### Platform (core + thin clients, ADR 0021)
- **ADR 0021 ACTIVATED 2026-07-07** (owner waiver of the demo-acceptance
  trigger recorded). Safety: tag `pre-stage-b` pushed; the running demo
  container stays on its pre-extraction image until B5.
- Slice progress:
  - **B-1 governance** — merged (PR #36).
  - **B0 flags + tripwire** — merged (PR #37): FEATURE_FLAGS, CLIENT_POLICIES,
    dependency-direction check with the debt enumerated (10 edges).
  - **B1a hooks** — merged (PR #38): activation/exit registries; projects no
    longer imports blacklist/logistics (debt 10 → 8).
  - **B1b surface registry** — merged (PR #39): person card composed by
    feature registration (panels/banners/form-extensions/exit-relevance);
    people no longer imports blacklist/messaging (debt 8 → 6).
  - **B1c (in progress):** reports tiles/panels via registry, finance export
    moved home, seed untangling, `clients/jober/demo` app — target debt 0.
  - **B2–B5 pending:** repo reshape (git mv, labels preserved), client policy
    layer + smoke client, retention + stdlib TOTP 2FA, final validation.
- Throughout: **test assertions unchanged** (Stage D bar); suite currently
  231 unit + 16 e2e, green at every merged slice.

### CorvinumEU (Stage C inputs, ready and waiting)
- Design doc v0.6 + Addendum A1 (fuel money, pending confirmation) + A2.
- Clickable 12-page design prototype (left slide-out sidebar, corvinum.eu
  design language, dark/light) on the `peopleops-prototype` branch of the
  corvinumeu repo (unpushed).

### Risks / notes
- Stage B is mid-flight: main is stable and green at every slice, but the demo
  should run from the running container or the `pre-stage-b` tag until B5
  re-validates.
- 39 PRs merged to date; the ~2–3 week Stage B estimate still holds (the
  hardest 40% — decoupling — is nearly done).


## 2026-06-29 — Phase 3 (6/n): inventory valuation

The unblocked part of inventory (round-4 confirmed valuation method: latest manual price, no weighted-average). Deduction review for missing items stays deferred (open decision).

- `EquipmentItem.unit_price` (manual latest price). `issued_equipment_value(person=None)` sums active issues × price (DB aggregate), company-wide or per person.
- Surfaced on the person card equipment panel (per-person value) and the Reports page (company "Equipment value" card). Admin shows/edits price; `seed_people` sets demo prices. i18n SK/HU/UK.

Verification: ruff clean; **166 unit tests pass** (3 new: qty×price sum company/per-person, returns excluded, zero when none).

## 2026-06-29 — Phase 3 (5/n): operational reports

- `core.views.reports`: read-only cross-module summary (plan §3) — active projects, total people, pending trials, compliance-alert count, accommodation occupancy, people-by-status, and a finance block gated by `finance.view_summary` (managers/observers). Reuses existing services; no new models.
- Reports nav tab + `/reports/`. i18n SK/HU/UK.

Verification: ruff clean; **163 unit tests pass** (4 new: login required, counts render, finance section hidden from recruiter / shown to observer).

## 2026-06-29 — Phase 3 (4/n): QR feedback + manager inbox

Worker-facing feedback (plan §10.1 `/feedback/<token>`, §11.11).

- `apps/feedback`: `FeedbackLink` (tokenized public entry point the QR encodes; optional project) and `FeedbackSubmission` (message + optional rating; **no account/PII**).
- Public **no-login** form at `/feedback/<token>/` (standalone template, not the app shell) → records a submission, shows a thank-you. Inactive/unknown token → 404.
- **Manager-only inbox** (`feedback.view`) listing submissions + active links with their public URLs + a create-link form. Gated nav tab.
- **Retention**: `purge_feedback` management command deletes submissions older than `FEEDBACK_RETENTION_DAYS` (≈1 month). i18n SK/HU/UK.

Verification: ruff clean; **159 unit tests pass** (5 new: public submit, message required, inactive/unknown 404, inbox manager-only, retention purge); image builds.

## 2026-06-28 — Phase 3 (3/n): transport trends

- `logistics.views.transport_trends`: last-12-weeks transport headcount per project + company total per week (plan §11.10), rendered as **dependency-free CSS bar charts** (no JS library).
- New Transport nav tab + `/transport/`. i18n SK/HU/UK.

Verification: ruff clean; **151 unit tests pass** (2 new: login required; company total = sum across projects).

## 2026-06-28 — Phase 3 (2/n): exit reconciliation & recycling

- `projects.services.exit_person`: atomic exit reconciliation (plan §11.13) — ends the active project assignment, releases the room, returns all issued equipment, then recycles the person to **Available** (default) or **Inactive**; audited. Orchestrates the existing lifecycle + logistics services. Missing-returnable-item **deductions remain an open decision** and are not modelled.
- Exit panel on the person card (gated `exit.reconcile` — coordinator + manager) with Exit-to-Available / Exit-to-Inactive; shown when there's something to reconcile (Working, active room, or issued equipment).
- i18n SK/HU/UK. No new migrations (reuses existing models).

Verification: ruff clean; **149 unit tests pass** (4 new: full reconcile + recycle, exit-to-inactive, view RBAC deny/allow).

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

## 2026-07-05

Stage B platform extraction — planning completed (docs only, build gated).

What changed (no production code touched; ADR 0001 still governs):
- `docs/platform/extraction-matrix.md`: DRAFT → **completed against the real
  repo** (2026-07-05 sweep: 11 apps, 26 models, 26 RBAC actions, 22 page
  templates, 9 commands). Per-artifact rows for every app; explicit all-26
  RBAC-actions table; dependency baseline table. All four open flags **resolved
  with repo evidence** (advances↔finance: no overlap; equipment: shared; auth:
  compatible + 2FA to add; core→feature coupling: three call sites + dashboard).
- `docs/platform/extraction-plan.md` (new): staged execution B0–B5 — safety
  net/flags → decouple (hook + registry designs for the four coupling sites) →
  in-place `git mv` reshape with **AppConfig.label pinning so no data migration**
  → `clients/jober/` policy layer → core additions CorvinumEU needs (2FA,
  retention, tasks) → validation. Risks + per-slice done-criteria; ~2–3 weeks
  (§12.5 estimate holds given the localized coupling).
- `docs/adr/0021-stage-b-extraction.md` (new): **Proposed** — activation trigger
  is Jober demo acceptance + owner go-ahead; on activation it supersedes ADR 0001
  and the plan's slices may land. Not in force while Proposed.
- Source register: both new docs registered as non-authoritative until activation.

Verification: docs-only diff; completeness check script confirms every model,
command, and action appears in the matrix; matrix ↔ plan ↔ ADR cross-references
consistent.

## 2026-07-04 (later)

Customer demo tooling — full-scenario seed + presenter runbook.

What changed:
- `apps/core/management/commands/seed_demo_scenario.py` — idempotent, fictional
  orchestration (via the real services) that fills every module screen for the
  demo: finance line items on DHLBA 2026-05 (+ recompute), two equipment items
  issued to Olha with one **flagged unreturned** (Reviews queue), Bohdan's
  **inactive reason**, an expiring **certificate**, a **blacklisted** person
  ("Ivan Zablokovaný", hashed ID `SK-DEMO-BL-001`) for the live re-entry moment,
  a **proposed** blacklist case on Diana to decide live, and a phone for Olha.
  Wired into `scripts/dev_app.sh up` after the other seeds.
- `docs/deployment/demo-runbook.md` — the ~60-min presenter script (Slovak +
  a Hungarian switch): prep/go-no-go, logins, cast, 11 acts mapped to the pains
  and the five answered questions, caveats, and the closing ask. Linked from
  `docs/deployment/local-demo.md`.

Verification: **226 unit tests pass** (was 224) — `tests/test_demo_scenario.py`
asserts every module screen is populated (finance net = revenue − cost = 6900,
pending equipment review, "Sick" inactive bucket, blacklisted person + active
fingerprint, `check_match("SK-DEMO-BL-001")` hits, a compliance alert, Olha's
phone) and that re-running the seed is idempotent. ruff clean.

## 2026-07-04

Blacklist & HMAC matching module (Q3 unblocked) — `apps/blacklist/`.

Jober confirmed the legal basis: **legitimate interest** (fraud prevention /
security vetting / hiring decisions). The last hard-blocked module is now built,
on the authoritative Jober spec (`Product_Design.md` §11.14 / §12.13). The written
contract text + a documented LIA are still pending, so **real-data execution stays
gated** (`BLACKLIST_MATCHING_ENABLED`); fictional data only until sign-off.

What changed:
- New `apps/blacklist/`: `BlacklistCategory` (configurable, seeded neutral
  placeholders), `BlacklistCase` (proposed/approved/rejected/removed), and
  `MatchFingerprint` (keyed **HMAC-SHA256** of a transiently-entered ID —
  **raw identifier never stored**; `key_version` allows key rotation). Migrations
  0001 + 0002 (seed).
- Services: `compute_fingerprint` (normalized, keyed), `check_match` (company-wide,
  active/non-expired, honours the enable gate), `propose_case` (no lifecycle
  change), `decide_case` (approve → BLACKLISTED + activate fingerprint; reject),
  `remove_case` (→ Available + revoke), `has_open_case`, `purge_expired` + a
  `purge_blacklist` command.
- Warning flow (§12.13): optional non-persisted ID on the intake form
  (`PersonForm`) → on a match, create the person, auto-propose a case, and warn —
  **no block, no silent merge**. `activate_on_project` now **hard-gates** on an
  unresolved case.
- RBAC: new **`blacklist.propose`** (coordinator + manager); **widened
  `blacklist.view_reason`** to coordinator + manager (client's visibility rule:
  flag = recruiter + coordinator + manager; reason = coordinator + manager);
  `blacklist.decide` stays manager-only. Matrix updated.
- UI: person-detail blacklist panel (flag to all; reason gated; propose/decide/
  remove), a warning banner, a manager review queue, a manager-only **Blacklist**
  nav tab. Admin + i18n SK/HU/UK. Settings: `BLACKLIST_HMAC_KEYS`,
  `BLACKLIST_MATCHING_ENABLED`, `BLACKLIST_RETENTION_DAYS`.
- Legal: `docs/security/blacklist-legal-basis.md` (legitimate-interest grounds +
  LIA placeholder + data-handling); Q3 in the open-questions doc marked BUILT.

Verification: ruff clean; **224 unit tests pass** (was 202) + **16 e2e** (blacklist
queue renders; manager sees the tab; coordinator 403). Covered: keyed/deterministic
hash, **raw id never persisted**, active/company-wide matching, propose→approve→
BLACKLISTED + fingerprint active, remove→Available + revoke, reject no-op,
open-case blocks activation, intake match warns without blocking, RBAC, retention
purge. Migrations build under pytest.

Next step:
- On the written text + LIA: confirm retention period + reason-category list, then
  lift the real-data gate. Q3 is the last blocker; everything else is merged.

## 2026-06-30

Finance sign convention CONFIRMED (Q4) — positive convention + hardening.

Jober confirmed (2026-06-29): costs and revenues are entered as **positive**
numbers; the system computes `net = revenue − cost`. This is exactly how the
finance module was already built (PRs #16–#17: amounts stored positive, sign
from the category kind), so the confirmation **validates** the existing build
rather than unblocking new work. This slice enforces the convention so it can't
be violated, and flips the docs from "assumption" to "confirmed".

What changed:
- `apps/finance/services.py`: `positive_amount()` guard — `set_line_item` and
  `record_financial_month` now **reject negative** amounts (raise FinanceError,
  surfaced by the existing view try/except).
- `apps/logistics/services.py`: `_non_negative()` guard on `set_room_rate` /
  `set_assignment_rate` (raise ValueError; the rate views now catch it and show
  a message instead of 500ing).
- Model validators (`MinValueValidator(0)`) on every money field for admin/form
  defence: finance line-item amount, monthly revenue/cost; room monthly_rate +
  rate_override, equipment unit_price, unreturned-item charge_amount. Migrations
  `finance/0003` + `logistics/0007` (validator-only; no data change).
- Docstrings + `docs/product/phase3-4-open-questions.md` Q4 +
  `docs/product/open-decisions.md`: assumption → **confirmed 2026-06-29**.

Point-by-point vs the request: (1) all cost fields accept/process positives —
yes, and negatives are now rejected; (2) ledger entries align — the Jober
finance model is project-month P&L (FinancialMonth + line items), not a
per-worker cash ledger (that's the CorvinumEU design); it computes
`net = revenue − cost` on positive inputs; (3) equipment charge =
`unit_price × quantity`, positive arithmetic, prices/charges validated
non-negative; (4) no ambiguous calc found — net is unambiguous under positives.

Verification: ruff clean; **207 unit tests pass** (was 202) — positive net =
revenue − cost, and negatives rejected for line items, monthly cost, room rate,
and assignment override. Migrations build under pytest.

Next step:
- Still useful (not blocking): a real filled month to reconcile the seeded
  category labels. Otherwise finance is done; remaining blocker is Q3 blacklist.

## 2026-06-29 (later 5)

Reports polish — inactive-by-reason breakdown.

What changed:
- `apps/people/services.py`: `inactive_by_reason(include_archived=False)` —
  counts Inactive people grouped by their structured reason (Q5), most-common
  first, with a "No reason" bucket for nulls; non-archived by default to match
  the reports page's workforce counts.
- Reports view/template gained an "Inactive by reason" panel next to "People by
  status". i18n SK/HU/UK.

Verification: ruff clean; **202 unit tests pass** (was 198) — grouping/ordering,
null bucket, archived excluded by default (and included on request), empty case.
(Read-only reporting; no model change, no migration.)

## 2026-06-29 (later 4)

Inactive-reasons catalog + exit recycling (Q5 + lifecycle polish).

What changed:
- `apps/people/models.py`: `InactiveReason` catalog (label, is_active, order —
  configurable in admin) and `Person.inactive_reason` FK + `Person.inactive_since`.
  Migration `0002`; data migration `0003` seeds the Q5 placeholders (Sick,
  Quit / left, Suspended, Military service, Other).
- `apps/projects/services.py`: `exit_person` now takes `inactive_reason` and,
  when exiting to Inactive, records the structured reason + since-date on the
  person (replacing the free-text-only exit).
- `apps/people/services.py`: `recycle_to_available` — returns an **Inactive**
  person to the **Available** pool (INACTIVE→AVAILABLE is already an allowed
  transition), clears the reason/since, audited `person.recycled`. Guarded to
  Inactive-only.
- views/urls: exit form captures the reason; `recycle_person` (POST) wires the
  previously-defined-but-**unused** `person.recycle_available` action
  (recruiter + coordinator + manager). Templates: reason `<select>` on the
  Exit-to-Inactive form, plus an Inactive panel showing the reason/since and a
  Recycle-to-Available button. Admin for `InactiveReason` + reason column on
  Person. i18n SK/HU/UK.

Verification: ruff clean; **198 unit tests pass** (was 192) — the `0003`
migration seeds the placeholders, exit-to-inactive records reason + since,
recycle clears them and returns Available, recycle is guarded to Inactive-only,
RBAC (recruiter/coordinator/manager yes, observer no), and the recycle view is
403 for observer / 302 + Available for coordinator.

Next step:
- Remaining work is blocked on Jober (blacklist legal Q3; the charge/deduct
  behaviours behind Q1/Q2/Q4). This clears the last safe-default-buildable slice.

## 2026-06-29 (later 3)

Phase 3 unreturned-equipment deduction review queue (Q2 safe default).

What changed:
- `apps/logistics/models.py`: `DeductionReviewStatus` (NONE/PENDING/APPROVED/
  WAIVED) + `review_status`, `charge_amount`, `reviewed_by/at`, `review_note` on
  `EquipmentIssue`. Migration `0006`. The charge review is **separate from the
  physical status** — a flagged item is still ISSUED (not returned) but its
  *charge* is under manager review. **No payroll deduction is ever executed**;
  APPROVED only records the manager's decision to recover (Q2 safe default).
- `apps/logistics/services.py`: `flag_unreturned` (snapshots
  `quantity × item.unit_price`, guarded to issued + un-reviewed), `review_deduction`
  (approve/waive, guarded to pending, audited), `pending_deduction_reviews`
  (queue + dynamic outstanding total). `exit_person` now **skips already-flagged
  items** when auto-returning (leaves them for the queue), replacing the old
  "deductions not modelled yet" note.
- RBAC: new **manager-only** `equipment.review_deduction` (queue + approve/waive);
  flagging uses the existing coordinator+manager `equipment.issue_return`.
  permission-matrix.md updated.
- views/urls: `flag_unreturned`, `equipment_reviews` (queue), `review_deduction`.
  Templates: per-item "Flag unreturned" + status badges on the person card; a
  manager review-queue page (approve/waive + note, outstanding total, "no
  automatic deduction" note); a manager-only **Reviews** nav tab. Admin + i18n
  SK/HU/UK.

Verification: ruff clean; **192 unit tests pass** (was 184) — flag snapshots the
charge at unit price, can't flag returned/double-flag, approve/waive records the
reviewer + note, review requires pending + a valid decision, the queue total is
dynamic, **exit leaves flagged items for review** while auto-returning the rest,
manager-only RBAC, and the queue view is 403 for coordinator / 200 for manager.
Migration `0006` builds under pytest.

Next step:
- Inactive-reasons catalog + exit recycling (small lifecycle slice), or wait on
  the blocked items (blacklist legal; the finance/accommodation/equipment answers).

## 2026-06-29 (later 2)

Phase 3 accommodation pricing + occupancy-cost reporting (Q1 safe default).

What changed:
- `apps/logistics/models.py`: `Room.monthly_rate` (per-room monthly EUR) and
  `RoomAssignment.rate_override` (optional per-assignment override) + an
  `effective_rate` property (override if set, else the room rate). Migration
  `0005`. This is the Q1 **safe default** — a per-room rate **recorded for
  reporting only, no payroll deduction** — and the room-rate-plus-override shape
  stays robust whether Jober's answer is per-room, per-bed, or per-person, so
  the slice is **not blocked** on the answer.
- `apps/logistics/services.py`: `set_room_rate`, `set_assignment_rate` (blank
  clears the override), and `accommodation_cost_report()` — per-accommodation
  occupancy plus two dynamic figures: `room_cost` (Σ room rates, standing) and
  `assigned_cost` (Σ effective rate over **active** assignments) + a company
  total. Reporting only; no deduction is created.
- `apps/logistics/views.py` + `config/urls.py`: `accommodation_costs` report,
  `set_room_rate_view`, `set_assignment_rate_view` — all gated **manager-only**
  (`accommodation.manage`, previously defined but unused). Coordinators still
  assign/release rooms; only managers see/set cost data.
- Templates: accommodation detail shows + edits room rates (manager); a cost
  report page (occupancy + room/assigned cost, with a "reporting only" note);
  person detail shows the effective rate and a manager override form; list links
  to the report. Admin + `seed_people` rates (€180/room). i18n SK/HU/UK.

Verification: ruff clean; **184 unit tests pass** (was 177) — rate set,
effective-rate override-then-room fallback, cost report room/assigned totals,
released assignments excluded from occupancy/assigned cost (standing room cost
remains), manager-only RBAC, and the cost view returns 403 to recruiter +
coordinator, 200 to manager. Migration `0005` builds under pytest.

Next step:
- Equipment unreturned → manager review queue (Q2 safe default), or the
  inactive-reasons catalog + exit recycling slice.

## 2026-06-29 (later)

Phase 4 finance — month lock/reopen and yearly/per-project rollups.

What changed:
- `apps/finance/services.py`: `lock_month` (close a month, audited `finance.locked`) and `reopen_month` (**reason mandatory**, recorded in the audit `reason` field as `finance.reopened` — Finance_Specs §5). Added read-only aggregations `project_totals(year=None)` and `yearly_totals()`; `company_totals` now takes an optional `year`. All dynamic — every project/month included.
- `apps/finance/views.py` + `config/urls.py`: `finance_month_lock` / `finance_month_reopen` (POST, FINANCE_MANAGE) and a `finance_year` page (per-project results + group breakdown + month list for one year). The month-detail form is now read-only when the month is locked (`editable = can_manage and not is_locked`), with manager-only lock / reopen-with-reason controls. The summary page gained per-project results and a yearly list linking into `finance_year`.
- No model changes (reuses `FinancialMonth.is_locked`), so no new migration.

Verification: ruff clean; **177 unit tests pass** (was 173) — lock blocks edits + reopen needs a reason, reopen reason is audited, the save view no-ops on a locked month, and project/yearly/company aggregations (incl. year filter + empty-year zero) are correct. Catalogs recompiled SK/HU/UK (fixed two fuzzy mis-matches: "Lock month"/"Reopen month").

Next step:
- Per-project line-item *columns* per `Finance_Specs.md`, or move to the accommodation pricing slice (Q1 safe-default).

## 2026-06-29

Phase 4 finance — configurable line-item catalog + per-month entry, recalc and group breakdowns.

What changed:
- `apps/finance/models.py`: `FinanceCategory` (configurable catalog: label, `kind` cost/revenue, `group`, active, order) and `FinanceLineItem` (one positive amount per category per `FinancialMonth`, unique together). Amounts are stored **positive**; the sign comes from `kind`, so `net = revenues − costs` holds regardless of which sign convention the source spreadsheet used (the open Phase-4 confirmation does not block this design).
- `apps/finance/services.py`: `set_line_item` (locked-month guarded, audited), `recompute_month` (rolls line items into `revenue`/`cost` by `kind` — summed **dynamically over the full set**, so it cannot reproduce the spreadsheet's off-by-one cost bug), and `group_breakdown` (per-group revenue−cost across one/all months for the manager's transport/accommodation/overhead view).
- `apps/finance/views.py` + `config/urls.py`: `finance_month_detail` (line-item entry form, gated FINANCE_VIEW_SUMMARY) and `finance_month_save` (FINANCE_MANAGE, POST → set items → recalc). `finance_summary` now shows the company group breakdown and links each month to its detail page.
- `seed_finance` management command seeds the 25-category catalog from `Finance_Specs.md §2` (idempotent); wired into `scripts/dev_app.sh up`. Admin registered for category + line item.
- i18n: new finance strings + group labels translated SK/HU/UK; fixed a reused-but-wrong "Overhead" (was "Prehľad"/overview → "Réžia") and "No line items yet." string.

Assumption recorded (still to confirm with Jober, one filled month): `net = revenue − cost`. The positive-amount + sign-by-kind model makes this robust either way.

Verification: ruff clean; **173 unit tests pass** (was 166) — recompute sums by kind, dynamic totals cover every cost row, locked-month blocks edits, group breakdown nets revenue−cost, save view persists + recomputes, detail view gated from recruiters. Migration `0002` builds cleanly under pytest; catalogs compiled. (Run `scripts/dev_app.sh rebuild` to pick up the new code in the local demo.)

Next step:
- Month lock/reopen UI (reason + audit) and the yearly rollup view; then per-project line-item columns per `Finance_Specs.md`.

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
