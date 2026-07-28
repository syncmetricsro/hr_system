"""The persistent worker status rail (J8).

The client asked for an always-visible list of workers and their state, with
notifications in the same rail. Three constraints in the brief are the ones
worth pinning, because each fails silently:

* **It must not become an N+1 on every page render.** The rail's contents are
  fetched once through htmx, so an ordinary page does not pay for them, and the
  fragment itself is one query rather than one per worker.
* **It is scoped exactly like the People list.** A rail that quietly showed
  every office would be a fourth leak of this week's shape.
* **The statuses are not a hardcoded working/not-working split.** They come
  from `LifecycleStatus`, so the vocabulary follows the lifecycle configuration
  and cannot drift from the People list beside it.
"""

from __future__ import annotations

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from core.accounts.models import Role
from core.offices.models import Office
from core.people.models import LifecycleStatus, Person
from core.people.rail import RAIL_LIMIT, rail_people

pytestmark = pytest.mark.django_db


class _FakeRequest:
    """The rail service only needs `.user`; building a real request adds
    middleware noise to a query-count assertion."""

    def __init__(self, user):
        self.user = user


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


def _person(office, name="Worker", status=LifecycleStatus.WORKING, recruiter=None):
    return Person.objects.create(
        first_name=name,
        last_name="Test",
        office=office,
        lifecycle_status=status,
        owning_recruiter=recruiter,
    )


# --- scoping, the failure this week keeps producing --------------------------


@pytest.mark.jober_only
def test_the_rail_shows_only_the_managers_offices(client, manager, offices):
    _person(offices[0], name="Mine")
    _person(offices[1], name="Theirs")

    client.force_login(manager)
    names = [
        str(p) for p in client.get(reverse("worker_status_rail")).context["rail_people"]
    ]
    assert names == ["Mine Test"]


@pytest.mark.jober_only
def test_an_observer_sees_every_office(client, django_user_model, offices):
    _person(offices[0], name="A")
    _person(offices[1], name="B")
    observer = django_user_model.objects.create_user(
        email="pozorovatel@demo.jober.test", password="x", role=Role.OBSERVER
    )
    client.force_login(observer)
    assert len(client.get(reverse("worker_status_rail")).context["rail_people"]) == 2


@pytest.mark.jober_only
def test_the_status_counts_narrow_with_the_list(client, manager, offices):
    """A summary above a scoped list must be scoped too - the exact bug that
    shipped three times this week."""
    _person(offices[0], name="Mine", status=LifecycleStatus.WORKING)
    _person(offices[1], name="T1", status=LifecycleStatus.WORKING)
    _person(offices[1], name="T2", status=LifecycleStatus.WORKING)

    client.force_login(manager)
    counts = client.get(reverse("worker_status_rail")).context["rail_status_counts"]
    working = [row for row in counts if row["value"] == LifecycleStatus.WORKING]
    assert working[0]["count"] == 1


def test_an_anonymous_visitor_cannot_fetch_it(client):
    response = client.get(reverse("worker_status_rail"))
    assert response.status_code in (302, 403)


# --- vocabulary comes from the lifecycle, not a hardcoded pair ---------------


def test_statuses_are_not_a_working_not_working_split(client, manager, offices):
    for status in (
        LifecycleStatus.AVAILABLE,
        LifecycleStatus.TRIAL_DAY,
        LifecycleStatus.WORKING,
        LifecycleStatus.INACTIVE,
    ):
        _person(offices[0], name=status, status=status)

    client.force_login(manager)
    counts = client.get(reverse("worker_status_rail")).context["rail_status_counts"]
    assert {row["value"] for row in counts} == {
        LifecycleStatus.AVAILABLE,
        LifecycleStatus.TRIAL_DAY,
        LifecycleStatus.WORKING,
        LifecycleStatus.INACTIVE,
    }


def test_statuses_nobody_holds_are_not_listed(client, manager, offices):
    """A rail full of zero rows is noise; People is where you browse."""
    _person(offices[0], status=LifecycleStatus.WORKING)
    client.force_login(manager)
    counts = client.get(reverse("worker_status_rail")).context["rail_status_counts"]
    assert [row["value"] for row in counts] == [LifecycleStatus.WORKING]


# --- cost -------------------------------------------------------------------


def test_an_ordinary_page_does_not_render_the_rail_contents(client, manager, offices):
    """The shell ships in the page; the workers do not. If this regresses,
    every page render pays for the rail."""
    _person(offices[0], name="Zzz")
    client.force_login(manager)
    body = client.get(reverse("dashboard")).content.decode()
    assert "data-worker-rail" in body  # the shell is there
    assert "Zzz Test" not in body  # the contents are not


def _query_count(user):
    with CaptureQueriesContext(connection) as captured:
        rail_people(_FakeRequest(user))
    return len(captured)


def test_the_cost_does_not_grow_with_headcount(manager, offices):
    """The N+1 the brief warns about.

    Asserting an exact number would be wrong - resolving the office scope is
    its own query and a legitimate constant. What matters is that twenty
    workers cost what one does.
    """
    _person(offices[0], name="Only")
    baseline = _query_count(manager)

    for i in range(20):
        _person(offices[0], name=f"W{i}")

    assert _query_count(manager) == baseline


def test_the_list_is_capped(client, manager, offices):
    for i in range(RAIL_LIMIT + 5):
        _person(offices[0], name=f"W{i}")
    client.force_login(manager)
    context = client.get(reverse("worker_status_rail")).context
    assert len(context["rail_people"]) == RAIL_LIMIT
    assert context["rail_truncated"] is True


def test_archived_workers_are_left_out(client, manager, offices):
    _person(offices[0], name="Active")
    archived = _person(offices[0], name="Gone")
    archived.is_archived = True
    archived.save(update_fields=["is_archived"])

    client.force_login(manager)
    names = [
        str(p) for p in client.get(reverse("worker_status_rail")).context["rail_people"]
    ]
    assert names == ["Active Test"]
