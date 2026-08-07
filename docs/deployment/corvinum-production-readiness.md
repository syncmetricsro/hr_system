# CorvinumEU PeopleOps production readiness backlog

Status: **Canonical production backlog — collected 2026-08-07. No real worker
data is authorized yet.**

This document is the single place to answer: “What still has to be decided,
built, configured, reviewed, and proven before Corvinum PeopleOps can enter
production?” The detailed operating procedure remains
[`corvinum-basic-production.md`](corvinum-basic-production.md); product
questions remain in
[`corvinum-open-questions.md`](../product/corvinum-open-questions.md).

Writing an item here does not make it complete. A gate becomes complete only
when its evidence is linked from this file or recorded in a living journal.

## 1. Approved two-server production topology

The two permanent Corvinum production hosts are:

| Hostname | Provider | Purpose | Must not do |
|---|---|---|---|
| `corvinum-main` | FORPSI | Production Dokku app `corvinum`, PostgreSQL service `pg-corvinum`, protected persistent media, TLS termination, scheduled backup creation | Build images, contain demo seeds, expose PostgreSQL publicly, or act as the only backup location |
| `corvinum-bsite` | Contabo | Receive and retain already-encrypted database/media/release archives from `corvinum-main` | Run PeopleOps, expose a database or file-sharing service, hold application secrets, or hold the backup private decryption key |

The existing `corvinum-staging` app on `syncmetric-prime` remains a
fictional-data release rehearsal environment outside this production pair. It
must never receive a restored production database or media volume.

```text
PeopleOps users --HTTPS--> corvinum-main
                               |-- Dokku app: corvinum
                               |-- PostgreSQL: pg-corvinum
                               |-- protected media volume
                               |
                               +-- encrypt locally --> corvinum-bsite
                                                        encrypted archives only

Company-held recovery key: outside both servers
Source/image history: GitHub + verified release artifacts
Runtime secrets: Doppler, injected only into corvinum-main
```

`corvinum-bsite` is a **backup site, not a warm standby**. It cannot take user
traffic after a failure. The initial recovery objectives are a maximum
24-hour data-loss window from nightly backups and restoration within four
business hours. If the client needs automatic failover or materially shorter
outage/data-loss limits, that requires another approved architecture and
budget; it must not be implied by the name “bsite.”

## 2. What is already reusable

The following foundations exist and should be verified, not rebuilt:

- the Corvinum thin client and its People, Projects, Trials, readiness and
  activation, occupational certificates, equipment, blacklist, ledger, gross
  wages, encrypted payslips, structured offer emails, Reports, Help,
  notifications, and Audit surfaces;
- role-gated server-side actions and protected media delivery;
- Manager-required TOTP in staging/production, with the localhost-only bypass
  isolated in `clients.corvinum_eu.local`;
- production HTTPS/cookie/HSTS settings, WhiteNoise static delivery, `/healthz/`,
  migration checks, production-image checks, and deploy smoke scripts;
- encrypted backup, backup-health, and restore-drill script foundations;
- real SMTP delivery proven with a controlled recipient through Doppler; and
- SK/HU client UI with complete compiled catalogs.

These are not enough to open the real-data gate. The gaps below remain.

## 3. P0 engineering — must land before production users

### COR-ENG-01 — account onboarding and credential lifecycle

Implement the approved
[`account-onboarding`](../product/corvinum-account-onboarding.md) boundary:

- Observer and Manager may invite Recruiter, Coordinator, or Manager;
- Recruiter and Coordinator cannot invite; nobody can invite an Observer;
- the first Observer uses a controlled deployment bootstrap;
- setup links are expiring, revocable, single-use, and do not reveal or create
  temporary shared passwords;
- users can change/recover their password; authorized staff can deactivate an
  account and perform a controlled lost-TOTP recovery;
- role changes, invitations, acceptance, revocation, account status, and TOTP
  recovery are audited without logging tokens or secrets; and
- Observer receives a narrow invitation action, not broad `user.manage`.

Open choices in C-Q24—expiry, resend, duplicate/inactive email handling,
deactivation/role-change authority, and final approval—must be resolved before
the model and routes are frozen.

### COR-ENG-02 — privileged authentication hardening

- Extend production TOTP from Manager to **Observer**, because Observer can
  invite privileged users and read Audit, ledger, wage, payslip, and export
  data. Decide whether Recruiter and Coordinator also require TOTP.
