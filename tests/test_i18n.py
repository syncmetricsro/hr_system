from __future__ import annotations

import pytest

# Jober-specific URLs/policies/languages — excluded from the corvinum lane.
pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


@pytest.fixture
def client_logged_in(client, django_user_model):
    user = django_user_model.objects.create_user(
        email="i18n@demo.jober.test", password="x", role="manager"
    )
    client.force_login(user)
    return client


@pytest.mark.parametrize(
    "prefix,expected",
    [
        ("en", "Reports"),
        ("sk", "Reporty"),
        ("hu", "Jelentések"),
        ("uk", "Звіти"),
    ],
)
def test_dashboard_renders_in_each_language(client_logged_in, prefix, expected):
    response = client_logged_in.get(f"/{prefix}/")
    assert response.status_code == 200
    assert expected in response.content.decode("utf-8")


def test_unprefixed_root_redirects_to_default_slovak(client_logged_in):
    response = client_logged_in.get("/")
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/sk/")
