from __future__ import annotations

import pytest
from django.urls import NoReverseMatch, reverse

from core.people.models import Person
from core.projects.models import Project
from core.projects.services import schedule_trial

# Jober-specific URLs/policies/languages — excluded from the corvinum lane.
pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


@pytest.fixture
def make_user(django_user_model):
    def _make(role, email):
        return django_user_model.objects.create_user(email=email, password="x", role=role)
    return _make


@pytest.fixture
def routed(make_user):
    coord_a = make_user("coordinator", "a@demo.jober.test")
    coord_b = make_user("coordinator", "b@demo.jober.test")
    p1 = Project.objects.create(name="Alpha", code="ALPHA")
    p2 = Project.objects.create(name="Beta", code="BETA")
    p1.responsible_coordinators.add(coord_a)
    p2.responsible_coordinators.add(coord_b)
    alice = Person.objects.create(first_name="Alice", last_name="Alpha")
    bob = Person.objects.create(first_name="Bob", last_name="Beta")
    schedule_trial(alice, p1, actor=coord_a)
    schedule_trial(bob, p2, actor=coord_b)
    return {"coord_a": coord_a}


def test_coordinator_sees_only_their_projects(client, routed):
    client.force_login(routed["coord_a"])
    body = client.get(reverse("trials_queue")).content.decode("utf-8")
    assert "Alice Alpha" in body       # coord_a's project trial
    assert "Bob Beta" not in body      # other coordinator's trial is routed away


def test_manager_sees_all_trials(client, make_user, routed):
    client.force_login(make_user("manager", "m@demo.jober.test"))
    body = client.get(reverse("trials_queue")).content.decode("utf-8")
    assert "Alice Alpha" in body
    assert "Bob Beta" in body


def test_corvinum_wage_routes_are_not_mounted_for_jober():
    with pytest.raises(NoReverseMatch):
        reverse("wage_list")
    with pytest.raises(NoReverseMatch):
        reverse("wage_record")
