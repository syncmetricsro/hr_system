# CorvinumEU PeopleOps — demo runbook

A presenter's script for a **~30-minute demo** of the CorvinumEU thin client.
Present in **Slovak** (HU switchable live). **Fictional data only** — say this
up front. Runs side-by-side with the Jober demo (port 8000) to show both
products from one platform.

## Before the demo

1. ```bash
   scripts/corvinum_app.sh up        # http://localhost:8001
   ```
   Builds the same production image Jober uses (only the settings module
   differs — a live talking point), migrates, seeds `seed_corvinum_demo`.
2. **Bring a phone with an authenticator app** (Google Authenticator, Aegis,
   FreeOTP…). The HR Admin login forces TOTP enrollment — this is Act 1, not
   an obstacle. *(Human prep: install the app beforehand; any TOTP app works.)*
3. Keep a second terminal on `scripts/corvinum_app.sh logs` — the payslip act
   shows the email arriving in the console backend.

### Logins (password `demo-corvinum-2026`)
| Role | Email |
|---|---|
| HR Admin (manager) | `hradmin@demo.corvinum.test` |
| Recruiter | `recruiter@demo.corvinum.test` |
| Coordinator | `coordinator@demo.corvinum.test` |
| Observer | `observer@demo.corvinum.test` |

### Demo cast (seeded)
- **Marek Skladník** — worker; issued safety boots (charged after leaving),
  a €100 open advance, €30 travel money; has an email on file.
- **Eszter Varga** — candidate with the activation checklist open.
- Companies **CV-ALFA** (Alfa Metallwerk) and **CV-BETA** (Beta Logistik).

## Run of show (~30 min)

1. **Login + 2FA (4m)** — log in as `hradmin` → forced TOTP setup → scan the
   QR-less otpauth secret with the phone app → verify. Talking point: §5.12
   security baseline; per-role enforcement is client config.
2. **Same platform, their brand (2m)** — dark corvinum.eu look, cobalt accent;
   flip SK↔HU. Optionally show Jober on :8000 in another tab: same code, two
   products.
3. **Checklist gate (5m)** — open Eszter → activation checklist panel (critical
   items open) → try to activate → **blocked with the item list** → tick the
   items (each records who/when) → activate.
4. **Equipment → ledger (5m)** — Marek's card: boots issued with value, flagged
   unreturned, charge approved → show the **linked PAY_DEDUCTION** in his
   ledger panel. No silent payroll magic: positive amounts, explicit effects.
5. **Ledger rhythm (6m)** — Ledger tab: record a cash advance → Thursday
   summary (14:00 cut-off, late entries roll to next Friday — proposed rule
   C-Q2, ask them to confirm) → 20th-to-20th cycle report → include cycle →
   locked entries only change via reversal → CSV export.
6. **Payslip (5m)** — record Marek's 2026-07 net pay → **Send encrypted PDF**
   → the one-time password appears once (read it out: "this is what you'd tell
   the worker by phone — it is never emailed") → show the email in the logs
   terminal → open the PDF attachment, wrong password fails, right one opens.
7. **Oversight (3m)** — Observer login: read-only; audit trail on Marek shows
   checklist ticks, ledger entries, the payslip send (no password anywhere).

## Caveats to state plainly
- Fictional data; the real-data/legal gate is not open. Translations are
  AI-drafted pending native review.
- The ledger/cycle rules and the payslip password channel are **built to
  proposed defaults** — confirm C-Q1…C-Q16
  (docs/product/corvinum-open-questions.md) before real use.
- Deployment pends server/domain/DB names (C-Q14).

## The ask (close with decisions)
1. Confirm the **ledger rules** (Thursday cut-off time, cycle boundary,
   partial-recovery question) and the **financial boundary in writing** (now
   including stored pay amounts, ADR 0023).
2. Decide the **payslip password channel** (phone / Messenger / in person).
3. Mandatory **document list** + retention periods (documents, pay data).
4. Confirm statuses/roles (HR Admin = manager mapping).
5. Provide **staging/production names** to unlock deployment.

## Where humans are needed (standing list)
- **Native SK/HU review** of all AI-drafted UI strings (both products).
- **Authenticator app** on the presenter's phone for Act 1.
- **SMTP credentials** (via Doppler) once payslip email should leave a real
  mailbox — console backend covers the demo.
- **CorvinumEU answers** to C-Q1…C-Q16; **legal** for retention/GDPR items.
