# ADR 0029: Job-offer emails over Django's mail backend (no new dependency)

Status: **Accepted — 2026-08-02.**
Date drafted: 2026-08-02

## Context

Jober could reach a worker by SMS only. `features/messaging` is Twilio-shaped end
to end: `OutboundMessage` stores `to_number`, there is no channel column, no
subject, and no placeholder substitution. `MessageTemplate.body` is sent verbatim,
so `Person.preferred_language` is never consulted — a gap `seed_messaging`'s
docstring records as its own backlog item.

That leaves no channel for the one message that genuinely needs long-form text and
the recipient's own language: a job offer. Recruiters were sending them out of
band, which puts the content and the fact of the send outside the system entirely.

Three pieces were already in place. `Person.email` exists (added under ADR 0023
for payslip delivery, explicitly "a generic contact attribute"). SMTP is
configured in `config/settings/base.py`, with the console backend forced locally.
`features/payslips/services.py::send_payslip` is a working precedent for sending
a worker an email and auditing it.

What was missing: a job-offer concept (`Project` has partner/office/coordinators
but no role title, wage, start date or offer text), any consent or objection
field, and any email counterpart to the `SMS_ALLOWED_RECIPIENTS` staging guard.

## Decision

- **No new dependency.** Delivery uses `django.core.mail.EmailMessage` and the
  configured `EMAIL_BACKEND`. No SDK, no lockfile change, so no §3.1 cooldown or
  package ADR is needed. This mirrors ADR 0019's reasoning for Twilio.

- **The transport lives inside `features/messaging`**, per `Jober_Messaging_Specs`
  §3 — no `features/offers` package and no client conditional in `core/`. It gets
  its **own records and its own actions**; `OutboundMessage` stays phone-shaped.
  New models: `JobOffer`, `OfferEmailTemplate`, `OutboundEmail`, `EmailBatch`.
  (If `JobOffer` later grows an application/response lifecycle it extracts to its
  own feature. That seam is known and not solved here.)

- **Templates are keyed `(kind, language)`**, and a send picks the row matching
  `Person.preferred_language`, falling back to `LANGUAGE_CODE` and then to any
  active row for that kind. This closes the gap SMS still has. The four kinds —
  new offer, reminder, seasonal campaign, closing soon — *are* the "different
  types of job offer". Bodies are operator-authored and stay outside the gettext
  catalogs, consistent with `docs/i18n-seeded-data.md`'s treatment of SMS bodies:
  the per-language rows are the translation mechanism.

- **Substitution is `string.Template.safe_substitute`**, not Django template
  rendering. Operator-authored text has no business reaching template internals,
  and `safe_substitute` leaves an unknown `$token` intact rather than raising
  halfway through a batch. Both send surfaces show a rendered preview, which is
  where a typo'd token is caught.

- **Three ordered guards before delivery**, evaluated in `send_offer_email`:
  1. the worker's own state — `email_opt_out`, `BLACKLISTED`, or no address on
     file ⇒ `BLOCKED`;
  2. the environment allowlist `EMAIL_ALLOWED_RECIPIENTS` ⇒ `BLOCKED`;
  3. delivery ⇒ `SENT`, or `FAILED` if the mail server refused.

  `BLOCKED` and `FAILED` stay distinct for the reason `OutboundMessage` already
  draws the line: FAILED means the server saw it and refused, BLOCKED means we
  never asked. Collapsing them makes a safety net look like an outage.

  Guard 1 is new relative to SMS, which consults neither flag. An operational
  text to a worker on shift is a different act from marketing a job to someone
  who asked us to stop, or to someone the company blocked.

- **`Person.email_opt_out`** is the GDPR Art. 21 objection mechanism, editable on
  the person form and audited. Operational mail (payslips) is a separate basis
  and deliberately ignores it.

- **Authorization**: `offer_email.send` (recruiter/coordinator/manager, with the
  same coordinator-scoped narrowing SMS applies), `offer.manage` and
  `offer_template.manage` (manager), and `offer_email.bulk_send` (manager only —
  one mistyped filter reaches every worker in an office). Unlike
  `sms.manage_templates`, `offer_template.manage` is enforced by a real view, not
  left to Django admin.

- **Office scoping (ADR 0026) applies to both surfaces.** `JobOffer` carries its
  own `office` column rather than reading it through a nullable `project`, so the
  boundary never depends on a relation being set. The bulk recipient query uses
  `scope_people`, and the *execution* is scoped, not only the preview.

- **`EMAIL_ALLOWED_RECIPIENTS` is the execution gate**, in place of a fourth
  boolean switch. Empty means unrestricted, which is what production wants, so it
  cannot simply be made mandatory; instead `manage.py check` emits
  `messaging.W001` when outreach is enabled with a real SMTP backend, DEBUG off,
  and no allowlist. Real sends to real people remain behind the real-data gate.

- **CorvinumEU gets neither the route nor the permission.** `offer_emails` is
  `False` in base and in `clients/corvinum_eu/settings.py`, the actions are absent
  from its policy module, and `features.messaging` is not installed there at all.
  Automated notification to workers is rejected in its design (§15.9).

## Consequences

- Jober gains an auditable outreach channel; every attempt is an `OutboundEmail`
  row whatever the outcome, and a campaign is a single `EmailBatch`.
- Sends are **synchronous**, like `send_sms`. A batch of 100 holds the request for
  the length of 100 SMTP round-trips. `OFFER_EMAIL_BATCH_LIMIT` caps the blast
  radius; a queue is the obvious next step if batches grow.
- There is still **no retry and no delivery confirmation**. SMTP acceptance is not
  delivery, and bounces are invisible to the app.
- `OutboundEmail` is registered with `core.retention` so the new PII store is not
  born undocumented — but the retention *period* is still unapproved, the same
  open item the messaging spec already flags for SMS.
- Two catalogs of near-duplicate text now exist (SMS templates and offer
  templates). That is the deliberate cost of not widening `OutboundMessage`.

This feature does not open the real-data gate.
