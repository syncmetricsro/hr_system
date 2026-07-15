# Jober — customer demo runbook

> Thin-client pair: this runbook is **Jober** (port 8000). The CorvinumEU
> runbook is [corvinum-demo-runbook.md](corvinum-demo-runbook.md) (port 8001).

A presenter's script for a **~60-minute, end-to-end live demo** of the complete
solution. Present in **Slovak** (the default UI) and flip to **Hungarian** once to
show the live language switch. **Fictional data only** — say this up front.

Companion: [jober-local-demo.md](jober-local-demo.md) (how the runner works).

---

## Before the demo (prep + go/no-go)

1. **Get the latest code + full demo data — launch WITH Twilio creds** (Act 7 is
   a live act, not optional):
   ```bash
   doppler run --project hr_system --config dev -- scripts/dev_app.sh rebuild
   ```
   Doppler (project `hr_system`, config `dev`; run from the repo root) injects
   the Twilio credentials; the script builds the current image, starts
   PostgreSQL, migrates, and seeds `seed_demo` → `seed_people` → `seed_logistics` →
   `seed_questionnaire` → `seed_finance` → **`seed_demo_scenario`**. App at
   **http://localhost:8000**. *(If you forget Doppler, the SMS panel shows
   "not configured" — relaunch with
   `doppler run --project hr_system --config dev -- scripts/dev_app.sh up`;
   the seeded data survives.)* **One-time smoothness setup:** put the phone
   controlled test-recipient number into Doppler —
   `doppler secrets set DEMO_SMS_PHONE "+1..."` — and the seed gives that
   number to **Olha**, so the Act-7 SMS arrives where the audience can see it.
   It must be a recipient distinct from `TWILIO_FROM_NUMBER`; Twilio rejects
   sending a message from a number to itself (error `21266`).
2. **Go/no-go:** `scripts/playwright_e2e.sh` green (21 e2e); click the three
   headline screens (Finance, Blacklist queue, Reviews); **send one test SMS**
   from Olha's card to the Twilio Virtual Phone and see it Delivered — never
   let the demo be the first live send of the day.
3. **Rehearse once** end-to-end and time it.
4. **Know the confirmation modals:** every destructive step in the script
   (blacklist Approve/Reject, charge Approve/Waive, month Lock/Reopen, Exit)
   pops a modal describing the action with Cancel/Agree. Don't fumble it —
   *sell* it: "the system never lets you destroy something by mis-click."
5. Both demos can run **side by side** (Jober :8000, CorvinumEU :8001) —
   per-client session cookies mean they no longer log each other out, and
   sessions are 30-day rolling, so you stay signed in across the demo.

### Logins (password `demo-jober-2026` for all)
| Role | Email | Used in |
|---|---|---|
| Manager | `manazer@demo.jober.test` | Acts 1, 3, 8, 10 |
| Recruiter | `naborar@demo.jober.test` | Acts 2, 3 |
| Coordinator | `koordinator@demo.jober.test` | Acts 4, 5 |
| Observer | `pozorovatel@demo.jober.test` | Act 10 |

### Demo cast (seeded)
- **Olha Kovalenko** — Working, housed, has equipment (one flagged unreturned), a
  phone, and an expiring certificate.
- **Farrukh Tashkentov** — Trial day (record the outcome live in Act 4).
- **Tran Van Minh** — Available. **Diana Horvathova** — Available, has a **proposed
  blacklist case** to decide live. **Bohdan Melnyk** — Inactive (reason: Sick — shows as „Choroba“ in the SK UI).
- **Ivan Zablokovaný** — already **Blacklisted**; his hashed ID is
  **`SK-DEMO-BL-001`** — type it in Act 3 to trigger the re-entry match.

---

## Run of show (~60 min)

### 0 · Frame the problem (2m)
Today: spreadsheets, memory, and phone handoffs. Goal: **one reliable system** —
one profile, one status, one document state, one controlled path. *"Everything you
see is fictional test data."*

### 1 · Manager dashboard (5m) — `manazer`
Operational overview tiles (active projects, people by status, pending trials,
compliance, occupancy, equipment value). Flip the language switcher **SK → HU → SK**
to show live bilingual UI.

### 2 · Recruiter intake (8m) — `naborar`
People list + search. **Add a candidate**; in the *ID number (blacklist check)*
field enter a clean ID → saves with **no** warning. Show the hard-gated intake
questionnaire and sensitive-field visibility (recruiter sees their own candidate's
DOB/disability). Note: the recruiter can see a blacklist *flag* but **not** the
reason.

### 3 · Blacklist re-entry catch (6m) — **headline**
Still as `naborar`, add another candidate but enter **`SK-DEMO-BL-001`** →
**restricted warning**: created but flagged, activation blocked, no reason shown.
Talking points: **legitimate-interest** basis (fraud prevention / security vetting /
hiring); we match on an **HMAC — the raw ID number is never stored**; it's a
**warning, never a silent merge**. Switch to `manazer` → **Blacklist** tab → the
queue → open Diana's proposed case → *(manager sees the reason)* → **Approve** or
**Reject**. **Caveat to say out loud:** this runs on fictional data only; real use
is gated on the signed LIA + the written contract text.

