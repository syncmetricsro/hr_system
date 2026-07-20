# Jober Requirements Supplement - Second Demo Interview

> **Changelog, 2026-07-20:** Records the second Jober demo interview as
> specification-level input. It removes transport from Jober scope; adds the
> warehouse, accommodation, feedback, age-warning, delivery-note, compliance,
> person-history, Telegram, and profitability requirements below; records the
> filled finance workbook; and updates the outstanding legal and client gates.

> **Status: SPECIFICATION ONLY.** Nothing in this supplement is evidence that a
> feature, migration, flag, or workflow is implemented. Where it conflicts with
> older discovery material, it is the later product requirement, but a separate
> build prompt and reviewed implementation are still required. It does not amend
> the main product design as "built" or "confirmed in production."

## 1. Scope boundary

Jober needs operational cost and recovery records, not a payroll engine.
Equipment inventory and accommodation per-head reporting may track money in and
out, and an approved equipment charge may contribute to a person's operational
debt/recovery history. They must not calculate wages or automatically deduct
money from wages. Per-project profitability is a separate, explicitly approved
Jober economic-reporting feature; it does not relax the no-payroll boundary.

Transport, weekly deliveries, routes, drivers, and vehicle management are now
**out of scope for Jober**. This reverses the first-interview assumption. Existing
code and the current `transport` flag are not removed by this documentation pass.
Fuel, driver, leasing, and toll remain valid manually entered P&L categories,
but there is no approved Jober transport module from which to populate them.

## 2. Equipment warehouse inventory

### Purpose

The primary Jober equipment deliverable is an auditable warehouse balance.
Staff must record bulk purchases and top-ups, issue sized items to people, and
see current quantity and value by catalog item and size. The monthly bookkeeper
report shows opening stock, receipts, issues, adjustments, and closing stock in
both quantity and EUR value. It is an accounting aid and is expected to match a
physical count only approximately.

Per-person carried equipment value is not a Jober report or success criterion.
An issuance remains linked to its recipient for custody and recovery decisions,
but Jober explicitly rejected an aggregate "value carried by each worker" view.

### Data model sketch

- `EquipmentVariant`: catalog item plus size; the stock-keeping key.
- `StockReceipt`: receipt date, supplier/reference, recorded by, and optional
  delivery-note attachment.
- `StockReceiptLine`: variant, positive quantity, and received total value.
- `StockMovement`: immutable receipt, issue, return, or approved adjustment with
  date, variant, quantity delta, value delta, source record, actor, and reason.
- `EquipmentIssue`: person, variant, quantity, issue/return state, and the stock
  movements produced by issuance and return.
- Current and monthly balances are derived from movements, never hand-stored
  totals. Money uses `Decimal`, never float, and stock cannot silently go below
  zero.

The stock-ledger extension belongs to `features/equipment`. Delivery-note files
also belong to this feature so it does not import `features/documents`; shared
storage and security primitives may come from core.

### UX

- Warehouse dashboard: current quantity and value by item and size, with a
  current grand total.
- Receive-stock form: receipt header followed by manually entered item lines.
- Existing issue-to-person flow: selection is by item and size and draws down
  available stock.
- Monthly report: month filter plus opening, received, issued, adjusted, and
  closing quantity/value, with a bookkeeper export in a later build decision.
- No Jober navigation item or report focused on per-person carried value.

### Workflow

1. An authorized user records a receipt and its itemized quantities and values.
2. Receipt movements increase quantity and value for each variant.
3. Issuance to a person creates the custody record and matching negative stock
   movement in one idempotent transaction.
4. Return or approved correction creates a new movement; posted movements are
   not silently edited or deleted.
5. A recovery decision may create an approved operational debt entry, but it
   does not alter payroll or compute a wage deduction.

Managers can manage catalog, receipts, adjustments, and recovery decisions.
Coordinators may issue/return equipment only for people in their projects.
Observers are read-only. All sensitive changes include actor and old/new values.

### Open questions

- Valuation method for mixed-price receipts: FIFO, weighted average, or another
  contract-approved method.
- Backdated movement policy, correction/reversal rules, stock-count adjustments,
  and whether a closed month can be reopened.
- Exact approval and settlement lifecycle for equipment-generated recovery debt.
- Required CSV columns and whether receipt totals include tax.

## 3. Accommodation per-head cost report

### Purpose

