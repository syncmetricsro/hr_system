from __future__ import annotations

from django.conf import settings
from django.template import Library
from django.utils.html import format_html
from django.utils.safestring import SafeString

from core.ui.icons import ICONS

register = Library()


@register.simple_tag
def icon(name: str, size: str = "sm") -> SafeString:
    """Render a named icon using the running client's own mechanism.

    Usage: ``{% icon "add" %}`` or ``{% icon "add" size="md" %}``. Backend
    is chosen per client via ``settings.ICON_BACKEND`` ("svg_sprite" or
    "material_symbols"). An unknown icon name, or a name not defined for
    the active backend, renders nothing rather than raising — icons are
    a presentational concern, not something that should 500 a page.
    """
    entry = ICONS.get(name)
    if entry is None:
        return SafeString("")

    backend = getattr(settings, "ICON_BACKEND", "svg_sprite")
    if backend == "material_symbols":
        ligature = entry.get("material")
        if not ligature:
            return SafeString("")
        return format_html(
            '<span class="material-symbols-outlined icon icon-{}" aria-hidden="true">{}</span>',
            size,
            ligature,
        )

    symbol = entry.get("svg")
    if not symbol:
        return SafeString("")
    return format_html(
        '<svg class="icon icon-{}" aria-hidden="true"><use href="#nav-icon-{}"></use></svg>',
        size,
        symbol,
    )
