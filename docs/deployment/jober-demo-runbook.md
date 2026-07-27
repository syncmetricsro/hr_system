# Jober amendment demo runbook

> Updated 2026-07-26 for office-scoped RBAC (ADR 0026 Phase B) and for
> presenting from **staging**. All people and amounts are fictional demo data.

This walkthrough demonstrates working Django workflows, not mock screens. Allow
40-50 minutes and present in Slovak, switching briefly to Hungarian or Ukrainian.

## Read this first: the demo is now office-scoped

Jober operates three offices — **Velký Meder (VM)**, **Győr (GYR)** and
**Dunajská Streda (DS)**. Every non-observer account sees only its own office's
data, and **each office has its own manager, recruiter and coordinator** — so
the separation can be shown from both sides rather than asserted from one. This
is the headline of §1 below, but it also changes what every other step shows:

- Manager/Recruiter/Coordinator see one office's people, projects, warehouse,
  accommodation, compliance and finance — **not** company totals.
- Only the Observer sees all three offices, and Finance routes them to a
  different, Observer-only executive dashboard.
- The office bounding the current view is always named in the top-right badge
  next to the role.

If a figure looks "too small" during the demo, that is the scoping working, not
missing data.

## Preparation

**Venue: staging.** The demo is given from
<https://jober-staging.80.211.210.46.sslip.io>, not from a laptop. Its database
was dropped and rebuilt on 2026-07-26, so it matches every figure quoted in
this runbook exactly. Do not reseed it again before the demo — a reseed *adds
and repairs* rows but cannot retract hand-made ones, which is what made the
warehouse stop reconciling last time.

1. Open the staging URL and sign in as `manazer@demo.jober.test`. Ask the owner
   for the password; treat whatever is written in `CLAUDE.md` as public.
2. Confirm before the client arrives: the header badge reads **Velký Meder**;
   Dashboard shows Warehouse stock and Accommodation occupancy; People lists
   **five** workers; Projects lists **DHL Bratislava and Minit** (Velký Meder's
   two, not all six); and no Transport navigation or project card is present.
3. Sign in as `manazer.gyor@demo.jober.test` in a **second** browser profile.
   Badge reads **Győr**; People lists **Farrukh only**; Projects lists
   **WEBASTO and Mevis 080**. This is the account §1 switches to, and having it
   already open is what makes that moment quick rather than a login detour.
4. Sign in as `pozorovatel@demo.jober.test` in a **third** profile and confirm
   the badge reads **All offices** and Finance opens the executive dashboard.

All nine staff accounts share one password — the one the owner set. Three
browser profiles (or one plus two private windows) is the smoothest way to
switch mid-demo.

**Uploads work — and are worth showing.** The earlier "don't upload anything"
warning was based on two things that turned out to be wrong or since fixed:
staging *does* have a storage mount, so uploads always survived redeploys, and
they are now served by a permission-checked view instead of 404ing. Uploading
a worker photo or a certificate scan is a legitimate part of the demo.
Better still, it demonstrates the boundary: a certificate document is visible
to managers, the Observer, the owning recruiter and the responsible
coordinator — an unconnected recruiter in the same office sees that the
certificate exists and gets a refusal on the file itself.

**Twilio.** Staging carries live provider credentials, but non-production apps
now enforce a recipient allowlist, so a send can only reach the configured
demo handset — editing a person's phone to a real number no longer texts it.
Confirm with the owner whether the live-SMS segment is wanted. If SMS is
switched off entirely, the panel says so and disables the control rather than
recording a failed message.

### Local fallback

If staging is unavailable, run `scripts/dev_app.sh rebuild` and present from
<http://localhost:8000> instead — same accounts, same seeded figures. Use
`doppler run --project hr_system --config dev -- scripts/dev_app.sh rebuild`
only if the live Twilio segment will actually be shown. **Rebuild, don't
reuse:** a database seeded before 2026-07-25 keeps a pre-split pooled stock
receipt and office-less people, so per-office figures and the blacklist step
will not look right.

Rehearse the issue/return and finance edits once beforehand. Never use real
worker data or the supplied client workbook.

Other demo accounts use the same password. **Office membership is what each
account can see**, so switching accounts is now part of the demo, not a detour:

