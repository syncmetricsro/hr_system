from __future__ import annotations

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from core.accounts import totp as totp_lib
from core.audit.services import record_event


def _requires_second_factor(user) -> bool:
    device = getattr(user, "totp_device", None)
    return device is not None and device.confirmed


def _role_requires_totp(user) -> bool:
    required = getattr(settings, "TWO_FACTOR_REQUIRED_ROLES", [])
    return getattr(user, "role", None) in required


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
            if _requires_second_factor(user):
                # Password OK — defer the session until the TOTP step passes.
                request.session["pending_2fa_user"] = user.pk
                return HttpResponseRedirect(reverse("two_factor_verify"))
            auth_login(request, user)
            record_event(user, "auth.login")
            if _role_requires_totp(user):
                messages.warning(request, _("Your role requires two-factor authentication — set it up now."))
                return HttpResponseRedirect(reverse("two_factor_setup"))
            return HttpResponseRedirect(reverse("dashboard"))
        error = _("Invalid email or password.")

    return TemplateResponse(request, "pages/login.html", {"error": error})


@require_http_methods(["POST"])
def logout_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        record_event(request.user, "auth.logout")
    auth_logout(request)
    return HttpResponseRedirect(reverse("login"))


@require_http_methods(["GET", "POST"])
def two_factor_verify(request: HttpRequest) -> HttpResponse:
    """Second login step for users with a confirmed TOTP device."""
    from django.contrib.auth import get_user_model

    user_pk = request.session.get("pending_2fa_user")
    if user_pk is None:
        return HttpResponseRedirect(reverse("login"))
    user = get_user_model().objects.filter(pk=user_pk, is_active=True).first()
    device = getattr(user, "totp_device", None) if user else None
    if user is None or device is None or not device.confirmed:
        request.session.pop("pending_2fa_user", None)
        return HttpResponseRedirect(reverse("login"))

    error = None
    if request.method == "POST":
        if totp_lib.verify(device.secret, request.POST.get("code", "")):
            request.session.pop("pending_2fa_user", None)
            auth_login(request, user)
            record_event(user, "auth.login", second_factor="totp")
            return HttpResponseRedirect(reverse("dashboard"))
        error = _("Invalid code.")
        record_event(user, "auth.totp_failed")

    return TemplateResponse(request, "pages/two_factor_verify.html", {"error": error})


@login_required
@require_http_methods(["GET", "POST"])
def two_factor_setup(request: HttpRequest) -> HttpResponse:
    """Create (or replace an unconfirmed) TOTP device; confirm with a code."""
    from core.accounts.models import TotpDevice

    device = getattr(request.user, "totp_device", None)
    error = None

    if request.method == "POST" and device is not None and not device.confirmed:
        if totp_lib.verify(device.secret, request.POST.get("code", "")):
            device.confirmed = True
            device.confirmed_at = timezone.now()
            device.save(update_fields=["confirmed", "confirmed_at"])
            record_event(request.user, "auth.totp_enabled")
            messages.success(request, _("Two-factor authentication enabled."))
            return HttpResponseRedirect(reverse("dashboard"))
        error = _("Invalid code.")

    if device is None:
        device = TotpDevice.objects.create(
            user=request.user, secret=totp_lib.generate_secret()
        )

    uri = totp_lib.provisioning_uri(
        device.secret,
        account=request.user.email,
        issuer=getattr(settings, "BRAND_NAME", "Platform"),
    )
    return TemplateResponse(
        request,
        "pages/two_factor_setup.html",
        {"device": device, "uri": uri, "qr_svg": _qr_svg(uri), "error": error},
    )


def _qr_svg(uri: str) -> str:
    """Inline SVG QR of the provisioning URI (ADR 0024): rendered server-side,
    embedded in the page — the secret makes no extra network trip."""
    import segno

    return segno.make(uri, error="m").svg_inline(scale=4, dark="#111111")