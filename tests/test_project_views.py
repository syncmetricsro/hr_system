from __future__ import annotations

import pytest
from django.urls import reverse

from core.people.models import Person
from core.projects.models import Project
from core.projects.services import activate_on_project

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager(django_user_model):
    return django_user_model.objects.create_user(
        email="m@demo.jober.test", password="x", role="manager"
    )


def test_project_list_requires_login(client):
    response = client.get(reverse("project_list"))
    assert response.status_code == 302
    assert reverse("login") in response.headers["Location"]


def test_project_list_shows_project(client, manager):
    Project.objects.create(name="DHL Bratislava", code="DHLBA")
    client.force_login(manager)
    body = client.get(reverse("project_list")).content.decode("utf-8")
    assert "DHL Bratislava" in body


def test_project_detail_lists_assigned_workers(client, manager):
    project = Project.objects.create(name="DHL Bratislava", code="DHLBA")
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    activate_on_project(person, project, actor=manager)
    client.force_login(manager)
    body = client.get(reverse("project_detail", args=[project.pk])).content.decode("utf-8")
    assert "Kovalenko" in body