| Role | Account | Office |
|---|---|---|
| Manager | `manazer@demo.jober.test` | Velký Meder |
| Recruiter | `naborar@demo.jober.test` | Velký Meder |
| Coordinator | `koordinator@demo.jober.test` | Velký Meder |
| Manager | `manazer.gyor@demo.jober.test` | Győr |
| Recruiter | `naborar.gyor@demo.jober.test` | Győr |
| Coordinator | `koordinator.gyor@demo.jober.test` | Győr |
| Manager | `manazer.ds@demo.jober.test` | Dunajská Streda |
| Recruiter | `naborar.ds@demo.jober.test` | Dunajská Streda |
| Coordinator | `koordinator.ds@demo.jober.test` | Dunajská Streda |
| Observer | `pozorovatel@demo.jober.test` | all three (role bypass) |

**All three offices are staffed, and that is what makes §1 convincing.** One
direction — "the Velký Meder manager cannot see Győr" — looks like a filter.
Signing in as `manazer.gyor@` and finding Velký Meder equally absent is what
shows it is a boundary. Each office's projects are also run by *that office's*
coordinator, so "who runs the Győr contracts?" has a real answer.

Seeded people, so you know who should be visible to whom: **Olha, Diana, Mira,
Bohdan, Ivan** are Velký Meder; **Farrukh** is Győr; **Tran** is Dunajská
Streda. Six projects, two per office: **DHL Bratislava + Minit** (Velký
Meder), **WEBASTO + Mevis 080** (Győr), **CARGO + RLS 067** (Dunajská
Streda) — so each office's P&L is a real roll-up of two contracts, not a
restatement of one.

## Headline sequence

### 1. Office separation

The newest and most consequential change: each office's data is walled off, and
this is enforced server-side, not hidden in the UI.

Signed in as **Manager** (`manazer@`, Velký Meder):

- Point at the **Velký Meder** badge beside the role in the header. That is the
  office bounding everything on screen.
- **People** lists Olha, Diana, Mira, Bohdan and Ivan. Farrukh (Győr) and Tran
  (Dunajská Streda) are absent — not filtered in the UI, never queried.
- **Projects** shows DHL Bratislava and Minit — Velký Meder's two. The
  other four, in Győr and Dunajská Streda, are not listed.
- **Warehouse** shows Velký Meder's stock only.

Then show that it is a real boundary, not a filter:

- Note the project id of DHL Bratislava, then edit the URL to a Győr or
  Dunajská Streda project (WEBASTO, Mevis 080, CARGO, RLS 067) or person. The
  server returns **403 Forbidden** — guessing a URL does not work.

**Now switch to `manazer.gyor@` and do it in reverse.** Győr's manager sees
WEBASTO and Mevis 080, sees Farrukh, and gets the same **403** on DHL
Bratislava. This is the moment worth spending time on: the first half alone
could be a permissions quirk in one account, and doing it symmetrically with a
second real manager is what shows the offices are genuinely walled off from
each other rather than one account being restricted.

Point out too that each office's projects list its *own* coordinator as
responsible — the Győr contracts are run by `koordinator.gyor@`, not by
somebody in Velký Meder who could not open them.

Now switch to **Observer** (`pozorovatel@`):

- The badge reads **All offices**.
- People and Projects show all three offices' records.
- **Finance** routes to a different page entirely — the Observer-only executive
  dashboard, with per-office roll-ups and a multi-series trend chart comparing
  the three offices.

Talking points: the observer role is the only cross-office view, and it is a
role bypass rather than a membership, so nobody accumulates offices by
accident. Blacklist is the one deliberate exception — matching stays
company-wide, so a person blocked at one office is still caught at the other
two (§8).

### 2. Scope correction: transport removed

Open Projects and a project detail. Point out that transport, delivery weeks,
vehicles, routes, and readiness requirements are absent. Existing historical
database structures were retained for compatibility, but Jober cannot navigate
to or create transport records.

### 3. Age warning at intake

Sign in as Recruiter and create or edit a fictional person. Enter a birth date
for someone younger than 18: the server-rendered warning appears immediately.
Enter a date within 30 days of the eighteenth birthday to show the advisory.
Submit the form to demonstrate the same warning without htmx. Open seeded
**Mira Novakova** to show the persisted-record warning.

