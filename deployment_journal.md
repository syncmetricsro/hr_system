# Deployment Journal

## 2026-07-20 - Corvinum wage release staging-data reconciliation

- The first PR #77 staging release applied `wage_ledger.0001` and passed the
  public HTTPS smoke suite, but acceptance found Marek's existing, sent
  `2026-07` fictional payslip from an earlier manual rehearsal. The idempotent
  seed correctly did not overwrite or delete that audited record.
- Moved the deterministic wage-versus-payslip checkpoint to fictional candidate
  Eszter Varga. Marek remains the encrypted-delivery example; no historical
  payslip, delivery timestamp, recipient, or audit event was changed.
- Merged the correction as PR **#78** and deployed application revision
  **`67bcfae`** to `corvinum-staging` as
  `jober-platform:corvinum-demo-67bcfae` (local image digest
  `sha256:ea8eed4632886882c4b62a5beeba2250032ebf84ff4aea0014cb92982b136a3a`).
- Dokku's replacement container passed uptime and port-8000 checks. Migrations
  are current, the idempotent fictional seed completed, and a read-only runtime
  assertion confirmed Eszter's exact source rows: June `1920.00 / 1450.00 EUR`
  and July `2050.00 / 1540.00 EUR`; wage ledger and payslips are ON while
  Corvinum transport remains OFF.
- The public HTTPS smoke suite passed health, login/secure CSRF, fingerprinted
  CSS, X-Frame-Options, and HSTS. The app remains available at
  `https://corvinum-staging.80.211.210.46.sslip.io`. The known Dokku
  default-bridge deprecation warning remains non-blocking host maintenance.

## 2026-07-20 — Jober amendments and latest Corvinum demo deployed

- Merged PR **#73** (shared platform/Corvinum work) and PR **#75** (Jober
  interview amendments) into `main`; the deployed application revision is
  **`cd28ac8`**.
- Built the npm-free production image locally without runtime credentials and
  streamed the same tag, **`jober-platform:demo-cd28ac8`** (local image digest
  `sha256:dbfc9c29680e929a76ce42b6e8e66efa863a2a23f246a879f5feba1607126198`),
  to both `jober-staging` and `corvinum-staging` on syncmetric-prime.
- Both Dokku replacement containers passed their uptime and port checks. Applied
  migrations through `projects.0005` and `logistics.0009`; `migrate --check`
  then passed for both isolated databases.
- Refreshed only fictional, idempotent demo data. Jober received the updated
  warehouse stock, accommodation-cost, regional-finance, and age-warning
  scenario; Corvinum retained its separate intake, checklist, equipment, and
  worker-ledger scenario.
- Runtime policy checks confirmed Jober transport OFF with profitability and
  warehouse stock ON, and Corvinum transport, profitability, and warehouse
  stock OFF. The public HTTPS smoke suite passed health, login/CSRF,
  fingerprinted static assets, X-Frame-Options, and HSTS for both apps.
- Public demos: `https://jober-staging.80.211.210.46.sslip.io` and
  `https://corvinum-staging.80.211.210.46.sslip.io`. The known Dokku
  default-bridge deprecation warning remains host maintenance; it did not
  affect either release.

## 2026-07-16 — Corvinum checklist in-place update deployed

- Built committed revision **`6abdb56`** in a detached clean worktree without
  runtime credentials and streamed
  `jober-platform:corvinum-demo-6abdb56` directly to the isolated
  `corvinum-staging` Dokku app.
- Dokku's replacement container passed its uptime and port-8000 checks before
  replacing the prior web process. The existing PostgreSQL service and
  fictional staging data were preserved; no reseeding was performed.
- The idempotent migration step reported no migrations to apply. Public HTTPS
  acceptance passed for `/healthz/`, the Slovak login page, and the compiled
  CSS asset.
- This release changes activation-checklist toggles to an in-place htmx panel
  refresh, preserving the user's URL and scroll position while retaining the
  full-page POST/redirect fallback.
- The known Dokku default-bridge deprecation warning remains tracked as host
  maintenance and did not affect the release.

## 2026-07-16 — Jober public fictional-data staging and Twilio configuration

- Deployed the committed release **`12d0735`** to the isolated Dokku app
  **`jober-staging`** on **syncmetric-prime**, with its separate
  `pg-jober-staging` PostgreSQL service, Jober settings module, temporary
  HTTPS hostname, and fictional-only seed data. Django checks and migrations
  completed cleanly; the public health endpoint returned `ok` after restart.
