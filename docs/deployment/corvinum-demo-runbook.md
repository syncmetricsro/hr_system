# CorvinumEU PeopleOps — client demo walkthrough

> This is the presenter runbook for **CorvinumEU** at
> <http://localhost:8001>. The Jober walkthrough is
> [jober-demo-runbook.md](jober-demo-runbook.md) and runs independently on
> port 8000.

## Public staging presenter URL

The current fictional-data client demo is also deployed to
<https://corvinum-staging.80.211.210.46.sslip.io/sk/prihlasenie/> on
**syncmetric-prime**. Use this URL for the client presentation; use the local
`localhost:8001` stack for practice and disposable resets.

The staging app contains only the published Recruiter intake v4 and fictional
CorvinumEU seed scenario. Its separately scoped Doppler staging configuration
has successfully delivered one encrypted fictional payslip PDF to a controlled
test inbox. Never use a real worker address for either environment.

Use this as the source of truth for the client demonstration. The extended
walkthrough takes **45–50 minutes**; 20-minute and 10-minute routes are included
below. The extended route intentionally shows every currently mounted product
area, including read-only boundaries and confirmation controls. Do not lengthen
the call by improvising features that are listed as deferred.
Present in Slovak and switch to Hungarian briefly. State at the start that all
names and records are fictional and that the real-data legal gate is not open.

## Choose the environment before rehearsing

The two demo environments have different reset and authentication behavior:

| Environment | Data behavior | TOTP behavior | Use |
|---|---|---|---|
| Local `localhost:8001` | Disposable; `down` then `up` rebuilds the seeded database | Fresh reset shows setup and a new QR code | Full rehearsal, destructive-path practice, screenshots |
| Public staging | Persistent PostgreSQL data shared by rehearsals | Enrolled HR Admin normally shows verification, not setup | Client presentation and final acceptance |

Do not assume public staging is clean. Before presenting it, inspect the
candidate, equipment, ledger, and payslip lists and choose the appropriate
create-versus-show path described below. Never clear TOTP enrollment, delete
demo records, or reset staging immediately before a call unless that mutation
was planned, rehearsed, and verified.

## One-time local Doppler setup

The local Corvinum SMTP demo uses Doppler project `hr_system`, config
`dev_corvinum_demo`. Configure the CLI once from the repository root:

```bash
doppler configure set --scope . project=hr_system config=dev_corvinum_demo
```

**Set the recipient allowlist once, before any real-SMTP run.** Payslip delivery
consults `EMAIL_ALLOWED_RECIPIENTS` (ADR 0023 amendment); empty means
*unrestricted*, which is correct in production and dangerous on a demo box:

```bash
doppler secrets set EMAIL_ALLOWED_RECIPIENTS="<controlled-test-inbox>" \
  --project hr_system --config dev_corvinum_demo
```

With it set, a fictional worker record that happens to hold a real address is
refused before the mail server is contacted, no one-time password is generated,
and the attempt appears in Audit as `payslip.send_blocked`. Without it, the
runner prints a warning and `manage.py check` reports `mail.W001`. Procedure —
"remember to use the test mailbox" — is not a control; this is.

This writes only to your local Doppler CLI configuration; it does not change
the committed [doppler.yaml](../../doppler.yaml) or add secrets to the
repository.

**Always pass `--project` and `--config` explicitly anyway.** If the CLI scope
is missing or was cleared, a bare `doppler run --` silently falls back to
[doppler.yaml](../../doppler.yaml), which selects the **Jober `dev`** config —
and that config carries working SMTP credentials with **no**
`EMAIL_ALLOWED_RECIPIENTS`. The Corvinum demo would then start with
unrestricted real sending from the wrong mail account. Verified on 2026-08-03,
when exactly that scope was found unset.

So every real-SMTP rehearsal command below names its configuration in full. For
a Jober provider-backed session in the same workspace, do the same:

```bash
doppler run --project hr_system --config dev -- scripts/dev_app.sh up
```

## Rehearse, reset, and start clean

The demo database is disposable. `down` removes the Corvinum app, database,
and network; the next `up` creates and seeds a clean scenario. This also removes
the HR Admin's TOTP enrollment, so a fresh QR code appears at the live demo.

### Once after the final code changes

Build the current working tree into the local production image, start the
client with the dedicated Corvinum demo SMTP configuration, and verify its
health:

```bash
doppler run --project hr_system --config dev_corvinum_demo -- scripts/corvinum_app.sh rebuild
scripts/corvinum_app.sh status
curl -fsS http://localhost:8001/healthz/
```

