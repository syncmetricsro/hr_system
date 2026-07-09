from __future__ import annotations

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.fixture
def make_user(django_user_model):
    def _make(role="observer", password="demo-pass-123"):
        return django_user_model.objects.create_user(
            email=f"{role}@demo.jober.test", password=password, role=role
        )

    return _make


def test_login_success(client, make_user):
    make_user(role="manager")
    response = client.post(
        reverse("login"),
        {"email": "manager@demo.jober.test", "password": "demo-pass-123"},
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith(reverse("dashboard"))


def test_login_wrong_password_shows_error(client, make_user):
    make_user(role="manager")
    response = client.post(
        reverse("login"),
        {"email": "manager@demo.jober.test", "password": "nope"},
    )
    assert response.status_code == 200
    assert "Nesprávny" in response.content.decode("utf-8")


def test_logout_redirects_to_login(client, make_user):
    user = make_user(role="recruiter")
    client.force_login(user)
    response = client.post(reverse("logout"))
    assert response.status_code == 302
    assert reverse("login") in response.headers["Location"]


def test_login_writes_audit_event(client, make_user):
    from core.audit.models import AuditEvent

    make_user(role="coordinator")
    client.post(
        reverse("login"),
        {"email": "coordinator@demo.jober.test", "password": "demo-pass-123"},
    )
    assert AuditEvent.objects.filter(action="auth.login").exists()


def test_manager_sees_gated_button_observer_does_not(client, make_user):
    manager = make_user(role="manager")
    client.force_login(manager)
    body = client.get(reverse("dashboard")).content.decode("utf-8")
    assert "Spravovať projekty" in body

    client.logout()
    observer = make_user(role="observer")
    client.force_login(observer)
    body = client.get(reverse("dashboard")).content.decode("utf-8")
    assert "Spravovať projekty" not in body


def test_language_switch_changes_active_language(client, make_user):
    user = make_user(role="manager")
    client.force_login(user)
    client.post(reverse("set_language"), {"language": "hu", "next": "/"})
    # The dashboard should now resolve under the Hungarian prefix.
    response = client.get("/hu/")
    assert response.status_code == 200
