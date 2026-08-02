# Job-offer emails — design

Implemented under ADR 0029. Legal basis and pending gates:
`docs/security/jober-offer-email-legal-basis.md`.

## Decision

Jober can email a worker a job offer, in that worker's own language, from the
person card (one recipient) or from a dedicated page (a filtered, office-scoped
list). Offers are authored as records rather than retyped; the email text lives
in reusable per-language templates.

## SMS and offer emails are different products

They share a feature package and some infrastructure, and nothing else.

| | SMS | Offer email |
|---|---|---|
| Purpose | operational nudge to someone already engaged | outreach about work they have not taken |
| Record | `OutboundMessage` (`to_number`) | `OutboundEmail` (`to_email`, subject, language) |
| Length | one segment if possible | long-form |
| Language | whatever the template was written in | the worker's `preferred_language` |
| Opt-out | none | `Person.email_opt_out`, checked first |
| Blacklist | not consulted | refuses to send |
| Bulk | no | yes, manager-only, capped and confirmed |

This is why `OutboundMessage` was not widened with a `channel` column. Per
`Jober_Messaging_Specs` §3, provider services may share safe infrastructure
helpers; they do not share false domain semantics.

## Content boundary

An offer email carries the worker's name and the offer's own terms: title,
project, office, location, wage, start date, free-text terms, and a coordinator
name. Nothing else about the person is interpolated, and there is deliberately no
placeholder for anything sensitive — no date of birth, no certificate state, no
lifecycle status, no financial history.

Attachments are not supported. `docs/product/document-storage-boundary.md` and
`docs/product/accountant-data-handoff.md` govern what may leave the system as a
file; an offer needs none of it.

## Authoring workflow

1. A manager creates a `JobOffer` (Offers tab). It carries its own `office`, so
   scoping never depends on the project relation being set; picking a project
   fills the office in and a mismatch is a validation error.
2. A manager maintains `OfferEmailTemplate` rows, one per `(kind, language)`.
   Four kinds ship: new offer, reminder, seasonal campaign, closing soon. The
   seed provides all four in SK/HU/UK.
3. Bodies interpolate `$first_name`, `$last_name`, `$offer_title`, `$project`,
   `$office`, `$location`, `$wage`, `$start_date`, `$terms`, `$coordinator` —
   listed beside the editor so nobody has to guess.

Substitution is `string.Template.safe_substitute`. An unknown `$token` survives
into the preview rather than raising mid-batch; the preview is where it is caught.

## Language selection

`preferred_language` → `settings.LANGUAGE_CODE` → any active row for that kind.

The last fallback is deliberate: a wrong-language offer is recoverable, silence
is not. `preferred_language` is a free `CharField` with no choices validation, so
an unusable value degrades to the default rather than failing the send.

This is the gap `seed_messaging`'s docstring records for SMS and does not close.

## Sending

**One person** — a panel on the person card, gated by `offer_email.send` plus the
same coordinator narrowing SMS uses. The panel renders even when nothing can be
sent (no address, opted out, blacklisted, no template, SMTP unconfigured), with
the control disabled and the reason shown. A panel that vanishes reads as a
missing feature.

**Many people** — `offers/<pk>/send/`, gated by `offer_email.bulk_send` (manager
only). GET previews: the office-scoped recipient list, the excluded rows *with
their reasons*, the cap and how many were left out, and the body as the first
recipient would receive it. POST requires a confirmation checkbox. Preview and
execution use the same scoped query — a page that scoped its preview but not its
execution would show ten names and email four hundred.

## Delivery states

`QUEUED` is only the moment between row creation and the send attempt; nothing
re-processes it. Then one of:

- **SENT** — the mail server accepted it. Not a delivery confirmation.
- **BLOCKED** — we never asked: opt-out, blacklist, no address, or the
  environment allowlist.
- **FAILED** — the mail server saw it and refused, or no template existed.

No retry, and no bounce handling. SMTP acceptance is where the app's knowledge
ends.

## Data model and audit

`JobOffer`, `OfferEmailTemplate` (unique on `kind`+`language`), `OutboundEmail`,
`EmailBatch`. Every send writes `offer_email.sent` with its outcome; every
campaign writes `offer_email.batch_sent`. `OutboundEmail` is registered with
`core.retention`, though the period is unapproved and the purge is a no-op until
it is set.

## Verification

`tests/test_offer_emails.py` (language, rendering, batching),
`tests/test_offer_email_safety.py` (opt-out, blacklist, allowlist, unconfigured
backend, the deploy check), `tests/test_offer_email_office_scoping.py`
(request-level 403s on both surfaces), `tests/test_offer_email_seed.py`,
`tests/e2e/test_offer_emails.py`.

## Deliberate non-goals

- **No scheduling.** Offers are sent when a human presses the button.
- **No application/response tracking.** A worker replies to a human mailbox;
  nothing here records interest, acceptance, or rejection. If that arrives,
  `JobOffer` extracts to its own feature — the seam is noted in ADR 0029.
- **No self-service unsubscribe link.** Objection is recorded by staff. A
  tokenised public endpoint touching a person record needs its own design.
- **No open/click tracking.**
- **Not for CorvinumEU.** Its design rejects automated worker notification
  (§15.9); it gets neither the flag, the route, nor the permission.