The runner validates the SMTP configuration before starting and forwards its
seven `DJANGO_EMAIL_*` variables only to the web container. Migrations and demo
seeds remain on the console backend. Running the script without Doppler remains
a safe, secret-free fallback that prints messages to the application log.

Do the complete rehearsal, including TOTP and one payslip email. Keep the
authenticator entry clearly named **Corvinum rehearsal** so it is not confused
with the fresh entry used in front of the client.

### Immediately after rehearsal

Reset all mutations without rebuilding the already-tested image:

```bash
scripts/corvinum_app.sh down
doppler run --project hr_system --config dev_corvinum_demo -- scripts/corvinum_app.sh up
scripts/corvinum_app.sh status
curl -fsS http://localhost:8001/healthz/
```

Delete the rehearsal authenticator entry. Do not log in as HR Admin again
before the live walkthrough, because the forced first-login TOTP setup is the
opening act.

### Presenter setup before the call

- Open the public staging URL above in a fresh private browser window at
  desktop width. A private window avoids an old browser-local theme choice.
- Before sharing the screen, confirm the login card shows the Corvinum logo,
  **CorvinumEU PeopleOps** heading, and no Jober name or artwork.
- Have a phone with Aegis, Google Authenticator, FreeOTP, or another TOTP app.
- Decide whether step 1 will demonstrate first-time enrollment on a clean local
  stack or ordinary verification on persistent staging. Both are valid; do not
  promise a QR code when staging already has an enrolled device.
- Open the controlled, non-personal test mailbox that will receive the payslip.
  Do not use a real worker's address while the real-data gate is closed.
- Confirm `EMAIL_ALLOWED_RECIPIENTS` names that mailbox: `doppler secrets get
  EMAIL_ALLOWED_RECIPIENTS --project hr_system --config dev_corvinum_demo --plain`.
  A blank result means the demo can email any address a record happens to hold.
- Keep this runbook and
  [the open client decisions](../product/corvinum-open-questions.md) open away
  from the shared screen.
- If role switching is planned, use a separate private browser profile for the
  Observer. One Corvinum browser session holds one signed-in account.

### Automated preflight

The companion walkthrough checker validates the same numbered route using the
hash-pinned test dependency set. Run it only from the repository's approved
test environment, never after installing packages directly on the host:

```bash
python scripts/test_corvinum_walkthrough.py --url http://localhost:8001
```

The default check does not send provider-backed email. A real SMTP check is a
separate, explicit action and must use the controlled recipient, the approved
Doppler scope, and the script's opt-in described by `--help`. The checker
creates fictional candidates and catalogue records, so run it against local by
default. When staging is the target, record the run in
[corvinum-demo-verification-summary.md](corvinum-demo-verification-summary.md)
and review the resulting fictional records before presenting.

## Demo accounts

All four accounts use the password `demo-corvinum-2026`.

| Role | Email | Best use in the demo |
|---|---|---|
| HR Admin / Manager | `hradmin@demo.corvinum.test` | Main walkthrough; required TOTP, all operational actions |
| Recruiter | `recruiter@demo.corvinum.test` | Person intake and editing |
| Coordinator | `coordinator@demo.corvinum.test` | Checklists and equipment operations |
| Observer | `observer@demo.corvinum.test` | Read-only ledger, exports, and audit |

### Seeded fictional scenario

- **Marek Skladník** has an email address, safety boots size 43 valued at
  **35.00 EUR**, an approved unreturned-equipment charge, a **100.00 EUR** open
  advance, and a **30.00 EUR** travel addition.
- **Eszter Varga** is a candidate with a nine-item activation checklist. Eight
  items are critical and initially open.
- **Alfa Metallwerk / CV-ALFA** and **Beta Logistik / CV-BETA** are the two
  partner projects.

## Extended walkthrough - 40–45 minutes

### 1. Secure entry and client isolation - 3 minutes

1. Sign in as `hradmin@demo.corvinum.test`.
2. On a clean local stack, scan the QR code on the required two-factor setup
   screen and enter the current six-digit code. On persistent staging, enter
   the current code on the verification screen using the already enrolled
   **Corvinum staging** authenticator entry.
3. Explain that Corvinum requires TOTP for the Manager/HR Admin role; this is a
   client policy on the shared platform, not merely a visual prompt.
4. Point out the Corvinum logo, dark shell, Slovak URL, and Corvinum-specific
   session. Jober is deployed separately and cannot leak navigation or data
   into this client.

Expected result: the Reports workspace opens after verification.

### 2. Reports as the interactive overview - 3 minutes

1. Start on **Reports**. Point out that the old passive overview was merged
   into this operational dashboard.
2. Hover an interactive metric to show its action-oriented tooltip, then open
   **People** from the metric and return to Reports.
