# Legitimate Interest Assessment — job-offer emails

> **DRAFT. Not legal advice. Unsigned, and not a completed LIA until the
> client's data-protection adviser has reviewed, edited and signed it.**
>
> Written by the engineering side so a DPO edits rather than starts from blank,
> and so the technical safeguards are described accurately. Every control cited
> in §3.4 is implemented and named by file — none is aspirational.
>
> Prepared 2026-08-03 · Processing: job-offer emails (ADR 0029, PR #157) ·
> Controller: Jober · Basis claimed: GDPR Art. 6(1)(f)
>
> Feature description: `docs/product/jober-offer-email-design.md`.
> Basis and outstanding gates: `docs/security/jober-offer-email-legal-basis.md`.
> **Both of those arrive with PR #157**, which is not yet merged — if you are
> reading this before it lands, those two links will not resolve. The
> processing they describe is what this assessment covers either way.
>
> **The feature runs on fictional data only until this is signed and the
> real-data gate opens.**

## 1 · Purpose test — is there a legitimate interest?

**The processing.** Sending a named worker or candidate an email describing a
specific job opening: title, project, office, location, wage, start date and
free-text terms. Sent either to one person from their record, or to a filtered,
office-scoped list of people.

**The interest.** Filling client placements from a pool of people who have
already been through Jober's intake. This is the company's core commercial
activity, and the pool exists precisely so that a person who was not placed
once can be placed later.

**Who benefits.** Jober, the end client whose vacancy is filled, and the worker
— for a labour-hire agency the interest is genuinely mutual, which matters at
§3. Recruitment is a recognised legitimate interest; the question is not whether
the aim is legitimate but whether *this* contact is proportionate, which is §3.

**Would it be unlawful not to do it?** No. This is a commercial interest, not a
legal obligation, which weakens the controller's side of the balance relative
to, say, the blacklist's fraud-prevention argument.

## 2 · Necessity test — is the processing necessary?

**Does it achieve the purpose?** Yes, and directly: the worker learns a specific
job exists on terms they can evaluate.

**Is there a less intrusive route?**

- *Waiting to be contacted.* Fails the purpose — placements are time-boxed and a
  pool that is never contacted is not a pool.
- *SMS instead.* Already exists, and is more intrusive per message, not less: it
  reaches a personal handset immediately and cannot carry the terms, so it
  drives a phone call rather than replacing one.
- *Contacting only people in an active placement.* Fails the purpose, which is
  precisely to reach people who are not currently placed.
- *A public job board with no direct contact.* Reaches fewer of the pool and
  transfers the effort to the worker, but is genuinely less intrusive. **This is
  the strongest alternative and the DPO should test it.** The counter-argument
  is that it does not reach a candidate who is not actively searching, which is
  most of the pool most of the time.

**Why not consent (Art. 6(1)(a))?** Consent is withdrawable at will and must be
freely given. In an agency relationship where the worker depends on the agency
for placements, consent is not obviously free — which makes it a *weaker* basis
here, not a safer one. A withdrawable permission also makes the pool
unmaintainable for its purpose. **Art. 21 objection is the proportionate control
instead**, and it is implemented (§3.4). The DPO should confirm this reasoning;
it is the most contestable choice in this document.

**Note on e-privacy.** If any of this content is ever treated as direct
marketing rather than recruitment operations, national e-privacy rules on
unsolicited email may apply *in addition* to the GDPR basis. **Not established
for SK/HU and outside engineering's competence** — flagged because the seasonal
campaign kind is the closest to marketing.

## 3 · Balancing test

### 3.1 Reasonable expectations

A person completed Jober's intake to be placed in work and supplied an email
address in that context. Being told about a job is close to the reason they gave
it. Two things stretch this:

- **Time.** An address given eighteen months ago for one placement carries a
  weaker expectation than one given last month.
- **Distance from the original context.** The `SEASONAL` campaign kind is the
  furthest from "the placement you applied for" and closest to marketing.

Note that `Person.email` was added for **payslip delivery** (ADR 0023) and is
described in the model as a generic contact attribute. It is deliberately not on
intake forms today. **The DPO should confirm the privacy notice actually told
people the address may be used for job offers** — a field introduced for payroll
and reused for outreach is exactly what an Art. 21 complaint would focus on.
`docs/product/jober-requirements-supplement.md` records that the notice
"supports legitimate-interest processing for SMS/email operational messaging",
which is not obviously the same thing.

### 3.2 Likely impact

Low. The content is a job offer; nothing sensitive is interpolated. The design
places a hard boundary on content — no date of birth, no certificate state, no
lifecycle status, no financial history, no attachments — and the placeholder set
is fixed in code, so it cannot drift by configuration.

The realistic harms are nuisance, and the inference a third party could draw from
seeing the mail (that this person is looking for work, or is on an agency's
books). Both are low but non-zero, and both scale with frequency, which is why
the frequency controls in §3.4 matter.

### 3.3 Vulnerability of the data subjects

**This is the strongest argument against, and should not be softened.** The
population is migrant labour-hire workers — the fictional seed data uses
Ukrainian, Central-Asian and Vietnamese names because that reflects the real
workforce. Relevant factors:

- Economic dependence on the agency for income.
- Language: offers may be read in a second or third language. The build sends in
  the worker's own `preferred_language` where a template exists, which helps and
  is a deliberate safeguard rather than a nicety.
- Objecting requires knowing you can. **A worker cannot currently opt out
  themselves** — a staff member must set the flag (§3.4). That is a real
  limitation of the balance, not a detail.

### 3.4 Safeguards actually implemented

Verified against the code on 2026-08-03. Each is a control that exists, not a
commitment.

| Safeguard | Where | Effect |
|---|---|---|
| **Art. 21 objection** | `Person.email_opt_out`, checked **first** in `send_offer_email` | An objection blocks every offer email and cannot be overridden by configuration |
| **Blacklisted people are never contacted** | `LifecycleStatus.BLACKLISTED` refused in the same first check | The SMS path consults neither flag; this one does |
| **Refusal is recorded, not silent** | every attempt writes an `OutboundEmail` row; `BLOCKED` (never asked the server) stays distinct from `FAILED` | A suppressed send is auditable, so the opt-out is verifiable rather than asserted |
| **Content boundary** | fixed placeholder set in `offer_placeholders` | Nothing sensitive can be interpolated, by configuration or by template text |
| **Frequency and blast radius** | bulk send is manager-only (`offer_email.bulk_send`), requires an explicit confirmation box, shows the recipient list *and the people it will skip, with reasons*, capped by `OFFER_EMAIL_BATCH_LIMIT` (100) | A campaign is a deliberate act with a visible recipient list, not a background job |
| **Data minimisation** | reuses existing `email` and `preferred_language`; adds one boolean | No new personal data is collected for this feature |
| **Office scoping** | `scope_people` on the recipient query; preview and execution share it | A manager reaches only their own office's workers |
| **Environment containment** | `EMAIL_ALLOWED_RECIPIENTS`, plus `manage.py check` warning `mail.W001` | A non-production system cannot email a real person even if a real address is typed into a fictional record |
| **Auditability** | `offer_email.sent` per attempt with outcome; `offer_email.batch_sent` per campaign | Who sent what, to whom, and whether it left |

**Not implemented, and relevant to the balance:**

- No self-service unsubscribe link. Objection depends on a worker asking staff
  and staff recording it. Deliberately deferred (a public unauthenticated
  endpoint touching a person record needs its own design), but it is the most
  obvious way to strengthen this assessment.
- No frequency cap over time. Nothing prevents the same person receiving an
  offer every week from four different offers.
- No retention period — bodies are kept indefinitely pending
  `jober-data-retention-proposal.md`.
- No bounce handling, so an address that has stopped working is retried forever.

## 4 · Outcome

**Engineering's reading: the balance is arguable and the safeguards are
substantive, but three things are unresolved and none is an engineering
decision.**

1. Whether the privacy notice told people this address could be used for job
   offers (§3.1).
2. Whether a public job board is a genuinely sufficient less-intrusive
   alternative (§2).
3. Whether staff-recorded objection is adequate for this population, or whether
   a self-service opt-out is required before real use (§3.3, §3.4).

The `SEASONAL` campaign kind is the weakest case throughout. If the DPO wants to
narrow scope rather than reject, **disabling that one kind while keeping the
other three is a small change** — templates are per-kind rows.

## 5 · Review and sign-off

Reassess if: the population changes; a self-service unsubscribe is added;
send frequency rises materially; content gains attachments or new placeholders;
or a worker objects and that objection is contested.

| | Name | Role | Date | Signature |
|---|---|---|---|---|
| Prepared (engineering draft) | | | 2026-08-03 | — |
| Reviewed | | Data-protection adviser / DPO | | |
| Approved | | Client business owner | | |

**Until signed, this feature stays on fictional data. This document does not
open the real-data gate.**
