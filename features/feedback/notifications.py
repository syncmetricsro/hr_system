from __future__ import annotations

from django.urls import reverse
from django.utils.translation import gettext as _

from core.accounts.permissions import Action, can
from core.notifications.types import NotificationItem
from core.ui.registry import flag_enabled
from features.feedback.models import FeedbackSubmission


def feedback_notification_provider(request):
    if not flag_enabled("feedback") or not can(request.user, Action.FEEDBACK_VIEW):
        return []
    latest = FeedbackSubmission.objects.order_by("-pk").first()
    if latest is None:
        return []
    count = FeedbackSubmission.objects.count()
    return [NotificationItem(
        key="feedback:inbox",
        version=f"{latest.pk}:{count}",
        category="alert",
        severity="info",
        title=str(_("Worker feedback is available")),
        detail=str(_("%(count)s feedback submissions in the inbox") % {"count": count}),
        url=reverse("feedback_inbox"),
        created_at=latest.created_at,
    )]
