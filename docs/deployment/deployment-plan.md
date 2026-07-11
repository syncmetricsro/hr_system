# Deployment plan — Dokku on one VPS, both thin clients

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
| `corvinum-staging` | `clients.corvinum_eu.production` | `staging.<corvinum-domain>` | `pg-corvinum-staging` |
| `corvinum` | `clients.corvinum_eu.production` | `<corvinum-domain>` | `pg-corvinum` |

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
(or `app.json` predeploy); first deploy also `createsuperuser` (real email
user; **never** `seed_demo`/`seed_corvinum_demo` on production).

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
- Monthly restore drill: restore latest dump into a scratch service, run
  `manage.py check` + row counts against it. Document each drill in
  `deployment_journal.md`.

## Security posture (already in the image/settings)

- HTTPS-only: HSTS, secure cookies, SSL redirect are default-on in both
  production modules; the `=0` overrides are for the local HTTP demo only.
- Static via whitenoise manifest storage (all client themes collected).
- No secrets in git; Doppler is canonical; `dokku config` holds runtime copies.
- Fictional-data rule holds until each client's legal gate opens.

## Rollout order

1. **Jober staging** → smoke (healthz, login, three headline screens, one
   Twilio Virtual-Phone SMS), then hold for the Jober demo/acceptance.
2. **CorvinumEU staging** → smoke (2FA enrollment with a real phone, checklist
   gate, ledger, payslip email to a test mailbox via real SMTP).
3. Production apps only after each client's acceptance + legal gates.

## Asks (what execution is blocked on)

| # | Ask | Blocks |
|---|---|---|
| D1 | SSH access to the VPS + hostname; confirm Dokku installed (or approve install) | everything |
| D2 | Jober staging+prod domain names (DNS A records to the VPS) | Jober apps, Twilio webhook |
| D3 | CorvinumEU staging+prod domain names | Corvinum apps (closes C-Q14) |
| D4 | Doppler service tokens (per app/config) | secrets sync |
| D5 | SMTP account for CorvinumEU payslips | payslip email beyond demo |
| D6 | Off-site backup target (bucket or host) | backup schedule |
| D7 | Twilio account upgrade decision | Jober SMS without trial prefix |
| D8 | Legal gates: Jober LIA/contract text; CorvinumEU C-Q6/13/16 | real data on production |

When D1–D4 land, staging deployment is one working session; this file plus
`jober-dokku-staging.md` are the runbook.