Talking point: this is a prominent warning, not a guessed legal hard-stop. The
business still needs to decide whether any under-age case must be blocked.

### 4. Warehouse stock accounting

Each office now keeps its **own warehouse**. Stock is received into one office,
FIFO only ever draws from the worker's own office, and there is no cross-office
transfer.

Sign in as Manager and open **Warehouse**.

- Show current quantity and EUR value by item and size. On a freshly seeded
  stack this is **Velký Meder's 36 units / EUR 623.50** — not a company total.
  (Győr holds 23 / EUR 406.00 and Dunajská Streda 14 / EUR 252.00; switch to
  Observer later to show the combined 73 / EUR 1 281.50.)
- Filter the monthly report and explain opening, receipts, issues, returns,
  adjustments, and closing value — all for this office.
- Open **Receive stock**. Note the **Receiving office** field: stock must land
  in a named warehouse, and the picker offers only offices you belong to. Show
  quantity plus total lot value; do not submit a duplicate unless demonstrating
  idempotency.
- The **Stock adjustment** form on the same page likewise names the office
  whose stock is being corrected.
- Open Olha as Coordinator and issue an item. The available quantity shown is
  **her own office's** stock, and overdraw is rejected atomically. Attempting
  more than Velký Meder holds fails with an error naming the office — it does
  not quietly consume Győr's stock.
- Return an item as either **Reusable - return to stock** or **Damaged or
  retired**. Reusable stock becomes a new FIFO lot at its original issued
  value, back in that worker's office.

The seeded history includes receipt, issue, restock, and retire examples in
every office. The manager recovery review snapshots FIFO issue value but does
not mutate payroll. Jober's primary view is warehouse balance — now per office,
not company-wide.

### 5. Accommodation cost report

Accommodation is office-scoped too: the list shows only this office's
locations, and each location now carries an **Office** — the same boundary as
People and Projects, enforced the same way.

**Do not try to demonstrate the 403 here.** The seed creates exactly one
accommodation location (Ubytovňa Nitra, Velký Meder), so there is no other
office's location to open by URL. The boundary is already shown convincingly
in §1 with a project and a person; repeat the point verbally instead.

Open **Accommodation**, then the Nitra location (Velký Meder). Show its
effective monthly capacity and per-head cost period. Open **Cost report**,
select the current month, and walk the **five figures** — the card shows these
and nothing else, reworked to the client's own specification (J3):

| Figure | Meaning |
|---|---|
| **Capacity** | beds the company is paying for, from the cost period |
| **Occupied beds** | how many workers are actually placed — a head count |
| **Standing cost** | capacity x per-head monthly cost; owed whether beds fill or not |
| **Worker payments** | what the placed workers themselves pay |
| **Empty-bed loss** | standing cost - worker payments - occupied cost |

Two points worth making out loud, because both have surprised people:

- **Occupied beds counts workers, not beds taken out of circulation.** A worker
  alone in a two-bed room who pays extra to keep it to himself counts as *one*;
  the bed he funds still reads as empty. This is a deliberate open question
  with the client, not an oversight.
- **Occupied cost is deliberately not displayed.** It appears in the loss
  formula above only so the arithmetic can be followed; the client asked for it
  off the card. If someone asks where it went, it is occupied beds x per-head
  cost, prorated by day.

Empty-bed loss never goes below zero: a full house has no empty beds, so it
reads 0 rather than a negative number.

Olha is seeded from mid-month with a separate worker payment, making the daily
proration visible — mid-month arrivals cost and pay a fraction of the month.
State explicitly that this report creates no wage, deduction, or recovery entry.

The summary bar at the top sums the same five figures **across this manager's
offices only**. An Observer sees all three offices in it; a manager does not.

### 6. Profit/loss by office

Still as **Manager**, open **Finance**. Scroll to the *Office roll-up ·
Profit/loss by office* panel: it lists **Velký Meder only** — a manager sees
their own office's P&L, never the company's. Open the seeded DHL Bratislava
month (2026-05):

