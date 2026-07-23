from __future__ import annotations

import pytest
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext

from core.audit.models import AuditEvent
from core.people.models import LifecycleStatus, Person
from core.projects.models import Project, TrialAssignment
from features.logistics.models import Accommodation, AccommodationCostPeriod, Room
from features.logistics.services import assign_room

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


@pytest.mark.parametrize("language,expected", [
    ("sk", "Vytvoriť ubytovanie"),
    ("hu", "Szállás létrehozása"),
    ("uk", "Створити місце проживання"),
])
def test_operations_labels_are_translated(language, expected):
    with translation.override(language):
        assert gettext("Create location") == expected


@pytest.fixture
def operations(django_user_model):
    manager = django_user_model.objects.create_user(
        email="manager@demo.jober.test", password="x", role="manager"
    )
    coordinator = django_user_model.objects.create_user(
        email="coordinator@demo.jober.test", password="x", role="coordinator"
    )
    recruiter = django_user_model.objects.create_user(
        email="recruiter@demo.jober.test", password="x", role="recruiter"
    )
    project = Project.objects.create(name="DHL", code="DHL", is_active=True)
    project.responsible_coordinators.add(coordinator)
    other = Project.objects.create(name="Other", code="OTHER", is_active=True)
    person = Person.objects.create(
        first_name="Tran", last_name="Available",
        lifecycle_status=LifecycleStatus.AVAILABLE, owning_recruiter=recruiter,
    )
    return manager, coordinator, recruiter, project, other, person


def test_coordinator_schedules_trial_from_queue(client, operations):
    _manager, coordinator, _recruiter, project, _other, person = operations
    client.force_login(coordinator)
    response = client.post(reverse("trial_create"), {
        "person": person.pk, "project": project.pk,
        "scheduled_for": "2026-08-01T08:30", "note": "Gate two",
    })
    assert response.status_code == 302
    trial = TrialAssignment.objects.get(person=person)
    assert trial.project == project and trial.note == "Gate two"
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.TRIAL_DAY


def test_coordinator_cannot_schedule_or_edit_other_project(client, operations):
    manager, coordinator, _recruiter, project, other, person = operations
    client.force_login(coordinator)
    response = client.post(reverse("trial_create"), {
        "person": person.pk, "project": other.pk,
        "scheduled_for": "2026-08-01T08:30", "note": "",
    })
    assert response.status_code == 400
    assert not TrialAssignment.objects.exists()

    client.force_login(manager)
    client.post(reverse("trial_create"), {
        "person": person.pk, "project": project.pk,
        "scheduled_for": "2026-08-01T08:30", "note": "",
    })
    trial = TrialAssignment.objects.get()
    client.force_login(coordinator)
    response = client.post(reverse("trial_edit", args=[trial.pk]), {
        "project": other.pk, "scheduled_for": "2026-08-02T09:00", "note": "moved",
    })
    assert response.status_code == 400
    trial.refresh_from_db()
    assert trial.project == project


def test_manager_edits_pending_trial_with_old_and_new_audit(client, operations):
    manager, _coordinator, _recruiter, project, other, person = operations
    client.force_login(manager)
    client.post(reverse("trial_create"), {
        "person": person.pk, "project": project.pk,
        "scheduled_for": "2026-08-01T08:30", "note": "old",
    })
    trial = TrialAssignment.objects.get()
    response = client.post(reverse("trial_edit", args=[trial.pk]), {
        "project": other.pk, "scheduled_for": "2026-08-02T09:00", "note": "new",
    })
    assert response.status_code == 302
    trial.refresh_from_db()
    assert trial.project == other and trial.note == "new"
    event = AuditEvent.objects.get(action="trial.updated")
    assert event.metadata["old"]["project"] == "DHL"
    assert event.metadata["new"]["project"] == "OTHER"


def test_manager_creates_location_and_room_but_coordinator_cannot(client, operations):
    manager, coordinator, _recruiter, _project, _other, _person = operations
    client.force_login(coordinator)
    assert client.get(reverse("accommodation_create")).status_code == 403

    client.force_login(manager)
    response = client.post(reverse("accommodation_create"), {
        "name": "Residence East", "address": "Nitra 2", "notes": "Night desk",
        "is_active": "on",
    })
    assert response.status_code == 302
    accommodation = Accommodation.objects.get(name="Residence East")
    response = client.post(reverse("room_create", args=[accommodation.pk]), {
        "label": "201", "capacity": 2, "monthly_rate": "220.00", "is_active": "on",
    })
    assert response.status_code == 302
    assert Room.objects.filter(accommodation=accommodation, label="201").exists()

    client.force_login(coordinator)
    assert client.get(reverse("room_edit", args=[Room.objects.get().pk])).status_code == 403


def test_accommodation_create_with_capacity_and_cost_records_a_cost_period(client, operations):
    manager, *_ = operations
    client.force_login(manager)
    response = client.post(reverse("accommodation_create"), {
        "name": "Residence West", "address": "Nitra 3", "notes": "",
        "is_active": "on", "capacity": 10, "per_head_cost": "42.50",
    })
    assert response.status_code == 302
    accommodation = Accommodation.objects.get(name="Residence West")
    period = AccommodationCostPeriod.objects.get(accommodation=accommodation)
    assert period.capacity == 10
    assert str(period.per_head_cost) == "42.50"


def test_accommodation_create_rejects_only_one_of_capacity_or_cost(client, operations):
    manager, *_ = operations
    client.force_login(manager)
    response = client.post(reverse("accommodation_create"), {
        "name": "Residence Half-filled", "address": "", "notes": "",
        "is_active": "on", "capacity": 10,
    })
    assert response.status_code == 200
    assert not Accommodation.objects.filter(name="Residence Half-filled").exists()


def test_occupied_room_cannot_be_deactivated_or_shrunk(client, operations):
    manager, coordinator, _recruiter, _project, _other, person = operations
    accommodation = Accommodation.objects.create(name="Residence")
    room = Room.objects.create(accommodation=accommodation, label="101", capacity=2)
    assign_room(person, room, actor=coordinator)
    client.force_login(manager)
    response = client.post(reverse("room_edit", args=[room.pk]), {
        "label": "101", "capacity": 0, "monthly_rate": "100", "is_active": "",
    })
    assert response.status_code == 200
    room.refresh_from_db()
    assert room.capacity == 2 and room.is_active
    response = client.post(reverse("accommodation_edit", args=[accommodation.pk]), {
        "name": "Residence", "address": "", "notes": "", "is_active": "",
    })
    assert response.status_code == 200
    accommodation.refresh_from_db()
    assert accommodation.is_active
