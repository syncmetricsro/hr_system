from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from core.people.models import Person
from features.logistics.models import Accommodation, Room, RoomAssignment, RoomAssignmentStatus
from features.logistics.services import accommodation_month_report, set_accommodation_cost_period

pytestmark = pytest.mark.django_db


def test_month_report_prorates_person_days_and_does_not_create_recovery():
    accommodation = Accommodation.objects.create(name="Fictional residence")
    room = Room.objects.create(accommodation=accommodation, label="A", capacity=2)
    set_accommodation_cost_period(
        accommodation, effective_month=date(2024, 2, 1), capacity=2,
        per_head_cost=Decimal("180"),
    )
    person = Person.objects.create(first_name="Demo", last_name="Resident")
    RoomAssignment.objects.create(
        person=person, room=room, status=RoomAssignmentStatus.ENDED,
        start_date=date(2024, 2, 15), end_date=date(2024, 3, 1),
        worker_payment_monthly=Decimal("100"),
    )
    row = accommodation_month_report(2024, 2)["rows"][0]
    assert row["occupied_days"] == 15
    assert row["standing_cost"] == Decimal("360.00")
    assert row["occupied_cost"] == Decimal("93.10")
    assert row["payments"] == Decimal("51.72")
    assert row["empty_bed_loss"] == Decimal("266.90")
    assert row["margin"] == Decimal("-308.28")
    assert person.room_assignments.count() == 1
