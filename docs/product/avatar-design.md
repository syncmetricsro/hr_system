# Avatars — workers and admin roles

Status: **Fully implemented 2026-07-25**, including §1's illustrated
per-role default art (delivered 2026-07-25 via the user's own image
generation, followed by chroma-key removal and exact flat-color
normalization — verified pixel-for-pixel against the §1 palette before
integration: 1024×1024 RGBA, true alpha transparency outside the circle,
circle fill and silhouette fill both exact hex matches, no gradient/noise).
Delivered as PNG, processed (resized to 256×256, re-encoded WebP) and
shipped at `static/avatars/default_{role}.webp` — **not**
`core/static/core/avatars/` as this doc originally specified, which was
never actually checked against `STATICFILES_DIRS` (`config/settings/
base.py`, which only scans the top-level `static/` dir and each client's
own `static/` dir) and would have silently 404'd in production; caught
before shipping by adding a test that calls Django's real
`staticfiles.finders.find()` instead of only checking that `{% static %}`
produces a URL string (`{% static %}` doesn't verify the file exists).
The Dockerfile also needed its own new `COPY static/avatars
/app/static/avatars` line — it copies `static/` subdirectories
individually, not the whole tree, the same class of gap the DejaVu font
vendoring hit earlier this session. `core/ui/templatetags/avatars.py`'s
placeholder branch is gone entirely; the no-photo case now always renders
an `<img>` pointing at the role-appropriate default (Person → worker;
User → their own role), same as an uploaded photo. Everything else was
already built as designed: Pillow (ADR 0027), local filesystem storage,
`Person.avatar`/`User.avatar`, upload validation, RBAC, and the navbar/
worker-list/person-detail template surface, for both Jober and CorvinumEU.
The repeatable fictional UI, rejection, proxy, and stored-file verification is
maintained in
[`../deployment/avatar-upload-acceptance.md`](../deployment/avatar-upload-acceptance.md).

## Why this doc exists

The app has never had a photo/avatar concept, and that's not an accident —
it's a repeated, deliberate pattern elsewhere in the codebase:

- `Certificate` (`features/compliance/models.py`) originally held dates only.
  Since 2026-07-31 it accepts files for the server-enforced forklift/crane/
  welding allowlist; high-risk document scans remain excluded by
  `document-storage-boundary.md`.
- 2FA setup (`core/accounts/totp.py`) shows a raw `otpauth://` URI instead of
  rendering a QR image — "QR rendering is intentionally absent (an image
  library would need a vendored asset + ADR)."
- Disability info (`core/people/models.py`) is "flag only, no documents."

Adding avatars for workers (`Person`) and the four admin roles (`User.role`:
recruiter, coordinator, manager, observer) means introducing genuinely new
infrastructure — image storage, an image-processing dependency, upload
validation, and new template surface — into a codebase that treats exactly
this kind of addition as needing an ADR (AGENTS.md §3.1). This doc is that
up-front design work.

## 1. Default avatar — generation brief

Five illustrated raster variants — one per admin role plus one for workers —
sharing a single style and differing only by background accent color (and
optionally a small role badge). Style: flat, minimalist, Slack/Teams-style
generic profile art. A gender/ethnicity-neutral head-and-shoulders silhouette
bust, centered in a solid-color circle, no gradients, no outlines, no
text/logos, no photorealistic detail. Square canvas so it crops cleanly to a
circle in CSS regardless of where it's displayed.

**Prompt** (fill in `{ROLE_COLOR}` per row of the palette table below):