3. Switch **Dark → Light → Dark** and **Slovak → Hungarian → Slovak** from the
   sidebar footer. Theme preference is browser-local; language changes the URL
   and the rendered interface.
4. Resize or collapse the sidebar briefly only if it helps the conversation.

Talking point: cards and lifecycle rows are drill-downs, not decorative
statistics; each opens a relevant list or filter.

### 3. Projects, assignments, and approved exports - 3 minutes

1. Open **Projects** and filter Active versus Inactive. Explain that the two
   seeded partner companies are represented as projects: **Alfa Metallwerk**
   (`CV-ALFA`) and **Beta Logistik** (`CV-BETA`).
2. Open Alfa Metallwerk. Show its code, office/partner metadata when present,
   responsible coordinators, financial-reporting eligibility, and linked
   worker list.
3. Return to Projects and point out **Export**. Manager and Observer can export
   approved people/project data; Coordinator and Recruiter cannot.
4. Do not claim full project create/edit/archive controls. Current project
   navigation and assignment are working; broader project CRUD remains a
   separately tracked product increment.

Talking point: project responsibility scopes coordinator actions, while core
records and permissions remain shared across clients without sharing data.

### 4. Add fictional personnel through guided intake - 4 minutes

1. Open **People -> Add person**. The clean demo bootstrap publishes Recruiter
   intake **v4**, a shared three-step questionnaire, automatically.
2. Enter this obviously fictional candidate so the client can follow the same
   person through the next steps:
   - first and last name: `Olena Demo`;
   - date/place of birth: `1995-05-14`, `Uzhhorod`;
   - phone: `+421 900 000 999`;
   - email: optional — leave it blank for the ordinary intake, or use the
     controlled test inbox only when rehearsing the later payslip-email step;
   - address/nationality: `Fiktívna 15, Komárno`, `Ukrajina`;
   - preferred language: `sk`;
   - disability: enter `nie`, then leave disability type empty.
   - leave the optional **ID number (blacklist check)** empty for this ordinary
     intake; the later blacklist demonstration supplies its own fictional ID.
3. Finish the questionnaire and show that the new person opens immediately in
   **Available** state with the HR Admin recorded as the intake owner.
4. Return briefly to **People**. Search for `Olena`, filter by Available, and
   point out the approved CSV export. Open the new record again.
5. On the person card distinguish operational details from restricted personal
   data. Explain that sensitive visibility is server-enforced for managers,
   observers, the owning recruiter, and the responsible coordinator.

Talking point: the questionnaire is versioned, validates every server-driven
step, handles conditional answers, and creates the personnel record only after
the final panel succeeds.

### 5. Schedule and record a trial day - 3 minutes

1. Continue on **Olena Demo**. In the **Next step** panel, select **Alfa
   Metallwerk** and choose a fictional arrival time tomorrow at `08:00`.
2. Select **Schedule trial**. Explain that recruiters, coordinators, and
   managers can schedule; the event records both the destination and arrival
   time.
3. Open **Trials**, find Olena’s pending trial, and record **Pass** as HR
   Admin. A coordinator can record the outcome too; an Observer cannot.
4. Return to Olena. The record is now in **Trial day** and the readiness panel
   is available for the approved project.

Talking point: a passed trial does not activate a worker by itself. It moves
the person into the documented readiness/approval workflow.

### 6. Readiness, activation checklist, and blocked activation - 4 minutes

1. On Olena’s record, show the activation checklist and the message listing
   eight open critical items. Explain that critical approvals block activation.
2. Tick one item. Point out the immediate confirmation and the recorded staff
   identity beside the completed item.
3. Leave the remaining items open so the blocking state remains easy to see.
4. In Readiness set Medical and Gear to complete, and Accommodation to **Not
   applicable** with a short reason. Transport is absent because Corvinum has
   that feature disabled.
5. Select **Activate (Working)** while critical checklist items remain open.
   Expected result: activation is rejected safely and the record remains in
   Trial day. Do not complete every item during the main route.

Talking point: passing a trial, completing readiness, and approving a checklist
are separate auditable decisions. No browser-only state can bypass the
server-side activation gates.

**If asked about small offices** (ADR 0031, and worth raising unprompted since
CorvinumEU runs with a single HR Manager): the trial day can be skipped. On an
Available person, a manager gets **Activate without a trial day** — pick a
project and readiness opens directly, with the person still Available. This
waives the *trial*, not readiness: medical and gear must still be complete, so
the entry medical certificate is never skipped. The same manager may then decide
their own activation request; the queue row says **your own request** and the
audit event records `self_approved`. Coordinators hold neither the waiver nor
the decision.

### 7. Work waiting for the user - 2 minutes

