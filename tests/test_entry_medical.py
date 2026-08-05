"""Recording an entry medical date, before and after activation.

From a live report: a worker showed "Medical — missing" on Compliance and the
alert could not be cleared. Their readiness said `medical_state = complete` with
`entry_medical_date = None`, because activation only ever checked the pillar
*state* while the compliance alert reads the *date*.

Two holes, and the second is the one everybody eventually falls into:

* a worker could be activated with Medical ticked and no date, straight into an
  alert;
* readiness is only editable on the way in, so once someone is Working there was
  no screen anywhere that set this field - and `MEDICAL_VALIDITY_MONTHS` is 12,
  so every worker needs a renewal recorded sooner or later.
"""

from __future__ import annotations

import datetime as dt

import pytest
from django.urls import reverse
from django.utils import translation

from core.accounts.models import Role
from core.audit.models import AuditEvent
from core.offices.models import Office
from core.people.models import LifecycleStatus, Person
from core.projects.models import PillarState, Project, ReadinessRecord
from core.projects.services import (
    WorkflowError,
    activate_on_project,
    get_or_create_readiness,
    medical_expiry,
    readiness_blockers,
    record_entry_medical,
    update_readiness,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def world(django_user_model):
    office = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    manager = django_user_model.objects.create_user(
        email="med-mgr@demo.test", password="x", role=Role.MANAGER
    )
    manager.offices.set([office])
    project = Project.objects.create(
        name="DHL", code="DHLMED", office=office, is_active=True
    )
    person = Person.objects.create(
        first_name="Olena",
        last_name="K",
        office=office,
        lifecycle_status=LifecycleStatus.AVAILABLE,
    )
    return {"manager": manager, "project": project, "person": person}


def _complete(readiness, actor, *, medical_date):
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
        entry_medical_date=medical_date,
    )


# --- closing the source ----------------------------------------------------


def test_medical_cannot_be_marked_complete_without_a_date(world):
    """The inconsistency that produced the live alert: a tick with no date
    passed activation and then could never be cleared."""
    readiness = get_or_create_readiness(world["person"], world["project"])

    # Suites run under the Slovak default locale, so an English regex only
    # matches inside an explicit override (CLAUDE.md gotcha).
    with (
        translation.override("en"),
        pytest.raises(WorkflowError, match="entry medical date"),
    ):
        update_readiness(
            readiness,
            actor=world["manager"],
            states={
                "medical": PillarState.COMPLETE,
                "gear": PillarState.COMPLETE,
                "accommodation": PillarState.COMPLETE,
                "transport": PillarState.NOT_APPLICABLE,
            },
            na_reasons={"transport": "own car"},
        )

    readiness.refresh_from_db()
    assert readiness.entry_medical_date is None


def test_an_incomplete_medical_still_needs_no_date(world):
    """The rule is about claiming completeness, not about filling the form in
    one sitting. Saving a half-done readiness must stay possible."""
    readiness = get_or_create_readiness(world["person"], world["project"])

    update_readiness(
        readiness,
        actor=world["manager"],
        states={"medical": PillarState.INCOMPLETE, "gear": PillarState.COMPLETE},
    )

    readiness.refresh_from_db()
    assert readiness.medical_state == PillarState.INCOMPLETE


# --- the renewal path, which is why this exists ----------------------------


def test_a_working_person_can_have_a_medical_recorded(client, world):
    """The screen that did not exist. Everyone reaches this: the certificate is
    valid for 12 months, so a renewal always has to be recordable afterwards."""
    person, project, manager = world["person"], world["project"], world["manager"]
    readiness = get_or_create_readiness(person, project)
    _complete(readiness, manager, medical_date=dt.date(2025, 8, 1))
    activate_on_project(person, project, actor=manager)
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.WORKING

    client.force_login(manager)
    response = client.post(
        reverse("medical_record", args=[person.pk]),
        {"entry_medical_date": "2026-08-01"},
    )

    assert response.status_code == 302
    readiness.refresh_from_db()
    assert readiness.entry_medical_date == dt.date(2026, 8, 1)
    assert AuditEvent.objects.filter(action="readiness.entry_medical_recorded").exists()


def test_the_panel_is_offered_to_a_working_person(client, world):
    person, project, manager = world["person"], world["project"], world["manager"]
    _complete(
        get_or_create_readiness(person, project),
        manager,
        medical_date=dt.date(2026, 7, 1),
    )
    activate_on_project(person, project, actor=manager)
    client.force_login(manager)

    body = client.get(reverse("person_detail", args=[person.pk])).content.decode()

    assert reverse("medical_record", args=[person.pk]) in body


