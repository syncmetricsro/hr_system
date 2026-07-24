# ADR 0028: fpdf2 for the downloadable feedback flyer (Cyrillic-capable PDF text)

Status: **Accepted — 2026-07-24.** Approved and added to
`requirements/runtime.in`/`requirements/test.in`; hash-pinned locks
regenerated via `scripts/write_requirements_lock.py`.

Date drafted: 2026-07-24

## Context

`docs/product/feedback-flyer-design.md` designs a downloadable, printable
PDF combining a feedback link's QR code and label text, for staff to print
and post. The design's first pass found this achievable with **no new
dependency** — extending `features/payslips/services.py::_simple_pdf()`'s
existing hand-written-PDF technique (manual `%PDF-1.4` object/xref/trailer
construction, `re f` vector-rectangle fills for QR modules) — but flagged a
real, explicit limitation: PDF's 14 standard base fonts (`WinAnsiEncoding`)
cover Slovak/Hungarian accented Latin characters but have **no Cyrillic
glyphs at all**, regardless of what string is passed in. A Ukrainian-
language flyer label is not achievable that way.

Presented with this tradeoff, the user chose **embed a real Cyrillic-
capable font now** over shipping Latin-script-only text. Properly embedding
a TrueType font as a PDF composite (CIDFontType2) font — `FontFile2`
embedding, glyph-ID mapping, subsetting, a `ToUnicode` CMap — is one of the
more error-prone corners of the PDF specification; hand-rolling it
correctly (matching `_simple_pdf()`'s stdlib-only, no-drawing-library
approach) risks producing malformed PDFs that fail to open or print for end
users, for a document specifically meant to be printed and posted publicly.
That is a poor tradeoff against adopting a small, mature, well-tested
library that already does this correctly.

## Decision

Adopt **fpdf2 2.8.7** (current stable as of this ADR, released
2026-02-28 — well clear of the AGENTS.md §3 ~3-day cooldown window) as a
new runtime dependency, plus its two required runtime dependencies not
already present: **fonttools 4.63.0** (released 2026-05-14) and
**defusedxml 0.7.1** (released 2021-03-08, long-stable). fpdf2's third
required dependency, Pillow, is already pinned at 12.3.0 (ADR 0027),
satisfying fpdf2's `Pillow!=9.2.*,>=8.3.2` constraint with no version
change.

Alongside the code dependency, vendor a **DejaVu Sans 2.37** TrueType font
pair (Regular + Bold) — `vendor/fonts/DejaVuSans.ttf`,
`vendor/fonts/DejaVuSans-Bold.ttf` — for fpdf2 to embed. DejaVu Sans has
broad Unicode coverage including Cyrillic, Slovak/Hungarian Latin
diacritics, and Greek; it's the de facto standard "just works" open Unicode
font (bundled by TeX Live, matplotlib, and most Linux distributions) and
hasn't changed since 2016 (version 2.37), which for a vendored, hash-pinned
asset is a feature, not a staleness concern — no ongoing supply-chain
exposure from frequent releases.

## §3.1 approval-gate notes (new PyPI packages)

- **Why not stdlib/Django:** as established by `_simple_pdf()`'s own
  existence, Python's standard library has no PDF-generation capability at
  all. Composite/embedded-font PDF generation specifically (what a real
  Cyrillic font needs) is substantially more complex than the flat-text/
  vector-fill content `_simple_pdf()` already hand-rolls, to the point that
  hand-rolling it is the wrong engineering tradeoff for a document meant to
  be printed and relied on (see Context).
- **Why fpdf2 specifically:** actively maintained
  (`py-pdf/fpdf2` on GitHub), "Production/Stable" classifier, 1,300+ unit
  tests, 300+ contributors, Python 3.10+. It's the direct, actively-
  maintained successor to the old `pyfpdf`/`PyFPDF` project (which this
  codebase does not use). Its declared runtime dependencies are minimal and
  all pure-Python except Pillow (already present): `defusedxml` (XXE-
  hardened XML parsing, a small, narrowly-scoped, long-stable security-
  focused library), `fontTools` (the standard Python font-manipulation
  library — used by literally the rest of the Python font tooling
  ecosystem), and `Pillow>=8.3.2` (already pinned). `uharfbuzz` (text
  shaping) is a **test-only** dependency of fpdf2 upstream, not a runtime
  requirement — it is not being added here.