1. Now open the bell in the top-right. The checklist opened in the previous
   step supplies a real actionable problem for this fresh demo database.
2. Show the separate **Problems** and **Updates** groups, linked destinations,
   counts, refresh control, and per-user dismiss control.
3. Follow the activation-checklist problem back to the candidate. Following a
   link does not dismiss it; it remains until manually dismissed or the
   underlying condition is resolved.

Talking point: the first release refreshes after navigation and mutations, so
an idle browser makes no periodic requests.

### 8. Compliance and occupational certificates - 3 minutes

1. Open **Compliance** from the navigation or Reports drill-down.
2. Show missing, expiring, and expired metadata alerts and follow one alert to
   its person record.
3. As HR Admin, open a fictional person's **Occupational certificates** panel.
   From `tests/fixtures/manual_uploads/certificates/`, select Forklift and
   upload `allowed-forklift-front.png` plus `allowed-forklift-back.png`; use
   `DEMO-FL-001`, issue `2026-07-01`, and expiry `2027-07-01`. Save and open
   both private file links.
4. If the PDF path matters to the audience, add the fictional crane certificate
   using `allowed-crane-certificate.pdf` as the only file. A PDF cannot have a
   separate back image.
5. Switch the Corvinum UI between Slovak and Hungarian and show that the manual
   category labels translate. The scan itself may be written in either
   language: it uploads as pixels/PDF pages, but the system does not detect its
   language, read its fields, or infer its certificate type.
6. Show that renewal preserves history and that Audit records the mutation.
7. Explain the enforced boundary: no identity, birth, residence, financial, or
   medical scans; those are metadata-only/prohibited. A client request for them
   becomes a separately scoped Secure Document Vault project.
8. Note that the exact metadata catalogue and retention periods remain
   client/legal decisions C-Q7, C-Q13, C-Q16, and C-Q18.

The full positive, negative, deliberate-mislabel, cleanup, and multilingual
matrix is in
[`certificate-upload-acceptance.md`](certificate-upload-acceptance.md). The
mislabel probe is internal-only and must not be performed during the client
walkthrough. Before presenting worker photos, also run the shared
[`avatar-upload-acceptance.md`](avatar-upload-acceptance.md) matrix with the
tracked fictional avatar fixtures.

Talking point: the occupational workflow is working in both thin clients, but
real documents remain behind the repository's DPA, hosting, backup, retention,
permissions, and security-review gate.

### 9. Equipment custody, review, and ledger trail - 4 minutes

1. Open **Equipment catalogue**. As HR Admin, add a fictional example such as
   `High-visibility vest`, size `L`, price `8.50 EUR`, active. Show that the
   new item is immediately available in personnel equipment dropdowns.
2. Explain that managers can search, edit, or deactivate catalogue entries;
   coordinators can issue/return items but cannot alter the catalogue.
3. Go to **People → Marek Skladník** and find **Equipment**.
4. Show the safety boots, quantity, unit price in EUR, and approved charge.
5. Open **Equipment reviews**. Explain that unreturned items require a manager
   decision. The seeded boots are already approved, so the queue may be empty;
   use Marek's person card and ledger as the evidence trail rather than creating
   another charge during the call.
6. Open **Ledger** and show the corresponding equipment deduction alongside
   the seeded 100.00 EUR advance and 30.00 EUR travel addition.

Talking point: equipment review and recovery are linked explicitly and audited.
Approval records a recovery entry; it does not mutate wages automatically.
Values are Decimal EUR amounts and nothing is silently deleted. Corvinum uses
the per-person custody/value view, not Jober's warehouse-stock report.

### 10. Ledger entry, exports, and safe consequences - 5 minutes

1. In **Ledger**, use **Record entry** to add a small fictional travel/fuel
   addition for Olena: project **Alfa**, entry type **Pay addition**, category
   **Travel / fuel**, amount `12.50 EUR`, and note `Demo only`. Point out that
   the amount is stored positive while entry type determines whether it adds
   to or deducts from pay.
2. Show the Thursday summary, cut-off explanation, and CSV download.
3. In the cycle selector use the current cycle end year/month and select
   **Show**. If rehearsing a historical seeded state, use the cycle containing
   Marek's entries instead.
4. Point out the per-person deduct, add, and net-effect columns and the detailed
   entries below.
5. Download the cycle CSV only if it helps the bookkeeping discussion.
6. Select **Include open entries in cycle**, show the consequence tooltip and
   confirmation dialog, then choose **Cancel**. This demonstrates the safety
   control without locking the rehearsal data.
7. Mention the cancellation path for open entries and reversal-only correction
   path after an entry is locked.

