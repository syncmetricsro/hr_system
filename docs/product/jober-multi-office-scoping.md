# Multi-office scoping (Velký Meder, Győr, Dunajská Streda)

Status: **Implemented** — Phase A 2026-07-24, Phase B 2026-07-25. Office
scoping now covers People, Projects, Reports, exports, Compliance,
Checklists, Notifications, accommodation, transport, finance and the
equipment stock ledger (split into per-office warehouses), with hard 403s
on cross-office access and an office badge in the shell. See
`docs/adr/0026-office-scoped-rbac.md`'s two execution notes for exactly
what was built and for three decisions taken during implementation that
differ from the design below.

**Only §3a remains design-only**: the office-principal / staff-invitation
subsystem, deferred by the owner as separable from office scoping itself.

Jober-owned content (CorvinumEU is confirmed single-site and unaffected),
hence the `jober-` prefix per `docs/README.md`'s naming convention.

> **Reading note.** Everything from "Why this doc exists" to §4 was written
> *before* implementation and describes the pre-change codebase in the
> present tense ("Project already carries office and region fields",
> "equipment stock is currently one pooled ledger"). It is kept as the
> impact analysis it was, not rewritten into a description of today's
> system — but read those sections as history. Where the shipped design
> diverges from the sketch, the divergence is flagged inline.

## Why this doc exists

Jober now operates as three physical offices — Velký Meder (SK), Győr (HU),
Dunajská Streda (SK) — instead of one. Recruiter/coordinator/manager staff
must only see the data belonging to whichever office(s) they work at; the
observer role (company owner/CEO) must see everything across all three.

This is not a UI feature like the avatar/pill/certificate docs. It reopens
a documented architectural decision:

> `docs/adr/0008-broad-read-action-gated-rbac.md` — "Jober confirmed broad
> internal read visibility with role-gated actions... No arbitrary
> per-user permission matrix is introduced in MVP."

Office-scoping is a second, orthogonal visibility dimension (tenancy) on
top of role. **Implementation should begin with a real ADR** amending or
superseding ADR 0008's "broad internal read" default — this doc is the
impact analysis that ADR would be based on, not a substitute for it.

The good news: the codebase is already halfway prepared for this without
knowing it.

- `Project` already carries `office` and `region` fields
  (`core/projects/models.py:15-16`):
  ```python
  office = models.CharField(_("office"), max_length=100, blank=True)
  region = models.CharField(_("region"), max_length=100, blank=True)
  ```
  Free text, currently used only for CSV export display
  (`core/ui/exports.py`) — never for filtering. This is the natural seed
  of a real `Office` model, and it already lives in `core`, not a client
  app, exactly where ADR 0021/0022's "no client branching in core" rule
  says a generic-but-currently-single-tenant concept belongs.
- `User` and `Person` have **zero** location concept today. A worker's
  office is only inferable transitively through their active
  `ProjectAssignment → Project.office` — which breaks for anyone benched
  or between placements.
- RBAC (`core/accounts/permissions.py::can()` / `can_read_internal()`) is
  purely role-based — no object/tenant scoping in the mechanism itself.
  Every existing "coordinator only sees their stuff" behavior is a
  separate ad hoc queryset filter, not a systemic layer (see §3).
- Blacklist is explicitly company-wide by design —
  `features/blacklist/models.py:96`, `MatchFingerprint`'s docstring: "Company-wide (no
  office scoping)" — confirmed also in
  `docs/security/jober-blacklist-legal-basis.md`, which describes
  role-based (not site-based) visibility. This must stay untouched.
- Equipment stock is currently one company-wide pooled FIFO ledger with no
  site dimension at all — the single largest piece of this change (§2).
- Demo data impact is small: 3 `Project` rows, 7 `Person` rows in Jober's
  seed — low-risk to reseed.

Decisions confirmed with the user:
- **`Person` gets a direct, explicit `office` field** — set at intake,
  independent of whatever project the worker is currently on, so
  benched/between-assignment workers still have a visible office.
- **Equipment stock is split per-office in this same pass** — not left
  pooled. The largest piece of work here, taken on deliberately.
- **`User` ↔ `Office` is many-to-many** (amended — see revision note
  below): a staff member can work at more than one office. Observer still
  spans all offices via a role-based bypass, not a membership assignment.
