# Environment

Last updated: 2026-06-21

Phase 1 additions:
- New runtime dependency: `whitenoise==6.12.0`, serving collected static files under gunicorn (production settings only; ADR 0016). Hash-pinned in `runtime.lock` and `test.lock`.
- Custom user model (`AUTH_USER_MODEL = accounts.User`); deploys must run `accounts`/`audit` migrations.
- Deploy-time env vars: `JOBER_BROAD_INTERNAL_READS` (default on); `DJANGO_SESSION_COOKIE_SECURE` / `DJANGO_CSRF_COOKIE_SECURE` (default secure — only set to `0` on the HTTP-only smoke network, never on staging/production).
- Local manual testing runs the production image over HTTP with those two flags + `DJANGO_SECURE_SSL_REDIRECT` set to `0`, app published on `:8000`, against a Postgres container on a shared (non-internal) Docker network. Seed with `manage.py seed_demo` (fictional `@demo.jober.test` users). The simplest path is `scripts/dev_app.sh up` / `down`.
- i18n: English is the base language, Slovak the visible default; EN/SK/HU/UK offered (ADR 0017). gettext is not on the host or in the images — regenerate catalogs with `scripts/compile_messages.sh` (runs the app image with gettext apt-installed). `.po` (source) and `.mo` (compiled) are committed under `locale/`.

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

Local PostgreSQL:

```bash
scripts/dev_db.sh up
scripts/dev_db.sh url
scripts/dev_db.sh down
```

This uses the digest-pinned PostgreSQL image on an internal Docker network. It does not publish the DB to the host; app containers join `jober-dev-net`, and `scripts/dev_db.sh psql` starts a temporary client container for inspection.
