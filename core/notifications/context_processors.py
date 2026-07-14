from __future__ import annotations

from core.accounts.models import Role
from core.notifications.services import visible_items


def notification_center(request):
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated or getattr(user, "role", None) == Role.OBSERVER:
        return {"notification_center": {"enabled": False}}
    return {"notification_center": visible_items(request)}