- **Office principals**: each office has zero or more Manager-role
  "principals" with elevated staffing authority over that office
  specifically (§3a). Observer always holds full principal authority
  everywhere, in addition to whichever dedicated principals exist.
- **Office creation is vendor-side only, permanently** — Jober licensed
  exactly 3 offices from SyncMetric s.r.o.; no in-app role, including
  Observer, can create a 4th. See §3a.

> **Revision (2026-07-24):** the original round of this doc decided
> "staff belong to exactly one office — a simple FK, not many-to-many."
> That decision is reversed above: staff can work at multiple offices,
> and a new office-principal/invitation subsystem (§3a) is added. §2 and
> §3 below are updated accordingly; no other section changed.

## 1. New `Office` model

A small new `core/offices/` app (kept separate from `core/accounts/` —
distinct concept, multiple other models FK into it):

```python
class Office(models.Model):
    name = models.CharField(max_length=100)     # "Velký Meder"
    code = models.CharField(max_length=10)       # "VM"
    country = models.CharField(max_length=2)     # "SK" / "HU"
```

Three rows to seed: Velký Meder (SK), Győr (HU), Dunajská Streda (SK) —
**confirm exact spelling/diacritics before seeding or writing i18n
strings**; this doc uses the accented forms the user provided, but
"Velky Meder"/"Gyor"/"Dunajska Streda" (ASCII) may be what's actually
wanted in code/URLs even if diacritics are used for display.

This consolidates today's two free-text `Project.office`/`Project.region`
fields into one real FK — `country` moves onto `Office` itself rather than
staying a separate string repeated on every `Project`.

The FK is nullable everywhere it's added, so CorvinumEU is entirely
unaffected — it simply never populates `Office` rows, the same way it
already leaves `Project.office` blank today. No client branching in core;
the difference between clients is data, not code, consistent with ADR
0021/0022.

## 2. Where the FK goes

| Model | Change |
|---|---|
| `User` | `offices` M2M (`core/offices/` app), not a single FK. Set initially at invitation time (§3a); changed thereafter only by a principal of the office(s) involved, or Observer. Observer doesn't need membership rows — the bypass is role-based (§3). |
| `Person` | `office` FK, nullable, set at intake — the primary scoping key for worker visibility, independent of project assignment. |
| `Project` | `office` FK **replaces** the existing free-text field (data migration needed, see §4). |
| `Accommodation` (`features/logistics/models.py`) | `office` FK. Rooms already FK to one `Accommodation`, so they inherit it transitively — no separate field on `Room`. |
| `EquipmentStockLot` / `EquipmentStockAllocation` | `office` FK — a physical batch of stock is received into one office's warehouse. `EquipmentIssue` (issuing to a person) draws from that person's office's available lots. |
| Finance (`FinancialMonth`/`FinanceLineItem`) | **No new FK.** Already keys off `Project`, and totals are "summed dynamically... never hardcoded" per the model's own docstring — office-level aggregates are `GROUP BY project__office` at query time. |
| Blacklist | **Deliberately untouched.** No office FK anywhere in `features/blacklist/` — matching and visibility stay company-wide. |

> **Resolved.** The offices keep fully independent warehouses; FIFO never
> draws across them, and an office short on stock raises rather than
> borrowing. Cross-office transfer stays out of scope. `EquipmentStockReceipt`
> carries the office, denormalised onto lot, allocation **and movement** —
> the last beyond this doc's field list, because the balance/report
> aggregate runs over movements in one query and inbound/outbound rows
> reach their office by different join paths.

**Equipment is the largest piece.** Today's `EquipmentStockMovement`/`Lot`/
`Allocation` are a single pooled FIFO ledger keyed only by `item`, with no
site concept at all — adding `office` means the valuation/allocation logic
needs an office dimension throughout, not just a nullable column on one
model. **Cross-office transfer (moving stock from Győr to Velký Meder) is
explicitly out of scope for this pass** — flagged as a real open product
question (do the offices actually share equipment, or keep fully separate
warehouses?) rather than designing a transfer feature nobody has asked for
yet.

## 3. RBAC: a new systemic layer, not another ad hoc filter

