# Permission Matrix — CorvinumEU

Last updated: 2026-07-18

Human-readable mirror of `clients/corvinum_eu/policies.py` (`ACTION_ROLES`).
When you change one, change the other in the same commit. The mechanism
(`Action`, `can()`, `require_action`) is shared core; only the grants are
client policy. **Any core action not listed here is denied for every
CorvinumEU role** (deny-by-default lookup) — that covers the Jober-only
features CorvinumEU never mounts (SMS, accommodation, transport, finance P&L,
feedback).

Roles: the core four; CorvinumEU's "HR Admin" maps to **Manager/Admin**
(C-Q9, ADR 0022). Reads are broad per ADR 0008; superusers pass every check.
2FA (TOTP) is **required for managers** (`TWO_FACTOR_REQUIRED_ROLES`).

Legend: ✅ permitted · — denied

## Actions

| Action | Recruiter | Coordinator | Manager/Admin (HR Admin) | Observer |
|---|---|---|---|---|
| `intake.create_edit` | ✅ | — | ✅ | — |
| `intake.assign_trial` | ✅ | ✅ | ✅ | — |
| `person.recycle_available` | ✅ | ✅ | ✅ | — |
| `person.archive` | — | — | ✅ | — |
| `project.assign` | — | ✅ | ✅ | — |
| `trial.record_outcome` | — | ✅ | ✅ | — |
| `readiness.complete` | — | ✅ | ✅ | — |
| `approval.activate` | — | — | ✅ | — |
| `project.manage` | — | — | ✅ | — |
| `exit.reconcile` | — | ✅ | ✅ | — |
| `equipment.issue_return` | — | ✅ | ✅ | — |
| `equipment.review_deduction` | — | — | ✅ | — |
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

## Lifecycle transitions (trial-day workflow enabled for demo, C-Q1)

Available → Trial day → Working / Available / Inactive / Blacklisted ·
Available/Working → Inactive · any → Blacklisted (via decided case) ·
Blacklisted → Available (manager removal). Recruiters, coordinators, and
managers may schedule trials; coordinators and managers may record outcomes.
