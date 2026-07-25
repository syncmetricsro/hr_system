"""A Person with no office belongs to their owning recruiter (ADR 0026 Phase B).

Decided 2026-07-25. Intake only infers an office when the recruiter belongs to
exactly one, so multi-office recruiters create people with ``office=None``.
A plain ``office__in`` filter would hide those from everyone except Observer -
including the recruiter who just created them.
"""

from __future__ import annotations

import pytest
from django.urls import reverse

from core.offices.models import Office
from core.offices.scoping import may_see_person, scope_people
from core.people.models import Person

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup(django_user_model):
    velky_meder = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    make = django_user_model.objects.create_user
    owner = make(email="owner@demo.jober.test", password="x", role="recruiter")
    owner.offices.set([velky_meder])
    other_recruiter = make(
        email="other@demo.jober.test", password="x", role="recruiter"
    )
    other_recruiter.offices.set([velky_meder])
    manager = make(email="mgr@demo.jober.test", password="x", role="manager")
    manager.offices.set([velky_meder])
    observer = make(email="obs@demo.jober.test", password="x", role="observer")

    unassigned = Person.objects.create(
        first_name="Unassigned", last_name="Candidate", owning_recruiter=owner
    )
    in_office = Person.objects.create(
        first_name="Assigned", last_name="Worker", office=velky_meder
    )
    return {
        "velky_meder": velky_meder,
        "owner": owner,
        "other_recruiter": other_recruiter,
        "manager": manager,
        "observer": observer,
        "unassigned": unassigned,
        "in_office": in_office,
    }


def test_owning_recruiter_sees_their_unassigned_person(setup):
    assert may_see_person(setup["owner"], setup["unassigned"]) is True


def test_another_recruiter_in_the_same_office_does_not(setup):
    """Ownership, not office membership, is what grants access here."""
    assert may_see_person(setup["other_recruiter"], setup["unassigned"]) is False


def test_manager_does_not_see_someone_elses_unassigned_person(setup):
    assert may_see_person(setup["manager"], setup["unassigned"]) is False


def test_observer_sees_unassigned_people(setup):
    assert may_see_person(setup["observer"], setup["unassigned"]) is True


def test_office_assignment_still_governs_people_who_have_one(setup):
    """The new rule must not loosen the normal case."""
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")
    elsewhere = Person.objects.create(
        first_name="Elsewhere",
        last_name="Worker",
        office=gyor,
        owning_recruiter=setup["owner"],
    )
    # Owned by this recruiter, but it HAS an office - and it isn't theirs.
    assert may_see_person(setup["owner"], elsewhere) is False


def test_scope_people_queryset_matches_the_object_level_rule(setup):
    owner_visible = set(scope_people(Person.objects.all(), setup["owner"]))
    assert owner_visible == {setup["unassigned"], setup["in_office"]}

    manager_visible = set(scope_people(Person.objects.all(), setup["manager"]))
    assert manager_visible == {setup["in_office"]}

    # Unrestricted: no filtering at all.
    assert set(scope_people(Person.objects.all(), setup["observer"])) == {
        setup["unassigned"],
        setup["in_office"],
    }


def test_scope_people_is_a_noop_when_no_offices_exist(django_user_model):
    """CorvinumEU: everyone still sees everyone."""
    Office.objects.all().delete()
    recruiter = django_user_model.objects.create_user(
        email="r@demo.corvinum.test", password="x", role="recruiter"
    )
    person = Person.objects.create(first_name="No", last_name="Office")
    assert set(scope_people(Person.objects.all(), recruiter)) == {person}
    assert may_see_person(recruiter, person) is True


@pytest.mark.jober_only
def test_people_list_shows_owned_unassigned_person_to_its_recruiter(client, setup):
    client.force_login(setup["owner"])
    body = client.get(reverse("people_list")).content.decode()
    assert "Unassigned" in body


@pytest.mark.jober_only
def test_people_list_hides_unassigned_person_from_a_manager(client, setup):
    client.force_login(setup["manager"])
    body = client.get(reverse("people_list")).content.decode()
    assert "Unassigned" not in body
    assert "Assigned" in body


@pytest.mark.jober_only
def test_detail_403s_for_a_manager_but_200s_for_the_owning_recruiter(client, setup):
    pk = setup["unassigned"].pk
    client.force_login(setup["manager"])
    assert client.get(reverse("person_detail", args=[pk])).status_code == 403
    client.force_login(setup["owner"])
    assert client.get(reverse("person_detail", args=[pk])).status_code == 200


@pytest.mark.jober_only
def test_csv_export_follows_the_same_rule(client, setup):
    # Managers hold EXPORT_APPROVED; recruiters do not, so the export is only
    # reachable as the manager - who must not receive the unassigned row.
    client.force_login(setup["manager"])
    body = client.get(reverse("export_people")).content.decode()
    assert "Assigned" in body
    assert "Unassigned" not in body
