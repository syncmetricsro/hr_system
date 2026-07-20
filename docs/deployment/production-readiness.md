# Production Readiness Journal

Tracks what must be true before the Jober app serves real users/data, and the
state of each gate. "Ready" = verified; "Open" = not done / needs a human or an
external input. Update this whenever a gate changes state.

Last updated: 2026-06-29

## Serving & runtime

| Gate | State | Notes |
|---|---|---|
| Static files served in production | ✅ Ready (2026-06-21) | WhiteNoise under gunicorn (ADR 0016). Regression test `test_static_css_is_served`. Found because Phase 0 smoke never requested an asset. |
| HTTPS + secure cookies on real host | ⚠️ Open | `SECURE_SSL_REDIRECT`/`SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE` default secure; **must not** set the `DJANGO_*_=0` overrides on staging/prod (those exist only for the HTTP smoke network). Verify once Dokku TLS is live. |
| Dokku staging deploy | ⚠️ Open | Blocked on external staging app/domain/PostgreSQL service names. Runbook: `docs/deployment/jober-dokku-staging.md`. |
| DB migrations on deploy | ✅ Ready | `accounts`/`audit` initial migrations run cleanly on pinned PostgreSQL 17. |
| Initial admin user | ✅ Ready (2026-06-21) | `manage.py ensure_superuser` — idempotent, env-driven (`DJANGO_SUPERUSER_EMAIL`/`_PASSWORD`), audited; wired into the Dokku release steps (`docs/deployment/jober-dokku-staging.md`). `seed_demo` remains fictional/staging only — never against a real-data DB. |
| Secret management | 🟡 Partial (2026-06-29) | **Doppler** is the secrets source (project `hr_system`, config `dev`); `doppler run --project hr_system --config dev -- scripts/dev_app.sh up` injects env locally (`doppler.yaml`, `docs/deployment/jober-twilio-setup.md`). Still to confirm: prod Doppler config + Dokku wiring (sync or service token) and `DJANGO_SECRET_KEY`/DB-cred rotation. |
| DB backups / restore | ⚠️ Open | Not yet defined for the Dokku PostgreSQL service. |

## Integrations

| Gate | State | Notes |
|---|---|---|
| Twilio SMS | 🟡 Verified live (2026-06-29) | End-to-end delivery confirmed through the app using live credentials via Doppler and a controlled Twilio Virtual Phone recipient; no phone values are recorded here. Code: stdlib client, signature-verified webhook (ADR 0019). **Remaining (ops, not code):** use a recipient distinct from the configured sender (Twilio rejects same-number attempts with `21266`), upgrade the account to allow non-verified recipients, and point the inbound webhook at public staging/TLS. Real worker numbers stay behind the real-data gate. |

## Product / legal gates (block real data, not code)

| Gate | State | Notes |
|---|---|---|
| Real worker PII | ⚠️ Open (blocked) | Fictional data only until the legal/security real-data gate (Handoff.md, AGENTS.md). |
| DPA / EU hosting / blacklist legal basis / leasing docs | ⚠️ Open | Lawyer items; block go-live, not coding. |
| Finance sign convention | ⚠️ Open | Needs one filled month (Phase 4). |
| Translation catalogs (EN/SK/HU/UK) | ⚠️ Partial (2026-06-23) | English base language; SK/HU/UK catalogs compiled and shipped (ADR 0017). All four render. **HU/UK + revised SK are AI-authored — need a fluent-speaker review** before client-facing use. Recompile via `scripts/compile_messages.sh`. |

## RBAC / audit posture

| Gate | State | Notes |
|---|---|---|
| Action-gated RBAC with broad reads | ✅ Ready | `apps/accounts/permissions.py`, mirrored by `docs/permissions/jober-permission-matrix.md` (ADR 0008/0015). |
| Append-only audit | ✅ Ready | `apps/audit` immutable `AuditEvent`; wired into login/logout. Extend `record_event` to every sensitive action as modules land. |
| Recruiter/coordinator read-scope (GDPR) | ⚠️ Open | Held configurable behind `BROAD_INTERNAL_READS`; do not hardcode a split until Jober confirms. |
