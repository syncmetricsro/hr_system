# Occupational certificate uploads

Status: **Implemented platform-wide 2026-07-31**

This is the shared Jober/CorvinumEU workflow for the only document classes the
base platform stores as files:

- forklift licence;
- crane licence;
- welding licence.

Identity, civil-status, immigration, financial, and medical scans are outside
this feature. Their minimum operational result may be represented as structured
metadata elsewhere, but they cannot use `Certificate` as a generic attachment
escape hatch. See
[`document-storage-boundary.md`](document-storage-boundary.md).

## Product behavior

A recruiter, coordinator, or manager with a sensitive-data relationship to the
person may add one immediately active certificate. The form records:

- the fixed occupational type;
- issuer and certificate number, both optional;
- issue date, optional;
- either an expiry date or “does not expire”;
- one PDF, one front/paper-scan image, or ordered front and back images.

A file is mandatory for every new occupational-certificate record. A PDF is the
whole certificate and cannot have a separate back side. There is no OCR, no
free-text document category, and no verification queue in this slice. Expiry
alerts inform staff but do not block trial, readiness, assignment, or
activation.

Renewal creates a new active row and marks the previous row `superseded`, so the
historical dates and file remain available under Certificate history. Archive
marks a row `archived` and retains its files. Ordinary users cannot hard-delete
a certificate. A manager-only emergency action can permanently purge files
uploaded for the wrong person or outside policy; it requires a reason, archives
the row, and leaves the audit/history metadata behind.

## Data model and enforcement

`features.compliance.Certificate` keeps its historical `HEALTH` and `OTHER`
category values because older metadata and the compliance badge system use
them. File operations, however, use the server-side `FILE_ALLOWED_CATEGORIES`
allowlist and accept only `FORKLIFT`, `CRANE`, or `WELDING`.

Relevant fields are:

- `category` and canonical `name`;
- `issuer` and `certificate_number`;
- `issue_date`, `expiry_date`, and `never_expires`;
- `front_document` and optional `back_document`;
- `record_status` (`active`, `superseded`, `archived`);
- `supersedes`, linking a renewal to the previous row.

The choice list, form, service, and model validation all enforce the allowlist.
The model also rejects an active occupational record without its primary file,
a back without a front, and a PDF combined with a back image. This layered
validation prevents crafted POSTs or service misuse from bypassing the UI.

Migration `compliance.0003_occupational_certificate_files` renames the original
single `document` field to `front_document` without moving stored bytes, adds
the workflow fields, and marks legacy no-expiry rows as `never_expires`.

For a fictional/staging database that predates the allowlist, run:

```text
python manage.py enforce_certificate_storage_policy
```

The default is a read-only report. `--purge-disallowed` requires the explicit
`--confirm-fictional-data` guard because the real-data gate is not open and the
command permanently removes disallowed stored files.

## Upload and delivery security

Images (JPEG, PNG, or WebP) are content-decoded, dimension-capped, resized only
when necessary while preserving aspect ratio, and re-encoded. Re-encoding drops
EXIF, including phone GPS metadata. SVG and all other formats are rejected.

PDFs are limited to four pages, must be unencrypted, and are rejected when they
contain document/page actions, forms, names/attachments, or annotations. An
accepted PDF is rebuilt from its pages so catalogue actions and metadata are not
retained. Each uploaded file is capped at 10 MB.

Files receive UUID storage names under `certificates/` on the protected media
volume. They are never exposed through a public media alias. Django streams each
side through a permission-checked endpoint using private cache headers. Access
requires both office scope and `can_view_sensitive`: managers, observers, the
owning recruiter, and responsible coordinators. Staff may see that a certificate
exists without necessarily receiving its scan.

## RBAC and audit

`certificate.manage` is granted to Recruiter, Coordinator, and Manager/Admin in
both clients. It covers create, metadata/file update, renewal, and archive, but
the person relationship check still applies. `certificate.purge_file` is
manager-only. Observer has read access where ordinary read and sensitive-data
rules permit it, but no write action.

Every mutation records append-only audit data with old and new values:

- `certificate.created` and `certificate.updated`;
- `certificate.renewed` and `certificate.superseded`;
- `certificate.archived`;
- `certificate.files_purged`.

The audit snapshot records file presence, not a secret URL or uploaded file
contents.

## Production gates and deliberate omissions

This feature does not open the real-data gate. DPA/hosting, reviewed sensitive
visibility, retention, encrypted and tested backups, erasure procedures, and a
security review remain required by `AGENTS.md` before real worker documents are
stored.

The current implementation uses filesystem storage and does not apply
application-level or per-file encryption. On Dokku, certificate bytes live on
the client's persistent media volume. The application never exposes that
directory directly, but VPS root/Dokku-equivalent host access can read a mounted
volume. Provider or host-volume encryption may protect detached or disposed
storage; it does not protect files from active root access. Production approval
must therefore verify the provider/volume encryption design, restrict and review
privileged host access, enable encrypted off-site media backups, complete a
restore drill, and explicitly accept the remaining root-access trust boundary.
The full checklist and escalation path are in
[`document-storage-boundary.md`](document-storage-boundary.md#current-at-rest-trust-boundary).

No malware-scanning dependency, OCR, external object store, or document
verification workflow was added. If the client requires excluded high-value
documents, that is a separately scoped Secure Document Vault project with its
own threat model and operating budget; it must not widen this allowlist.

## Language handling

The UI translates the manually selected Forklift/Crane/Welding categories and
upload controls. Jober exposes EN/SK/HU/UK; CorvinumEU exposes SK/HU. The
document bytes themselves have no language-dependent path: safe images are
decoded/re-encoded and PDFs are rebuilt without extracting their text.

Consequently, an occupational certificate written in Slovak, Hungarian,
Ukrainian, English, or another language can be stored when an operator selects
an allowlisted category, but the platform does not detect the language,
recognize the document type, read issuer/number/dates, translate content, or
compare the scan with entered metadata. A high-risk document mislabeled as an
allowlisted category is therefore not detected from its pixels. The fictional
acceptance and cleanup procedure is documented in
[`../deployment/certificate-upload-acceptance.md`](../deployment/certificate-upload-acceptance.md).
