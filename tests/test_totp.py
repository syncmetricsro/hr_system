from __future__ import annotations

import time

import pytest
from django.urls import reverse

from core.accounts import totp
from core.accounts.models import TotpDevice

pytestmark = pytest.mark.django_db

# RFC 6238 Appendix B vectors (SHA1, ASCII secret "12345678901234567890").
RFC_SECRET = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
RFC_VECTORS = [
    (59, "94287082"),
    (1111111109, "07081804"),
    (1111111111, "14050471"),
    (1234567890, "89005924"),
]


def test_rfc6238_vectors():
    for t, expected in RFC_VECTORS:
        # RFC vectors are 8-digit; our 6-digit codes are their last 6 digits.
        assert totp.totp_at(RFC_SECRET, t) == expected[-6:]


def test_verify_window():
    now = int(time.time())
    assert totp.verify(RFC_SECRET, totp.totp_at(RFC_SECRET, now), at=now)
    assert totp.verify(
        RFC_SECRET, totp.totp_at(RFC_SECRET, now - 30), at=now
    )  # ±1 step
    assert not totp.verify(RFC_SECRET, totp.totp_at(RFC_SECRET, now - 90), at=now)
    assert (
        not totp.verify(RFC_SECRET, "000000", at=now)
        or totp.totp_at(RFC_SECRET, now) == "000000"
    )
    assert not totp.verify(RFC_SECRET, "junk", at=now)


def test_generate_secret_is_base32():
    import base64

    secret = totp.generate_secret()
    assert len(base64.b32decode(secret)) == 20


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        email="m@demo.jober.test", password="x", role="manager"
    )


def test_login_unchanged_without_device(client, user):
    resp = client.post(reverse("login"), {"email": user.email, "password": "x"})
    assert resp.status_code == 302 and resp["Location"].endswith("/")  # dashboard


def test_confirmed_device_forces_verify_step(client, user):
    device = TotpDevice.objects.create(
        user=user, secret=totp.generate_secret(), confirmed=True
    )
    resp = client.post(reverse("login"), {"email": user.email, "password": "x"})
    assert reverse("two_factor_verify") in resp["Location"]
    # Wrong code stays on the verify page…
    resp = client.post(reverse("two_factor_verify"), {"code": "000001"})
    assert resp.status_code == 200
    # …the current code completes login.
    code = totp.totp_at(device.secret, int(time.time()))
    resp = client.post(reverse("two_factor_verify"), {"code": code})
    assert resp.status_code == 302
    assert client.get(reverse("dashboard")).status_code == 200


def test_disabled_two_factor_bypasses_device_and_role_requirement(
    client, user, settings
):
    settings.TWO_FACTOR_AUTH_ENABLED = False
    settings.TWO_FACTOR_REQUIRED_ROLES = ["manager"]
    TotpDevice.objects.create(user=user, secret=totp.generate_secret(), confirmed=True)

    resp = client.post(reverse("login"), {"email": user.email, "password": "x"})

    assert resp.status_code == 302
    assert resp["Location"] == reverse("dashboard")
    assert "pending_2fa_user" not in client.session
    assert client.get(reverse("dashboard")).status_code == 200


def test_disabled_two_factor_setup_redirects_without_creating_device(
    client, user, settings
):
    settings.TWO_FACTOR_AUTH_ENABLED = False
    client.force_login(user)

    resp = client.get(reverse("two_factor_setup"))

    assert resp.status_code == 302
    assert resp["Location"] == reverse("dashboard")
    assert not TotpDevice.objects.filter(user=user).exists()


def test_role_requirement_redirects_to_setup(client, user, settings):
    settings.TWO_FACTOR_REQUIRED_ROLES = ["manager"]
    resp = client.post(reverse("login"), {"email": user.email, "password": "x"})
    assert reverse("two_factor_setup") in resp["Location"]


def test_setup_page_embeds_qr_svg(client, user):
    """ADR 0024: the setup page carries an inline SVG QR of the otpauth URI —
    no external requests, no JS."""
    client.force_login(user)
    resp = client.get(reverse("two_factor_setup"))
    html = resp.content.decode()
    assert "<svg" in html and 'class="qr-plate"' in html
    svg = html[html.index("<svg") : html.index("</svg>")]
    assert "http://" not in svg and "https://" not in svg


