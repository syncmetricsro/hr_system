from __future__ import annotations

import pytest
from django.utils import translation

from core.people.models import InactiveReason, LifecycleStatus, Person
from core.people.services import inactive_by_reason

pytestmark = pytest.mark.django_db


def _inactive(name, reason=None, archived=False):
    return Person.objects.create(
        first_name=name, last_name="X",
        lifecycle_status=LifecycleStatus.INACTIVE,
        inactive_reason=reason, is_archived=archived,
    )


def test_counts_group_by_reason_desc():
    sick = InactiveReason.objects.create(label="Sick (t)")
    left = InactiveReason.objects.create(label="Left (t)")
    _inactive("a", sick)
    _inactive("b", sick)
    _inactive("c", left)
    Person.objects.create(first_name="avail", last_name="X")  # AVAILABLE, excluded

    rows = inactive_by_reason()
    assert rows[0] == {"value": sick.pk, "label": "Sick (t)", "count": 2}
    assert {"value": left.pk, "label": "Left (t)", "count": 1} in rows
    assert sum(r["count"] for r in rows) == 3


def test_null_reason_bucketed():
    _inactive("noreason")  # inactive, no reason
    with translation.override("en"):
        rows = inactive_by_reason()
    assert rows == [{"value": "none", "label": "No reason", "count": 1}]


def test_archived_excluded_by_default():
    reason = InactiveReason.objects.create(label="Suspended (t)")
    _inactive("live", reason)
    _inactive("gone", reason, archived=True)
    assert inactive_by_reason() == [
        {"value": reason.pk, "label": "Suspended (t)", "count": 1}
    ]
    assert inactive_by_reason(include_archived=True)[0]["count"] == 2


def test_empty_when_no_inactive():
    Person.objects.create(first_name="avail", last_name="X")
    assert inactive_by_reason() == []
