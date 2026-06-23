# Dokku Staging Skeleton

Last updated: 2026-06-17

This is a runbook placeholder until the container base-image digests and Python dependency lock are approved.

## Intended staging shape

- Dokku app: `jober-staging`
- Database: Dokku PostgreSQL service, attached via environment variables.
- Runtime: Django + Gunicorn, image built from `python@sha256:d764629ce0ddd8c71fd371e9901efb324a95789d2315a47db7e4d27e78f1b0e9`.
- Static files: built in container, collected with `collectstatic`.
- Tailwind: build-stage only with verified standalone CLI v4.3.0; binary excluded from runtime.
- Playwright browsers: test environment only; excluded from runtime.

## Required secrets

Set these through Dokku config, never Git:

```bash
dokku config:set jober-staging \
  DJANGO_SETTINGS_MODULE=config.settings.production \
  DJANGO_SECRET_KEY=<generated-secret> \
  DJANGO_ALLOWED_HOSTS=<staging-domain> \
  DB_NAME=<dokku-db-name> \
  DB_USER=<dokku-db-user> \
  DB_PASSWORD=<dokku-db-password> \
  DB_HOST=<dokku-db-host> \
  DB_PORT=5432 \
  DJANGO_SUPERUSER_EMAIL=<admin-email> \
  DJANGO_SUPERUSER_PASSWORD=<admin-password>
```

Do **not** set `DJANGO_SECURE_SSL_REDIRECT`, `DJANGO_SESSION_COOKIE_SECURE`, or
`DJANGO_CSRF_COOKIE_SECURE` here — they default to secure and must stay on for a
real (HTTPS) deployment. The `=0` overrides exist only for the local HTTP demo.

## Release / deploy steps

Run on each deploy (e.g. Dokku release phase / `app.json` predeploy):

```bash
python manage.py migrate --noinput
python manage.py ensure_superuser   # idempotent; creates the admin from the env vars above
```

`ensure_superuser` is safe to re-run: it creates the Manager/Administrator
superuser if absent and otherwise leaves it (and its password) alone. Do **not**
run `seed_demo` against staging/production — it creates fictional users only.
Static files are baked into the image at build time (`collectstatic`) and served
by WhiteNoise, so no separate static step is needed.

## Blocked before deployment

- Confirm the Dokku PostgreSQL service name and staging domain.
- Push/deploy the already-building Docker image path to staging.
