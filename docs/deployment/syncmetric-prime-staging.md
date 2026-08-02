# syncmetric-prime — staging deploy runbook (both clients)

Concrete, executable version of [deployment-plan.md](deployment-plan.md) for the
**syncmetric-prime** VPS. Brings up **two staging apps** on **fictional data**:

| App | Settings module | Staging URL | DB service |
|---|---|---|---|
| `jober-staging` | `config.settings.production` | `https://jober-staging.<PARENT>` | `pg-jober-staging` |
| `corvinum-staging` | `clients.corvinum_eu.production` | `https://corvinum-staging.<PARENT>` | `pg-corvinum-staging` |

Fill the placeholders once: `<PARENT>` (parent domain), `<VPS_IP>`,
`<OPS_EMAIL>` (Let's Encrypt), `<DOKKU_VERSION>` (current stable, pinned).
Production apps and real PII are **out of scope** — gated on the legal items
(deployment-plan asks D8).

> **Execution model:** the owner runs every command over their own SSH session
> and pastes output back; nothing here transmits secrets through a third party.
> Root commands are on the VPS; the build/transfer step is on the dev machine.

## Current CorvinumEU staging state — 2026-08-01

The CorvinumEU half of this runbook is now deployed as a **fictional-data
client demo**:

| Item | Current value |
|---|---|
| Dokku host | `syncmetric-prime` (Dokku 0.38.25) |
| App / database | `corvinum-staging` / `pg-corvinum-staging` |
| Settings module | `clients.corvinum_eu.production` |
| Temporary public URL | `https://corvinum-staging.80.211.210.46.sslip.io/sk/prihlasenie/` |
| Deployed image | `jober-platform:demo-1458ff7` |
| Proxy upload ceiling | `client_max_body_size 25m` on both staging apps |
| Seed data | published Recruiter intake v3 and fictional CorvinumEU scenario only |

Verified at deployment: Gunicorn is running on port 8000, the unauthenticated
Slovak route redirects to login, the login page and CSS are served over HTTPS,
and migrations plus both fictional seed commands complete. This is not a
production hostname and does not authorize real PII.

Email delivery is verified on this host: a controlled fictional payslip was
sent as an encrypted PDF to the designated test inbox. The SMTP runtime values
were synchronized through a **read-only service token scoped only to
`hr_system/stg_corvinum-staging`**. Never add a Doppler token to the app
image/container, synchronize unrelated secrets, or document a recipient,
credential, or one-time PDF password. Revoke or replace the staging token when
the demonstration window ends.

## Repeatable CorvinumEU staging release procedure

Use this procedure for subsequent changes to the already deployed demo. It is
intentionally image-first: the VPS never builds source code and a Docker build
never receives Doppler or Dokku secrets.

### 1. Freeze and verify the local release

```bash
cd /home/disane/Dev/hr_system
git status --short                 # must be empty
git rev-parse --short HEAD

# Run the relevant unit/browser checks before a client-facing release.
python3 scripts/check_no_node_artifacts.py
python3 scripts/verify_vendor_assets.py
```

### 2. Build and stream a unique image

```bash
APP=corvinum-staging
TAG="corvinum-demo-$(git rev-parse --short HEAD)"
IMAGE="jober-platform:$TAG"

docker build -t "$IMAGE" .
docker image inspect "$IMAGE" >/dev/null
docker image save "$IMAGE" | \
  ssh syncmetric-prime-dokku "git:load-image $APP $IMAGE"
```

### 3. Release, then prove it

Run on the administrative VPS account, not the restricted `dokku@` account:

```bash
APP=corvinum-staging
HOSTNAME=corvinum-staging.80.211.210.46.sslip.io

sudo dokku run "$APP" python manage.py migrate --noinput
sudo dokku run "$APP" python manage.py enforce_certificate_storage_policy
sudo dokku ps:report "$APP"
curl -fsS "https://$HOSTNAME/healthz/"
```

The certificate-policy command is a read-only report by default. Inspect any
listed legacy files before acting. Its destructive mode is restricted to a
confirmed fictional-data environment and must never be made an automatic
release step.

Back on the development machine, run:

```bash
scripts/deploy_smoke.sh "https://$HOSTNAME" --https
```

Run `seed_questionnaire` and `seed_corvinum_demo` only for a deliberately new
or reset **fictional** staging database—not as a routine release action. Check
the client login, TOTP, one representative write, and the Dokku logs before a
client call. Do not re-send an email merely as a deployment smoke check.

### 4. Roll back when necessary

Keep the prior unique image tag until the replacement has passed smoke checks.
To return to it, deploy the prior image explicitly, then re-run migration and
smoke verification:

```bash
ssh syncmetric-prime-dokku \
  "git:from-image corvinum-staging jober-platform:<previous-tag>"
```

Never roll a database schema backward casually; stop and assess if a migration
is not backward compatible.

## Help-area staging acceptance gate

Run this gate after the Help-only PR is merged and deployed to both staging
apps. It is not permission to deploy an unreviewed branch or to use real
worker records.

1. Sign into Jober in Slovak and open `/sk/help/`. Confirm exactly 12 cards:
   Getting started, People, Projects, Readiness, Certificates, Equipment,
   Accommodation, Reports, Finance, Feedback, Blacklist, and Audit.
2. Sign into CorvinumEU in Hungarian and open `/hu/help/`. Confirm exactly 12
   cards: Getting started, People, Projects, Readiness, Certificates,
   Equipment, Reports, Ledger, Payslips, Gross wages, Blacklist, and Audit.
3. Open every visible card. Each page must contain Purpose, On this page,
   Roles and permissions, numbered Workflow, a boundary, an annotated image,
   and working related-topic links.
4. Confirm every thumbnail and primary screenshot loads from that client's
   namespace. Jober must not show Corvinum imagery or ledger/pay articles;
   Corvinum must not show Jober imagery or accommodation/finance/feedback.
5. Verify Jober Equipment describes goods receipts and stock reconciliation,
   while Corvinum Equipment describes returning an original issue. Verify the
   Corvinum Readiness article includes critical checklist guidance.
6. At 375×667, verify one card per row, no horizontal overflow, and touch the
   card body—not only its title—to open it. At desktop width, use Tab and Enter
   to open a focused card.
7. Switch light and dark themes. Card text, focus rings, callouts, and related
   links must remain legible.
8. Request `/help/logistics/` and confirm it permanently redirects to
   `/help/equipment/`. Direct unsupported article URLs must return 404.

Inspect only seeded fictional screens. In particular, do not open or capture a
TOTP enrollment secret, one-time payslip password, provider credential, Audit
event rows/log contents, or a non-fictional record. Record the deployed commit,
image digest, both 12-card results, and any exception in `deployment_journal.md`.

## Required upload-request ceiling

Set this once for every new Dokku app before testing avatars or occupational
certificates:

```bash
APP=<app>                         # jober-staging | corvinum-staging
sudo dokku nginx:set "$APP" client-max-body-size 25m
sudo dokku proxy:build-config "$APP"
sudo dokku nginx:validate-config "$APP"
sudo dokku nginx:show-config "$APP" | grep client_max_body_size
```

The final command must show `client_max_body_size 25m;`. On the installed Dokku
0.38.25, `nginx:set` updated the computed value but did not rewrite the active
nginx file by itself; `proxy:build-config` was required. A plain
`dokku nginx:reload` only reloads the file already on disk and is not a
substitute for rebuilding it.

This 25 MB value is a proxy admission ceiling, not the application's validation
limit. Django still rejects an avatar above 5 MB and each certificate file
above 10 MB with a user-facing error. The larger proxy ceiling allows a
front-and-back certificate request (up to two 10 MB files plus multipart form
overhead) to reach those validators.

A request larger than 25 MB will still be rejected by nginx with its generic
413 response. That is an intentional outer resource guard, but a branded proxy
error page or browser-side size preflight remains separate UX hardening; this
configuration fix does not claim either one.

If the browser instead shows nginx's unbranded **413 Request Entity Too Large**
page, the request never reached Django. Compare the computed setting with the
active file, rebuild, validate, and verify again:

```bash
sudo dokku nginx:report "$APP" | grep "computed client max body size"
sudo dokku nginx:show-config "$APP" | grep client_max_body_size
sudo dokku proxy:build-config "$APP"
sudo dokku nginx:validate-config "$APP"
sudo dokku nginx:show-config "$APP" | grep client_max_body_size
```

The 2026-08-01 staging incident was this exact mismatch: both apps still served
nginx's 1 MB default, so a roughly 1.9 MB fictional avatar was rejected before
Django. After both active configs showed 25 MB, all four large generated PNGs
used in the manual pass uploaded and rendered successfully in Jober. They
appeared consistently in person detail, the People list and the bottom-right
quick-access worker panel. Server inspection found only their four referenced
512×512 WebP outputs, without EXIF or retained originals: 77,042 stored bytes
for 7,770,049 source bytes. No application redeploy was needed.

## Jober staging preparation on the same host

Jober can use the same Dokku host while remaining structurally isolated. It
must receive its own app, database, cookie namespace, runtime configuration,
fictional data, and (if SMS is demonstrated) its own scoped provider config.

| Item | Planned value |
|---|---|
| App | `jober-staging` |
| Database | `pg-jober-staging` |
| Settings module | `config.settings.production` |
| Temporary hostname | `jober-staging.80.211.210.46.sslip.io` |
| Client selection | Jober settings module; never a Corvinum override |

Before creating it, prepare a separate Doppler config such as
`hr_system/stg_jober-staging`. It needs the normal Jober Django/runtime
settings and, only if an SMS demonstration is required, its own test
`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`, and
`DEMO_SMS_PHONE`. Do not reuse the Corvinum SMTP token or configuration.

The first deployment follows the same image-stream process, but after the
app/database/config/domain/TLS setup it runs the Jober fictional scenario:

```bash
for command in seed_demo seed_people seed_logistics seed_questionnaire seed_finance seed_messaging seed_demo_scenario; do
  sudo dokku run jober-staging python manage.py "$command"
done
```

> **Office scoping (ADR 0026, 2026-07-25).** Re-run these seeds on any
> staging database created before that date: pre-split pooled equipment
> stock and office-less people otherwise make per-office figures and the
> blacklist walkthrough disagree with the demo runbook. The commands are
> idempotent and include repair paths for existing rows.

Then run the HTTPS smoke check, verify the Jober-branded login and separate
`jober_sessionid` / `jober_csrftoken` cookies, and perform one controlled
Twilio Virtual Phone test only if the dedicated staging credentials are ready.
Creating this second public app, its database, its DNS/TLS hostname, and its
provider configuration remains a deliberate next deployment step; none has
been created by this documentation update.

---

## Phase 0 — Assess + DNS

On the VPS (as a sudo user):
```bash
lsb_release -a            # expect Ubuntu 22.04/24.04 LTS
free -h && df -h /        # ~4 GB RAM, 20 GB free is comfortable (box runs, never builds)
```
DNS: add two **A records** at the domain registrar, both pointing at `<VPS_IP>`:
```
jober-staging.<PARENT>      A   <VPS_IP>
corvinum-staging.<PARENT>   A   <VPS_IP>
```
Verify propagation before Phase 1:
```bash
dig +short jober-staging.<PARENT> corvinum-staging.<PARENT>
```

## Phase 1 — Install Dokku + plugins (VPS, root, once)

**No pipe-to-shell (AGENTS.md §3.4).** Download the pinned bootstrap, verify it,
then run it:
```bash
cd /root
wget -O bootstrap.sh https://dokku.com/install/<DOKKU_VERSION>/bootstrap.sh
sha256sum bootstrap.sh            # record the hash in deployment_journal.md
less bootstrap.sh                 # review before executing
sudo DOKKU_TAG=<DOKKU_VERSION> bash bootstrap.sh
```
Plugins (pinned) + Let's Encrypt global email + owner SSH key:
```bash
sudo dokku plugin:install https://github.com/dokku/dokku-postgres.git --name postgres
sudo dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git --name letsencrypt
sudo dokku letsencrypt:set --global email <OPS_EMAIL>
# add the key you deploy/manage with:
echo "<your-ssh-public-key>" | sudo dokku ssh-keys:add admin
```

## Phase 2 — Build + transfer the image (dev machine)

For a Dokku version that supports `git:load-image` (including the installed
syncmetric-prime Dokku 0.38.23), stream the prebuilt image directly through the
restricted Dokku SSH account. Use a unique tag for every release:

```bash
TAG="corvinum-demo-$(git rev-parse --short HEAD)"
docker build -t "jober-platform:$TAG" .
docker image save "jober-platform:$TAG" | \
  ssh syncmetric-prime-dokku "git:load-image corvinum-staging jober-platform:$TAG"
```

This remains a local build without secrets; it does not create a source
checkout or run an application build on the VPS. The generic transfer fallback
for an older Dokku host is:

```bash
TAG="v$(date +%Y%m%d)-$(git rev-parse --short HEAD)"
docker build -t "jober-platform:$TAG" .
docker save "jober-platform:$TAG" | bzip2 | ssh <VPS_IP> 'bunzip2 | docker load'
```
Both apps deploy this **one tag**; rollback later = redeploy the previous tag.
No registry (keeps the supply-chain surface small).

## Phase 3 — Create each app (VPS, root)

Run this block **twice**, substituting the per-app values from the table below.

```bash
APP=<app>                     # jober-staging | corvinum-staging
DB=<db>                       # pg-jober-staging | pg-corvinum-staging
MODULE=<module>               # config.settings.production | clients.corvinum_eu.production
DOMAIN=<app>.<PARENT>
TAG=<the tag from Phase 2>

dokku apps:create "$APP"
dokku postgres:create "$DB"
dokku postgres:link "$DB" "$APP"          # sets DATABASE_URL + a linked alias

# Core config. DB_* mirror the linked service (read them from `dokku postgres:info $DB`).
dokku config:set --no-restart "$APP" \
  DJANGO_SETTINGS_MODULE="$MODULE" \
  DJANGO_SECRET_KEY="$(openssl rand -base64 48)" \
  DJANGO_ALLOWED_HOSTS="$DOMAIN" \
  DB_NAME=<from postgres:info> DB_USER=<…> DB_PASSWORD=<…> DB_HOST=<…> DB_PORT=5432 \
  DJANGO_SUPERUSER_EMAIL=<admin-email> DJANGO_SUPERUSER_PASSWORD="$(openssl rand -base64 24)"

dokku ports:set "$APP" http:80:8000       # gunicorn listens on 8000 (Dockerfile EXPOSE)
dokku domains:set "$APP" "$DOMAIN"
dokku git:from-image "$APP" "jober-platform:$TAG"
dokku letsencrypt:enable "$APP"

# Required for avatars and front/back certificates; see the section above.
dokku nginx:set "$APP" client-max-body-size 25m
dokku proxy:build-config "$APP"
dokku nginx:validate-config "$APP"
dokku nginx:show-config "$APP" | grep client_max_body_size
```

Per-app extra config (from the owner's local `doppler run` — paste values into
`dokku config:set`, never git):
- **jober-staging**: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`,
  `TWILIO_FROM_NUMBER`, `DEMO_SMS_PHONE=<approved-demo-recipient>`. The
  recipient must be distinct from `TWILIO_FROM_NUMBER`; Twilio rejects a
  same-number attempt with error `21266`. Do not record either phone number in
  this runbook.
- **corvinum-staging**: `DJANGO_EMAIL_HOST/PORT/HOST_USER/HOST_PASSWORD/USE_TLS`
  + `DJANGO_DEFAULT_FROM_EMAIL` for payslip email (or leave the console backend
  for a first bring-up). 2FA-for-managers is already on via the settings module.

Leave `DJANGO_SECURE_SSL_REDIRECT` / `DJANGO_SESSION_COOKIE_SECURE` /
`DJANGO_CSRF_COOKIE_SECURE` **unset** — they default secure and must stay on
for real HTTPS. (The `=0` overrides are local-demo only.)

## Phase 4 — Release + seed staging (VPS, root, per app)

```bash
dokku run "$APP" python manage.py migrate --noinput
dokku run "$APP" python manage.py ensure_superuser        # idempotent, from env
dokku run "$APP" python manage.py enforce_certificate_storage_policy
```
The certificate-policy command reports only. If it finds a disallowed legacy
file, inspect the exact fictional staging record before considering the
explicit `--purge-disallowed --confirm-fictional-data` remediation. Never use
that destructive confirmation on a real-data database.

Staging is fictional-data by design — seed it so the demo cast is present:
```bash
# jober-staging
for c in seed_demo seed_people seed_logistics seed_questionnaire seed_finance seed_messaging seed_demo_scenario; do
  dokku run jober-staging python manage.py "$c"
done
# corvinum-staging
dokku run corvinum-staging python manage.py seed_questionnaire
dokku run corvinum-staging python manage.py seed_corvinum_demo
```
*(Never run these on a real-data production app.)*

## Phase 5 — Verify

From the dev machine:
```bash
scripts/deploy_smoke.sh https://jober-staging.<PARENT> --https
scripts/deploy_smoke.sh https://corvinum-staging.<PARENT> --https
```
Manual: log into both; enroll 2FA on corvinum (`hradmin`); send one live SMS
from Olha's card to the separate approved Twilio test recipient and confirm it
in Twilio's controlled test view; open the **Audit** page. For an avatar/media
release, run [`avatar-upload-acceptance.md`](avatar-upload-acceptance.md) with
the tracked fictional fixtures. For a certificate-related release, also run
[`certificate-upload-acceptance.md`](certificate-upload-acceptance.md): at
minimum upload/open the fictional front/back forklift card in both clients and
the single crane PDF in one. Record the selected category and UI language. Do
not upload real documents, and keep the deliberate birth/ID mislabel probe out
of ordinary deploy smoke checks.
Register the Twilio inbound webhook now that a public HTTPS host exists:
`https://jober-staging.<PARENT>/webhooks/twilio/inbound/`.

## Phase 6 — Backups

**Deferred by the owner on 2026-07-26** until CorvinumEU accepts the offer —
that build provides the off-site destination (a Contabo Storage VPS in the EU,
per `corvinum-basic-production.md`), so doing Jober first would mean buying a
second one. Both databases hold fictional data, so a loss costs a reseed today.

**Install this before the real-data gate opens for any client, whichever comes
first.** Past that point a lost database is lost personal data and a GDPR
availability failure, not an inconvenience.

Everything below is ready to run; read it before choosing an approach.

### Why not `dokku postgres:backup-schedule`

The plugin's own scheduler is **S3-only** — `postgres:backup-auth` takes an AWS
access key pair and `postgres:backup-schedule` takes a bucket name. There is no
"local target" variant, so the placeholder that used to sit here was wrong. It
also backs up *only* the database: not the media volume (which now holds real
uploads) and not a release manifest.

### Use the repo's script instead

`scripts/offsite_backup.sh` was generalised on 2026-07-26 from the CorvinumEU
one; a single invocation backs up a single app. It exports the database via
`dokku postgres:export`, adds the media volume and a non-secret release
manifest, **encrypts with GPG before transfer**, verifies the remote checksum,
and keeps 35 daily plus 12 monthly generations. It deliberately never runs
`dokku config:export`, because that output carries Doppler-synchronised
secrets.

It runs **on the host**, as root, from cron — not over the restricted
`dokku`-only SSH access used elsewhere in this runbook.

```bash
# /etc/dokku-backups/jober-staging.env   (root-owned, 0600, outside git)
DOKKU_APP=jober-staging
POSTGRES_SERVICE=pg-jober-staging
BACKUP_PREFIX=jober-staging
MEDIA_SOURCE_DIR=/var/lib/dokku/data/storage/jober-staging-media
BACKUP_REMOTE=<user>@<off-site-host>          # asks D6
BACKUP_REMOTE_DIR=/srv/jober-staging-backups
BACKUP_GPG_RECIPIENT=<public key fingerprint>
BACKUP_SSH_KEY=/root/.ssh/dokku-backup_ed25519
```

```cron
20 03 * * *  . /etc/dokku-backups/jober-staging.env    && /path/to/scripts/offsite_backup.sh >> /var/log/jober-staging-backup.log 2>&1
50 03 * * *  . /etc/dokku-backups/jober-staging.env    && /path/to/scripts/backup_health.sh  >> /var/log/jober-staging-backup-health.log 2>&1
35 03 * * *  . /etc/dokku-backups/corvinum-staging.env && /path/to/scripts/offsite_backup.sh >> /var/log/corvinum-staging-backup.log 2>&1
```

**`BACKUP_PREFIX` must match between the backup and health jobs for an app.**
The retention pass globs on it, so a mismatch either prunes nothing or prunes
another app's history; the health check would also report "no backup" for an
app that is backing up fine. Giving each app its own `BACKUP_REMOTE_DIR` avoids
the question entirely, and is the recommendation.

### What the owner must supply

1. **An off-site host and account** — open question **D6**. It must not be on
   the same provider as the Dokku host, or a provider-level loss takes both.
2. **A GPG public key** for `BACKUP_GPG_RECIPIENT`. Keep the private recovery
   key off *both* servers; an encrypted backup whose key lives beside it is not
   a backup.
3. Root shell on the host to install the env files and cron entries.

### Then prove it restores

A backup nobody has restored is a hypothesis. Run
`scripts/backup_restore_drill.sh` once against a scratch database, and record
the result in `deployment_journal.md`. Until that has happened, item 4 stays
open even with a schedule running.

## Rotating the PostgreSQL password

Run **on the host** (`syncmetric-prime`), as a user with sudo. Executed once on
2026-07-26; the notes below are what that attempt taught.

```bash
SVC=pg-jober-staging
PWFILE=/var/lib/dokku/services/postgres/$SVC/PASSWORD
sudo cp "$PWFILE" "/root/${SVC}-PASSWORD.bak"
NEW=$(openssl rand -hex 16)

sudo docker exec dokku.postgres.$SVC \
  psql -U postgres -c "ALTER USER postgres WITH PASSWORD '$NEW';"   # expect: ALTER ROLE
printf %s "$NEW" | sudo tee "$PWFILE" >/dev/null
sudo dokku config:set jober-staging DB_PASSWORD="$NEW"              # <- the step that matters
```

**Do not use `postgres:unlink` + `postgres:link` for this.** This app does not
read `DATABASE_URL` at all — `config/settings/base.py` builds the connection
from `DB_HOST`/`DB_NAME`/`DB_USER`/`DB_PASSWORD`/`DB_PORT`. Relinking therefore
fixes nothing, and if the plugin thinks the app is already unlinked it creates
a *second* link under a colour alias (`DOKKU_POSTGRES_AQUA_URL`) while leaving
a stale `DATABASE_URL` behind. That is what caused the 2026-07-26 outage.

Two things to check afterwards, because a failed rotation can look successful:

- `sudo dokku run jober-staging python -c "…connection.ensure_connection()…"`
  must print `DB OK`.
- If any command printed a DSN, confirm its password **changed**. An identical
  password after a "successful" run means `ALTER USER` or the file write failed
  silently — both need root, and both fail quietly without it.

Recovery: restore `/root/<service>-PASSWORD.bak` over `$PWFILE`, re-run
`ALTER USER` with that value, and `config:set DB_PASSWORD` to match.

## Rollback

```bash
dokku git:from-image "$APP" "jober-platform:<previous-tag>"   # redeploy the prior image
```

## Still gated (not done here)

Production apps + real PII (D8: Jober LIA/contract text, DPA, EU-hosting
approval; CorvinumEU C-Q6/13/16). Twilio account upgrade (D7) removes the trial
prefix. CI/CD pipeline is deliberately deferred.
