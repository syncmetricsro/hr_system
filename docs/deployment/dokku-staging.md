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
  DB_PORT=5432
```

## Blocked before deployment

- Confirm the Dokku PostgreSQL service name and staging domain.
- Push/deploy the already-building Docker image path to staging.
