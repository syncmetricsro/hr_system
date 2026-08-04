# CLAUDE.md — working in the Jober repo

Session onboarding for coding agents. **`AGENTS.md` is the binding authority**
(scope, security, supply chain, never-do list) — read it first; this file never
overrides it. Product truth lives in `Jober_Product_Design.md` (+ `Jober_Finance_Specs.md`,
`Jober_Messaging_Specs.md`); decisions in `docs/adr/` and `docs/product/`.

## State of the project (2026-07-25)

- **Phases 0–4 built and merged.** All modules live: people/lifecycle, projects/
  trials/readiness, logistics (rooms+rates, equipment+deduction review,
  transport), compliance, messaging (Twilio), intake, feedback, finance
  (line items, lock/reopen, rollups; **positive sign convention** — amounts never
  negative, net = revenue − cost), inactive reasons + recycling, and the
  **blacklist** (HMAC matching; execution gated on pending LIA/legal text).
- **Office-scoped RBAC is live for Jober (ADR 0026, Phases A+B).** Three
  offices (Velký Meder/Győr/Dunajská Streda); `Person.office`,
  `Project.office`, `Accommodation.office`, `User.offices` M2M, and a
  per-office equipment stock ledger. Every non-Observer role sees only its
  own office(s); Observer spans all by role bypass. See the RBAC convention
  below before adding any queryset. Only §3a of the ADR (office principals /
  staff invitations) is unbuilt.
- **Fictional data only** — the real-data gate has not opened. Never real PII.
- **Stages B and C are COMPLETE (ADR 0021 executed 2026-07-09; ADR 0022
  executed 2026-07-11 — deployment pends server names).** The repo is `core/` +
  `features/` + `clients/{jober,corvinum_eu,_smoke}`: policies via
  `settings.CLIENT_POLICIES`, features flag-gated (`FEATURE_FLAGS`), UI composed
  through `core/ui/registry.py` (+ per-client `CLIENT_THEME_CSS`), hooks in
  `core/projects/services.py` and `features/logistics/services.py`. Build
  discipline stands: deps **feature → core only** (`scripts/
  check_dependency_direction.py`); no client branching in core. CorvinumEU:
  `features/{checklists,advances}` (off for Jober), equipment/blacklist/
  compliance/intake reused, 2FA on for managers, seeds in
  `clients/corvinum_eu/demo` (`seed_corvinum_demo`); open client decisions in
  `docs/product/corvinum-open-questions.md`.
- Test baseline: **~654 Jober unit + ~425 CorvinumEU + 50 e2e** (2026-07-25).
  Suite counts are tracked in `test_journal.md` — update it (and
  `BUILD_JOURNAL.md`) with every slice.

## How to run things (no Python on the host — everything in pinned containers)

Provider-backed testing is opt-in and requires Doppler. Human demos or
automated integration checks that actually call Twilio/SMTP must be launched as
`doppler run -- <committed-runner>`; the runner must forward only the required
variables into the runtime/test container. Never expose provider secrets to a
Docker build stage. The normal unit and Playwright suites are intentionally
secret-free and use mocks/fakes or the app's fail-closed unconfigured path.

```bash
# Demo/dev app stack (production image + Postgres) at http://localhost:8000
scripts/dev_app.sh up|down|rebuild|status|logs     # seeds demo users + full scenario
# Twilio-enabled human session:
doppler run --project hr_system --config dev -- scripts/dev_app.sh up
# Logins: {manazer,naborar,koordinator}@demo.jober.test        -> Velký Meder
#         {manazer,naborar,koordinator}.gyor@demo.jober.test   -> Győr
#         {manazer,naborar,koordinator}.ds@demo.jober.test     -> Dunajská Streda
#         pozorovatel@demo.jober.test  -> all three (role bypass, no membership)
#   Password: demo-jober-2026 — LOCAL ONLY. Staging's accounts were rotated
#   away from this value on 2026-07-26 because this repo is public; ask the
#   owner for that one. `seed_demo` no longer resets an existing password
#   (use --reset-passwords to force it), so reseeding cannot republish it.
#   Each staff account belongs to exactly one office, so a "missing" record is
#   usually scoping. Verify office work with two managers in different offices,
#   not one: one account seeing less proves nothing on its own.

# Unit tests + lint (test image built from requirements/test.lock; needs a dev DB)
scripts/dev_db.sh up          # digest-pinned Postgres on the internal jober-dev-net
docker run --rm --network jober-dev-net \
  -e DB_HOST=jober-dev-db -e DB_NAME=jober -e DB_USER=jober -e DB_PASSWORD=<from .env.dev-db> \
  -e HOME=/tmp -e DJANGO_SETTINGS_MODULE=config.settings.local -e DJANGO_DEBUG=1 \
  -v "$PWD":/app -w /app --user "$(id -u):$(id -g)" \
  jober-test:phase4 python -m pytest -q -p no:cacheprovider --ignore=tests/e2e
#   …same container for: ruff check --no-cache core features clients config tests
#   …and: python manage.py makemigrations <app>

# Browser e2e — PRE-DEPLOY ONLY, and only when asked (see Workflow below).
# Builds the current app + Playwright image, seeds both clients, runs tests/e2e.
scripts/playwright_e2e.sh

# i18n (gettext is NOT in the runtime/test images — this script apt-installs it)
scripts/compile_messages.sh --extract   # then compile with no args
scripts/compile_messages.sh --check     # read-only PO/MO completeness check
```

