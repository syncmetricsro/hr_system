"""Staff activity statistics (J2).

The client accepted that the audit log is traceability rather than reporting,
then asked for the reporting separately. This is its own page, not a filter on
the log.

Two properties are load-bearing and easy to lose:

* **Every recruiter is listed, including the zeros.** The stated purpose is
  spotting a large gap between two recruiters, and a table that drops its zero
  rows cannot show a gap.
* **Nothing here reads the audit log.** All three figures come from domain
  fields that already existed - `Person.owning_recruiter`,
  `EquipmentIssue.issued_by`, `RoomAssignment.assigned_by` - so the statistics
  survive the audit retention purge that `core.retention` will eventually run.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from uuid import uuid4

import pytest
from django.apps import apps as django_apps
from django.urls import reverse
from django.utils import timezone

from core.accounts.models import Role
from core.offices.models import Office
from core.people.models import Person
from core.reporting.periods import resolve_period
from core.reporting.staff_activity import people_registered, recruiter_productivity

pytestmark = pytest.mark.django_db

JULY = {"period": "month", "month": "2026-07"}


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


@pytest.fixture
def observer(django_user_model):
    return django_user_model.objects.create_user(
        email="pozorovatel@demo.jober.test", password="x", role=Role.OBSERVER
    )


def _recruiter(django_user_model, email):
    return django_user_model.objects.create_user(
        email=email, password="x", role=Role.RECRUITER
    )


def _person(recruiter, office, when=dt.date(2026, 7, 10), name="Worker"):
    person = Person.objects.create(
        first_name=name, last_name="Test", office=office, owning_recruiter=recruiter
    )
    # created_at is auto_now_add, so the date is forced afterwards.
    Person.objects.filter(pk=person.pk).update(
        created_at=timezone.make_aware(dt.datetime.combine(when, dt.time(12, 0)))
    )
    return person


# --- recruiter productivity --------------------------------------------------


def test_counts_registrations_per_recruiter(django_user_model, observer, offices):
    fast = _recruiter(django_user_model, "fast@demo.jober.test")
    slow = _recruiter(django_user_model, "slow@demo.jober.test")
    for i in range(3):
        _person(fast, offices[0], name=f"F{i}")
    _person(slow, offices[0], name="S0")

    rows = recruiter_productivity(resolve_period(JULY), observer)
    counts = {r["recruiter"].email: r["registered"] for r in rows}
    assert counts["fast@demo.jober.test"] == 3
    assert counts["slow@demo.jober.test"] == 1


def test_a_recruiter_who_registered_nobody_is_still_listed(
    django_user_model, observer, offices
):
    """The whole point is spotting a gap; a missing row is not a gap."""
    busy = _recruiter(django_user_model, "busy@demo.jober.test")
    _recruiter(django_user_model, "idle@demo.jober.test")
    _person(busy, offices[0])

    rows = recruiter_productivity(resolve_period(JULY), observer)
    counts = {r["recruiter"].email: r["registered"] for r in rows}
    assert counts["idle@demo.jober.test"] == 0


def test_ordered_by_volume_so_the_gap_is_visible(django_user_model, observer, offices):
    slow = _recruiter(django_user_model, "slow@demo.jober.test")
    fast = _recruiter(django_user_model, "fast@demo.jober.test")
    _person(slow, offices[0], name="S")
    for i in range(4):
        _person(fast, offices[0], name=f"F{i}")

    rows = recruiter_productivity(resolve_period(JULY), observer)
    assert [r["registered"] for r in rows][:2] == [4, 1]


def test_registrations_outside_the_period_are_not_counted(
    django_user_model, observer, offices
):
    recruiter = _recruiter(django_user_model, "r@demo.jober.test")
    _person(recruiter, offices[0], when=dt.date(2026, 6, 30), name="June")
    _person(recruiter, offices[0], when=dt.date(2026, 7, 1), name="July")

    rows = recruiter_productivity(resolve_period(JULY), observer)
    assert rows[0]["registered"] == 1


def test_a_gapped_period_skips_the_month_between(django_user_model, observer, offices):
    recruiter = _recruiter(django_user_model, "r@demo.jober.test")
    _person(recruiter, offices[0], when=dt.date(2026, 1, 10), name="Jan")
    _person(recruiter, offices[0], when=dt.date(2026, 2, 10), name="Feb")
    _person(recruiter, offices[0], when=dt.date(2026, 3, 10), name="Mar")

    period = resolve_period({"period": "months", "month": ["2026-01", "2026-03"]})
    rows = recruiter_productivity(period, observer)
    assert rows[0]["registered"] == 2


# --- office scoping ----------------------------------------------------------


@pytest.mark.jober_only
def test_a_manager_counts_only_their_own_offices_registrations(
    django_user_model, manager, offices
):
    recruiter = _recruiter(django_user_model, "r@demo.jober.test")
    _person(recruiter, offices[0], name="Mine")
    _person(recruiter, offices[1], name="Theirs")

    rows = recruiter_productivity(resolve_period(JULY), manager)
    assert rows[0]["registered"] == 1
    assert people_registered(resolve_period(JULY), manager) == 1


@pytest.mark.jober_only
def test_an_observer_counts_every_office(django_user_model, observer, offices):
    recruiter = _recruiter(django_user_model, "r@demo.jober.test")
    _person(recruiter, offices[0], name="A")
    _person(recruiter, offices[1], name="B")

    assert recruiter_productivity(resolve_period(JULY), observer)[0]["registered"] == 2
    assert people_registered(resolve_period(JULY), observer) == 2


# --- the page ---------------------------------------------------------------


def test_the_page_is_separate_from_the_audit_log(client, manager):
    """The client's distinction: traceability there, reporting here."""
    client.force_login(manager)
    response = client.get(reverse("staff_activity"))
    assert response.status_code == 200
    assert reverse("staff_activity") != reverse("audit_log")


