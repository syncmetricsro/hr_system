# Permission Matrix — CorvinumEU

Last updated: 2026-07-11

Human-readable mirror of `clients/corvinum_eu/policies.py` (`ACTION_ROLES`).
When you change one, change the other in the same commit. The mechanism
(`Action`, `can()`, `require_action`) is shared core; only the grants are
client policy. **Any core action not listed here is denied for every
CorvinumEU role** (deny-by-default lookup) — that covers the Jober-only
features CorvinumEU never mounts (trials, SMS, accommodation, transport,
finance P&L, feedback).

Roles: the core four; CorvinumEU's "HR Admin" maps to **Manager/Admin**
(C-Q9, ADR 0022). Reads are broad per ADR 0008; superusers pass every check.
2FA (TOTP) is **required for managers** (`TWO_FACTOR_REQUIRED_ROLES`).

Legend: ✅ permitted · — denied

## Actions

| Action | Recruiter | Coordinator | Manager/Admin (HR Admin) | Observer |
|---|---|---|---|---|
| `intake.create_edit` | ✅ | — | ✅ | — |
| `person.recycle_available` | ✅ | ✅ | ✅ | — |
| `project.assign` | — | ✅ | ✅ | — |
| `readiness.complete` | — | ✅ | ✅ | — |
| `approval.activate` | — | — | ✅ | — |
| `project.manage` | — | — | ✅ | — |
| `exit.reconcile` | — | ✅ | ✅ | — |
| `equipment.issue_return` | — | ✅ | ✅ | — |
| `equipment.review_deduction` | — | — | ✅ | — |
| `checklist.tick` | — | ✅ | ✅ | — |
| `ledger.enter` | — | — | ✅ | — |
| `ledger.view` | — | — | ✅ | ✅ |
| `payslip.manage` | — | — | ✅ | — |
| `blacklist.propose` | — | ✅ | ✅ | — |
| `blacklist.decide` | — | — | ✅ | — |
| `blacklist.view_reason` | — | — | ✅ | — |
| `catalog.manage` | — | — | ✅ | — |
| `user.manage` | — | — | ✅ | — |
| `export.approved` | — | — | ✅ | ✅ |
| `audit.view` | — | — | ✅ | ✅ |

## Lifecycle transitions (trial-less, C-Q1 default)

Available ⇄ Working · Available/Working → Inactive · any → Blacklisted
(via decided case) · Blacklisted → Available (manager removal). No
`TRIAL_DAY` state — `recruitment_trials` is off for this client.
