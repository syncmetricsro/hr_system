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
    assert totp.verify(RFC_SECRET, totp.totp_at(RFC_SECRET, now - 30), at=now)   # ±1 step
    assert not totp.verify(RFC_SECRET, totp.totp_at(RFC_SECRET, now - 90), at=now)
    assert not totp.verify(RFC_SECRET, "000000", at=now) or totp.totp_at(RFC_SECRET, now) == "000000"
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
    device = TotpDevice.objects.create(user=user, secret=totp.generate_secret(), confirmed=True)
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


def test_role_requirement_redirects_to_setup(client, user, settings):
    settings.TWO_FACTOR_REQUIRED_ROLES = ["manager"]
    resp = client.post(reverse("login"), {"email": user.email, "password": "x"})
    assert reverse("two_factor_setup") in resp["Location"]


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
