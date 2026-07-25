from __future__ import annotations

import pytest
from django.urls import reverse

from core.offices.models import Office
from core.projects.models import Project
from features.logistics.forms import assignable_rooms, transport_projects
from features.logistics.models import Accommodation, Room

pytestmark = pytest.mark.django_db


@pytest.fixture
def two_offices(django_user_model):
    velky_meder = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")

    manager = django_user_model.objects.create_user(
        email="mgr@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([velky_meder])
    observer = django_user_model.objects.create_user(
        email="obs@demo.jober.test", password="x", role="observer"
    )

    a_vm = Accommodation.objects.create(name="VM House", office=velky_meder)
    a_gyr = Accommodation.objects.create(name="Győr House", office=gyor)
    return {
        "velky_meder": velky_meder,
        "gyor": gyor,
        "manager": manager,
        "observer": observer,
        "a_vm": a_vm,
        "a_gyr": a_gyr,
    }


# --- accommodation (HTTP) - accommodation feature is Jober-only (off for
# CorvinumEU per "rejected in interview" - clients/corvinum_eu/settings.py),
# so these routes don't exist there at all; no CorvinumEU-lane case applies.


@pytest.mark.jober_only
def test_accommodation_list_hides_other_offices_accommodation(client, two_offices):
    client.force_login(two_offices["manager"])
    body = client.get(reverse("accommodation_list")).content.decode()
    assert "VM House" in body
    assert "Győr House" not in body


@pytest.mark.jober_only
def test_accommodation_list_observer_sees_all_offices(client, two_offices):
    client.force_login(two_offices["observer"])
    body = client.get(reverse("accommodation_list")).content.decode()
    assert "VM House" in body
    assert "Győr House" in body


@pytest.mark.jober_only
def test_manager_cannot_view_another_offices_accommodation_detail(client, two_offices):
    client.force_login(two_offices["manager"])
    resp = client.get(reverse("accommodation_detail", args=[two_offices["a_gyr"].pk]))
    assert resp.status_code == 403


@pytest.mark.jober_only
def test_manager_can_view_their_own_offices_accommodation_detail(client, two_offices):
    client.force_login(two_offices["manager"])
    resp = client.get(reverse("accommodation_detail", args=[two_offices["a_vm"].pk]))
    assert resp.status_code == 200


@pytest.mark.jober_only
def test_observer_can_view_any_offices_accommodation_detail(client, two_offices):
    client.force_login(two_offices["observer"])
    resp = client.get(reverse("accommodation_detail", args=[two_offices["a_gyr"].pk]))
    assert resp.status_code == 200


@pytest.mark.jober_only
def test_manager_cannot_edit_another_offices_accommodation(client, two_offices):
    client.force_login(two_offices["manager"])
    resp = client.post(
        reverse("accommodation_edit", args=[two_offices["a_gyr"].pk]),
        {"name": "Hacked", "address": "", "is_active": True},
    )
    assert resp.status_code == 403


@pytest.mark.jober_only
def test_occupancy_tile_counts_only_the_managers_own_office(two_offices, rf):
    """An aggregate over another office's rooms is still a read of their
    accommodation data. Caught by a post-implementation sweep, not by the
    original slice - the tile had no office reference at all.

    Belongs in this Jober-only group rather than with the pure functions
    below: occupancy_tile is flag-gated on `accommodation` and returns None
    for CorvinumEU, so it is not client-agnostic the way
    transport_projects/assignable_rooms are.
    """
    from features.logistics.models import RoomAssignment, RoomAssignmentStatus
    from features.logistics.panels import occupancy_tile
    from core.people.models import Person

    vm_room = Room.objects.create(
        accommodation=two_offices["a_vm"],
        label="101",
        capacity=2,
        monthly_rate="100.00",
    )
    Room.objects.create(
        accommodation=two_offices["a_gyr"],
        label="201",
        capacity=9,
        monthly_rate="100.00",
    )
    person = Person.objects.create(first_name="Olha", last_name="VM")
    RoomAssignment.objects.create(
        person=person, room=vm_room, status=RoomAssignmentStatus.ACTIVE
    )

    request = rf.get("/")
    request.user = two_offices["manager"]
    assert occupancy_tile(request)["value"] == "1/2"  # not 1/11

    request.user = two_offices["observer"]
    assert occupancy_tile(request)["value"] == "1/11"


# --- transport_projects() / assignable_rooms() - pure functions, no HTTP, so
# these run under both clients regardless of whether the transport/
# accommodation *pages* are routable there, and give real CorvinumEU-lane
# coverage of the underlying scoping logic.


def test_transport_projects_excludes_other_office_for_manager(two_offices):
    p_vm = Project.objects.create(
        name="VM Project", code="VMPROJ", office=two_offices["velky_meder"]
    )
    Project.objects.create(
        name="Győr Project", code="GYRPROJ", office=two_offices["gyor"]
    )
    projects = transport_projects(two_offices["manager"])
    assert list(projects) == [p_vm]


def test_transport_projects_returns_all_for_observer(two_offices):
    p_vm = Project.objects.create(
        name="VM Project", code="VMPROJ", office=two_offices["velky_meder"]
    )
    p_gyr = Project.objects.create(
        name="Győr Project", code="GYRPROJ", office=two_offices["gyor"]
    )
    projects = transport_projects(two_offices["observer"])
    assert set(projects) == {p_vm, p_gyr}


def test_transport_projects_unaffected_when_no_offices_exist(django_user_model):
    manager = django_user_model.objects.create_user(
        email="mgr@demo.corvinum.test", password="x", role="manager"
    )
    project = Project.objects.create(name="No Office Project", code="NOOFF")
    assert list(transport_projects(manager)) == [project]


def test_assignable_rooms_excludes_other_offices_room_for_manager(two_offices):
    vm_room = Room.objects.create(
        accommodation=two_offices["a_vm"],
        label="101",
        capacity=2,
        monthly_rate="100.00",
    )
    Room.objects.create(
        accommodation=two_offices["a_gyr"],
        label="201",
        capacity=2,
        monthly_rate="100.00",
    )
    rooms = assignable_rooms(two_offices["manager"])
    assert list(rooms) == [vm_room]


def test_assignable_rooms_returns_all_for_observer(two_offices):
    vm_room = Room.objects.create(
        accommodation=two_offices["a_vm"],
        label="101",
        capacity=2,
        monthly_rate="100.00",
    )
    gyr_room = Room.objects.create(
        accommodation=two_offices["a_gyr"],
        label="201",
        capacity=2,
        monthly_rate="100.00",
    )
    rooms = assignable_rooms(two_offices["observer"])
    assert set(rooms) == {vm_room, gyr_room}


def test_assignable_rooms_unaffected_when_no_offices_exist(django_user_model):
    manager = django_user_model.objects.create_user(
        email="mgr@demo.corvinum.test", password="x", role="manager"
    )
    accommodation = Accommodation.objects.create(name="No Office House")
    room = Room.objects.create(
        accommodation=accommodation, label="1", capacity=2, monthly_rate="100.00"
    )
    assert list(assignable_rooms(manager)) == [room]
