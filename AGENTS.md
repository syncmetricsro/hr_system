# AGENTS.md — Jober Workforce Platform

Binding instructions for any coding agent working in this repository. If a rule here conflicts with a task, **follow the rule and say why**.

This file governs **scope, security, supply chain, and how to work**. The **what to build** lives in the implementation plan (`jober_coding_agent_product_design_plan_v3_jober_only.md`) and the Jober v0.4 interview delta. When this file and the plan disagree on *security or dependencies*, this file wins.

---

## 0. Project state (read first)

- This repository is the **real Jober production application**, not the old demo. The static vanilla-JS demo was a design reference only; its "install nothing / no backend" rules no longer apply here.
- Scope is **Jober only**. Do not introduce CorvinumEU, multi-client abstractions, white-label infrastructure, shift scheduling, fleet/vehicles, sick leave, worker portal, or Pohoda. They are out of scope by decision, not by omission.
- Stack is **npm-free by decision**: Django + htmx + Alpine.js + Tailwind standalone CLI + Playwright-Python + PostgreSQL + Dokku. There is **no Node.js, no npm, no React, no Vite** anywhere in the repository, build, or runtime.

---

## 1. Golden rules (non-negotiable)

1. **Never add Node.js, npm, pnpm, yarn, `package.json`, a JS lockfile, or `node_modules`** — anywhere, ever. The production image must build with no Node toolchain present.
2. **Every dependency is pinned and verified.** Python packages are hash-pinned in a committed lockfile; vendored JS assets and downloaded binaries are SHA-256-verified and fail closed on mismatch.
3. **Installs and builds run inside the container/CI, never against host secrets.** No build step ever has access to production credentials, SSH keys, or the deploy token.
4. **Minimal dependencies.** Adding any new PyPI package requires an ADR and human approval. Default to the standard library and Django's batteries before reaching for a package.
5. **No secrets in Git.** Provider credentials (Twilio, Telegram, SMTP, database) come from environment / a secret manager, never committed.
6. **The agent does not fetch media or secrets.** It writes an asset/secret *request* and a runbook; a human supplies binaries, fonts, images, and credentials (see §7).
7. **When a business decision is missing, stop and write a decision note.** Do not fossilize a guess into a migration and make humans excavate it later.
8. **Small, reviewable PRs**, tests with every business-critical change, permissions + audit treated as part of each feature.

---

## 2. Stack constraints

**Use:**
- Python; Django 6.x pinned to a supported release; PostgreSQL; Gunicorn.
- Django templates, forms/formsets, sessions, localization, management commands.
- Server-side authorization on every protected action. Django owns routing, rendering, validation, authorization, workflow state, and persistence.
- **htmx** (vendored, pinned, checksummed) for server-driven interaction.
- **Alpine.js** (vendored, pinned, checksummed) for narrow local UI state only — never persisted data, permissions, calculations, or workflow.
- **Tailwind standalone CLI** for CSS (no PostCSS/Sass/Node).
- **Playwright via PyPI + pytest** for browser tests.

**Never use:** Node/npm/React/Vite/SPA framework; a general browser REST API (JSON endpoints need a demonstrated external-integration need + ADR); CDN-hosted runtime assets.

---

## 3. Supply-chain hardening

The whole point of this stack is a small, auditable dependency surface. Keep it that way.

### 3.1 Python / PyPI

- **Hash-pinned, fully-locked dependencies.** Use `uv` (or pip-tools) to produce a lockfile with hashes for the full transitive tree. Install with hash enforcement (`uv pip sync` / `pip install --require-hashes`). A resolved-but-unhashed install is not acceptable.
- **Exact version pins** for direct dependencies; no floating ranges (`>=`, `^`, `~`) in the committed lock.
- **Commit the lockfile.** CI installs **only** from the committed lockfile; it never re-resolves freely.
- **Cooldown.** Do not adopt a package version published less than ~3 days ago without explicit human approval. Newly published versions are the highest-risk window (compromised-maintainer pushes).
- **Build-script caution.** Treat `setup.py` / build-backend execution as install-time code execution (the PyPI analogue of an npm postinstall). Prefer wheels over sdists; review any dependency that runs significant code at install/build.
- **Approval gate.** New PyPI package → ADR stating why the standard library / Django can't do it, who maintains the package, and its transitive weight. No silent `uv add`.
- **Installs happen inside the container build only.** Never `pip install` on a host that holds secrets.
- **No pipe-to-shell** (`curl … | sh`) for anything, ever. No global installs.

### 3.2 Vendored frontend assets (htmx, Alpine)

- Vendored as **local files in the repo**, never CDN-loaded.
- Pin exact versions; keep a **checked-in SHA-256 manifest**; CI **re-verifies and fails closed** on mismatch.
- Record source URL, version, license, and retrieval date in a `vendor/MANIFEST.md`.
- Upgrades happen through a deliberate PR that updates the file and the manifest hash together.

### 3.3 Downloaded binaries (Tailwind standalone CLI, Playwright browsers)

These replaced npm packages but are still supply-chain artifacts — treat them as such.

