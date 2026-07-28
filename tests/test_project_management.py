"""Managing project records (production-readiness item 15).

`Action.PROJECT_MANAGE` was granted to Manager in both clients and implemented
nowhere. The only ways to add a project were the demo seed, a shell, or Django
admin - which needs a superuser no client role has, writes no audit event and
honours no office boundary. The client intends to enter a whole project on his
trial instance, so he would have hit this in his first ten minutes.

The properties worth pinning are the ones that fail quietly:

* a manager cannot file a project against another office, by picking *or* by
  posting;
* the coordinator picker cannot reintroduce the bug the demo seed had, where a
  coordinator was made responsible for projects they get a 403 on;
* a duplicate `code` is a field error, not a 500;
* deactivation keeps everything attached to the project.
"""

from __future__ import annotations

import pytest
from django.urls import reverse

from core.accounts.models import Role
from core.audit.models import AuditEvent
from core.offices.models import Office
from core.projects.forms import ProjectForm
from core.projects.models import Project

pytestmark = pytest.mark.django_db


@pytest.fixture
def offices():
    return (
        Office.objects.create(name="Velký Meder", code="VM", country="SK"),
        Office.objects.create(name="Győr", code="GYR", country="HU"),
    )


@pytest.fixture
def manager(django_user_model, offices):
    user = django_user_model.objects.create_user(
        email="manazer@demo.jober.test", password="x", role=Role.MANAGER
    )
    user.offices.set([offices[0]])
    return user


def _coordinator(django_user_model, office, email):
    user = django_user_model.objects.create_user(
        email=email, password="x", role=Role.COORDINATOR
    )
    user.offices.set([office])
    return user


def _payload(**over):
    data = {
        "name": "DHL Bratislava",
        "partner": "DHL",
        "code": "DHLBA",
        "financial_reporting_eligible": "on",
        "is_active": "on",
        "notes": "",
    }
    data.update(over)
    return data


# --- creating ---------------------------------------------------------------


def test_a_manager_can_create_a_project(client, manager, offices):
    client.force_login(manager)
    response = client.post(
        reverse("project_create"), _payload(office=offices[0].pk), follow=True
    )
    assert response.status_code == 200
    project = Project.objects.get(code="DHLBA")
    assert project.office == offices[0]


def test_creating_is_audited(client, manager, offices):
    """Django admin was the only way to add a project and records nothing.
    Going through the service layer is most of the point of this feature."""
    client.force_login(manager)
    client.post(reverse("project_create"), _payload(office=offices[0].pk))
    assert AuditEvent.objects.filter(action="project.created").exists()


def test_a_duplicate_code_is_a_field_error_not_a_500(client, manager, offices):
    Project.objects.create(name="Existing", code="DHLBA", office=offices[0])
    client.force_login(manager)
    response = client.post(reverse("project_create"), _payload(office=offices[0].pk))
    assert response.status_code == 200
    assert "code" in response.context["form"].errors
    assert Project.objects.filter(code="DHLBA").count() == 1


# --- the office boundary ----------------------------------------------------


@pytest.mark.jober_only
def test_a_manager_cannot_pick_another_office(manager, offices):
    form = ProjectForm(user=manager)
    assert list(form.fields["office"].queryset) == [offices[0]]


@pytest.mark.jober_only
def test_a_manager_cannot_post_another_office_either(client, manager, offices):
    """The picker narrowing is presentation; the queryset is the validation."""
    client.force_login(manager)
    response = client.post(reverse("project_create"), _payload(office=offices[1].pk))
    assert response.status_code == 200
    assert "office" in response.context["form"].errors
    assert not Project.objects.filter(code="DHLBA").exists()


@pytest.mark.jober_only
def test_a_manager_cannot_open_another_offices_edit_form(client, manager, offices):
    theirs = Project.objects.create(name="Győr", code="GYR1", office=offices[1])
    client.force_login(manager)
    assert client.get(reverse("project_edit", args=[theirs.pk])).status_code == 403


@pytest.mark.jober_only
def test_a_manager_can_edit_their_own_offices_project(client, manager, offices):
    """Guard the opposite failure: a blanket 403 satisfies the test above."""
    mine = Project.objects.create(name="Mine", code="VM1", office=offices[0])
    client.force_login(manager)
    assert client.get(reverse("project_edit", args=[mine.pk])).status_code == 200


