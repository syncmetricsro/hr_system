"""Person-card contributions of the worker-messaging feature.

Two panels, deliberately separate: SMS is a short operational nudge to a
handset, an offer email is long-form outreach to an inbox with its own
permission, its own opt-out and its own record type.
"""

from __future__ import annotations

from core.accounts.models import Role
from core.accounts.permissions import Action, user_office_scope
from core.accounts.permissions import can as user_can
from core.mail import email_configured
from core.ui.registry import flag_enabled
from features.messaging.models import JobOffer, MessageTemplate, OfferEmailKind
from features.messaging.services import offer_email_block_reason, sms_configured


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
        # The panel still renders when SMS is unconfigured, with the control
        # disabled and a reason. Hiding it entirely would leave a presenter
        # wondering where the feature went; offering a live button that files
        # a failed message is worse still.
        "sms_configured": sms_configured(),
        "message_templates": MessageTemplate.objects.filter(is_active=True),
        "recent_messages": person.messages.all()[:5],
    }


def offer_email_panel(request, person):
    if not flag_enabled("offer_emails"):
        return None
    if not user_can(request.user, Action.OFFER_EMAIL_SEND):
        return None
    # Same coordinator narrowing as SMS: a coordinator contacts their own
    # people, not everyone in the office.
    if getattr(request.user, "role", None) == Role.COORDINATOR:
        if request.user.pk not in person.responsible_coordinator_ids():
            return None

    offers = JobOffer.objects.filter(is_active=True).select_related("project", "office")
    scope = user_office_scope(request.user)
    if scope is not None:
        offers = offers.filter(office__in=scope)

    # Like the SMS panel, this renders even when nothing can be sent - with the
    # control disabled and the reason visible. A panel that vanishes when a
    # worker opts out just reads as a missing feature.
    return {
        "email_configured": email_configured(),
        "person_email": person.email,
        "blocked_reason": offer_email_block_reason(person),
        "offers": offers,
        "kinds": OfferEmailKind.choices,
        "recent_emails": person.emails.all()[:5],
    }