- costs are entered and displayed negative, revenues positive;
- stored values remain positive magnitudes with category kind carrying meaning;
- positive cost input and negative revenue input are rejected;
- every category row is dynamically summed, including the seeded EUR 200
  extraordinary-cost row;
- locking prevents edits and reopening requires an audited reason.

Try opening another office's financial month by URL, or POSTing to it: **403**.
The boundary covers finance mutations, not just the page.

Now switch to **Observer** and reopen Finance. This is the moment to show the
**executive dashboard** — a different page, Observer-only, with all three
offices rolled up side by side and a multi-series trend chart comparing them.
Manager sees one office; the owner sees the company.

For the CEO specifically, this is the slide that matters. On a freshly seeded
stack the three offices land clearly differently across Jan–Jul 2026:

| Office | Revenue | Net |
|---|---|---|
| Velký Meder | €165 300 | €46 100 |
| Győr | €117 730 | €24 690 |
| Dunajská Streda | €85 150 | €18 180 |

(Company net for Jan–Jul 2026 is therefore **€88 970** on **€368 180** revenue.
These are the exact seeded figures, verified against staging on 2026-07-26 —
quote them as read off the screen, not as approximations.)

Six contracts sit behind those three lines, each with its own shape — DHL
Bratislava grows steadily, Minit peaks over summer, WEBASTO dips and recovers,
Mevis 080 is flat, CARGO ramps fast, RLS 067 slowly declines. Say that out
loud: the roll-up is a real sum of differently-behaving contracts, not one
project restated.

The year view also carries **Nov–Dec 2025** for all six projects, so there is a
prior-year tail to compare against. Point out that 2025's smaller total
(~€90 900) is two months, not a bad year — per-month it runs ~€45k against
2026's ~€52.6k, which is the growth story.

Export CSV and show the detailed period, **office**, project, category, kind,
group, and signed-amount rows, followed by explicit per-office (`office_summary`)
and grand summaries. The export is office-scoped like everything else: the
manager's file contains Velký Meder only. The demo uses fictional numbers only.
`HV 202510.xlsx` remains a specification source, not seed data; its `202510`
filename versus `November 2025` sheet label is still an open client question.

### 6a. Using Finance: manual entry, end to end

Section 6 is the demo narrative. This is the operating guide — what a manager
actually does, and the two things that surprise people.

**Every figure is typed in. Nothing is derived.** Finance reads no data from
People, Equipment, Accommodation or anywhere else; `features/finance/` imports
nothing from those modules. The numbers on screen are exactly the numbers
somebody entered, taken from the client's own workbook. (An earlier fix list
recorded the opposite — that Finance pulls from headcount and inventory and
that this must be removed. It never did.)

**Step 1 — create the month.** Finance → the *Record month* form: pick the
project, type the year and month, and a first revenue and cost figure. Only
projects flagged as financially reportable appear, and only from your own
office(s).

**Step 2 — enter the categories.** Open the month. Every active finance
category is one input, labelled with its kind (cost or revenue) and grouped by
reporting group. Fill in what the workbook says and press save.

**Type the signs exactly as the spreadsheet has them.** Costs are entered
**negative**, revenues **positive**. A positive cost is *rejected* with
"Costs must be entered as negative amounts", and a negative revenue likewise.
That refusal is deliberate: it is the one thing standing between a cost and
being silently booked as revenue. Storage keeps positive magnitudes and the
category's kind carries the meaning, so the display re-signs them for you.

**The surprise: saving recalculates the month from the line items.** The
revenue and cost typed in step 1 are provisional. As soon as you save any
category, the month's totals are recomputed as the sum of its line items and
the step-1 figures are replaced. This is intentional — it is what makes the
spreadsheet's off-by-one impossible, because the total is always the sum of
everything present rather than a stored range. But if you type a headline
figure, then enter categories that sum to something else, **the categories
win**. Expect the number to change, and treat step 1 as a placeholder.

**Locking and reopening.** Lock makes the line items read-only. Reopening
requires a written reason and is audited — the reason is not optional and not
free of consequence, it appears in the audit log against your name.

**What you can read back.** The month page charts the net result by finance
group. The Finance page charts the monthly trend and a margin gauge. The year
view (`Finance → a year`) gives month-by-month results for comparison across
the year. Observers get a different, all-offices executive page instead.
CSV export carries period, office, project, category, kind, group and signed
amount, followed by per-office and grand summaries — scoped like everything
else, so a manager's file contains their own office only.

