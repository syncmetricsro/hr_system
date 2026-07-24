"""QR helpers: inline SVG (ADR 0024) and a printable PDF flyer (ADR 0028).

Shared by 2FA enrollment (core/accounts) and feedback invitations
(features/feedback) — both just need a QR of a URL/URI with no extra network
trip or client-side JS.
"""

from __future__ import annotations

from django.conf import settings

_FONT_REGULAR = settings.BASE_DIR / "vendor" / "fonts" / "DejaVuSans.ttf"
_FONT_BOLD = settings.BASE_DIR / "vendor" / "fonts" / "DejaVuSans-Bold.ttf"


def qr_svg(data: str, *, scale: int = 4) -> str:
    import segno

    return segno.make(data, error="m").svg_inline(scale=scale, dark="#111111")


def qr_pdf(data: str, *, label: str = "") -> bytes:
    """A one-page, printable A4 PDF: the same QR module matrix `qr_svg` draws
    (segno, error correction level "m"), plus `label` and the raw URL as
    text below it — for staff to print and post (docs/product/
    feedback-flyer-design.md). Text uses the vendored DejaVu Sans font
    (ADR 0028) rather than a PDF standard base font, since base fonts have
    no Cyrillic glyphs and `label` may be any supported UI language.
    """
    import segno
    from fpdf import FPDF

    matrix = [list(row) for row in segno.make(data, error="m").matrix_iter(scale=1)]
    modules = len(matrix)

    pdf = FPDF(unit="mm", format="A4")
    pdf.add_page()
    pdf.add_font("DejaVu", "", str(_FONT_REGULAR))
    pdf.add_font("DejaVu", "B", str(_FONT_BOLD))

    page_width = pdf.w
    qr_size_mm = 90.0  # ~9cm printed - scannable from a few steps away
    module_size = qr_size_mm / modules
    qr_x = (page_width - qr_size_mm) / 2
    qr_y = 40.0

    pdf.set_fill_color(17, 17, 17)  # matches qr_svg's dark="#111111"
    for row_index, row in enumerate(matrix):
        for col_index, dark in enumerate(row):
            if dark:
                pdf.rect(
                    qr_x + col_index * module_size,
                    qr_y + row_index * module_size,
                    module_size,
                    module_size,
                    style="F",
                )

    if label:
        pdf.set_font("DejaVu", "B", 18)
        pdf.set_xy(0, qr_y + qr_size_mm + 12)
        pdf.cell(page_width, 10, text=label, align="C")

    pdf.set_font("DejaVu", "", 11)
    pdf.set_xy(0, qr_y + qr_size_mm + 24)
    pdf.cell(page_width, 8, text=data, align="C")

    return bytes(pdf.output())