- **License:** fpdf2 itself is **LGPL-3.0-only**. Used here as an
  unmodified pip dependency (dynamic import, not statically linked/modified
  source), which is exactly the usage LGPL is designed to permit freely
  without imposing copyleft obligations on this codebase. `fontTools` is
  MIT; `defusedxml` is PSF-2.0-or-later.
- **Cooldown:** fpdf2 2.8.7 published 2026-02-28 (≈5 months clear);
  fonttools 4.63.0 published 2026-05-14 (≈2 months clear); defusedxml 0.7.1
  published 2021 (long-stable). All well past the ~3-day cooldown rule.
- **Build-time impact:** all three install from prebuilt/pure-Python
  wheels — `fonttools` ships a `manylinux` wheel, `fpdf2`/`defusedxml` are
  `py3-none-any` — no C-extension compilation added to the Docker build.
- **Transitive drift check:** downloading against the existing pinned
  `.in` files and diffing the regenerated `.lock` files confirmed **zero**
  unrelated version drift this time (unlike Pillow's addition, which
  re-resolved `asgiref`/`typing_extensions`/`charset-normalizer` and needed
  explicit re-pinning per ADR 0027) — the lock diffs are purely additive
  (`defusedxml`, `fonttools`, `fpdf2` and nothing else changed).
- **Scope of use, deliberately narrow:** used only by
  `features/feedback/services.py`'s new flyer-generation function. Not used
  for payslips (`_simple_pdf()` stays as-is — no reason to migrate working,
  narrowly-scoped code) or anywhere else.

## Vendored font asset (AGENTS.md §3.2 discipline applied to a non-JS asset)

§3.2 names htmx/Alpine specifically, but the same discipline — local files
in the repo (never fetched at request time), pinned exact version, checked-
in SHA-256 manifest entries, source/version/license/date recorded — applies
to any vendored binary the running app depends on. The DejaVu font files
are needed at **request time** (fpdf2 loads them to generate each flyer),
unlike the Tailwind CLI (build-time only, deliberately *not* committed), so
they're committed like `htmx.min.js`/`chart.min.js` rather than fetched
fresh per build.

- Source: `https://sourceforge.net/projects/dejavu/files/dejavu/2.37/dejavu-fonts-ttf-2.37.tar.bz2`.
- Integrity: the downloaded archive's MD5 was checked against the value
  officially published on `dejavu-fonts.github.io/Download.html`
  (`d0efec10b9f110a32e9b8f796e21782c`) and matched exactly *before*
  extracting; the SHA-256 values recorded in `vendor/MANIFEST.md` and
  `scripts/verify_vendor_assets.py` were computed directly from the
  extracted files, not copied from any third party.
- License: Bitstream Vera Fonts Copyright + public domain (DejaVu's own
  changes) — `vendor/fonts/dejavu-LICENSE`, also vendored and hash-pinned.

## Consequences

- `requirements/runtime.in`/`test.in` gain `defusedxml==0.7.1`,
  `fonttools==4.63.0`, `fpdf2==2.8.7`; both `.lock` files regenerated,
  purely additive diffs. `jober-test:phase4` rebuilt from
  `Dockerfile.playwright-python` so the pinned test image actually has
  these importable.
- `vendor/fonts/{DejaVuSans.ttf,DejaVuSans-Bold.ttf,dejavu-LICENSE}` added,
  recorded in `vendor/MANIFEST.md`, verified by
  `scripts/verify_vendor_assets.py`.
- This unblocks `docs/product/feedback-flyer-design.md`'s flyer-generation
  step with genuine Cyrillic support, not a Latin-only stand-in.
- No other part of the codebase changes as a result of adding this
  dependency — payslip PDF generation (`_simple_pdf()`) is untouched.