def test_qr_svg_helper_is_deterministic_per_uri():
    from core.ui.qr import qr_svg

    svg = qr_svg("otpauth://totp/X:a@b?secret=ABC&issuer=X")
    assert svg.startswith("<svg") and "</svg>" in svg
    assert svg == qr_svg("otpauth://totp/X:a@b?secret=ABC&issuer=X")
    assert svg != qr_svg("otpauth://totp/X:a@b?secret=DIFFERENT&issuer=X")


def test_setup_confirm_flow(client, user):
    client.force_login(user)
    resp = client.get(reverse("two_factor_setup"))
    assert resp.status_code == 200
    device = TotpDevice.objects.get(user=user)
    assert not device.confirmed
    code = totp.totp_at(device.secret, int(time.time()))
    resp = client.post(reverse("two_factor_setup"), {"code": code})
    assert resp.status_code == 302
    device.refresh_from_db()
    assert device.confirmed


# --- the deployment switch (2026-08-09) ------------------------------------
#
# TWO_FACTOR_AUTH_ENABLED became env-overridable so a client test window can be
# granted password-only access for a stated period without a release per flip.
# The behaviour of the switch being off is covered above; what is new is that a
# deployment can set it, that it defaults to on, and that turning it off
# announces itself.


def _setting_under_env(value: str | None) -> str:
    """Read TWO_FACTOR_AUTH_ENABLED from a fresh interpreter with that env."""
    import os
    import subprocess
    import sys
    from pathlib import Path

    repo = Path(__file__).resolve().parent.parent
    env = dict(os.environ)
    env.update(
        {
            "DJANGO_SETTINGS_MODULE": "config.settings.local",
            "DJANGO_DEBUG": "1",
            "DJANGO_SECRET_KEY": "test-only-two-factor-switch-key",
        }
    )
    if value is None:
        env.pop("DJANGO_TWO_FACTOR_ENABLED", None)
    else:
        env["DJANGO_TWO_FACTOR_ENABLED"] = value
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import django; django.setup();"
            " from django.conf import settings;"
            " print(settings.TWO_FACTOR_AUTH_ENABLED)",
        ],
        capture_output=True,
        text=True,
        env=env,
        cwd=repo,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def test_two_factor_is_on_when_the_environment_says_nothing():
    """The default must stay on: an environment that forgets to mention it
    keeps two-factor authentication rather than silently losing it."""
    assert _setting_under_env(None) == "True"


def test_a_deployment_can_switch_two_factor_off():
    assert _setting_under_env("0") == "False"


def test_switching_it_back_on_needs_only_the_variable():
    assert _setting_under_env("1") == "True"


def test_a_disabled_switch_is_reported_outside_debug(settings):
    """The exemption announces itself on every deploy, so 'we will turn it back
    on' cannot quietly become nobody's job."""
    from core.checks import two_factor_disabled_check

    settings.DEBUG = False
    settings.TWO_FACTOR_AUTH_ENABLED = False

    warnings = two_factor_disabled_check(None)

    assert [w.id for w in warnings] == ["accounts.W001"]


def test_the_local_demo_runners_are_not_nagged(settings):
    """They disable it on purpose; warning there teaches people to ignore it."""
    from core.checks import two_factor_disabled_check

    settings.DEBUG = True
    settings.TWO_FACTOR_AUTH_ENABLED = False

    assert two_factor_disabled_check(None) == []


def test_an_enabled_deployment_is_quiet(settings):
    from core.checks import two_factor_disabled_check

    settings.DEBUG = False
    settings.TWO_FACTOR_AUTH_ENABLED = True

    assert two_factor_disabled_check(None) == []


def test_an_enrolled_device_survives_the_switch(client, user, settings):
    """The promise behind the temporary exemption.

    Turning it off must not delete anyone's second factor, or 'we will re-enable
    it' would mean every manager enrolling again from scratch.
    """
    device = TotpDevice.objects.create(
        user=user, secret=totp.generate_secret(), confirmed=True
    )

    settings.TWO_FACTOR_AUTH_ENABLED = False
    resp = client.post(reverse("login"), {"email": user.email, "password": "x"})
    assert resp["Location"] == reverse("dashboard")
    assert TotpDevice.objects.filter(pk=device.pk, confirmed=True).exists()

    client.logout()
    settings.TWO_FACTOR_AUTH_ENABLED = True
    resp = client.post(reverse("login"), {"email": user.email, "password": "x"})
    assert resp["Location"] == reverse("two_factor_verify")