# --- the coordinator picker, and the bug it must not reintroduce ------------


@pytest.mark.jober_only
def test_coordinators_from_another_office_are_rejected(
    client, django_user_model, manager, offices
):
    """The demo seed had exactly this bug until 2026-07-26: a coordinator made
    responsible for projects they get a 403 on, which reads as broken data the
    moment anyone asks who runs the Győr contracts."""
    stray = _coordinator(django_user_model, offices[1], "koordinator.gyor@demo.jober.test")
    client.force_login(manager)
    response = client.post(
        reverse("project_create"),
        _payload(office=offices[0].pk, responsible_coordinators=[stray.pk]),
    )
    assert response.status_code == 200
    assert "responsible_coordinators" in response.context["form"].errors
    assert not Project.objects.filter(code="DHLBA").exists()


@pytest.mark.jober_only
def test_a_coordinator_of_the_same_office_is_accepted(
    client, django_user_model, manager, offices
):
    own = _coordinator(django_user_model, offices[0], "koordinator@demo.jober.test")
    client.force_login(manager)
    client.post(
        reverse("project_create"),
        _payload(office=offices[0].pk, responsible_coordinators=[own.pk]),
    )
    project = Project.objects.get(code="DHLBA")
    assert list(project.responsible_coordinators.all()) == [own]


# --- deactivation, never deletion -------------------------------------------


def test_deactivating_keeps_the_project_and_its_history(client, manager, offices):
    """Four models PROTECT a project, so deletion is impossible by design.
    Deactivation must not quietly lose anything either."""
    project = Project.objects.create(name="Mine", code="VM1", office=offices[0])
    client.force_login(manager)

    client.post(reverse("project_set_active", args=[project.pk]), {"active": "0"})

    project.refresh_from_db()
    assert project.is_active is False
    assert Project.objects.filter(pk=project.pk).exists()


def test_reactivating_works(client, manager, offices):
    project = Project.objects.create(
        name="Mine", code="VM1", office=offices[0], is_active=False
    )
    client.force_login(manager)
    client.post(reverse("project_set_active", args=[project.pk]), {"active": "1"})
    project.refresh_from_db()
    assert project.is_active is True


def test_deactivation_is_audited(client, manager, offices):
    project = Project.objects.create(name="Mine", code="VM1", office=offices[0])
    client.force_login(manager)
    client.post(reverse("project_set_active", args=[project.pk]), {"active": "0"})
    assert AuditEvent.objects.filter(action="project.deactivated").exists()


@pytest.mark.jober_only
def test_another_offices_project_cannot_be_deactivated(client, manager, offices):
    theirs = Project.objects.create(name="Theirs", code="GYR1", office=offices[1])
    client.force_login(manager)
    response = client.post(
        reverse("project_set_active", args=[theirs.pk]), {"active": "0"}
    )
    theirs.refresh_from_db()
    assert response.status_code == 403
    assert theirs.is_active is True


# --- who may manage ---------------------------------------------------------


@pytest.mark.parametrize("role", [Role.RECRUITER, Role.COORDINATOR])
def test_lesser_roles_cannot_reach_the_form(client, django_user_model, role):
    user = django_user_model.objects.create_user(
        email=f"{role}@demo.jober.test", password="x", role=role
    )
    client.force_login(user)
    assert client.get(reverse("project_create")).status_code == 403


def test_the_overview_page_offers_a_create_link(client, manager):
    """Item 15 recorded a "Manage projects" button pointing at the read-only
    list. It was in `templates/pages/dashboard.html`, which **no view
    renders** - the `dashboard` URL delegates to `reports()`. So the button was
    not merely misleading, it was invisible, and the page a manager actually
    lands on had no way to create a project at all."""
    client.force_login(manager)
    body = client.get(reverse("dashboard")).content.decode()
    assert reverse("project_create") in body


def test_a_lesser_role_gets_no_create_link_on_the_overview(client, django_user_model):
    recruiter = django_user_model.objects.create_user(
        email="naborar@demo.jober.test", password="x", role=Role.RECRUITER
    )
    client.force_login(recruiter)
    body = client.get(reverse("dashboard")).content.decode()
    assert reverse("project_create") not in body
