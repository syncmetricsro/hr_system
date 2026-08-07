# Deployment plan — Dokku on one VPS, both thin clients

> **CorvinumEU production decision (updated 2026-08-07):** the two permanent
> hosts are FORPSI `corvinum-main` for production and Contabo
> `corvinum-bsite` for encrypted backups only. Existing fictional staging stays
> on `syncmetric-prime`, outside that pair. The Corvinum rows below describe
> app naming and settings only; their previous shared/always-on hosting
> assumption is superseded by
> [corvinum-basic-production.md](corvinum-basic-production.md) and the canonical
> [production backlog](corvinum-production-readiness.md).
> Jober’s topology is unchanged.

Contextual tooltips are shipped in the existing CSS, JavaScript, and templates.
They require no deployment setting, migration, service, or network endpoint.

The floating notification center uses ordinary Django requests only. It does
not require a worker process, message broker, WebSocket proxying, or additional
Dokku configuration. Realtime SSE/WebSocket delivery is explicitly deferred to
a future ADR and must not be enabled by changing proxy timeouts alone.

Owner decision 2026-07-11: **Dokku on the existing VPS**. One versioned
application artifact; one Dokku app per client; per-client database, domain,
TLS, secrets, backups (design doc §12.4 — GDPR isolation is structural, no
multi-tenancy). Supersedes nothing: `jober-dokku-staging.md` remains the
Jober staging detail sheet and is referenced below.

## Topology

| Dokku app | Settings module | Domain (ask) | DB service |
|---|---|---|---|
| `jober-staging` | `config.settings.production` | `staging.<jober-domain>` | `pg-jober-staging` |
| `jober` | `config.settings.production` | `<jober-domain>` | `pg-jober` |
| `corvinum-staging` on `syncmetric-prime` | `clients.corvinum_eu.production` | current staging domain | `pg-corvinum-staging` |
| `corvinum` on `corvinum-main` | `clients.corvinum_eu.production` | `<corvinum-domain>` | `pg-corvinum` |

Same image everywhere; **`DJANGO_SETTINGS_MODULE` is the only thing that
selects the client** (proven daily by the local dual-demo setup). Staging
apps run **fictional seeds only**; production apps run **no seeds** and stay
empty until each client's real-data/legal gate opens (Jober: LIA + contract
text; CorvinumEU: C-Q6 written confirmation + C-Q13/16 retention answers).

## Image path

1. Build locally/CI from the repo `Dockerfile` (digest-pinned base, hash-pinned
   locks, Tailwind fetch-and-verify — all existing).
2. Tag per release (`v<date>-<shortsha>`), `docker save | ssh dokku docker load`
   or a registry if one is approved later (registry = new supply-chain surface,
   needs its own decision).
3. `dokku git:from-image <app> <image:tag>` per app — all four apps deploy the
   **same tag**; rollback = redeploy the previous tag.

## Per-app one-time setup (run once, per app)

```bash
dokku apps:create <app>
dokku postgres:create <db> && dokku postgres:link <db> <app>
dokku config:set <app> DJANGO_SETTINGS_MODULE=<module> \
  DJANGO_SECRET_KEY=<generated> DJANGO_ALLOWED_HOSTS=<domain> \
  DB_NAME=… DB_USER=… DB_PASSWORD=… DB_HOST=… DB_PORT=5432   # from postgres:link
# Doppler is the source of truth; sync into dokku config, never git:
doppler secrets download --no-file --format env-no-quotes | xargs dokku config:set <app>
dokku domains:set <app> <domain>
dokku letsencrypt:enable <app>
dokku checks:enable <app>        # zero-downtime check against /healthz/
```

Release step (every deploy): `dokku run <app> python manage.py migrate --noinput`
followed by **`scripts/deploy_smoke.sh https://<domain> --https`** (healthz,
CSRF, fingerprinted static with immutable caching, X-Frame-Options, HSTS,
Secure cookies — fails closed)
(or `app.json` predeploy); first deploy also `createsuperuser` (real email
user; **never** `seed_demo`/`seed_corvinum_demo` on production).

