from __future__ import annotations

from django import template
from django.utils.html import format_html
from django.utils.safestring import SafeString

register = template.Library()


@register.simple_tag(takes_context=True)
def nav_active(context, *url_names: str) -> str:
    """Return ``is-active`` when the resolved view belongs to this nav tab.

    Usage: ``<a class="folder-tab {% nav_active 'people_list' 'person_detail' %}">``.
    Matches on the resolver's ``url_name`` so it works under every language
    prefix (fixes the hardcoded Overview tab that stayed highlighted forever).
    """
    request = context.get("request")
    match = getattr(request, "resolver_match", None)
    if match is None:
        return ""
    return "is-active" if match.url_name in url_names else ""


@register.simple_tag
def flag_on(name: str) -> bool:
    """True when a feature flag is enabled for the running client (Stage C4:
    the shared shell must not link URLs a client's flag set never mounts)."""
    from core.ui.registry import flag_enabled

    return flag_enabled(name)


@register.simple_tag(takes_context=True)
def nav_badge(context, slot: str) -> SafeString:
    """Attention-count badge for a nav tab (docs/product/
    pill-system-design.md §3) - reuses the existing ``.notification-count``
    pill styling. Renders nothing if no feature registered a provider for
    ``slot``, or the provider returned no count. Place inside the same
    ``{% if %}`` block that already gates the tab itself, so this never
    queries for a role/client that wouldn't see the tab at all.

    Usage: ``{% nav_badge "compliance" %}``.
    """
    from core.ui.registry import nav_badge as _nav_badge

    request = context.get("request")
    if request is None:
        return SafeString("")
    result = _nav_badge(request, slot)
    if not result or not result.get("count"):
        return SafeString("")
    css = "notification-count-alert" if result.get("severe") else "notification-count-warning"
    return format_html('<span class="notification-count {}">{}</span>', css, result["count"])


@register.filter
def db_trans(value):
    """Runtime-translate seeded catalog labels (blacklist categories,
    checklist items, …): the DB stores the canonical English string; if the
    active catalog has it as a msgid it renders localized, otherwise the
    operator-entered text falls through unchanged."""
    from django.utils.translation import gettext

    return gettext(str(value)) if value else value
