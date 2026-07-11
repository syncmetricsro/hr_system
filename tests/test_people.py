from __future__ import annotations

import pytest

from core.accounts.permissions import Action, can
from core.audit.models import AuditEvent
from core.people.models import LifecycleError, LifecycleStatus, Person
from core.people.permissions import can_view_sensitive
from core.projects.models import AssignmentStatus, Project, ProjectAssignment
from core.projects.services import activate_on_project, end_assignment

pytestmark = pytest.mark.django_db


@pytest.fixture
def users(django_user_model):
    def make(role):
        return django_user_model.objects.create_user(
            email=f"{role}@demo.jober.test", password="x", role=role
        )

    return {
        "recruiter": make("recruiter"),
        "recruiter2": django_user_model.objects.create_user(
            email="recruiter2@demo.jober.test", password="x", role="recruiter"
        ),
        "coordinator": make("coordinator"),
        "coordinator2": django_user_model.objects.create_user(
            email="coordinator2@demo.jober.test", password="x", role="coordinator"
        ),
        "manager": make("manager"),
        "observer": make("observer"),
    }


@pytest.fixture
def person(users):
    return Person.objects.create(
        first_name="Olha", last_name="Kovalenko", owning_recruiter=users["recruiter"]
    )


# --- lifecycle ---------------------------------------------------------------

def test_search_name_is_normalized(person):
    assert person.search_name == "olha kovalenko"


@pytest.mark.jober_only  # Jober grants/lifecycle/features
def test_valid_transition_is_audited(person, users):
    person.set_status(LifecycleStatus.TRIAL_DAY, actor=users["recruiter"], reason="trial")
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.TRIAL_DAY
    event = AuditEvent.objects.get(action="person.lifecycle_changed")
    assert event.metadata["from_status"] == LifecycleStatus.AVAILABLE
    assert event.metadata["to_status"] == LifecycleStatus.TRIAL_DAY


def test_invalid_transition_raises(person, users):
    person.set_status(LifecycleStatus.WORKING, actor=users["manager"])
    with pytest.raises(LifecycleError):
        person.set_status(LifecycleStatus.TRIAL_DAY, actor=users["manager"])


# --- assignments -------------------------------------------------------------

def test_activation_creates_active_assignment_and_sets_working(person, users):
    project = Project.objects.create(name="DHL", code="DHLBA")
    activate_on_project(person, project, actor=users["coordinator"])
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.WORKING
    assert person.assignments.filter(status=AssignmentStatus.ACTIVE).count() == 1


def test_reassignment_keeps_one_active_and_retains_history(person, users):
    p1 = Project.objects.create(name="DHL", code="DHLBA")
    p2 = Project.objects.create(name="WEBASTO", code="WEB")
    activate_on_project(person, p1, actor=users["coordinator"])
    activate_on_project(person, p2, actor=users["coordinator"])
    assert person.assignments.filter(status=AssignmentStatus.ACTIVE).count() == 1
    assert person.assignments.count() == 2  # history retained
    assert person.current_assignment().project == p2


def test_duplicate_active_assignment_is_rejected_by_constraint(person):
    from django.db import IntegrityError

    p1 = Project.objects.create(name="DHL", code="DHLBA")
    p2 = Project.objects.create(name="WEBASTO", code="WEB")
    ProjectAssignment.objects.create(person=person, project=p1, status=AssignmentStatus.ACTIVE)
    with pytest.raises(IntegrityError):
        ProjectAssignment.objects.create(person=person, project=p2, status=AssignmentStatus.ACTIVE)


def test_end_assignment_returns_to_available(person, users):
    project = Project.objects.create(name="DHL", code="DHLBA")
    activate_on_project(person, project, actor=users["coordinator"])
    end_assignment(person, actor=users["coordinator"], reason="exit")
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.AVAILABLE
    assert person.assignments.filter(status=AssignmentStatus.ACTIVE).count() == 0


# --- sensitive-field visibility (Q4) -----------------------------------------

def test_sensitive_visible_to_oversight_and_owner(person, users):
    assert can_view_sensitive(users["manager"], person)
    assert can_view_sensitive(users["observer"], person)
    assert can_view_sensitive(users["recruiter"], person)         # owning recruiter
    assert not can_view_sensitive(users["recruiter2"], person)    # other recruiter


def test_sensitive_visible_to_responsible_coordinator_only(person, users):
    project = Project.objects.create(name="DHL", code="DHLBA")
    project.responsible_coordinators.add(users["coordinator"])
    activate_on_project(person, project, actor=users["coordinator"])
    assert can_view_sensitive(users["coordinator"], person)       # responsible
    assert not can_view_sensitive(users["coordinator2"], person)  # unrelated coordinator


# --- placement RBAC ----------------------------------------------------------

def test_project_assign_action_roles(users):
    assert can(users["coordinator"], Action.PROJECT_ASSIGN)
    assert can(users["manager"], Action.PROJECT_ASSIGN)
    assert not can(users["recruiter"], Action.PROJECT_ASSIGN)
    assert not can(users["observer"], Action.PROJECT_ASSIGN)