- Created the separate read-only Doppler scope `hr_system/stg_jober-staging`
  and synchronized exactly the four approved Jober SMS runtime keys:
  `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`, and
  `DEMO_SMS_PHONE`. Jober email remains intentionally deferred for this demo.
  No Doppler token, provider credential, sender, or recipient value is
  recorded here.
- Initial SMS troubleshooting confirmed that Twilio error **21266** means the
  configured recipient matched the configured sender. This is a provider
  safety rule, not a Dokku, CSRF, or application error. The controlled demo
  recipient must be a distinct, approved SMS-capable/verified number; do not
  use `TWILIO_FROM_NUMBER` as `DEMO_SMS_PHONE`.
- Before presenting SMS, send one harmless controlled test message and confirm
  delivery in Twilio. Configure and test the signed inbound webhook only after
  that outbound check succeeds.

## 2026-07-15 — CorvinumEU public fictional-data staging demo deployed

- Deployed the committed release **`12d0735`** (`jober-platform:corvinum-demo-12d0735`)
  to the isolated Dokku app **`corvinum-staging`** on
  **syncmetric-prime** (Dokku 0.38.23). The public temporary demo URL is
  `https://corvinum-staging.80.211.210.46.sslip.io/sk/prihlasenie/`; it is not
  a production CorvinumEU domain.
- The app uses `clients.corvinum_eu.production`, the separate linked PostgreSQL
  service `pg-corvinum-staging`, and the existing explicit `http:80:8000` port
  mapping. The image was built locally without secrets and streamed directly to
  Dokku with `git:load-image`; no source checkout or application build ran on
  the VPS.
- Applied migrations and seeded only the published **Recruiter intake v3** and
  the fictional CorvinumEU scenario. The four `@demo.corvinum.test` accounts,
  projects, checklist, equipment/ledger records, and questionnaire are staging
  demonstration data only.
- Verified externally: HTTPS login route returns 200 with a Secure Corvinum
  CSRF cookie; `/sk/` correctly redirects unauthenticated visitors to login;
  CSS returns `200 text/css`; and Gunicorn is running on port 8000 without
  application errors in the Dokku log.
- Created a Doppler **read-only, config-scoped service token**, synchronized
  only the seven `DJANGO_EMAIL_*` values into this Dokku app, and completed one
  controlled fictional payslip-email test successfully. The encrypted PDF
  reached the controlled test inbox; no recipient address, SMTP credential,
  one-time PDF password, or token value is recorded here. No real recipient or
  real personal data is authorized.
- The Dokku default-bridge-network deprecation warning is recorded as post-demo
  host maintenance; it did not affect this deployment. Revoke or replace the
  staging service token after the demo according to the retention decision.
- Documented the repeatable image-stream release and rollback procedure for
  `corvinum-staging`, plus the planned isolated `jober-staging` app/database,
  hostname, provider boundary, fictional seeding, and acceptance checks on the
  same Dokku host. Jober has not yet been created or deployed there.
- Clarified the Jober-specific staging sheet: `config.settings.production`
  selects Jober, while a separately scoped `TWILIO_*` configuration enables
  only its controlled SMS demonstration. Corvinum's SMTP configuration and
  service token must not be reused.
- Documented Jober's exact staging release boundary: derive explicit `DB_*`
  values from the linked service without recording them, run migrations and
  `ensure_superuser` after an image deployment, and use the repository's real
  fictional seed sequence only for a deliberate reset. Same-origin HTTPS does
  not require an unused `DJANGO_CSRF_TRUSTED_ORIGINS` setting in this codebase.

## 2026-07-15 — CorvinumEU recruitment trials enabled

- Enabled the shared recruitment-trial feature for CorvinumEU’s demo. Recruiters,
  coordinators, and managers may schedule a trial; coordinators and managers
  may record its outcome. Observers remain read-only.
- Added Trial day transitions to Corvinum’s client policy and updated the
  client-demo walkthrough to show scheduling, outcome, and the subsequent
  readiness/checklist gate.

## 2026-07-15 — Corvinum blacklist archive and re-entry demo

- Added a manager-only operational archive action. It is explicitly not GDPR
  erasure: it hides the original record from the People list while retaining
  its blacklist case, active HMAC fingerprint, and audit history.
- The guided intake now accepts a transient blacklist identifier and type on
  its final panel. The raw identifier is validated and matched but never
  persisted as an intake answer. A match creates a new proposed case for
  manager review and blocks activation; it never merges or auto-blacklists.
- The Corvinum runbook now contains the full fictional propose → approve →
  archive → re-enter → manager-decision scenario.

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