Each accommodation has its own monthly per-head base cost. Assignment applies
that cost to an occupant and separately records what that person pays, including
person-specific household variations. The monthly accommodation report shows
occupancy, empty-bed loss, cost, worker payments, and margin. It never creates a
wage deduction.

### Data model sketch

- `AccommodationCostPeriod`: accommodation, effective month, capacity, and
  per-head cost.
- `RoomAssignment`: person, accommodation/room, occupied dates, and separate
  monthly worker-payment amount or override.
- `AccommodationMonthlyResult`: derived occupancy, vacant capacity, base cost,
  payment total, margin, and empty-bed loss; not a stored accounting total.

Placement is `features/accommodation`, enabled for Jober and disabled for
CorvinumEU. It may later contribute signed accommodation lines to Jober
profitability through platform composition, not a direct feature import.

### UX and workflow

An authorized user sets capacity and per-head cost when creating or repricing an
accommodation. Assigning a person applies the effective cost and requires an
explicit worker-payment amount when it differs. The month-filtered report shows
occupied versus empty capacity and reconciles cost, payments, and margin.
Managers manage prices and view money; coordinators manage scoped assignments;
observers may view only if client policy grants it.

### Open questions

- Whether partial-month occupancy is daily-prorated or charged by another rule.
- Whether spouse/child amounts are one combined payment or separately itemized.
- Effective-date, retroactive correction, month-close, and historical snapshot
  rules.

## 4. Worker-to-office feedback tickets

### Purpose

Workers need a route to the office that bypasses their coordinator/recruiter.
Office staff can read, respond to, and resolve a complaint or feedback ticket.
The offhand request for internal team chat is recorded as a nice-to-have only;
it is not part of this feature.

### Data model sketch

- `FeedbackTicket`: public identifier, worker identity policy, subject/body,
  language, status, priority, timestamps, and resolved by/at.
- `FeedbackReply`: ticket, body, author side (worker or office), actor when
  internal, and timestamp.
- Statuses are minimally `open`, `awaiting_worker`, `awaiting_office`, and
  `resolved`, pending client confirmation.

Placement is `features/feedback`. This extends the current one-way feedback
inbox; it must not be described as already providing ticket replies or closure.

### UX and workflow

A worker submits through a controlled public link or approved channel. The
office receives a restricted inbox item, responds in-system, and resolves it
with an auditable actor. Coordinators and recruiters do not receive access by
default. Public endpoints require abuse controls and must not expose whether a
person exists.

### Open questions

- Anonymous versus identified submissions and how identity is verified.
- How workers receive replies without introducing a worker portal.
- Office role access, notifications, attachments, retention, reopening, and
  response-time expectations.

## 5. Under-18 birth-date warning

### Purpose and model

Entering or viewing a date of birth must visibly identify a person who is under
18 or near the threshold. The reusable age calculation belongs in `core/people`;
the threshold, presentation, and any workflow effect are Jober client policy.
Age is calculated against the relevant current/action date and is not stored as
a stale numeric field.

### UX and workflow

Show the warning on the person form and detail page and re-evaluate it on save.
This interview confirms highlighting only. It does not authorize an activation
block or substitute for legal review.

### Open questions

- Define "near 18" and the exact warning thresholds.
- Confirm whether under-18 status only warns or blocks any workflow.
- Confirm which roles may override a block if one is later approved.

## 6. DAC delivery-note attachment

### Purpose and model

A stock receipt may carry its scanned DAC/delivery note: a small PDF containing
the itemized purchase list, stamp, and signature. `StockReceiptAttachment`
records the receipt, file metadata, uploader, timestamp, and restricted storage
reference in `features/equipment`. Items remain manually entered; OCR is out.

### UX and workflow

Upload or replace the document from the receipt detail after explicit file-type
and size validation. Authorized office users can download it; every upload and
replacement is audited. This occurs roughly three or four times per year and is
explicitly low priority.

### Open questions

- Maximum file size, replacement/version retention, and exact role visibility.
- Storage/retention details remain pending the processor DPA review.

## 7. Unified compliance dashboard and operational debt

### Purpose

One manager surface should combine scoped missing-item alerts with a per-person
operational debt/recovery column such as the interview's "EUR 850 in the red."
The financial column is manager-only. Coordinators continue to see missing-item
alerts only for their projects and must not gain financial visibility through
the shared table.

### Data model and placement

Missing compliance facts remain owned by their source modules. Per-person money
is a capability-level overlap with `features/advances`, but Jober's exact entry
types and settlement rules are not yet approved. The client dashboard composes
registered columns; `features/compliance` must not import another feature.

