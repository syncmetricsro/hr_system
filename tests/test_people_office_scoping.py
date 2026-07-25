from __future__ import annotations

import pytest
from django.urls import reverse

from core.offices.models import Office
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

    vm_person = Person.objects.create(
        first_name="Olha", last_name="VM", office=velky_meder
    )
    gyr_person = Person.objects.create(
        first_name="Farrukh", last_name="Gyor", office=gyor
    )
    return {
        "velky_meder": velky_meder,
        "gyor": gyor,
        "manager": manager,
        "observer": observer,
        "vm_person": vm_person,
        "gyr_person": gyr_person,
    }


def test_people_list_hides_other_offices_person(client, two_offices):
    client.force_login(two_offices["manager"])
    body = client.get(reverse("people_list")).content.decode()
    assert "Olha" in body
    assert "Farrukh" not in body


def test_people_list_observer_sees_all_offices(client, two_offices):
    client.force_login(two_offices["observer"])
    body = client.get(reverse("people_list")).content.decode()
    assert "Olha" in body
    assert "Farrukh" in body


def test_manager_cannot_view_another_offices_person_detail(client, two_offices):
    client.force_login(two_offices["manager"])
    resp = client.get(reverse("person_detail", args=[two_offices["gyr_person"].pk]))
    assert resp.status_code == 403


def test_manager_can_view_their_own_offices_person_detail(client, two_offices):
    client.force_login(two_offices["manager"])
    resp = client.get(reverse("person_detail", args=[two_offices["vm_person"].pk]))
    assert resp.status_code == 200


def test_observer_can_view_any_offices_person_detail(client, two_offices):
    client.force_login(two_offices["observer"])
    resp = client.get(reverse("person_detail", args=[two_offices["gyr_person"].pk]))
    assert resp.status_code == 200


def test_people_csv_export_scoped_to_manager_office(client, two_offices):
    client.force_login(two_offices["manager"])
    body = client.get(reverse("export_people")).content.decode()
    assert "Olha" in body
    assert "Farrukh" not in body


def test_people_csv_export_observer_sees_all(client, two_offices):
    client.force_login(two_offices["observer"])
    body = client.get(reverse("export_people")).content.decode()
    assert "Olha" in body
    assert "Farrukh" in body


def test_manager_cannot_archive_another_offices_person(client, two_offices):
    client.force_login(two_offices["manager"])
    resp = client.post(reverse("archive_person", args=[two_offices["gyr_person"].pk]))
    assert resp.status_code == 403


def test_manager_cannot_recycle_another_offices_person(client, two_offices):
    client.force_login(two_offices["manager"])
    resp = client.post(reverse("recycle_person", args=[two_offices["gyr_person"].pk]))
    assert resp.status_code == 403


def test_people_list_unaffected_when_no_offices_exist(client, django_user_model):
    """CorvinumEU: zero Office rows anywhere - every non-Observer role still
    sees the full list, not an empty one."""
    manager = django_user_model.objects.create_user(
        email="mgr@demo.corvinum.test", password="x", role="manager"
    )
    Person.objects.create(first_name="No", last_name="Office")
    client.force_login(manager)
    body = client.get(reverse("people_list")).content.decode()
    assert "No" in body