## Gotchas that have actually bitten

- **Container-name collision:** `dev_db.sh` and `dev_app.sh` both use a container
  named `jober-dev-db` with *different passwords*. If `dev_app.sh up` fails with
  password-auth errors: `scripts/dev_app.sh down && scripts/dev_app.sh up`.
- **Never bypass the safe translation extractor.** Raw msgmerge fuzzy matches
  pair unrelated strings (for example, "trial waived" with "Trial failed").
  `compile_messages.sh --extract` disables fuzzy matching, excludes tests,
  refuses unreviewed active-to-obsolete changes, and does not compile.
  Translate every blank addition, then run the script without arguments.
- **Tests run under the Slovak default locale.** Assertions on translated
  strings need `translation.override("en")` (see `tests/test_i18n.py` pattern).
- **Django 6 needs `DJANGO_DEBUG=1`** (or a real `DJANGO_SECRET_KEY`) for
  management commands in the test container — base settings refuse the dev key
  when DEBUG is off.
- Long/wrapped `.po` entries (`msgid ""` + continuation lines) can't be patched
  or counted with single-line regexes — use the committed semantic checker.
- Container-created files can land root-owned; run containers with
  `--user "$(id -u):$(id -g)" -e HOME=/tmp`.
- **The full Jober suite takes ~7 minutes — give it a real timeout.** Killing it
  part-way leaves `test_jober` behind *with a live session*, and the next run
  reports hundreds of errors that are all `DuplicateDatabase` / "is being
  accessed by other users". It looks like catastrophe and is housekeeping:
  ```bash
  docker exec jober-dev-db psql -U jober -d postgres \
    -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='test_jober';" \
    -c "DROP DATABASE IF EXISTS test_jober;"
  ```

## Workflow (established, follow it)

**No pull requests** (changed 2026-08-04). Work lands through a local branch
merged locally and pushed. See the note below before "helpfully" reinstating PRs.

1. One slice per branch: `git checkout -b <slice-name>` off an up-to-date `main`.
2. Build with tests; run **ruff check *and* `ruff format --check`** plus the
   full unit suite in the container, and **`scripts/test_corvinum.sh`** (the
   corvinum-flags lane — Stage D requires both flag sets green; mark genuinely
   Jober-specific tests `@pytest.mark.jober_only`).
   **Do not run the e2e suite** — it is opt-in; see below.

   **`ruff check` is not the whole lint gate.** `scripts/ci_quality.sh` also runs
   `ruff format --check` **on the files this branch changed**, so a formatting
   diff fails CI while `ruff check` says "All checks passed" locally. Format the
   changed files only — running `ruff format` across the tree reformats ~127
   files that CI never asked about:
   ```bash
   changed=$(git diff --name-only --diff-filter=ACMR $(git merge-base HEAD main) \
     | grep -E '^(core|features|clients|config|tests|scripts)/.*\.py$')
   docker run … jober-test:phase4 ruff format --no-cache $changed
   ```
3. Update `BUILD_JOURNAL.md` + `test_journal.md` (newest-first entries).
4. Commit (imperative subject; end body with the `Co-Authored-By: Claude …`
   trailer), then land it:

```bash
git checkout main && git pull --ff-only
git merge --no-ff <slice-name>     # the merge commit groups the slice
git push
git branch -d <slice-name>
```

**Slice branches stay local — don't push them.** A branch only needed to be on
the remote so `gh pr create` had a head ref to diff; with no PRs there is
nothing to push it for, and `main` already carries every commit plus a merge
commit naming the branch. (Three branches from the old flow are still on the
remote and fully merged; they are harmless.)

