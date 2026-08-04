"""Activating a known worker without a trial day (ADR 0031).

The trial day is the right default for a stranger and a detour for a worker the
office already knows. Nothing in the services ever required one — readiness and
activation never referenced ``Trial`` — so the requirement was purely the shape
of the person page, which only opened readiness after a trial passed.

What is waived is the **trial**, not readiness. The four pillars still gate
activation, so the entry medical certificate is still recorded. These tests
exist mostly to keep that distinction from eroding.
"""

from __future__ import annotations

import pytest
from django.urls import reverse

from core.accounts.models import Role
from core.offices.models import Office
from core.people.models import LifecycleStatus, Person
from core.projects.models import (
    AssignmentStatus,
    PillarState,
    Project,
    ReadinessRecord,
    TrialAssignment,
)
from core.projects.services import (
    WorkflowError,
    decide_activation,
    exit_person,
    request_activation,
    update_readiness,
    waive_trial,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def world(django_user_model):
    vm = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")

    def user(email, role, office):
        u = django_user_model.objects.create_user(email=email, password="x", role=role)
        u.offices.set([office])
        return u

    manager = user("waive-mgr@demo.jober.test", Role.MANAGER, vm)
    coordinator = user("waive-coord@demo.jober.test", Role.COORDINATOR, vm)
    gyor_manager = user("waive-mgr.gyor@demo.jober.test", Role.MANAGER, gyor)

    project = Project.objects.create(name="DHL", code="DHLW", office=vm, is_active=True)
    gyor_project = Project.objects.create(
        name="Audi", code="AUDIW", office=gyor, is_active=True
    )
    person = Person.objects.create(
        first_name="Mykola",
        last_name="P",
        office=vm,
        lifecycle_status=LifecycleStatus.AVAILABLE,
    )
    return {
        "manager": manager,
        "coordinator": coordinator,
        "gyor_manager": gyor_manager,
        "project": project,
        "gyor_project": gyor_project,
        "person": person,
    }


def _complete_pillars(readiness, actor):
    update_readiness(
        readiness,
        actor=actor,
        states={
            "medical": PillarState.COMPLETE,
            "gear": PillarState.COMPLETE,
            "accommodation": PillarState.COMPLETE,
            "transport": PillarState.NOT_APPLICABLE,
        },
        na_reasons={"transport": "own car"},
    )


# --- the whole point -------------------------------------------------------


def test_a_manager_activates_without_any_trial(world):
    """The full route, end to end, by one person: waive, complete readiness,
    request, approve. Both halves of ADR 0031 are needed for this to pass."""
    person, project, manager = world["person"], world["project"], world["manager"]

    readiness = waive_trial(person, project, actor=manager)
    _complete_pillars(readiness, manager)
    approval = request_activation(person, project, actor=manager)
    decide_activation(approval, "approve", actor=manager)

    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.WORKING
    assert person.assignments.filter(
        status=AssignmentStatus.ACTIVE, project=project
    ).exists()
    # No trial was invented along the way — the lifecycle should not claim one.
    assert not TrialAssignment.objects.filter(person=person).exists()


def test_readiness_still_gates_a_waived_activation(world):
    """The waiver skips the trial, not the four pillars. Medical clearance is a
    legal requirement, and it would be a quiet thing to lose here."""
    person, project, manager = world["person"], world["project"], world["manager"]
    readiness = waive_trial(person, project, actor=manager)
    update_readiness(
        readiness,
        actor=manager,
        states={
            "medical": PillarState.INCOMPLETE,
            "gear": PillarState.COMPLETE,
            "accommodation": PillarState.COMPLETE,
            "transport": PillarState.NOT_APPLICABLE,
        },
        na_reasons={"transport": "own car"},
    )

    with pytest.raises(WorkflowError):
        request_activation(person, project, actor=manager)


def test_the_person_stays_available_until_the_decision(world):
    """Waiving opens readiness; it does not deploy anybody."""
    person = world["person"]
    waive_trial(person, world["project"], actor=world["manager"])

    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.AVAILABLE


def test_waiving_is_refused_for_a_person_who_is_not_available(world):
    person, project, manager = world["person"], world["project"], world["manager"]
    readiness = waive_trial(person, project, actor=manager)
    _complete_pillars(readiness, manager)
    decide_activation(
        request_activation(person, project, actor=manager), "approve", actor=manager
    )
    person.refresh_from_db()

    with pytest.raises(WorkflowError):
        waive_trial(person, project, actor=manager)


# --- the waiver is spent once used -----------------------------------------


def test_exiting_clears_the_waiver(world):
    """A worker recycled to Available must not land back in readiness on a
    record describing work they have already finished."""
    person, project, manager = world["person"], world["project"], world["manager"]
    readiness = waive_trial(person, project, actor=manager)
    _complete_pillars(readiness, manager)
    decide_activation(
        request_activation(person, project, actor=manager), "approve", actor=manager
    )

    exit_person(person, actor=manager, reason="contract ended")

    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.AVAILABLE
    assert not ReadinessRecord.objects.filter(person=person, trial_waived=True).exists()


# --- who may do it ---------------------------------------------------------


@pytest.mark.jober_only
def test_a_coordinator_cannot_waive_the_trial(client, world):
    """Manager-only. The button being hidden is presentation, not a control."""
    client.force_login(world["coordinator"])
    response = client.post(
        reverse("readiness_waive_trial", args=[world["person"].pk]),
        {"project": world["project"].pk},
    )

    assert response.status_code == 403
    assert not ReadinessRecord.objects.filter(person=world["person"]).exists()


@pytest.mark.jober_only
def test_a_manager_cannot_waive_into_another_office(client, world):
    """Office scoping (ADR 0026) applies to both sides: this manager may not
    reach the Győr project even though they hold the action."""
    client.force_login(world["manager"])
    response = client.post(
        reverse("readiness_waive_trial", args=[world["person"].pk]),
        {"project": world["gyor_project"].pk},
    )

    assert response.status_code == 403
    assert not ReadinessRecord.objects.filter(person=world["person"]).exists()


@pytest.mark.jober_only
def test_a_manager_cannot_waive_another_offices_person(client, world):
    person = Person.objects.create(
        first_name="Béla",
        last_name="T",
        office=Office.objects.get(code="GYR"),
        lifecycle_status=LifecycleStatus.AVAILABLE,
    )
    client.force_login(world["manager"])
    response = client.post(
        reverse("readiness_waive_trial", args=[person.pk]),
        {"project": world["project"].pk},
    )

    assert response.status_code == 403


# --- what the person page shows --------------------------------------------


@pytest.mark.jober_only
def test_the_readiness_panel_opens_for_an_available_waived_person(client, world):
    """The trial requirement was only ever this template condition."""
    client.force_login(world["manager"])
    detail = reverse("person_detail", args=[world["person"].pk])

    before = client.get(detail)
    assert b'name="medical"' not in before.content

    client.post(
        reverse("readiness_waive_trial", args=[world["person"].pk]),
        {"project": world["project"].pk},
    )

    after = client.get(detail)
    assert b'name="medical"' in after.content