### 4 · Coordinator activation (8m) — `koordinator`
**Field** queue → Farrukh → record trial outcome (pass) → **readiness gate**
(medical + gear required; accommodation + transport may be N/A) → **activate to
Working**. Then try to activate the Act-3 flagged candidate → **blocked** by the
open blacklist case (ties it together).

### 5 · Logistics (8m) — `koordinator` / `manazer`
Assign a room (**capacity enforced**). **Accommodation → Cost report** (`manazer`):
per-room €180 rate, occupancy, room-vs-assigned cost — **reporting only, nothing
deducted** *(Q1)*. Issue equipment to a worker; then the **unreturned-item** flow —
flag an item → **Reviews** queue (`manazer`) → **Approve charge / Waive**, no
automatic payroll deduction *(Q2)*.

### 6 · Compliance (4m)
**Compliance** list: Olha's forklift licence expiring in ~15 days, plus
missing/expiring-medical alerts — the manager's early-warning on papers.

### 7 · Messaging — live SMS + the Telegram question (6m)
Open Olha (she has a phone) → **Send SMS** from an approved template → show the
outbound log go **Sent/Delivered**. Talking points: templates are multilingual;
coordinators can only message their own project's workers; every send is
audited. Mention the caveat casually: *"still on the Twilio trial account, so
messages carry the trial prefix — the account upgrade removes it."*

**Then ask the Telegram question (bring a pen):** in round 4 you told us *no
Telegram bot* because you already run a **manual Telegram broadcast channel**.
Now that the messaging module is real — do you want that channel **integrated**?
Concretely: (a) keep it fully manual as today, (b) system-assisted broadcast
(compose in Jober with the multilingual templates + audit, post to your channel),
or (c) the full bot with per-worker opt-in and delivery status (what round 4
declined). Whatever they answer, write it down — it updates
`Jober_Messaging_Specs.md` and the round-4 record.

### 8 · Finance (8m) — `manazer`
**Finance** summary: company totals, per-project results, yearly rollup. Open the
DHLBA month → **line items** already entered → change one → **Save & recalculate** →
**net = revenue − cost**, all values **positive** *(Q4)*. **Lock** the month, then
**Reopen** with a reason (audited). Show the **group breakdown**
(transport/accommodation/overhead).

### 9 · Exit, recycle, inactive reasons (5m)
**Exit** a worker → to **Inactive** with a **catalog reason** *(Q5)*. **Recycle**
Bohdan → back to **Available**. **Reports → Inactive by reason** shows the named
breakdown.

### 10 · Oversight & RBAC (5m)
**Reports** + **CSV exports** (people/projects/finance). Then the **Audit** tab —
the append-only log of every sensitive action (who, what, whom, when, why),
filterable by actor/action/record/date; show the day's own demo actions in it
(the blacklist decision from Act 3, the month lock from Act 8). Log in as
`pozorovatel` (**Observer**): read-only — sees the finance summary **and the
Audit log** (oversight by design), but **not** the Reviews queue or blacklist
reasons. *"Hidden buttons are backed by real server-side checks; nothing in
the audit log can be edited or deleted."*

### 11 · Close (3m)
Recap: **all five of your questions are implemented** — accommodation cost *(Q1)*,
equipment-deduction review *(Q2)*, blacklist on legitimate interest *(Q3)*, positive
finance convention *(Q4)*, inactive reasons *(Q5)*. Then the caveats and the ask.

---

## Caveats (state these plainly)
- **Fictional data only** — the real-data/legal gate is not yet open.
- **Blacklist** — legitimate-interest basis; **LIA + written contract text pending**;
  matching is gated (`BLACKLIST_MATCHING_ENABLED`); never enter a real ID.
- **Translations** are AI-drafted — native SK/HU/UK review pending.
- **SMS** needs live Twilio (trial-number prefix until the account is upgraded).
- **Deployment** is the local demo image — **Dokku staging pending** on
  server/domain/DB names.
- **Finance category labels** to be reconciled against one real filled month.

## The ask (close with a decision)
1. **Green-light a real-data pilot** — this starts the legal/security gate work.
2. **Deliver the blacklist written text + LIA**, with the **retention period** and
   final **reason-category list**.
3. **Confirm the finance category labels** (share one filled month).
4. **Provide staging server/domain/DB names** so we can stand up Dokku.
5. **Arrange a native-speaker translation review** (SK/HU/UK).
6. **Decide the Telegram integration level** (from Act 7): manual channel as
   today / system-assisted broadcast / full bot with opt-in. Also: upgrade the
   Twilio account so SMS drops the trial prefix.