Today, every "coordinator only sees their stuff" behavior is a separate,
hand-written queryset filter — found in `features/compliance/services.py`,
`features/compliance/notifications.py`,
`features/checklists/notifications.py`, `core/notifications/services.py`
(three separate sites), `core/projects/views.py` (two sites),
`core/projects/forms.py::operable_projects()`,
`features/logistics/forms.py`, and `core/ui/views.py` — roughly thirteen
sites, all keyed off `responsible_coordinators`/`owning_recruiter_id`, none
aware of any location concept. The shape is identical everywhere: "if role
== coordinator, filter to `responsible_coordinators=user`." Office-scoping
adds one more condition to that same shape at each site — described once
here, not re-derived per file:

> if role is not observer, filter to `office in user.offices.all()`, **in
> addition to** whatever role-based filter already applies there.

(Amended: since `User`↔`Office` is many-to-many, this is a
membership-in-set check, not an equality check against a single value.)

`core/accounts/permissions.py` should get one new helper (e.g.
`user_office_scope(user)` — returns a queryset of `Office` the user
belongs to, or all offices for Observer) that all thirteen sites call
into, rather than each one growing its own `if user.office` check
independently — this is the actual architectural change ADR 0008 needs to
account for.

> **As shipped, this differs.** `user_office_scope` returns **`None`** for
> an unrestricted caller, not "all offices": filtering by
> `office__in=<every office>` would still exclude records whose office is
> unset, which is not the same as "no filter". It also returns `None` when
> no `Office` rows exist at all, so CorvinumEU is unaffected. A second
> helper module, `core/offices/scoping.py`, carries the `Person`-specific
> rule that an office-less person belongs to their owning recruiter.

**Observer bypasses office-scoping entirely** — a role check, the same way
`can()` already special-cases roles today, not a "belongs to all offices"
assignment.

**One pre-existing gap, worth closing in the same pass** (closed
2026-07-25): `core/ui/exports.py`'s CSV export currently has **zero**
recruiter/coordinator scoping — it's a fully global export today, independent of multi-office.
Once the office-scope helper exists, wiring the export through it fixes a
real existing hole, not just a new multi-office concern — worth calling
out explicitly since it's the highest-risk leak vector once real
(non-fictional) data loads.

**Reports/dashboard** (`core/ui/views.py::reports()`) is almost entirely
global aggregates today, except one existing precedent — `pending_trials`
already filters to a coordinator's own projects. Every other tile needs
the same office-based filtering for non-observer roles, following that one
precedent rather than inventing a new pattern.

## 3a. Office principals and staff invitation (new)

There is currently **no staff invitation/signup flow anywhere in the
app** — `core/accounts/views.py` has only `login_page`, `logout_view`,
`two_factor_verify`, `two_factor_setup`; there's no `forms.py` or
`urls.py` in `core/accounts/`. `Action.USER_MANAGE`
(`core/accounts/permissions.py:49`) is defined and granted to Manager in
both clients' `policies.py`, but is entirely dormant — no view or
template references it anywhere. This section is genuinely new
functionality, not a refinement of something that exists.

**`Office.principals`** — a `ManyToManyField(User, related_name=
"principal_of_offices", blank=True)` on the new `Office` model, mirroring
`Project.responsible_coordinators` (`core/projects/models.py:19-24`)
field-for-field — the only existing precedent anywhere in the codebase
for "specific users get elevated rights over a specific object," already
proven at ~9 call sites and manageable via Django admin's
`filter_horizontal`.

**Invite authority is tiered by which role is being invited, not just the
inviter's own role:**

| Actor | Can invite | Scope |
|---|---|---|
| Observer (CEO) | Manager, Recruiter, or Coordinator | Any office |
| Principal Manager (of office X) | Manager, Recruiter, or Coordinator | Office X only |
| Regular Manager (member of office X, not principal) | Recruiter or Coordinator only — **not** Manager | Office X only |
| Recruiter / Coordinator | Nobody | — |

Two actions, not one, since the check depends on the target role:
- `Action.OFFICE_MANAGER_INVITE` — granted `{MANAGER, OBSERVER}` in
  `ACTION_ROLES`, but the real check additionally requires `office in
  user.principal_of_offices.all()` **or** `user.role == Role.OBSERVER`. A
  regular (non-principal) manager fails this despite holding the Manager
  role — the same role-gate-plus-object-scope shape
  `operable_projects()` (`core/projects/forms.py`) already uses for
  coordinators.
