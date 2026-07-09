"""Reports contribution of the compliance/documents feature."""

from __future__ import annotations

from django.utils.translation import gettext as _

from apps.compliance.services import compliance_alerts
from apps.core.registry import flag_enabled


def compliance_tile(request):
    if not flag_enabled("documents"):
        return None
    return {"label": _("Compliance"), "value": len(compliance_alerts(request.user))}