def test_a_future_medical_date_is_refused(world):
    person, project, manager = world["person"], world["project"], world["manager"]
    _complete(
        get_or_create_readiness(person, project),
        manager,
        medical_date=dt.date(2026, 7, 1),
    )
    activate_on_project(person, project, actor=manager)

    with pytest.raises(WorkflowError):
        record_entry_medical(
            person, project, dt.date.today() + dt.timedelta(days=1), actor=manager
        )


def test_recording_a_medical_touches_only_the_date(world):
    """It is not a back door into the activation workflow."""
    person, project, manager = world["person"], world["project"], world["manager"]
    readiness = get_or_create_readiness(person, project)
    _complete(readiness, manager, medical_date=dt.date(2026, 7, 1))
    activate_on_project(person, project, actor=manager)
    before = ReadinessRecord.objects.get(pk=readiness.pk)

    record_entry_medical(person, project, dt.date(2026, 7, 20), actor=manager)

    after = ReadinessRecord.objects.get(pk=readiness.pk)
    assert after.entry_medical_date == dt.date(2026, 7, 20)
    assert after.gear_state == before.gear_state
    assert after.accommodation_state == before.accommodation_state
    assert after.medical_state == before.medical_state


@pytest.mark.jober_only
def test_a_recruiter_cannot_record_a_medical(client, world, django_user_model):
    """Hiding the panel is presentation; the action is the control."""
    person, project, manager = world["person"], world["project"], world["manager"]
    _complete(
        get_or_create_readiness(person, project),
        manager,
        medical_date=dt.date(2026, 7, 1),
    )
    activate_on_project(person, project, actor=manager)

    recruiter = django_user_model.objects.create_user(
        email="med-rec@demo.test", password="x", role=Role.RECRUITER
    )
    recruiter.offices.set(list(Office.objects.all()))
    client.force_login(recruiter)

    response = client.post(
        reverse("medical_record", args=[person.pk]),
        {"entry_medical_date": "2026-08-01"},
    )
    assert response.status_code == 403


# --- and the date has to still be valid (2026-08-05) -----------------------
#
# The pillar says "we checked"; the date says when. A medical from three years
# ago used to tick, activate cleanly, and show as expired in Compliance one
# second later, with nothing having stopped it. Recording a date closed half
# the hole; this closes the other half.


def test_activation_is_refused_when_the_recorded_medical_has_expired(settings, world):
    settings.MEDICAL_VALIDITY_MONTHS = 12
    readiness = get_or_create_readiness(world["person"], world["project"])
    lapsed = dt.date.today() - dt.timedelta(days=400)
    _complete(readiness, world["manager"], medical_date=lapsed)

    blockers = readiness_blockers(readiness)

    assert [b for b in blockers if b["field"] == "entry_medical_date"], blockers
    with translation.override("en"):
        message = readiness_blockers(readiness)[0]["message"]
    # The date is the actionable part: an office told only "medical expired"
    # has to go looking for what it expired against.
    assert str(medical_expiry(readiness)) in message


def test_a_current_medical_activates_normally(settings, world):
    """The regression guard: this whole thread started with an alert nobody
    could clear, and over-correcting into a gate nobody can pass is worse."""
    settings.MEDICAL_VALIDITY_MONTHS = 12
    readiness = get_or_create_readiness(world["person"], world["project"])
    _complete(readiness, world["manager"], medical_date=dt.date.today())

    assert readiness_blockers(readiness) == []

    activate_on_project(world["person"], world["project"], actor=world["manager"])
    world["person"].refresh_from_db()
    assert world["person"].lifecycle_status == LifecycleStatus.WORKING


def test_an_expiring_medical_does_not_block_activation(settings, world):
    """Inside the window is inside the window. Compliance warns at 30 days;
    activation only refuses what has actually run out."""
    settings.MEDICAL_VALIDITY_MONTHS = 12
    readiness = get_or_create_readiness(world["person"], world["project"])
    nearly = dt.date.today() - dt.timedelta(days=350)
    _complete(readiness, world["manager"], medical_date=nearly)

    assert readiness_blockers(readiness) == []


def test_renewing_the_date_clears_the_activation_blocker(settings, world):
    settings.MEDICAL_VALIDITY_MONTHS = 12
    readiness = get_or_create_readiness(world["person"], world["project"])
    _complete(
        readiness,
        world["manager"],
        medical_date=dt.date.today() - dt.timedelta(days=400),
    )
    assert readiness_blockers(readiness)

    record_entry_medical(
        world["person"], world["project"], dt.date.today(), actor=world["manager"]
    )

    readiness.refresh_from_db()
    assert readiness_blockers(readiness) == []