- Add server-side login and TOTP-attempt rate limiting with generic error
  behavior; none exists today.
- Audit failed authentication safely, without recording a submitted password
  or turning arbitrary email addresses into a durable PII log.
- Approve a shorter or explicitly accepted rolling session lifetime; the
  current default is 30 days of inactivity.
- Decide the break-glass administration path. A Django superuser is a
  SyncMetric operational identity, not the client's Observer account. Restrict
  or disable public Django-admin access if it is not required, and document
  credential custody and recovery either way.

### COR-ENG-03 — production-safe initialization

A clean production database currently has no safe Corvinum-specific bootstrap.
The activation checklist lives inside `seed_corvinum_demo`, which also creates
known-password demo users, fictional workers, projects, wages, and payslips.
Production must instead have an idempotent initializer that creates **only**
client-approved configuration:

- the published intake questionnaire/version;
- the approved activation checklist and help text;
- approved inactive and blacklist categories;
- required client settings/catalog defaults; and
- the first Observer bootstrap handoff.

`seed_corvinum_demo` must be unavailable or fail closed under production
settings. Production initialization must never create fictional accounts,
people, projects, offers, ledger entries, wages, payslips, or known passwords.
System checks must refuse a production launch with no active critical
activation checklist; an empty template set must not make activation easier.

### COR-ENG-04 — retention, erasure, and data-subject operations

Agree a signed retention schedule, then implement it across every Corvinum
personal-data store: Person/intake data and avatars, certificates and files,
blacklist cases/fingerprints, project/trial/readiness/checklist history,
equipment custody/recovery, advances and settlement cycles, gross wages,
payslips and delivery addresses, offer-email records/bodies, Audit events, and
sessions.

Current automated retention is materially incomplete: blacklist fingerprints
and offer emails register jobs, but offer retention defaults to “keep forever,”
and most other stores have no purge/anonymization path. Required behavior:

- preview/dry-run and reviewed execution for destructive jobs;
- legal-hold and statutory-record exceptions;
- file deletion alongside database anonymization where permitted;
- an audited Art. 15/16/17/18 request workflow for access, correction,
  erasure, and restriction; operational Archive is not erasure;
- scheduled `run_retention` execution and failure alerting on `corvinum-main`;
  and
- documented deletion latency in encrypted backup generations.

### COR-ENG-05 — audit coverage and privileged-access boundary

Re-run a current audit review after onboarding is built. At minimum cover:

- failed login/TOTP attempts and every account/role/status/TOTP-recovery action;
- certificate file views/downloads and emergency purges;
- wage, payslip, ledger, blacklist, and personal-data exports/views where the
  approved policy requires access logging;
- retention, erasure, restore, and configuration/bootstrap operations; and
- who can bypass application immutability through Django admin, database, or
  host access.

The current audit model is append-only in application code, not against a
database owner or host root. Production approval must either strengthen that
boundary or explicitly accept and monitor it.

### COR-ENG-06 — media lifecycle and upload failure behavior

- Keep media on a dedicated persistent `corvinum-main` volume and deliver it
  only through Django authorization; never add a public nginx `/media/` alias.
- Implement the historical orphan-file sweep and the approved
  retention/erasure deletion path.
- Confirm FORPSI disk/volume encryption, file ownership/modes, privileged-host
  access, encrypted media backup, and the residual fact that active root can
  read mounted files.
- Set Dokku/nginx `client-max-body-size` to `25m`, rebuild the proxy config, and
  add a branded/graceful 413 response. The application keeps its stricter
  per-file limits and validation.
- Have the security review explicitly accept the current sanitized-image/PDF
  design without malware scanning, or commission an approved scanning design.

Only forklift, crane, and welding licence files are allowed. Identity cards,
passports, birth certificates, residence papers, medical reports, and health
certificate scans remain outside PeopleOps.

### COR-ENG-07 — independent outbound-email safety gates

Payslip delivery and job-offer email share SMTP but have different legal and
operational approval. Production must be able to disable either workflow
independently and fail closed when its gate is incomplete.

- Offers: either approve lawful basis/transparency text, provider DPA,
  retention, opt-out handling, and real-recipient use, or keep offer sending
  disabled in production.
