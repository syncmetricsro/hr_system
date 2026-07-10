from __future__ import annotations

from django.conf import settings


def brand(request):
    """Client branding for the shared shell (Stage B3): the base template reads
    these instead of hardcoding a client's name/mark."""
    return {
        "BRAND_NAME": getattr(settings, "BRAND_NAME", "Platform"),
        "BRAND_MARK": getattr(settings, "BRAND_MARK", "P"),
    }
