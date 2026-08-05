# Permission Matrix — CorvinumEU

Last updated: 2026-08-02

Human-readable mirror of `clients/corvinum_eu/policies.py` (`ACTION_ROLES`).
When you change one, change the other in the same commit. The mechanism
(`Action`, `can()`, `require_action`) is shared core; only the grants are
client policy. **Any core action not listed here is denied for every
CorvinumEU role** (deny-by-default lookup) — that covers the Jober-only
features CorvinumEU never mounts (SMS, accommodation, transport, finance P&L,
feedback).

Roles: the core four; CorvinumEU's "HR Admin" maps to **Manager/Admin**
(C-Q9, ADR 0022). Reads are broad per ADR 0008; superusers pass every check. ADR 0026 adds office scoping platform-wide, but it is a **no-op here**: CorvinumEU is single-site and never creates `Office` rows, so `user_office_scope` returns its unrestricted sentinel and no queryset is narrowed.
2FA (TOTP) is **required for managers in staging and production**
(`TWO_FACTOR_AUTH_ENABLED` plus `TWO_FACTOR_REQUIRED_ROLES`). The fictional-data
runner on `localhost:8001` is the deliberate development exception and uses
password-only login through `clients.corvinum_eu.local`.

Legend: ✅ permitted · — denied

## Actions

| Action | Recruiter | Coordinator | Manager/Admin (HR Admin) | Observer |
|---|---|---|---|---|
| `intake.create_edit` | ✅ | — | ✅ | — |
| `intake.assign_trial` | ✅ | ✅ | ✅ | — |
| `person.recycle_available` | ✅ | ✅ | ✅ | — |
| `certificate.manage` (create/edit/renew/archive an allowlisted occupational certificate) | ✅ | ✅ | ✅ | — |
| `certificate.purge_file` (emergency permanent file removal, reason required) | — | — | ✅ | — |
| `person.archive` | — | — | ✅ | — |
| `project.assign` | — | ✅ | ✅ | — |
| `trial.record_outcome` | — | ✅ | ✅ | — |
| `readiness.complete` | — | ✅ | ✅ | — |
| `approval.activate` (decide a pending activation request) | — | — | ✅ | — |
| `activation.waive_trial` (open readiness without a trial day) | — | — | ✅ | — |
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
| `audit.view` (Observer only from 2026-08-04) | — | — | — | ✅ |
| `staff_activity.view` (Observer only from 2026-08-04) | — | — | — | ✅ |
| `offer_email.send` / `offer.manage` / `offer_template.manage` / `offer_email.bulk_send` (worker messaging not in this product) | — | — | — | — |

> **No worker messaging (ADR 0029, peopleops design §15.9).** Neither SMS nor
> job-offer emails exist here: worker contact is phone + Messenger. The four
> `offer*` actions are absent from `clients/corvinum_eu/policies.py` (a missing
> key is deny), the `offer_emails` flag is `False`, and `features.messaging` is
> not in `INSTALLED_APPS` — so the routes do not exist either. This is a data
> and configuration difference, not a client branch in core.

> **Activation needs a manager here too (since 2026-07-27).** The activation
> route is shared core code, so CorvinumEU gets the same control as Jober: a
> coordinator completes readiness and *requests* activation, and a manager
> decides from the Activations queue. **This removed a capability CorvinumEU
> coordinators previously had** — they could activate directly, contrary to
> this matrix. A manager cannot decide their own request either.

## Lifecycle transitions (trial-day workflow enabled for demo, C-Q1)

Available → Trial day → Working / Available / Inactive / Blacklisted ·
Available/Working → Inactive · any → Blacklisted (via decided case) ·
Blacklisted → Available (manager removal). Recruiters, coordinators, and
managers may schedule trials; coordinators and managers may record outcomes.
