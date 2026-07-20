from __future__ import annotations

import pytest
from django.urls import reverse

from features.logistics.models import EquipmentItem, EquipmentIssue
from core.people.models import LifecycleStatus, Person
from core.projects.models import Project, TrialAssignment

# Jober-specific URLs/policies/languages — excluded from the corvinum lane.
pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


@pytest.fixture
def users(django_user_model):
    def make(role):
        return django_user_model.objects.create_user(
            email=f"{role}@demo.jober.test", password="x", role=role
        )
    return {r: make(r) for r in ("recruiter", "coordinator", "manager", "observer")}


@pytest.fixture
def objs(users):
    person = Person.objects.create(first_name="A", last_name="B", lifecycle_status=LifecycleStatus.TRIAL_DAY)
    project = Project.objects.create(name="DHL", code="DHLBA")
    trial = TrialAssignment.objects.create(person=person, project=project)
    item = EquipmentItem.objects.create(name="Boots")
    issue = EquipmentIssue.objects.create(person=person, item=item)
    return {"person": person, "project": project, "trial": trial, "issue": issue}


# (url_name, kwargs_fn, method, role_that_must_be_denied)
CASES = [
    ("assign_trial", lambda o: {"person_pk": o["person"].pk}, "post", "observer"),
    ("trial_outcome", lambda o: {"trial_pk": o["trial"].pk}, "post", "recruiter"),
    ("readiness_update", lambda o: {"person_pk": o["person"].pk}, "post", "recruiter"),
    ("activate_person", lambda o: {"person_pk": o["person"].pk}, "post", "recruiter"),
    ("assign_room", lambda o: {"person_pk": o["person"].pk}, "post", "observer"),
    ("issue_equipment", lambda o: {"person_pk": o["person"].pk}, "post", "observer"),
    ("return_equipment", lambda o: {"issue_pk": o["issue"].pk}, "post", "observer"),
    ("finance_record", lambda o: {}, "post", "observer"),
    ("finance_summary", lambda o: {}, "get", "recruiter"),
    ("intake_start", lambda o: {}, "get", "observer"),
]


@pytest.mark.parametrize("url_name,kwargs_fn,method,denied_role", CASES)
def test_denied_role_gets_403(client, users, objs, url_name, kwargs_fn, method, denied_role):
    client.force_login(users[denied_role])
    url = reverse(url_name, kwargs=kwargs_fn(objs))
    response = getattr(client, method)(url)
    assert response.status_code == 403


@pytest.mark.parametrize("url_name,kwargs_fn,method,denied_role", CASES)
def test_anonymous_is_redirected(client, objs, url_name, kwargs_fn, method, denied_role):
    url = reverse(url_name, kwargs=kwargs_fn(objs))
    response = getattr(client, method)(url)
    assert response.status_code == 302
    assert reverse("login") in response.headers["Location"]


@pytest.mark.parametrize("role", ("recruiter", "coordinator", "manager"))
def test_authorized_roles_can_schedule_a_trial(client, users, role):
    person = Person.objects.create(first_name="Available", last_name="Person")
    project = Project.objects.create(name="DHL", code=f"DHL-{role}")
    if role == "coordinator":
        project.responsible_coordinators.add(users[role])
    client.force_login(users[role])

    response = client.post(
        reverse("assign_trial", args=[person.pk]),
        {"project": project.pk, "scheduled_for": "2026-07-13T08:30"},
    )

    assert response.status_code == 302
    trial = TrialAssignment.objects.get(person=person)
    assert trial.scheduled_for is not None
