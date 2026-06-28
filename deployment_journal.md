# Deployment Journal

## 2026-06-21

Phase 1 deployment-relevant changes.

- **Static serving fixed (production-readiness).** The production image runs gunicorn, which does not serve static files; nothing else did either, so all `/static/...` assets returned the HTML 404 page (`text/html`) and the shell rendered unstyled. Adopted WhiteNoise (ADR 0016): middleware + `CompressedManifestStaticFilesStorage` in production settings only; hash-pinned in `runtime.lock`/`test.lock`. Verified the live image serves `app.css` as `200 text/css` with a fingerprinted URL. A Playwright regression now guards it. See `docs/deployment/production-readiness.md`.
- **Deploy steps now include migrations:** `accounts` and `audit` initial migrations must run on deploy (custom `AUTH_USER_MODEL`).
- **New deploy-time env vars:** `JOBER_BROAD_INTERNAL_READS` (default on), and `DJANGO_SESSION_COOKIE_SECURE` / `DJANGO_CSRF_COOKIE_SECURE` (default **secure**). The `=0` overrides exist only for the HTTP-only smoke network and must never be set on staging/production.
- **No production superuser path yet** — `seed_demo` creates fictional users for local/staging only and must not run against a real-data DB. A `createsuperuser` (custom email user) step is required before go-live.

Correction to the 2026-06-17 entry below: its "Current blocker" (Python lock + digest-pinned base images) was **resolved later in Phase 0** — `Dockerfile`, hash-pinned `runtime.lock`/`test.lock`, and digest-pinned Python/PostgreSQL/Playwright images all landed and the image builds/migrates/serves. The remaining deployment blocker is Dokku staging, pending external app/domain/PostgreSQL service names.

## 2026-06-17

Phase 0 production deployment direction:
- The static demo deployment notes below are historical and apply only to the old design reference.
- Production target is a Jober-only Django app deployed to Dokku with PostgreSQL.
- Added `docs/deployment/dokku-staging.md` as the staging shell/runbook.
- No Dockerfile was added yet because `AGENTS.md` requires base images pinned by digest, and those digests have not been resolved from a trusted source.
- No Tailwind binary was added; `vendor/tailwind/REQUEST.md` records the human-supplied artifact and checksum requirement.
- No Python dependency install was run on the host.

Current blocker:
- Generate the hash-pinned Python dependency lock and choose digest-pinned base images inside an approved container/CI path before staging can run.

## 2026-06-13

Current deployment method:
- Static files only.
- Primary previews:
  - Internal combined build: open `demo/internal/index.html`.
  - CorvinumEU client build: open `demo/corvinum/index.html`.
  - Jober client build: open `demo/jober/index.html`.
- Optional local server: run `python3 -m http.server` from `demo/`, then open:
  - `http://127.0.0.1:8000/internal/`
  - `http://127.0.0.1:8000/corvinum/`
  - `http://127.0.0.1:8000/jober/`

Verified today:
- The demo is split into the three static build folders above.
- Browser verification is recorded in `test_journal.md`.

No deployment artifacts, backend service, package files, or build output are required.
