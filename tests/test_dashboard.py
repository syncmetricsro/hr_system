from __future__ import annotations

import pytest
from django.urls import reverse
from django.utils import translation

from core.people.models import LifecycleStatus, Person
from core.projects.models import Project
from core.projects.services import schedule_trial

pytestmark = pytest.mark.django_db


@pytest.mark.jober_only  # Jober grants/lifecycle/features
def test_dashboard_renders_the_combined_report_surface(client, django_user_model):
    Project.objects.create(name="DHL", code="DHLBA", is_active=True)
    Person.objects.create(first_name="Ava", last_name="A", lifecycle_status=LifecycleStatus.AVAILABLE)
    person = Person.objects.create(first_name="Tom", last_name="T", lifecycle_status=LifecycleStatus.AVAILABLE)

    coord = django_user_model.objects.create_user(email="c@demo.jober.test", password="x", role="coordinator")
    schedule_trial(person, Project.objects.get(code="DHLBA"), actor=coord)  # -> one pending trial

    manager = django_user_model.objects.create_user(email="m@demo.jober.test", password="x", role="manager")
    client.force_login(manager)
    with translation.override("sk"):
        response = client.get(reverse("dashboard"))
        body = response.content.decode("utf-8")

    assert response.status_code == 200
    assert "Reporty" in body
    assert 'href="/sk/projects/"' in body
    assert 'href="/sk/trials/"' in body
    assert "1" in body  # one pending trial is reflected in its drill-down tile
