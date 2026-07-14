from __future__ import annotations

import hashlib

from django.urls import reverse
from django.utils.translation import gettext as _

from core.accounts.permissions import Action, can
from core.notifications.types import NotificationItem
from core.ui.registry import flag_enabled
from features.blacklist.models import BlacklistCase, BlacklistCaseStatus


def blacklist_notification_provider(request):
    if not flag_enabled("duplicate_blacklist") or not can(request.user, Action.BLACKLIST_DECIDE):
        return []
    cases = list(BlacklistCase.objects.filter(status=BlacklistCaseStatus.PROPOSED).order_by("pk"))
    if not cases:
        return []
    state = "|".join(f"{case.pk}:{case.status}:{case.updated_at.isoformat()}" for case in cases)
    return [NotificationItem(
        key="blacklist:proposed",
        version=hashlib.sha256(state.encode()).hexdigest(),
        category="alert",
        severity="danger",
        title=str(_("Blacklist decisions are waiting")),
        detail=str(_("%(count)s proposed cases require a decision") % {"count": len(cases)}),
        url=reverse("blacklist_queue"),
        created_at=max(case.updated_at for case in cases),
    )]
