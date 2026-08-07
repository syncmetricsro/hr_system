# Job-offer emails — design

Implemented under ADR 0029. Legal basis and pending gates:
`docs/security/jober-offer-email-legal-basis.md`.

## Status — paused 2026-08-03, read this first

**Built and ready to review.** PR #157 on `feat/offer-emails`, six commits, CI
green, no review yet. Nothing uncommitted.

**Deferred by decision (2026-08-03):** Jober has not supplied a `noreply@`
address, so Jober email configuration waits until a demo is scheduled. **No code
change is needed to hold this state** — the `offer_emails` flag stays on and the
feature now honestly reports itself unavailable (`email_configured()` treats the
default `localhost` host as unset). To enable later: set `DJANGO_EMAIL_HOST`,
`DJANGO_EMAIL_PORT`, `DJANGO_EMAIL_HOST_USER`, `DJANGO_EMAIL_HOST_PASSWORD`,
`DJANGO_EMAIL_USE_TLS`, `DJANGO_DEFAULT_FROM_EMAIL` **and**
`EMAIL_ALLOWED_RECIPIENTS`.

CorvinumEU payslip delivery is unaffected and verified end to end against real
SMTP — see `docs/deployment/corvinum-demo-verification-summary.md`. On
2026-08-07 the owner also approved this structured offer-email workflow for
CorvinumEU, Manager/HR Admin-only; the narrower client policy is recorded in
ADR 0029 and its permission matrix.

### Environment state

| Config | State |
|---|---|
| `stg_corvinum-staging` | allowlist set in Doppler **and** applied with `dokku config:set` |
| `stg_jober-staging` | allowlist set both places; `DJANGO_EMAIL_BACKEND` is still an **empty string** — harmless now that empty reads as unconfigured, but `console.EmailBackend` is the correct way to say "no email here" |
| `dev` (Jober local) | no allowlist. Low priority: `scripts/dev_app.sh` forwards no `DJANGO_EMAIL_*`, so it matters only for the cross-config trap — `corvinum_app.sh` *does* forward them, so running it against this config picks up Jober's SMTP with no allowlist |
| `prd` | no mail configured; production is blocked on deployment-plan ask **D8** regardless |

Doppler does not reach syncmetric-prime. Values are pasted into
`dokku config:set`, so a Doppler-only change is invisible to staging
(`docs/deployment/syncmetric-prime-staging.md`).

### Open, carried forward

- **Legal:** Art. 28 DPA with the mail provider, a job-offer-specific LIA, and an
  approved retention period. `OFFER_EMAIL_RETENTION_DAYS` is deliberately `0` =
  keep everything, so the registered purge job is a no-op until one is agreed.
  Full list in `docs/security/jober-offer-email-legal-basis.md`.
- **Product:** may offers go to `INACTIVE` people in the recycling pool? The
  build permits it; nothing in the lifecycle model decides it.
- **Known gap, not fixed:** `payslip_send` has no office guard. Not exploitable
  today — CorvinumEU creates no `Office` rows so the scope helper returns its
  unrestricted sentinel, and Jober has payslips off — but real the moment
  either changes.
- **Corrected 2026-08-03 — there is no i18n debt.** An earlier revision of this
  section claimed the catalogs on `main` were stale and that a re-extract would
  shrink them. That was wrong. `msgfmt --statistics` reports **1576 translated,
  0 untranslated, 0 fuzzy** in all three languages. The figures behind the claim
  came from `grep -c '^msgstr ""$'`, which counts the *wrapped* form where
  `msgstr ""` is followed by continuation lines — a translated long string, not
  an empty one. Running `--extract` would drop obsolete entries and produce ~44
  genuine fuzzy matches to review, so it creates work rather than fixing
  anything. This branch's approach of appending only its own msgids was right,
  but for a different reason than stated.
- **Deliberate non-goals** (see the bottom of this doc): no retry, no bounce
  handling, no self-service unsubscribe, and sends are synchronous.

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
- **Not general CorvinumEU messaging.** CorvinumEU enables this structured
  job-offer email workflow for Manager/HR Admin only. SMS, arbitrary group
  email, scheduling, and Messenger automation remain excluded.
