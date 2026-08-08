# Environment

Appearance themes are entirely browser-side. Jober defaults to Light and uses
`jober-theme`; CorvinumEU defaults to Dark and uses `corvinum-theme`. Values are
`light`, `dark`, or `system` in localStorage. No environment variable, secret,
backend service, or build dependency is required.

Contextual tooltips are also entirely browser-side. They use the shared
`static/src/js/app.js`, translated template attributes, and client theme tokens;
there is no package, service, endpoint, cookie, or build dependency.

Notification delivery is interaction-driven: full page responses render the
current feed and htmx mutations trigger a fragment refresh. No polling,
WebSocket, SSE, broker, or additional runtime dependency is used.

- `DJANGO_SESSION_COOKIE_AGE` (seconds, default 2592000 = 30 days): rolling session lifetime — every request refreshes expiry (`SESSION_SAVE_EVERY_REQUEST`); only inactivity logs out. Per-client session, CSRF, and language cookie names (`jober_*` / `corvinum_*`) prevent the two apps evicting each other's state on a shared host.
- Language selection updates both the client-specific language cookie and the
  language-prefixed URL. The shared endpoint treats the current URL prefix as
  the source language when a stale or missing cookie disagrees with it; no new
  environment setting is required.

Last updated: 2026-08-05

## Secrets during human and automated testing

- Doppler project `hr_system`, config `dev`, is the local source for Twilio and
  other external-provider test credentials; `doppler.yaml` selects it without
  storing secret values.
- Any human session or automated integration check that exercises a real/test
  provider must run through `doppler run -- <committed-runner>`. That runner
  forwards only the required variables into the runtime/test container; secrets
  must never enter Docker build stages, logs, screenshots, or test artifacts.
- Example for a Twilio-enabled Jober session:
  `doppler run --project hr_system --config dev -- scripts/dev_app.sh up` (or
  `rebuild`).
- Corvinum's isolated local SMTP demo uses Doppler project `hr_system`, config
  `dev_corvinum_demo`:
  `doppler run --project hr_system --config dev_corvinum_demo -- scripts/corvinum_app.sh up`.
  The runner forwards only the required `DJANGO_EMAIL_*` variables to the web
  runtime; migrations and fictional-data seeds never receive provider secrets.
  Without that injected SMTP backend it safely uses console email. The same
  backend now serves encrypted payslips and the Manager-only structured
  job-offer email workflow; no separate mailbox variables or committed address
  are introduced. Keep `EMAIL_ALLOWED_RECIPIENTS` set to a controlled demo
  inbox whenever SMTP is used outside production. It is comma-separated, and
  since 2026-08-09 an entry beginning with `@` is a **whole domain** —
  `@mozmail.com,@jober.sk,one@example.test` mixes both forms. Domain matching is
  **exact**: `@jober.sk` allows `anna@jober.sk` and refuses
  `anna@mail.jober.sk`, so a subdomain is listed separately when it is wanted.
  An entry with no `@` is treated as an exact address nobody has, and a bare `@`
  matches nothing; `manage.py check` reports both (`mail.W002`). Empty still
  means unrestricted, which is production's setting. `SMS_ALLOWED_RECIPIENTS`
  has no equivalent — phone numbers have no domain, and its entries are
  normalised so spacing and dashes do not matter. Bulk reviews expire after
  `OFFER_EMAIL_PREVIEW_MAX_AGE` seconds (default `900`); keep the default unless
  an explicitly reviewed operating requirement changes it. The independent
  `OFFER_EMAIL_BATCH_LIMIT` default remains `100` and larger selections fail.
- `DJANGO_TWO_FACTOR_ENABLED` is the master switch for TOTP. **Default on**;
  an environment that says nothing keeps two-factor authentication. Set it to
  `0` only for a stated, time-boxed reason — a client test window where the
  office has been given passwords and a second factor would lock them out.
  While it is off, `manage.py check` reports `accounts.W001` on every deploy, so
  the exemption cannot go quiet. Turning it back on needs only the variable:
  enrolled devices are kept, so each user's second factor returns unchanged and
  nobody re-enrols.
