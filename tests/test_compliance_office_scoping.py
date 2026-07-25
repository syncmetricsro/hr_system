from __future__ import annotations

import datetime as dt

import pytest
from django.urls import reverse

from core.offices.models import Office
from core.people.models import LifecycleStatus, Person
from features.compliance.services import compliance_alerts

pytestmark = pytest.mark.django_db

TODAY = dt.date.today()


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
        lifecycle_status=LifecycleStatus.WORKING,
    )
    Person.objects.create(
        first_name="Farrukh",
        last_name="Gyor",
        office=gyor,
        lifecycle_status=LifecycleStatus.WORKING,
    )
    return {
        "velky_meder": velky_meder,
        "gyor": gyor,
        "manager": manager,
        "observer": observer,
    }


def test_compliance_alerts_hides_other_offices_person_for_manager(two_offices):
    alerts = compliance_alerts(two_offices["manager"])
    names = {a["person"].first_name for a in alerts}
    assert "Olha" in names
    assert "Farrukh" not in names


def test_compliance_alerts_observer_sees_all_offices(two_offices):
    alerts = compliance_alerts(two_offices["observer"])
    names = {a["person"].first_name for a in alerts}
    assert "Olha" in names
    assert "Farrukh" in names


def test_compliance_alerts_no_viewer_is_unrestricted(two_offices):
    """viewer=None is a deliberate internal 'no filter' convention, distinct
    from an anonymous *web* request - must not be silently scoped to nothing."""
    alerts = compliance_alerts()
    names = {a["person"].first_name for a in alerts}
    assert "Olha" in names
    assert "Farrukh" in names


def test_compliance_list_page_hides_other_offices_person(client, two_offices):
    client.force_login(two_offices["manager"])
    body = client.get(reverse("compliance_list")).content.decode()
    assert "Olha" in body
    assert "Farrukh" not in body


def test_compliance_alerts_unaffected_when_no_offices_exist(django_user_model):
    """CorvinumEU: zero Office rows anywhere - alerts still cover everyone."""
    manager = django_user_model.objects.create_user(
        email="mgr@demo.corvinum.test", password="x", role="manager"
    )
    Person.objects.create(
        first_name="No", last_name="Office", lifecycle_status=LifecycleStatus.WORKING
    )
    alerts = compliance_alerts(manager)
    assert any(a["person"].first_name == "No" for a in alerts)
