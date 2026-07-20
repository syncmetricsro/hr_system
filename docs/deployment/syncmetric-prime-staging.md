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

## Current CorvinumEU staging state — 2026-07-15

The CorvinumEU half of this runbook is now deployed as a **fictional-data
client demo**:

| Item | Current value |
|---|---|
| Dokku host | `syncmetric-prime` (Dokku 0.38.23) |
| App / database | `corvinum-staging` / `pg-corvinum-staging` |
| Settings module | `clients.corvinum_eu.production` |
| Temporary public URL | `https://corvinum-staging.80.211.210.46.sslip.io/sk/prihlasenie/` |
| Deployed image | `jober-platform:corvinum-demo-12d0735` |
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
cd /home/disane/Development/HR_System
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
sudo dokku ps:report "$APP"
curl -fsS "https://$HOSTNAME/healthz/"
```

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
for command in seed_demo seed_people seed_logistics seed_questionnaire seed_finance seed_demo_scenario; do
  sudo dokku run jober-staging python manage.py "$command"
done
```

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
```
Staging is fictional-data by design — seed it so the demo cast is present:
```bash
# jober-staging
for c in seed_demo seed_people seed_logistics seed_questionnaire seed_finance seed_demo_scenario; do
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
in Twilio's controlled test view; open the **Audit** page.
Register the Twilio inbound webhook now that a public HTTPS host exists:
`https://jober-staging.<PARENT>/webhooks/twilio/inbound/`.

## Phase 6 — Backups

```bash
dokku postgres:backup-schedule pg-jober-staging    "0 3 * * *" <off-site-or-local>
dokku postgres:backup-schedule pg-corvinum-staging "15 3 * * *" <off-site-or-local>
```
If no off-site target yet (asks D6), schedule local backups and record the
off-site copy as pending. Run one drill and log it:
```bash
DB_CONTAINER=... scripts/backup_restore_drill.sh    # adapt to the dokku pg service
```

## Rollback

```bash
dokku git:from-image "$APP" "jober-platform:<previous-tag>"   # redeploy the prior image
```

## Still gated (not done here)

Production apps + real PII (D8: Jober LIA/contract text, DPA, EU-hosting
approval; CorvinumEU C-Q6/13/16). Twilio account upgrade (D7) removes the trial
prefix. CI/CD pipeline is deliberately deferred.
