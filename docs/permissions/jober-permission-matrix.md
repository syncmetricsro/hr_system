# Permission Matrix — Jober

Last updated: 2026-07-18

This document is the human-readable mirror of `clients/jober/policies.py`
(`ACTION_ROLES`; the `Action` enum lives in `core/accounts/permissions.py`). When you change one, change the other in the same commit.

## Model

- **Four fixed roles**, no per-user permission matrices (plan §8, ADR 0008).
- **Reads are broad** by default: any authenticated internal role may read
  ordinary operational records. Offices are filters, not access boundaries.
  This is governed by the single switch `BROAD_INTERNAL_READS`
  (env `JOBER_BROAD_INTERNAL_READS`, default on) so the still-open GDPR
  recruiter/coordinator read-scope decision can be narrowed later without a
  hardcoded split (`docs/product/jober-open-decisions.md`).
- **Roles restrict actions** (writes) and **sensitive reads**. Those are the
  rows below. A superuser passes every check.
- Every gated view uses `require_action(...)`; every gated button uses the
  `{% can %}` template tag. A hidden button must be backed by a server check.

Legend: ✅ permitted · — denied

## Actions

| Action | Recruiter | Coordinator | Manager/Admin | Observer |
|---|---|---|---|---|
| `intake.create_edit` | ✅ | — | ✅ | — |
| `intake.assign_trial` | ✅ | ✅ | ✅ | — |
| `person.recycle_available` | ✅ | ✅ | ✅ | — |
| `person.archive` | — | — | ✅ | — |
| `project.assign` (place/reassign a person on a project) | — | ✅ | ✅ | — |
| `sms.send` | ✅ | ✅ | ✅ | — |
| `trial.record_outcome` | — | ✅ | ✅ | — |
| `readiness.complete` | — | ✅ | ✅ | — |
| `room.assign` | — | ✅ | ✅ | — |
| `equipment.issue_return` | — | ✅ | ✅ | — |
| `transport.record` | — | ✅ | ✅ | — |
| `exit.reconcile` | — | ✅ | ✅ | — |
| `approval.activate` | — | — | ✅ | — |
| `project.manage` | — | — | ✅ | — |
| `accommodation.manage` | — | — | ✅ | — |
| `equipment.review_deduction` | — | — | ✅ | — |
| `catalog.manage` | — | — | ✅ | — |
| `user.manage` | — | — | ✅ | — |
| `blacklist.propose` | — | ✅ | ✅ | — |
| `blacklist.decide` | — | — | ✅ | — |
| `sms.manage_templates` | — | — | ✅ | — |
| `checklist.tick` (Jober: feature off — ADR 0022) | — | ✅ | ✅ | — |
| `ledger.enter` (Jober: feature off — ADR 0022) | — | — | ✅ | — |
| `ledger.view` (Jober: feature off — ADR 0022) | — | — | ✅ | ✅ |
| `wage.manage` (Jober: feature off) | — | — | ✅ | — |
| `wage.view` (Jober: feature off) | — | — | ✅ | ✅ |
| `payslip.manage` (Jober: feature off — ADR 0023) | — | — | ✅ | — |
| `payslip.view` (Jober: feature off — ADR 0023) | — | — | ✅ | ✅ |
| `finance.manage` | — | — | ✅ | — |
| `export.approved` | — | — | ✅ | ✅ |

## Sensitive fields / reads (carved out of broad-read default)

| Sensitive read | Recruiter | Coordinator | Manager/Admin | Observer |
|---|---|---|---|---|
| `blacklist.view_reason` (reasons; warning *existence* stays broad) | — | ✅ | ✅ | — |
| `feedback.view` (worker feedback inbox) | — | — | ✅ | — |
| `finance.view_summary` | — | — | ✅ | ✅ |
| `audit.view` | — | — | ✅ | ✅ |

## Person sensitive fields (per-object rule)

DOB, place of birth, disability flag/type, and identifiers are **not** a flat
role grant — visibility depends on the viewer's relationship to that person
(phase1-open-questions Q4). Implemented as `apps.people.permissions.can_view_sensitive`:
visible to **managers, observers, the owning recruiter, and the person's
responsible coordinator(s)**; hidden from unconnected recruiters/coordinators.

## Notes per role

- **Recruiter** — owns intake while it is theirs; routes candidates to trial
  days; recycles Available people; sends approved SMS; sees that a blacklist
  warning exists but not the restricted reason. Cannot record trial outcomes,
  complete readiness, approve Working, or manage projects/catalogs/users/finance.
- **Coordinator** — schedules and records project trials, then handles
  readiness data, rooms, equipment, transport headcounts, and exit
  reconciliation; sends approved SMS.
  Coordinators may assign existing rooms but cannot create or edit accommodation
  locations or room catalogue records.
  Cannot approve Working, manage users, decide blacklist, or view feedback.
- **Manager/Administrator** — all permitted reads plus every management action,
  including finance, users, blacklist decisions, audit, and exports.
  Accommodation management includes creating, editing, and deactivating
  locations and rooms; occupied catalogue records cannot be deactivated.
- **Observer** — read-only: approved dashboards/lists, approved financial
  summaries, exports only where explicitly allowed. No operational/financial
  writes.

## Scope of this slice (Phase 1 foundation)

The mechanics (roles, `can()`, `require_action`, `{% can %}`, audit) are wired
now. Most action rows do not yet have a backing business view — those land as
each module is built in later Phase 1/2 work. The matrix is authored ahead so
new views adopt the correct gate from day one.
