from __future__ import annotations

import pytest
from django.urls import reverse

from core.people.models import InactiveReason, LifecycleStatus, Person

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


def test_people_list_filters_inactive_reason_and_preserves_search(client, make_user):
    sick = InactiveReason.objects.get(label="Sick")
    Person.objects.create(
        first_name="Olha",
        last_name="Sick",
        lifecycle_status=LifecycleStatus.INACTIVE,
        inactive_reason=sick,
    )
    Person.objects.create(
        first_name="Olha",
        last_name="NoReason",
        lifecycle_status=LifecycleStatus.INACTIVE,
    )
    Person.objects.create(first_name="Olha", last_name="Available")
    client.force_login(make_user("observer"))

    response = client.get(
        reverse("people_list"),
        {"q": "olha", "status": "inactive", "inactive_reason": str(sick.pk)},
    )
    body = response.content.decode()
    assert "Olha Sick" in body
    assert "Olha NoReason" not in body
    assert response.context["query"] == "olha"
    assert response.context["inactive_reason"] == str(sick.pk)

    no_reason = client.get(
        reverse("people_list"),
        {"status": "inactive", "inactive_reason": "none"},
    )
    assert "Olha NoReason" in no_reason.content.decode()
    assert "Olha Sick" not in no_reason.content.decode()


def test_people_list_ignores_invalid_or_inapplicable_inactive_reason(client, make_user):
    reason = InactiveReason.objects.get(label="Sick")
    Person.objects.create(
        first_name="Ina",
        last_name="One",
        lifecycle_status=LifecycleStatus.INACTIVE,
        inactive_reason=reason,
    )
    Person.objects.create(first_name="Ava", last_name="One")
    client.force_login(make_user("observer"))

    invalid = client.get(
        reverse("people_list"),
        {"status": "inactive", "inactive_reason": "999999"},
    )
    assert invalid.context["inactive_reason"] == ""
    assert "Ina One" in invalid.content.decode()

    inapplicable = client.get(
        reverse("people_list"),
        {"status": "available", "inactive_reason": str(reason.pk)},
    )
    assert inapplicable.context["inactive_reason"] == ""
    assert "Ava One" in inapplicable.content.decode()


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
