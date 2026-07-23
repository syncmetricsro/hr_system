"""Inline SVG QR helper (ADR 0024): rendered server-side, embedded in the page.

Shared by 2FA enrollment (core/accounts) and feedback invitations
(features/feedback) — both just need a QR of a URL/URI with no extra network
trip or client-side JS.
"""

from __future__ import annotations


def qr_svg(data: str, *, scale: int = 4) -> str:
    import segno

    return segno.make(data, error="m").svg_inline(scale=scale, dark="#111111")
