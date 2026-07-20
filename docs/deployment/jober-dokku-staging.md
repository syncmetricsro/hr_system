# Dokku Staging Skeleton — Jober

> Platform-wide deployment architecture (both clients, topology, asks):
> [deployment-plan.md](deployment-plan.md).

Last updated: 2026-07-15

The image and locks are approved. The concrete shared-host staging procedure,
including the planned isolated Jober app/database and `git:load-image` release
path, is maintained in [syncmetric-prime-staging.md](syncmetric-prime-staging.md).

## Intended staging shape

- Dokku app: `jober-staging`
- Database: Dokku PostgreSQL service, attached via environment variables.
- **Client selector:** `DJANGO_SETTINGS_MODULE=config.settings.production`.
  This is the Jober client; `clients.corvinum_eu.production` must never be set
  on this app.
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

`DJANGO_ALLOWED_HOSTS` contains only the hostname, for example
`jober-staging.80.211.210.46.sslip.io`, never an `https://` URL. The current
application does not read a `DJANGO_CSRF_TRUSTED_ORIGINS` environment variable;
it is not required for the same-origin HTTPS Jober staging flow. Do not add an
unused setting merely because it appears in Dokku config output.

The PostgreSQL link is the credential source. Derive `DB_NAME`, `DB_USER`,
`DB_PASSWORD`, `DB_HOST`, and `DB_PORT` from the linked `pg-jober-staging`
service on the VPS; do not paste database values into this runbook, chat, or
shell history. `DATABASE_URL` may be present from Dokku's link, but this Django
configuration intentionally reads the explicit `DB_*` values.

## Jober SMS demo configuration — separate Doppler scope

Jober is the client that uses **Twilio SMS**. Create a separate, read-only
staging Doppler configuration such as `hr_system/stg_jober-staging`; do not
reuse CorvinumEU's SMTP configuration or service token.

For the controlled Twilio Virtual Phone demonstration, synchronize only these
values into `jober-staging` at runtime:

```text
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
TWILIO_FROM_NUMBER
DEMO_SMS_PHONE
```

The basic Jober UI can start without Twilio, but the live SMS demonstration
cannot. After the public Jober staging hostname is live, configure Twilio's
inbound webhook to:

```text
https://jober-staging.80.211.210.46.sslip.io/webhooks/twilio/inbound/
```

Use only the approved test configuration and Virtual Phone while the
fictional-data gate remains in force. Never put a Doppler token into the image
or app container, and never send staging SMS to an unapproved recipient. The
`DEMO_SMS_PHONE` recipient must be distinct from `TWILIO_FROM_NUMBER`; Twilio
rejects a same-number message with error `21266`.

## Release / deploy steps

After each streamed image deployment, run on the administrative VPS account:

```bash
sudo dokku run jober-staging python manage.py migrate --noinput
sudo dokku run jober-staging python manage.py ensure_superuser
```

`ensure_superuser` is safe to re-run: it creates the Manager/Administrator
superuser if absent and otherwise leaves it (and its password) alone. The
fictional Jober seed commands are a deliberate one-time action for an
intentionally new or reset **staging demo** database; never run them against
production or a database containing real data:

```bash
for command in seed_demo seed_people seed_logistics seed_questionnaire seed_finance seed_demo_scenario; do
  sudo dokku run jober-staging python manage.py "$command"
done
```

There is no `seed_jober_demo` command in this repository. Do not make seeding
part of an automatic release phase.
Static files are baked into the image at build time (`collectstatic`) and served
by WhiteNoise, so no separate static step is needed.

## Before first staging deployment

- Create the isolated `jober-staging` app and `pg-jober-staging` database.
- Configure a separate staging hostname, Django secret, and Doppler scope; do
  not reuse CorvinumEU credentials. Add the dedicated `TWILIO_*` values only
  when the controlled SMS demonstration is ready.
- Build and stream the reviewed image from the local checkout, then migrate,
  seed fictional data, and run the HTTPS smoke check described in the shared
  runbook.
