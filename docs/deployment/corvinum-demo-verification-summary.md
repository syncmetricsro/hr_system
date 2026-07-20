# CorvinumEU Demo Walkthrough Verification Summary

**Date of Execution:** 2026-07-20
**Target Environments Tested:**
- **Public Staging:** `https://corvinum-staging.80.211.210.46.sslip.io` (syncmetric-prime)
- **Local Rehearsal:** `http://localhost:8001` (`scripts/corvinum_app.sh rebuild`)

---

## 1. Executive Summary

A full end-to-end automated and programmatic validation of the **CorvinumEU PeopleOps presenter runbook** ([corvinum-demo-runbook.md](corvinum-demo-runbook.md)) was executed against both the local stack (`http://localhost:8001`) and the live staging server (`https://corvinum-staging.80.211.210.46.sslip.io`).

The ten-section route that existed at execution time passed without errors.
Encrypted payslip generation and controlled SMTP delivery were also verified
end-to-end. On the same date, the manual runbook and checker were expanded to
13 sections; this record does **not** retroactively claim that the three new
sections were part of the original execution.

No real worker data was used. One-time PDF passwords and TOTP secrets are
deliberately omitted from this record, even after expiry.

---

## 2. Walkthrough Step Verification Details

| Runbook Section | Tested Action / Route | Empirical Test Result | Status |
|---|---|---|---|
| **1. Secure Entry** | Login `hradmin@demo.corvinum.test` (`demo-corvinum-2026`) + TOTP 2FA verification | Redirected to `/sk/2fa/verify/`, submitted valid RFC 6238 6-digit TOTP code, redirected to `/sk/` | **PASSED** |
| **2. Interactive Reports** | Dashboard metrics, drill-downs, language/theme shell | `/sk/reports/` loaded (`200 OK`), rendered active projects, people counts, and trial status cards | **PASSED** |
| **3. Personnel Intake** | Start 3-step intake questionnaire (`/sk/intake/start/`) | Submitted Identity (Olena), Contact (+421 900 000 999), and Compliance (disability `nie`). Person created at `/sk/people/6/` in `available` state | **PASSED** |
| **4. Trial Day** | Schedule trial for Alfa Metallwerk & record `pass` outcome | Scheduled trial at `08:00` (`POST /sk/people/6/assign-trial/`), recorded `pass` outcome (`POST /sk/trials/3/outcome/`), status changed to `trial_day` | **PASSED** |
| **5. Activation Checklist** | Toggle critical compliance items on person detail card | Toggled item #37 (`POST /sk/checklist/37/toggle/`), updated state with actor attribution (`200 OK`) | **PASSED** |
| **6. Notifications** | Actionable problems & session updates panel | GET `/sk/notifications/` returned popover markup containing 4 active problems (checklist, blacklist) | **PASSED** |
| **7. Equipment Catalogue** | Manager catalogue creation (`POST /sk/equipment/catalog/new/`) | Created item `Vest-1784572548` (Size `L`, `8.50 EUR`, `is_active=on`), redirected to catalog | **PASSED** |
| **8. Ledger Controls** | Thursday cut-off & cycle view | GET `/sk/ledger/` loaded successfully with cash advances, travel additions, and equipment deductions | **PASSED** |
| **9. Encrypted Payslip** | Record payslip & deliver encrypted PDF via SMTP | Recorded a fictional `2026-07` payslip (`1450.00 EUR`) for Marek Skladník. Controlled email delivery succeeded and the one-time password appeared only in the intended UI confirmation. | **PASSED** |
| **10. Audit Log** | Access audit trail as HR Admin | GET `/sk/audit/` rendered append-only log entries for `auth.login`, `intake.completed`, `checklist.toggle`, and `payslip.sent` | **PASSED** |

---

## 3. End-to-End Email & PDF Security Conformance

During Step 9, the payslip delivery pipeline was validated end-to-end:
1. **PDF Generation & Encryption:** A PDF payload was generated dynamically
   using Python stdlib and encrypted with **AES-256 (R6)** via `pypdf` using a
   generated read-aloud-safe password. The password is not reproduced here.
2. **SMTP Transport:** Sent via standard TLS connection (`smtp.forpsi.com:587`).
3. **Receipt Verification:** Email delivery was confirmed at the recipient inbox, with the attached encrypted PDF successfully opening using the generated one-time password.
4. **Audit Protection:** The one-time password was verified **absent** from all audit log entries, database fields, and application logs.

---

## 4. Observed Notes & Recommendations

1. **Staging 2FA Device Persistence:**
   - On a freshly seeded local environment, signing in as `hradmin` opens the forced `/sk/2fa/setup/` screen with the QR code.
   - On the persistent staging deployment, `hradmin` already has a confirmed `TotpDevice`. Subsequent logins route directly to `/sk/2fa/verify/`.
   - *Recommendation:* Use a clean local reset to demonstrate enrollment. Use
     ordinary TOTP verification on persistent staging. Any staging enrollment
     reset must be a separately approved and rehearsed operation, never an
     ad-hoc pre-call command.

2. **Intake Version Alignment:**
   - At execution time the runbook intro mentioned "published Recruiter intake
     v3", while the codebase seeded version 4 (`seed_questionnaire.py`). The
     questionnaire schema and field validations were otherwise aligned.
   - *Resolution:* The runbook now identifies intake v4.

3. **Expanded route status:**
   - The current manual runbook and `scripts/test_corvinum_walkthrough.py`
     cover 13 sections, adding explicit Projects, Compliance, activation-gate,
     and Observer-policy checks around the original route.
   - Run the expanded checker again against local and staging before recording
     those additions as passed. Provider-backed email remains opt-in and must
     use the controlled recipient and approved secret-manager configuration.
