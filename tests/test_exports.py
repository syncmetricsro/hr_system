from __future__ import annotations

import pytest
from django.urls import reverse

from apps.people.models import Person
from apps.projects.models import Project

pytestmark = pytest.mark.django_db


@pytest.fixture
def make_user(django_user_model):
    def _make(role):
        return django_user_model.objects.create_user(
            email=f"{role}@demo.jober.test", password="x", role=role
        )
    return _make


def test_people_export_returns_csv_for_manager(client, make_user):
    Person.objects.create(first_name="Olha", last_name="Kovalenko")
    client.force_login(make_user("manager"))
    response = client.get(reverse("export_people"))
    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
    body = response.content.decode("utf-8")
    assert "last_name" in body and "Kovalenko" in body


def test_projects_export_for_observer(client, make_user):
    Project.objects.create(name="DHL", code="DHLBA")
    client.force_login(make_user("observer"))
    response = client.get(reverse("export_projects"))
    assert response.status_code == 200
    assert "DHLBA" in response.content.decode("utf-8")


def test_people_export_denied_for_recruiter(client, make_user):
    client.force_login(make_user("recruiter"))
    assert client.get(reverse("export_people")).status_code == 403


def test_finance_export_denied_for_recruiter(client, make_user):
    client.force_login(make_user("recruiter"))
    assert client.get(reverse("export_finance")).status_code == 403


def test_finance_export_allowed_for_observer(client, make_user):
    client.force_login(make_user("observer"))
    assert client.get(reverse("export_finance")).status_code == 200


def test_export_anonymous_redirects(client):
    response = client.get(reverse("export_people"))
    assert response.status_code == 302
    assert reverse("login") in response.headers["Location"]
