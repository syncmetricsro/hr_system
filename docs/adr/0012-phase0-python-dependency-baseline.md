# ADR 0012: Phase 0 Python Dependency Baseline

Status: Accepted

## Context

Phase 0 needs enough Python packages to run the Django shell, connect to PostgreSQL, serve through Gunicorn, and execute smoke tests without Node/npm.

## Decision

Use this initial direct dependency set:

Runtime:
- `Django==6.0.6`
- `gunicorn==26.0.0`
- `psycopg==3.3.4`
- `psycopg-binary==3.3.4`

Test:
- all runtime packages above;
- `pytest==9.1.0`
- `pytest-django==4.12.0`
- `playwright==1.60.0`
- `pytest-playwright==0.8.0`
- `ruff==0.15.17`

The transitive dependency trees are locked in:
- `requirements/runtime.lock`
- `requirements/test.lock`

Both locks were generated inside the digest-pinned Python 3.12 container and verified with `pip install --require-hashes`.

## Consequences

Playwright and Ruff are test-only and are not installed into the production runtime image.

`psycopg-binary` is accepted for the initial containerized deployment to avoid adding OS package installation to the production image. If the team later wants source-built `psycopg` against system `libpq`, that requires a separate ADR and reviewed OS package list.