Do not claim the proposed Thursday cut-off or 20th-to-20th cycle is final. Ask
the client to confirm C-Q2 and C-Q3.

### 11. What was taken off the gross wage - 8 minutes

**This is the section the client asked for, and the one to rehearse.** Changed
2026-08-04: the overview now shows the office's own ledger deductions and an
**After deductions** column. Do the arithmetic on screen, not in your head.

The line to hold throughout: **After deductions is not net pay.** It is gross
minus what *this office* recorded — advances, equipment, damage. Tax and levies
are not in it. That is exactly why the recorded net payslip keeps its own
column: so the two can be compared instead of confused.

Eszter's seeded figures, to check before you start:

| Calendar month | Recorded gross wage | Recorded net payslip |
|---|---:|---:|
| `2026-06` | `1920.00 EUR` | `1450.00 EUR` |
| `2026-07` | `2050.00 EUR` | `1540.00 EUR` |

**Check which cycle is open before the call.** The entries below are refused if
their date falls in a cycle that has already been settled, and on a
long-running staging database most cycles have been. Verified on staging
2026-08-04: `2026-07` and `2026-08` are settled, **`2026-06` is open**, which
is why the walkthrough below uses June. Confirm before presenting:

```bash
ssh syncmetric-prime-dokku "run corvinum-staging python manage.py shell -c \"import datetime as dt; from features.advances.services import cycle_is_settled, cycle_for; [print(d, cycle_for(d), 'settled:', cycle_is_settled(d)) for d in (dt.date(2026,6,10), dt.date(2026,6,25), dt.date(2026,7,8))]\""
```

Expected today, and the reason the walkthrough uses June:

```
2026-06-10 (2026, 6) settled: False   <- the dates below are accepted
2026-06-25 (2026, 7) settled: True    <- June date, JULY cycle, refused
2026-07-08 (2026, 7) settled: True    <- refused on purpose in step 8
```

The script has to be an **argument** (`shell -c "..."`), not piped in. `dokku run`
over the restricted account does not forward stdin, so a heredoc reaches nothing:
the shell starts, reads EOF, prints `50 objects imported automatically` and exits
with no output at all. It reads as success. Read-only either way - the check is a
single `SELECT ... EXISTS` and writes nothing.

If June has since been settled too, pick any month where the check prints
`False` and adjust the figures — the arithmetic is what matters, not the month.

1. Open **Eszter Varga** and scroll to **Wage and payslip overview**. Four
   columns: gross wage, ledger deductions, after deductions, net payslip.
   Ledger deductions is empty for both months and **After deductions equals the
   gross figure** — nothing has been taken off yet. Say that out loud; it is
   the "before" picture and the contrast is the whole point. (Eszter carries no
   ledger entries in the seed, which is what makes her the right subject.)
2. Open **Ledger** and record a cash advance against Eszter:
   - Entry type **Pay deduction**, category **Cash advance**, amount `200`
   - **Entry date `2026-06-08`** — the field that makes this demonstrable. It
     decides both the settlement cycle and the calendar month the entry shows
     under. Without it every entry would land on today and June could not be
     shown at all.
   - Note: `advance paid in cash on site`
3. Record a second entry the same way: **Pay deduction**, category
   **Equipment**, amount `50`, entry date `2026-06-15`.

   **Keep both dates on the 1st–20th.** A date of 21–30 June is still the June
   *calendar month* on this table, but it settles in the **July** cycle — which
   is closed, so the entry would be refused. That split trips people up; it is
   worth understanding before you are in front of the client, and it is a fair
   thing to show deliberately in step 8.
4. Return to Eszter's profile. The June row now reads:

   | Month | Gross | Ledger deductions | After deductions | Net payslip |
   |---|---:|---:|---:|---:|
   | `2026-07` | `2050.00` | — | `2050.00` | `1540.00` |
   | `2026-06` | `1920.00` | `250.00` | `1670.00` | `1450.00` |

   `1920.00 − 250.00 = 1670.00`. Point at the three figures in order. The July
   row is untouched, which shows the entry date really did place the money in
   June.
5. **Now name the remaining gap, before the client does.** After deductions is
   `1670.00` and the recorded payslip is `1450.00`. Say that the difference is
   **whatever payroll applied, and that this system does not calculate it** —
   the product shows what the office controls and stops there.

   Do **not** attribute the difference to tax and levies, or to any other
   specific cause. Both figures here are fictional fixtures entered by hand and
   the `220.00` is arbitrary; naming a cause invites "why exactly 220?", which
   has no answer. The honest sentence is about what the system does, not about
   what the number means.
