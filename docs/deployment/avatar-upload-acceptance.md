# Fictional avatar upload acceptance runbook

Use this check for Jober and CorvinumEU after an avatar/media release, after
creating a new Dokku app, or before demonstrating worker photos. It is a
fictional-data local/staging check only. Never use a real worker photo while
the real-data gate remains closed.

## Tracked fixture pack

A fresh repository checkout contains the curated fixtures at:

```text
tests/fixtures/manual_uploads/avatars/
```

Verify them from the repository root before use:

```bash
sha256sum --check tests/fixtures/manual_uploads/SHA256SUMS
```

The pack contains square JPEG/PNG, landscape JPEG, portrait WebP, harmless
test EXIF, two files larger than nginx's former 1 MB default, and invalid
JPEG/SVG rejection cases. Every portrait is synthetic and has no real-person
reference. See the pack's `README.md` and `PROVENANCE.md`.

## Dokku prerequisite

The active nginx configuration must show `client_max_body_size 25m;`:

```bash
APP=<app>                         # jober-staging | corvinum-staging
sudo dokku nginx:show-config "$APP" | grep client_max_body_size
```

If it does not, follow
[`syncmetric-prime-staging.md`](syncmetric-prime-staging.md#required-upload-request-ceiling).
A raw nginx 413 page means the request did not reach Django. The application
still enforces its own 5 MB per-avatar limit.

## Positive UI matrix

Use fictional people in the signed-in user's office scope. Do not overwrite a
presenter-critical avatar without agreeing on the cleanup first.

1. Upload `01-olha-square-with-test-exif.jpg`. Confirm it appears in person
   detail, the People list, and the bottom-right quick-access worker panel.
2. Upload `02-farrukh-landscape.jpg`. Confirm the center crop keeps the face
   and both list/detail circles render without stretching.
3. Upload `03-anh-portrait.webp`. Confirm the centered portrait crop remains
   useful and persists after a reload.
4. Upload `04-marek-square.png` and `05-eszter-square.png` to separate
   fictional people or as deliberate replacements. These cross the old nginx
   1 MB limit and must now reach Django and succeed.
5. Upload `06-mira-novakova-square.png` only to fictional Mira Novakova. It is
   an entirely synthetic, age-appropriate portrait for her under-18 test row;
   confirm the avatar changes without altering or hiding the under-18 warning.
6. Replace one existing avatar. Confirm the new UUID file is used, the old
   image no longer renders, and Audit shows `Avatar replaced` rather than a
   second independent add.
7. Remove one test avatar. Confirm the worker default returns in all consumers
   and Audit records the removal.
8. Repeat one representative upload under the other client's settings. Jober
   and CorvinumEU share the processor, but this verifies the client UI and
   deployment configuration too.

For a staff-account avatar, use the self-service header control and confirm the
navbar changes. Worker avatars use the person record and are gated by the same
office scope and edit permission as the worker.

## Negative UI checks

1. Upload `reject/reject-not-an-image.jpg`. Expected: a friendly invalid-image
   error; no avatar or file is created.
2. Upload `reject/reject-vector.svg`. Expected: rejected because only JPEG,
   PNG, and WebP are allowed.
3. Verify an unauthorized role cannot mutate another worker's avatar. A hidden
   button is not sufficient; the server must refuse the request.

The automated suite covers the 5 MB boundary, excessive dimensions,
decompression-bomb handling, removal/replacement cleanup, authorization, and
audit sequencing. Do not manufacture oversized or decompression-bomb payloads
against shared staging.

## Stored-file check

The persistent media volume must retain only processed UUID-named WebPs, never
the browser's JPEG/PNG/WebP source. Run this read-only check on the VPS:

```bash
APP=<app>
sudo dokku run "$APP" python -c '
from pathlib import Path
from PIL import Image

root = Path("/app/media/avatars")
files = sorted(path for path in root.rglob("*") if path.is_file())
print("files", len(files), "bytes", sum(path.stat().st_size for path in files))
for path in files:
    with Image.open(path) as image:
        print(
            path.relative_to(root),
            path.stat().st_size,
            image.format,
            image.size,
            "exif", len(image.getexif()),
        )
'
```

Expected for every uploaded avatar:

- path under `avatars/person/` or `avatars/user/` with a UUID `.webp` name;
- decoded format `WEBP`;
- dimensions `512×512` or smaller when the source itself was smaller;
- zero EXIF entries;
- substantially smaller stored bytes for large photographic sources.

For the 2026-08-01 Jober pass, four large fictional source PNGs totalled
7,770,049 bytes and their four stored 512×512 WebPs totalled 77,042 bytes—a
99.008% reduction, about 101× smaller. All four stored paths matched database
references and no avatar orphan remained.

## Cleanup and evidence

- Keep only avatars useful to the shared fictional demo; remove temporary
  replacements through the UI so the action is audited.
- Record client, environment, fixture filename, source format/shape, UI
  consumers checked, pass/fail, cleanup, and the relevant audit event.
- Do not commit screenshots containing credentials or non-fictional data.
- Uploaded media is private application data, not a static Git asset. It must
  be included in encrypted off-site backups before the real-data gate opens.