- Payslips: approve the recorded-net meaning, PDF wording/itemization decision,
  password handoff channel, retention, and recipient correction process before
  real delivery.
- Configure `noreply@corvinum.eu`, SMTP TLS, sender-domain SPF/DKIM/DMARC, bounce
  or non-delivery handling, and a monitored operational contact.
- Keep `EMAIL_ALLOWED_RECIPIENTS` mandatory on staging. Remove or change that
  restriction for production only as an explicit cutover step after approval.

### COR-ENG-08 — production configuration checks

Add a fail-closed production check covering at least:

- `clients.corvinum_eu.production`, `DEBUG=False`, real secret key, exact
  allowed host/domain, secure cookies/redirects, and TOTP-required roles;
- PostgreSQL connectivity and a persistent writable `MEDIA_ROOT` mount;
- an independent rotatable `BLACKLIST_HMAC_KEYS` value rather than relying on
  the Django secret-key fallback;
- approved non-placeholder blacklist, offer, pay, audit, certificate, and
  worker retention settings;
- correct SMTP sender/config when an email workflow is enabled;
- no production demo command/data/account, no test recipient allowlist drift,
  and no console email backend; and
- the client-approved language/theme, medical-validity interval, ledger cutoff,
  and cycle rules.

`manage.py check --deploy` and this client check must run before each release.

### COR-ENG-09 — production-grade restore tooling

The current restore helper proves row-count restoration in controlled test
environments, but the two-host production procedure needs a rehearsed wrapper:

- fetch and verify one encrypted archive from `corvinum-bsite`;
- decrypt only in an approved restricted workspace using the company-held key;
- restore PostgreSQL and media into a temporary isolated scratch service,
  never the live `corvinum` app and never shared fictional staging;
- verify schema, representative records, protected files, checksums, and app
  boot—not row counts alone;
- securely remove decrypted scratch data; and
- record RPO/RTO and evidence in `deployment_journal.md`.

With only two permanent servers, the initial scratch environment may be
temporary and private on `corvinum-main` during a maintenance window, provided
capacity and isolation are proven. `corvinum-bsite` must remain encrypted-
archive-only.

## 4. Client/product decisions that can change code

All items below need written confirmation. Existing defaults may be kept, but
silence is not acceptance.

| Decision group | Questions to settle | Effect if the current default is rejected |
|---|---|---|
| Lifecycle and roles | Status flow, HR Admin→Manager mapping, single-admin behavior, SK default, dark default (C-Q1/C-Q8/C-Q9) | Policy, labels, tests, and Help change |
| Intake and activation | Exact required fields, nine checklist definitions, EU/non-EU permit behavior, duplicate-check meaning (C-Q7/C-Q22) | Questionnaire/checklist production initializer and gates change |
| Medical metadata | Which fitness date is stored, who can view it, job/country-specific validity instead of the current global 12 months | Compliance calculation, activation gate, retention, and access tests change |
| Ledger rhythm | Thursday cutoff, 20th boundary, carry-forward, partial recovery, travel/fuel rules (C-Q2/C-Q3/C-Q4/C-Q10) | Ledger services, exports, and historical migration may change |
| Wage/payslip meaning | Financial boundary, whether recorded net is before/after advances, whether PDFs itemize deductions, password channel (C-Q6/C-Q15/C-Q17/C-Q20/C-Q21) | Labels, validation, PDF, Help, and possibly model/export changes |
| Equipment | Which items have recoverable values and who approves them (C-Q12) | Catalogue defaults and recovery policy change |
| Documents | Accept metadata-only/prohibited classes, three-file allowlist, external paper custody, and whether the optional paper register is wanted (C-Q18/C-Q25) | Base boundary stays closed; optional register is a separate implementation |
| Accountant handoff | Employing entity, explicit SK/HU jurisdiction, accountant role/DPA, fields, secure transfer, custody, retention (C-Q19) | Separate future feature; unresolved/mixed/other-country cases must fail closed |
| Outbound offers | Lawful basis, transparency/opt-out text, provider DPA, message retention (C-Q23) | Enable production sending only after approval; otherwise disable |
| Onboarding operations | Expiry, resend/revoke, duplicate/inactive email, role/deactivation/TOTP authority, final approval (C-Q24) | Account-onboarding model and policy change |

Bus fuel logging, the paper archive register, accountant export, and payslip
itemization are not assumed launch features merely because they are designed.