6. If asked to close that gap: it needs the client's statutory rules and the
   deferred wage workbook (`radonak.xlsx`), and it is a payroll-calculation
   scope decision (C-Q6, C-Q17), not a switch to flip. Do not promise it.
7. **Ask the client which convention they enter.** The net figure is stored and
   printed exactly as typed — the system never computes or checks it — so
   whether an advance already handed over in cash is *inside* that number is
   the office's habit, not a product rule. It matters: the PDF the worker
   receives is labelled **Net amount paid**, which reads as *what reached your
   account*, and that label is only correct if they enter the post-advance
   figure. Record the answer against C-Q17.
8. **Show the guard — it demonstrates well and takes ten seconds.** Record a
   third entry with entry date **`2026-07-08`**, inside the already-settled
   July cycle. It is refused with a message naming the cycle, and nothing is
   written. Say why: a settled cycle has already been paid out, so money cannot
   be quietly added to it after the fact; corrections from that point are
   reversals, which leave the original visible. This is a good place to make
   the calendar-month versus 21st-to-20th distinction concrete.

Note on periods, which reliably comes up: gross wage, payslip and the
deductions column are all keyed by **calendar month**. The settlement cycle is
the separate 21st-to-20th window. An entry dated the 25th of July therefore
appears in the July row here while settling in the August cycle — deliberate, so
this table's four columns always mean the same period.

A missing source shows as `—` and is never treated as zero: with no gross wage
recorded, **After deductions is blank rather than negative**.

### 12. Encrypted payslip delivery - 4 minutes

1. Open **Payslips** and inspect Eszter's same seeded `2026-06` and `2026-07` net
   values. Point out the separate **Issue date** column: the fictional June
   payslip was issued on `2026-07-05`, while the July payslip was issued on
   `2026-07-20`. The issue date describes the document and does not redefine
   its calendar-month payroll period. This also confirms that the person
   overview reads the payslip record; it does not copy or calculate the
   displayed number.
2. If creation itself must be demonstrated, use a different fictional person
   and an unused period. The **Payslip date (optional)** field accepts any
   valid date independently of the selected period. Leave it blank once to
   demonstrate that the server records the local creation date. Do not
   overwrite or duplicate Eszter's numeric checkpoint rows.
3. On persistent staging, if the intended Marek/period row already exists, do
   not create it again. Use that row's **Resend (new password)** action. The
   database allows one payslip per person and period.
4. Before sending, edit Marek's email to a controlled, non-personal test inbox
   with a real deliverable domain. The seeded `@demo.corvinum.test` address is
   deliberately non-deliverable.
5. Select **Send encrypted PDF** or **Resend (new password)**.
6. Point out that the one-time PDF password is shown only in the on-screen
   confirmation and must be delivered separately by phone, Messenger, or in
   person. It is never included in the email or audit log.
7. Open the received message in the test inbox and use the separately displayed
   password to open its encrypted PDF attachment.
8. **Say what the PDF contains before they read it.** Four lines: worker,
   period, `Net amount paid`, and an optional note. It does **not** itemise the
   advance or the equipment deduction you recorded in section 11 — those live on
   the internal ledger and the office-facing pay overview only.

   Expect the question *"so can the worker see what was deducted?"*. The answer
   is **not today, and it needs your decision** (C-Q21). Do not promise it in
   the room: it depends on the C-Q20 answer, because if the entered net is
   already post-advance then printing the advance again would understate the
   pay. Offer the shape instead — gross, the deductions the office recorded, a
   subtotal, then the recorded net stated separately — and take the answer away
   in writing.

**Resend** delivers a newly encrypted PDF to the same address as the last
successful delivery and displays a new one-time password. If the send fails,
the application keeps the existing delivery record and shows an in-app error;
it never exposes a server-error page.

If the app was intentionally started without Doppler, the console backend
prints MIME output instead and does **not** offer a clickable attachment.

### 13. Audit filters and person history - 3 minutes

1. Open **Audit** as HR Admin. Filter by Marek or by an action from this
   session, such as the checklist tick or payslip send.
2. Show that sensitive changes record the actor and before/after context while
   the one-time payslip password is absent.
3. Return to Olena and show the person-level History sequence: intake, trial,
   status, and related operational events. Distinguish this concise timeline
   from the global append-only audit.
4. Explain that actor-complete person history is still being refined; the
   global Audit remains the authoritative actor record in this build.

### 14. Observer RBAC and close - 3 minutes

1. In a separate private browser profile, sign in as
   `observer@demo.corvinum.test`.
2. Open People, Projects, Gross wages, Payslips, Ledger, exports, and Audit.
   Confirm read visibility and the same four seeded wage/payslip amounts.