**Why, so this does not get undone:** the GitHub review UI was ceremony for a
repo with one maintainer — nobody reviewed the PRs, and waiting on CI to merge
cost ~9 minutes a slice. CI still runs on every push to `main`; it now reports
*after* the fact instead of gating a merge, which makes **step 2 the real gate**.
`main` has no branch protection, so a red local run reaches `main` unopposed.

**The e2e suite is opt-in** (changed 2026-08-04). It is no longer part of the
per-slice loop and is **not** run automatically by CI. Run it **before a staging
deploy, and only when explicitly asked for** — locally with
`scripts/playwright_e2e.sh`, or in CI with `gh workflow run browser-e2e.yml`
(that workflow is `workflow_dispatch` only and never triggers itself).

## Conventions

- **Business logic lives in `core|features/<app>/services.py`** (post-B2 layout), is `@transaction.atomic`
  where it mutates, and **audits via `apps.audit.services.record_event`** —
  views stay thin and gate with `@require_action(Action.X)`.
- **RBAC:** add actions to `Action` in `core/accounts/permissions.py`, grant
  them in each client's `policies.py`, and mirror them in that client's matrix
  (`docs/permissions/{jober,corvinum}-permission-matrix.md`). Templates
  use `{% can 'action.name' %}`; hidden buttons must have server-side checks.
- **Office scoping is a second, orthogonal boundary (ADR 0026) — every new
  queryset must honour it.** Role says *what* you may do; office says *whose
  data*. Concretely, for anything you add:
  - Filter lists/aggregates through `user_office_scope(user)`
    (`core/accounts/permissions.py`), treating its `None` as "unrestricted" —
    **never** as "all offices"; an all-offices queryset still excludes rows
    whose office is unset, which is a different thing.
  - For `Person` querysets use `core/offices/scoping.py`'s `scope_people()` /
    `may_see_person()` instead of a bare `office__in`: an office-less person
    belongs to their owning recruiter, and that rule lives in one place.
  - Guard any view taking an object pk with a 403 (`_assert_*_in_scope`
    pattern, e.g. `core/people/views.py`) — filtering a list does not stop
    someone typing another office's URL.
  - Aggregates count too: a dashboard tile summing every office's rooms is
    still a cross-office read (that exact bug shipped once).
  - Blacklist is the one deliberate exception — matching and visibility stay
    company-wide, so a person blocked at one office is caught at all three.
  - CorvinumEU populates no `Office` rows, so all of this is a no-op there;
    keep it that way (data difference, never client branching).
- **Money:** `Decimal`, stored **positive** (validators enforce), totals always
  computed dynamically — never hardcode a sum.
- **i18n:** English msgids in code/templates; SK/HU/UK catalogs under `locale/`.
- **Seeds are idempotent** management commands using fictional domains
  (`demo.jober.test`, `demo.corvinum.test`); `seed_demo_scenario` /
  `seed_corvinum_demo` orchestrate demo state. **Seeded catalog labels are
  canonical English rendered via `|db_trans`** with msgids registered in
  per-app `catalog_i18n.py` — full pattern: `docs/i18n-seeded-data.md`.
- **Migrations:** generate in the test container; data migrations get a reverse
  function; never edit an applied migration.
- **New PyPI deps need an ADR + human approval** (AGENTS.md §3.1 — cooldown,
  hash-pinned locks). Prefer stdlib/Django; e.g. Twilio is called via `urllib`,
  not an SDK.

## Where answers live

- **Docs index (per-client naming convention): `docs/README.md`** — unprefixed
  = platform-shared; `jober-`/`corvinum-` prefixes mark client ownership.

- Open/answered client questions: `docs/product/jober-phase3-4-open-questions.md`
  (all five answered; blacklist real-use pends LIA + written text —
  `docs/security/jober-blacklist-legal-basis.md`).
- Demos: Jober `docs/deployment/jober-demo-runbook.md` (+ `jober-local-demo.md`, port 8000); CorvinumEU `docs/deployment/corvinum-demo-runbook.md` (`scripts/corvinum_app.sh`, port 8001; both stacks run side-by-side).
- Platform docs: `docs/platform/{extraction-matrix,extraction-plan,corvinumeu-peopleops-design}.md` — **Stages B+C are built** (ADRs 0021/0022/0023); these are the plans of record, not gates. Still gated: real deployment (server names, C-Q14) and everything behind the real-data/legal gate. CorvinumEU open decisions: `docs/product/corvinum-open-questions.md`.
- Deployment: `docs/deployment/deployment-plan.md` (Dokku/VPS, both clients, asks D1–D8); journals `deployment_journal.md`, `ENVIRONMENT.md`.
