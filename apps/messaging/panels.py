"""Person-card contribution of the worker-messaging feature (SMS panel)."""

from __future__ import annotations

from apps.accounts.models import Role
from apps.accounts.permissions import Action
from apps.accounts.permissions import can as user_can
from apps.core.registry import flag_enabled
from apps.messaging.models import MessageTemplate


def sms_panel(request, person):
    if not flag_enabled("worker_messaging"):
        return None
    can_message = (
        bool(person.phone)
        and user_can(request.user, Action.SMS_SEND)
        and (
            getattr(request.user, "role", None) != Role.COORDINATOR
            or request.user.pk in person.responsible_coordinator_ids()
        )
    )
    if not can_message:
        return None
    return {
        "message_templates": MessageTemplate.objects.filter(is_active=True),
        "recent_messages": person.messages.all()[:5],
    }
