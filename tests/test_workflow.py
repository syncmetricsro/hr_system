from __future__ import annotations

import pytest

from apps.people.models import LifecycleStatus, Person
from apps.projects.models import (
    AssignmentStatus,
    PillarState,
    Project,
    TrialOutcome,
    TrialState,
)
from apps.projects.services import (
    WorkflowError,
    activate_from_readiness,
    get_or_create_readiness,
    record_trial_outcome,
    schedule_trial,
    update_readiness,
)

pytestmark = pytest.mark.django_db


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
    trial = schedule_trial(person, project, actor=actor)
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.TRIAL_DAY
    assert trial.outcome == TrialOutcome.PENDING


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
    })
    assert r.is_ready()


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


def test_full_path_to_working(fixtures):
    actor, project, person = fixtures
    # intake-available -> trial -> pass -> readiness -> activate
    trial = schedule_trial(person, project, actor=actor)
    record_trial_outcome(trial, TrialOutcome.PASS, actor=actor)
    r = get_or_create_readiness(person, project)
    update_readiness(r, actor=actor, states={
        "medical": PillarState.COMPLETE, "gear": PillarState.COMPLETE,
        "accommodation": PillarState.COMPLETE, "transport": PillarState.NOT_APPLICABLE,
    })
    activate_from_readiness(person, project, actor=actor)
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.WORKING
    assert person.assignments.filter(status=AssignmentStatus.ACTIVE).count() == 1
