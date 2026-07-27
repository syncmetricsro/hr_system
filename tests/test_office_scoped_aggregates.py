"""Aggregates are the blind spot in ADR 0026, so they get their own file.

Office scoping has two enforcement points: a filter on every list, and an
``_assert_..._in_scope`` guard on every view that takes an object pk. Aggregates
fall between them. They open no single record, so no guard fires; and they are
not obviously "lists", so the filter gets forgotten. Three such leaks have now
shipped - a dashboard tile summing every office's rooms, the audit log, and the
accommodation cost report - each found while doing something else.

This file exists so the next one is found on purpose. Every test here was
written against the *unfixed* code first and observed to fail.

The equipment deduction queue was the worst of the set: it is not merely a
read. A manager could post another office's issue pk and charge money to a
worker they have no business seeing.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.apps import apps as django_apps
from django.urls import reverse

from core.offices.models import Office
from core.people.models import Person

if not django_apps.is_installed("features.logistics"):
    pytest.skip("Jober feature set not installed", allow_module_level=True)

from features.logistics.models import (  # noqa: E402
    DeductionReviewStatus,
    EquipmentIssue,
    EquipmentIssueStatus,
    EquipmentItem,
)
from features.logistics.services import (  # noqa: E402
    issued_equipment_value,
    pending_deduction_reviews,
)

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


@pytest.fixture
def offices():
    return (
        Office.objects.create(name="Velký Meder", code="VM", country="SK"),
        Office.objects.create(name="Győr", code="GYR", country="HU"),
    )


@pytest.fixture
def manager(django_user_model, offices):
    """A manager of Velký Meder only."""
    user = django_user_model.objects.create_user(
        email="manazer@demo.jober.test", password="x", role="manager"
    )
    user.offices.set([offices[0]])
    return user


@pytest.fixture
def observer(django_user_model):
    return django_user_model.objects.create_user(
        email="pozorovatel@demo.jober.test", password="x", role="observer"
    )


def _flagged_issue(office, *, charge="30.00"):
    person = Person.objects.create(
        first_name="Farrukh", last_name="Tashkentov", office=office
    )
    item = EquipmentItem.objects.create(name="Helmet", unit_price=Decimal("30.00"))
    return EquipmentIssue.objects.create(
        person=person,
        item=item,
        quantity=1,
        status=EquipmentIssueStatus.ISSUED,
        review_status=DeductionReviewStatus.PENDING,
        charge_amount=Decimal(charge),
    )


# --- the equipment deduction queue -----------------------------------------


def test_the_review_queue_hides_another_offices_issues(manager, offices):
    _flagged_issue(offices[1])
    assert list(pending_deduction_reviews(manager)["issues"]) == []


def test_the_queue_total_narrows_with_the_queue(manager, offices):
    """The total is the figure a manager acts on; leaking it in aggregate is
    the same disclosure as leaking the rows."""
    _flagged_issue(offices[0], charge="30.00")
    _flagged_issue(offices[1], charge="500.00")
    assert pending_deduction_reviews(manager)["total"] == Decimal("30.00")


def test_an_observer_still_sees_every_office(observer, offices):
    _flagged_issue(offices[0])
    _flagged_issue(offices[1])
    assert pending_deduction_reviews(observer)["issues"].count() == 2


def test_a_manager_cannot_decide_another_offices_deduction(client, manager, offices):
    """The one that is a write, not a read. Filtering the queue does not stop
    a posted pk, and this decision charges money to a named worker."""
    issue = _flagged_issue(offices[1])
    client.force_login(manager)
    response = client.post(
        reverse("review_deduction", args=[issue.pk]),
        {"decision": "approve", "note": "x"},
    )
    issue.refresh_from_db()
    assert response.status_code == 403
    assert issue.review_status == DeductionReviewStatus.PENDING


def test_a_manager_can_still_decide_their_own_offices_deduction(
    client, manager, offices
):
    """Guard the opposite failure: a 403 on everything would pass the test
    above while breaking the feature."""
    issue = _flagged_issue(offices[0])
    client.force_login(manager)
    client.post(
        reverse("review_deduction", args=[issue.pk]),
        {"decision": "waive", "note": "x"},
    )
    issue.refresh_from_db()
    assert issue.review_status != DeductionReviewStatus.PENDING


# --- the issued-equipment value tile ----------------------------------------


def test_the_equipment_value_tile_sums_only_the_managers_offices(manager, offices):
    _flagged_issue(offices[0], charge="30.00")
    _flagged_issue(offices[1], charge="500.00")
    # 1 helmet x 30.00, the Velký Meder issue alone.
    assert issued_equipment_value(user=manager) == Decimal("30.00")


def test_the_equipment_value_tile_is_unrestricted_for_an_observer(observer, offices):
    _flagged_issue(offices[0])
    _flagged_issue(offices[1])
    assert issued_equipment_value(user=observer) == Decimal("60.00")


# --- the None sentinel on a tenant that has no offices yet ------------------


def test_finance_renders_on_a_tenant_with_no_offices(client, django_user_model):
    """`user_office_scope` returns None both for an unrestricted caller *and*
    when no Office rows exist at all. Finance handled only the first reading
    and passed the sentinel straight into `office__in=`, which raises - a 500,
    not a leak.

    This is not hypothetical: an instance with no offices is precisely the
    empty one the client asked to be handed for their trial (J11). A manager
    opening Finance before creating an office got an error page.
    """
    assert not Office.objects.exists()
    manager = django_user_model.objects.create_user(
        email="manazer@demo.jober.test", password="x", role="manager"
    )
    client.force_login(manager)
    response = client.get(reverse("finance_summary"))
    assert response.status_code == 200
