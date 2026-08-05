# Permission Matrix — Jober

Last updated: 2026-08-02

This document is the human-readable mirror of `clients/jober/policies.py`
(`ACTION_ROLES`; the `Action` enum lives in `core/accounts/permissions.py`). When you change one, change the other in the same commit.

## Model

- **Four fixed roles**, no per-user permission matrices (plan §8, ADR 0008).
- **Reads are broad within a user's office scope.** Any authenticated
  internal role may read ordinary operational records belonging to the
  office(s) they're a member of (`User.offices`); Observer bypasses office
  scoping entirely and sees every office. This is a real access boundary
  for non-Observer roles as of ADR 0026 (`core/accounts/permissions.py::
  user_office_scope`) — not just a display filter — with a hard 403 on
  direct access to another office's record (e.g. Finance, People, Projects
  detail views). The broad-within-scope *role* default (any role can read
  any record type, subject to the office boundary above) is governed by
  the single switch `BROAD_INTERNAL_READS` (env
  `JOBER_BROAD_INTERNAL_READS`, default on) so the still-open GDPR
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
| `certificate.manage` (create/edit/renew/archive an allowlisted occupational certificate) | ✅ | ✅ | ✅ | — |
| `certificate.purge_file` (emergency permanent file removal, reason required) | — | — | ✅ | — |
| `person.archive` | — | — | ✅ | — |
| `project.assign` (place/reassign a person on a project) | — | ✅ | ✅ | — |
| `sms.send` | ✅ | ✅ | ✅ | — |
| `offer_email.send` (email one worker a job offer; coordinator-scoped like `sms.send`) | ✅ | ✅ | ✅ | — |
| `trial.record_outcome` | — | ✅ | ✅ | — |
| `readiness.complete` | — | ✅ | ✅ | — |
| `room.assign` | — | ✅ | ✅ | — |
| `equipment.issue_return` | — | ✅ | ✅ | — |
| `equipment.view_stock` | — | — | ✅ | ✅ |
| `equipment.manage_stock` | — | — | ✅ | — |
| `transport.record` (Jober: feature off) | — | ✅ | ✅ | — |
| `exit.reconcile` | — | ✅ | ✅ | — |
| `approval.activate` (decide a pending activation request) | — | — | ✅ | — |
| `activation.waive_trial` (open readiness without a trial day) | — | — | ✅ | — |
| `project.manage` | — | — | ✅ | — |
| `accommodation.manage` | — | — | ✅ | — |
| `equipment.review_deduction` | — | — | ✅ | — |
| `catalog.manage` | — | — | ✅ | — |
| `user.manage` (**not enforced** — granted but no view implements it) | — | — | ✅ | — |
| `blacklist.propose` | — | ✅ | ✅ | — |
| `blacklist.decide` | — | — | ✅ | — |
| `sms.manage_templates` (**not enforced** — admin-only in practice) | — | — | ✅ | — |
| `offer.manage` (author/edit/close job offers — ADR 0029) | — | — | ✅ | — |
| `offer_template.manage` (per-language offer email bodies — ADR 0029) | — | — | ✅ | — |
| `offer_email.bulk_send` (email an offer to a filtered list; capped + confirmed) | — | — | ✅ | — |
| `checklist.tick` (Jober: feature off — ADR 0022) | — | ✅ | ✅ | — |
| `ledger.enter` (Jober: feature off — ADR 0022) | — | — | ✅ | — |
| `ledger.view` (Jober: feature off — ADR 0022) | — | — | ✅ | ✅ |
| `wage.manage` (Jober: feature off) | — | — | ✅ | — |
| `wage.view` (Jober: feature off) | — | — | ✅ | ✅ |
| `payslip.manage` (Jober: feature off — ADR 0023) | — | — | ✅ | — |
| `payslip.view` (Jober: feature off — ADR 0023) | — | — | ✅ | ✅ |
| `finance.manage` | — | — | ✅ | — |
| ↳ covers the project–year grid save (`finance_project_year_save`, 2026-08-05) — same action, one more route | — | — | ✅ | — |
| `export.approved` | — | — | ✅ | ✅ |

## Sensitive fields / reads (carved out of broad-read default)

| Sensitive read | Recruiter | Coordinator | Manager/Admin | Observer |
|---|---|---|---|---|
| `blacklist.view_reason` (reasons; warning *existence* stays broad) | — | ✅ | ✅ | — |
| `feedback.view` (worker feedback inbox) | — | — | ✅ | — |
| `finance.view_summary` | — | — | ✅ | ✅ |
| `audit.view` | — | — | ✅ | ✅ |
| `staff_activity.view` | — | — | ✅ | ✅ |

## Person sensitive fields (per-object rule)

DOB, place of birth, disability flag/type, and identifiers are **not** a flat
role grant — visibility depends on the viewer's relationship to that person
(phase1-open-questions Q4). Implemented as
`core.people.permissions.can_view_sensitive`: visible to **managers,
observers, the owning recruiter, and the person's responsible
coordinator(s)**; hidden from unconnected recruiters/coordinators.

This sits *inside* the office boundary: a manager cannot see another office's
person at all, sensitive fields or otherwise. And a person with **no** office
is visible only to their owning recruiter (plus Observer) — see
`core/offices/scoping.py::may_see_person`.

## Notes per role

