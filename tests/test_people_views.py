from __future__ import annotations

import pytest
from django.urls import reverse

from core.people.models import Person

pytestmark = pytest.mark.django_db


@pytest.fixture
def make_user(django_user_model):
    def _make(role, email=None):
        return django_user_model.objects.create_user(
            email=email or f"{role}@demo.jober.test", password="x", role=role
        )

    return _make


def test_people_list_requires_login(client):
    response = client.get(reverse("people_list"))
    assert response.status_code == 302
    assert reverse("login") in response.headers["Location"]


def test_people_list_shows_person(client, make_user):
    Person.objects.create(first_name="Olha", last_name="Kovalenko")
    client.force_login(make_user("observer"))
    response = client.get(reverse("people_list"))
    assert response.status_code == 200
    assert "Kovalenko" in response.content.decode("utf-8")


def test_detail_shows_sensitive_for_manager(client, make_user):
    person = Person.objects.create(
        first_name="Olha", last_name="Kovalenko",
        has_disability=True, disability_type="reduced mobility",
    )
    client.force_login(make_user("manager"))
    body = client.get(reverse("person_detail", args=[person.pk])).content.decode("utf-8")
    assert "reduced mobility" in body


def test_detail_hides_sensitive_from_unconnected_recruiter(client, make_user):
    owner = make_user("recruiter")
    other = make_user("recruiter", "rec2@demo.jober.test")
    person = Person.objects.create(
        first_name="Olha", last_name="Kovalenko", owning_recruiter=owner,
        has_disability=True, disability_type="reduced mobility",
    )
    client.force_login(other)
    body = client.get(reverse("person_detail", args=[person.pk])).content.decode("utf-8")
    assert "reduced mobility" not in body


def test_detail_shows_sensitive_to_owning_recruiter(client, make_user):
    owner = make_user("recruiter")
    person = Person.objects.create(
        first_name="Olha", last_name="Kovalenko", owning_recruiter=owner,
        has_disability=True, disability_type="reduced mobility",
    )
    client.force_login(owner)
    body = client.get(reverse("person_detail", args=[person.pk])).content.decode("utf-8")
    assert "reduced mobility" in body
