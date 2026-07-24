# ADR 0027: Pillow for avatar/certificate image upload validation

Status: **Accepted — 2026-07-24.** Approved and added to
`requirements/runtime.in`/`requirements/test.in`; hash-pinned locks
regenerated via `scripts/write_requirements_lock.py`.

Date drafted: 2026-07-24

## Context

`docs/product/avatar-design.md` designs worker/admin profile pictures:
users upload a photo, the server must verify it's a genuine image (not
just trust the file extension), strip EXIF metadata (phone photos carry
GPS tags — relevant once the real-data/legal gate opens), reject SVG
outright (script-injection risk), and re-encode to a normalized size/
format before storing. `docs/product/certificate-upload-design.md` needs
the identical image-validation step for photographed (not PDF) certificate
documents. Neither is achievable with the standard library — Python has
no built-in image codec, decoder, or resize capability.

## Decision

Adopt **Pillow 12.3.0** (current stable as of this ADR, released
2026-07-01 — well clear of the AGENTS.md §3 ~3-day cooldown window) as a
new runtime dependency.

## §3.1 approval-gate notes (new PyPI package)

- **Why not stdlib/Django:** Python's standard library has no image
  codec, decoder, or resize capability at all. Django itself has no
  built-in image-processing layer either (`ImageField` only stores a
  file path; validating/re-encoding pixel data needs an actual imaging
  library).
- **Maintainer/weight:** Pillow (PIL Fork) is the de facto standard
  Python imaging library — actively maintained
  (python-pillow/Pillow on GitHub), ships prebuilt wheels for all
  platforms this project targets, and has **no required transitive
  dependencies** for the operations this feature needs (decode/verify,
  EXIF strip, resize, re-encode to WebP). Optional codecs it can link
  against (e.g. for less common formats) aren't needed here and won't be
  installed.
- **Cooldown:** 12.3.0 was published 2026-07-01; this ADR is drafted
  2026-07-24 — 23 days clear of the ~3-day cooldown rule.
- **Build-time impact:** installed from a prebuilt wheel (`manylinux`),
  no C-extension compilation needed in the Docker build — consistent
  with how `psycopg-binary`/`cryptography` are already handled.
- **Scope of use, deliberately narrow:** this dependency is used only for
  server-side upload validation and re-encoding (verify → strip EXIF →
  center-crop/resize → save as WebP). It is not used for anything else in
  the codebase, and no other feature currently has a stated need for it.

## Consequences

- `requirements/runtime.in` and `requirements/test.in` gain
  `Pillow==12.3.0`; both `.lock` files were regenerated in the pinned
  Python image via `scripts/write_requirements_lock.py`. Adding Pillow
  re-resolved three unrelated transitive packages to newer point
  releases (`asgiref` 3.11.1→3.12.1, `typing_extensions` 4.15.0→4.16.0,
  and in `test.lock` only, `charset-normalizer` 3.4.7→3.4.9) — all three
  were pinned back to their previously-vetted versions in both `.in`
  files (matching the exact precedent ADR 0016 already set for
  WhiteNoise/certifi/greenlet), so the actual lock diff is Pillow-only in
  both files, and no cooldown-window release was pulled in incidentally.
- This unblocks both `docs/product/avatar-design.md` and
  `docs/product/certificate-upload-design.md`'s upload-validation steps,
  which were both explicitly blocked on this ADR.
- No other part of the codebase changes as a result of adding this
  dependency — it has zero interaction with existing features until the
  avatar/certificate-upload code that uses it is itself built.
