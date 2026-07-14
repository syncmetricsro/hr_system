from __future__ import annotations

import pytest
from django.urls import reverse

from core.people.models import Person

pytestmark = pytest.mark.django_db


@pytest.fixture
def make_user(django_user_model):
    def _make(role):
        return django_user_model.objects.create_user(
            email=f"{role}@demo.jober.test", password="x", role=role
        )
    return _make


def test_manager_can_edit_phone(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    client.force_login(make_user("manager"))
    resp = client.post(
        reverse("person_edit", args=[person.pk]),
        {"first_name": "Olha", "last_name": "Kovalenko", "phone": "+18777804236"},
    )
    assert resp.status_code == 302
    person.refresh_from_db()
    assert person.phone == "+18777804236"


def test_manager_can_edit_person_email(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    client.force_login(make_user("manager"))
    response = client.post(
        reverse("person_edit", args=[person.pk]),
        {"first_name": "Olha", "last_name": "Kovalenko", "email": "olha@example.test"},
    )
    assert response.status_code == 302
    person.refresh_from_db()
    assert person.email == "olha@example.test"


def test_edit_requires_login(client):
    person = Person.objects.create(first_name="A", last_name="B")
    resp = client.get(reverse("person_edit", args=[person.pk]))
    assert resp.status_code == 302
    assert reverse("login") in resp.headers["Location"]


def test_observer_cannot_edit(client, make_user):
    person = Person.objects.create(first_name="A", last_name="B")
    client.force_login(make_user("observer"))
    assert client.get(reverse("person_edit", args=[person.pk])).status_code == 403


def test_disability_type_is_disabled_and_cleared_when_not_applicable(client, make_user):
    person = Person.objects.create(
        first_name="Olha", last_name="Kovalenko", has_disability=True,
        disability_type="Mobility impairment",
    )
    client.force_login(make_user("manager"))

    body = client.get(reverse("person_edit", args=[person.pk])).content.decode()
    assert 'x-data="{ hasDisability: true }"' in body
    assert 'x-bind:disabled="!hasDisability"' in body

    response = client.post(
        reverse("person_edit", args=[person.pk]),
        {"first_name": "Olha", "last_name": "Kovalenko", "has_disability": ""},
    )
    assert response.status_code == 302
    person.refresh_from_db()
    assert person.has_disability is False
    assert person.disability_type == ""
