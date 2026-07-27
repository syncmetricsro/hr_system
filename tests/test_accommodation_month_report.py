"""The accommodation month report: five figures, and only five.

The client reviewed this page on the handover call and asked for two things.
The first was a correction: **empty-bed loss never subtracted worker payments**,
so it overstated the loss by exactly what the workers were paying. The second
was subtraction — margin and the internal occupied-cost term off the card.

The reported "occupancy counter is inverted" turned out not to exist. The page
showed *bed-days* (labelled as such) where the client read *beds*; three
workers across a month is 93, not 3. The fix is a head count, not a sign flip.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from core.offices.models import Office
from core.people.models import Person
from features.logistics.models import (
    Accommodation,
    Room,
    RoomAssignment,
    RoomAssignmentStatus,
)
from features.logistics.services import (
    accommodation_month_report,
    set_accommodation_cost_period,
)

pytestmark = pytest.mark.django_db

DISPLAYED = {
    "capacity",
    "occupied_beds",
    "standing_cost",
    "payments",
    "empty_bed_loss",
}


@pytest.fixture
def viewer(django_user_model):
    """Observer — role bypass, so the office scope is the unrestricted
    ``None`` sentinel and these tests see every accommodation."""
    return django_user_model.objects.create_user(
        email="pozorovatel@demo.jober.test", password="x", role="observer"
    )


def _place(room, payment, start, end=None, name="Resident"):
    person = Person.objects.create(first_name="Demo", last_name=name)
    return RoomAssignment.objects.create(
        person=person,
        room=room,
        status=RoomAssignmentStatus.ACTIVE,
        start_date=start,
        end_date=end,
        worker_payment_monthly=Decimal(payment),
    )


def _residence(name, capacity, per_head, month=date(2026, 7, 1)):
    accommodation = Accommodation.objects.create(name=name)
    set_accommodation_cost_period(
        accommodation,
        effective_month=month,
        capacity=capacity,
        per_head_cost=Decimal(per_head),
    )
    return accommodation


# --- the client's own worked example, verbatim from the handover call -------


def test_client_acceptance_fixture(viewer):
    """Capacity 18 at 180 EUR/head; two workers share Apartment 1 at 50 each,
    a third has a two-bed room to himself and pays 230."""
    accommodation = _residence("Fictional residence", capacity=18, per_head="180")
    apartment = Room.objects.create(
        accommodation=accommodation, label="Apartment 1", capacity=2
    )
    twin = Room.objects.create(accommodation=accommodation, label="Twin", capacity=2)
    july = date(2026, 7, 1)
    _place(apartment, "50", july, name="One")
    _place(apartment, "50", july, name="Two")
    _place(twin, "230", july, name="Three")

    row = accommodation_month_report(2026, 7, viewer)["rows"][0]

    assert row["capacity"] == 18
    assert row["occupied_beds"] == 3
    assert row["standing_cost"] == Decimal("3240.00")  # 18 x 180
    assert row["payments"] == Decimal("330.00")  # 50 + 50 + 230
    assert row["empty_bed_loss"] == Decimal("2370.00")  # 3240 - 330 - 540
    # Internal term, checked here but deliberately not rendered.
    assert row["occupied_cost"] == Decimal("540.00")  # 3 x 180


def test_the_bed_a_worker_pays_extra_for_is_not_counted_as_occupied(viewer):
    """The client called this out explicitly. Occupancy follows people, so the
    lone worker in the twin room contributes one bed, not two, even though his
    230 EUR covers both."""
    accommodation = _residence("Fictional residence", capacity=18, per_head="180")
    twin = Room.objects.create(accommodation=accommodation, label="Twin", capacity=2)
    _place(twin, "230", date(2026, 7, 1))

    row = accommodation_month_report(2026, 7, viewer)["rows"][0]
    assert row["occupied_beds"] == 1


# --- what the card may show -------------------------------------------------


def test_margin_is_gone(viewer):
    """Removed on request; the word the client used for it was "price"."""
    _residence("Fictional residence", capacity=4, per_head="180")
    report = accommodation_month_report(2026, 7, viewer)
    assert "margin" not in report["rows"][0]
    assert "margin" not in report["company"]


def test_every_displayed_figure_is_present_on_both_row_and_summary(viewer):
    _residence("Fictional residence", capacity=4, per_head="180")
    report = accommodation_month_report(2026, 7, viewer)
    assert DISPLAYED <= set(report["rows"][0])
    assert DISPLAYED <= set(report["company"])


# --- summary across accommodations ------------------------------------------


def test_summary_sums_the_same_five_across_accommodations(viewer):
    july = date(2026, 7, 1)
    first = _residence("Residence A", capacity=10, per_head="180", month=july)
    second = _residence("Residence B", capacity=8, per_head="180", month=july)
    _place(Room.objects.create(accommodation=first, label="A", capacity=2), "50", july)
    _place(Room.objects.create(accommodation=second, label="B", capacity=2), "60", july)

    report = accommodation_month_report(2026, 7, viewer)
    rows = {row["accommodation"].name: row for row in report["rows"]}
    company = report["company"]

    assert company["capacity"] == 18
    assert company["occupied_beds"] == 2
    for key in ("standing_cost", "payments", "empty_bed_loss"):
        assert company[key] == rows["Residence A"][key] + rows["Residence B"][key], key


def test_an_accommodation_without_a_cost_period_is_flagged_not_counted(viewer):
    Accommodation.objects.create(name="Unpriced residence")
    report = accommodation_month_report(2026, 7, viewer)
    assert report["rows"][0]["missing_period"] is True
    assert report["company"]["standing_cost"] == Decimal("0.00")


# --- office scoping (ADR 0026), which this aggregate had none of ------------


@pytest.mark.jober_only
def test_a_manager_sees_only_their_own_offices_residences(django_user_model):
    """This report opened no single record, so the ``_assert_..._in_scope``
    guards next to it never fired — yet it listed every office's residences
    and summed them into one company-wide bar. Exactly the aggregate leak
    ADR 0026 warns about."""
    velky_meder = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")
    mine = _residence("VM residence", capacity=10, per_head="180")
    theirs = _residence("GYR residence", capacity=8, per_head="180")
    Accommodation.objects.filter(pk=mine.pk).update(office=velky_meder)
    Accommodation.objects.filter(pk=theirs.pk).update(office=gyor)

    manager = django_user_model.objects.create_user(
        email="manazer@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([velky_meder])

    report = accommodation_month_report(2026, 7, manager)
    assert [row["accommodation"].name for row in report["rows"]] == ["VM residence"]
    # The summary bar must narrow too, or the leak just moves up the page.
    assert report["company"]["capacity"] == 10


@pytest.mark.jober_only
def test_an_observer_still_spans_every_office(django_user_model, viewer):
    velky_meder = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")
    mine = _residence("VM residence", capacity=10, per_head="180")
    theirs = _residence("GYR residence", capacity=8, per_head="180")
    Accommodation.objects.filter(pk=mine.pk).update(office=velky_meder)
    Accommodation.objects.filter(pk=theirs.pk).update(office=gyor)

    report = accommodation_month_report(2026, 7, viewer)
    assert len(report["rows"]) == 2
    assert report["company"]["capacity"] == 18


# --- proration and the zero floor -------------------------------------------


def test_month_report_prorates_person_days_and_does_not_create_recovery(viewer):
    """Mid-month arrivals are prorated by day — the client did not object to
    this and it stays. Fifteen of February's 29 days, at 180/head."""
    accommodation = _residence(
        "Fictional residence", capacity=2, per_head="180", month=date(2024, 2, 1)
    )
    room = Room.objects.create(accommodation=accommodation, label="A", capacity=2)
    assignment = _place(room, "100", date(2024, 2, 15), end=date(2024, 3, 1))
    assignment.status = RoomAssignmentStatus.ENDED
    assignment.save(update_fields=["status"])

    row = accommodation_month_report(2024, 2, viewer)["rows"][0]
    assert row["occupied_beds"] == 1
    assert row["standing_cost"] == Decimal("360.00")
    assert row["occupied_cost"] == Decimal("93.10")  # 180 x 15/29
    assert row["payments"] == Decimal("51.72")  # 100 x 15/29
    assert row["empty_bed_loss"] == Decimal("215.17")  # 360 - 51.72 - 93.10
    assert assignment.person.room_assignments.count() == 1


