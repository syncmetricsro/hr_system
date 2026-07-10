> **Status: EXECUTED (2026-07-07 → 2026-07-09, PRs #36–#45).** As-executed
> deviations are recorded in ADR 0021; this text is kept as the plan of record.
> This is the staged execution plan for Stage B (shared-core extraction), to be
> run **only after** [ADR 0021](../adr/0021-stage-b-extraction.md) is activated
> (Jober demo acceptance + pilot green-light). Companion to the completed
> [extraction-matrix.md](extraction-matrix.md). Until activation, ADR 0001's
> single-client rule governs and none of these slices may land.

# Stage B execution plan — Jober → shared core + thin client

**Written:** 2026-07-05, against the repo at PR #28 (11 apps, 26 models, 226 unit
+ 16 e2e tests). **Strategy (decided):** evolve **HR_System in place**, one
reviewable PR slice at a time, each slice green on the full suite before the next.
**Target layout:** design doc §12.4 (`core/` + `features/` + `clients/` +
`deploy/`). **Acceptance bar throughout:** Stage D — no client conditionals in
core; every core change genuinely reusable; **Jober behavior preserved, proven by
the existing tests passing with assertions unchanged**.

## Slice sequence

Each slice = one branch → PR → merge, exactly like the Phase 0–4 workflow.
Estimated total: **2–3 weeks** (§12.5 estimate holds; B1 is ~40% of the work and
the couplings are already located and bounded — see the matrix dependency table).

---

### B0 · Safety net + scaffolding (½ day)

- Record the baseline: full unit + e2e counts, `manage.py showmigrations` state,
  and a dependency sweep snapshot (the matrix table) committed to the journal.
- Add **`FEATURE_FLAGS`** and **`CLIENT_POLICIES`** settings scaffolding to
  `config/settings/base.py` — Jober values = everything on, policies pointing at
  the current in-repo defaults. **No behavior change**; flags are read but all-on.
- Add a CI-runnable **dependency-direction check** (script asserting no
  core-candidate imports a feature-candidate) — it *fails* at B0 (documents the
  debt) and must pass by the end of B1. Modeled on
  `scripts/check_no_node_artifacts.py`.

**Done when:** suite green, flags visible in settings, dep-check script exists.

### B1 · Decouple core-candidates from feature-candidates (~40% of effort)

All moves happen **inside `apps/`** (no renames yet) so diffs stay reviewable.
Four call sites, four designs:

1. **Pre-activation policy hook** (`projects → blacklist`).
   `core`-side: `activation_checks` registry in `apps/projects/services.py`
   (list of callables raising `WorkflowError`). `apps/blacklist` registers
   `has_open_case` at app-ready. `activate_on_project` iterates the registry
   instead of importing blacklist. Same hook later carries CorvinumEU's
   checklist/document hard-stops.
2. **Post-exit hook** (`projects → logistics`).
   `exit_person` fires an `exit_reconciliation` hook (or Django signal);
   `features`-side handlers release the room and return unflagged equipment.
   Ordering: handlers must be idempotent; audit events unchanged (assert in tests).
3. **Panel/tile registry** (`people → 5 apps`, `apps/core → everything`).
   A small `core.ui.registry`: features register *(template name, context
   provider, required action)* for three surfaces — person card, dashboard,
   reports. `person_detail`/`dashboard`/`reports` views render registered panels;
   templates `{% include %}` them. The intake-form blacklist-ID field becomes a
   registered **form extension** (field set + post-save handler) contributed by
   the blacklist feature — same pattern, one registry module.
4. **Seed untangling.** `seed_people` keeps people/projects only; equipment,
   accommodation, finance rows move to per-feature seeds; `seed_demo_scenario`
   already orchestrates cross-feature and simply calls them in order.

Also in B1: `person_history` reads registry-contributed history providers instead
of importing feature models; CSV exports split so each feature ships its own
(`export.approved` gate stays core).

**Done when:** the B0 dep-check passes (feature → core only); full suite green
with **unchanged assertions**; e2e unchanged.

### B2 · Repo reshape (git mv, no logic changes)

- `git mv` per the matrix: `apps/{accounts,audit,people,projects*,core-shell}` →
  `core/…`; the nine feature apps → `features/…`; `apps/projects` splits into
  `core/organizations`+`core/assignments` and `features/recruitment_trials`.
