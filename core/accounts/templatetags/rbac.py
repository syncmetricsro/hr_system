from __future__ import annotations

from django import template

from core.accounts.permissions import Action, can as _can

register = template.Library()


@register.simple_tag(takes_context=True)
def can(context, action_value: str) -> bool:
    """Template gate: ``{% can 'project.manage' as may_manage %}``.

    A hidden button must be backed by a real server-side check, so this mirrors
    the same ``can()`` used by the ``require_action`` view decorator.
    """
    user = getattr(context.get("request"), "user", None)
    try:
        action = Action(action_value)
    except ValueError:
        return False
    return _can(user, action)
