from __future__ import annotations

from django import template

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


@register.filter
def db_trans(value):
    """Runtime-translate seeded catalog labels (blacklist categories,
    checklist items, …): the DB stores the canonical English string; if the
    active catalog has it as a msgid it renders localized, otherwise the
    operator-entered text falls through unchanged."""
    from django.utils.translation import gettext

    return gettext(str(value)) if value else value
