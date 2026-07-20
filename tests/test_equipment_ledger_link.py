from __future__ import annotations

from decimal import Decimal
from datetime import date
from uuid import uuid4

import pytest
from django.utils import translation

from core.people.models import Person
from features.advances.models import EntryType, LedgerEntry, PayEffect
from features.logistics.models import EquipmentItem
from features.logistics.services import (
    flag_unreturned, issue_equipment, receive_stock, review_deduction,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager(django_user_model):
    return django_user_model.objects.create_user(
        email="eq-manager@demo.jober.test", password="x", role="manager"
    )


@pytest.fixture
def flagged_issue(manager):
    person = Person.objects.create(first_name="Eq", last_name="Worker")
    item = EquipmentItem.objects.create(name="Jacket", size="L", unit_price=Decimal("25.00"))
    receive_stock(
        received_on=date.today(), operation_key=uuid4(),
        lines=[{"item": item, "quantity": 2, "total_value": Decimal("50.00")}],
        actor=manager,
    )
    issue = issue_equipment(person, item, 2, actor=manager, operation_key=uuid4())
    return flag_unreturned(issue, actor=manager)


def test_approved_charge_creates_linked_ledger_entry(settings, manager, flagged_issue):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, "advances": True}
    with translation.override("en"):  # note text is created in the actor's locale
        review_deduction(flagged_issue, "approve", actor=manager)
    entry = LedgerEntry.objects.get(person=flagged_issue.person)
    assert entry.entry_type == EntryType.PAY_DEDUCTION
    assert entry.pay_effect == PayEffect.DEDUCT
    assert entry.amount == Decimal("50.00")  # 25 × 2, positive magnitude
    assert f"issue #{flagged_issue.pk}" in entry.note


def test_waive_creates_no_entry(settings, manager, flagged_issue):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, "advances": True}
    review_deduction(flagged_issue, "waive", actor=manager)
    assert not LedgerEntry.objects.filter(person=flagged_issue.person).exists()


def test_flag_off_creates_no_entry(settings, manager, flagged_issue):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, "advances": False}
    review_deduction(flagged_issue, "approve", actor=manager)
    assert not LedgerEntry.objects.filter(person=flagged_issue.person).exists()