- `Action.OFFICE_STAFF_INVITE` (Recruiter/Coordinator) — granted
  `{MANAGER, OBSERVER}`, passes for **any** manager who is a member of
  that office (`office in user.offices.all()`), principal or not, plus
  the same principal-or-Observer bypass.

**Principal promotion/appointment is Observer-exclusive**, and separate
from both invite actions: `Action.OFFICE_PRINCIPAL_APPOINT`, granted
`{OBSERVER}` only. Used to (a) add an existing Manager to
`Office.principals`, and (b) appoint the first principal for an office
that currently has none. An existing principal cannot make a peer manager
a fellow principal — only Observer grants principal status. Inviting a
new Manager never automatically makes them a principal; that's always a
separate, deliberate Observer action.

**`StaffInvitation` model** (new): `email`, `role`, `offices` (M2M to
`Office`), `token` (stdlib `secrets.token_urlsafe` — no new dependency),
`invited_by` (FK `User`), `created_at`, `expires_at` (e.g. 7 days),
`accepted_at` (nullable, single-use). An invitation targeting Manager is
only creatable by someone passing `OFFICE_MANAGER_INVITE`'s full check;
one targeting Recruiter/Coordinator only needs `OFFICE_STAFF_INVITE`.

**Views**: `invite_staff` (branches on the two invite actions depending
on the selected target role — form: email, role, office(s)) and a public
`accept_invitation(token)` (no login required — validates
token/expiry/single-use, lets the invitee set a password, creates the
`User` with the invited role and offices, marks the invitation accepted).
Email delivery reuses the existing `EmailMessage` pattern already used
for payslip delivery (`features/payslips/services.py`) — a new template,
not a new channel or dependency.

Every step is audited via `core.audit.services.record_event`:
`"staff.invited"`, `"staff.invitation_accepted"`,
`"office.principal_appointed"`, `"user.offices_changed"`.

**Bootstrapping simplifies** with this design: since Observer can appoint
a principal for any office lacking one directly in-app, there's no
special-cased seed requirement for principals — seed data only needs the
3 `Office` rows plus the existing `ensure_superuser`-bootstrapped Observer
account; that Observer appoints real principals through the product
itself afterward. Seed data may still pre-assign demo principals for
convenience, but it's no longer architecturally required.

**Office creation is vendor-side only, permanently.** Jober licensed
exactly 3 offices (Dunajská Streda, Velký Meder, Győr) from SyncMetric
s.r.o. No `Action`, view, route, or RBAC path lets any Jober role —
including Observer — create a 4th `Office` row. If Django admin exposes
`Office` CRUD at all, it's superuser-restricted (SyncMetric ops), not
part of any Jober-facing role's surface. A 4th office is a commercial
request to SyncMetric (email/support ticket) outside the product, not a
feature to build. This is a deliberate license-enforcement boundary, not
an oversight — worth noting it's also a natural monetization lever
(offices-as-a-billable-dimension), consistent with the per-seat pricing
discussion held earlier, though that's a separate business decision from
this design.

## 4. Migration & seed impact

- Reseed 3 `Project` rows + 7 `Person` rows
  (`clients/jober/demo/management/commands/seed_people.py`/
  `seed_demo_scenario.py`) with real `Office` FKs instead of free-text
  `office`/`region` strings. Small, low-risk.
- The `Project.office`/`region` free-text → FK swap needs a **data
  migration** with a mapping step (existing string values → matching
  `Office` rows) since the field already holds real values — it isn't a
  purely additive column.

## Open items before implementation

- Confirm exact office names/diacritics for seeding, URLs, and i18n
  strings.
- Whether equipment can ever move between offices (transfer flow) — not
  designed here.
- Write the actual ADR amending/superseding ADR 0008 before code starts —
  "broad internal read" is a stated architectural default this change
  directly revises, and per the project's own discipline (new client
  additions require documenting what changed and why), this deserves the
  same treatment.
- The invitation flow (§3a) is the app's first authentication-adjacent
  feature beyond login/2FA — needs the same security review rigor as any
  auth surface before implementation: token entropy and expiry, single-use
  enforcement, and no email-enumeration leak through the invite form's
  error states (e.g. inviting an email that's already a `User` should
  fail the same visible way as any other validation error).
