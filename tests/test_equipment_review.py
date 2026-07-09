from __future__ import annotations

from decimal import Decimal

import pytest
from django.urls import reverse

from core.accounts.permissions import Action, can
from features.logistics.models import (
    DeductionReviewStatus,
    EquipmentIssueStatus,
    EquipmentItem,
)
from features.logistics.services import (
    DeductionReviewError,
    flag_unreturned,
    issue_equipment,
    pending_deduction_reviews,
    review_deduction,
)
from core.people.models import Person
from core.projects.services import exit_person

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup(django_user_model):
    manager = django_user_model.objects.create_user(
        email="m@demo.jober.test", password="x", role="manager"
    )
    coord = django_user_model.objects.create_user(
        email="c@demo.jober.test", password="x", role="coordinator"
    )
    item = EquipmentItem.objects.create(name="Boots", size="42", unit_price=Decimal("45.00"))
    person = Person.objects.create(first_name="A", last_name="B")
    return manager, coord, item, person


def test_flag_snapshots_charge_at_unit_price(setup):
    manager, coord, item, person = setup
    issue = issue_equipment(person, item, 2, actor=coord)
    flag_unreturned(issue, actor=coord)
    issue.refresh_from_db()
    assert issue.review_status == DeductionReviewStatus.PENDING
    assert issue.charge_amount == Decimal("90.00")  # 2 × 45
    assert issue.status == EquipmentIssueStatus.ISSUED  # still physically out


def test_cannot_flag_returned_or_double_flag(setup):
    manager, coord, item, person = setup
    issue = issue_equipment(person, item, 1, actor=coord)
    flag_unreturned(issue, actor=coord)
    with pytest.raises(DeductionReviewError):
        flag_unreturned(issue, actor=coord)  # already pending


def test_approve_and_waive(setup):
    manager, coord, item, person = setup
    a = issue_equipment(person, item, 1, actor=coord)
    b = issue_equipment(person, item, 1, actor=coord)
    flag_unreturned(a, actor=coord)
    flag_unreturned(b, actor=coord)
    review_deduction(a, "approve", actor=manager, note="not returned")
    review_deduction(b, "waive", actor=manager)
    a.refresh_from_db()
    b.refresh_from_db()
    assert a.review_status == DeductionReviewStatus.APPROVED
    assert a.reviewed_by == manager and a.review_note == "not returned"
    assert b.review_status == DeductionReviewStatus.WAIVED


def test_review_requires_pending_and_valid_decision(setup):
    manager, coord, item, person = setup
    issue = issue_equipment(person, item, 1, actor=coord)
    with pytest.raises(DeductionReviewError):
        review_deduction(issue, "approve", actor=manager)  # not pending
    flag_unreturned(issue, actor=coord)
    with pytest.raises(DeductionReviewError):
        review_deduction(issue, "nonsense", actor=manager)


def test_pending_queue_total(setup):
    manager, coord, item, person = setup
    p2 = Person.objects.create(first_name="C", last_name="D")
    a = issue_equipment(person, item, 1, actor=coord)   # 45
    b = issue_equipment(p2, item, 2, actor=coord)       # 90
    flag_unreturned(a, actor=coord)
    flag_unreturned(b, actor=coord)
    review_deduction(a, "waive", actor=manager)          # leaves only b pending
    queue = pending_deduction_reviews()
    assert list(queue["issues"]) == [b]
    assert queue["total"] == Decimal("90.00")


def test_exit_leaves_flagged_items_for_review(setup):
    manager, coord, item, person = setup
    keep = issue_equipment(person, item, 1, actor=coord)
    flagged = issue_equipment(person, item, 1, actor=coord)
    flag_unreturned(flagged, actor=coord)
    exit_person(person, actor=coord, reason="left")
    keep.refresh_from_db()
    flagged.refresh_from_db()
    assert keep.status == EquipmentIssueStatus.RETURNED       # auto-returned
    assert flagged.status == EquipmentIssueStatus.ISSUED      # left for review
    assert flagged.review_status == DeductionReviewStatus.PENDING


def test_review_rbac(setup):
    manager, coord, _item, _person = setup
    assert can(manager, Action.EQUIPMENT_REVIEW_DEDUCTION)
    assert not can(coord, Action.EQUIPMENT_REVIEW_DEDUCTION)


def test_review_queue_view_gated(client, setup):
    manager, coord, _item, _person = setup
    url = reverse("equipment_reviews")
    client.force_login(coord)
    assert client.get(url).status_code == 403
    client.force_login(manager)
    assert client.get(url).status_code == 200
