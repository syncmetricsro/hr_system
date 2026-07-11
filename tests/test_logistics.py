from __future__ import annotations

import pytest

from core.accounts.permissions import Action, can
from features.logistics.models import Accommodation, Room, RoomAssignmentStatus
from features.logistics.services import CapacityError, assign_room, release_room
from core.people.models import Person

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup(django_user_model):
    coord = django_user_model.objects.create_user(
        email="c@demo.jober.test", password="x", role="coordinator"
    )
    accommodation = Accommodation.objects.create(name="Ubytovňa")
    room = Room.objects.create(accommodation=accommodation, label="101", capacity=1)
    return coord, room


def test_assign_room_sets_active_and_occupancy(setup):
    coord, room = setup
    person = Person.objects.create(first_name="A", last_name="B")
    assignment = assign_room(person, room, actor=coord)
    assert assignment.status == RoomAssignmentStatus.ACTIVE
    assert room.occupancy() == 1
    assert room.is_full()


def test_capacity_is_enforced(setup):
    coord, room = setup
    p1 = Person.objects.create(first_name="A", last_name="B")
    p2 = Person.objects.create(first_name="C", last_name="D")
    assign_room(p1, room, actor=coord)
    with pytest.raises(CapacityError):
        assign_room(p2, room, actor=coord)


def test_reassign_keeps_one_active_room(setup):
    coord, room = setup
    room2 = Room.objects.create(accommodation=room.accommodation, label="102", capacity=2)
    person = Person.objects.create(first_name="A", last_name="B")
    assign_room(person, room, actor=coord)
    assign_room(person, room2, actor=coord)
    assert person.room_assignments.filter(status=RoomAssignmentStatus.ACTIVE).count() == 1
    assert room.occupancy() == 0
    assert room2.occupancy() == 1


def test_release_room(setup):
    coord, room = setup
    person = Person.objects.create(first_name="A", last_name="B")
    assign_room(person, room, actor=coord)
    release_room(person, actor=coord)
    assert room.occupancy() == 0


@pytest.mark.jober_only  # Jober grants/lifecycle/features
def test_room_assign_rbac(django_user_model):
    coord = django_user_model.objects.create_user(email="c2@demo.jober.test", password="x", role="coordinator")
    observer = django_user_model.objects.create_user(email="o@demo.jober.test", password="x", role="observer")
    assert can(coord, Action.ROOM_ASSIGN)
    assert not can(observer, Action.ROOM_ASSIGN)
