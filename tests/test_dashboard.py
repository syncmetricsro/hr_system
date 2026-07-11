from __future__ import annotations

import pytest
from django.urls import reverse
from django.utils import translation

from core.people.models import LifecycleStatus, Person
from core.projects.models import Project
from core.projects.services import schedule_trial

pytestmark = pytest.mark.django_db


@pytest.mark.jober_only  # Jober grants/lifecycle/features
def test_dashboard_shows_real_metrics(client, django_user_model):
    Project.objects.create(name="DHL", code="DHLBA", is_active=True)
    Person.objects.create(first_name="Ava", last_name="A", lifecycle_status=LifecycleStatus.AVAILABLE)
    person = Person.objects.create(first_name="Tom", last_name="T", lifecycle_status=LifecycleStatus.AVAILABLE)

    coord = django_user_model.objects.create_user(email="c@demo.jober.test", password="x", role="coordinator")
    schedule_trial(person, Project.objects.get(code="DHLBA"), actor=coord)  # -> one pending trial

    manager = django_user_model.objects.create_user(email="m@demo.jober.test", password="x", role="manager")
    client.force_login(manager)
    with translation.override("sk"):
        body = client.get(reverse("dashboard")).content.decode("utf-8")

    assert "Prevádzkový prehľad" in body          # heading (sk)
    assert "Tom T" in body                         # pending trial listed on the dashboard
    assert "DHL" in body
