from __future__ import annotations

from django.conf import settings


def brand(request):
    """Client branding for the shared shell (Stage B3): the base template reads
    these instead of hardcoding a client's name/mark."""
    return {
        "BRAND_NAME": getattr(settings, "BRAND_NAME", "Platform"),
        "BRAND_MARK": getattr(settings, "BRAND_MARK", "P"),
        "BRAND_LOGO": getattr(settings, "BRAND_LOGO", ""),
        "CLIENT_DEFAULT_THEME": getattr(settings, "CLIENT_DEFAULT_THEME", "light"),
        "CLIENT_THEME_STORAGE_KEY": getattr(settings, "CLIENT_THEME_STORAGE_KEY", "platform-theme"),
        # Optional per-client stylesheet layered over the shared shell
        # (Stage C4, ADR 0022) — a static path, e.g. "corvinum/theme.css".
        "CLIENT_THEME_CSS": getattr(settings, "CLIENT_THEME_CSS", ""),
    }
