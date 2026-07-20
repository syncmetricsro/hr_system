from __future__ import annotations

from decimal import Decimal

import pytest
from django.test import override_settings

from features.logistics.models import EquipmentItem
from features.logistics.services import issue_equipment, issued_equipment_value, return_equipment
from core.people.models import Person

pytestmark = pytest.mark.django_db


@pytest.fixture
def coord(django_user_model):
    return django_user_model.objects.create_user(email="c@demo.jober.test", password="x", role="coordinator")


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=False)
def test_issued_value_sums_qty_times_price(coord):
    boots = EquipmentItem.objects.create(name="Boots", unit_price=Decimal("45.00"))
    vest = EquipmentItem.objects.create(name="Vest", unit_price=Decimal("8.50"))
    person = Person.objects.create(first_name="A", last_name="B")
    issue_equipment(person, boots, 1, actor=coord)
    issue_equipment(person, vest, 2, actor=coord)
    assert issued_equipment_value(person) == Decimal("62.00")   # 45 + 2*8.50
    assert issued_equipment_value() == Decimal("62.00")          # company-wide


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=False)
def test_returned_equipment_excluded_from_value(coord):
    boots = EquipmentItem.objects.create(name="Boots", unit_price=Decimal("45.00"))
    person = Person.objects.create(first_name="A", last_name="B")
    issue = issue_equipment(person, boots, 1, actor=coord)
    return_equipment(issue, actor=coord)
    assert issued_equipment_value(person) == Decimal("0")


def test_value_zero_with_no_issues():
    assert issued_equipment_value() == Decimal("0")
