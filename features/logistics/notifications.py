from __future__ import annotations

import hashlib

from django.urls import reverse
from django.utils.translation import gettext as _

from core.accounts.permissions import Action, can
from core.notifications.types import NotificationItem
from core.ui.registry import flag_enabled
from features.logistics.services import pending_deduction_reviews


def logistics_notification_provider(request):
    if not flag_enabled("equipment") or not can(request.user, Action.EQUIPMENT_REVIEW_DEDUCTION):
        return []
    issues = list(pending_deduction_reviews()["issues"])
    if not issues:
        return []
    state = "|".join(f"{issue.pk}:{issue.review_status}:{issue.charge_amount}" for issue in issues)
    return [NotificationItem(
        key="equipment:pending-reviews",
        version=hashlib.sha256(state.encode()).hexdigest(),
        category="alert",
        severity="warning",
        title=str(_("Equipment reviews are waiting")),
        detail=str(_("%(count)s unreturned equipment reviews") % {"count": len(issues)}),
        url=reverse("equipment_reviews"),
        created_at=max(issue.issued_at for issue in issues),
    )]
