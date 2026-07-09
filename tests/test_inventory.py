from __future__ import annotations

import pytest

from core.accounts.permissions import Action, can
from features.logistics.models import EquipmentIssueStatus, EquipmentItem
from features.logistics.services import issue_equipment, return_equipment
from core.people.models import Person

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup(django_user_model):
    coord = django_user_model.objects.create_user(
        email="c@demo.jober.test", password="x", role="coordinator"
    )
    item = EquipmentItem.objects.create(name="Boots", size="42")
    person = Person.objects.create(first_name="A", last_name="B")
    return coord, item, person


def test_issue_equipment_creates_issued(setup):
    coord, item, person = setup
    issue = issue_equipment(person, item, 2, actor=coord)
    assert issue.status == EquipmentIssueStatus.ISSUED
    assert issue.quantity == 2
    assert person.equipment_issues.filter(status=EquipmentIssueStatus.ISSUED).count() == 1


def test_return_equipment_marks_returned(setup):
    coord, item, person = setup
    issue = issue_equipment(person, item, actor=coord)
    return_equipment(issue, actor=coord)
    issue.refresh_from_db()
    assert issue.status == EquipmentIssueStatus.RETURNED
    assert issue.returned_at is not None


def test_equipment_rbac(django_user_model):
    coord = django_user_model.objects.create_user(email="c2@demo.jober.test", password="x", role="coordinator")
    observer = django_user_model.objects.create_user(email="o@demo.jober.test", password="x", role="observer")
    assert can(coord, Action.EQUIPMENT_ISSUE_RETURN)
    assert not can(observer, Action.EQUIPMENT_ISSUE_RETURN)
