# ADR 0023: CorvinumEU payslips — stored pay amounts + AES-256-encrypted PDF by email

Status: **Accepted — owner approved 2026-07-11 (deps + password design)**

## Context / scope change

CorvinumEU now wants to (a) **store what workers were paid** per period and
(b) **email each worker their payslip as an encrypted PDF**. This crosses the
financial boundary the design doc drew (§3, §5.10 "operational cash tracking,
not payroll") — recorded here as a client-requested scope change. The ledger's
C-Q6 boundary sign-off is superseded for this narrow purpose: pay amounts are
stored; payroll *calculation* remains out of scope. Fictional data only until
the real-data gate; salary-record retention joins the open questions (C-Q16).

## Password / crypto decisions

- **The worker's social security number was considered and rejected** as the
  PDF password: low entropy, partially guessable structure, and it would turn
  a national identifier into a credential.
- Per-payslip password: **12 characters, truly random** (`secrets`), from an
  unambiguous alphabet (no `0/O/1/l/I`), displayed grouped `XXXX-XXXX-XXXX`
  (~70 bits). PDFs are offline-brute-forceable, so length is the security;
  12 grouped chars is the agreed usability/security balance (owner decision).
- Encryption: **PDF 2.0 AES-256 (R6)** via pypdf.
- The password is **never stored and never emailed** — it is shown exactly
  once to the office user who triggers the send, for out-of-band delivery
  (phone/Messenger/in person — channel is client question C-Q15). Lost
  password ⇒ resend with a fresh one. Audit events record the send, never
  the password.
- The encrypted PDF itself is **not stored**; only payslip metadata
  (person, period, net amount, sent when/to/by). Regenerated on demand.

## New dependencies (AGENTS.md §3.1 approval gate)

Stdlib/Django cannot produce encrypted PDFs. Owner approved (2026-07-11):

| Package | Version | Published | Why / maintainer |
|---|---|---|---|
| `pypdf` | 6.14.2 | 2026-06-23 | PDF encryption (AES-256 R6); py-pdf org, pure Python |
| `cryptography` | 49.0.0 | 2026-06-12 | pypdf's AES backend; PyCA, the Python crypto standard |
| `cffi` / `pycparser` | 2.1.0 / 3.0 | transitives | required by cryptography |

Cooldown (≥3 days) satisfied for all. Wheels only, hash-pinned into
`runtime.lock` + `test.lock` via `scripts/write_requirements_lock.py` in the
digest-pinned build container. The PDF *content* is generated with a minimal
stdlib writer (one page, text only) — pypdf is used for encryption, keeping
the new surface small. Alternative `qpdf` (OS package + subprocess) rejected
as a second package ecosystem for the same job.

## Consequences

- `features/payslips` is a CorvinumEU-only flag (`payslips`, off for Jober —
  zero behavior change; installed for both so the shared suite covers it).
- `core/people.Person` gains an optional `email` field (a reusable core
  contact attribute; not added to any intake form yet).
- Email goes through Django's SMTP backend (credentials via Doppler in real
  deployments; console/locmem locally). A send with no configured backend
  fails loudly, never silently.
- GDPR: pay data is sensitive; exports/retention for payslips pend C-Q16 and
  the legal review that governs all real data.
