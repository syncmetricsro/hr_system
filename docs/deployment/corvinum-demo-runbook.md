# CorvinumEU PeopleOps — client demo walkthrough

> This is the presenter runbook for **CorvinumEU** at
> <http://localhost:8001>. The Jober walkthrough is
> [jober-demo-runbook.md](jober-demo-runbook.md) and runs independently on
> port 8000.

Use this as the source of truth for the client demonstration. The extended
walkthrough takes **25–30 minutes**; a ten-minute route is included below.
Present in Slovak and switch to Hungarian briefly. State at the start that all
names and records are fictional and that the real-data legal gate is not open.

## One-time local Doppler setup

The local Corvinum SMTP demo uses Doppler project `hr_system`, config
`dev_corvinum_demo`. Configure the CLI once from the repository root:

```bash
doppler configure set --scope . project=hr_system config=dev_corvinum_demo
```

This writes only to your local Doppler CLI configuration; it does not change
the committed [doppler.yaml](../../doppler.yaml) or add secrets to the
repository. After this setup, use `doppler run -- scripts/corvinum_app.sh ...`
for the real-SMTP rehearsal. For a Jober provider-backed session in the same
workspace, always select its configuration explicitly:

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
doppler run -- scripts/corvinum_app.sh rebuild
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
doppler run -- scripts/corvinum_app.sh up
scripts/corvinum_app.sh status
curl -fsS http://localhost:8001/healthz/
```

Delete the rehearsal authenticator entry. Do not log in as HR Admin again
before the live walkthrough, because the forced first-login TOTP setup is the
opening act.

### Presenter setup before the call

- Open <http://localhost:8001> in a fresh private browser window at desktop
  width. A private window avoids an old browser-local theme choice.
- Before sharing the screen, confirm the login card shows the Corvinum logo,
  **CorvinumEU PeopleOps** heading, and no Jober name or artwork.
- Have a phone with Aegis, Google Authenticator, FreeOTP, or another TOTP app.
- Open the controlled, non-personal test mailbox that will receive the payslip.
  Do not use a real worker's address while the real-data gate is closed.
- Keep this runbook and
  [the open client decisions](../product/corvinum-open-questions.md) open away
  from the shared screen.
- If role switching is planned, use a separate private browser profile for the
  Observer. One Corvinum browser session holds one signed-in account.

## Demo accounts

All four accounts use the password `demo-corvinum-2026`.

| Role | Email | Best use in the demo |
|---|---|---|
| HR Admin / Manager | `hradmin@demo.corvinum.test` | Main walkthrough; forced TOTP, all operational actions |
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

## Extended walkthrough — 25–30 minutes

### 1. Secure entry — 3 minutes

1. Sign in as `hradmin@demo.corvinum.test`.
2. On the forced two-factor setup screen, scan the QR code and enter the
   current six-digit code. The manual secret is the fallback.
3. Explain that Corvinum requires TOTP for the Manager/HR Admin role; this is a
   client policy on the shared platform, not merely a visual prompt.

Expected result: the Reports workspace opens after verification.

### 2. Reports as the interactive overview — 3 minutes

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

### 3. Add fictional personnel through guided intake — 4 minutes

1. Open **People → Add person**. The clean demo bootstrap publishes the shared
   three-step intake questionnaire automatically.
2. Enter this obviously fictional candidate so the client can follow the same
   person through the next steps:
   - first and last name: `Olena Demo`;
   - date/place of birth: `1995-05-14`, `Uzhhorod`;
   - phone: `+421 900 000 999`;
   - address/nationality: `Fiktívna 15, Komárno`, `Ukrajina`;
   - preferred language: `sk`;
   - disability: enter `nie`, then leave disability type empty.
3. Finish the questionnaire and show that the new person opens immediately in
   **Available** state with the HR Admin recorded as the intake owner.

Talking point: the questionnaire is versioned, validates every server-driven
step, handles conditional answers, and creates the personnel record only after
the final panel succeeds.

### 4. Guided activation checklist — 3 minutes

1. Continue on **Olena Demo**. If the intake was skipped, use
   **People → Eszter Varga** instead. Opening the record instantiates the
   checklist from the global template on first use.
2. Show the activation checklist and the message listing eight open critical
   items. Explain that critical approvals block activation.
3. Tick one item. Point out the immediate confirmation and the recorded staff
   identity beside the completed item.
4. Leave the remaining items open so the blocking state remains easy to see.

Do **not** promise a trial-day or readiness workflow in this client. Corvinum's
current configuration does not enable recruitment trials; the checklist is the
demonstrable approval control.

### 5. Work waiting for the user — 2 minutes

1. Now open the bell in the top-right. The checklist opened in the previous
   step supplies a real actionable problem for this fresh demo database.
2. Show the separate **Problems** and **Updates** groups, linked destinations,
   counts, refresh control, and per-user dismiss control.
3. Follow the activation-checklist problem back to the candidate. Following a
   link does not dismiss it; it remains until manually dismissed or the
   underlying condition is resolved.

Talking point: the first release refreshes after navigation and mutations, so
an idle browser makes no periodic requests.

### 6. Equipment charge with a ledger trail — 3 minutes

1. Go to **People → Marek Skladník** and find **Equipment**.
2. Show the safety boots, quantity, unit price in EUR, and approved charge.
3. Open **Ledger** and show the corresponding equipment deduction alongside
   the seeded 100.00 EUR advance and 30.00 EUR travel addition.

Talking point: equipment review and payroll effect are linked explicitly and
audited. Values are decimal EUR amounts; nothing is silently calculated or
deleted.

### 7. Ledger controls and safe consequences — 4 minutes

1. In **Ledger**, show the Thursday summary and its cut-off explanation.
2. In the cycle selector use **2026 / 7** and select **Show**.
3. Point out the per-person deduct, add, and net-effect columns and the detailed
   entries below.
4. Select **Include open entries in cycle**, show the consequence tooltip and
   confirmation dialog, then choose **Cancel**. This demonstrates the safety
   control without locking the rehearsal data.
5. Mention CSV export and the reversal-only correction path after an entry is
   locked.

Do not claim the proposed Thursday cut-off or 20th-to-20th cycle is final. Ask
the client to confirm C-Q2 and C-Q3.

### 8. Encrypted payslip delivery — 4 minutes

1. Open **Payslips** and record a payslip for Marek:
   - period: `2026-07`
   - net amount: `1450.00`
   - note: `Fictional client demo`
2. Before sending, edit Marek's email to a controlled, non-personal test inbox
   with a real deliverable domain. The seeded `@demo.corvinum.test` address is
   deliberately non-deliverable.
3. Select **Send encrypted PDF**.
4. Point out that the one-time PDF password is shown only in the on-screen
   confirmation and must be delivered separately by phone, Messenger, or in
   person. It is never included in the email or audit log.
5. Open the received message in the test inbox and use the separately displayed
   password to open its encrypted PDF attachment.

If the app was intentionally started without Doppler, the console backend
prints MIME output instead and does **not** offer a clickable attachment.

### 9. Audit and close — 3 minutes

1. Open **Audit** as HR Admin. Filter by Marek or by an action from this
   session, such as the checklist tick or payslip send.
2. Show that sensitive changes record the actor and before/after context while
   the one-time payslip password is absent.
3. If useful, switch to the Observer profile to show read-only ledger, export,
   and audit access without operational write controls.
4. Close on the decisions listed below.

## Ten-minute route

When time is tight, use only:

1. HR Admin login and forced TOTP.
2. Interactive Reports, one tooltip, and the SK/HU switch.
3. Add `Olena Demo` through intake, then tick one checklist item and show its
   notification.
4. Marek → equipment value → linked ledger deduction.
5. Ledger confirmation dialog, then Cancel.
6. Audit and the decision checklist. Skip payslip creation unless the client
   specifically asks about delivery.

## Current Corvinum feature boundary

The following are intentionally **not mounted** in CorvinumEU today and must
not be presented as hidden or unfinished menu items:

- recruitment trials;
- accommodation and room assignment;
- transport scheduling and trends;
- profitability/finance dashboards;
- SMS or worker-portal feedback.

Corvinum currently demonstrates people and projects, compliance, activation
checklists, equipment review, blacklist decisions, advances/deductions,
payslips, notifications, Reports, and Audit. These boundaries come from the
client feature configuration and remain subject to confirmed client scope.

## Recovery during rehearsal or the live call

| Symptom | Recovery |
|---|---|
| Nothing at port 8001 | Run `scripts/corvinum_app.sh status`, then `scripts/corvinum_app.sh up` |
| UI does not contain the latest changes | Run `scripts/corvinum_app.sh rebuild` before the call, then repeat the health check |
| TOTP code is rejected after a reset | Delete the old authenticator entry, return to login, and scan the newly generated QR code |
| Rehearsal data is already changed | Run `down`, then `up`; this recreates the disposable database and seed |
| Runner reports a missing SMTP variable | Confirm all seven `DJANGO_EMAIL_*` values exist in Doppler `hr_system/dev_corvinum_demo`; do not print their values |
| SMTP send fails | Confirm Marek has a deliverable controlled test address, then check `scripts/corvinum_app.sh logs`; FORPSI may also require the current country in its GeoIP allow-list |
| Console email appears instead of real delivery | Restart with `doppler run -- scripts/corvinum_app.sh up` |
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
