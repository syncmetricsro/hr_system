# Jober amendment demo runbook

> Updated 2026-07-20 for the second-interview headline pack. This is the Jober
> client on port 8000; all people and amounts are fictional demo data.

This walkthrough demonstrates working Django workflows, not mock screens. Allow
35-45 minutes and present in Slovak, switching briefly to Hungarian or Ukrainian.

## Preparation

1. Run `scripts/dev_app.sh rebuild` from the repository root. Use
   `doppler run --project hr_system --config dev -- scripts/dev_app.sh rebuild`
   only if the optional live Twilio segment will actually be shown.
2. Open <http://localhost:8000> and sign in as
   `manazer@demo.jober.test` / `demo-jober-2026`.
3. Confirm Dashboard shows Warehouse stock and Accommodation occupancy, the
   Finance page has Megyer and DS, and no Transport navigation or project card
   is present.
4. Run `scripts/playwright_e2e.sh` and rehearse the issue/return and finance
   edits once. Never use real worker data or the supplied client workbook.

Other demo accounts use the same password:

| Role | Account |
|---|---|
| Recruiter | `naborar@demo.jober.test` |
| Coordinator | `koordinator@demo.jober.test` |
| Observer | `pozorovatel@demo.jober.test` |

## Headline sequence

### 1. Scope correction: transport removed

Open Projects and a project detail. Point out that transport, delivery weeks,
vehicles, routes, and readiness requirements are absent. Existing historical
database structures were retained for compatibility, but Jober cannot navigate
to or create transport records.

### 2. Age warning at intake

Sign in as Recruiter and create or edit a fictional person. Enter a birth date
for someone younger than 18: the server-rendered warning appears immediately.
Enter a date within 30 days of the eighteenth birthday to show the advisory.
Submit the form to demonstrate the same warning without htmx. Open seeded
**Mira Novakova** to show the persisted-record warning.

Talking point: this is a prominent warning, not a guessed legal hard-stop. The
business still needs to decide whether any under-age case must be blocked.

### 3. Warehouse stock accounting

Sign in as Manager and open **Warehouse**.

- Show current quantity and EUR value by item and size.
- Filter the monthly report and explain opening, receipts, issues, returns,
  adjustments, and closing value.
- Open Receive stock and show quantity plus total lot value; do not submit a
  duplicate unless demonstrating idempotency.
- Open Olha as Coordinator and issue an item. Available quantity is visible and
  overdraw is rejected atomically.
- Return an item as either **Reusable - return to stock** or **Damaged or
  retired**. Reusable stock becomes a new FIFO lot at its original issued value.

The seeded history includes receipt, issue, restock, and retire examples. The
manager recovery review snapshots FIFO issue value but does not mutate payroll.
Jober's primary view is warehouse balance, not a per-person carried-value total.

### 4. Accommodation cost and margin

Open **Accommodation**, then the Nitra location. Show its effective monthly
capacity and per-head cost period. Open **Cost report**, select the current
month, and explain:

- standing cost = capacity x per-head monthly cost;
- occupied cost and worker payments use assignment-date overlap and daily
  proration;
- empty-bed loss is unused standing capacity;
- margin = worker payments - full standing cost.

Olha is seeded from mid-month with a separate worker payment, making the
proration visible. State explicitly that this report creates no wage,
deduction, or recovery entry.

### 5. Regional project P&L

Open **Finance**. Show the regional roll-ups for **Megyer** and **DS**, then the
company and per-project totals. Open the fictional Minit-style project month:

- costs are entered and displayed negative, revenues positive;
- stored values remain positive magnitudes with category kind carrying meaning;
- positive cost input and negative revenue input are rejected;
- every category row is dynamically summed, including the seeded EUR 200
  extraordinary-cost row;
- locking prevents edits and reopening requires an audited reason.

Export CSV and show detailed period, region, project, category, kind, group, and
signed amount rows followed by explicit regional and grand summaries. The demo
uses fictional numbers only. `HV 202510.xlsx` remains a specification source,
not seed data; its `202510` filename versus `November 2025` sheet label is still
an open client question.

## Supporting flow

If time allows, show the existing trial-readiness-activation flow, compliance
alerts, blacklist warning/manager decision, equipment recovery review, role
switching, and optional SMS. Readiness now requires medical, gear, and the
accommodation decision only; transport is not a pillar for Jober.

## Deferred, do not present as delivered

- Telegram channel bot access and administration.
- DAC delivery-note PDF attachment.
- Worker-office feedback conversations and replies.
- Consolidated financial-debt settlement.
- Actor-complete person-level history replacing the global audit surface.
- Projects CRUD.

These items have no inactive demo placeholders. Telegram and sensitive document
behavior also remain gated by external access and the Art. 28 DPA review.

## Caveats and decisions to collect

- Fictional data only; the real-data gate remains closed.
- Confirm whether the finance period is October 2025 or November 2025.
- Confirm whether regions can grow and whether P&L opt-out is per project.
- Confirm stock backdating, adjustments, valuation corrections, and month close.
- Confirm accommodation proration/payment semantics.
- Confirm whether the age warning ever blocks an action.
- Obtain the Art. 28 processor DPA and processors/retention list.
- Obtain Telegram channel access and bot administrator details for its later slice.
