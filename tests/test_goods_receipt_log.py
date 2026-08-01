"""The goods-receipt log (J5).

The client demonstrated the gap live: after receiving 3 helmets and 2 boots he
could see the new totals but could not answer "what did I take in today?".

This needed no new model - `receive_stock()` has been writing a receipt header
and its lines all along, and nothing read them back. It is a read view over
records that already existed.

Office scoping is asserted here rather than left for a follow-up. A receipt
names a supplier, a reference and a value for one office, and this week
produced three separate leaks of exactly that shape.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from django.apps import apps as django_apps
from django.test import override_settings
from django.urls import reverse

if not django_apps.is_installed("features.logistics"):
    pytest.skip("Jober feature set not installed", allow_module_level=True)

from core.offices.models import Office  # noqa: E402
from core.reporting.periods import resolve_period  # noqa: E402
from features.logistics.models import EquipmentItem  # noqa: E402
from features.logistics.services import goods_receipts, receive_stock  # noqa: E402

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


@pytest.fixture
def item():
    return EquipmentItem.objects.create(name="Demo boot", size="42")


@pytest.fixture
def offices():
    return (
        Office.objects.create(name="Velký Meder", code="VM", country="SK"),
        Office.objects.create(name="Győr", code="GYR", country="HU"),
    )


def _receipt(item, when, *, office=None, quantity=3, value="30.00", supplier="Acme"):
    return receive_stock(
        received_on=when,
        lines=[{"item": item, "quantity": quantity, "total_value": Decimal(value)}],
        operation_key=uuid4(),
        supplier=supplier,
        reference=f"REF-{when:%Y%m%d}-{quantity}",
        office=office,
    )


# --- the question the client could not answer --------------------------------


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_lists_what_was_booked_in(item):
    _receipt(item, date(2026, 7, 14), supplier="Fictional Safety Supply")
    log = goods_receipts()
    assert len(log["rows"]) == 1
    row = log["rows"][0]
    assert row["receipt"].supplier == "Fictional Safety Supply"
    assert row["quantity"] == 3
    assert row["value"] == Decimal("30.00")


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_newest_first(item):
    _receipt(item, date(2026, 7, 1))
    _receipt(item, date(2026, 7, 20))
    _receipt(item, date(2026, 7, 10))
    dates = [row["receipt"].received_on for row in goods_receipts()["rows"]]
    assert dates == sorted(dates, reverse=True)


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_totals_are_summed_from_the_lines_not_stored(item):
    """A stored total can drift from what the receipt contains; a computed one
    cannot. Same rule as every other money figure in the app."""
    other = EquipmentItem.objects.create(name="Vest", size="")
    receive_stock(
        received_on=date(2026, 7, 14),
        lines=[
            {"item": item, "quantity": 2, "total_value": Decimal("20.00")},
            {"item": other, "quantity": 5, "total_value": Decimal("37.50")},
        ],
        operation_key=uuid4(),
    )
    log = goods_receipts()
    assert log["rows"][0]["quantity"] == 7
    assert log["rows"][0]["value"] == Decimal("57.50")
    assert log["quantity"] == 7
    assert log["value"] == Decimal("57.50")


# --- period filtering, reusing J7 -------------------------------------------


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_filters_by_period(item):
    _receipt(item, date(2026, 1, 15))
    _receipt(item, date(2026, 3, 15))
    _receipt(item, date(2026, 7, 15))
    year = resolve_period({"period": "year", "year": "2026"})
    march = resolve_period({"period": "month", "month": "2026-03"})
    assert len(goods_receipts(year)["rows"]) == 3
    assert len(goods_receipts(march)["rows"]) == 1


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_a_gapped_period_excludes_the_months_between(item):
    _receipt(item, date(2026, 1, 15))
    _receipt(item, date(2026, 3, 15))
    _receipt(item, date(2026, 7, 15))
    period = resolve_period({"period": "months", "month": ["2026-01", "2026-03"]})
    assert len(goods_receipts(period)["rows"]) == 2


# --- office scoping, from the first commit ----------------------------------


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_a_manager_sees_only_their_own_offices_receipts(
    client, django_user_model, item, offices
):
    velky_meder, gyor = offices
    _receipt(item, date(2026, 7, 14), office=velky_meder, supplier="VM supplier")
    _receipt(item, date(2026, 7, 15), office=gyor, supplier="GYR supplier")

    manager = django_user_model.objects.create_user(
        email="manazer@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([velky_meder])
    client.force_login(manager)

    response = client.get(
        reverse("goods_receipt_log") + "?period=month&month=2026-07"
    )
    suppliers = [r["receipt"].supplier for r in response.context["log"]["rows"]]
    assert suppliers == ["VM supplier"]
    # The headline totals must narrow with the list, not sit above it unscoped.
    assert response.context["log"]["quantity"] == 3


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_a_manager_cannot_open_another_offices_receipt_by_pk(
    client, django_user_model, item, offices
):
    """Filtering the list does not stop a typed URL - the gap that let a
    manager decide another office's deduction."""
    velky_meder, gyor = offices
    theirs = _receipt(item, date(2026, 7, 15), office=gyor)

    manager = django_user_model.objects.create_user(
        email="manazer@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([velky_meder])
    client.force_login(manager)

    assert (
        client.get(reverse("goods_receipt_detail", args=[theirs.pk])).status_code == 403
    )


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_a_manager_can_open_their_own_offices_receipt(
    client, django_user_model, item, offices
):
    """Guard the opposite failure: a blanket 403 would pass the test above."""
    velky_meder, _gyor = offices
    mine = _receipt(item, date(2026, 7, 14), office=velky_meder)

    manager = django_user_model.objects.create_user(
        email="manazer@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([velky_meder])
    client.force_login(manager)

    response = client.get(reverse("goods_receipt_detail", args=[mine.pk]))
    assert response.status_code == 200
    assert response.context["quantity"] == 3
    assert response.context["value"] == Decimal("30.00")


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_an_observer_sees_every_office(client, django_user_model, item, offices):
    velky_meder, gyor = offices
    _receipt(item, date(2026, 7, 14), office=velky_meder)
    _receipt(item, date(2026, 7, 15), office=gyor)

    observer = django_user_model.objects.create_user(
        email="pozorovatel@demo.jober.test", password="x", role="observer"
    )
    client.force_login(observer)

    response = client.get(
        reverse("goods_receipt_log") + "?period=month&month=2026-07"
    )
    assert len(response.context["log"]["rows"]) == 2


# --- detail view -------------------------------------------------------------


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_the_detail_view_lists_the_lines(client, django_user_model, item):
    other = EquipmentItem.objects.create(name="Vest", size="M")
    receipt = receive_stock(
        received_on=date(2026, 7, 14),
        lines=[
            {"item": item, "quantity": 2, "total_value": Decimal("20.00")},
            {"item": other, "quantity": 5, "total_value": Decimal("37.50")},
        ],
        operation_key=uuid4(),
    )
    manager = django_user_model.objects.create_user(
        email="manazer@demo.jober.test", password="x", role="manager"
    )
    client.force_login(manager)

    response = client.get(reverse("goods_receipt_detail", args=[receipt.pk]))
    lines = response.context["lines"]
    assert {line.item.name for line in lines} == {"Demo boot", "Vest"}
    assert response.context["quantity"] == 7


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_an_empty_period_says_so_rather_than_failing(client, django_user_model, item):
    _receipt(item, date(2026, 7, 14))
    manager = django_user_model.objects.create_user(
        email="manazer@demo.jober.test", password="x", role="manager"
    )
    client.force_login(manager)
    response = client.get(reverse("goods_receipt_log") + "?period=month&month=2026-02")
    assert response.status_code == 200
    assert response.context["log"]["rows"] == []


# --- the seed has to make this demonstrable ---------------------------------


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_the_demo_seed_spreads_receipts_across_months(item):
    """One receipt per office in a single month makes the period filter look
    broken rather than empty. The seed now adds an earlier top-up."""
    from django.core.management import call_command

    call_command("seed_logistics")
    months = {
        row["receipt"].received_on.replace(day=1) for row in goods_receipts()["rows"]
    }
    assert len(months) >= 2, f"all seeded receipts fall in one month: {months}"


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_the_seed_is_idempotent(item):
    from django.core.management import call_command

    call_command("seed_logistics")
    first = len(goods_receipts()["rows"])
    call_command("seed_logistics")
    assert len(goods_receipts()["rows"]) == first