An operational recovery entry records person, source, positive magnitude,
effect/type, status, actor, timestamps, and reversal relation. It is not a wage
record and cannot automatically modify payroll.

### UX and workflow

Managers filter by person, project, alert type, and debt state. Coordinators see
only their projects and no debt column. Selecting a row opens the person's
record and source events. Approved equipment recovery can contribute an entry;
settlement or reversal is explicit and audited.

### Open questions

- Which transactions create debt, who approves them, and how payment/waiver or
  dispute is settled.
- Whether the interview number is a net balance, gross outstanding charges, or
  a value maintained by an external process.
- Whether Jober can use `features/advances` unchanged or needs client policy and
  Jober-specific entry types.

## 8. Person-level history with actor

### Purpose and placement

The worker record is the primary audit view. Every displayed history event must
show who acted, when, what operation occurred, record type, and meaningful old
and new values. Core append-only audit remains in `core/audit`; person history in
`core/people` receives feature events through a registry.

### UX and workflow

The person page provides filters for person, date, operation, and record type.
Managers can investigate the full permitted history; other roles see only data
they may otherwise read. Once actor-complete person history meets those needs,
the standalone global audit navigation may be removed. Removing navigation must
not remove audit storage or authorized administrative access.

### Open questions

- Whether any system-wide audit view must remain for security/operations staff.
- Export, retention, and redaction rules for audit evidence.

## 9. Worker messaging: SMS and Telegram

### Purpose and configuration

Jober requires Twilio SMS from a dedicated prepaid number for Slovak/Hungarian
workers and Telegram for Ukrainian workers. The client already has a Telegram
channel and will grant access; a bot posts to that channel. This is a
channel-broadcast model, not per-worker chat-ID onboarding.

Placement remains shared `features/worker_messaging`, with provider/channel
policy in `clients/jober`. Telegram is target ON for Jober and remains OFF for
CorvinumEU. This decision supersedes the round-4 "manual channel, no bot"
banner and the per-worker Telegram opt-in/chat-ID design in
[`Jober_Messaging_Specs.md`](../../Jober_Messaging_Specs.md). The remainder of
that document is not declared superseded by this supplement.

### UX and workflow

Authorized staff compose and confirm a language-appropriate message. SMS may
resolve individual recipients under existing role/project policy. Telegram
publishes one message to the configured Ukrainian-worker channel; it must not
claim per-person delivery, project targeting, or person-level opt-in evidence
that the channel model cannot provide. Provider credentials are injected only
at runtime through the approved secret manager.

### Open questions and gates

- Telegram channel access, bot token/setup, administrator ownership, and test
  environment are still owed by the client.
- Confirm whether one channel is sufficient or future audience segmentation is
  required.
- Personal-data message content remains pending Art. 28 DPA review.

## 10. Jober per-project profitability

> **Provenance:** supplied as `HV 202510.xlsx` and referred to as
> `HV_202510.xlsx`; Jober per-project P&L, SHA-256
> `2e293b79dc237072c08e0ea16a36eaf8a60eed8b2bf3d1298b74e6a93f5743f6`.
> This is not `radonak.xlsx`, the deferred CorvinumEU per-worker wage sheet.

### Purpose and scope

This is a monthly project P&L, explicitly in scope for Jober and explicitly out
for CorvinumEU. It is a genuine profitability/economic dashboard, separate from
the operational-cost-only boundary for accommodation and equipment and still
not payroll.

The verified workbook contains one sheet named `November 2025`, two regions
(Megyer and DS), and nine projects. Costs are negative, revenues positive, and
project P/L is their sum. The filename indicates `202510`, so the authoritative
reporting month remains an open question.

### Data model sketch

- `Project.region`: roll-up key; whether it is a configurable catalog is open.
- `FinancePeriod`: project plus year/month, state, lock/reopen metadata, actor,
  and optional note; unique per project-month.
- `FinanceCategory`: client-seeded label, cost/revenue kind, grouping, order,
  active state, and manual/operational source policy.
- `FinanceLine`: period, category, signed `Decimal` amount, actor, and timestamps.
- Cost, revenue, P/L, regional totals, and grand totals are always derived over
  the complete active category and project sets.

Target placement is `features/profitability`, Jober ON and CorvinumEU OFF. The
current repository implementation remains under `features/finance` and enforces
positive magnitudes with sign derived from category kind; reconciling that
implementation with the filled workbook is future build work.

