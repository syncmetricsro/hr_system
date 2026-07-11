# Phase 0 Risk And Blocker List

Last updated: 2026-06-21

## Active workstation blockers

- None. (Translation catalogs are now generated/compiled — English base language with SK/HU/UK catalogs, ADR 0017. gettext runs via `scripts/compile_messages.sh` against the app image, not the host. HU/UK + revised SK still need a fluent-speaker review before client use — tracked in the production readiness journal.)

## Server deployment pending

- Dokku staging remains a server task once the staging app/domain/PostgreSQL service names are available.

## Current safe progress

- Node/npm artifacts were removed from tracked production files.
- Django skeleton, local templates, local htmx/Alpine assets, checksum verification, and no-Node policy check are in place.
- Tailwind standalone CLI v4.3.0 provenance is pinned to the official Tailwind Labs `tailwindcss-linux-x64` release asset and official `sha256sums.txt`. Docker fetches and verifies it in a build stage, then excludes the binary from runtime.
- Runtime and test Python dependency locks were generated inside the digest-pinned Python 3.12 container and verified with `pip install --require-hashes`.
- A production Dockerfile was added using `python@sha256:d764629ce0ddd8c71fd371e9901efb324a95789d2315a47db7e4d27e78f1b0e9`.
- The production image built successfully as `jober-platform:phase0`.
- A temporary PostgreSQL 17 container using `postgres@sha256:2203e6282d9e7de7c24d7da234e2a744fb325df366a3fd8ed940e8abbee39527` accepted Django migrations, and `/healthz/` returned `ok` from the running container.
- Local PostgreSQL helper `scripts/dev_db.sh` uses the same digest-pinned Postgres image, an internal Docker network, gitignored credentials, containerized `psql`, and disposable reset.
- Non-browser Django smoke tests passed in the hash-pinned test environment.
- Playwright browser smoke passed in the digest-pinned official Playwright Python test image on an internal-only Docker network with app, DB, and runner containers.
- The shell uses fictional project-level data only and does not introduce business migrations.

## Recommended next Phase 1 task

The foundation slice (authentication, four-role action-gated RBAC, localization wiring, append-only audit, fictional seed/reset) is done and green (see 2026-06-21 build/test journal entries). Next: the Phase 1 business spine — project administration and the Person model + lifecycle-status state machine — then hard-gated recruiter intake. Each new view must adopt `require_action`/`{% can %}` and record sensitive changes via `record_event`, and must keep recruiter/coordinator read scope configurable (do not hardcode the GDPR split).
