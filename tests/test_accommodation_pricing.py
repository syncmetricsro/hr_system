from __future__ import annotations

from decimal import Decimal

import pytest
from django.urls import reverse

from apps.accounts.permissions import Action, can
from apps.logistics.models import Accommodation, Room
from apps.logistics.services import (
    accommodation_cost_report,
    assign_room,
    set_assignment_rate,
    set_room_rate,
)
from apps.people.models import Person

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup(django_user_model):
    manager = django_user_model.objects.create_user(
        email="m@demo.jober.test", password="x", role="manager"
    )
    coord = django_user_model.objects.create_user(
        email="c@demo.jober.test", password="x", role="coordinator"
    )
    acc = Accommodation.objects.create(name="Ubytovňa Nitra")
    room = Room.objects.create(accommodation=acc, label="101", capacity=2)
    return manager, coord, acc, room


def test_set_room_rate(setup):
    manager, _coord, _acc, room = setup
    set_room_rate(room, "180.00", actor=manager)
    room.refresh_from_db()
    assert room.monthly_rate == Decimal("180.00")


def test_effective_rate_uses_override_then_room(setup):
    manager, coord, _acc, room = setup
    set_room_rate(room, "180", actor=manager)
    person = Person.objects.create(first_name="A", last_name="B")
    assignment = assign_room(person, room, actor=coord)
    assert assignment.effective_rate == Decimal("180")  # falls back to room rate
    set_assignment_rate(assignment, "120", actor=manager)
    assert assignment.effective_rate == Decimal("120")  # override wins
    set_assignment_rate(assignment, "", actor=manager)  # clear
    assert assignment.rate_override is None
    assert assignment.effective_rate == Decimal("180")


def test_cost_report_room_and_assigned_totals(setup):
    manager, coord, acc, room = setup
    room2 = Room.objects.create(accommodation=acc, label="102", capacity=2, monthly_rate=Decimal("200"))
    set_room_rate(room, "180", actor=manager)
    p1 = Person.objects.create(first_name="A", last_name="B")
    p2 = Person.objects.create(first_name="C", last_name="D")
    assign_room(p1, room, actor=coord)                       # effective 180
    a2 = assign_room(p2, room2, actor=coord)
    set_assignment_rate(a2, "150", actor=manager)            # override 150 (room is 200)

    report = accommodation_cost_report()
    row = report["rows"][0]
    assert row["room_cost"] == Decimal("380")     # 180 + 200 (standing, all rooms)
    assert row["assigned_cost"] == Decimal("330")  # 180 + 150 (override) over 2 active
    assert row["occupancy"] == 2
    assert report["company"]["room_cost"] == Decimal("380")
    assert report["company"]["assigned_cost"] == Decimal("330")


def test_cost_report_ignores_released_assignments(setup):
    manager, coord, _acc, room = setup
    set_room_rate(room, "180", actor=manager)
    person = Person.objects.create(first_name="A", last_name="B")
    assign_room(person, room, actor=coord)
    from apps.logistics.services import release_room
    release_room(person, actor=coord)
    report = accommodation_cost_report()
    assert report["company"]["occupancy"] == 0
    assert report["company"]["assigned_cost"] == Decimal("0")
    assert report["company"]["room_cost"] == Decimal("180")  # standing cost remains


def test_rate_rbac(setup):
    manager, coord, _acc, _room = setup
    assert can(manager, Action.ACCOMMODATION_MANAGE)
    assert not can(coord, Action.ACCOMMODATION_MANAGE)


def test_costs_view_gated_to_manager(client, setup, django_user_model):
    manager, coord, _acc, _room = setup
    recruiter = django_user_model.objects.create_user(
        email="r@demo.jober.test", password="x", role="recruiter"
    )
    url = reverse("accommodation_costs")

    client.force_login(recruiter)
    assert client.get(url).status_code == 403
    client.force_login(coord)
    assert client.get(url).status_code == 403
    client.force_login(manager)
    assert client.get(url).status_code == 200


def test_set_room_rate_view_persists(client, setup):
    manager, _coord, _acc, room = setup
    client.force_login(manager)
    resp = client.post(reverse("set_room_rate", kwargs={"pk": room.pk}), {"monthly_rate": "199.50"})
    assert resp.status_code == 302
    room.refresh_from_db()
    assert room.monthly_rate == Decimal("199.50")
