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
  `TWILIO_FROM_NUMBER`, `DEMO_SMS_PHONE=+18777804236` (the Virtual Phone).
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
from Olha's card and watch the Twilio Virtual Phone; open the **Audit** page.
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
