# ADR 0022: Stage C — CorvinumEU as the first thin client

Status: **Accepted — activated 2026-07-11 (owner green-light)**
Date drafted: 2026-07-11

Executes Stage C of the platform roadmap (design doc §12.5; sequencing per
[ADR 0020](0020-white-label-platform-sequencing.md)) on the core extracted in
Stage B ([ADR 0021](0021-stage-b-extraction.md), executed 2026-07-09).

## Decision

Build **CorvinumEU PeopleOps** as `clients/corvinum_eu/` — settings, policies,
theme, seeds — plus the CorvinumEU-required feature apps, on the unchanged
Stage B core. One PR per slice, full suite green per slice, and the Stage D
bar continues to govern: **no client conditionals in core; every core change
reusable; Jober's tests pass with assertions unchanged**.

### Scope mapping (design doc → repo)

| Design doc capability | Where it lands |
|---|---|
| Client layer (§12.4) | `clients/corvinum_eu/{settings,policies}.py` — flags, SK/HU languages, branding, 2FA-required roles |
| Equipment & issued items (§5.8) | **Reuse `features/logistics`** behind its existing `equipment` sub-flag (`accommodation`/`transport` off) — issue/return/flag/deduction-review is already built |
| Duplicate/blacklist (§5.6) | **Reuse `features/blacklist`** (HMAC matching, propose/decide queue) |
| Documents w/ expiry (§5.4) | **Reuse `features/compliance`** (metadata + expiry alerts); file upload/verification workflow is a later slice extension, flag-gated |
| Approval checklists (§5.5) | **New `features/checklists`** — hooks into `core/projects` activation checks |
| Advance & deduction ledger (§5.10) | **New `features/advances`** — explicit-field model (positive amounts, `entry_type`/`pay_effect`/`settlement_status`), Thursday summary, 20th-to-20th cycle |
| 2FA (§5.12) | Already core (Stage B4b); CorvinumEU turns it on via `TWO_FACTOR_REQUIRED_ROLES` |
| Retention/GDPR (§5.12) | Already core (`core/retention`) |

### Deviations / deferrals recorded at activation

- **`features/fuel_costs` (Addendum A1.2) is NOT built** — the request is
  secondhand and the addendum itself says "pending confirmation… do not treat
  as decided". Private-car fuel money needs no new module (it is a ledger
  `PAY_ADDITION`, category `travel_fuel`).
- **Deployment (staging/production) is deferred** — no server/domain/DB names
  exist for CorvinumEU; Stage C ends at "runs locally under
  `clients.corvinum_eu.settings` with seeds and green suites".
- **Roles**: CorvinumEU's "HR Admin" maps to the core `manager` role for MVP
  (the core role set is reused; a distinct role would be a core change and is
  not yet justified). Recorded for client confirmation.
- **Unconfirmed client decisions** (status lifecycle, mandatory documents,
  exact ledger rules, default language) are built to the design doc's own
  proposed defaults, on **fictional data only**, and tracked in
  [docs/product/corvinum-open-questions.md](../product/corvinum-open-questions.md)
  — the same discipline used for Jober's five open questions.
- The physical logistics split (accommodation/equipment/transport as separate
  apps) remains deferred: sub-flags already give CorvinumEU equipment-only
  mounting, so the label surgery stays unjustified.

## Consequences

- The suite must stay green under **three** settings modules: `clients.jober`
  (all-on), `clients.corvinum_eu` (CorvinumEU set), `clients._smoke` (all-off).
- New actions (checklists, ledger) join the core `Action` enum with per-client
  grants in each client's policies; Jober's grants are untouched (features off).
- Supply-chain rules unchanged: **no new runtime dependencies** anywhere in
  Stage C; the theme is client-local CSS/templates (npm-free, no CDN assets).
- The peopleops prototype (`corvinumeu` repo, Addendum A2) is the visual
  reference for the theme slice; production markup stays server-rendered
  Django/htmx.