3. Confirm that Add person, checklist mutation, catalogue management, ledger
   entry, payslip management, blacklist decisions, and operational lifecycle
   controls are absent.
4. Close on the decisions listed below and state that the client policy grants
   actions server-side; hiding buttons is not the authorization boundary.

## Optional manager demonstration — blacklist and re-entry protection

Use this only after the main route, with **fictional** data and HR Admin signed
in. It is a manager-controlled safety workflow, not an automatic deletion or
silent deduplication feature.

### What the current product does

1. Open a fictional person created during this rehearsal, such as **Olena
   Demo**.
2. In the **Blacklist** panel, select a neutral demonstration category, enter
   the fictional reason `Demo only — manager review required`, and enter the
   fictional identifier `CE-DEMO-BL-2026-001` in **ID number (optional,
   hashed)**.
3. Choose **Propose blacklist**. This creates a proposed case; it does not yet
   change the person’s status.
4. Open **Blacklist** in the navigation. Show the proposed case, then choose
   **Approve** and enter `Fictional approval for walkthrough` as the decision
   reason.
5. Return to the person. Expected result: the person is **Blacklisted**, the
   case is approved, and activation is blocked. Explain that the raw ID is not
   stored: the application retains only a keyed HMAC fingerprint, its type,
   key version, and expiry.
6. Open **Audit** and filter for the fictional person or blacklist action.
   Show the proposal, decision, actor, and timestamp. Do not display or claim
   to store the raw identifier.

### Archive and re-enter the fictional person — 4 minutes

There is deliberately no destructive person-delete control. **Archive person**
hides the record from the operational People list but retains the case,
fingerprint, and audit history. It is not GDPR erasure and cannot bypass
blacklist protection.

1. On the original approved person, open **Archive person**, enter
   `Fictional re-entry demonstration`, confirm the consequence dialog, and
   submit. The original record disappears from People but remains Blacklisted
   for authorized audit/review purposes.
2. Start **People → Add person** and use a visibly different fictional name,
   for example `Olena Re-entry`, so the audience can distinguish the two
   records.
3. Complete Identity and Contact with fictional values. On the final
   **Compliance** panel, enter `nie` for disability, then enter the **same**
   fictional identifier `CE-DEMO-BL-2026-001` and choose `national_id` as the
   ID type. Finish intake.
4. Expected result: the new record is created for review, a **proposed
   blacklist match** is raised, and activation remains blocked. The system does
   not merge the two people and does not automatically blacklist the new one.
5. The manager decides the new proposal in the Blacklist queue. The queue's
   **Matched via** row shows which fingerprint matched (ID, or the composite
   below). An approval blacklists the new record; a rejection closes only that
   new proposal. The original approved case remains until a manager explicitly
   removes it with a reason.

Optional composite variant (no ID code): repeat the re-entry with the ID field
left empty, but re-use the original fictional first name, surname, and date of
birth in any spelling or order (diacritics and swapped name order still match)
and enter the same fictional **Mother's maiden name (blacklist check)** on the
Compliance panel. The same proposed-match warning appears, labelled with the
composite fingerprint type. The maiden name is hashed transiently and never
stored.

Talking point: only keyed HMAC fingerprints are retained — one for the optional
ID code and one for the name + birth date + mother's-maiden-name composite. No
raw identifier or maiden name is ever stored as an intake answer, audit value,
or person field. Re-entering only a name, birth date, phone, or email — without
the maiden name — deliberately does not create a blacklist match.

## Twenty-minute route

Use this route when the audience wants breadth but not every mutation:

1. Sign in with required TOTP, identify the isolated Corvinum shell, and open
   Reports.
2. Show one report drill-down, the SK/HU switch, Projects, and project-scoped
   worker links.
3. Create Olena through intake v4, schedule and pass the trial, tick one
   checklist item, and demonstrate blocked activation.
4. Open the notification and compliance surfaces and follow one issue to the
   person record.
5. Show Marek's equipment custody, approved recovery, and linked ledger entry.
6. Show Thursday/cycle summaries, CSV availability, and the cycle confirmation
   dialog; choose Cancel.
7. Show Eszter's calendar-month gross wage and net payslip side by side, quote
   the four expected fixture values, and explain why no net is calculated.
8. Show the matching payslip row and explain encryption/password separation
   without sending unless provider delivery is an agreed objective.
9. Filter Audit by an action from the session and close with Observer read-only
   access and the open-decision list.

## Ten-minute route

When time is tight, use only:

1. HR Admin login and required TOTP setup or verification, depending on the
   selected environment.
2. Interactive Reports, one tooltip, and the SK/HU switch.
3. Add Olena Demo through intake, schedule and pass one trial, then tick one
   checklist item and show its notification.