def test_a_full_house_reports_no_empty_bed_loss_rather_than_a_negative_one(viewer):
    """With every bed filled, standing cost equals occupied cost, so the raw
    formula yields -payments. That is not a loss, and a figure labelled one
    must not go negative."""
    july = date(2026, 7, 1)
    accommodation = _residence("Fictional residence", capacity=2, per_head="180")
    room = Room.objects.create(accommodation=accommodation, label="A", capacity=2)
    _place(room, "50", july, name="One")
    _place(room, "50", july, name="Two")

    row = accommodation_month_report(2026, 7, viewer)["rows"][0]
    assert row["occupied_beds"] == 2
    assert row["empty_bed_loss"] == Decimal("0.00")


def test_a_worker_who_changes_room_mid_month_still_occupies_one_bed(viewer):
    """Occupancy is a head count. Two assignments, one person, one bed."""
    july = date(2026, 7, 1)
    accommodation = _residence("Fictional residence", capacity=4, per_head="180")
    first = Room.objects.create(accommodation=accommodation, label="A", capacity=2)
    second = Room.objects.create(accommodation=accommodation, label="B", capacity=2)
    mover = _place(first, "50", july, end=date(2026, 7, 16))
    # unique_active_room_per_person: the old bed is released before the new one.
    mover.status = RoomAssignmentStatus.ENDED
    mover.save(update_fields=["status"])
    RoomAssignment.objects.create(
        person=mover.person,
        room=second,
        status=RoomAssignmentStatus.ACTIVE,
        start_date=date(2026, 7, 16),
        worker_payment_monthly=Decimal("50"),
    )

    row = accommodation_month_report(2026, 7, viewer)["rows"][0]
    assert row["occupied_beds"] == 1
