# Certificate document uploads

Status: **Implemented 2026-07-24**, exactly as designed below — data model
(`category` + `document`), Pillow/pypdf validation, RBAC
(`certificate.manage`), the person-detail Certificates panel, and audit
events, for both Jober and CorvinumEU. One naming deviation: an edit that
only changes dates (no new document) audits as `certificate.updated` rather
than reusing `certificate.replaced`/`certificate.uploaded` — `§5` below
listed only the create/replace/delete cases and didn't anticipate a
metadata-only edit. `Certificate.category` (`pill-system-design.md`'s
schema addition, §2 there) landed in the same migration as `document`, as
this doc recommended — the rest of that doc (status pill, validity icons,
nav badges) remains design-only.

## Why this doc exists

`pill-system-design.md` designed `Certificate.category` and per-category
validity icons — but rendered *from* whatever certificates a person already
has. At that point `Certificate` was still, in its own docstring, "metadata
only — no file storage." There was nothing to actually upload. This doc
designs that missing piece: HR staff (recruiter, coordinator, manager)
attaching a real document — a forklift/crane/welding licence, scanned or
photographed — to a worker.

The payoff of doing the previous two docs first: this feature doesn't need
to design *any* new display logic. The worker-list icon row and the
person-detail avatar already read live from `person.certificates` at render
time (per `pill-system-design.md`). Once this feature creates a real
`Certificate` row with a `category`, dates, and a `document`, the next page
render already shows the right icon with the right validity tint — "their
information should update and reflect that too on their worker page" is
satisfied by ordinary server-rendering, not by any special live-update
mechanism.

**No certificate CRUD exists at all today.** `features/compliance/` has
exactly one view (`compliance_list`, read-only alerts) — no `forms.py`, no
create/edit/delete URLs. This is greenfield.

## 1. Data model

Add to `Certificate` (`features/compliance/models.py`) — in the same
migration as `pill-system-design.md`'s `category` field if that hasn't
landed yet, since the upload form needs a category selector anyway:

- `document = models.FileField(upload_to=..., blank=True, null=True)`
- Existing `name` / `issue_date` / `expiry_date` / `category` unchanged.

`upload_to` generates `certificates/{uuid4}.{ext}` — same collision/
enumeration/cache-busting reasoning as the avatar doc's
`avatars/{model}/{uuid4}.{ext}`.

This reuses the avatar doc's storage decision wholesale: local filesystem +
Dokku persistent volume, same `MEDIA_ROOT`, just a different subdirectory of
the same volume — not a new storage mechanism, not a second infrastructure
decision.

No `uploaded_by` field is added — who uploaded, replaced, or deleted a
document is captured by the audit event (§5), not denormalized onto the
model.

**Multiple rows per category are allowed.** This matches how `Certificate`
already works (free-standing rows per person, ordered by `expiry_date`) — a
worker can have an expired forklift licence and its renewal as two separate
rows, keeping renewal history. When more than one row shares a category,
the icon shown for that category (per `pill-system-design.md`) uses
whichever row is most relevant: the soonest-expiring non-expired row if one
exists, else the most severe (most-expired) row if none are currently
valid.

## 2. Upload validation

Unlike an avatar photo, a certificate document must stay **legible**, and
must support **both image and PDF** sources — a phone photo of a physical
licence card, or a PDF export from an issuing authority, are both realistic.

- **Images** (JPEG/PNG/WebP): reuse the avatar doc's Pillow validation —
  decode-and-verify it's a genuine image, reject SVG outright
  (script-injection risk), strip EXIF (phone photos carry GPS tags) — but
  **do not center-crop to square**. Only cap maximum dimensions and
  file size, and re-encode to strip metadata, preserving the original
  aspect ratio so the document stays readable.
- **PDFs**: no new dependency needed — `pypdf` is already pinned
  (`requirements/runtime.lock`, v6.14.2) and already used elsewhere in the
  codebase (`features/payslips/services.py`, to *generate* encrypted
  payslip PDFs on the fly, never persisted). For an *uploaded* PDF, the
  equivalent of Pillow's `Image.verify()` is instantiating
  `pypdf.PdfReader` on the uploaded bytes and touching `.pages` — this
  raises (`PdfReadError`/`EmptyFileError`/similar) on malformed or
  disguised-non-PDF input, which is enough to reject garbage uploads.
- Reject anything that isn't JPEG/PNG/WebP/PDF (no executables, no SVG, no
  Office documents).
