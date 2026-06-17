# Jober Workforce Platform

Production Django application for Jober's internal workforce-management platform.

The current work is Phase 0: source reconciliation, npm-free Django skeleton, local assets, containerized checks, and architecture decisions. The old static demo remains a design reference only.

Hard constraints:
- Jober only.
- No Node.js, npm, pnpm, yarn, React, Vite, package files, JavaScript lockfiles, or `node_modules`.
- Django owns routing, rendering, validation, authorization, persistence, and workflow state.
- htmx and Alpine are vendored local assets with checksums.
- Tailwind standalone CLI is fetched from the pinned official Tailwind Labs release, verified against the official checksum, and kept out of the runtime image.

Local PostgreSQL is available through `scripts/dev_db.sh` without installing PostgreSQL on the host. See [ENVIRONMENT.md](ENVIRONMENT.md) and [docs/deployment/local-dev-db.md](docs/deployment/local-dev-db.md).
