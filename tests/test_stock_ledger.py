from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from django.test import override_settings

from core.people.models import Person
from features.logistics.models import EquipmentItem, EquipmentStockMovement
from features.logistics.services import (
    LogisticsWorkflowError,
    equipment_month_report,
    equipment_stock_balance,
    issue_equipment,
    receive_stock,
    return_equipment,
)

pytestmark = pytest.mark.django_db


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_fifo_preserves_lot_value_and_restock_snapshot():
    item = EquipmentItem.objects.create(name="Demo boot", size="38")
    person = Person.objects.create(first_name="Fictional", last_name="Worker")
    receive_stock(
        received_on=date(2026, 4, 1), operation_key=uuid4(),
        lines=[{"item": item, "quantity": 3, "total_value": Decimal("10.00")}],
    )
    receive_stock(
        received_on=date(2026, 4, 2), operation_key=uuid4(),
        lines=[{"item": item, "quantity": 2, "total_value": Decimal("9.00")}],
    )
    issue = issue_equipment(person, item, 4, operation_key=uuid4())
    assert issue.issued_stock_value == Decimal("14.50")
    assert equipment_stock_balance()["value"] == Decimal("4.50")
    return_equipment(issue, disposition="restock")
    assert equipment_stock_balance()["value"] == Decimal("19.00")


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_stock_operations_are_idempotent_and_overdraw_rolls_back():
    item = EquipmentItem.objects.create(name="Demo trousers", size="M")
    person = Person.objects.create(first_name="Demo", last_name="Person")
    key = uuid4()
    first = receive_stock(
        received_on=date(2026, 5, 1), operation_key=key,
        lines=[{"item": item, "quantity": 2, "total_value": Decimal("20")}],
    )
    assert receive_stock(
        received_on=date(2026, 5, 1), operation_key=key,
        lines=[{"item": item, "quantity": 2, "total_value": Decimal("20")}],
    ).pk == first.pk
    with pytest.raises(LogisticsWorkflowError):
        issue_equipment(person, item, 3, operation_key=uuid4())
    assert not person.equipment_issues.exists()
    assert equipment_stock_balance()["quantity"] == 2
    with pytest.raises(LogisticsWorkflowError):
        issue_equipment(person, item, 1)
    issue_key = uuid4()
    issue = issue_equipment(person, item, 1, operation_key=issue_key)
    assert issue_equipment(person, item, 1, operation_key=issue_key).pk == issue.pk
    assert equipment_stock_balance()["quantity"] == 1
    # The current-date issue does not rewrite the historical May closing balance.
    assert equipment_month_report(2026, 5)["closing"]["value"] == Decimal("20")
    movement = EquipmentStockMovement.objects.first()
    with pytest.raises(ValueError):
        movement.save()


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=False)
def test_non_jober_policy_allows_legacy_issue_without_receipt():
    item = EquipmentItem.objects.create(name="Legacy coat")
    person = Person.objects.create(first_name="Legacy", last_name="Worker")
    assert issue_equipment(person, item).issued_stock_value is None