**On any database carrying history, also run
`dokku run <app> python manage.py backfill_audit_persons`** after `migrate`.
The migration that added `AuditEvent.person` can only attribute events whose
target *was* a person; everything a manager searches for - the equipment issue,
the room assignment, the blacklist proposal - needs the command, which resolves
targets through the live app registry. Without it the audit person filter
returns nothing for pre-existing rows, which is exactly how it looked when the
client reported it. Idempotent, and `--dry-run` reports without writing.

Session policy: 30-day rolling sessions by default
(`DJANGO_SESSION_COOKIE_AGE` overrides, seconds); cookie names are per-client
(`jober_sessionid` / `corvinum_sessionid`) so apps never evict each other's
logins on a shared host.

Client-specific env:
- **Jober**: `TWILIO_*` (from Doppler); inbound webhook
  `https://<domain>/webhooks/twilio/inbound/` configured at Twilio once
  staging is live (deployment_journal 2026-06-29 item); Twilio account
  upgrade removes the trial prefix.
- **CorvinumEU**: `DJANGO_EMAIL_*` SMTP credentials for payslip delivery
  (console backend is demo-only); 2FA is already enforced for managers by the
  settings module.

## Backups & restore

- `dokku postgres:backup-auth` + `backup-schedule` daily per DB to the
  approved off-site target (owner to name one: S3-compatible bucket or
  rsync target — see asks).
- Monthly restore drill: **`scripts/backup_restore_drill.sh`** — dumps,
  restores into a scratch DB, and fails unless per-table row counts are
  identical (proven against both demo DBs 2026-07-12). Document each run in
  `deployment_journal.md`; copy the kept dump off-site (D6).

## Security posture (already in the image/settings)

- HTTPS-only: HSTS, secure cookies, SSL redirect are default-on in both
  production modules; the `=0` overrides are for the local HTTP demo only.
- Static via whitenoise manifest storage (all client themes collected).
- Light/Dark/System selection is delivered by the existing static bundle and
  localStorage; it requires no deployment variable, migration, or service.
- No secrets in git; Doppler is canonical; `dokku config` holds runtime copies.
- Fictional-data rule holds until each client's legal gate opens.

## Rollout order

0. **Run the browser suite against the exact revision being deployed.** Since
   2026-08-04 it is not part of the per-commit gate and CI does not run it by
   itself, so **this is the one place it is required** — a deploy is the moment
   the accumulated UI risk is worth 45 minutes. Locally
   `scripts/playwright_e2e.sh`, or `gh workflow run browser-e2e.yml --ref <sha>`.
1. **Jober staging** → smoke (healthz, login, three headline screens, one
   Twilio Virtual-Phone SMS), then hold for the Jober demo/acceptance.
2. **CorvinumEU staging** → smoke (2FA enrollment with a real phone, checklist
   gate, ledger, payslip email to a test mailbox via real SMTP).
3. Production apps only after each client's acceptance + legal gates.

## Asks and current state

| # | Ask/status | Blocks |
|---|---|---|
| D1–D3 | **Completed for staging:** `syncmetric-prime`, both public staging apps, DNS/TLS and per-app databases exist | — |
| D4 | Staging Doppler configs exist; create and inject a separate production Corvinum config for `corvinum-main` | production secrets/runtime |
| D5 | `noreply@corvinum.eu` SMTP is proven with controlled delivery; finish production sender/DPA/retention/DNS and bounce handling | real payslip/offer delivery |
| D6 | **Target selected:** Contabo `corvinum-bsite`; provision, harden, install encrypted transfer/health schedules, and pass restore drill | real-data backup gate |
| D7 | Twilio account upgrade decision | Jober SMS without trial prefix |
| D8 | Corvinum legal/privacy/retention and product gates in `corvinum-production-readiness.md` | real Corvinum users/data |
| D9 | Provision/harden FORPSI `corvinum-main` and choose the final production domain | Corvinum production deploy |

The concrete staging runbook is
[syncmetric-prime-staging.md](syncmetric-prime-staging.md) (owner decision
2026-07-12: fresh VPS **syncmetric-prime**, per-client subdomains under one
parent, staging-only both clients, owner-runs-I-guide).