4. Marek -> equipment value -> linked ledger deduction.
5. Ledger confirmation dialog, then Cancel.
6. Eszter's `2026-07` gross `2050.00 EUR` beside recorded net `1540.00 EUR`,
   with the source-versus-calculation boundary stated explicitly.
7. Audit and the decision checklist. Skip payslip creation unless the client
   specifically asks about delivery.

## Current Corvinum feature boundary

The following are intentionally **not mounted** in CorvinumEU today and must
not be presented as hidden or unfinished menu items:

- accommodation and room assignment;
- transport scheduling and trends;
- profitability/finance dashboards;
- SMS or worker-portal feedback.

Corvinum currently demonstrates people and projects, recruitment trials,
compliance, activation checklists, equipment review, blacklist decisions,
advances/deductions, calendar-month gross wages, recorded net payslips,
notifications, Reports, and Audit. These
boundaries come from the client feature configuration and remain subject to
confirmed client scope.

## Recovery during rehearsal or the live call

| Symptom | Recovery |
|---|---|
| Nothing at port 8001 | Run `scripts/corvinum_app.sh status`, then `scripts/corvinum_app.sh up` |
| UI does not contain the latest changes | Run `scripts/corvinum_app.sh rebuild` before the call, then repeat the health check |
| Local TOTP code is rejected after a reset | Delete the old local authenticator entry, return to login, and scan the newly generated QR code |
| Staging opens verification but no enrolled authenticator is available | Stop and coordinate a deliberate staging TOTP reset; do not improvise deletion during the call |
| Local rehearsal data is already changed | Run `down`, then `up`; this recreates the disposable database and seed |
| Staging already contains Olena/catalogue/payslip records | Use a visibly unique fictional suffix, show the existing row, or use Resend; never assume staging is disposable |
| Runner reports a missing SMTP variable | Confirm all seven `DJANGO_EMAIL_*` values exist in Doppler `hr_system/dev_corvinum_demo`; do not print their values |
| SMTP send fails | Confirm Marek has a deliverable controlled test address, then check `scripts/corvinum_app.sh logs`; FORPSI may also require the current country in its GeoIP allow-list |
| Console email appears instead of real delivery | Restart with `doppler run --project hr_system --config dev_corvinum_demo -- scripts/corvinum_app.sh up` |
| Ledger entry refused, naming a cycle | That cycle is settled; pick a date in an open one. Check with the `cycle_is_settled` snippet in section 11. Never reopen a settled cycle to make a demo work |
| Payslip creation reports a duplicate | Select the existing person/period row and use Resend, or choose an unused fictional period |
| Wage and payslip figures appear inconsistent | Verify the four fictional fixture values above, then confirm the two source records and period labels; do not infer statutory deductions from the difference |
| Certificate fixture is absent or its checksum fails | Restore `tests/fixtures/manual_uploads/` from a clean checkout and rerun `sha256sum --check`; never substitute a real worker document |
| A foreign-language certificate uploads but nothing is extracted | Expected: the base product stores manually classified safe files and has no OCR, language detection, translation, or field extraction |
| A prohibited-looking fixture passes when labelled Forklift | Expected current limitation of the internal mislabel probe; immediately use the Manager-only purge and retain the audit event |
| A risky button is reached accidentally | Use **Cancel** in the confirmation dialog; do not include or settle the cycle during the main walkthrough |

## Decisions to request from the client

1. Confirm the lifecycle/status model and HR Admin-to-Manager role mapping
   (C-Q1, C-Q9).
2. Confirm the Thursday cut-off, cycle boundary, and correction rules
   (C-Q2–C-Q5).
3. Confirm the financial boundary and the payslip password delivery channel
   (C-Q6, C-Q15).
4. Supply the mandatory document list and legally approved retention periods
   for compliance, ledger/equipment history, and pay data (C-Q7, C-Q13, C-Q16).
5. Confirm Slovak/dark defaults and provide staging/production names
   (C-Q8, C-Q14).

See [corvinum-open-questions.md](../product/corvinum-open-questions.md) for the
full C-Q1–C-Q16 register.

## Mandatory caveats

- Fictional data only; the GDPR/real-data gate is not open.
- SK/HU translations require native review before production.
- Ledger and cycle behavior implements reversible proposed defaults, not
  confirmed payroll policy.
- SMTP/provider-backed testing must use Doppler project `hr_system`, config
  `dev_corvinum_demo`, through the one-time CLI setup and exact `doppler run`
  commands above. Starting without Doppler stays secret-free and uses console
  email.
- Production still depends on approved domains, database names, secrets,
  backups, retention decisions, and security/legal sign-off.
