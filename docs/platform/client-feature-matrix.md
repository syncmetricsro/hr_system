# Cross-Client Feature Matrix

> **Changelog, 2026-07-20:** Adds the first repository-level Jober/CorvinumEU
> target matrix. It records Jober transport OFF, Telegram and profitability ON,
> shared equipment with divergent reports, the new Jober interview features,
> the received Jober finance workbook, and the still-deferred CorvinumEU wage
> workbook.

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
| People registry and archive | `core/people` | ON | CURRENT | ON | CURRENT | Returning-person matching must include inactive/archived records |
| Under-18 warning | `core/people` + client policy | SPEC | Not implemented | OFF/unconfirmed | Not implemented | Threshold and workflow effect open |
| Projects and assignments | `core/organizations`, `core/assignments` | ON | Partial project management | ON | CURRENT | Full create/edit/archive parity remains a Jober requirement |
| Recruitment trial/checklist/activation | `features/recruitment_trials`, `features/checklists` | ON | Trial/readiness current; Jober checklist flag OFF | ON | CURRENT | Jober interview confirms complete flow; runtime flags do not yet match |
| Documents, no OCR | `features/documents` | ON, PENDING | CURRENT | ON | CURRENT | Production specifics pending Art. 28 DPA and processor/retention list |
| Duplicate/blacklist fingerprints | `features/duplicate_blacklist` | ON, PENDING | CURRENT behind legal/data gates | ON, PENDING | CURRENT behind gates | Optional anonymized fields; manager approval; real data pending legal gate |
| Missing-item notifications | `features/compliance` | ON | CURRENT | ON | CURRENT | Coordinators project-scoped; roles enforced server-side |
| Unified compliance/debt dashboard | client dashboard registry + source features | SPEC | Missing-item surface only | OFF/unconfirmed | Not implemented | Jober debt column manager-only; no feature-to-feature import |
| Per-person operational recovery/debt | `features/advances` + client policy | SPEC | Flag OFF | ON | CURRENT | Shared capability confirmed; Jober entry types/settlement open; never a wage engine |
| Equipment catalog and issuance | `features/equipment` | ON | CURRENT | ON | CURRENT | Shared base capability with client-selected reports |
| Warehouse stock ledger/report | `features/equipment` | SPEC, primary | Not implemented | OFF | Not implemented | Jober balance by item/size/value and monthly movements |
| Per-person equipment outstanding report | `features/equipment` | OFF as deliverable | Incidental value exists | ON | CURRENT | CorvinumEU report feeds recovery decisions; not a Jober success criterion |
| Equipment DAC attachment | `features/equipment` | LOW, PENDING | Not implemented | OFF/unconfirmed | Not implemented | Manual item entry, no OCR; storage specifics pending DPA |
| Accommodation occupancy | `features/accommodation` | ON | CURRENT | OFF | Flag OFF | Jober-only |
| Accommodation per-head cost/margin | `features/accommodation` | SPEC | Current room-rate report differs | OFF | Not installed/enabled | Operational reporting only; no wage deduction |
| Transport/deliveries/vehicles | `features/transport` | OFF | **Flag ON; mismatch** | OFF | Flag OFF | Removed by second Jober interview; code removal is separate work |
| Worker feedback intake | `features/feedback` | ON | CURRENT one-way inbox | OFF | Flag OFF | CorvinumEU rejected worker portal/feedback |
| Feedback ticket/reply/resolve | `features/feedback` | SPEC | Not implemented | OFF | Not implemented | Identity, reply delivery, and retention open |
| SMS messaging | `features/worker_messaging` | ON, PENDING | CURRENT Twilio path | OFF | Flag OFF | SK/HU segment; personal-data content pending DPA/provider setup |
| Telegram channel bot | `features/worker_messaging` | ON, PENDING | Not implemented | OFF | Not implemented | Ukrainian segment; pending channel access and bot setup |
| Person history with actor | `core/audit`, `core/people` | SPEC | History lacks complete actor coverage | ON/general audit | Audit current | Jober prefers person timeline; global nav may later be removed |
| Per-project profitability/P&L | `features/profitability` | ON, SPEC | Flag ON under `features.finance`; model differs | OFF | Flag OFF | Unblocked by verified Jober workbook; hard client divergence |
| Profitability CSV export | `features/profitability` | ON, SPEC | Existing export requires reconciliation | OFF | Not enabled | Bookkeeper export only; no live accounting integration |
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
- Jober messaging selects SMS and a Telegram broadcast channel. CorvinumEU keeps
  automated worker messaging OFF.
- Both clients may use an operational recovery/advance capability, but client
  policies define entry types and reports. Neither capability authorizes payroll
  computation.
