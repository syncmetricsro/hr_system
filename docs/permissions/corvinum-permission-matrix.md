# Permission Matrix — CorvinumEU

Last updated: 2026-07-20

Human-readable mirror of `clients/corvinum_eu/policies.py` (`ACTION_ROLES`).
When you change one, change the other in the same commit. The mechanism
(`Action`, `can()`, `require_action`) is shared core; only the grants are
client policy. **Any core action not listed here is denied for every
CorvinumEU role** (deny-by-default lookup) — that covers the Jober-only
features CorvinumEU never mounts (SMS, accommodation, transport, finance P&L,
feedback).

Roles: the core four; CorvinumEU's "HR Admin" maps to **Manager/Admin**
(C-Q9, ADR 0022). Reads are broad per ADR 0008; superusers pass every check. ADR 0026 adds office scoping platform-wide, but it is a **no-op here**: CorvinumEU is single-site and never creates `Office` rows, so `user_office_scope` returns its unrestricted sentinel and no queryset is narrowed.
2FA (TOTP) is **required for managers** (`TWO_FACTOR_REQUIRED_ROLES`).

Legend: ✅ permitted · — denied

## Actions

| Action | Recruiter | Coordinator | Manager/Admin (HR Admin) | Observer |
|---|---|---|---|---|
| `intake.create_edit` | ✅ | — | ✅ | — |
| `intake.assign_trial` | ✅ | ✅ | ✅ | — |
| `person.recycle_available` | ✅ | ✅ | ✅ | — |
| `certificate.manage` (create/replace/delete a certificate document) | ✅ | ✅ | ✅ | — |
| `person.archive` | — | — | ✅ | — |
| `project.assign` | — | ✅ | ✅ | — |
| `trial.record_outcome` | — | ✅ | ✅ | — |
| `readiness.complete` | — | ✅ | ✅ | — |
| `approval.activate` (**not enforced** — see note below) | — | — | ✅ | — |
| `project.manage` | — | — | ✅ | — |
| `exit.reconcile` | — | ✅ | ✅ | — |
| `equipment.issue_return` | — | ✅ | ✅ | — |
| `equipment.review_deduction` | — | — | ✅ | — |
| `equipment.view_stock` (Jober-only warehouse policy) | — | — | — | — |
| `equipment.manage_stock` (Jober-only warehouse policy) | — | — | — | — |
| `catalog.manage` (equipment catalogue) | — | — | ✅ | — |
| `checklist.tick` | — | ✅ | ✅ | — |
| `ledger.enter` | — | — | ✅ | — |
| `ledger.view` | — | — | ✅ | ✅ |
| `wage.manage` | — | — | ✅ | — |
| `wage.view` | — | — | ✅ | ✅ |
| `payslip.manage` | — | — | ✅ | — |
| `payslip.view` | — | — | ✅ | ✅ |
| `blacklist.propose` | — | ✅ | ✅ | — |
| `blacklist.decide` | — | — | ✅ | — |
| `blacklist.view_reason` | — | — | ✅ | — |
| `catalog.manage` | — | — | ✅ | — |
| `user.manage` | — | — | ✅ | — |
| `export.approved` | — | — | ✅ | ✅ |
| `audit.view` | — | — | ✅ | ✅ |

> **`approval.activate` is not enforced here either (2026-07-27).** The
> activation route is shared core code (`core/projects/views.py::activate_person`)
> and is gated by `project.assign`, which coordinators hold; the Activate button
> sits behind `readiness.complete`, also a coordinator action. CorvinumEU grants
> the same three actions as Jober, so a CorvinumEU coordinator can approve
> Working exactly as a Jober one can. Tracked as Jober production-readiness
> item 14 — the fix is in shared code and lands for both clients at once.

## Lifecycle transitions (trial-day workflow enabled for demo, C-Q1)

Available → Trial day → Working / Available / Inactive / Blacklisted ·
Available/Working → Inactive · any → Blacklisted (via decided case) ·
Blacklisted → Available (manager removal). Recruiters, coordinators, and
managers may schedule trials; coordinators and managers may record outcomes.
