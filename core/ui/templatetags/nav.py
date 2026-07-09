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
