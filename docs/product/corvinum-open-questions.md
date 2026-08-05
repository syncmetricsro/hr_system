# CorvinumEU — open client questions (Stage C build defaults)

Stage C (ADR 0022) builds on **fictional data** with the design doc's proposed
defaults wherever the client has not yet confirmed a decision. Every default
below is reversible configuration or seed data — none is baked into core.
Sources: design doc §5.10/§12.6/§13, Addendum A1.

| # | Question (design doc ref) | Default built in Stage C | Confirm with |
|---|---|---|---|
| C-Q1 | Status lifecycle — statuses are proposed, not confirmed (§12.6) | **Trial-day workflow enabled for the demo**: Available → Trial day → Working / Available / Inactive / Blacklisted; transitions in `clients/corvinum_eu/policies.py` | Client confirmation still required |
| C-Q2 | Ledger rules (§5.10 "must be fixed before build"): timezone + Thursday cut-off | Europe/Bratislava, **Thursday 14:00**; entries after cut-off roll to next week's Friday, never retro-inserted | Client (exact time) |
| C-Q3 | 20th-to-20th cycle boundary | Window = 21st 00:00 → 20th 24:00 inclusive, local time, date math correct across Dec→Jan. **Amended 2026-08-05 (ADR 0032):** the boundary is unchanged, but a run now *collects* every entry still outstanding at its cutoff, not only those dated inside its own window — an advance that missed its run is recovered by the next one instead of never | Client |
| C-Q4 | Partial advance recovery across cycles (§13.3, model-affecting) | **Not in MVP** — an advance settles in one cycle; reversal entries are the correction path. If confirmed needed, add linked recovery entries (`recovers_advance_id`) | Client |
| C-Q5 | Correction/immutability | **Answered 2026-08-05 (ADR 0033).** Blanket immutability rejected. An entry is **deletable until the money is paid** — open or included — and immutable once settled with pay, where a reversal remains the correction path. Every deletion writes an audit event carrying the values, so a figure leaves the ledger but not the record. A cycle closed by mistake can be **reopened while its own 21st-to-20th window is still running**; afterwards the refusal names the next run and its dates | **Answered** |
| C-Q6 | Financial boundary sign-off (§13.1) — **scope changed 2026-07-11**: client asked to store pay amounts + email encrypted payslips (ADR 0023); payroll *calculation* still out of scope | Payslips feature built; written confirmation still wanted | Client (written) |
| C-Q7 | Mandatory metadata/certificate types + which expire (§13.2) | Nothing enforced as mandatory yet; high-risk identity/medical/civil-status scans are proposed metadata-only or prohibited. **Note added 2026-08-05:** the medical is tracked as a *date* with a single global validity of **12 months** (`MEDICAL_VALIDITY_MONTHS`), and since that date now blocks activation once it lapses, the number matters. SK and HU intervals differ, and night work and driving typically carry shorter ones — ask for their actual intervals and whether they vary by job | Client |
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

Once answered, either the label or the entry rule needs to change.

**C-Q21 — should the payslip PDF itemise what was deducted?** Today it prints
four lines: worker, period, `Net amount paid`, and an optional note. A worker
who had 200 EUR taken as an advance and 50 EUR for equipment sees neither on
the document they receive; both live only on the internal ledger and on the
office-facing pay overview.

**Not built, and deliberately so — it needs written client confirmation first.**
The blockers are not technical; the data has joined since 2026-08-04 and the PDF
writer is four lines of `build_encrypted_pdf`. They are:

1. **C-Q20 must be answered first.** If the entered net is already
   post-advance, itemising the advance again reads as a second deduction and
   understates the pay by that amount to the person least able to challenge it.
2. **After deductions is not net pay**, and a PDF cannot carry the caption that
   makes that clear on the internal screen. A worker forwards the document; the
   explanation does not travel with it. Printing `1800.00` beside `1540.00`
   with no statutory line invites exactly the dispute the office wants to avoid.
3. **It moves the C-Q6 payroll boundary.** A document that shows gross, minus
   deductions, arriving at a figure that is not the paid figure, is a partial
   payroll calculation whatever the labels say.

The shape to propose, if confirmed: gross, the itemised deductions the office
recorded, a subtotal, then the recorded net as a **separately stated** figure,
with one line saying the remaining difference is applied by payroll and not
calculated by this system. That answers "what was taken off me" without the
document claiming to derive net pay.

Get the answer in writing, like C-Q6. This is a document about someone's pay.

**C-Q23 — would the office run a paper archive register?** Proposed by the
owner on 2026-08-05 and written up in
[`paper-archive-register-design.md`](paper-archive-register-design.md):
track that a paper exists and when it expires, never store a scan, and print a
QR label for the archive sleeve so a specific sheet can be found again.

**Designed, not built.** Four things to settle before any code:

1. Which papers do they keep, and which expire? This is the same answer C-Q7
   needs, so ask them together.
2. **Would they actually label every paper, every time?** If the honest answer
   is "mostly", build the catalogue and the expiry chasing and drop the labels
   — a half-labelled archive looks complete and is not.
3. Where do the papers live, and who may read the register?
4. How long is each type kept after a worker leaves? This makes C-Q13 and
   C-Q16 blocking rather than open.

Worth saying out loud at the demo: the QR token exists so nobody has to type an
identity-document number into the system. It is a compliance improvement, not
just a filing convenience — and it is **not** the Secure Document Vault, which
remains separately scoped and unbuilt (C-Q18).

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
