from __future__ import annotations

import hashlib

from django.urls import reverse
from django.utils.translation import gettext as _

from core.accounts.models import Role
from core.notifications.types import NotificationItem
from core.ui.registry import flag_enabled
from features.compliance.services import compliance_alerts


def compliance_notification_provider(request):
    if not flag_enabled("documents") or request.user.role == Role.OBSERVER:
        return []
    alerts = compliance_alerts(request.user)
    if request.user.role == Role.RECRUITER:
        alerts = [row for row in alerts if row["person"].owning_recruiter_id == request.user.pk]
    if not alerts:
        return []
    state = "|".join(
        f'{row["person"].pk}:{row["severity"]}:{row["due"] or "missing"}' for row in alerts
    )
    version = hashlib.sha256(state.encode()).hexdigest()
    severe = sum(1 for row in alerts if row["severity"] in {"expired", "missing"})
    return [NotificationItem(
        key="compliance:open",
        version=version,
        category="alert",
        severity="danger" if severe else "warning",
        title=str(_("Compliance problems need attention")),
        detail=str(_("%(count)s open document or medical alerts") % {"count": len(alerts)}),
        url=reverse("compliance_list"),
    )]