### Category seeds

Costs: gross wage before deductions, SZCO/subcontractors, levies, driver,
damage, forklift training, forklift licence, accommodation, insurance, medical,
coordinators, leasing, fuel, toll, factoring, office, recruitment, HR, clothing,
and other extraordinary costs.

Revenues: invoices, deductions received from workers, lunch, accommodation,
and damage recovered. Original source labels and group mappings are maintained
in [`Jober_Finance_Specs.md`](../../Jober_Finance_Specs.md).

### MVP UX and workflow

Managers manually enter each project's monthly lines, calculate consistent
totals, review regional and grand totals, and export CSV for the bookkeeper.
Closed months are reproducible and locked; reopening requires a reason and
audit. Observers may view closed reports but cannot edit them. No direct
accounting integration or OCR/PDF import is in scope.

The workbook demonstrates the risk being removed: Minit's cost formula omits a
EUR 200 extraordinary-cost row, which overstates Minit, Megyer, and grand-total
profit by EUR 200. System totals must be query-derived and cannot use
project-specific spreadsheet ranges.

### Later operational sources

- Accommodation cost/revenue may come from `features/accommodation` through a
  registered contribution interface.
- Deductions received may come from the approved recovery/advance capability.
- Clothing may come from `features/equipment`.
- SZCO remains manual until the deferred subcontractor-settlement feature is
  separately approved.
- Fuel, driver, leasing, and toll remain manual because Jober transport and
  vehicle tracking are OFF.
- Coordinators, office, factoring, insurance, HR, recruitment, and other
  overhead remain manual.

### Open questions

- Is the source period October 2025 (`202510`) or November 2025 (sheet label)?
- Can the region list grow beyond Megyer and DS?
- Is profitability enabled per project or globally for Jober?
- Must application storage use signed values, or may it normalize positive
  magnitudes by category while preserving signed entry/export behavior?

## 11. Confirmed Jober requirements retained

- Role- and project-scoped missing-item notifications.
- Optional anonymized blacklist fingerprints using name, birth number, mother's
  maiden name, and optional document number, with manager approval.
- Returning-person detection includes inactive and archived people.
- Archive instead of delete; retention is pending the client retention list.
- Sized equipment catalog and person issuance.
- Trial day, checklist, and activation gate.
- Confirmation dialogs for irreversible actions.
- Project management, with parity to the shared project capability.
- Jober-only per-project profitability and CSV export; no live accounting link.
- Small document uploads with no OCR.
- Full four-role Jober policy: recruiter, coordinator, manager, and observer.
- English source plus Slovak, Hungarian, and Ukrainian UI support, with Slovak
  default per platform policy.

## Appendix A. Client-owed artifacts and decisions

| Artifact or decision | Status | Blocks |
|---|---|---|
| Filled Jober P&L workbook | Received and verified | No longer blocks Jober profitability specification |
| Art. 28 processor DPA naming Syncmetric | Not received | Sensitive-data production use |
| Processor/recipient and retention list referenced by the privacy notice | Not received | Concrete retention and processor review |
| Employee privacy notice | Received, partial evidence only | Does not lift the DPA gate |
| Telegram channel access and bot setup | Not received | Telegram integration/testing |
| Correct `202510` versus `November 2025` period | Open | Finance period reconciliation |
| Region growth and profitability toggle scope | Open | Finance configuration |
| Stock valuation and month-close policy | Open | Inventory accounting behavior |
| Recovery/debt workflow | Open | Per-person financial behavior |
| Accommodation proration/payment rules | Open | Monthly accommodation calculations |
| Under-18 thresholds and workflow effect | Open | Age-warning behavior |
| Feedback identity/reply/retention rules | Open | Ticket workflow |
| Five- versus ten-year retention | Open pending retention list | Archive/blacklist/document retention |

The privacy notice supports legal-obligation processing for core HR data,
contract processing for equipment issuance and wage-deduction agreements, and
legitimate-interest processing for SMS/email operational messaging. It is a
controller transparency notice, not the required processor agreement. Real
worker PII remains barred until the repository's full real-data gate passes.
The client cited a possible forthcoming online-invoicing/inspection law as an
additional reason to retain anonymized blacklist matching rather than expose a
plain personal-data list; that statement is context, not a verified legal basis
or a substitute for the DPA, retention schedule, LIA, and legal review.
