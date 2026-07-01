from __future__ import annotations

import pytest
from django.urls import reverse

from apps.accounts.permissions import Action, can
from apps.people.models import InactiveReason, LifecycleError, LifecycleStatus, Person
from apps.people.services import recycle_to_available
from apps.projects.services import exit_person

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup(django_user_model):
    coord = django_user_model.objects.create_user(
        email="c@demo.jober.test", password="x", role="coordinator"
    )
    person = Person.objects.create(first_name="A", last_name="B")
    reason = InactiveReason.objects.create(label="Sick (test)", order=99)
    return coord, person, reason


def test_migration_seeded_placeholder_reasons():
    # The 0003 data migration seeds the Q5 placeholders.
    assert InactiveReason.objects.filter(label="Sick").exists()
    assert InactiveReason.objects.filter(label="Military service").exists()


def test_exit_to_inactive_records_reason(setup):
    coord, person, reason = setup
    exit_person(person, actor=coord, reason="left the site", outcome="inactive", inactive_reason=reason)
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.INACTIVE
    assert person.inactive_reason == reason
    assert person.inactive_since is not None


def test_recycle_clears_reason_and_returns_available(setup):
    coord, person, reason = setup
    exit_person(person, actor=coord, outcome="inactive", inactive_reason=reason)
    recycle_to_available(person, actor=coord, reason="returned")
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.AVAILABLE
    assert person.inactive_reason is None
    assert person.inactive_since is None


def test_recycle_requires_inactive(setup):
    coord, person, _reason = setup  # person is AVAILABLE
    with pytest.raises(LifecycleError):
        recycle_to_available(person, actor=coord)


def test_recycle_rbac(django_user_model):
    for role in ("recruiter", "coordinator", "manager"):
        u = django_user_model.objects.create_user(email=f"{role}@demo.jober.test", password="x", role=role)
        assert can(u, Action.PERSON_RECYCLE_AVAILABLE)
    observer = django_user_model.objects.create_user(email="o@demo.jober.test", password="x", role="observer")
    assert not can(observer, Action.PERSON_RECYCLE_AVAILABLE)


def test_recycle_view_persists_and_gated(client, setup, django_user_model):
    coord, person, reason = setup
    exit_person(person, actor=coord, outcome="inactive", inactive_reason=reason)
    url = reverse("recycle_person", kwargs={"person_pk": person.pk})

    observer = django_user_model.objects.create_user(email="o2@demo.jober.test", password="x", role="observer")
    client.force_login(observer)
    assert client.post(url).status_code == 403

    client.force_login(coord)
    resp = client.post(url)
    assert resp.status_code == 302
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.AVAILABLE
