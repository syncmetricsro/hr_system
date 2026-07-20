from __future__ import annotations

import pytest
from datetime import date
from decimal import Decimal
from uuid import uuid4
from django.urls import reverse
from django.utils import translation

from features.logistics.models import Accommodation, EquipmentIssueStatus, EquipmentItem, Room, RoomAssignmentStatus
from features.logistics.services import assign_room, issue_equipment, receive_stock
from core.people.models import LifecycleStatus, Person
from core.projects.models import AssignmentStatus, Project
from core.projects.services import activate_on_project, exit_person

# Jober-specific URLs/policies/languages — excluded from the corvinum lane.
pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


@pytest.fixture
def staffed(django_user_model):
    coord = django_user_model.objects.create_user(email="c@demo.jober.test", password="x", role="coordinator")
    project = Project.objects.create(name="DHL", code="DHLBA")
    person = Person.objects.create(first_name="Olha", last_name="K")
    activate_on_project(person, project, actor=coord)  # WORKING + active assignment
    room = Room.objects.create(accommodation=Accommodation.objects.create(name="Dom"), label="1", capacity=2)
    assign_room(person, room, actor=coord)
    item = EquipmentItem.objects.create(name="Boots")
    receive_stock(
        received_on=date.today(), operation_key=uuid4(),
        lines=[{"item": item, "quantity": 1, "total_value": Decimal("10")}],
        actor=coord,
    )
    issue_equipment(person, item, actor=coord, operation_key=uuid4())
    return coord, person


def test_exit_reconciles_everything_and_recycles(staffed):
    coord, person = staffed
    exit_person(person, actor=coord, reason="end of contract")
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.AVAILABLE
    assert person.assignments.filter(status=AssignmentStatus.ACTIVE).count() == 0
    assert person.room_assignments.filter(status=RoomAssignmentStatus.ACTIVE).count() == 0
    # Stock-tracked custody stays open until the item is physically returned.
    assert person.equipment_issues.filter(status=EquipmentIssueStatus.ISSUED).count() == 1


def test_exit_to_inactive(staffed):
    coord, person = staffed
    exit_person(person, actor=coord, outcome="inactive")
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.INACTIVE


def test_exit_view_denied_for_recruiter(client, django_user_model, staffed):
    recruiter = django_user_model.objects.create_user(email="r@demo.jober.test", password="x", role="recruiter")
    _coord, person = staffed
    client.force_login(recruiter)
    assert client.post(reverse("exit_person", args=[person.pk])).status_code == 403


def test_exit_view_works_for_coordinator(client, staffed):
    coord, person = staffed
    client.force_login(coord)
    resp = client.post(reverse("exit_person", args=[person.pk]), {"outcome": "available"})
    assert resp.status_code == 302
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.AVAILABLE


def test_exit_actions_describe_their_effect_before_submit(client, staffed):
    coord, person = staffed
    client.force_login(coord)
    with translation.override("en"):
        exit_url = reverse("exit_person", args=[person.pk])
        body = client.get(reverse("person_detail", args=[person.pk])).content.decode("utf-8")

    assert body.count(f'action="{exit_url}"') == 2
    assert "data-confirm=" in body
    assert "sets the person to Available" in body
    assert "sets the person to Inactive with the chosen reason" in body
