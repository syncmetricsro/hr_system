# Fictional manual-upload fixtures

This directory is intentionally tracked so a fresh repository checkout can
repeat the Jober and CorvinumEU avatar/certificate acceptance checks. Every
person, issuer, identifier, and country shown here is invented. The assets are
for local or fictional staging use only and must never be copied into a
real-data environment.

Verify the files before using them:

```bash
sha256sum --check tests/fixtures/manual_uploads/SHA256SUMS
```

## Avatars

Use files under `avatars/` with the shared
[avatar acceptance runbook](../../../docs/deployment/avatar-upload-acceptance.md).

| File | Input case | Expected result |
|---|---|---|
| `01-olha-square-with-test-exif.jpg` | Square JPEG with harmless test EXIF | Accepted; EXIF removed; 512×512 WebP stored |
| `02-farrukh-landscape.jpg` | Landscape JPEG | Accepted; centered square crop; 512×512 WebP stored |
| `03-anh-portrait.webp` | Portrait WebP | Accepted; centered square crop; 512×512 WebP stored |
| `04-marek-square.png` | Large square PNG | Accepted; resized and stored as WebP |
| `05-eszter-square.png` | Large square PNG with fine edges | Accepted; resized and stored as WebP |
| `reject/reject-not-an-image.jpg` | Plain text with a JPEG extension | Rejected as an invalid image |
| `reject/reject-vector.svg` | Harmless SVG | Rejected; avatars allow JPEG, PNG, or WebP only |

The two large PNGs also cross nginx's former 1 MB default, so they are useful
for confirming a Dokku app has the required 25 MB request ceiling. They remain
below Django's 5 MB per-avatar limit.

## Certificates

Use files under `certificates/` with the shared
[certificate acceptance runbook](../../../docs/deployment/certificate-upload-acceptance.md).

| Files | Manual case | Expected result |
|---|---|---|
| `allowed-forklift-front.png` + `allowed-forklift-back.png` | Forklift front/back card | Accepted |
| `allowed-crane-certificate.pdf` | Crane PDF as the only file | Accepted |
| `allowed-welding-certificate.png` | Welding paper scan | Accepted |
| `prohibited-birth-certificate.pdf` | Internal boundary/mislabel fixture | No ordinary Birth category exists; see runbook |
| `prohibited-national-id-front-back.pdf` | Internal boundary/mislabel fixture | No ordinary Identity category exists; see runbook |
| `prohibited-medical-fitness-certificate.png` | Internal boundary/mislabel fixture | No ordinary Medical/Health category exists; see runbook |

The last three files are deliberately unmistakable fictional specimens. Do
not use them during a client presentation. A deliberate mislabel probe tests a
known limitation—manual category validation is not OCR—and must be followed
immediately by the manager-only permanent file purge described in the runbook.

## What was intentionally omitted

The working generation directories, original source renders, processed
previews, contact sheets, duplicate PNG/PDF forms, and ZIP archives remain
gitignored under `test-artifacts/`. Git contains only the inputs needed to
repeat the manual acceptance matrix. Automated tests continue to construct
their own minimal files in memory and do not depend on this directory.

See `PROVENANCE.md` for origin and safety markings. Do not remove the visible
`FICTIONAL TEST ...` or `NOT VALID` markings from any document fixture.
