# ADR 0016: Serve static files with WhiteNoise under gunicorn

Status: Accepted
Date: 2026-06-21

## Context

The production image runs `gunicorn config.wsgi:application`. Gunicorn does not
serve static files, and `django.contrib.staticfiles` only serves them through the
`runserver` development command. Phase 0's smoke tests asserted only headings and
the health endpoint, so they never requested an asset — the gap stayed hidden
until Phase 1 added a real login UI and a human saw an unstyled page. Every
`/static/...` request (compiled Tailwind CSS, vendored htmx/Alpine, `app.js`) was
returning the HTML 404 page with `Content-Type: text/html`, which browsers reject
under `X-Content-Type-Options: nosniff`.

The Dokku deployment target collects static with `collectstatic` but no separate
web server (nginx) is configured to serve them.

## Decision

- Adopt **WhiteNoise 6.12.0** to serve collected static files from the WSGI app.
- Enable it in **production settings only** (`config/settings/production.py`):
  insert `whitenoise.middleware.WhiteNoiseMiddleware` immediately after
  `SecurityMiddleware`, and set the staticfiles backend to
  `whitenoise.storage.CompressedManifestStaticFilesStorage`. Local `runserver`
  serves static itself and the test suite does not need it, so base/local
  settings are left untouched (this also avoids a missing-`staticfiles/` warning
  in tests).
- Hash-pin in both `requirements/runtime.lock` and `requirements/test.lock`,
  generated in the digest-pinned Python image via `scripts/write_requirements_lock.py`.

## §3.1 approval-gate notes (new PyPI package)

- **Why not stdlib/Django:** Django cannot serve static under a WSGI server; the
  only alternatives are a separate static web server (extra infra, not present on
  the Dokku target) or WhiteNoise.
- **Maintenance/weight:** WhiteNoise is a long-established, widely used project
  with **zero runtime dependencies** (single pure-Python wheel) — minimal
  transitive surface. Adding it to `test.in` re-resolved two unrelated transitive
  point releases (`certifi`, `greenlet`); both were pinned back to their vetted
  versions so the lock change is WhiteNoise-only and no cooldown-window release
  was pulled (AGENTS.md §3 cooldown).
- **Build-time code:** installed from a wheel, no sdist build step.

## Consequences

- Static assets serve with correct content types and long-lived, fingerprinted
  cache URLs (manifest storage), so the production shell renders styled.
- A Playwright regression (`test_static_css_is_served`) now fetches the
  stylesheet and asserts `200` + `text/css`, so this cannot silently regress.
- Secure-by-default cookie/SSL settings are unchanged; WhiteNoise sits behind
  `SecurityMiddleware`.
