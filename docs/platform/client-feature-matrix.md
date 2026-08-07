# Cross-Client Feature Matrix

> **Changelog, 2026-07-20:** Adds the first repository-level Jober/CorvinumEU
> target matrix. It records Jober transport OFF, Telegram and profitability ON,
> shared equipment with divergent reports, the new Jober interview features,
> the received Jober finance workbook, and the still-deferred CorvinumEU wage
> workbook.

> **Reconciled against `main`, 2026-07-26** (production-readiness item 9). The
> runtime columns were materially stale: warehouse stock and the under-18
> warning were listed as unimplemented when both ship, and Jober transport was
> flagged as an ON/OFF mismatch that `clients/jober/settings.py` had already
> resolved. Office scoping (ADR 0026) is now recorded, including the fact that
> it divides the two clients by *data* rather than by feature flag.

> **Status: SPECIFICATION MATRIX.** Target state is product intent; runtime state
> reports the current branch and is not changed by this document.

## Legend

| Marker | Meaning |
|---|---|
| ON | Required for the client target |
| OFF | Explicitly excluded from the client target |
| SPEC | Required but not yet implemented to this specification |
| LOW | Required/allowed but explicitly low priority |
| PENDING | Target selected but blocked by an external artifact or decision |
| CURRENT | Present/enabled in the current branch |

## Matrix

