from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.template.response import TemplateResponse

from features.compliance.services import compliance_alerts


@login_required
def compliance_list(request: HttpRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        "pages/compliance_list.html",
        {"alerts": compliance_alerts(request.user)},
    )
