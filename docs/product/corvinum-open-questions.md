# CorvinumEU — open client questions (Stage C build defaults)

Stage C (ADR 0022) builds on **fictional data** with the design doc's proposed
defaults wherever the client has not yet confirmed a decision. Every default
below is reversible configuration or seed data — none is baked into core.
Sources: design doc §5.10/§12.6/§13, Addendum A1.

| # | Question (design doc ref) | Default built in Stage C | Confirm with |
|---|---|---|---|
| C-Q1 | Status lifecycle — statuses are proposed, not confirmed (§12.6) | Core lifecycle minus trial-day (Available ⇄ Working / Inactive / Blacklisted), transitions in `clients/corvinum_eu/policies.py` | Client |
| C-Q2 | Ledger rules (§5.10 "must be fixed before build"): timezone + Thursday cut-off | Europe/Bratislava, **Thursday 14:00**; entries after cut-off roll to next week's Friday, never retro-inserted | Client (exact time) |
| C-Q3 | 20th-to-20th cycle boundary | Window = 21st 00:00 → 20th 24:00 inclusive, local time, date math correct across Dec→Jan | Client |
| C-Q4 | Partial advance recovery across cycles (§13.3, model-affecting) | **Not in MVP** — an advance settles in one cycle; reversal entries are the correction path. If confirmed needed, add linked recovery entries (`recovers_advance_id`) | Client |
| C-Q5 | Correction/immutability | No hard deletes; pre-inclusion edits audited; post-inclusion only reversal entries (opposite `pay_effect`) | Client sign-off |
| C-Q6 | Financial boundary sign-off (§13.1) — **scope changed 2026-07-11**: client asked to store pay amounts + email encrypted payslips (ADR 0023); payroll *calculation* still out of scope | Payslips feature built; written confirmation still wanted | Client (written) |
| C-Q7 | Mandatory document types + which expire (§13.2) | Compliance certificates seeded with the §5.4 type list; nothing enforced as mandatory yet | Client |
| C-Q8 | Default UI language (SK or HU) + default theme (light/dark) | **SK default**, HU switchable; dark-default theme per the prototype | Client |
| C-Q9 | "HR Admin" as a distinct role vs. core `manager` | Mapped to `manager` for MVP | Client |
| C-Q10 | Private-car fuel money basis/cadence/eligibility (A1.1) | Flat manual `PAY_ADDITION`, category `travel_fuel`, entered per worker | Client |
| C-Q11 | Bus fuel log `features/fuel_costs` (A1.2 — secondhand request) | **Not built** pending decision-maker confirmation | Decision-maker |
| C-Q12 | Which equipment items carry recorded values (§13.1) | All issued items take an optional value (existing `features/logistics` model) | Client |
| C-Q13 | Retention periods for ledger + equipment-deduction history (§13.2) | No purge registered for ledger entries yet (`core/retention` ready when periods are known) | Client + legal |
| C-Q14 | Staging/production server, domain, DB names | Deployment deferred (ADR 0022) | Owner |
| C-Q15 | Payslip password delivery channel (ADR 0023 — never by email) | Shown once to the office user; phone/Messenger assumed | Client |
| C-Q16 | Retention period for stored pay amounts (payslips) | No purge registered yet; joins the GDPR review | Client + legal |

Update this file (and the design doc's §16 back-and-forth notes) as answers
arrive — the pattern that worked for Jober's Q1–Q5.
