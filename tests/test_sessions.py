from __future__ import annotations

import pytest
from django.conf import settings
from django.urls import reverse

# Jober-specific URLs/policies/languages — excluded from the corvinum lane.
pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


def test_session_policy_is_30_day_rolling():
    """Owner decision 2026-07-12: activity keeps staff signed in; only
    inactivity (30 days by default, env-overridable) logs out."""
    assert settings.SESSION_COOKIE_AGE == 30 * 24 * 3600
    assert settings.SESSION_SAVE_EVERY_REQUEST is True


def test_client_cookie_names_do_not_collide():
    """Both demo apps share localhost (ports are cookie-invisible): each
    client must use its own session/CSRF cookie names."""
    assert settings.SESSION_COOKIE_NAME == "jober_sessionid"
    assert settings.CSRF_COOKIE_NAME == "jober_csrftoken"


def test_login_sets_rolling_cookie_with_configured_age(client, django_user_model):
    user = django_user_model.objects.create_user(
        email="ses@demo.jober.test", password="x", role="manager"
    )
    response = client.post(reverse("login"), {"email": user.email, "password": "x"})
    cookie = response.cookies.get("jober_sessionid")
    assert cookie is not None, "login must set the client-named session cookie"
    assert int(cookie["max-age"]) == settings.SESSION_COOKIE_AGE
