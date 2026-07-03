# Security review — 2026-06-29

Scope: internal review of the auth / RBAC / PII / endpoint surface as it stands
after the Phase 3–4 slices (finance, accommodation pricing, equipment review,
inactive/recycle, reports). This is an internal engineering review, **not** an
external audit or the Phase 5 acceptance security review.

## Conclusion

**No high- or medium-severity issues found.** The posture is strong:
action-gated RBAC that fails closed, object-scoped sensitive-field visibility,
CSRF on all state-changing forms, a fail-closed HMAC-verified webhook, hardened
production settings, and secrets kept in the environment. Three low-severity /
decision-point observations are listed below.

## What was reviewed and found sound

- **RBAC** (`apps/accounts/permissions.py`). `require_action` redirects anonymous
  users to login and raises `PermissionDenied` (403) for authenticated-but-denied
  — fail closed. `can()` is role → allowed-actions with an explicit superuser
  bypass and a safe `Role()` parse (unknown role → no access). Writes/sensitive
  reads are gated; ordinary reads are broad by design (ADR 0008).
- **Sensitive fields** (`apps/people/permissions.can_view_sensitive`). DOB /
  place of birth / disability are object-scoped to managers, observers, the
  owning recruiter, and the responsible coordinator(s); hidden from unconnected
  recruiters/coordinators. Templates gate on `show_sensitive`, so hidden data is
  backed by a server-side check (not just CSS).
- **CSRF**. Django protection is active; every POST form emits `{% csrf_token %}`.
  The only `@csrf_exempt` is the Twilio inbound webhook, which is compensated by
  an `X-Twilio-Signature` HMAC-SHA1 check using `hmac.compare_digest`
  (constant-time) and **fails closed** when the token or signature is missing
  (`apps/messaging/views.twilio_inbound`, `services.verify_twilio_signature`).
- **Injection / XSS**. No raw SQL (`.raw`/`.extra`), no `eval`/`exec`, no
  `mark_safe`/`|safe` in app code or templates — Django autoescaping is intact
  and the ORM parameterises queries.
- **Secrets & settings**. No credentials in the repo (Twilio/DB via env; the
  dev-only `SECRET_KEY` default is guarded to refuse boot when `DEBUG` is off).
  Production settings: `DEBUG=False`, `SECURE_SSL_REDIRECT`, HSTS (1y, subdomains,
  preload), secure session/CSRF cookies, `SECURE_PROXY_SSL_HEADER`.
- **Audit / PII in logs**. `record_event` stores actor + target type/id +
  catalog labels/reasons — no raw worker PII (names, identifiers) in audit
  metadata; no `print`/logger calls emit PII.
- **Data policy**. Fictional-only seed data (fictional demo domain asserted in
  `seed_demo`); no real PII before the legal/real-data gate.

## Observations (low severity / decisions)

1. **Cost figures are visible under broad read.** Accommodation `monthly_rate`
   (accommodation detail + the person card's `effective_rate`) and the equipment
   `charge_amount` review badge render for any authenticated internal role, while
   the *aggregate* cost reports are manager-gated (`accommodation.manage`,
   `equipment.review_deduction`). Per ADR 0008 (broad internal reads; only
   sensitive *fields* are restricted, and cost is not classified sensitive) this
   is consistent-by-design — but it is inconsistent with gating the reports.
   **Decision point:** if per-worker/room cost figures should be management-only,
   gate those inline displays behind the same manager check. Internal-only
   exposure; not externally reachable.

2. **Webhook absolute-URL under a proxy.** The Twilio signature base is built
   from `request.build_absolute_uri()`. `SECURE_PROXY_SSL_HEADER` is set so the
   scheme resolves to `https` behind the Dokku/TLS proxy; ensure the webhook URL
   configured in Twilio **exactly matches** the public host (and `ALLOWED_HOSTS`)
   so signatures validate. Mismatch fails closed (rejects valid inbound) — a
   functional risk, not a vulnerability. (Multi-valued POST params would use the
   last value in the signature base; Twilio params are single-valued, so this is
   negligible.)

3. **Feedback link token** is `uuid4().hex[:12]` (48 bits). Fine for
   low-sensitivity QR feedback links; do not reuse this token scheme for anything
   that gates sensitive data.

## Not in scope / deferred

- External penetration test and the Phase 5 acceptance security review.
- Object-level authorization on operational *writes* (e.g. a coordinator may act
  on a person outside their projects): this is the intended action-gated model
  (ADR 0008, "offices are filters, not access boundaries"), not a finding.
- Blacklist module (unbuilt, blocked on the Q3 legal answer) — to be reviewed
  when it lands, given it will hold the most sensitive data.
