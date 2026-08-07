# CorvinumEU cost-conscious production and backup runbook

This runbook is the approved first-year operating model for CorvinumERP. Its
two permanent hosts are **`corvinum-main`**, a FORPSI Basic Linux VPS (2 vCPU,
4 GB RAM, 40 GB NVMe) for production, and **`corvinum-bsite`**, a separate
Contabo Storage VPS 10 in the EU that stores encrypted backup archives only.
It is appropriate only while traffic stays low. It is not a capacity guarantee
or an automatic-failover design. The complete launch backlog is
[`corvinum-production-readiness.md`](corvinum-production-readiness.md).

The operator completes provider purchases, DPAs, DNS, firewall changes, and
credential setup. Do not put provider passwords, database dumps, GPG private
keys, Supabase tokens, or Doppler values in this repository or in a release
archive.

## 1. Non-negotiable acceptance gates

Do not admit real data until all of these are complete:

- Signed and filed DPA/data-location review for **FORPSI, Contabo, and the SMTP
  provider**. Include Supabase if the separate website/CV flow is placed inside
  the launch recovery scope. The inventory must cover applicant/personnel data,
  CVs and documents, and financial/bank or payment-record categories where
  used.
- Retention rules approved for ERP records and backup archives, plus website
  CVs if that separate flow is included.
- A successful, restricted monthly restore drill completed in **under four
  business hours** and recorded in `deployment_journal.md`.
- Encryption recovery material held outside both VPS providers (for example,
  company-controlled encrypted password manager plus offline recovery copy).
- The FORPSI disk/volume encryption and key/recovery arrangement is documented
  and approved, privileged root/Dokku access is restricted and reviewed, and
  the residual fact that active host root can read the mounted ERP media volume
  is explicitly accepted. The application does not provide per-file encryption;
  see `docs/product/document-storage-boundary.md` §Current at-rest trust
  boundary.
- No raw payment-card data is collected or backed up by either system.
- The production account-onboarding gate in
  `docs/product/corvinum-account-onboarding.md` is implemented and rehearsed:
  Observer and Manager can invite Recruiter, Coordinator, or Manager through a
  secure audited flow; nobody can invite an Observer; Observer and Manager
  TOTP enrolment and account recovery work without shared or temporary
  passwords.