## 5. Legal, privacy, and organizational P0 gates

- Identify the controller/employing entity and document the processing
  purposes/lawful bases for recruitment, employment administration, medical
  fitness metadata, blacklist matching, equipment recovery, wage/pay records,
  and job-offer outreach.
- Sign and inventory applicable Article 28 agreements and EU data locations
  for FORPSI, Contabo, the SMTP/mail provider, and any other real processor.
  Include Supabase only if the separate website/CV flow is part of launch;
  include the accountant only if a handoff is commissioned.
- Approve the role/sensitive-field matrix, privileged-host access list,
  onboarding authority, export access, session policy, and TOTP scope.
- Approve the retention schedule, backup retention/deletion latency, legal
  holds, original-paper custody, data-subject request procedure, and
  termination/return-of-data procedure.
- Complete the blacklist necessity/legal-basis assessment and the job-offer
  outreach assessment before those features handle real people. Disable either
  feature if its gate is not complete.
- Complete a current security review and external penetration test after P0
  engineering. The June review predates Corvinum onboarding, payslips, wages,
  offer email, certificate uploads, and several permission changes.
- Maintain an incident-response and GDPR breach-notification procedure with
  named Corvinum/SyncMetric contacts, evidence preservation, credential
  rotation, worker communication, and recovery responsibilities.
- Obtain explicit acceptance of the document-storage boundary and residual
  active-root risk. If excluded scans are required, stop and scope the Secure
  Document Vault separately.
- Decide whether production starts empty or receives an opening-data import.
  Any import needs a field mapping, legal transfer route, validation/deduping,
  reconciliation totals, rollback plan, and deletion of temporary copies. Real
  source data must never travel through Git, issue trackers, ordinary email, or
  fictional staging.
- Name the operational owners for access reviews, onboarding, document
  classification, blacklist decisions, pay/ledger corrections, backups,
  incidents, and vendor support. Train every user against the SK/HU Help and
  the “no excluded scans” boundary before their account is activated.
- Adopt an end-user security baseline: individual accounts only, no shared
  passwords/TOTP devices, managed and patched browsers/devices, screen lock,
  secure password storage, and a written lost/stolen-device reporting path.

## 6. `corvinum-main` infrastructure and deployment tasks

- Provision the approved FORPSI Ubuntu LTS host and set hostname
  `corvinum-main`; record provider account owner, EU location, service/spec,
  support route, and DPA.
- Use SSH keys only; disable password/root remote login, restrict SSH source
  addresses where practical, expose only HTTP/HTTPS publicly, and leave
  PostgreSQL private. Record every human with host/Dokku access.
- Configure security updates, time synchronization, firewall, log rotation,
  a modest OOM-only swap file, and a documented patch/reboot window.
- Install the approved Dokku/PostgreSQL stack, app `corvinum`, service
  `pg-corvinum`, and protected persistent media mount. Do not build release
  images on this host.
- Choose the final PeopleOps domain, create DNS, enable/renew TLS, run the HTTPS
  smoke suite, and verify HSTS, secure cookies, host/proxy handling, clickjacking
  and MIME-sniffing protection. Review CSP, Referrer-Policy, and
  Permissions-Policy during the security pass rather than assuming them.
- Inject a dedicated production Doppler configuration; keep database, Django,
  SMTP, blacklist-HMAC, backup, and bootstrap secrets out of Git, images,
  shell history, logs, and screenshots. Document rotation and disaster access.
- Build a versioned image in the controlled build environment, verify it, load
  it into Dokku, run migrations and production-safe initialization, then run
  smoke/UAT. Keep one verified rollback image and take a fresh encrypted backup
  before risky migrations.
- Monitor HTTP health, TLS expiry, PostgreSQL, disk, memory/swap, container
  restarts, application/security errors, backup freshness, and scheduled
  retention. Alerts must carry no worker PII.
- Keep at least 10 GB free; alert at 60% disk and treat 75% as urgent. Upgrade
  the VPS if recurring swap/OOM, capacity pressure, or restore time breaks the
  agreed limits.

## 7. `corvinum-bsite` backup tasks

- Provision the approved Contabo EU Storage VPS and set hostname
  `corvinum-bsite`; record account owner, location, capacity, support, and DPA.