> Flat vector illustration, minimalist corporate profile-picture icon. A
> generic, gender-neutral, featureless head-and-shoulders silhouette bust,
> centered inside a perfect circle that fills most of the frame. Circle
> background is a solid flat color `{ROLE_COLOR}`; the silhouette itself is a
> soft off-white (#F5F5F0), flat-shaded with no gradients, no outlines, no
> text, no logos, no watermark, no specific ethnicity or gender markers, no
> photorealistic detail. Clean modern SaaS/HR-software aesthetic, similar in
> spirit to Slack or Microsoft Teams default avatar icons. Square 1:1 canvas,
> generous margin around the circle for safe cropping, no drop shadow outside
> the circle. High resolution, 1024×1024px, PNG, transparent outside the
> circle.

Starting palette (placeholder hex values — adjustable once the first render
comes back; not final brand tokens):

| Role | Accent color |
|---|---|
| Worker | `#4A6FA5` (slate blue) |
| Recruiter | `#2F9E8F` (teal) |
| Coordinator | `#C9922B` (amber) |
| Manager | `#6B4E9E` (indigo) |
| Observer | `#6B7280` (graphite) |

Deliver at 1024×1024; implementation downscales/re-encodes to a 256×256 WebP
for actual serving (see §2). Defaults are **shared across both clients**
(not per-client themed) — role color-coding is more useful at a glance than
brand color-coding for a placeholder, and a real uploaded photo personalizes
each record anyway once one exists. The five files ship as static assets
bundled with the app (not user uploads), at
`core/static/core/avatars/default_{role}.webp` — e.g. `default_worker.webp`,
`default_recruiter.webp`, `default_coordinator.webp`,
`default_manager.webp`, `default_observer.webp`.

Review step: the user reviews the AI-generated (or hand-designed) renders
against this brief before they're integrated; this doc doesn't presuppose
the render will be accepted as-is.

## 2. Storage & serving

**Decision: Django `ImageField` → local filesystem → a Dokku persistent
volume**, served by a permission-checked Django view — not an object store,
not the database, and (as of 2026-07-26) **not** a direct nginx alias; see
the serving bullet below for why that was reversed.

- New settings: `MEDIA_ROOT` / `MEDIA_URL = "/media/"` in
  `config/settings/base.py`. Neither exists today — `STORAGES["default"]`
  is currently a declared-but-unused `FileSystemStorage` with no
  `MEDIA_ROOT` backing it. Production settings point `MEDIA_ROOT` at the
  Dokku-mounted path.
- Deploy step (new): `dokku storage:mount <app>
  /var/lib/dokku/data/storage/<app>-media:/app/media`. This is new
  infrastructure not covered anywhere in
  `docs/deployment/deployment-plan.md` today (that plan only reaches
  Postgres via `dokku postgres:link` and TLS via `dokku letsencrypt` — no
  volumes). The eventual implementation slice should add this as an
  explicit deployment step, and the mounted directory needs to ride along
  in whichever off-site backup target answers open question D6 (currently
  scoped to DB backups only).
- ~~Serving: a per-app `nginx.conf.d` snippet aliasing `/media/` straight to
  the host-mounted directory, so reads never hit the Django process.~~
  **Superseded 2026-07-26 — do not do this.** A bare alias serves every file
  to anyone holding its URL, and a UUID filename is obscurity, not
  authorization. It would have exposed certificate *scans*, which is why
  production-readiness item 3 flagged it before it was built.
  **What shipped instead:** `/media/` has no route in any environment, and
  each file is delivered by a view in `core/media_views.py` that re-runs the
  page's own checks — the office boundary for avatars, and the office
  boundary plus `can_view_sensitive` for certificate documents. The DEBUG-only
  `django.views.static.serve` alias was removed too: it meant local
  development bypassed every check while production served nothing, so a
  bypass was one settings flag away and invisible locally.
  If per-request cost ever matters, the upgrade path is `X-Accel-Redirect`
  via a Dokku `nginx-includes` file — nginx sends the bytes, Django still
  authorizes. **WhiteNoise remains not viable** either way: per ADR 0016 it
  snapshots its static directory into an immutable manifest at process start,
  so files uploaded after boot would not be found without a restart.
- New dependency: **Pillow**, to validate uploads are genuine images, strip
  EXIF, center-crop, resize, and re-encode. This needs the AGENTS.md §3.1
  approval-gate treatment before it's added — modeled on ADR 0016's
  structure:
  - *Why not stdlib:* Python's standard library has no image codec/resize
    support.
  - *Maintainer/weight:* Pillow is the de facto standard Python imaging
    library, actively maintained, ships prebuilt wheels, no required
    transitive dependencies.
  - *Cooldown:* confirm the pinned version wasn't published in the last
    ~3 days before locking it (AGENTS.md §3 cooldown rule).
- Migration path: `STORAGES["default"]` is already Django's storage
  abstraction point, so moving to S3-compatible object storage later (if
  multi-server or CDN needs arise) is a `django-storages` + `boto3` swap
  with **no model or view code changes** — this decision isn't a dead end,
  just the right starting point for a single-VPS-per-client deployment.

**Explicitly rejected:**
- **Postgres `bytea` column.** The instinct that Postgres alone isn't
  enough was right: storing binary images in the DB bloats `pg_dump`/WAL,
  has no CDN/etag/caching story, and Django has no first-class pattern for
  serving images out of a DB column efficiently.
- **Gravatar / external avatar-by-email-hash service.** A runtime call to a
  third-party host keyed by email hash is at odds with the project's
  privacy posture (fictional-data-only gate today, HMAC-based blacklist
  matching, no real PII yet) and wouldn't allow company-controlled photos
  anyway.

## 3. Data model & upload handling

- Add `avatar = models.ImageField(upload_to=..., blank=True, null=True)` to
  both `Person` (`core/people/models.py`) and `User`
  (`core/accounts/models.py`).
- `upload_to` generates `avatars/{model}/{uuid4}.{ext}` — UUID filenames
  avoid path collisions/enumeration and bust browser cache automatically on
  replace.
- Server-side validation on upload (Pillow):
  - Decode-and-verify the file is actually an image, not just extension
    sniffing.
  - Allow-list JPEG/PNG/WebP only; **reject SVG outright** (script-injection
    risk if ever inline-rendered).
  - Cap input dimensions/file size to guard against decompression-bomb
    abuse.
  - Re-encode on save: strip EXIF (phone photos carry GPS tags — this
    matters once the real-data/legal gate opens), center-crop to square,
    resize to a max stored dimension of 512×512, save as WebP.
- Every avatar add/replace/remove is audited via
  `core.audit.services.record_event`, matching how other `Person`/`User`
  mutations are recorded.
- Recycling/erasure: `core/people/services.py::recycle_to_available()`
  only flips `lifecycle_status` back to `AVAILABLE` and clears the
  inactive reason — it does not anonymize or delete anything, and neither
  does `Person.archive()` (a soft `is_archived` flag). There is **no
  existing hard-delete/anonymization hook for `Person` today**, so there's
  nothing to "hook into" yet. This is an open item, not a solved one: when
  a real erasure/anonymization feature is eventually built, it will need
  to explicitly delete the avatar file from disk (not just null the
  field), so no orphaned PII-bearing file survives it. The same open item
  applies to certificate documents — see
  `docs/product/certificate-upload-design.md`.

## 4. RBAC

- **Own avatar (`User`).** Self-service, no new `Action` — the same trust
  boundary as changing your own password. The guard is
  `request.user.pk == target.pk` (or superuser), not a role check.
- **Worker avatar (`Person`).** Staff-uploaded from the person detail page —
  `Person` has no login of its own, so there's no worker self-service path
  to design for. Reuse the existing `Action.INTAKE_CREATE_EDIT`
  (`core/accounts/permissions.py`), which already gates `person_create` and
  `person_edit` (`core/people/views.py`), rather than adding a new
  fine-grained action for a single field.

## 5. Where avatars show up

A single template tag centralizes the fallback rule so every template that
shows an avatar stays consistent: `core/templatetags/avatars.py`, e.g.
`{% avatar person_or_user size="sm" %}`, resolving **uploaded photo → else
the role-appropriate default static asset**, rendered as an `<img>` inside a
fixed circular container (`.avatar avatar--sm/md/lg` CSS classes).

**Phase 1 — ships with this feature:**
1. **Navbar** (`templates/layouts/base.html`, `.header-account` div) — the
   signed-in user's own avatar (~32px) next to
   `{{ user.get_role_display }}`, before the language/theme controls.
   Today that area shows only the role label — no avatar, name, or photo at
   all.
2. **Worker list** (`templates/pages/people_list.html`) — each `.person-row`
   card changes from a text-only name/status block to a flex row with a
   leading avatar thumbnail (~40px) before the text.
3. **Person detail header** (`templates/pages/person_detail.html`) — a
   larger avatar (~96px) beside the person's name/header info.

**Phase 2 — explicitly deferred, not part of the first build slice:**
- Attribution avatars anywhere else a person/user's name appears as an
  actor — audit trail entries, feedback/messaging thread authorship,
  "owning recruiter" badges on person detail, compliance reviewer names.
  Deferred because it touches many more templates than the core feature
  needs in order to be useful.
- Multiple stored thumbnail sizes, if a single 512px master + CSS
  `object-fit: cover` proves insufficient at scale.

## Remaining open items (post-implementation)

- ~~Finalize and approve the Pillow ADR~~ — done, `docs/adr/0027-pillow-
  avatar-images.md`, Accepted 2026-07-24.
- Add the Dokku storage-mount step (**not** an nginx `/media/` alias — see §2) to
  `docs/deployment/deployment-plan.md` (and the per-client staging docs)
  before first production deploy with avatars enabled — `MEDIA_ROOT` is
  already env-overridable in both `config/settings/production.py` and
  `clients/corvinum_eu/production.py` for when that mount exists, but the
  actual Dokku/nginx configuration is a deployment-time step, not code.
- ~~Confirm final default-avatar art and land the five illustrated static
  assets~~ — done 2026-07-25, `static/avatars/default_{role}.webp`.
- Decide whether the off-site backup target answering D6 also covers the
  media volume, or whether avatars get a separate backup story.