- SMTP transport security is explicit and mutually exclusive. Providers using
  STARTTLS (normally port 587) set `DJANGO_EMAIL_USE_TLS=1` and
  `DJANGO_EMAIL_USE_SSL=0`; providers using implicit SSL (normally port 465)
  set `DJANGO_EMAIL_USE_TLS=0` and `DJANGO_EMAIL_USE_SSL=1`. Enabling both is a
  `mail.E001` configuration error and `email_configured()` fails closed.
- The `localhost:8001` runner selects `clients.corvinum_eu.local`, which disables
  TOTP entirely for fictional-data client testing, including for accounts with
  an existing confirmed device. Corvinum staging and production select
  `clients.corvinum_eu.production`; that module keeps TOTP enabled and requires
  it for managers. Never point a public deployment at the local settings module.
- The standard pytest and Playwright suites do **not** require Doppler. They
  remain deterministic and secret-free, use mocks/fakes where applicable, and
  cover fail-closed behavior when provider credentials are absent.

Phase 1 additions:
- New runtime dependency: `whitenoise==6.12.0`, serving collected static files under gunicorn (production settings only; ADR 0016). Hash-pinned in `runtime.lock` and `test.lock`.
- Custom user model (`AUTH_USER_MODEL = accounts.User`); deploys must run `accounts`/`audit` migrations.
- Deploy-time env vars: `JOBER_BROAD_INTERNAL_READS` (default on); `DJANGO_SESSION_COOKIE_SECURE` / `DJANGO_CSRF_COOKIE_SECURE` (default secure — only set to `0` on the HTTP-only smoke network, never on staging/production).
- Local manual testing runs the production image over HTTP with those two flags + `DJANGO_SECURE_SSL_REDIRECT` set to `0`, app published on `:8000`, against a Postgres container on a shared (non-internal) Docker network. Seed with `manage.py seed_demo` (fictional `@demo.jober.test` users). The simplest path is `scripts/dev_app.sh up` / `down`.
- i18n: English is the base language, Slovak the visible default; EN/SK/HU/UK
  are offered (ADR 0017). gettext is absent from the host and runtime/test
  images. Use `scripts/compile_messages.sh --extract` for safe extraction,
  translate all blank additions, run the script without arguments to validate
  and compile, then run `--check` for a read-only PO/MO synchronization check.
  Extraction temporarily installs gettext inside the app container, ignores
  tests, disables fuzzy matching, and refuses unapproved active-to-obsolete
  changes. `.po` remains the source of truth and `.mo` is committed beside
  it. **Do not invoke host `pybabel`, raw `makemessages`, or `msgmerge`:**
  they bypass the repository's domain, exclusions, and loss guards.

System:
- OS: Ubuntu 24.04.4 LTS in VirtualBox, Linux kernel `6.17.0-35-generic`.
- Workspace: `/home/disane/Development/HR_System`.
- Git: repository on branch `main`.

Available local tools observed:
- `python3`: Python 3.12.3.
- `docker`: Docker version 29.5.3, build d1c06ef.
- `rg`: available for text scans.
- `uv`: not installed.

Production stack target:
- Django 6.x, PostgreSQL, Gunicorn.
- Django templates with local htmx and Alpine assets.
- Tailwind standalone CLI v4.3.0, fetched from the pinned official Tailwind Labs release and checksum-verified before execution in Docker/CI.
- Playwright through PyPI + pytest in test environments only.
- XlsxWriter 3.2.9 for the Jober finance XLSX export, accepted in ADR 0036;
  pure Python, zero runtime transitives, exact-version and SHA-256 locked.
- Dokku staging/production deployment.