- **Migration safety (the one sharp edge):** pin every moved app's
  `AppConfig.label` to its historical label (`people`, `projects`, `logistics`,
  …) so `django_migrations`, FK references, and `db_table` names are untouched —
  **no data migration, no table renames**. The `projects` split keeps both new
  apps under labels that preserve existing migration history (`projects` label
  stays with organizations+assignments; trials models keep their tables via
  explicit `db_table` + a squashed migration note).
  Verify against a dump of the demo DB: `migrate --check` reports no changes.
- Settings become layered: `config/settings/base.py` (platform) +
  `clients/jober/settings.py` (INSTALLED_APPS from flags, locale set, branding
  constants); `DJANGO_SETTINGS_MODULE` selects the client at startup (§12.4).
- Update lint/test paths, Dockerfiles' COPY lists, i18n `LOCALE_PATHS`.

**Done when:** suite green; `migrate --check` clean against a pre-reshape DB dump;
production image builds; e2e green (URLs unchanged).

### B3 · Client layer — `clients/jober/`

- Move the policy *data* behind the B0 interfaces: `Role` enum + `ACTION_ROLES`,
  `ALLOWED_TRANSITIONS` values, `can_view_sensitive` rules, inactive-reason +
  finance-category + blacklist-category seed values, Slovak URL slugs.
- Core ships neutral defaults (a minimal role set + permissive-but-safe policy)
  so `core/` boots without any client.
- Branding: base-template logo/name blocks + CSS tokens overridable from
  `clients/jober/{templates,static}`; demo assets (`seed_demo_scenario`,
  demo runbook) move under the client.

**Done when:** Jober runs entirely as `clients.jober.settings`; suite green;
a `clients/_smoke/` synthetic client (core defaults, all flags off) boots and
passes core-only tests.

### B4 · Core additions CorvinumEU requires (each a reusable capability)

- **2FA** in `core/accounts` (TOTP, per-role enforcement flag) — required by
  CorvinumEU §5.12, useful to Jober.
- **`core/retention`** — generalize the `purge_feedback`/`purge_blacklist`
  pattern into a `RetentionPolicy` registry (per-record-type days + action).
- **`core/tasks`** (only if Stage C confirms need) — internal task/notification
  model per CorvinumEU §6; defer if the CorvinumEU build can start without it.

**Done when:** each addition lands with tests, flags off changes nothing for
Jober, suite green.

### B5 · Validate + declare Stage B done

- Full suite under Jober flags (assertions unchanged from B0 baseline).
- Dep-direction check green in CI; grep proves no `if client == …` in `core/`.
- `clients/_smoke` all-off boot test green.
- Update ADR 0021 Status → Accepted-and-executed note; refresh the platform docs.
- **Exit artifact:** Stage C (CorvinumEU thin client) can start from
  `clients/corvinum_eu/` + `features/{documents,checklists,advances}` per the
  design doc — a config + theme + feature exercise, not a rebuild. (Plus, if
  confirmed, the small `features/fuel_costs` bus-fuel log — see design-doc
  Addendum A1; private-car fuel money is already inside `features/advances`.)

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Migration/table breakage during the reshape | `AppConfig.label` pinning + `db_table` preservation; `migrate --check` against a real dump is a B2 gate; no schema changes allowed in B2 |
| Hidden coupling beyond the three known sites | B0 dep-check script is the tripwire; B1 isn't done until it passes |
| i18n catalog split loses translations | msgids move with their apps; `compile_messages.sh --extract` diff reviewed per slice; catalogs are append-only during Stage B |
| e2e instability from URL/template moves | URLs are frozen during Stage B (client URL config lands in B3 without changing paths); e2e suite runs per slice |
| Estimate creep in B1 | The four designs above are fixed-scope; anything discovered beyond them becomes an explicit new slice, not silent scope growth |
| Supply-chain rules (AGENTS.md) | No new runtime deps anywhere in Stage B; registries/hooks are stdlib + Django only |

## Definition of done (whole stage)

Stage D bar restated: core contains no client conditionals; every core change is
reusable; Jober's tests pass **unchanged**; both flag sets (Jober, smoke-off)
green; a third client would be config + branding + optional features.
