# ADR 0019: Twilio SMS via the standard library (no SDK)

Status: Accepted
Date: 2026-06-28

## Context

Phase 2 includes approved SMS messaging (plan §11.12, `messaging_specification.md`):
outbound sending plus an inbound webhook. AGENTS.md prefers calling provider REST
APIs through one pinned HTTP client over adding a vendor SDK, and requires inbound
webhooks to be signature-verified and to fail closed; no secrets in the repo.

## Decision

- **No new dependency.** Twilio's REST API is called with the **standard library**
  (`urllib.request`, HTTP Basic auth) — a single form-encoded POST to
  `…/Messages.json`. The inbound signature is verified with stdlib `hmac`/`hashlib`
  /`base64`. This avoids the Twilio SDK and even a third-party HTTP client, so no
  lockfile change / cooldown / package ADR is needed.
- **Credentials from the environment only**: `TWILIO_ACCOUNT_SID`,
  `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`. Unset ⇒ `SmsNotConfigured`; sends are
  recorded as `failed` (the dev/demo default — never silently faked).
- **Inbound webhook fails closed**: `verify_twilio_signature` recomputes the
  base64 HMAC-SHA1 of `url + sorted(params)` keyed by the auth token and compares
  with `hmac.compare_digest`; a missing/invalid signature ⇒ 403. The endpoint is
  `csrf_exempt` (external caller) and unauthenticated, outside `i18n_patterns`.
- **Authorization**: sending gated by `sms.send` (recruiter/coordinator/manager);
  a coordinator may only message people on their own projects (coordinator-scoped).
  Templates are manager-managed (`sms.manage_templates`).
- **No Telegram bot** (existing manual channel), per the reconciled plan.

## Consequences

- Production-ready code now; **live sending requires the operator to set the
  Twilio env vars** and expose the webhook URL publicly. Tests mock the network
  call, so behaviour is verified without live sends or real credentials.
- Real SMS to real numbers remains behind the real-data/legal gate; until then the
  console/unconfigured path keeps everything fictional.
- If volume/features outgrow the stdlib call, revisit adopting a pinned HTTP
  client via the §3.1 approval gate.