Current Phase 0 state:
- Django skeleton files are present, but Python dependencies are not installed on the host.
- Python dependencies are locked with hashes:
  - Runtime lock: `requirements/runtime.lock`.
  - Test lock: `requirements/test.lock`.
  - Locks were generated inside `python@sha256:d764629ce0ddd8c71fd371e9901efb324a95789d2315a47db7e4d27e78f1b0e9`.
- Digest-pinned images resolved:
  - Python 3.12 slim: `python@sha256:d764629ce0ddd8c71fd371e9901efb324a95789d2315a47db7e4d27e78f1b0e9`.
  - PostgreSQL 17: `postgres@sha256:2203e6282d9e7de7c24d7da234e2a744fb325df366a3fd8ed940e8abbee39527`.
  - Playwright Python test image: `mcr.microsoft.com/playwright/python:v1.60.0-noble@sha256:8ff591d613b01c884cc488339ed4318b4513eaf0c57a164a878ba49e70e3f384`.
- Vendored local JS assets:
  - htmx `2.0.4`, checksum recorded in `vendor/MANIFEST.md`.
  - Alpine `3.15.12`, checksum recorded in `vendor/MANIFEST.md`.
- Tailwind standalone CLI v4.3.0 provenance:
  - Official release: `https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.3.0`.
  - Official asset: `tailwindcss-linux-x64`.
  - Official checksum file: `https://github.com/tailwindlabs/tailwindcss/releases/download/v4.3.0/sha256sums.txt`.
  - Official Linux x64 SHA-256: `73f0e5459054e5cfaa8ab6f3b940f3fbe0f13cc7fd83bc24e7c655033c203400`.
  - Committed checksum file: `vendor/tailwind/tailwindcss-v4.3.0-linux-x64.sha256`.
  - Docker builds fetch and verify the binary in the `tailwind` stage, then copy only `static/dist/css/app.css` to the runtime image.
  - Local convenience build: `TAILWIND_BIN=/home/disane/.local/bin/tailwindcss scripts/build_tailwind.sh`.
- Production Dockerfile is present and uses the digest-pinned Python image.
- Local image built successfully as `jober-platform:phase0`.
- Temporary PostgreSQL verification passed using the digest-pinned PostgreSQL image.
- Playwright Python browser smoke passes in the digest-pinned official Playwright Python test image. The test image tag `v1.60.0-noble` matches `playwright==1.60.0` in `requirements/test.lock`. The app, test PostgreSQL, and browser runner use an internal Docker network with no outbound route. See `docs/product/playwright-test-environment-note.md`.

Forbidden local tooling:
- Do not use host Node/npm/pnpm/yarn for this project.
- Do not create `package.json`, JavaScript lockfiles, `node_modules`, React, or Vite artifacts.

Useful checks:

```bash
python3 scripts/check_no_node_artifacts.py
python3 scripts/verify_vendor_assets.py
TAILWIND_BIN=/home/disane/.local/bin/tailwindcss TAILWIND_SHA256=73f0e5459054e5cfaa8ab6f3b940f3fbe0f13cc7fd83bc24e7c655033c203400 scripts/build_tailwind.sh
docker build -t jober-platform:phase0 .
scripts/check_production_image.sh jober-platform:phase0
scripts/playwright_smoke.sh
```

GitHub runs the same containerized policy through
`.github/workflows/application-ci.yml`: `scripts/ci_quality.sh` covers
dependency/vendor integrity, no-Node checks, full-codebase Ruff lint,
incremental formatting, both client unit lanes, migration consistency, and the
production image; `scripts/playwright_e2e.sh`
covers the full two-client browser lane. The workflow deliberately performs a
minimal authenticated `git fetch` instead of using the Node-based
`actions/checkout` runtime.

Local PostgreSQL:

```bash
scripts/dev_db.sh up
scripts/dev_db.sh url
scripts/dev_db.sh down
```

This uses the digest-pinned PostgreSQL image on an internal Docker network. It does not publish the DB to the host; app containers join `jober-dev-net`, and `scripts/dev_db.sh psql` starts a temporary client container for inspection.
