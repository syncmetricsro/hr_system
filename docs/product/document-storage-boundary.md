# Platform document-storage boundary

Status: **Product-owner decision adopted 2026-07-31; client acceptance and
real-data controls still pending**

## Decision

The Jober/CorvinumEU base platform is not a general-purpose identity,
civil-status, immigration, financial, or medical-document repository. It
deliberately minimizes the files it stores:

- high-risk document scans are metadata-only or prohibited;
- file uploads are limited to an explicit occupational-qualification
  allowlist: forklift, crane, and welding licences;
- adding another uploadable class requires a new product and security decision,
  not a catalogue edit or free-text workaround.

This reduces unnecessary breach impact and operating complexity. It does not
lower the security standard for the personal, blacklist, financial, payslip,
audit, and allowlisted certificate data the platform still holds.

## Excluded from the base product

The following must not be uploaded to or copied into Jober or CorvinumEU:

- passports, national identity cards, birth certificates, and residence
  documents;
- medical reports, examination results, diagnoses, and health/fitness
  certificate scans;
- bank statements, tax documents, and comparable high-value personal records;
- unrestricted “other HR attachment” files.

Where the business has a lawful need to verify a requirement, the platform
should retain only the minimum structured result, such as the requirement
type, missing/verified/expired status, verification actor/time, and validity
dates. It should not invite users to copy full identifiers, diagnoses,
examination findings, or document contents into notes. Health-related metadata
may itself be special-category personal data and still needs a lawful basis,
restricted access, retention, and audit.

## File-allowed occupational certificates

The enforced base-product allowlist is:

- forklift licence;
- crane licence;
- welding licence.

These files remain personal data. Authenticated delivery, object-level
authorization, upload sanitation, mutation audit, encrypted backup, retention,
and erasure requirements all apply. The shared implementation is documented in
[`certificate-upload-design.md`](certificate-upload-design.md).

The system must express every future document type as one of:

- `METADATA_ONLY` — only an approved set of structured fields can be retained;
- `FILE_ALLOWED` — a file is allowed for an explicitly approved occupational
  qualification;
- `PROHIBITED` — neither a file nor unnecessary document details are collected.

Training alone is not an adequate control. UI choices, forms, services, model
validation, migration checks, and tests must enforce the same policy. The
current certificate file path enforces the three-value `FILE_ALLOWED` set; a
broader metadata-requirement catalogue remains separate future work — now
sketched as the **paper archive register**
([`paper-archive-register-design.md`](paper-archive-register-design.md),
designed 2026-08-05, not built, C-Q25). It stays inside this boundary: work
papers only, metadata only, and an opaque token in place of any document
number.

## An accountant request does not reopen this boundary

The employer or its payroll accountant may need minimum structured facts for
registrations and payroll, and may need specific civil-status evidence when a
worker actually claims a tax benefit. That does not make the base platform the
right custodian or transport for the underlying scans.

The platform must not upload an identity card, birth certificate, or medical
paper merely in order to forward it. It may later export an approved allowlist
of structured payroll fields and evidence-verification metadata. Any legally
required source evidence is handled through a separately approved employer/
accountant custody and transfer process. Medical examination details never
belong in the ordinary payroll handoff. See
[`accountant-data-handoff.md`](accountant-data-handoff.md).

## Current at-rest trust boundary

The base platform does **not** encrypt each uploaded certificate with an
application-managed key. In the documented Dokku deployment, sanitized files
are stored on the client's persistent media volume. Django controls access
through the web application, but the VPS root user, a Dokku operator with
equivalent host access, and a process that compromises the mounted application
host can read the stored files directly.

This is an explicit current trust boundary, not a claim that the files are
public. Authenticated delivery, office and relationship authorization, UUID
storage names, and HTTPS protect the normal application path. They do not
protect data from a privileged host administrator or a compromised root
account. Disk or volume encryption protects powered-off, detached, or disposed
storage according to the provider/key design, but it also does not hide a
mounted volume from active root access.

Before either client stores real certificate scans, the production security
review must record and approve all of the following:

- the provider's documented disk/volume encryption, or an approved host-level
  encrypted-volume design and its key/recovery ownership;
- who can obtain root/Dokku host access, with SSH-key-only administration,
  least privilege, access review, and a response/rotation procedure;
- per-client media-volume isolation, permissions, retention, erasure, and
  orphan-file handling;
- encrypted off-site media backups and a completed restore drill;
- explicit acceptance of the residual risk that active host root can read the
  mounted files.

If the threat model requires files to remain unreadable to the application host
administrator, the base filesystem design is insufficient. That requirement
needs separately designed application-level encryption/key isolation or the
Secure Document Vault described below. Do not quietly treat a provider's
“encrypted disk” label as satisfying that stronger requirement.

## Optional Secure Document Vault

If a client insists on storing excluded scans, offer a separately scoped and
priced Secure Document Vault project that can integrate with this platform.

**Architecture, data model, phasing and the open commissioning decisions are in
[`secure-document-vault-design.md`](secure-document-vault-design.md)**; the
client-facing version is
[`secure-document-vault-proposal.md`](secure-document-vault-proposal.md). This
section states the requirements only.

It requires its own:

- necessity/lawful-basis and DPIA assessment;
- threat model, access model, and separation of duties;
- encryption and key-management design;
- malware-safe upload and controlled download path;
- complete access audit, retention, deletion, and data-subject procedures;
- encrypted off-site backups and tested recovery;
- hosting, DPA, incident-response, and operating-security budget.

The base platform should retain only status and an opaque vault reference. It
must not duplicate the file or its sensitive contents, and the vault must
authorize each access independently. A shared-drive link is not a substitute.

## Before real data

The remaining confirmations are:

1. client acceptance of the metadata-only/prohibited classes and three-type
   file allowlist;
2. the minimum structured metadata that is legally and operationally needed;
3. access and retention for each retained field/file class;
4. where originals are kept outside the platform;
5. approval of the at-rest trust boundary and production media controls above;
6. whether a separate vault discovery/security project is commissioned.
7. the employing entity, explicit Slovak or Hungarian payroll jurisdiction,
   accountant role, jurisdiction-specific minimum field list, and external
   evidence-custody/transfer process. Mixed, posted, unresolved cross-border,
   and other-country handoffs are out of scope.

The repository-wide real-data gate in `AGENTS.md` remains closed until its DPA,
hosting, permissions, retention, backup, and security-review conditions pass.