> Every role note below describes what that role may do **within its own
> office(s)** (ADR 0026). Office membership (`User.offices`) is the outer
> boundary; the role rules are what applies inside it. Observer is the only
> role that spans offices, by role bypass rather than membership. Blacklist is
> the deliberate exception: matching and visibility stay company-wide.

- **Recruiter** — office set at intake from their own membership when
  unambiguous; a person left without an office is visible to that recruiter
  and nobody else (`core/offices/scoping.py`). Owns intake while it is theirs;
  routes candidates to trial days; recycles Available people; sends approved
  SMS and emails job offers to one worker at a time; sees that a blacklist
  warning exists but not the restricted reason. Cannot record trial outcomes,
  complete readiness, approve Working, or manage projects/catalogs/users/finance.
- **Coordinator** — schedules and records project trials, then handles
  readiness data, rooms, equipment issuance, and exit
  reconciliation; sends approved SMS and job-offer emails, both limited to
  people on their own projects.
  Coordinators may assign existing rooms but cannot create or edit accommodation
  locations or room catalogue records.
  Cannot manage users, decide blacklist, or view feedback.
  **Cannot approve Working** — a coordinator *requests* activation once
  readiness is complete and a manager of that office decides
  (`approval.activate`). Enforced since 2026-07-27; before then coordinators
  could activate directly, which is why this line carried a correction.
  A coordinator also cannot skip the trial day (`activation.waive_trial`).
- **Manager/Administrator** — within their office(s), all permitted reads plus
  every management action, including finance, users, blacklist decisions,
  audit, and exports. Authoring job offers and their email templates, and
  sending an offer to a filtered list, are manager-only (`offer.manage`,
  `offer_template.manage`, `offer_email.bulk_send`) — a bulk send reaches every
  worker matching a filter, so the blast radius earns the narrower grant. Not company-wide: another office's person, project,
  accommodation or financial month returns 403, and lists/aggregates/exports
  cover their own office only.
  Accommodation management includes creating, editing, and deactivating
  locations and rooms; occupied catalogue records cannot be deactivated.
- **Observer** — the only cross-office role: sees all three offices and lands
  on the Observer-only executive finance dashboard. Read-only: approved
  dashboards/lists, warehouse stock, approved financial summaries, exports
  only where explicitly allowed. No operational/financial writes, and
  **no messaging of any kind** — spanning every office is exactly what makes
  Observer the account that must not be able to email workers.

## Granted, but not enforced anywhere

**A row in the Actions table means "this role is permitted this action". It
does not mean the action is enforced somewhere.** **2 of the 38 actions have no
server-side enforcement at all** (was 4 until `approval.activate` was wired on
2026-07-27, and 3 until `project.manage` was wired on 2026-07-28), so granting or revoking them changes nothing today. They are marked **not enforced** in the tables above.
`activation.waive_trial` (added 2026-08-04) is enforced by
`readiness_waive_trial`, so it does not join that list.

Re-run the check before trusting any row (last done 2026-08-04). The criterion
is a reference from a view, panel or service — a `{% can %}` in a template only
hides a button and enforces nothing:

```bash
grep -rl "Action.<NAME>" --include=views.py --include=panels.py \
        --include=services.py core features
```

Zero hits means nothing enforces it. Both remaining ones are referenced
nowhere at all.

`project.manage` was on this list until 2026-07-28 and is now enforced by
`project_create` / `project_edit` / `project_set_active`. Worth recording what
the entry got wrong: it said the action "has a visible button and no
enforcement", but that button lives in `templates/pages/dashboard.html`, which
**no view renders** — so it was invisible rather than misleading, and the page
managers actually land on had no project entry point at all.

| Action | What actually happens today |
|---|---|
| `user.manage` | Nothing implements it — see below. Item 11. |
| `sms.manage_templates` | Nothing implements it. `MessageTemplate` is editable only in Django admin, which needs a superuser no Jober role holds, and none are seeded. Item 16. |

### User and credential management specifically

`user.manage` is granted to Manager but **nothing implements it**.
There is no route in the product that can create a user, change a password,
reset one, deactivate an account, or clear a lost 2FA enrolment; `core/
accounts/` has no `urls.py` or `forms.py`. Django admin is not a substitute
for a client, since it requires a superuser and no Jober role is one.

When it is built, the authority model is office-scoped like everything
else — designed in `docs/product/jober-multi-office-scoping.md` §3a
(invitation) and §3b (credential lifecycle):

| Actor | May act on accounts | Scope |
|---|---|---|
| Observer (CEO) | any account | **every office** |
| Principal Manager of office X | any account in X, incl. Managers | office X |
| Regular Manager, member of office X | Recruiter/Coordinator in X | office X |
| Recruiter / Coordinator | their own account | — |

**That gives Observer a write authority this matrix otherwise denies it.**
Observer is read-only over *operations* and authoritative over *staffing* —
the CEO hires and removes people but does not record trial outcomes. The
row above says "Observer: —" for `user.manage` because nothing is built;
whichever slice implements §3a/§3b must change that cell and keep this
explanation beside it, rather than leaving the matrix and the design docs
disagreeing.

## Scope of this slice (Phase 1 foundation)

The mechanics (roles, `can()`, `require_action`, `{% can %}`, audit) are wired
now. Most action rows do not yet have a backing business view — those land as
each module is built in later Phase 1/2 work. The matrix is authored ahead so
new views adopt the correct gate from day one.
