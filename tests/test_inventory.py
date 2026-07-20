from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from core.accounts.permissions import Action, can
from features.logistics.models import EquipmentIssueStatus, EquipmentItem
from features.logistics.services import issue_equipment, receive_stock, return_equipment
from core.people.models import Person

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup(django_user_model):
    coord = django_user_model.objects.create_user(
        email="c@demo.jober.test", password="x", role="coordinator"
    )
    item = EquipmentItem.objects.create(name="Boots", size="42")
    receive_stock(
        received_on=date.today(), operation_key=uuid4(),
        lines=[{"item": item, "quantity": 10, "total_value": Decimal("100")}],
        actor=coord,
    )
    person = Person.objects.create(first_name="A", last_name="B")
    return coord, item, person


def test_issue_equipment_creates_issued(setup):
    coord, item, person = setup
    issue = issue_equipment(person, item, 2, actor=coord, operation_key=uuid4())
    assert issue.status == EquipmentIssueStatus.ISSUED
    assert issue.quantity == 2
    assert person.equipment_issues.filter(status=EquipmentIssueStatus.ISSUED).count() == 1


def test_return_equipment_marks_returned(setup):
    coord, item, person = setup
    issue = issue_equipment(person, item, actor=coord, operation_key=uuid4())
    return_equipment(issue, actor=coord, disposition="restock")
    issue.refresh_from_db()
    assert issue.status == EquipmentIssueStatus.RETURNED
    assert issue.returned_at is not None


def test_equipment_rbac(django_user_model):
    coord = django_user_model.objects.create_user(email="c2@demo.jober.test", password="x", role="coordinator")
    observer = django_user_model.objects.create_user(email="o@demo.jober.test", password="x", role="observer")
    assert can(coord, Action.EQUIPMENT_ISSUE_RETURN)
    assert not can(observer, Action.EQUIPMENT_ISSUE_RETURN)
