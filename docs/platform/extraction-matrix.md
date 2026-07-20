> **Changelog, 2026-07-20:** The second Jober demo interview reverses Jober
> transport to OFF, confirms capability-level overlap between Jober operational
> debt and CorvinumEU advances, and confirms shared equipment with different
> client-selected reports. The received Jober P&L workbook unblocks Jober
> profitability specification and is explicitly distinct from the deferred
> CorvinumEU wage workbook. Existing artifact labels are otherwise unchanged.

> **Status: HISTORICAL EXTRACTION RECORD + SPECIFICATION DELTAS — this change
> does not alter the current build.**
> Per [ADR 0001](../adr/0001-jober-only-scope.md) the production app stays
> **single-client Jober** with no platform abstractions, client switching, or
> shared-client data models. This matrix is the **post-completion** extraction
> checklist (Stage B; see [ADR 0020](../adr/0020-white-label-platform-sequencing.md)
> and the draft [ADR 0021](../adr/0021-stage-b-extraction.md)). Execution is
> staged in [extraction-plan.md](extraction-plan.md) and begins only when ADR 0021
> is activated (Jober demo acceptance + pilot green-light).

# Jober → Platform Extraction Matrix

**Purpose:** label every Jober artifact so the shared-core extraction (Stage B, design doc §12.5) is a checklist, not a guess.
**Status:** **COMPLETED against the actual Jober repository, 2026-07-05** (post-PR #28: 11 apps, 26 models, 26 RBAC actions, 22 page templates, 9 management commands, 226 unit + 16 e2e tests). Supersedes the design-level seed rows.

---

## Labels

| Label | Meaning | Target location |
|---|---|---|
| **core** | Client-agnostic platform spine; both/all clients need it | `core/*` |
| **feature** | Reusable optional module, switched on per client | `features/*` |
| **client-policy** | Jober-specific business rule (statuses, approvals, workflows) | `clients/jober/policies` · `clients/jober/workflows` |
| **theme-ui** | Jober-specific branding, templates, static | `clients/jober/templates` · `clients/jober/static` |
| **infra** | Technical infrastructure (deploy, CI, settings, utilities) | `deploy/`, shared config |
| **obsolete** | Dead, superseded, or removable | delete |

**Assignment rule:** default a thing to the *most client-agnostic* label it can honestly hold. If it contains an `if client/feature`-style branch, split it: the agnostic part → core, the specific part → client-policy or feature. "Already in Jober" never auto-labels as core (design doc §7.0 reuse audit).

---

## Dependency baseline (swept 2026-07-05)

Deps must end up **feature → core only**. Current graph:

| App | Imports from | Verdict |
|---|---|---|
| `audit` | — | ✅ clean core candidate |
| `accounts` | audit | ✅ clean |
| `people` | accounts, audit, **blacklist, finance, logistics, messaging, projects** | ⚠️ core candidate importing 4 feature candidates — **split required** (slice B1) |
| `projects` | accounts, audit, people, **blacklist, logistics** | ⚠️ split required (activation gate, exit reconciliation — B1) |
| `apps/core` | accounts, **blacklist, compliance, finance, logistics**, people, projects | ⚠️ dashboard/reports aggregate everything — panel registry (B1) |
| logistics / finance / intake / messaging / compliance / feedback / blacklist | core candidates only | ✅ already point the right way |

The coupling is one-directional and localized to three call sites plus the
dashboard — see extraction-plan slice **B1** for the hook/registry designs.

---

## Per-app artifact rows

### `apps/accounts` → `core/accounts` (+ client-policy)

| Artifact | Type | Label | Target | Notes / split |
|---|---|---|---|---|
| `User` (email login), `UserManager` | model | core | `core/accounts` | maps cleanly; **2FA not yet built** — planned core addition (B4), required by CorvinumEU |
| `Role` enum (4 roles) | model choices | **client-policy** | `clients/jober/policies` | CorvinumEU has 7 roles; core defines the interface, client supplies the enum |
| `Action` enum + `can()` / `require_action` / `can_read_internal` (`permissions.py`) | authz mechanism | core | `core/accounts` | mechanism is client-agnostic; `BROAD_INTERNAL_READS` switch stays core config |
| `ACTION_ROLES` matrix (26 actions) | authz data | **client-policy** | `clients/jober/policies` | the role↔action grid is per client, loaded via `CLIENT_POLICIES` |
| `{% can %}` template tag | template tag | core | `core/accounts` | |
| `login_page` / `logout_view`, login template | view/UI | core | `core/accounts` + `core/ui` | Slovak URL slugs (`/prihlasenie/`) → client URL config |
| `seed_demo`, `reset_demo`, `ensure_superuser` | command | infra / client | `clients/jober` (seeds), `core/accounts` (ensure_superuser) | |

### `apps/audit` → `core/audit`

| Artifact | Type | Label | Target | Notes |
|---|---|---|---|---|
| `AuditEvent` (append-only), `record_event()` | model/service | core | `core/audit` | zero deps; move as-is |
| `audit.view` action | authz | core mechanism / client matrix | — | as with all actions: name core, grant client |

### `apps/people` → `core/people` (+ client-policy, split panels)

| Artifact | Type | Label | Target | Notes / split |
|---|---|---|---|---|
| `Person` (identity, lifecycle, archive, search) | model | core | `core/people` | CorvinumEU needs extra intake fields (children/smoking/…) → additive columns or a per-client profile extension model, decided in Stage C |
| `LifecycleStatus` + `set_status` mechanism | model/service | core | `core/people` | transition *engine* is core |
| `ALLOWED_TRANSITIONS` values (5-state Jober set) | workflow data | **client-policy** | `clients/jober/policies` | CorvinumEU has a 9-stage pipeline; core validates against the client-supplied map |
| `InactiveReason` catalog + seed | model | core | `core/people` | both clients need inactive/archive reasons (CorvinumEU §5.3); *seed values* per client |
| `SENSITIVE_FIELDS` + `can_view_sensitive` (`permissions.py`) | authz rule | **client-policy** | `clients/jober/policies` | visibility rules are Jober's Q4 answer; core defines the hook |
| `recycle_to_available`, `inactive_by_reason`, `person_history` | service | core | `core/people` | `person_history` currently reads feature models → becomes registry-fed (B1) |
| `people_list`, `person_create/edit/detail`, `recycle_person` views + `PersonForm` | view/UI | core | `core/people` | `person_detail` context + template compose 5 feature panels → **panel registry** (B1); blacklist-ID field on the form → contributed by `features/duplicate_blacklist` |
| `person_detail.html`, `person_form.html`, `people_list.html` | template | core + theme-ui | `core/ui` + `clients/jober/templates` | structure core; branding/wording client |
| `seed_people` | command | client | `clients/jober` | move its finance/logistics/equipment seeding into feature seeds (B1) |

### `apps/projects` → split: `core/organizations` + `core/assignments` + `features/recruitment_trials`

| Artifact | Type | Label | Target | Notes / split |
|---|---|---|---|---|
| `Project` (partner, office, coordinators M2M) | model | core | `core/organizations` | "companies are projects" (CorvinumEU interview); CorvinumEU adds PartnerCompany/Worksite/Position as siblings in Stage C |
| `ProjectAssignment` (one-active rule, snapshots) | model | core | `core/assignments` | |
| `activate_on_project` / `end_assignment` / `exit_person` | service | core | `core/assignments` | **B1 splits:** blacklist gate → pre-activation policy hook; room/equipment return inside `exit_person` → post-exit hook the features subscribe to |
| `TrialAssignment`, `ReadinessRecord`, trial/readiness services + ADR 0018 gate | model/service | **feature** | `features/recruitment_trials` | Jober's trial-day workflow; CorvinumEU's `TestEvent` is a sibling design, not shared code |
| `project_list/detail`, `trials_queue`, `trial_outcome`, `readiness_update`, `activate_person`, `exit_view` views | view | core / feature | per model split above | |
| `project.assign/manage`, `trial.record_outcome`, `readiness.complete`, `approval.activate`, `exit.reconcile` actions | authz | mechanism core / grants client | — | |

### `apps/logistics` → split three ways

| Artifact | Type | Label | Target | Notes |
|---|---|---|---|---|
| `Accommodation`, `Room` (+ `monthly_rate`), `RoomAssignment` (+ `rate_override`, `effective_rate`) | model | **feature** | `features/accommodation` | Jober-only (CorvinumEU excludes housing) |
| `assign_room`/`release_room`, rate services, `accommodation_cost_report` | service | feature | `features/accommodation` | |
| accommodation views + 3 templates + `room.assign`/`accommodation.manage` actions | view/UI | feature | `features/accommodation` | |
| `EquipmentItem` (unit_price), `EquipmentIssue` (+ `DeductionReviewStatus` review fields) | model | **feature** | `features/equipment` | **shared by both clients** (flag resolved below); Jober's target adds warehouse receipts/movements by item+size, while CorvinumEU retains per-issue value/custody |
| `issue/return_equipment`, `flag_unreturned`, `review_deduction`, `pending_deduction_reviews`, `issued_equipment_value` | service | feature | `features/equipment` | Report policy diverges: Jober selects stock balance/monthly in-out and does not require person-carried value; CorvinumEU selects person-level outstanding items/value |
| equipment views, `equipment_reviews.html`, `equipment.issue_return`/`equipment.review_deduction` actions | view/UI | feature | `features/equipment` | |
| `TransportWeek`, `record_transport_week`, `transport_trends` view/template, `transport.record` action | model/view | **feature** | `features/transport` | **Target OFF for both clients.** Jober removed transport in the second interview; its current runtime flag/code remain until a separate build prompt |

### `apps/finance` → `features/profitability` (Jober-only)

| Artifact | Type | Label | Target | Notes |
|---|---|---|---|---|
| `FinancialMonth`, `FinanceCategory`, `FinanceLineItem` (current positive-storage implementation; target reconciliation pending) | model | feature | `features/profitability` | Jober-only project-month P&L; verified filled source uses negative costs and positive revenues. This feature is distinct from, but may receive totals from, per-person recovery/advances |
| all finance services (line items, recompute, lock/reopen, rollups, `company_totals`) | service | feature | `features/profitability` | |
| 7 finance views, 3 templates, `finance.manage`/`finance.view_summary` actions, `seed_finance` | view/UI/command | feature | `features/profitability` | category *labels* are Jober data (seed) |

### `apps/intake` → `features/intake`

| Artifact | Type | Label | Target | Notes |
|---|---|---|---|---|
| `IntakeQuestionnaireVersion`, `IntakePanel`, `IntakeQuestion`, `RecruitmentIntake`, `IntakeAnswer` | model | feature | `features/intake` | the **engine** (versioned questionnaire, typed-negative gating) is reusable; the *questionnaire content* is seeded per client (`seed_questionnaire` → client seed) |
| `intake_start`/`intake_panel` views, `intake_panel.html`, `intake.create_edit` action | view/UI | feature | `features/intake` | |

### `apps/messaging` → `features/worker_messaging` (Jober-only)

| Artifact | Type | Label | Target | Notes |
|---|---|---|---|---|
| `MessageTemplate`, `OutboundMessage`, `InboundMessage` | model | feature | `features/worker_messaging` | Jober selects Twilio SMS plus Telegram channel-bot broadcast; CorvinumEU rejected automated messaging (phone + Messenger) — flag off |
| `send_sms` (stdlib Twilio), `verify_twilio_signature`, `twilio_inbound` webhook | service/view | feature | `features/worker_messaging` | Telegram adapter/config is a Jober spec delta pending channel access; webhook URL stays un-prefixed infra routing |
| `sms.send`/`sms.manage_templates` actions, SMS panel on person card | authz/UI | feature | contributed via panel registry (B1) | |

### `apps/compliance` → `features/documents` family (both clients)

| Artifact | Type | Label | Target | Notes |
|---|---|---|---|---|
| `Certificate` (dates-only), `compliance_alerts`, `add_months` | model/service | feature | `features/documents` | Jober = dates-only alerts; CorvinumEU extends the same family with files/verification/visibility in Stage C — design the feature so Certificate is the minimal case |
| `compliance_list` view/template | view/UI | feature | `features/documents` | |

### `apps/feedback` → `features/feedback` (Jober-only)

| Artifact | Type | Label | Target | Notes |
|---|---|---|---|---|
| `FeedbackLink` (token), `FeedbackSubmission`, `purge_feedback` | model/command | feature | `features/feedback` | CorvinumEU rejected a worker portal; purge pattern generalizes into `core/retention` (B4) |
| `feedback_form` (public), `feedback_inbox`, `feedback_link_create`, `feedback.view` action | view | feature | `features/feedback` | |

### `apps/blacklist` → `features/duplicate_blacklist` (both clients)

| Artifact | Type | Label | Target | Notes |
|---|---|---|---|---|
| `BlacklistCategory`, `BlacklistCase`, `MatchFingerprint` (HMAC, key rotation) | model | feature | `features/duplicate_blacklist` | confirmed shared; CorvinumEU adds DuplicateMatch review states in Stage C |
| `compute_fingerprint`, `check_match`, `propose/decide/remove_case`, `has_open_case`, `purge_expired` + `purge_blacklist` | service/command | feature | `features/duplicate_blacklist` | activation gate + intake check delivered via B1 hooks; retention joins `core/retention` (B4) |
| queue/propose/decide/remove views, `blacklist_queue.html`, 3 blacklist actions | view/UI | feature | `features/duplicate_blacklist` | reason-visibility grant (coordinator+manager) is client-policy data |
| `BLACKLIST_HMAC_KEYS` / `MATCHING_ENABLED` / `RETENTION_DAYS` settings | config | feature config | client settings | legal gate stays per client |

### `apps/core` → split: `core/ui` + registries + per-feature exports

| Artifact | Type | Label | Target | Notes |
|---|---|---|---|---|
| `healthz` | view | infra | `core/ui` | |
| `dashboard`, `reports` (aggregate all modules) | view | core mechanism | `core/ui` + **panel registry** | features contribute tiles/panels; today's cross-imports dissolve (B1) |
| `exports.py` (people/projects/finance CSV, `export.approved`) | view | per-feature | each feature ships its export | export *framework* (approved-exports gate) stays core |
| `seed_demo_scenario` | command | client | `clients/jober` demo assets | with the demo runbook |

### RBAC actions (all 26) — mechanism core, grants client-policy

The `Action` **names** and enforcement live in `core/accounts`; which roles hold
each grant is the client's `ACTION_ROLES` matrix. Feature-owned actions move with
their feature; the client matrix only grants what its enabled features register.

| Action | Owner after extraction |
|---|---|
| `intake.create_edit`, `intake.assign_trial` | `features/intake` / `features/recruitment_trials` |
| `person.recycle_available` | `core/people` |
| `sms.send`, `sms.manage_templates` | `features/worker_messaging` |
| `project.assign`, `project.manage`, `approval.activate` | `core/organizations` + `core/assignments` |
| `trial.record_outcome`, `readiness.complete` | `features/recruitment_trials` |
| `room.assign`, `accommodation.manage` | `features/accommodation` |
| `equipment.issue_return`, `equipment.review_deduction`, `catalog.manage` | `features/equipment` |
| `transport.record` | `features/transport` |
| `exit.reconcile` | `core/assignments` (hooks notify features) |
| `user.manage` | `core/accounts` |
| `blacklist.propose`, `blacklist.decide`, `blacklist.view_reason` | `features/duplicate_blacklist` |
| `finance.manage`, `finance.view_summary` | `features/profitability` |
| `export.approved` | core export framework (per-feature exports register under it) |
| `feedback.view` | `features/feedback` |
| `audit.view` | `core/audit` |

### Templates, static, i18n

| Artifact | Label | Target | Notes |
|---|---|---|---|
| `templates/layouts/base.html` (nav, language switch, role badge) | core + theme hooks | `core/ui` | nav tabs become registry-driven; logo/branding blocks overridable per client |
| 22 `templates/pages/*` | follow their app | per rows above | |
| `static/` (Tailwind build, vendored htmx/Alpine + checksums) | infra + theme | shared build; tokens per client | CorvinumEU theme = corvinum.eu design system (§7.0 reuse audit gates any component transplant) |
| `locale/{sk,hu,uk}` catalogs (EN source) | core + per-feature | split per app move | msgids move with their apps; client-specific wording in client catalogs; CorvinumEU = SK/HU dual-field |

### Infra (shared, unchanged by extraction)

| Artifact | Label | Notes |
|---|---|---|
| Dockerfiles (digest-pinned), `requirements/*.lock` (hash-pinned), `scripts/*` (dev_app, dev_db, playwright, compile_messages, checks) | infra | settings become layered: `config/settings/base` + `clients/<client>/settings`; one artifact, deployed once per client (§12.4) |
| `tests/` (226 unit + 16 e2e) | infra | the Stage B safety net; reorganized alongside app moves, assertions unchanged (Stage D bar) |

### Obsolete

| Artifact | Notes |
|---|---|
| `demo/` static prototype (already non-authoritative) | stays historical reference; not extracted |
| — no dead production code identified in the sweep | |

---

## Open flags — RESOLVED (2026-07-05, against the repo)

- ~~**Advances vs. Jober financials overlap.**~~ **Confirmed capability-level
  overlap (second Jober interview, 2026-07-20).** Jober moves per-person
  operational debt/recovery money (the compliance example showed a person
  "EUR 850 in the red"), so `features/advances` is not purely net-new from a
  product-capability perspective. Exact model/service reuse, Jober entry types,
  approvals, and settlement remain a later design/build decision. This is not
  wage computation and must never auto-deduct payroll. Jober-only project P&L
  remains separately owned by `features/profitability`.
- ~~**Equipment on both clients.**~~ **Yes — shared.** Jober ships
  issue/return/deduction-review and targets a warehouse stock ledger;
  `features/equipment` serves both. Client policy selects genuinely different
  reports: Jober balance by item/size/value plus monthly in-out, CorvinumEU
  per-person custody/outstanding value for recovery decisions. Neither report
  substitutes for the other.
- **Finance workbook provenance.** `HV 202510.xlsx` (called `HV_202510.xlsx` in
  discovery notes) is the received Jober per-project P&L and unblocks that
  specification. It is not `radonak.xlsx`, the deferred CorvinumEU per-worker
  wage sheet. The two files do not gate or specify the same feature.
- ~~**Auth compatibility.**~~ **Compatible, with one addition.** Email-login
  `User` + action-gated RBAC transfer cleanly; **2FA must be added to
  `core/accounts`** (B4) — a genuinely reusable core capability, not a workaround.
  Role enum + grants matrix become client-policy.
- ~~**Core importing features.**~~ **Located and bounded:** three call sites
  (`people` panels/matching, `projects` gate/exit, `apps/core` dashboard) — all
  dissolved by the B1 hook/registry designs in
  [extraction-plan.md](extraction-plan.md).
