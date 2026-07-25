from __future__ import annotations

import pytest
from django.urls import reverse

from core.offices.models import Office
from core.projects.forms import operable_projects
from core.projects.models import Project, TrialAssignment, TrialOutcome
from core.people.models import Person

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

    p_vm = Project.objects.create(name="VM Project", code="VMPROJ", office=velky_meder)
    p_gyr = Project.objects.create(name="Győr Project", code="GYRPROJ", office=gyor)
    return {
        "velky_meder": velky_meder,
        "gyor": gyor,
        "manager": manager,
        "observer": observer,
        "p_vm": p_vm,
        "p_gyr": p_gyr,
    }


def test_project_list_hides_other_offices_project(client, two_offices):
    client.force_login(two_offices["manager"])
    body = client.get(reverse("project_list")).content.decode()
    assert "VM Project" in body
    assert "Győr Project" not in body


def test_project_list_observer_sees_all_offices(client, two_offices):
    client.force_login(two_offices["observer"])
    body = client.get(reverse("project_list")).content.decode()
    assert "VM Project" in body
    assert "Győr Project" in body


def test_manager_cannot_view_another_offices_project_detail(client, two_offices):
    client.force_login(two_offices["manager"])
    resp = client.get(reverse("project_detail", args=[two_offices["p_gyr"].pk]))
    assert resp.status_code == 403


def test_manager_can_view_their_own_offices_project_detail(client, two_offices):
    client.force_login(two_offices["manager"])
    resp = client.get(reverse("project_detail", args=[two_offices["p_vm"].pk]))
    assert resp.status_code == 200


def test_observer_can_view_any_offices_project_detail(client, two_offices):
    client.force_login(two_offices["observer"])
    resp = client.get(reverse("project_detail", args=[two_offices["p_gyr"].pk]))
    assert resp.status_code == 200


def test_operable_projects_excludes_other_office_even_for_manager(two_offices):
    projects = operable_projects(two_offices["manager"])
    assert list(projects) == [two_offices["p_vm"]]


def test_operable_projects_returns_all_for_observer(two_offices):
    projects = operable_projects(two_offices["observer"])
    assert set(projects) == {two_offices["p_vm"], two_offices["p_gyr"]}


def test_trials_queue_hides_other_offices_pending_trial(client, two_offices):
    vm_person = Person.objects.create(first_name="Olha", last_name="VM")
    gyr_person = Person.objects.create(first_name="Farrukh", last_name="Gyor")
    vm_trial = TrialAssignment.objects.create(
        person=vm_person,
        project=two_offices["p_vm"],
        outcome=TrialOutcome.PENDING,
        scheduled_date="2026-08-01",
    )
    gyr_trial = TrialAssignment.objects.create(
        person=gyr_person,
        project=two_offices["p_gyr"],
        outcome=TrialOutcome.PENDING,
        scheduled_date="2026-08-01",
    )
    client.force_login(two_offices["manager"])
    resp = client.get(reverse("trials_queue"))
    # The notification panel (out of scope for this slice) also surfaces
    # person names, so assert on the queryset the view actually built.
    assert list(resp.context["trials"]) == [vm_trial]
    assert gyr_trial not in resp.context["trials"]


def test_manager_cannot_record_outcome_for_another_offices_trial(client, two_offices):
    person = Person.objects.create(first_name="Farrukh", last_name="Gyor")
    trial = TrialAssignment.objects.create(
        person=person,
        project=two_offices["p_gyr"],
        outcome=TrialOutcome.PENDING,
        scheduled_date="2026-08-01",
    )
    client.force_login(two_offices["manager"])
    resp = client.post(reverse("trial_outcome", args=[trial.pk]), {"outcome": "pass"})
    assert resp.status_code == 403


def test_projects_csv_export_scoped_to_manager_office(client, two_offices):
    client.force_login(two_offices["manager"])
    body = client.get(reverse("export_projects")).content.decode()
    assert "VM Project" in body
    assert "Győr Project" not in body


def test_projects_csv_export_observer_sees_all(client, two_offices):
    client.force_login(two_offices["observer"])
    body = client.get(reverse("export_projects")).content.decode()
    assert "VM Project" in body
    assert "Győr Project" in body


def test_manager_cannot_assign_trial_for_another_offices_person(client, two_offices):
    person = Person.objects.create(first_name="Farrukh", last_name="Gyor")
    client.force_login(two_offices["manager"])
    resp = client.post(
        reverse("assign_trial", args=[person.pk]),
        {"project": two_offices["p_gyr"].pk, "scheduled_for": "2026-08-01T09:00"},
    )
    assert resp.status_code == 403


def test_manager_cannot_update_readiness_for_another_offices_person(
    client, two_offices
):
    person = Person.objects.create(first_name="Farrukh", last_name="Gyor")
    client.force_login(two_offices["manager"])
    resp = client.post(
        reverse("readiness_update", args=[person.pk]),
        {"project": two_offices["p_gyr"].pk},
    )
    assert resp.status_code == 403


def test_manager_cannot_exit_another_offices_person(client, two_offices):
    person = Person.objects.create(first_name="Farrukh", last_name="Gyor")
    client.force_login(two_offices["manager"])
    resp = client.post(
        reverse("exit_person", args=[person.pk]), {"outcome": "available"}
    )
    assert resp.status_code == 403


def test_manager_cannot_activate_another_offices_person(client, two_offices):
    person = Person.objects.create(first_name="Farrukh", last_name="Gyor")
    client.force_login(two_offices["manager"])
    resp = client.post(
        reverse("activate_person", args=[person.pk]),
        {"project": two_offices["p_gyr"].pk},
    )
    assert resp.status_code == 403


def test_project_list_unaffected_when_no_offices_exist(client, django_user_model):
    """CorvinumEU: zero Office rows anywhere - every non-Observer role still
    sees the full list, not an empty one."""
    manager = django_user_model.objects.create_user(
        email="mgr@demo.corvinum.test", password="x", role="manager"
    )
    Project.objects.create(name="No Office Project", code="NOOFF")
    client.force_login(manager)
    body = client.get(reverse("project_list")).content.decode()
    assert "No Office Project" in body
