# CorvinumEU cost-conscious production and backup runbook

This runbook is the approved first-year operating model for CorvinumERP. It
uses a **FORPSI Basic Linux VPS** (2 vCPU, 4 GB RAM, 40 GB NVMe) for production
and a separate **Contabo Storage VPS 10 in the EU** as an encrypted backup
target. It is appropriate only while traffic stays low and staging is
on-demand. It is not a capacity guarantee.

The operator completes provider purchases, DPAs, DNS, firewall changes, and
credential setup. Do not put provider passwords, database dumps, GPG private
keys, Supabase tokens, or Doppler values in this repository or in a release
archive.

## 1. Non-negotiable acceptance gates

Do not admit real data until all of these are complete:

- Signed and filed DPA/data-location review for **FORPSI, Contabo, and
  Supabase**. The DPA inventory must cover applicant/personnel data, CVs and
  documents, and financial/bank or payment-record categories where used.
- Retention rules approved for ERP records, website CVs, and backup archives.
- A successful, restricted monthly restore drill completed in **under four
  business hours** and recorded in `deployment_journal.md`.
- Encryption recovery material held outside both VPS providers (for example,
  company-controlled encrypted password manager plus offline recovery copy).
- No raw payment-card data is collected or backed up by either system.

Contabo’s DPA is completed in its customer panel; provider guidance is at
[Contabo’s DPA article](https://help.contabo.com/en/support/solutions/articles/103000274684-can-i-create-a-data-processing-agreement-with-contabo-/).

## 2. Order and provision the hosts

| Role | Selected service | Required choices | Explicit exclusions |
|---|---|---|---|
| Production | FORPSI **Basic Linux VPS** | Ubuntu LTS, 2 vCPU / 4 GB RAM / 40 GB NVMe | No build workload and no permanent staging workload |
| Backup target | Contabo **Storage VPS 10** | European Union region, Ubuntu, one IPv4 address | No Plesk/cPanel, no Object Storage add-on, no public application/database/file-sharing service |

Keep `corvinum.eu` and its website host separate from the ERP host. The
production host serves only the `corvinum` Dokku application and its own
PostgreSQL service. The independent Contabo host accepts encrypted archive
uploads over a restricted SSH account only.

Before an operator first deploys, enforce SSH keys only, disable password SSH,
limit administration source addresses in the firewall where practical, and
expose only HTTPS publicly on the FORPSI host. The backup host needs no public
web or database port.

## 3. Application topology and releases

| Dokku app | Database service | Data rule | Runtime state |
|---|---|---|---|
| `corvinum` | `pg-corvinum` | Production data only after the acceptance gates | Continuously running |
| `corvinum-staging` | `pg-corvinum-staging` | Fictional data only, never a production copy | Start only for rehearsal, deploy checks, and restore drills |

Build the versioned image on CI or a controlled workstation, then transfer the
already-built image to FORPSI. The production VPS must not compile release
images or receive build secrets. Keep exactly the running image and one
previous, verified rollback image; remove older images only after the new
release passes `scripts/deploy_smoke.sh`.

The existing generic Dokku details remain in
[deployment-plan.md](deployment-plan.md). For this host, replace its
always-on Corvinum staging assumption with the on-demand procedure below:

```bash
# Run on the FORPSI host as the Dokku operator.
scripts/corvinum_staging.sh status
scripts/corvinum_staging.sh start
# Deploy/rehearse/restore and run the staging smoke checks.
scripts/corvinum_staging.sh stop
```

`DOKKU_STAGING_APP=another-name` may be supplied only if the host uses a
different app name. Staging must be stopped immediately after the operation.

## 4. Capacity, swap, and upgrade triggers

Before every deploy or restore drill, leave **at least 10 GB free** on the
FORPSI volume. Alert at **60% disk usage** and treat **75%** as urgent.
Configure a modest swap file only as an OOM safety net; recurring swap activity
is a capacity failure, not normal operation.

Upgrade the FORPSI VPS to Standard immediately if any of these occur:

- staging must remain continuously online;
- the restricted restore drill cannot finish within four business hours;
- an OOM event, sustained memory pressure, or recurring swap use appears; or
- disk, CPU, or database pressure prevents reliable deployments/backups.

Host monitoring must record disk use, memory/swap activity, container restart
events, PostgreSQL health, TLS expiry, and HTTP health. Alert delivery itself
is an owner-selected monitoring integration and must not carry application PII.

## 5. Encrypted nightly ERP backup

`scripts/corvinum_offsite_backup.sh` runs **on the FORPSI host**. It creates an
encrypted archive containing:

- `pg-corvinum` through `dokku postgres:export`;
- a non-secret release/domain manifest; and
- the configured ERP media directory after document uploads exist.

It deliberately does **not** export Dokku configuration, because that may
contain Doppler-synchronised credentials. It encrypts before transfer, uploads
with SSH host-key verification, verifies the remote checksum, and retains 35
daily plus 12 monthly (first-of-month) generations.

### One-time owner setup

1. Create a dedicated non-login backup user on Contabo, a restricted
   `authorized_keys` entry for the FORPSI host key, and a root-owned backup
   directory such as `/srv/corvinum-backups`. Restrict the key to SFTP/SCP or
   the minimal forced commands required by the chosen SSH policy; do not give
   it sudo.
2. Generate an encryption key under company control. Import **only its public
   recipient key** to the FORPSI host. Store the private recovery key outside
   FORPSI and Contabo. Test decryption from the recovery location before any
   production data is accepted.
3. Create a root-owned `/etc/corvinum/backup.env` (mode `0600`), outside the
   repository, with values equivalent to:

   ```bash
   BACKUP_REMOTE=corvinum-backup@<contabo-ip-or-hostname>
   BACKUP_REMOTE_DIR=/srv/corvinum-backups
   BACKUP_GPG_RECIPIENT=<public-key-fingerprint>
   BACKUP_SSH_KEY=/root/.ssh/corvinum-backup_ed25519
   DOKKU_APP=corvinum
   POSTGRES_SERVICE=pg-corvinum
   # Add only after ERP uploads exist:
   # MEDIA_SOURCE_DIR=/absolute/path/to/corvinum/media
   ```

4. Install the script with the release and schedule it from the host’s
   root-owned scheduler, for example:

   ```cron
   15 02 * * * . /etc/corvinum/backup.env && /home/dokku/HR_System/scripts/corvinum_offsite_backup.sh >> /var/log/corvinum-backup.log 2>&1
   45 02 * * * . /etc/corvinum/backup.env && /home/dokku/HR_System/scripts/corvinum_backup_health.sh >> /var/log/corvinum-backup-health.log 2>&1
   ```

   Adjust the repository path to the deployed release location. Scheduler
   logs must be access-restricted and rotated. Do not source Doppler exports
   into the backup task: it needs no application secrets.

`scripts/corvinum_backup_health.sh` fails when no verified daily archive is
younger than **26 hours** or the Contabo filesystem reaches **60%** use. Treat
either failure as an operational incident. Upgrade the target before retained
encrypted archives exceed 60% of its 300 GB capacity.

## 6. Website Supabase data is a separate backup stream

The `corvinum.eu` website’s Supabase database and its private CV/storage bucket
are not reachable through the ERP PostgreSQL service. They require a separate,
least-privilege Supabase backup identity and an approved private-bucket export
method. That credential has not been placed in this repository and must not be
reused from a developer session.

Before the real-data gate, the website operator must automate all of the
following into the same encrypted Contabo retention scheme:

1. a Supabase database export;
2. a complete private CV/storage-bucket export with an object manifest; and
3. checksum, encryption, off-site transfer, retention, and restore testing.

Record the first full database and private-storage sizes. If the 35 daily and
12 monthly encrypted generations would exceed 60% of the 300 GB target, expand
or replace the backup target **before** that point. Do not rely on a VPS
snapshot, a database export alone, or a public bucket for recoverability.

## 7. Monthly restore drill

Once per calendar month, schedule a short maintenance window:

1. Start fictional-data staging with `scripts/corvinum_staging.sh start`.
2. Copy one encrypted archive to the approved restricted restore workspace and
   decrypt it only there using the company-held recovery key.
3. Restore PostgreSQL into `pg-corvinum-staging` or another isolated scratch
   service; never into production. Use
   `scripts/backup_restore_drill.sh` or the equivalent Dokku restore procedure
   to verify tables and row counts.
4. For website data, test the database export and a sample of the private CV
   object manifest in an isolated Supabase project/bucket.
5. Record start/end time, archive timestamp, verification result, cleanup, and
   any fault in `deployment_journal.md`; target under four business hours.
6. Stop staging with `scripts/corvinum_staging.sh stop` and securely remove
   temporary decrypted material.

## 8. Day-one checklist

- [ ] FORPSI Basic and Contabo Storage VPS 10 provisioned in the approved EU
      locations; Contabo Object Storage remains **None**.
- [ ] Provider DPAs, data-location review, and retention approval complete.
- [ ] Production/staging apps each have a separate database; staging contains
      fictional data only and is stopped when idle.
- [ ] Production uses HTTPS, secure cookies, SSH keys, restricted firewall,
      and Doppler-injected runtime secrets.
- [ ] GPG public key imported to FORPSI; recovery material stored outside both
      providers; nightly backup and health schedules have passed once.
- [ ] Website Supabase database + private CV bucket export is automated,
      encrypted, transferred, and restore-tested.
- [ ] A monthly restore drill has completed in under four business hours.