- Size cap higher than avatar photos — e.g. ~10MB — since scanned
  documents run larger than a profile photo.
- This feature is the one that actually *adds* the Pillow dependency if it
  ships before the avatar feature does (or vice versa) — either way, it's
  one shared AGENTS.md §3.1 ADR, not two separate approvals for the same
  package.

## 3. RBAC

New `Action.CERTIFICATE_MANAGE = "certificate.manage"`
(`core/accounts/permissions.py`), covering create, replace-document, and
delete in one action — matching the project's existing coarse-grained
action style (e.g. `EQUIPMENT_ISSUE_RETURN` covers both issue and return in
one action, rather than splitting per verb).

**Role-only grant, no per-project scoping**: `{RECRUITER, COORDINATOR,
MANAGER}` in both `clients/jober/policies.py` and
`clients/corvinum_eu/policies.py`. This mirrors two existing actions
already granted to exactly this trio in both clients —
`Action.INTAKE_ASSIGN_TRIAL` and `Action.PERSON_RECYCLE_AVAILABLE` — neither
of which restricts by project despite including coordinators, so this stays
consistent with precedent rather than introducing the first object-scoped
action in the codebase. (This is a deliberately different grant from
`Action.INTAKE_CREATE_EDIT`, which excludes coordinators in both clients —
certificate management is intentionally broader than general person-record
editing.)

Per `CLAUDE.md`'s RBAC convention, the new action must land in the same
commit as:
- `core/accounts/permissions.py` (`Action` enum member)
- `clients/jober/policies.py` and `clients/corvinum_eu/policies.py`
  (`ACTION_ROLES` grants)
- `docs/permissions/jober-permission-matrix.md` and
  `docs/permissions/corvinum-permission-matrix.md` (both explicitly state
  "when you change one, change the other in the same commit")

Read access (seeing a person's existing certificates) stays as broad as
today's `compliance_list` — no action gate on reading, consistent with the
broad-internal-read default (ADR 0008).

## 4. Views, forms, and where this surfaces

- New `features/compliance/forms.py`: `CertificateForm` (category, name,
  issue_date, expiry_date, document).
- New views in `features/compliance/views.py`, each
  `@require_action(Action.CERTIFICATE_MANAGE)`: create, edit (replace the
  document and/or update dates), delete. Mounted in `config/urls.py` under
  the same `_feature_on("compliance", "documents")` gate that
  `compliance_list` already uses.
- Surfaced as a new **person-detail panel**, registered with
  `register_person_panel` in `features/compliance/apps.py` (alongside the
  app's existing `register_report_tile` and alert-provider registrations)
  — using the `person_panels` slot that
  `templates/pages/person_detail.html` and
  `core/people/views.py::person_detail` already wire up (ADR 0021 Stage B),
  rather than hand-editing the template. The panel lists the person's
  certificates (category icon, name, dates, validity) and an "Add
  certificate" action, gated by `Action.CERTIFICATE_MANAGE` in the panel
  template itself — hidden buttons still need the server-side check.
- Standard POST → redirect → GET, using the existing flash-message pattern
  (`{% if messages %}` in `templates/layouts/base.html`) — no htmx
  required. Because both the worker-list icon row and the person-detail
  avatar read `person.certificates` fresh on every render, a normal page
  reload after upload already shows the new document's icon and updated
  detail-page section.

## 5. Audit

Every mutation is audited via `core.audit.services.record_event` (the
avatar doc previously cited a stale `apps.audit.services` path — corrected
there too):

- `record_event(request.user, "certificate.uploaded", target=certificate, person=person.pk, category=..., name=...)` on create
- `"certificate.replaced"` on document swap
- `"certificate.deleted"` on delete

## Open items for the implementation slice

- Land the Pillow ADR (§3.1) once, shared with the avatar feature if both
  are implemented around the same time — don't duplicate the approval.
- Confirm the exact PDF/image size cap and max dimensions with whoever
  owns the Dokku volume's disk budget, since certificate documents will
  accumulate faster than avatar photos (multiple rows per person, kept for
  renewal history per §1).
- File cleanup on person erasure/anonymization is **not yet possible** —
  neither `recycle_to_available()` nor `Person.archive()` deletes
  anything today. This is a shared open item with the avatar doc: a future
  real erasure feature needs to delete both avatar and certificate files
  explicitly, not assume an existing hook does it.
