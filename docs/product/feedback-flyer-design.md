# Feedback link — downloadable PDF flyer with QR code

Status: **Implemented 2026-07-24**, with one deliberate change from this
doc's original plan: the Cyrillic-text open question (below) was resolved
by the user in favor of **real font embedding**, not the Latin-only
fallback this doc initially recommended as the default path. That meant
adopting a new dependency (`fpdf2`, ADR 0028) plus a vendored DejaVu Sans
font pair, rather than extending `_simple_pdf()`'s hand-written, no-
dependency approach — the hand-rolled composite-font PDF structure a
Cyrillic base-14-font workaround would have needed (`FontFile2` embedding,
GID mapping, `ToUnicode` CMaps) was judged too error-prone to write by
hand for a document meant to be printed and relied on. See ADR 0028 for the
full tradeoff writeup. Everything else below matches the original design:
`core/ui/qr.py::qr_pdf()` walks the same segno matrix `qr_svg()` already
uses, the gated view/route/button are exactly as planned, and the flyer's
own on-page filename uses the link's `token` (not a possibly-unsafe raw
`label` string) for the `Content-Disposition` filename.

## Why this doc exists

Feedback links (`features/feedback/models.py::FeedbackLink`) already
render an on-screen QR code in the inbox
(`templates/pages/feedback_inbox.html:16-23`, via `core.ui.qr.qr_svg()`),
added 2026-07-23 per `BUILD_JOURNAL.md`. What's missing: a downloadable,
printable version — a one-page PDF combining the QR code and the link
text that staff can print and post somewhere workers will see it (a
break-room wall, a noticeboard), rather than only ever viewing the QR on
a screen.

## The key finding: this needs no new dependency

`core/ui/qr.py::qr_svg()` wraps `segno.make(data, error="m")` and only
ever calls `.svg_inline(...)` — SVG is the only output path used today.
But `segno` (already pinned, `requirements/runtime.lock`) exposes the raw
QR module matrix directly (`.matrix_iter()`/`.matrix`), which can be
walked to emit **PDF vector-rectangle fill operators** (`re f` — "define
rectangle, fill") for each dark module, straight into a hand-written PDF
content stream. That's the exact technique
`features/payslips/services.py::_simple_pdf()` already uses to build a
minimal PDF from scratch (stdlib-only: manual `%PDF-1.4` object/xref/
trailer construction, no drawing library) — this feature extends that
same pattern rather than introducing a second PDF-generation approach.

`pypdf` (also already pinned) isn't needed for the drawing itself — it
has no image/canvas API, which is exactly why the payslip code only uses
it for `PdfWriter.encrypt(...)`, never for content. A QR flyer has no
comparable need for encryption, so this feature may not need `pypdf` at
all — plain `_simple_pdf()`-style generation is enough.

## Design

### 1. `core/ui/qr.py` — new `qr_pdf()` helper

Alongside the existing `qr_svg(data, *, scale=4)`, add
`qr_pdf(data: str, *, label: str = "") -> bytes`:
- Get the QR matrix from the same `segno.make(data, error="m")` call
  already used for `qr_svg`.
- Emit one `re f` fill-rectangle operator per dark module into a PDF
  content stream (module size scaled to fit a reasonable printed QR size
  on an A4 page — large enough to scan from a few steps away, e.g.
  ~8×8cm).
- Optionally draw `label` and the raw URL as text below the QR using the
  same `BT ... Tj ... ET` text-stream pattern `_simple_pdf()` already
  uses.
- Assemble the full PDF (object table, xref, trailer) following
  `_simple_pdf()`'s exact structure — this could even become a small
  shared helper both payslips and this feature call, if a future refactor
  wants that; not required for this design.

### 2. New gated view

A new view (e.g. `feedback_link_pdf(request, pk)`), gated the same way
existing feedback views are — `@require_action(Action.FEEDBACK_VIEW)`,
matching `feedback_inbox`/`feedback_link_create`
(`features/feedback/views.py:39,57`). Returns
`HttpResponse(content_type="application/pdf")` with
`Content-Disposition: attachment; filename="feedback-<label>.pdf"`,
mirroring the attachment-header convention already established in
`core/ui/exports.py::csv_response()`.

### 3. UI

A "Download PDF" button next to each link's existing on-screen QR in
`templates/pages/feedback_inbox.html`, using this session's `{% icon
"export" %}` tag.

## Real constraint to flag, not gloss over: no Cyrillic support

PDF's 14 standard base fonts (used via `WinAnsiEncoding` in a
hand-written PDF like `_simple_pdf()`) cover Slovak and Hungarian
accented Latin characters, but **not Cyrillic**. A Ukrainian-language
flyer (label text, any instructions printed on it) is **not achievable**
with this dependency-free approach — `WinAnsiEncoding` simply has no
Cyrillic glyphs to reference, regardless of what string is passed in.

Two real options, to decide before implementation:
- **Ship flyer text in English/Latin script only** (the QR itself is
  language-agnostic — it just encodes a URL). Simplest, no new
  dependency, but means Ukrainian-speaking workers see an English label
  on the printed flyer, even though the form they scan into is fully
  translated.
- **Embed a real font resource** (e.g. a subsetted TTF with Cyrillic
  coverage) directly in the PDF — this is materially bigger than
  anything in this design: font subsetting/embedding logic, a new
  vendored font asset (own approval path, similar to how Chart.js was
  vendored per AGENTS.md §3.2), and non-trivial additions to the
  hand-written PDF structure (`/Font` dictionaries need embedded
  `FontFile2`/`ToUnicode` CMaps for a non-base-14 font). This should be
  its own follow-up decision, not bundled into the first version.

## Open items for the implementation slice

- Decide the Cyrillic question above before writing code — it changes
  the scope meaningfully.
- Confirm whether the flyer needs branding (client logo) — `BRAND_LOGO`
  is already available per-client (`clients/jober/settings.py`,
  `clients/corvinum_eu/settings.py`) but embedding a raster logo into a
  hand-written PDF hits the same "no image-drawing primitive" limitation
  described in the certificate-upload doc's exploration of `pypdf` — an
  SVG logo could theoretically be vector-traced the same way the QR is,
  but a raster one (the CorvinumEU logo is `.webp`) could not, without
  Pillow or a real PDF drawing library.
- Print-size/margin testing on real paper once built — this is a
  physical-printing artifact, not just a rendered page.
