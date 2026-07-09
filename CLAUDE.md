# CLAUDE.md — working in the Jober repo

Session onboarding for coding agents. **`AGENTS.md` is the binding authority**
(scope, security, supply chain, never-do list) — read it first; this file never
overrides it. Product truth lives in `Product_Design.md` (+ `Finance_Specs.md`,
`Messaging_Specs.md`); decisions in `docs/adr/` and `docs/product/`.

## State of the project (2026-07-05)

- **Phases 0–4 built and merged.** All modules live: people/lifecycle, projects/
  trials/readiness, logistics (rooms+rates, equipment+deduction review,
  transport), compliance, messaging (Twilio), intake, feedback, finance
  (line items, lock/reopen, rollups; **positive sign convention** — amounts never
  negative, net = revenue − cost), inactive reasons + recycling, and the
  **blacklist** (HMAC matching; execution gated on pending LIA/legal text).
- **Fictional data only** — the real-data gate has not opened. Never real PII.
- **Stage B is ACTIVE (ADR 0021 activated 2026-07-07).** The repo is being
  restructured to `core/` + `features/` + `clients/` per
  `docs/platform/extraction-plan.md` (slices B0–B5). Build discipline: deps
  point **feature → core only**; the core never branches on client identity;
  moved apps keep their directory basenames (labels/tables untouched). Demo
  fallback: tag `pre-stage-b`; don't rebuild the demo container mid-extraction.
- Test baseline: **226 unit + 16 e2e**. Suite counts are tracked in
  `test_journal.md` — update it (and `BUILD_JOURNAL.md`) with every slice.

## How to run things (no Python on the host — everything in pinned containers)

```bash
# Demo/dev app stack (production image + Postgres) at http://localhost:8000
scripts/dev_app.sh up|down|rebuild|status|logs     # seeds demo users + full scenario
# Logins: {manazer,naborar,koordinator,pozorovatel}@demo.jober.test / demo-jober-2026

# Unit tests + lint (test image built from requirements/test.lock; needs a dev DB)
scripts/dev_db.sh up          # digest-pinned Postgres on the internal jober-dev-net
docker run --rm --network jober-dev-net \
  -e DB_HOST=jober-dev-db -e DB_NAME=jober -e DB_USER=jober -e DB_PASSWORD=<from .env.dev-db> \
  -e HOME=/tmp -e DJANGO_SETTINGS_MODULE=config.settings.local -e DJANGO_DEBUG=1 \
  -v "$PWD":/app -w /app --user "$(id -u):$(id -g)" \
  jober-test:phase4 python -m pytest -q -p no:cacheprovider --ignore=tests/e2e
#   …same container for: ruff check --no-cache core features clients config tests
#   …and: python manage.py makemigrations <app>

# Browser e2e (builds current app + Playwright images, seeds, runs tests/e2e)
scripts/playwright_e2e.sh

# i18n (gettext is NOT in the runtime/test images — this script apt-installs it)
scripts/compile_messages.sh --extract   # then compile with no args
```

## Gotchas that have actually bitten

- **Container-name collision:** `dev_db.sh` and `dev_app.sh` both use a container
  named `jober-dev-db` with *different passwords*. If `dev_app.sh up` fails with
  password-auth errors: `scripts/dev_app.sh down && scripts/dev_app.sh up`.
- **msgmerge fuzzy matches are wrong more often than right.** After
  `--extract`, check every new msgid: fuzzies pair unrelated strings (e.g.
  "Reject" → "Projekt"). Fix the msgstr *and* remove the `#, fuzzy` flag (it may
  sit 1–3 lines above the msgid with `#|` lines between).
- **Tests run under the Slovak default locale.** Assertions on translated
  strings need `translation.override("en")` (see `tests/test_i18n.py` pattern).
- **Django 6 needs `DJANGO_DEBUG=1`** (or a real `DJANGO_SECRET_KEY`) for
  management commands in the test container — base settings refuse the dev key
  when DEBUG is off.
- Long/wrapped `.po` entries (`msgid ""` + continuation lines) can't be patched
  with single-line regexes — handle the wrapped block explicitly.
- Container-created files can land root-owned; run containers with
  `--user "$(id -u):$(id -g)" -e HOME=/tmp`.

## Workflow (established, follow it)

1. One slice per branch: `git checkout -b <slice-name>` off `main`.
2. Build with tests; run **ruff + full unit suite** in the container; e2e if UI/URLs changed.
3. Update `BUILD_JOURNAL.md` + `test_journal.md` (newest-first entries).
4. Commit (imperative subject; end body with the `Co-Authored-By: Claude …` trailer),
   push, `gh pr create`, then `gh pr merge --merge --delete-branch`, and
   fast-forward local `main`.

## Conventions

- **Business logic lives in `core|features/<app>/services.py`** (post-B2 layout), is `@transaction.atomic`
  where it mutates, and **audits via `apps.audit.services.record_event`** —
  views stay thin and gate with `@require_action(Action.X)`.
- **RBAC:** add actions to `Action` + `ACTION_ROLES` in
  `core/accounts/permissions.py` and mirror them in
  `docs/permissions/permission-matrix.md` (tests assert the mapping). Templates
  use `{% can 'action.name' %}`; hidden buttons must have server-side checks.
- **Money:** `Decimal`, stored **positive** (validators enforce), totals always
  computed dynamically — never hardcode a sum.
- **i18n:** English msgids in code/templates; SK/HU/UK catalogs under `locale/`.
- **Seeds are idempotent** management commands using the fictional
  `demo.jober.test` domain; `seed_demo_scenario` orchestrates the full demo state.
- **Migrations:** generate in the test container; data migrations get a reverse
  function; never edit an applied migration.
- **New PyPI deps need an ADR + human approval** (AGENTS.md §3.1 — cooldown,
  hash-pinned locks). Prefer stdlib/Django; e.g. Twilio is called via `urllib`,
  not an SDK.

## Where answers live

- Open/answered client questions: `docs/product/phase3-4-open-questions.md`
  (all five answered; blacklist real-use pends LIA + written text —
  `docs/security/blacklist-legal-basis.md`).
- Demo: `docs/deployment/demo-runbook.md` (+ `local-demo.md`).
- Platform future: `docs/platform/{extraction-matrix,extraction-plan,corvinumeu-peopleops-design}.md` — **gated, do not build**.
- Deployment/ops journals: `deployment_journal.md`, `ENVIRONMENT.md`.