def test_a_recruiter_cannot_open_it(client, django_user_model):
    """Manager and observer only."""
    recruiter = _recruiter(django_user_model, "naborar@demo.jober.test")
    client.force_login(recruiter)
    assert client.get(reverse("staff_activity")).status_code == 403


def test_a_coordinator_cannot_open_it(client, django_user_model):
    coordinator = django_user_model.objects.create_user(
        email="koordinator@demo.jober.test", password="x", role=Role.COORDINATOR
    )
    client.force_login(coordinator)
    assert client.get(reverse("staff_activity")).status_code == 403


def test_an_observer_can_open_it(client, observer):
    client.force_login(observer)
    assert client.get(reverse("staff_activity")).status_code == 200


def test_the_page_carries_a_period_control(client, manager):
    client.force_login(manager)
    response = client.get(reverse("staff_activity") + "?period=year&year=2026")
    assert response.context["period"].kind == "year"


# --- logistics contributions -------------------------------------------------


@pytest.mark.jober_only
@pytest.mark.skipif(
    not django_apps.is_installed("features.logistics"), reason="Jober feature set"
)
def test_equipment_issuance_is_attributed_to_the_coordinator(
    client, django_user_model, manager, offices
):
    from features.logistics.models import EquipmentItem
    from features.logistics.services import issue_equipment, receive_stock

    coordinator = django_user_model.objects.create_user(
        email="koordinator@demo.jober.test", password="x", role=Role.COORDINATOR
    )
    recruiter = _recruiter(django_user_model, "r@demo.jober.test")
    person = _person(recruiter, offices[0])
    item = EquipmentItem.objects.create(name="Helmet", unit_price=Decimal("30"))
    # Issuance draws from the person's own office, so that office needs stock.
    receive_stock(
        received_on=dt.date(2026, 7, 1),
        lines=[{"item": item, "quantity": 5, "total_value": Decimal("150")}],
        operation_key=uuid4(),
        office=offices[0],
    )
    # Stock-tracked issuance requires an idempotency key.
    issue_equipment(person, item, 2, actor=coordinator, operation_key=uuid4())

    client.force_login(manager)
    response = client.get(reverse("staff_activity"))
    panels = response.context["panels"]
    issuance = [p for p in panels if p.get("coordinator_issuance")]
    assert issuance, "logistics did not contribute an issuance panel"
    row = issuance[0]["coordinator_issuance"][0]
    assert row["coordinator"] == "koordinator@demo.jober.test"
    assert row["quantity"] == 2


@pytest.mark.jober_only
@pytest.mark.skipif(
    not django_apps.is_installed("features.logistics"), reason="Jober feature set"
)
def test_a_first_placement_is_not_counted_as_a_transfer(
    django_user_model, observer, offices
):
    from features.logistics.models import Accommodation, Room
    from features.logistics.services import assign_room
    from features.logistics.staff_activity import accommodation_transfers

    coordinator = django_user_model.objects.create_user(
        email="koordinator@demo.jober.test", password="x", role=Role.COORDINATOR
    )
    recruiter = _recruiter(django_user_model, "r@demo.jober.test")
    person = _person(recruiter, offices[0])

    first = Accommodation.objects.create(name="House A", office=offices[0])
    second = Accommodation.objects.create(name="House B", office=offices[0])
    room_a = Room.objects.create(accommodation=first, label="A", capacity=2)
    room_b = Room.objects.create(accommodation=second, label="B", capacity=2)

    assign_room(person, room_a, actor=coordinator)
    period = resolve_period(
        {"period": "month", "month": f"{timezone.localdate():%Y-%m}"}
    )
    assert accommodation_transfers(period, observer) == []

    assign_room(person, room_b, actor=coordinator)
    transfers = accommodation_transfers(period, observer)
    assert len(transfers) == 1
    assert transfers[0]["moved_from"] == first
    assert transfers[0]["moved_to"] == second
    assert transfers[0]["by"] == coordinator


# --- the seed has to make the report demonstrable ---------------------------


@pytest.mark.jober_only
def test_the_demo_seed_spreads_registrations_across_recruiters(django_user_model):
    """A staff-activity table showing one recruiter with everything and two
    with nothing demonstrates the zero rows but not the gap between two working
    recruiters, which is the comparison the report exists for.

    Guards a demo property, not a code path - nothing else would notice.
    """
    from django.core.management import call_command

    call_command("seed_demo")
    call_command("seed_people")

    owners = {
        p.owning_recruiter.email
        for p in Person.objects.filter(owning_recruiter__isnull=False)
    }
    assert len(owners) >= 2, f"every seeded person belongs to one recruiter: {owners}"


@pytest.mark.jober_only
def test_reseeding_repairs_an_existing_databases_attribution(django_user_model):
    """The correction has to reach databases that already exist, or staging
    keeps showing the old attribution however often it is reseeded."""
    from django.core.management import call_command

    call_command("seed_demo")
    call_command("seed_people")

    one = django_user_model.objects.get(email="naborar@demo.jober.test")
    Person.objects.update(owning_recruiter=one)
    assert Person.objects.exclude(owning_recruiter=one).count() == 0

    call_command("seed_people")

    assert Person.objects.exclude(owning_recruiter=one).exists()
