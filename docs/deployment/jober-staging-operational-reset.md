# Jober staging operational-data reset

This runbook clears the fictional operational history from
`jober-staging` while retaining the accounts and structural configuration that
Jober staff need to sign in and create their own test scenario.

It is for the current fictional-data staging phase only. Never use it against
production or any database that may contain real worker data. The real-data
gate, retention policy and legal holds would require a different, approved
erasure process.

## Reset boundary

Retain:

- `accounts.User`, password hashes, roles, staff/superuser flags and optional
  account TOTP devices;
- the three Jober offices and user-office memberships, without which scoped
  Recruiter, Coordinator and Manager accounts could sign in but could not
  operate normally;
- Django migrations, content types and permissions;
- the published intake questionnaire and its panels/questions;
- inactive, blacklist and finance category catalogues required by forms.

Clear:

- people, projects, assignments, trials, readiness and activation records;
- accommodation, rooms, equipment catalogue/stock/issues and transport data;
- financial months and line items;
- certificates and their referenced files;
- intake answers/submissions, blacklist cases/fingerprints, feedback, messages,
  offers, notifications and other operational rows;
- every old Audit event;
- every Django session, deliberately logging everyone out;
- referenced person avatars while retaining account avatars.

Do not run the fictional scenario seed commands after this reset. They would
put the old demo cast and figures back. Essential reference data is retained,
so Jober can begin entering its own fictional test records immediately.

## Why this is not `flush` or a database recreation

`manage.py flush`, dropping `pg-jober-staging`, or recreating/linking the
database would also remove accounts, password hashes, office memberships and
the initial superuser. Exporting and re-importing only selected account rows is
more fragile than retaining their tables because Django auth has permission
and many-to-many dependencies.

The repository does not currently ship a general-purpose operational-reset
management command. Each reset therefore uses a reviewed, guarded Django shell
payload generated from the current deployed model inventory. Do not retain an
old payload as an evergreen command: a later migration may add a configuration
model that must join the preserve list.

## Repeat procedure

### 1. Resolve the exact target

On `syncmetric-prime`:

```bash
sudo dokku config:get jober-staging DJANGO_SETTINGS_MODULE
sudo dokku config:get jober-staging DB_HOST
sudo dokku domains:report jober-staging | grep jober-staging
```

Expected settings, database host and public hostname:

```text
config.settings.production
dokku-postgres-pg-jober-staging
jober-staging.80.211.210.46.sslip.io
```

Stop if any value identifies another app or database.

### 2. Take rollback snapshots

```bash
sudo install -d -m 700 /var/backups/jober-staging-reset

jober_reset_stamp="$(date -u +%Y%m%dT%H%M%SZ)"
jober_reset_dump="/var/backups/jober-staging-reset/jober-staging-${jober_reset_stamp}.dump"
jober_reset_media="/var/backups/jober-staging-reset/jober-staging-media-${jober_reset_stamp}.tar.gz"

sudo sh -c "dokku postgres:export pg-jober-staging > '$jober_reset_dump'"
sudo test -s "$jober_reset_dump"
sudo ls -lh "$jober_reset_dump"
sudo sha256sum "$jober_reset_dump"

if sudo test -d /var/lib/dokku/data/storage/jober-staging-media; then
  sudo tar -C /var/lib/dokku/data/storage/jober-staging-media \
    -czf "$jober_reset_media" .
  sudo test -s "$jober_reset_media"
  sudo ls -lh "$jober_reset_media"
  sudo sha256sum "$jober_reset_media"
fi
```

Do not continue after an empty or failed export. These local snapshots are a
short-term rollback aid, not a substitute for the encrypted off-site backup
and restore drill required before the real-data gate.

### 3. Stop the public app before final inventory

This Dokku installation does not have a `maintenance:*` command. Use the core
process controls:

```bash
sudo dokku ps:report jober-staging --running
sudo dokku ps:stop jober-staging
sudo dokku ps:report jober-staging --running
```

The final value must be `false`. Nginx returns 502 while the web process is
stopped; one-off `dokku run` tasks remain available.

### 4. Capture the current schema inventory

```bash
sudo dokku run jober-staging python manage.py shell -c \
'from django.apps import apps
for model in sorted(
    (
        model for model in apps.get_models()
        if model._meta.managed and not model._meta.proxy
    ),
    key=lambda model: model._meta.label_lower,
):
    count = model.objects.count()
    if count:
        print(f"{model._meta.label_lower}: {count}")'
```

Record the account boundary separately:

