# CorvinumEU — open client questions (Stage C build defaults)

Stage C (ADR 0022) builds on **fictional data** with the design doc's proposed
defaults wherever the client has not yet confirmed a decision. Every default
below is reversible configuration or seed data — none is baked into core.
Sources: design doc §5.10/§12.6/§13, Addendum A1.

| # | Question (design doc ref) | Default built in Stage C | Confirm with |
|---|---|---|---|
| C-Q1 | Status lifecycle — statuses are proposed, not confirmed (§12.6) | **Trial-day workflow enabled for the demo**: Available → Trial day → Working / Available / Inactive / Blacklisted; transitions in `clients/corvinum_eu/policies.py` | Client confirmation still required |
| C-Q2 | Ledger rules (§5.10 "must be fixed before build"): timezone + Thursday cut-off | Europe/Bratislava, **Thursday 14:00**; entries after cut-off roll to next week's Friday, never retro-inserted | Client (exact time) |
| C-Q3 | 20th-to-20th cycle boundary | Window = 21st 00:00 → 20th 24:00 inclusive, local time, date math correct across Dec→Jan | Client |
| C-Q4 | Partial advance recovery across cycles (§13.3, model-affecting) | **Not in MVP** — an advance settles in one cycle; reversal entries are the correction path. If confirmed needed, add linked recovery entries (`recovers_advance_id`) | Client |
| C-Q5 | Correction/immutability | No hard deletes; pre-inclusion edits audited; post-inclusion only reversal entries (opposite `pay_effect`) | Client sign-off |
| C-Q6 | Financial boundary sign-off (§13.1) — **scope changed 2026-07-11**: client asked to store pay amounts + email encrypted payslips (ADR 0023); payroll *calculation* still out of scope | Payslips feature built; written confirmation still wanted | Client (written) |
| C-Q7 | Mandatory metadata/certificate types + which expire (§13.2) | Nothing enforced as mandatory yet; high-risk identity/medical/civil-status scans are proposed metadata-only or prohibited | Client |
| C-Q8 | Default UI language (SK or HU) + default theme (light/dark) | **SK default**, HU switchable; **Dark default**, with Light and System selectable per browser | Client |
| C-Q9 | "HR Admin" as a distinct role vs. core `manager` | Mapped to `manager` for MVP | Client |
| C-Q10 | Private-car fuel money basis/cadence/eligibility (A1.1) | Flat manual `PAY_ADDITION`, category `travel_fuel`, entered per worker | Client |
| C-Q11 | Bus fuel log `features/fuel_costs` (A1.2 — secondhand request) | **Not built** pending decision-maker confirmation | Decision-maker |
| C-Q12 | Which equipment items carry recorded values (§13.1) | All issued items take an optional value (existing `features/logistics` model) | Client |
| C-Q13 | Retention periods for ledger + equipment-deduction history (§13.2) | No purge registered for ledger entries yet (`core/retention` ready when periods are known) | Client + legal |
| C-Q14 | Staging/production server, domain, DB names | Deployment deferred (ADR 0022) | Owner |
| C-Q15 | Payslip password delivery channel (ADR 0023 — never by email) | Shown once to the office user; phone/Messenger assumed | Client |
| C-Q16 | Retention period for stored pay amounts (payslips) | No purge registered yet; joins the GDPR review | Client + legal |
| C-Q17 | Corvinum wage-source and payroll reconciliation definition | **Narrowed 2026-08-04.** The overview now also shows the office's own ledger deductions and a derived **After deductions** column (gross − recorded ledger entries). The application still does **not** derive statutory net pay or flag the remaining gap as an error; tax, levies, and `radonak.xlsx` remain deferred. The recorded net payslip stays a separate column so the two can be compared | Client + payroll owner |
| C-Q18 | Confirm the platform document-storage boundary ([decision note](document-storage-boundary.md)) | Base PeopleOps stores structured metadata for high-risk requirements; files only for forklift, crane, and welding licences. Excluded scans require a separately scoped Secure Document Vault | Client |
| C-Q19 | Confirm employing entity and SK/HU accountant handoff ([research/design note](accountant-data-handoff.md)) | **Supported jurisdictions: Slovakia and Hungary, as separate schedules.** Confirm the entity, employment-level jurisdiction, recipient role/DPA, exact country fields/evidence, custody, transfer, and retention. No ID scans or medical details in routine handoff; mixed, posted, unresolved cross-border, and other-country cases are refused | Client + accountant/payroll owner + legal/privacy |

Update this file (and the design doc's §16 back-and-forth notes) as answers
arrive — the pattern that worked for Jober's Q1–Q5.

## Raised 2026-08-04, ask at the demo

**C-Q20 — when the office enters a net payslip figure, is it before or after an
advance already handed over in cash?** `Payslip.net_amount` is stored and
printed exactly as typed; the system never computes it and never checks it
against the gross wage or the ledger. Both conventions therefore produce an
identical payslip, and only the office knows which one it used.

It matters for the worker-facing document: the PDF prints **"Net amount paid"**,
which reads as *what reached your account*. That label is correct only under the
post-advance convention. Under the pre-advance convention the worker is shown a
figure larger than they received, with no mention of the advance anywhere on the
document — the deduction lives only on the internal ledger.

Once answered, either the label or the entry rule needs to change, and the
question of whether the PDF should itemise deductions at all (see C-Q6 on the
payroll-calculation boundary) can be settled with it.

## Answered by observation

**How many administrators does an office actually have? — at least sometimes,
one.** Raised by the client on 2026-08-04 and confirmed on CorvinumEU staging,
which runs with a single HR Manager. Two consequences, both fixed in ADR 0031:
the separation-of-duties rule made activation permanently impossible for that
manager (two approvals sat undecidable, answering 403), and the trial day could
not be skipped for a worker the office already knows.

This is worth carrying into C-Q9 ("HR Admin" as a distinct role): a role split
that assumes two people is a role split this deployment cannot staff. Any future
control that requires a *distinct* second person should be checked against the
single-admin case before it is built.
