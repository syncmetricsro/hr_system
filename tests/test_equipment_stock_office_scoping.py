from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from django.test import override_settings

from core.accounts.permissions import user_office_scope
from core.offices.models import Office
from core.people.models import Person
from features.logistics.models import EquipmentItem, EquipmentStockLot
from features.logistics.services import (
    LogisticsWorkflowError,
    adjust_stock,
    equipment_month_report,
    equipment_stock_balance,
    issue_equipment,
    receive_stock,
    return_equipment,
    stock_ledger_enabled,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def offices():
    velky_meder = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")
    return velky_meder, gyor


@pytest.fixture
def stocked(offices):
    """One item, stock received into each of two offices."""
    velky_meder, gyor = offices
    item = EquipmentItem.objects.create(name="Demo boot", size="42")
    receive_stock(
        received_on=date(2026, 4, 1),
        operation_key=uuid4(),
        lines=[{"item": item, "quantity": 3, "total_value": Decimal("30.00")}],
        office=velky_meder,
    )
    receive_stock(
        received_on=date(2026, 4, 2),
        operation_key=uuid4(),
        lines=[{"item": item, "quantity": 5, "total_value": Decimal("50.00")}],
        office=gyor,
    )
    return {"item": item, "velky_meder": velky_meder, "gyor": gyor}


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_fifo_only_draws_from_the_persons_own_office(stocked):
    """The core of the split: a VM worker's issue consumes VM's lot, leaving
    Győr's untouched, even though Győr's lot is larger and equally old."""
    person = Person.objects.create(
        first_name="Olha", last_name="VM", office=stocked["velky_meder"]
    )
    issue_equipment(person, stocked["item"], 3, operation_key=uuid4())

    vm_lot = EquipmentStockLot.objects.get(office=stocked["velky_meder"])
    gyr_lot = EquipmentStockLot.objects.get(office=stocked["gyor"])
    assert vm_lot.remaining_quantity == 0
    assert gyr_lot.remaining_quantity == 5


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_issue_rejects_when_own_office_is_short_despite_stock_elsewhere(stocked):
    """No silent cross-office draw: VM holds 3, Győr holds 5, and a VM worker
    asking for 5 must fail rather than reach into Győr's warehouse."""
    person = Person.objects.create(
        first_name="Olha", last_name="VM", office=stocked["velky_meder"]
    )
    with pytest.raises(LogisticsWorkflowError) as exc:
        issue_equipment(person, stocked["item"], 5, operation_key=uuid4())
    # The error names the office, so the operator knows *whose* stock is short.
    assert "Velký Meder" in str(exc.value)
    assert EquipmentStockLot.objects.get(office=stocked["gyor"]).remaining_quantity == 5


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_issue_rejects_when_person_has_no_office(stocked):
    person = Person.objects.create(first_name="No", last_name="Office")
    with pytest.raises(LogisticsWorkflowError):
        issue_equipment(person, stocked["item"], 1, operation_key=uuid4())


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_stock_balance_scoped_to_manager_office(stocked, django_user_model):
    manager = django_user_model.objects.create_user(
        email="mgr@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([stocked["velky_meder"]])
    scope = user_office_scope(manager)
    assert equipment_stock_balance(offices=scope)["quantity"] == 3
    assert equipment_stock_balance(offices=scope)["value"] == Decimal("30.00")


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_stock_balance_offices_none_is_unrestricted_for_observer(
    stocked, django_user_model
):
    """offices=None must mean genuinely unfiltered - both offices' stock, plus
    any legacy office-less movement, not 'all offices'."""
    observer = django_user_model.objects.create_user(
        email="obs@demo.jober.test", password="x", role="observer"
    )
    assert user_office_scope(observer) is None
    balance = equipment_stock_balance(offices=None)
    assert balance["quantity"] == 8
    assert balance["value"] == Decimal("80.00")


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_month_report_scoped_to_one_office(stocked, django_user_model):
    manager = django_user_model.objects.create_user(
        email="mgr@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([stocked["velky_meder"]])
    scope = user_office_scope(manager)
    report = equipment_month_report(2026, 4, offices=scope)
    assert report["closing"]["quantity"] == 3
    assert report["by_type"]["receipt"]["quantity"] == 3


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_adjustment_only_affects_the_named_office(stocked):
    adjust_stock(
        stocked["item"],
        -2,
        occurred_on=date(2026, 4, 5),
        reason="damaged in VM",
        office=stocked["velky_meder"],
    )
    assert (
        EquipmentStockLot.objects.get(office=stocked["velky_meder"]).remaining_quantity
        == 1
    )
    assert EquipmentStockLot.objects.get(office=stocked["gyor"]).remaining_quantity == 5


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_return_restocks_into_the_persons_current_office(stocked):
    person = Person.objects.create(
        first_name="Olha", last_name="VM", office=stocked["velky_meder"]
    )
    issue = issue_equipment(person, stocked["item"], 3, operation_key=uuid4())
    return_equipment(issue, disposition="restock")

    restocked = (
        EquipmentStockLot.objects.filter(office=stocked["velky_meder"])
        .order_by("-id")
        .first()
    )
    assert restocked.remaining_quantity == 3
    assert EquipmentStockLot.objects.filter(office=stocked["gyor"]).count() == 1


# --- installs with no offices at all (CorvinumEU) keep the pooled ledger ---


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_pooled_ledger_still_works_when_no_offices_exist():
    """With zero Office rows the ledger behaves exactly as before this slice:
    one shared pool, no office required on the person."""
    assert Office.objects.count() == 0
    item = EquipmentItem.objects.create(name="Demo boot", size="42")
    person = Person.objects.create(first_name="No", last_name="Office")
    receive_stock(
        received_on=date(2026, 4, 1),
        operation_key=uuid4(),
        lines=[{"item": item, "quantity": 3, "total_value": Decimal("30.00")}],
    )
    issue = issue_equipment(person, item, 2, operation_key=uuid4())
    assert issue.issued_stock_value == Decimal("20.00")
    assert equipment_stock_balance()["quantity"] == 1


def test_stock_ledger_is_disabled_for_corvinum(settings):
    """Cheap insurance: the whole office-split path is dormant for CorvinumEU
    because its stock ledger is off, independent of Office rows existing."""
    if "corvinum" not in str(settings.SETTINGS_MODULE or "").lower():
        pytest.skip("only meaningful under the CorvinumEU settings lane")
    assert stock_ledger_enabled() is False
