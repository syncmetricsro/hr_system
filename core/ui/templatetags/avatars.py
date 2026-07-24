from __future__ import annotations

from django.template import Library
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import SafeString

register = Library()

# Illustrated per-role default avatars (docs/product/avatar-design.md §1),
# generated 2026-07-25 - static/avatars/default_{role}.webp (STATICFILES_DIRS
# only scans the top-level static/ dir - NOT core/static/ - and the
# Dockerfile copies static/ subdirectories individually, so this needs its
# own COPY line there too). Person has no .role field, so it always gets
# the "worker" default.
_DEFAULT_AVATAR_ROLES = {"recruiter", "coordinator", "manager", "observer"}


def _default_avatar_url(obj) -> str:
    role = getattr(obj, "role", None)
    if role not in _DEFAULT_AVATAR_ROLES:
        role = "worker"
    return static(f"avatars/default_{role}.webp")


@register.simple_tag
def avatar(obj, size: str = "sm") -> SafeString:
    """Render an avatar for a Person or User: uploaded photo if present,
    else an illustrated per-role default (docs/product/avatar-design.md) -
    a worker silhouette for a Person, or the matching role-colored
    silhouette for a User (recruiter/coordinator/manager/observer).

    Usage: ``{% avatar person_or_user size="md" %}``.
    """
    photo = getattr(obj, "avatar", None) if obj is not None else None
    if photo:
        return format_html(
            '<img class="avatar avatar-{}" src="{}" alt="">', size, photo.url
        )
    return format_html(
        '<img class="avatar avatar-{}" src="{}" alt="">', size, _default_avatar_url(obj)
    )


# Tone per LifecycleStatus value (core.people.models) - kept as raw strings
# rather than importing the enum, matching this module's existing duck-typed
# style (avatar() above never imports Person/User either).
_STATUS_TONES = {
    "working": "success",
    "trial_day": "warning",
    "available": "info",
    "inactive": "neutral",
    "blacklisted": "danger",
}


@register.simple_tag
def status_pill(person, size: str = "dot") -> SafeString:
    """Render a worker's lifecycle status as a colored pill overlapping the
    avatar's bottom edge (docs/product/pill-system-design.md §1) - a
    ``Person`` concept only, never called for a ``User``'s own avatar.

    ``size="dot"``: a plain colored dot, no text (worker-list thumbnail -
    no room for a legible label at that size). ``size="label"``: a labeled
    pill (person-detail header).

    Usage - wrap together with ``{% avatar %}`` in a ``.avatar-stack``
    container so the pill has something to overlap:
    ``<span class="avatar-stack">{% avatar person %}{% status_pill person %}</span>``
    """
    status = getattr(person, "lifecycle_status", None)
    tone = _STATUS_TONES.get(status, "neutral")
    label = person.get_lifecycle_status_display() if hasattr(person, "get_lifecycle_status_display") else ""
    if size == "label":
        return format_html(
            '<span class="status-pill status-pill-label status-pill-{}">{}</span>', tone, label
        )
    return format_html(
        '<span class="status-pill status-pill-dot status-pill-{}" aria-hidden="true" data-tooltip="{}"></span>',
        tone, label,
    )


@register.simple_tag(takes_context=True)
def person_badges(context, person) -> list[dict]:
    """Feature-contributed small icon row for a person (docs/product/
    pill-system-design.md §2 Phase 2), e.g. certificate-category icons -
    core has no built-in notion of what these are, it only renders whatever
    ``core.ui.registry.register_person_badges`` contributions return.

    Returns a plain list (not markup) so callers control rendering:
    ``{% person_badges person as badges %}{% for b in badges %}...{% endfor %}``.
    """
    from core.ui.registry import person_badges as _person_badges

    request = context.get("request")
    if request is None:
        return []
    return _person_badges(request, person)
