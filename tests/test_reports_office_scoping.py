from __future__ import annotations

import pytest
from django.urls import reverse

from core.offices.models import Office
from core.people.models import LifecycleStatus, Person
from core.projects.models import Project

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

    Person.objects.create(
        first_name="Olha",
        last_name="VM",
        office=velky_meder,
        lifecycle_status=LifecycleStatus.AVAILABLE,
    )
    Person.objects.create(
        first_name="Farrukh",
        last_name="Gyor",
        office=gyor,
        lifecycle_status=LifecycleStatus.AVAILABLE,
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


def test_reports_total_people_and_active_projects_scoped_to_manager_office(
    client, two_offices
):
    client.force_login(two_offices["manager"])
    body = client.get(reverse("reports")).content.decode()
    assert "VM Project" in body
    assert "Győr Project" not in body


def test_reports_shows_all_offices_for_observer(client, two_offices):
    client.force_login(two_offices["observer"])
    body = client.get(reverse("reports")).content.decode()
    assert "VM Project" in body
    assert "Győr Project" in body


def test_reports_unaffected_when_no_offices_exist(client, django_user_model):
    """CorvinumEU: zero Office rows anywhere - reports still shows everything."""
    manager = django_user_model.objects.create_user(
        email="mgr@demo.corvinum.test", password="x", role="manager"
    )
    Project.objects.create(name="No Office Project", code="NOOFF")
    client.force_login(manager)
    body = client.get(reverse("reports")).content.decode()
    assert "No Office Project" in body
