# Customer demo runbook — Jober

A presenter's script for a **~60-minute, end-to-end live demo** of the complete
solution. Present in **Slovak** (the default UI) and flip to **Hungarian** once to
show the live language switch. **Fictional data only** — say this up front.

Companion: [local-demo.md](local-demo.md) (how the runner works).

---

## Before the demo (prep + go/no-go)

1. **Get the latest code + full demo data:**
   ```bash
   scripts/dev_app.sh rebuild
   ```
   This builds the current image, starts PostgreSQL, migrates, and seeds
   `seed_demo` → `seed_people` → `seed_questionnaire` → `seed_finance` →
   **`seed_demo_scenario`** (fills every module screen). App at
   **http://localhost:8000**.
   - Optional live SMS (Act 7): `doppler run -- scripts/dev_app.sh rebuild` so
     Twilio creds reach the app.
2. **Go/no-go:** `scripts/playwright_e2e.sh` should be green (16 e2e), then click
   the three headline screens (Finance, Blacklist queue, Reviews).
3. **Rehearse once** end-to-end and time it.

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
  blacklist case** to decide live. **Bohdan Melnyk** — Inactive (reason: Sick).
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

### 7 · Messaging (optional, 4m)
If launched with Doppler/Twilio: open Olha (she has a phone) → **Send SMS** from an
approved template → shows Sent/Delivered + the outbound log. Fallback: show the
templates and message history.

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
**Reports** + **CSV exports** (people/projects/finance). A person's **append-only
audit trail**. Then log in as `pozorovatel` (**Observer**): read-only — sees the
finance summary but **not** the Reviews queue or blacklist reasons. *"Hidden
buttons are backed by real server-side checks."*

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
