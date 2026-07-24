# ADR 0026: Office-scoped RBAC for Jober's multi-office operation

Status: **Partially Accepted — Phase A EXECUTED 2026-07-24.** The
Activation trigger below was satisfied for the finance-relevant slice of
this decision (Jober confirmed office names and requested the full
platform change); Phase B (below) remains pending, unbuilt.

Date drafted: 2026-07-24

## Execution note (Phase A, 2026-07-24)

Built now: the real `Office` model (`core/offices/` — client-agnostic
mechanism, installed by every client the same way `core.people` is, but
deliberately *empty* by default; the three real offices are seeded only
by Jober's own `seed_people.py`, not a `core/offices` migration, so
CorvinumEU's database never receives Jober's office names just because it
shares the app), `Project.office` as a real FK replacing the free-text
field, `User.offices` M2M (decision point 2's User half), the shared
`user_office_scope()` helper
(`core/accounts/permissions.py`, decision point 4's mechanism — returns
`None` for Observer as a genuine "unrestricted" sentinel, not an
all-offices queryset, since the latter would incorrectly exclude any
record with no office assigned), full office-scoping of every finance
service function and view (`features/finance/`), and a new executive
finance dashboard (`templates/pages/finance_executive.html`) that only
Observer sees — same `finance_summary` URL, role-branched content, per the
product decision recorded in `docs/product/jober-multi-office-scoping.md`.
A 403 guard prevents a non-Observer from viewing or mutating another
office's financial month by guessing a URL or crafting a POST.

**Not built (Phase B, still pending, unaffected by this execution):**
`Person.office`, `Accommodation.office`, splitting the pooled equipment
stock ledger (decision point 2's remaining scope), the office-principal/
staff-invitation subsystem (points 4a/4b), and rewriting the ~13 ad hoc
RBAC call sites outside finance (compliance, checklists, notifications,
projects, logistics, CSV export, reports tiles — point 4's remaining
scope). Blacklist (point 3) and the office-creation ceiling (point 7)
were always meant to be architectural invariants rather than code to
build, and remain exactly as designed.

**Revision (2026-07-24, same day, pre-activation):** the original draft
decided staff belong to exactly one office (single FK on `User`). That is
reversed below — staff can work at multiple offices, and a new
office-principal/staff-invitation subsystem is added (decision points 2,
4a, 4b). Since this ADR was never activated, this is an in-place
amendment, not a superseding ADR.

Amends [ADR 0008](0008-broad-read-action-gated-rbac.md); does not replace
it. Full impact analysis: `docs/product/jober-multi-office-scoping.md`.

## Context

Jober now operates three physical offices instead of one: Velký Meder
(SK), Győr (HU), and Dunajská Streda (SK). Recruiter, coordinator, and
manager staff must only see their own office's data; the observer role
(company owner/CEO) must continue to see everything across all offices.

ADR 0008 established Jober's RBAC model: "broad internal read visibility
with role-gated actions... no arbitrary per-user permission matrix is
introduced in MVP." That default assumed a single tenant. Office-scoping
adds a second, orthogonal visibility dimension — tenancy by office — on
top of role. It does not replace role-gating; it narrows the "broad
internal read" default for three of the four roles, while observer keeps
exactly the visibility ADR 0008 already granted.

The design doc found the codebase already partially anticipates this:
`Project` carries free-text `office`/`region` fields today (unused for
filtering), while `User` and `Person` have no location concept at all, and
existing coordinator/recruiter scoping is ~13 separate ad hoc queryset
filters rather than a systemic mechanism — including one pre-existing gap
(the CSV export has no recruiter/coordinator scoping today, independent of
this change).

## Decision (on activation)

1. Introduce a real `Office` model (`core/offices/`), seeded with Velký
   Meder, Győr, and Dunajská Streda. Nullable/optional everywhere it's
   referenced, so CorvinumEU (single-site) is unaffected.
2. Add an **`offices` many-to-many** (not a single FK) to `User`, plus an
   `office` FK to `Person` (explicit, set at intake — independent of
   project assignment), `Project` (replacing the existing free-text
   field), `Accommodation`, and the equipment stock ledger
   (`EquipmentStockLot`/`Allocation`). A staff member can work at more
   than one office.
3. Blacklist matching and visibility stay company-wide — explicitly
   **not** office-scoped, preserving the existing documented invariant
   (`features/blacklist/models.py`, `docs/security/jober-blacklist-legal-basis.md`).
4. Replace the ~13 scattered ad hoc coordinator/recruiter filters with one
   shared office-scoping helper in `core/accounts/permissions.py`
   (membership-in-set, not equality, given point 2), applied consistently,
   and use the same pass to close the CSV export's pre-existing scoping
   gap.
4a. **`Office.principals`** (M2M to `User`, mirroring `Project.
   responsible_coordinators`) grants specific Manager-role users elevated
   staffing authority over a specific office. Invite authority is tiered
   by the role being invited, not just the inviter's role: Observer can
   invite Manager/Recruiter/Coordinator anywhere; a principal of office X
   can invite Manager/Recruiter/Coordinator for X; a regular (non-
   principal) manager who is a member of office X can invite only
   Recruiter/Coordinator for X, never Manager. Full detail (two separate
   `Action`s, the `StaffInvitation` model, views, audit events):
   `docs/product/jober-multi-office-scoping.md` §3a.
4b. **Principal promotion/appointment is Observer-exclusive** — a
   separate action from ordinary staff invitation. Only Observer can add
   a Manager to `Office.principals` or appoint the first principal for an
   office that has none; existing principals cannot create fellow
   principals.
5. Observer bypasses office-scoping by role for reads, and separately
   holds full principal authority everywhere (invite any role, appoint/
   promote principals, assign office membership) — the only role that can
   create principals at all.
6. Cross-office equipment transfer is explicitly out of scope for the
   first slice — offices get independent stock ledgers; whether stock
   ever moves between them is a separate, later decision.
7. **Office creation is permanently outside the product's RBAC surface.**
   Jober licensed exactly 3 offices from SyncMetric s.r.o.; no `Action`,
   view, or route lets any Jober role — including Observer — create a 4th.
   Additional offices are a commercial request to SyncMetric, not a
   feature.

Full field-by-field and file-by-file detail lives in
`docs/product/jober-multi-office-scoping.md` — this ADR records the
decision and its trigger, not the implementation plan.

## Activation trigger

**Phase A — satisfied 2026-07-24**: Jober confirmed the exact office
names/diacritics (Velký Meder/VM/SK, Győr/GYR/HU, Dunajská Streda/DS/SK),
seeded via `clients/jober/demo/management/commands/seed_people.py` (Jober-
only — deliberately **not** a `core/offices` migration, since that app is
installed by every client and a migration has no per-client conditional;
seeding Jober's specific office names there would leak them into
CorvinumEU's database too), and explicitly requested the full platform
change be built rather than deferred.

**Still open, blocks Phase B's equipment-stock split specifically**:
whether the three offices share equipment stock or keep fully independent
warehouses (informs whether transfer flows are needed once that slice is
built) — not required for anything executed in Phase A.

## Consequences

- `Person`/`User`/`Project` gain a schema dimension that didn't exist
  before; existing demo seed data (3 projects, 7 people) is small enough
  to reseed cheaply.
- Every report, export, and notification query that currently returns
  company-wide or role-scoped results must be re-audited against the new
  office dimension — the design doc enumerates the known call sites, but
  this ADR's acceptance test is that no non-observer role can read another
  office's `Person`, `Project`, `Accommodation`, or equipment-stock data
  through any existing view, including exports.
- Blacklist remains the one deliberate exception: a candidate flagged at
  one office must still be caught at all three.
- ADR 0008 is not superseded outright — its role-gating decision stands;
  this ADR narrows its "broad internal read" consequence for Jober only.
- This introduces the app's **first-ever** user invitation/authentication-
  adjacent flow — the acceptance bar now also includes "no staff account
  can be created except via seed bootstrap or a valid, unexpired,
  single-use invitation token," and "no in-app path exists anywhere to
  create a 4th `Office` row."
