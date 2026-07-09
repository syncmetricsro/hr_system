from __future__ import annotations

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from core.audit.services import record_event


@require_http_methods(["GET", "POST"])
def login_page(request: HttpRequest) -> HttpResponse:
    """Email/password login reusing the existing Slovak login markup."""
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("dashboard"))

    error = None
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        user = authenticate(request, username=email, password=password)
        if user is not None and user.is_active:
            auth_login(request, user)
            record_event(user, "auth.login")
            return HttpResponseRedirect(reverse("dashboard"))
        error = _("Invalid email or password.")

    return TemplateResponse(request, "pages/login.html", {"error": error})


@require_http_methods(["POST"])
def logout_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        record_event(request.user, "auth.logout")
    auth_logout(request)
    return HttpResponseRedirect(reverse("login"))