```bash
sudo dokku run jober-staging python manage.py shell -c \
'from django.db.models import Count
from core.accounts.models import User
from core.offices.models import Office
print("users:", User.objects.count())
print("superusers:", User.objects.filter(is_superuser=True).count())
print("staff:", User.objects.filter(is_staff=True).count())
print("roles:", list(
    User.objects.values("role").annotate(total=Count("id")).order_by("role")
))
print("offices:", Office.objects.count())
print("office memberships:", User.offices.through.objects.count())'
```

### 5. Generate and review the guarded purge payload

The payload must be prepared from the inventory and current deployed code, not
copied blindly from an older reset. It must:

1. require the exact confirmation phrase
   `CLEAR-JOBER-STAGING-OPERATIONAL-DATA`;
2. assert `DATABASES["default"]["HOST"]` is exactly
   `dokku-postgres-pg-jober-staging`;
3. contain the reviewed preserve list from this document;
4. assert both the expected preserved counts and exact non-empty operational
   inventory before changing anything;
5. collect the current `Person.avatar`, `Certificate.front_document` and
   `Certificate.back_document` names before clearing their rows;
6. execute the operational-table `TRUNCATE ... RESTART IDENTITY CASCADE`
   inside `transaction.atomic()`;
7. assert every selected operational model is empty and all account/office
   counts are unchanged before committing;
8. remove only the collected operational media after the database transaction;
9. print a final summary containing cleared-table, deleted-file, user, office
   and office-membership counts.

This design intentionally clears Audit and sessions. Raw PostgreSQL truncation
is used only for this confirmed fictional staging reset; ordinary application
users still cannot alter the append-only Audit log.

Load the reviewed payload into `jober_purge_code`, confirm it is non-empty, and
execute it only against the named app:

```bash
test -n "$jober_purge_code" && echo "Purge code is ready"

sudo dokku run jober-staging \
  env CONFIRM_OPERATIONAL_PURGE=CLEAR-JOBER-STAGING-OPERATIONAL-DATA \
  python manage.py shell -c "$jober_purge_code"
```

Any inventory mismatch must abort without changing data. Leave the app stopped
and investigate; do not weaken or remove the guard merely to make it run.

### 6. Verify before restarting

Re-run the model and account inventories. Only the preserved model rows should
remain; Audit, sessions and every operational model must report zero. Check for
unreferenced operational files separately:

```bash
sudo find \
  /var/lib/dokku/data/storage/jober-staging-media/avatars/person \
  /var/lib/dokku/data/storage/jober-staging-media/certificates \
  -type f 2>/dev/null | wc -l
```

Files under `avatars/user/` belong to retained login accounts and are outside
this cleanup. A non-zero operational-file result means orphaned files need a
separate reviewed cleanup; it does not justify deleting the entire media root.

### 7. Restart and accept

```bash
sudo dokku ps:start jober-staging
sudo dokku ps:report jober-staging --running
curl -fsS https://jober-staging.80.211.210.46.sslip.io/healthz/
```

Expected: `true`, then `ok`. Sign in with retained credentials and verify that
People, Projects, Audit and the other operational lists begin empty. The first
new login creates the first new `auth.login` Audit event and session; that is
expected and proves the new history started after the reset.

## Execution record — 2026-08-05

Target: fictional `jober-staging` on `syncmetric-prime`, database
`pg-jober-staging`.

Rollback artifacts created before the purge:

| Artifact | Size | SHA-256 |
|---|---:|---|
| `/var/backups/jober-staging-reset/jober-staging-20260805T191527Z.dump` | 283 KiB | `4966c6b830b93bc986460e5ddb249f4d16b86cae27d26b8b06876c4c5986c320` |
| `/var/backups/jober-staging-reset/jober-staging-media-20260805T191527Z.tar.gz` | 9.9 MiB | `e5b1f716c8f884e9eec10bc30ca99c47942353c151a7c7b9200625501cc68d29` |

Before the purge: 11 users, one superuser, one staff account, three offices,
nine office memberships, eight people, six projects, 950 Audit events and 91
sessions. The detailed inventory is preserved in the operator transcript for
this reset.

The attempted `maintenance:enable`/`maintenance:report` commands were absent
on this Dokku host and changed nothing. `ps:stop` was used instead and reported
`true` before stopping and `false` afterward.

The guarded purge completed with:

```text
PURGE COMPLETE: 43 operational tables cleared; 10 referenced operational
media files removed; 11 users, 3 offices and 9 office memberships preserved.
```

At the time this entry was written, the destructive step had succeeded and the
app remained stopped pending the post-reset inventory, orphaned-media count,
health check and manual empty-screen acceptance. Record those results in
`deployment_journal.md` rather than retroactively treating them as complete.

