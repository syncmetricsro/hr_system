# Jober — what we need from you

Every outstanding decision on one page, with what each one is holding up.
Grouped by **who can answer it**, because these go to three different people.

Prepared 2026-08-03. CorvinumEU's nineteen open items live in their own register
(`docs/product/corvinum-open-questions.md`) and are not repeated here.

## The short version

Nothing in the build is waiting on engineering. **Six items block real worker
data entirely**, and they are the first two sections below. Everything in the
third section affects how well the system fits, not whether it can be used.

---

## A · For your data-protection adviser or lawyer

These gate the real-data legal gate (`AGENTS.md`). Until they are settled the
system runs on fictional data, which it does today.

**A1 · Sign off the blacklist LIA.**
Draft: `docs/security/jober-blacklist-lia.md`. Recorded as required since
**2026-06-30** — the oldest open item here.
*Blocks:* any real use of duplicate/blacklist matching.
*The draft flags four decisions only you can make:* what a person is told and
when; whether the mother's-maiden-name composite is proportionate; whether the
reason categories stay clear of special-category data; and whether the stated
purpose narrows to fraud and safety.
*If unanswered:* the module stays on fictional data behind its execution gate.

**A2 · Sign off the job-offer email LIA.**
Draft: `docs/security/jober-offer-email-lia.md`.
*Blocks:* emailing real workers about real jobs.
*Three open points:* whether your privacy notice actually told people this
address could be used for job offers; whether a public job board is a
sufficient less-intrusive alternative; and whether staff-recorded objection is
adequate or a self-service unsubscribe is needed first.
*If unanswered:* the feature ships disabled — it already reports itself
unavailable — and can be enabled later with no code change.

**A3 · Confirm the retention periods.**
Proposal with reasoning: `docs/security/jober-data-retention-proposal.md`.
*Blocks:* real data in ten stores.
*The one to look at first* is blacklist fingerprints — currently a **5-year
placeholder already running in code**; we propose 3. Payslips, person records
and wage data need statutory numbers we do not have; your accountant likely
does.
*If unanswered:* data accumulates indefinitely, because guessing a period
destroys evidence.

**A4 · Supply the written worker contract / privacy notice text.**
Promised, not yet delivered. Needed to confirm what workers were actually told.
*Blocks:* A1 and A2 both depend on it.

---

## B · For you to obtain from vendors

**B1 · Processor agreements (Art. 28).**
Checklist: `docs/security/jober-processor-dpa-requirements.md`. **None
received.** Needed from: FORPSI for hosting (sees everything, including
certificate scans and pay data — the easiest one to forget), Twilio for SMS,
and FORPSI again for CorvinumEU payslip mail.
*Blocks:* real data reaching any of them.
*Ask each one specifically how long they keep message bodies and backups* — our
deleting a record locally does not delete their copy.

**B2 · A `noreply@` address for Jober.**
*Blocks:* job-offer emails for Jober. CorvinumEU already has
`noreply@corvinum.eu` and it is verified working end to end.
*If unanswered:* the feature stays visibly unavailable. Deferred by your
decision on 2026-08-03; no code change needed either way.

**B3 · An off-site backup destination.**
Scripts exist; the host does not. It will hold a full copy of everything, so it
needs its own processor agreement (B1).
*Blocks:* the tested-backups condition of the real-data gate.

---

## C · Business decisions — yours

None of these block real data. They affect how well the system matches how you
actually work.

**C1 · May job offers go to people marked INACTIVE?**
The recycling pool. The build permits it today; nothing in the lifecycle model
decides it. *Ask yourself:* is someone you marked inactive a candidate for a new
opening, or someone you have stopped contacting?

**C2 · Catalogue and reference values.** Five entries have sat as "not modelled
in Phase 0" since the start, and each currently runs on placeholders:
remaining Person/WorkerProfile fields · allowed inactive-reason values ·
real accommodation list with rooms, capacities and rates · equipment catalogue
with sizes, opening stock and purchase prices · the missing-returnable-item
deduction process.
*If unanswered:* demos keep using fictional catalogues, and the first real
month of data will need re-entering.

**C3 · Blacklist reason categories.** Seeded with neutral placeholders. Some
plausible categories would touch health or criminal-allegation data, which
changes the legal basis (A1).

**C4 · Finance period and P&L scope.** Whether the finance period is October or
November 2025, and whether profit-and-loss opt-out is per project.

**C5 · Should recruiters see the Reports page — and if not, where do they
land?** Raised 2026-08-06: recruiters (`naborar`) are apparently not privy to
what Reports shows.

The straightforward reading is "hide the tab", and it is not that simple, so
this needs deciding before it is built rather than after. **Reports is the page
every role lands on after signing in**, and the logo in the corner of every
screen goes back to it. Hiding it from recruiters therefore has to say where a
recruiter goes instead, or they are refused at the door and again every time
they click the logo.

Worth knowing while you decide: the page is not only reports. It also carries
the active-project and people counts, people-by-status, inactive-by-reason, the
project-and-personnel list, and the compliance, occupancy and equipment-value
tiles — and it is how a recruiter reaches the People list today.

What we need from you:

1. Should recruiters see Reports at all?
2. If not, where should they land after signing in? **Our suggestion: the People
   list** — it is the screen they work in all day, it is already limited to
   their own office, and they can already open it.
3. Does the same apply to coordinators, or to recruiters only?

Managers and Observers are unaffected either way.

*Not blocked on engineering.* Once the landing page is settled the change is
small — a permission, a hidden tab, and a different destination for the logo and
the sign-in redirect. Nothing has been built yet, deliberately: building the
permission first would make the question rhetorical.

---

## What we are *not* waiting for

So the list is not read as bigger than it is:

- **Office scoping** is built and enforced across every module.
- **The three licensed offices** are settled; a fourth is a commercial question
  to SyncMetric, not a feature.
- **Transport** is deliberately out of scope for Jober.
- **Equipment returns** are out — "what we issue, stays out", confirmed 2026-07-28.
- **Yearly reporting periods** exist already (day/week/month/several
  months/year) on the warehouse and receipts screens.

---

## Where the detail lives

| Ask | Document |
|---|---|
| A1 | `docs/security/jober-blacklist-lia.md`, `jober-blacklist-legal-basis.md` |
| A2 | `docs/security/jober-offer-email-lia.md`, `jober-offer-email-legal-basis.md` |
| A3 | `docs/security/jober-data-retention-proposal.md` |
| B1 | `docs/security/jober-processor-dpa-requirements.md` |
| B3 | `docs/deployment/deployment-plan.md` (ask D6) |
| C2, C4 | `docs/product/jober-open-decisions.md` |
| all legal gates | deployment ask **D8** |
