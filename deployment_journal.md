# Deployment Journal

## 2026-07-15 — CorvinumEU cost-conscious production operating model

- Recorded the owner decision for a low-traffic **FORPSI Basic** production
  VPS (2 vCPU / 4 GB / 40 GB NVMe), with `corvinum-staging` stopped except for
  rehearsals, deployment checks, and restore drills. Standard is the defined
  upgrade path for continuous staging, resource pressure/OOMs, recurring swap,
  or a restore that exceeds four business hours.
- Added `docs/deployment/corvinum-basic-production.md`: provider choices,
  external DPA and data-location gates, encrypted off-site retention, disk
  thresholds, website Supabase backup boundary, and a restricted monthly
  restore procedure.
- Added deployment-host scripts for an encrypted PostgreSQL/release-manifest
  backup, backup-age/capacity monitoring, and explicit staging start/stop.
  The scripts retain 35 daily and 12 monthly archives, fail at 26-hour backup
  age or 60% target use, and intentionally never export Doppler/Dokku config.
- Still owner-controlled and not claimed complete: VPS orders, DPA signatures,
  SSH/firewall/DNS setup, GPG recovery-key custody, monitoring delivery, and
  least-privilege Supabase database/private-bucket export automation.

## 2026-07-15 — Corvinum intake seed correction

- Corvinum local and fictional staging bootstrap instructions now seed the
  published personnel-intake questionnaire before the client scenario. Clean
  resets no longer leave the visible **Add person** action without a usable
  questionnaire.
- Production remains unaffected: demo seeds must never run against a real-data
  environment.

## 2026-07-15 — Corvinum client-demo rehearsal runbook

- Refreshed `docs/deployment/corvinum-demo-runbook.md` into a rehearsal-safe
  20–25 minute walkthrough with a ten-minute fallback route, exact demo
  accounts, presenter checkpoints, recovery steps, and a clean disposable-DB
  reset between practice and the client call.
- Corrected the demonstrated scope to match Corvinum's active feature flags:
  recruitment trials, accommodation, transport, profitability, messaging, and
  feedback are not mounted in this thin client.
- Corrected the local payslip demonstration: the console backend proves the
  fictional recipient and attachment output but is not a clickable mailbox;
  real provider-backed testing remains Doppler-injected.

## 2026-07-14 — Operations workspace migration

- Deploy includes logistics migration `0008_room_is_active_and_unique_label`.
  It adds an active flag to rooms and enforces unique room labels within each
  accommodation. Existing rooms default active; no record is deleted.
- Run the normal migration step before serving the new accommodation forms.
  The production image remains npm-free and contains no new runtime dependency.

## 2026-07-12 (later)

Staging deploy target chosen and runbook written.

- **Target: syncmetric-prime** — fresh VPS, Dokku to be installed. Scope: **staging only, both clients** on fictional data (`jober-staging`, `corvinum-staging`) under **per-client subdomains of one parent domain**. Execution: owner runs commands, I guide.
- **`docs/deployment/syncmetric-prime-staging.md`** written — concrete phased command sequence (assess/DNS → pinned no-pipe-to-shell Dokku install → build+`docker save|ssh load` transfer → per-app create/config/TLS → migrate+seed → `deploy_smoke.sh --https` verify → backups). Honors AGENTS §3.4 (download+checksum+review the Dokku bootstrap, never `wget|bash`).
- Asks updated: D1 names the box; D2/D3 record the subdomain choice. Production apps + real PII remain gated on D8.

## 2026-07-12

Release tooling landed (production-readiness §2 complete).

- **`scripts/deploy_smoke.sh <url> [--https]`** — post-deploy gate: healthz, login+CSRF, fingerprinted static with immutable caching, X-Frame-Options; with `--https` also HSTS + Secure cookies. Passed against both local stacks.
- **`scripts/backup_restore_drill.sh`** — dump → scratch restore → exact per-table row-count comparison. First drills PASSED: jober (47 tables/395 rows), corvinum (39 tables/298 rows). Dumps kept under `backups/` (gitignored); off-site copy pends D6.
- Also landed this cycle: console error logging (`django.request` → container logs), the corvinum-flags test lane (`scripts/test_corvinum.sh`). Remaining before staging: owner asks D1–D4.

## 2026-07-11

Deployment architecture decided and documented.

- **Owner decision:** Dokku on the existing VPS; four apps (`jober[-staging]`, `corvinum[-staging]`) from the **same image tag**, `DJANGO_SETTINGS_MODULE` selects the client; per-app Postgres/domain/Let's Encrypt/secrets/backups. Full plan + one-time setup commands + rollout order: `docs/deployment/deployment-plan.md`.
- **Execution blocked on asks D1–D8** (SSH/hostname, four domains, Doppler tokens, SMTP for payslips, backup target, Twilio upgrade, legal gates). Staging is one working session once D1–D4 land.
- Guardrails restated: production never runs demo seeds; fictional data only until each client's legal gate; secrets Doppler → `dokku config:set`, never git.

## 2026-06-29

Secrets + Twilio SMS go-live readiness.

- **Secrets via Doppler.** Project `hr_system`, config `dev` holds the Twilio creds. Local runs use `doppler run -- scripts/dev_app.sh up` (dev_app forwards `TWILIO_*` into the container; committed `doppler.yaml` selects the project/config). No secrets in git. See `docs/deployment/twilio-setup.md`.
- **Twilio SMS verified live** end-to-end through the app: live SID/token + a trial number delivered to the Twilio Virtual Phone (`Delivered` in Messaging Logs). Test-credential magic-number path also verified.
- New deploy-time env vars: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` (from Doppler/secret store, never the repo).
- **Remaining for SMS prod:** upgrade the Twilio account (removes the trial prefix; allows arbitrary recipients), and configure the inbound webhook (`/webhooks/twilio/inbound/`) once a public HTTPS host exists (Dokku staging or a tunnel). For Dokku, inject Doppler secrets via sync (`doppler secrets download … | dokku config:set`) or a service token (`doppler run -- gunicorn …`).

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