| Capability | Target module | Jober target | Jober current branch | CorvinumEU target | CorvinumEU current branch | Notes / gate |
|---|---|---|---|---|---|---|
| People registry and archive | `core/people` | ON | CURRENT, **office-scoped** | ON | CURRENT | Returning-person matching must include inactive/archived records; Jober people carry an office and non-Observer roles see only their own (a person with no office falls to their owning recruiter) |
| Office-scoped RBAC | `core/offices`, `core/accounts` | ON | CURRENT | OFF (single site) | OFF **by data** | Jober confines every non-Observer role to its own offices, with a 403 on cross-office object access. CorvinumEU never creates `Office` rows, so the same code is a no-op there — no client branching in `core` |
| Under-18 warning | `core/people` + client policy | SPEC | **CURRENT** | OFF/unconfirmed | Present (shared core) | `core/people/services.py::age_warning` returns a server-authoritative critical warning under 18 and an advisory within 30 days of the birthday; it informs, it does not block. Whether it should gate a workflow is still open |
| Projects and assignments | `core/organizations`, `core/assignments` | ON | Assignments/trials CURRENT; **project records themselves cannot be created, edited or archived in-app** | ON | CURRENT | `project.manage` is granted but implemented nowhere: the dashboard's "Manage projects" button links to the read-only list. Only `project_list` and `project_detail` routes exist. Production-readiness item 15 |
| Recruitment trial/checklist/activation | `features/recruitment_trials`, `features/checklists` | ON | Trial/readiness current; Jober checklist flag OFF | ON | CURRENT | Jober interview confirms complete flow; runtime flags do not yet match |
| Documents, no OCR | `features/compliance` | ON with restricted file boundary | CURRENT | ON with restricted file boundary | CURRENT | Shared policy and code permit files only for forklift/crane/welding licences; high-risk identity/medical/civil-status documents are metadata-only or prohibited. Excluded scans require a separately scoped Secure Document Vault. Real data still waits on DPA, access, backup, erasure, and retention gates |
| Duplicate/blacklist fingerprints | `features/duplicate_blacklist` | ON, PENDING | CURRENT behind legal/data gates | ON, PENDING | CURRENT behind gates | Optional anonymized fields; manager approval; real data pending legal gate |
| Missing-item notifications | `features/compliance` | ON | CURRENT | ON | CURRENT | Coordinators project-scoped; roles enforced server-side |
| Unified compliance/debt dashboard | client dashboard registry + source features | SPEC | Missing-item surface only | OFF/unconfirmed | Not implemented | Jober debt column manager-only; no feature-to-feature import |
| Per-person operational recovery/debt | `features/advances` + client policy | SPEC | Flag OFF | ON | CURRENT | Shared capability confirmed; Jober entry types/settlement open; never a wage engine |
| Equipment catalog and issuance | `features/equipment` | ON | CURRENT | ON | CURRENT | Shared base capability with client-selected reports |
| Warehouse stock ledger/report | `features/logistics` | ON, primary | CURRENT, **per office** | OFF | Not implemented | Jober balance by item/size/value and monthly movements; each office holds its own stock and FIFO never draws across offices (ADR 0026) |
| Per-person equipment outstanding report | `features/equipment` | OFF as deliverable | Incidental value exists | ON | CURRENT | CorvinumEU report feeds recovery decisions; not a Jober success criterion |
| Equipment DAC attachment | `features/equipment` | LOW, PENDING | Not implemented | OFF/unconfirmed | Not implemented | Manual item entry, no OCR; storage specifics pending DPA |
| Accommodation occupancy | `features/accommodation` | ON | CURRENT, **office-scoped** | OFF | Flag OFF | Jober-only; locations carry an office and the occupancy tile counts only the viewer's offices |
| Accommodation per-head cost/margin | `features/accommodation` | SPEC | Current room-rate report differs | OFF | Not installed/enabled | Operational reporting only; no wage deduction |
| Transport/deliveries/vehicles | `features/transport` | OFF | Flag OFF | OFF | Flag OFF | Removed by second Jober interview; `clients/jober/settings.py` sets `"transport": False`, so the earlier flag mismatch is resolved. Code removal is still separate work |
| Worker feedback intake | `features/feedback` | ON | CURRENT one-way inbox | OFF | Flag OFF | CorvinumEU rejected worker portal/feedback |
| Feedback ticket/reply/resolve | `features/feedback` | SPEC | Not implemented | OFF | Not implemented | Identity, reply delivery, and retention open |
| SMS messaging | `features/messaging` | ON, PENDING | CURRENT Twilio path | OFF | Flag OFF | SK/HU segment; personal-data content pending DPA/provider setup |
| Structured job-offer email | `features/messaging` | ON, PENDING | CURRENT | ON, PENDING | CURRENT, Manager/HR Admin-only | Per-language templates, recipient preview, opt-out/blacklist guards and audited sends. Real recipients remain gated by each client's lawful basis, provider DPA, retention decision and production readiness |
| Telegram channel bot | `features/messaging` | ON, PENDING | Not implemented | OFF | Not implemented | Manager/Admin-only, outbound text to one Ukrainian-worker channel; no per-worker delivery model or inbound bot. Pending client access/privacy gates; canonical design: `docs/product/jober-telegram-channel-design.md` |
| Person history with actor | `core/audit`, `core/people` | SPEC | History lacks complete actor coverage | ON/general audit | Audit current | Jober prefers person timeline; global nav may later be removed |
| Per-project profitability/P&L | `features/profitability` | ON, SPEC | Flag ON under `features.profitability`; model differs | OFF | Flag OFF | Unblocked by verified Jober workbook; hard client divergence |
| Profitability CSV export | `features/profitability` | ON, SPEC | Existing export requires reconciliation | OFF | Not enabled | Bookkeeper export only; no live accounting integration. Finance rolls up by office and is scoped to the viewer's offices (ADR 0026) |
| Accountant data handoff | Future shared feature, not yet authorized | PENDING, SK/HU separate | Not implemented | PENDING, SK/HU separate | Not implemented | Country-specific structured payroll facts and conditional tax declarations/evidence; no excluded scans. Jurisdiction is explicit per employment and never inferred from office. Mixed, posted, unresolved cross-border, and other-country cases are refused. Exact entity, recipient/DPA, fields, custody, transfer, and retention remain gated by `docs/product/accountant-data-handoff.md` |
| Wage ledger | `features/wage_ledger` | OFF | Flag OFF | ON | CURRENT | CorvinumEU calendar-month recorded gross wage beside recorded net payslip; no statutory net computation |
| Payslips | `features/payslips` | OFF | Flag OFF | ON | CURRENT | CorvinumEU only |

## Client policy divergences

- Jober equipment selects warehouse balance and monthly stock movement reports;
  CorvinumEU selects person-level custody/outstanding-value reports. One report
  must not be treated as satisfying both clients.
- Jober profitability is an economic dashboard backed by `HV 202510.xlsx`;
  CorvinumEU explicitly excludes P&L. `radonak.xlsx` is a separate, deferred
  CorvinumEU per-worker wage artifact.
- Jober uses all four platform roles. CorvinumEU remains manager-centric where
  its client policy says so.
- **Office scoping divides by data, not by flag.** Jober is multi-site and
  therefore scoped; CorvinumEU is single-site and never creates `Office` rows,
  so `user_office_scope()` returns its unrestricted sentinel and every scoped
  query behaves exactly as it did before ADR 0026. This is the pattern to copy
  for future site-shaped divergences — it keeps client branching out of `core`.
- Jober messaging selects SMS and a Telegram broadcast channel. CorvinumEU keeps
  SMS and general worker messaging OFF, but owner approval on 2026-08-07 enables
  the narrower structured job-offer email workflow for Manager/HR Admin.
- Both clients may use an operational recovery/advance capability, but client
  policies define entry types and reports. Neither capability authorizes payroll
  computation.