- Do not install Dokku or expose HTTP, PostgreSQL, object storage, or public file
  sharing. Permit SSH transfer only from `corvinum-main` and named emergency
  administrators.
- Create a dedicated non-login, non-sudo backup identity restricted to the
  minimum transfer/checksum/retention commands and a root-owned backup tree.
- Store only GPG-encrypted archives. The decryption private key and recovery
  material live outside both servers; `corvinum-main` holds only the public
  recipient key.
- Run nightly database + media + non-secret release-manifest backups from
  `corvinum-main`, encrypt before transfer, verify the remote checksum, retain
  35 daily and 12 monthly generations, and alert when the newest verified copy
  exceeds 26 hours or storage reaches 60%.
- Back up the website Supabase database/private CV bucket as a separate stream
  only if that system is included in the production recovery scope. PeopleOps
  database backups do not cover it.
- Prove a complete monthly restore in under four business hours. A backup is
  not accepted merely because a cron job exits successfully.

## 8. Release, UAT, and go-live evidence

Before the first production user or real record:

- [ ] All P0 engineering items above are merged; Ruff, dependency direction,
      both client unit lanes, migration checks, production-image/static checks,
      secret/no-Node/vendor checks, and the full two-client browser suite pass
      on the exact release revision.
- [ ] SK and HU text—including onboarding, password recovery, retention notices,
      mail, Help, and errors—has native-speaker review; catalogs have no fuzzy,
      blank, divergent, or stale entries.
- [ ] Corvinum UAT covers all four roles, denied actions, mobile/desktop,
      light/dark, intake, activation, certificates, equipment, ledger, wages,
      payslips, offers (if enabled), reports, audit, account onboarding,
      deactivation, and TOTP recovery.
- [ ] A clean-database rehearsal proves the production initializer, first
      Observer bootstrap and TOTP, Observer→Manager invitation, Manager TOTP,
      and zero demo users/data/known passwords.
- [ ] A controlled SMTP test proves the exact sender, TLS, receipt, blocked
      staging recipients, failure handling, and absence of passwords/tokens
      from logs/audit.
- [ ] Fictional avatar and certificate fixtures prove protected upload,
      authorized download, replacement cleanup, emergency purge, nginx request
      limits, and the graceful 413 path.
- [ ] `corvinum-main` and `corvinum-bsite` hardening, access lists, monitoring,
      backup health, key custody, and a full restore drill are recorded.
- [ ] Legal/privacy gates, client decisions, document boundary, residual risks,
      incident response, support ownership, RPO, and RTO are signed off.
- [ ] The opening-data decision is signed off. If data is imported, source and
      destination counts, rejected rows, duplicate resolution, temporary-file
      cleanup, and client acceptance are recorded.
- [ ] Production deploy uses no seed command. After migrations/bootstrap, run
      HTTPS smoke checks, a role/2FA check, backup check, and a rollback
      rehearsal before admitting worker data.

## 9. Explicitly not required for the initial launch

Unless the client separately commissions them, the following do not block the
base PeopleOps production launch:

- Secure Document Vault or storage of excluded identity/civil/medical scans;
- paper archive register and QR labels;
- accountant export or evidence transfer;
- statutory payroll/net-pay calculation or `radonak.xlsx` automation;
- bus fuel logging;
- accommodation, transport scheduling, profitability/P&L, SMS, Telegram,
  worker portal, or feedback; and
- warm standby/automatic failover from `corvinum-bsite`.

If any of these becomes a launch promise, move it into P0 with its own approved
requirements, legal/security boundary, tests, and operating runbook.

## 10. Recommended execution order

1. Resolve client decisions, legal gates, launch feature enable/disable choices,
   RPO/RTO, domain, and processor agreements.
2. Build onboarding/credential lifecycle, privileged-auth hardening, safe
   production initialization, and fail-closed production checks.
3. Build retention/erasure, audit completion, media cleanup, and independent
   outbound-email gates.
4. Provision and harden `corvinum-main` and `corvinum-bsite`; configure DNS,
   Doppler, persistent media, encrypted backups, monitoring, and alerts.
5. Complete current security review/penetration test and fix findings.
6. Run clean-database, staging, email, role, upload, backup, and restore UAT.
7. Obtain written go-live sign-off, deploy the exact accepted image, bootstrap
   the first Observer, and admit real data only after every P0 gate is evidenced.