**Open with the client before they rely on this** (unresolved from the July
interview, and blocking a faithful mapping of their workbook):

1. **Which workbook columns are inputs and which are computed?** The category
   catalogue currently treats every row as an input. If some are meant to be
   derived from others, that changes the entry screen.
2. **Is the period October or November 2025?** The file is named `202510`
   while the sheet is labelled `November 2025`.
3. **Is one chart enough?** The client asked for a single monthly-result chart;
   the page currently carries more than that. Confirm before removing any.

### 7. Equipment issuing and deduction review

Sign in as Coordinator and open a fictional worker (e.g. **Olha**).

- In the Equipment panel, issue an item and point out the new neutral
  **Issued** badge next to it — issued items are now visually distinct from
  items under charge review, at a glance.
- Attempt **Flag unreturned** on the issued item. Confirm the badge changes
  to the warning-colored **Pending review** badge, showing the charge
  amount at the item's issued stock value.
- Switch to Manager and open **Equipment reviews**. The outstanding total is
  this office's, like every other queue. Show it and the queued item, then
  either:
  - **Approve charge** — back on the worker's page, the badge stays
    warning-colored ("Charge approved · amount"), signaling the recovery
    is recorded but not yet settled; or
  - **Waive** — the badge turns success-green ("Waived"), showing the
    review is resolved with no charge.

Talking point: approving only records the charge for manual recovery — no
payroll deduction is ever executed automatically. The badge coloring is the
whole point of this slice: issued (neutral), pending (warning, needs a
decision), waived (success, resolved) are now distinguishable without
reading the text.

### 8. Blacklist: the deliberate exception to office scoping

Worth showing explicitly, because it is the one place separation is *not*
applied — and that is a design decision, not an oversight.

Seeded **Ivan Zablokovaný** is blacklisted (approved), and **Diana Horvathova**
has a proposed case awaiting the manager's decision. Show the manager's
blacklist queue and decide Diana's case live.

Talking point: a candidate blocked at one office must be caught at all three,
so blacklist matching and visibility stay company-wide by design (ADR 0026).
Everything else — people, projects, stock, accommodation, finance — is walled
off per office; fraud protection deliberately is not.

## Supporting flow

**Activation now needs two people.** A coordinator completes the four readiness
pillars and clicks **Request activation** — which does *not* activate. A manager
of that office decides from the **Activations** tab, and cannot decide a request
they raised themselves. Worth showing: it is the separation-of-duties control a
client's auditor asks about, and the seed leaves one request waiting in
**Dunajská Streda** — so `manazer.ds@` has a queue item while `manazer@`'s
queue is empty, which demonstrates the queue is office-scoped too.

If time allows, show the existing trial-readiness-activation flow, compliance
alerts, role switching, and optional SMS. Compliance and notification queues are
office-scoped like the rest. Readiness now requires medical, gear, and the
accommodation decision only; transport is not a pillar for Jober.

## Deferred, do not present as delivered

- Office principals and staff invitations (ADR 0026 §3a): office membership is
  currently set by seed/admin, not self-service. Designed, not built.
- Cross-office equipment transfer: each office's warehouse is independent by
  decision; moving stock between them is a separate, later question.
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
- Uploaded files are stored on a persistent volume and served only through a
  permission check — never a public URL. Certificate scans follow the same
  visibility rule as date of birth and identifiers.
- The demo account password is published in a **public** repository. Rotate it
  before any external audience, or put staging behind access control.
- Confirm whether the finance period is October 2025 or November 2025.
- Confirm whether P&L opt-out is per project. (Office growth is no longer an
  open product question: the three licensed offices are a vendor-side ceiling
  per ADR 0026, so a fourth is a commercial request to SyncMetric, not a
  feature.)
- Confirm stock backdating, adjustments, valuation corrections, and month close.
- Confirm accommodation proration/payment semantics.
- Confirm whether the age warning ever blocks an action.
- Obtain the Art. 28 processor DPA and processors/retention list.
- Obtain Telegram channel access and bot administrator details for its later slice.
