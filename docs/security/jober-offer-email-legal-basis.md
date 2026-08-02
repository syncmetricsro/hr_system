# Offer emails — legal basis & data handling

**Status: legal basis stated; LIA, DPA and an approved retention period pending.
Real-data execution is gated until sign-off — the module runs on fictional data
only (`AGENTS.md`), and `EMAIL_ALLOWED_RECIPIENTS` keeps non-production apps from
reaching a real inbox.**

Implementation: ADR 0029; design `docs/product/jober-offer-email-design.md`.

## Legal basis (stated by the client)

**Legitimate interest** (GDPR Art. 6(1)(f)) for operational messaging, recorded in
`docs/product/jober-requirements-supplement.md` — the privacy notice "supports
legitimate-interest processing for SMS/email operational messaging".

Job offers sit at the *outreach* end of that basis rather than the operational end.
A shift reminder to a worker on assignment and a seasonal campaign to a pool of
past candidates are not the same processing, even though they use one address and
one code path. That distinction is the reason this feature carries an opt-out
while payslip delivery does not, and it is the point the LIA has to address
explicitly rather than inherit.

Consent was **not** chosen as the basis. Consent that can be withdrawn at will
would make the recruitment pool unusable for its purpose, and Art. 21 objection
(the opt-out below) is the proportionate control for a legitimate-interest basis.

## Still required before real-data use

- **A documented Legitimate Interest Assessment (LIA)** covering job-offer
  outreach specifically: purpose, necessity, and the balancing test against a
  candidate who gave an address for one placement and is contacted about another.
  The supplement's one line about operational messaging is an input to this, not
  a substitute for it.
- **The Art. 28 processor agreement (DPA)** with the mail provider — recorded as
  *Not received*. `Jober_Messaging_Specs` §2 requires it to cover the provider,
  content, identifiers, retention, deletion and incident handling.
- **An approved retention period** for message bodies and delivery records.
  `OFFER_EMAIL_RETENTION_DAYS` defaults to **0 = keep everything**, deliberately:
  guessing a period would destroy evidence. The purge job is registered with
  `core.retention` and is a no-op until the period is set.
- **The written worker contract text** — the same pending item the blacklist
  basis records — to confirm the transparency wording actually shown to workers.
- Confirmation that offer emails may go to people in **`INACTIVE`** state (the
  recycling pool). The implementation permits it today; nothing about the
  lifecycle model answers whether it should.

## How the implementation minimises risk

- **Objection is a first-class field.** `Person.email_opt_out` blocks every offer
  send and is the Art. 21 mechanism. It is editable on the person form, audited,
  and checked **before** the allowlist and before the mail server, so an
  objection is never one configuration change away from being ignored.
  Operational mail (payslips) is a separate basis and deliberately ignores it.
- **Blacklisted people are never emailed an offer.** `send_offer_email` refuses on
  `LifecycleStatus.BLACKLISTED`. The SMS path consults neither flag; an offer is
  exactly the message that must not reach someone the company has blocked.
- **A refused send is recorded, not silent.** Every attempt creates an
  `OutboundEmail` row. `BLOCKED` (we never asked the mail server) stays distinct
  from `FAILED` (it saw the message and refused), so a safety net is never
  mistaken for an outage — or for a delivery.
- **Environment allowlist.** `EMAIL_ALLOWED_RECIPIENTS` restricts recipients on
  every non-production app. The reasoning is the one `tests/test_sms_safety.py`
  records: a fictional person record with a real address typed into it is
  indistinguishable from any other, so "the data is fake" is not a control.
  Empty means unrestricted, which is production's setting, so it cannot be made
  mandatory — instead `manage.py check` raises `messaging.W001` when outreach is
  enabled with a real SMTP backend, DEBUG off, and no allowlist. That warning is
  the execution gate, the counterpart of `BLACKLIST_MATCHING_ENABLED`.
- **Blast radius is capped.** Bulk sending is manager-only
  (`offer_email.bulk_send`), requires an explicit confirmation box, shows the
  recipient list and a rendered preview first, and is capped by
  `OFFER_EMAIL_BATCH_LIMIT` (default 100). Both the preview *and* the execution
  are office-scoped.
- **Data minimisation.** No new personal data is collected. The feature reuses the
  existing `Person.email` and `preferred_language` columns and adds one boolean.
  Offer bodies contain only the worker's name and the offer's own terms.
- **Auditability.** Every send writes `offer_email.sent` with its outcome, and
  every campaign writes `offer_email.batch_sent`, to the append-only audit log.

## Deliberate non-goals

- **No tracking pixels, open tracking, or click tracking.** Nothing measures
  whether a worker read the message.
- **No inbound surface.** Replies go to a human mailbox; the app does not ingest
  them, so nothing a worker writes back is stored here.
- **No unsubscribe link in the message.** Objection is recorded by staff on the
  person record. A tokenised self-service unsubscribe URL is the obvious
  improvement and is deliberately deferred — it is a public unauthenticated
  endpoint touching a person record, which needs its own design and review.

This feature does not open the real-data gate.
