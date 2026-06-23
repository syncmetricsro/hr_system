# Production Readiness Journal

Tracks what must be true before the Jober app serves real users/data, and the
state of each gate. "Ready" = verified; "Open" = not done / needs a human or an
external input. Update this whenever a gate changes state.

Last updated: 2026-06-21

## Serving & runtime

| Gate | State | Notes |
|---|---|---|
| Static files served in production | ✅ Ready (2026-06-21) | WhiteNoise under gunicorn (ADR 0016). Regression test `test_static_css_is_served`. Found because Phase 0 smoke never requested an asset. |
| HTTPS + secure cookies on real host | ⚠️ Open | `SECURE_SSL_REDIRECT`/`SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE` default secure; **must not** set the `DJANGO_*_=0` overrides on staging/prod (those exist only for the HTTP smoke network). Verify once Dokku TLS is live. |
| Dokku staging deploy | ⚠️ Open | Blocked on external staging app/domain/PostgreSQL service names. Runbook: `docs/deployment/dokku-staging.md`. |
| DB migrations on deploy | ✅ Ready | `accounts`/`audit` initial migrations run cleanly on pinned PostgreSQL 17. |
| Initial admin user | ⚠️ Open | No production superuser path yet. `seed_demo` is **fictional/staging only** — never run against a real-data DB. Need a documented `createsuperuser` step (custom email user) for go-live. |
| Secret management | ⚠️ Open | `DJANGO_SECRET_KEY` and DB creds via env; confirm Dokku secret storage and rotation before prod. |
| DB backups / restore | ⚠️ Open | Not yet defined for the Dokku PostgreSQL service. |

## Product / legal gates (block real data, not code)

| Gate | State | Notes |
|---|---|---|
| Real worker PII | ⚠️ Open (blocked) | Fictional data only until the legal/security real-data gate (Handoff.md, AGENTS.md). |
| DPA / EU hosting / blacklist legal basis / leasing docs | ⚠️ Open | Lawyer items; block go-live, not coding. |
| Finance sign convention | ⚠️ Open | Needs one filled month (Phase 4). |
| Translation catalogs (HU/UK) | ⚠️ Open | i18n wired; catalogs not compiled (gettext not in toolchain). Non-default languages fall back to Slovak source. |

## RBAC / audit posture

| Gate | State | Notes |
|---|---|---|
| Action-gated RBAC with broad reads | ✅ Ready | `apps/accounts/permissions.py`, mirrored by `docs/permissions/permission-matrix.md` (ADR 0008/0015). |
| Append-only audit | ✅ Ready | `apps/audit` immutable `AuditEvent`; wired into login/logout. Extend `record_event` to every sensitive action as modules land. |
| Recruiter/coordinator read-scope (GDPR) | ⚠️ Open | Held configurable behind `BROAD_INTERNAL_READS`; do not hardcode a split until Jober confirms. |
