# Deployment Journal

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