Contabo’s DPA is completed in its customer panel; provider guidance is at
[Contabo’s DPA article](https://help.contabo.com/en/support/solutions/articles/103000274684-can-i-create-a-data-processing-agreement-with-contabo-/).

## 2. Order and provision the hosts

| Role | Selected service | Required choices | Explicit exclusions |
|---|---|---|---|
| `corvinum-main` — production | FORPSI **Basic Linux VPS** | Ubuntu LTS, 2 vCPU / 4 GB RAM / 40 GB NVMe | No build workload and no staging workload |
| `corvinum-bsite` — backup | Contabo **Storage VPS 10** | European Union region, Ubuntu, one IPv4 address | No Plesk/cPanel, no Object Storage add-on, no public application/database/file-sharing service, no decryption private key |

Keep `corvinum.eu` and its website host separate from the ERP host.
`corvinum-main` serves only the `corvinum` Dokku application and its own
PostgreSQL service, apart from a temporary isolated restore scratch service
during a planned drill. `corvinum-bsite` accepts encrypted archive uploads over
a restricted SSH account only.

Before an operator first deploys, enforce SSH keys only, disable password SSH,
limit administration source addresses in the firewall where practical, and
expose only HTTPS publicly on `corvinum-main`. `corvinum-bsite` needs no public
web or database port and should accept backup SSH only from `corvinum-main` and
named emergency administrators.

## 3. Application topology and releases

| Dokku app | Database service | Data rule | Runtime state |
|---|---|---|---|
| `corvinum` on `corvinum-main` | `pg-corvinum` | Production data only after the acceptance gates | Continuously running |
| `corvinum-staging` on existing `syncmetric-prime` | `pg-corvinum-staging` | Fictional data only, never a production copy | Release rehearsal outside the production pair |

Build the versioned image on CI or a controlled workstation, then transfer the
already-built image to `corvinum-main`. The production VPS must not compile
release images or receive build secrets. Keep exactly the running image and one
previous, verified rollback image; remove older images only after the new
release passes `scripts/deploy_smoke.sh`.

The existing generic Dokku details remain in
[deployment-plan.md](deployment-plan.md). The current fictional staging app on
`syncmetric-prime` remains the release-rehearsal target; do not copy it to
`corvinum-main`, and never restore production data into it.

## 4. Capacity, swap, and upgrade triggers

Before every deploy or restore drill, leave **at least 10 GB free** on
`corvinum-main`. Alert at **60% disk usage** and treat **75%** as urgent.
Configure a modest swap file only as an OOM safety net; recurring swap activity
is a capacity failure, not normal operation.

Upgrade the FORPSI VPS to Standard immediately if any of these occur:

- the production workload or temporary isolated restore scratch cannot fit
  without pressure;
- the restricted restore drill cannot finish within four business hours;
- an OOM event, sustained memory pressure, or recurring swap use appears; or
- disk, CPU, or database pressure prevents reliable deployments/backups.

Host monitoring must record disk use, memory/swap activity, container restart
events, PostgreSQL health, TLS expiry, and HTTP health. Alert delivery itself
is an owner-selected monitoring integration and must not carry application PII.

## 5. Encrypted nightly ERP backup

`scripts/offsite_backup.sh` runs **on `corvinum-main`** (renamed from
`corvinum_offsite_backup.sh` on 2026-07-26 when it was generalised to back up
any Dokku app; set `DOKKU_APP`, `POSTGRES_SERVICE` and `BACKUP_PREFIX`
explicitly). It creates an
encrypted archive containing:

- `pg-corvinum` through `dokku postgres:export`;
- a non-secret release/domain manifest; and
- the configured ERP media directory after document uploads exist.

It deliberately does **not** export Dokku configuration, because that may
contain Doppler-synchronised credentials. It encrypts before transfer, uploads
with SSH host-key verification, verifies the remote checksum, and retains 35
daily plus 12 monthly (first-of-month) generations.

### One-time owner setup

1. Create a dedicated non-login backup user on `corvinum-bsite`, a restricted
   `authorized_keys` entry for the `corvinum-main` host key, and a root-owned
   backup directory such as `/srv/corvinum-backups`. Restrict the key to SFTP/SCP or
   the minimal forced commands required by the chosen SSH policy; do not give
   it sudo.
2. Generate an encryption key under company control. Import **only its public
   recipient key** to `corvinum-main`. Store the private recovery key outside
   `corvinum-main` and `corvinum-bsite`. Test decryption from the recovery
   location before any production data is accepted.
3. Create a root-owned `/etc/corvinum/backup.env` (mode `0600`) on
   `corvinum-main`, outside the
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
   15 02 * * * . /etc/corvinum/backup.env && /home/dokku/HR_System/scripts/offsite_backup.sh >> /var/log/corvinum-backup.log 2>&1
   45 02 * * * . /etc/corvinum/backup.env && /home/dokku/HR_System/scripts/backup_health.sh >> /var/log/corvinum-backup-health.log 2>&1
   ```

   Adjust the repository path to the deployed release location. Scheduler
   logs must be access-restricted and rotated. Do not source Doppler exports
   into the backup task: it needs no application secrets.

`scripts/backup_health.sh` fails when no verified daily archive is
younger than **26 hours** or the Contabo filesystem reaches **60%** use. Treat
either failure as an operational incident. Upgrade the target before retained
encrypted archives exceed 60% of its 300 GB capacity.

## 6. Website Supabase data is a separate, conditional backup stream

If the separate website/CV system is included in the agreed launch recovery
scope, the `corvinum.eu` website’s Supabase database and private CV/storage bucket
are not reachable through the ERP PostgreSQL service. They require a separate,
least-privilege Supabase backup identity and an approved private-bucket export
method. That credential has not been placed in this repository and must not be
reused from a developer session.

Before treating that website flow as protected by this backup design, its
operator must automate all of the following into the same encrypted Contabo
retention scheme:

1. a Supabase database export;
2. a complete private CV/storage-bucket export with an object manifest; and
3. checksum, encryption, off-site transfer, retention, and restore testing.

Record the first full database and private-storage sizes. If the 35 daily and
12 monthly encrypted generations would exceed 60% of the 300 GB target, expand
or replace the backup target **before** that point. Do not rely on a VPS
snapshot, a database export alone, or a public bucket for recoverability.

## 7. Monthly restore drill

Once per calendar month, schedule a short maintenance window:

1. Create a temporary, network-restricted scratch database and media workspace
   on `corvinum-main` during the approved maintenance window. It must use
   explicit scratch names and must not be linked to the live `corvinum` app.
2. Copy one encrypted archive to the approved restricted restore workspace and
   decrypt it only there using the company-held recovery key.
3. Restore PostgreSQL and media into that scratch service; never into
   `pg-corvinum`, the live app, or shared fictional staging. Use the
   production-grade wrapper required by
   [`corvinum-production-readiness.md`](corvinum-production-readiness.md)
   to verify schema, representative data, files, checksums, and application
   boot—not row counts alone.
4. If the website/CV flow is in recovery scope, test its database export and a
   sample of the private CV object manifest in an isolated Supabase
   project/bucket.
5. Record start/end time, archive timestamp, verification result, cleanup, and
   any fault in `deployment_journal.md`; target under four business hours.
6. Destroy the scratch database/service and securely remove temporary decrypted
   material. Confirm the live production app remained untouched.

## 8. Day-one checklist

- [ ] `corvinum-main` (FORPSI Basic) and `corvinum-bsite` (Contabo Storage VPS
      10) provisioned in the approved EU locations; Contabo Object Storage
      remains **None**.
- [ ] Provider DPAs, data-location review, and retention approval complete.
- [ ] `corvinum-main` contains production only; existing staging remains on
      `syncmetric-prime`, contains fictional data only, and never receives a
      production restore.
- [ ] Production uses HTTPS, secure cookies, SSH keys, restricted firewall,
      and Doppler-injected runtime secrets.
- [ ] GPG public key imported to `corvinum-main`; recovery material stored
      outside both providers; nightly backup and health schedules have passed
      once.
- [ ] If the website/CV flow is in launch recovery scope, its Supabase database
      + private bucket export is automated, encrypted, transferred, and
      restore-tested; otherwise the exclusion is written down.
- [ ] A monthly restore drill has completed in under four business hours.
- [ ] The first Observer was created through the controlled deployment
      bootstrap and completed TOTP; that Observer successfully invited a
      Manager through the expiring, single-use onboarding flow, and the
      Manager completed TOTP.
