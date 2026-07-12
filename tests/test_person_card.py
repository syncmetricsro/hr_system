from __future__ import annotations

import pytest
from django.urls import reverse
from django.utils import translation

from core.people.models import LifecycleStatus, Person
from core.people.services import person_history
from core.projects.models import Project, TrialOutcome
from core.projects.services import record_trial_outcome, schedule_trial

pytestmark = pytest.mark.django_db


@pytest.fixture
def coordinator(django_user_model):
    return django_user_model.objects.create_user(
        email="c@demo.jober.test", password="x", role="coordinator"
    )


@pytest.mark.jober_only  # Jober grants/lifecycle/features
def test_history_is_newest_first_and_covers_events(coordinator):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    project = Project.objects.create(name="DHL", code="DHLBA")
    trial = schedule_trial(person, project, actor=coordinator)
    record_trial_outcome(trial, TrialOutcome.FAIL, actor=coordinator)

    with translation.override("en"):
        history = person_history(person)
    assert history, "history should not be empty"
    labels = [e["label"] for e in history]
    assert "Trial scheduled" in labels
    assert "Trial outcome" in labels
    assert "Status changed" in labels  # lifecycle transitions audited
    whens = [e["when"] for e in history]
    assert whens == sorted(whens, reverse=True)  # newest first


def test_people_list_status_filter(client, django_user_model):
    Person.objects.create(first_name="Ava", last_name="Available", lifecycle_status=LifecycleStatus.AVAILABLE)
    Person.objects.create(first_name="Ina", last_name="Inactive", lifecycle_status=LifecycleStatus.INACTIVE)
    user = django_user_model.objects.create_user(email="m@demo.jober.test", password="x", role="manager")
    client.force_login(user)

    body = client.get(reverse("people_list"), {"status": "inactive"}).content.decode("utf-8")
    assert "Inactive" in body
    assert "Available</h3>" not in body  # the Available person's name is filtered out


def test_history_translates_lifecycle_values_and_seeded_equipment(coordinator):
    from features.logistics.models import EquipmentItem
    from features.logistics.services import issue_equipment

    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    boots = EquipmentItem.objects.create(name="Work boots", size="42")
    issue_equipment(person, boots, 1, actor=coordinator)
    person.set_status(LifecycleStatus.WORKING, actor=coordinator)

    with translation.override("hu"):
        history = person_history(person)

    details = [event["detail"] for event in history]
    assert "Elérhető → Dolgozik" in details
    assert "Munkavédelmi bakancs 42" in details