- **Tailwind standalone CLI:** pin to **v4.3.0**, official Tailwind Labs release asset `tailwindcss-linux-x64`, SHA-256 `73f0e5459054e5cfaa8ab6f3b940f3fbe0f13cc7fd83bc24e7c655033c203400` from that release's `sha256sums.txt`. CI/Docker fetches it from the pinned release URL, verifies SHA-256 **before executing**, and **fails closed** on mismatch. Build CSS in a build stage; **exclude the binary from the runtime image**. Permit a `TAILWIND_BIN` override for local convenience only; never depend on a developer's workstation install in CI or Dokku.
- **Playwright browsers:** installed via `python -m playwright install` in the **test environment only**. Never present in the production runtime image. Pin the Playwright version in the lockfile.

### 3.4 Containers & CI

- **Base images pinned by digest** (`@sha256:…`), not tags like `latest` or `6`.
- **GitHub Actions pinned by commit SHA**, not by floating tag.
- Build inside the container; no host secrets in the build context.
- CI gates: ruff/format, pyright/type-check, pytest, Playwright smoke, migration consistency, **dependency hash verification**, **vendored-asset checksum verification**, secret scan, production image builds **without Node/npm**.

### 3.5 Secrets & messaging providers (Twilio, Telegram, SMTP, DB)

- All credentials via environment / approved secret manager. **No committed `.env`** with real values (`.env.example` with placeholders only).
- **Verify inbound webhooks.** Twilio: validate the `X-Twilio-Signature`. Telegram: set and check a secret webhook token (and restrict to Telegram's IP ranges where feasible). Reject unverified callbacks.
- **Least privilege** provider tokens; separate test vs production credentials; rotate on exposure.
- Prefer calling provider **REST APIs through one pinned HTTP client** over adding large vendor SDKs (see the messaging spec). Any SDK adopted goes through §3.1's approval + hash-pin + cooldown.

---

## 4. Build & run discipline

- One domain / work package per PR where practical; no unrelated refactors bundled with feature work.
- Migrations reviewed for data-loss risk; back up before risky migrations.
- Tests required: domain/service, view, form, template/htmx-fragment, and authorization + audit where applicable.
- Update documentation and the relevant journal (§8) when behavior changes.
- Idempotency on any action where a repeated submit could duplicate an important effect (room assignment, stock movement, approval, period lock, message send).

---

## 5. Security, data & privacy

- **RBAC: four roles** (Recruiter, Coordinator, Manager/Admin, Observer). **Broad internal read visibility; actions gated by role.** No arbitrary per-user permission matrices in MVP.
- **Audit old + new values** for every sensitive create/change — this is the safety net for the broad-read model. Audit is append-only to ordinary users.
- **No real worker PII** until the real-data gate passes (signed DPA, approved hosting, reviewed permissions + sensitive-field visibility, documented blacklist/feedback retention, tested backups, passed security review). Use fictional data with Cyrillic / Central-Asian / Vietnamese names until then (also validates Unicode).
- **Decimal money, never floats.** (The Django spike already found one truthiness/parse bug that silently zeroed amounts — parse with explicit `is not None` checks, not truthiness.)
- HU/SK/UA via Django localization; **no English UI**. Every user-facing string goes through i18n.

---

## 6. Mobile (coordinator field mode)

- htmx full-page-fallback first: every htmx interaction must also work as a normal request if the fragment swap fails.
- Touch targets ≥ 44px; verified at 375×667 in a Playwright mobile project.
- **Open caveat:** the spike proved a mobile list/filter/detail flow, **not** a rich field workflow. Before committing field mode to htmx-only, prove it on a real device. If it strains, raise an ADR for a *narrowly scoped* enhancement — never a SPA, never npm.

---

## 7. Media & secret request rule

The agent **never fetches binaries, fonts, images, or credentials, and never signs up for provider accounts.** Instead it writes:
- an **asset/secret request** listing exactly what's needed (filename/binary + version + SHA-256 to verify, or which env var + which provider), and
- a **runbook** describing where the human places it and how the build consumes and verifies it.

A human supplies the artifact; the agent then verifies it (checksum / presence) before use. This keeps every externally-sourced byte under human control.

Design references: the demo for visual language, plus `frontend-design/SKILL.md` and `typography_and_fonts.md`.

---

## 8. Documentation / living journals

Keep these current at the repository root:
- `BUILD_JOURNAL.md` — what was built, decisions, gotchas.
- `ENVIRONMENT.md` — tools, versions, pins, how to set up locally.
- `deployment_journal.md` — Dokku/staging/production steps and incidents.
- `test_journal.md` — what's tested, gaps, last full-run results.
- ADRs under `docs/adr/` for every architectural decision in the plan's Phase-0 list.

---

## 9. Operating-system & editor packages (always)

- Do not install OS packages, AUR packages, or editor/marketplace extensions to make the build work. These are active supply-chain targets. If something seems to need one, **stop and ask**.

---

## 10. Ask / skills

- When a requirement is unclear or a decision is missing, **ask or write a decision note** rather than guessing — especially for statuses, permissions, financial formulas, blacklist rules, legal basis, retention, or intake questions.
- If a relevant Anthropic **skill** would help (e.g. document generation), request it rather than improvising.

---

## 11. Hard "never do" list

- Never add Node/npm/React/Vite/`node_modules`.
- Never load runtime assets from a CDN.
- Never install an unpinned, unhashed, or unapproved dependency.
- Never run an externally downloaded binary without verifying its SHA-256 first.
- Never commit secrets or a populated `.env`.
- Never act on an unverified inbound webhook.
- Never put real worker PII in the system before the real-data gate.
- Never resurrect CorvinumEU, shifts, fleet, sick leave, the worker portal, or Pohoda in a PR.
