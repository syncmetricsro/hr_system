from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_POST

from core.notifications.services import dismiss_item, visible_items


@login_required
@require_GET
def notification_panel(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(
        request,
        "notifications/panel.html",
        {"notification_center": visible_items(request)},
    )


@login_required
@require_POST
def notification_dismiss(request: HttpRequest) -> HttpResponse:
    key = request.POST.get("key", "")
    version = request.POST.get("version", "")
    if not key or not version or not dismiss_item(request, key, version):
        return HttpResponseBadRequest(_("Notification is not available."))
    if request.headers.get("HX-Request") == "true":
        return TemplateResponse(
            request,
            "notifications/panel.html",
            {"notification_center": visible_items(request)},
        )
    next_url = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = reverse("reports")
    return redirect(next_url)
