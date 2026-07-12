from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone
from django.utils import translation

from core.people.models import LifecycleStatus, Person
from core.projects.models import (
    AssignmentStatus,
    PillarState,
    Project,
    TrialOutcome,
    TrialState,
)
from core.projects.services import (
    WorkflowError,
    activate_from_readiness,
    get_or_create_readiness,
    record_trial_outcome,
    schedule_trial,
    update_readiness,
)

# Jober-specific URLs/policies/languages — excluded from the corvinum lane.
pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


@pytest.fixture
def fixtures(django_user_model):
    actor = django_user_model.objects.create_user(
        email="c@demo.jober.test", password="x", role="coordinator"
    )
    project = Project.objects.create(name="DHL", code="DHLBA")
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    return actor, project, person


# --- trials ------------------------------------------------------------------

def test_schedule_sets_trial_day(fixtures):
    actor, project, person = fixtures
    scheduled_for = timezone.now() + timedelta(days=1)
    trial = schedule_trial(person, project, actor=actor, scheduled_for=scheduled_for)
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.TRIAL_DAY
    assert trial.outcome == TrialOutcome.PENDING
    assert trial.scheduled_for == scheduled_for


def test_schedule_requires_available(fixtures):
    actor, project, person = fixtures
    person.set_status(LifecycleStatus.INACTIVE, actor=actor)
    with pytest.raises(WorkflowError):
        schedule_trial(person, project, actor=actor)


@pytest.mark.parametrize("outcome", [TrialOutcome.FAIL, TrialOutcome.NO_SHOW])
def test_fail_or_no_show_recycles(fixtures, outcome):
    actor, project, person = fixtures
    trial = schedule_trial(person, project, actor=actor)
    record_trial_outcome(trial, outcome, actor=actor)
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.AVAILABLE


def test_pass_keeps_trial_day(fixtures):
    actor, project, person = fixtures
    trial = schedule_trial(person, project, actor=actor)
    record_trial_outcome(trial, TrialOutcome.PASS, actor=actor)
    person.refresh_from_db()
    trial.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.TRIAL_DAY
    assert trial.state == TrialState.COMPLETED


def test_second_trial_after_recycle_keeps_history(fixtures):
    actor, project, person = fixtures
    t1 = schedule_trial(person, project, actor=actor)
    record_trial_outcome(t1, TrialOutcome.FAIL, actor=actor)
    schedule_trial(person, project, actor=actor)
    assert person.trials.count() == 2


def test_outcome_recorded_twice_rejected(fixtures):
    actor, project, person = fixtures
    trial = schedule_trial(person, project, actor=actor)
    record_trial_outcome(trial, TrialOutcome.PASS, actor=actor)
    with pytest.raises(WorkflowError):
        record_trial_outcome(trial, TrialOutcome.FAIL, actor=actor)


# --- readiness + activation --------------------------------------------------

def test_readiness_ready_when_required_complete_optional_na(fixtures):
    actor, project, person = fixtures
    r = get_or_create_readiness(person, project)
    update_readiness(r, actor=actor, states={
        "medical": PillarState.COMPLETE, "gear": PillarState.COMPLETE,
        "accommodation": PillarState.NOT_APPLICABLE, "transport": PillarState.NOT_APPLICABLE,
    }, na_reasons={"accommodation": "private flat", "transport": "own car"})
    assert r.is_ready()


def test_na_requires_a_reason(fixtures):
    actor, project, person = fixtures
    r = get_or_create_readiness(person, project)
    with pytest.raises(WorkflowError):
        update_readiness(r, actor=actor, states={"transport": PillarState.NOT_APPLICABLE})


def test_entry_medical_date_is_saved(fixtures):
    actor, project, person = fixtures
    r = get_or_create_readiness(person, project)
    update_readiness(r, actor=actor, states={"medical": PillarState.COMPLETE}, entry_medical_date="2026-05-01")
    r.refresh_from_db()
    assert str(r.entry_medical_date) == "2026-05-01"


def test_future_entry_medical_date_is_rejected(fixtures):
    actor, project, person = fixtures
    r = get_or_create_readiness(person, project)
    with pytest.raises(WorkflowError):
        update_readiness(
            r, actor=actor, states={"medical": PillarState.COMPLETE},
            entry_medical_date=timezone.localdate() + timedelta(days=1),
        )


def test_medical_cannot_be_na(fixtures):
    actor, project, person = fixtures
    r = get_or_create_readiness(person, project)
    with pytest.raises(WorkflowError):
        update_readiness(r, actor=actor, states={"medical": PillarState.NOT_APPLICABLE})


def test_activation_blocked_until_ready(fixtures):
    actor, project, person = fixtures
    schedule_trial(person, project, actor=actor)
    trial = person.trials.first()
    record_trial_outcome(trial, TrialOutcome.PASS, actor=actor)
    with pytest.raises(WorkflowError):
        activate_from_readiness(person, project, actor=actor)


def test_activation_error_names_the_missing_readiness_requirement(fixtures):
    actor, project, person = fixtures
    trial = schedule_trial(person, project, actor=actor)
    record_trial_outcome(trial, TrialOutcome.PASS, actor=actor)
    get_or_create_readiness(person, project)

    with translation.override("hu"), pytest.raises(WorkflowError) as exc:
        activate_from_readiness(person, project, actor=actor)

    assert "orvosi alkalmasság" in str(exc.value).lower()


def test_not_applicable_without_a_reason_does_not_pass_readiness(fixtures):
    _actor, project, person = fixtures
    readiness = get_or_create_readiness(person, project)
    readiness.medical_state = PillarState.COMPLETE
    readiness.gear_state = PillarState.COMPLETE
    readiness.accommodation_state = PillarState.NOT_APPLICABLE
    readiness.transport_state = PillarState.COMPLETE
    readiness.save()
    assert not readiness.is_ready()


def test_full_path_to_working(fixtures):
    actor, project, person = fixtures
    # intake-available -> trial -> pass -> readiness -> activate
    trial = schedule_trial(person, project, actor=actor)
    record_trial_outcome(trial, TrialOutcome.PASS, actor=actor)
    r = get_or_create_readiness(person, project)
    update_readiness(r, actor=actor, states={
        "medical": PillarState.COMPLETE, "gear": PillarState.COMPLETE,
        "accommodation": PillarState.COMPLETE, "transport": PillarState.NOT_APPLICABLE,
    }, na_reasons={"transport": "own car"})
    activate_from_readiness(person, project, actor=actor)
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.WORKING
    assert person.assignments.filter(status=AssignmentStatus.ACTIVE).count() == 1
