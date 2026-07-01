from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.audit.services import record_event
from apps.logistics.models import (
    Accommodation,
    EquipmentIssue,
    EquipmentIssueStatus,
    RoomAssignment,
    RoomAssignmentStatus,
    TransportWeek,
)


class CapacityError(Exception):
    """Raised when a room is at capacity."""


@transaction.atomic
def set_room_rate(room, rate, *, actor=None):
    """Set a room's monthly rate (EUR). Recorded for reporting only (Q1)."""
    room.monthly_rate = Decimal(rate or 0)
    room.save(update_fields=["monthly_rate"])
    record_event(actor, "accommodation.rate_set", target=room, rate=str(room.monthly_rate))
    return room


@transaction.atomic
def set_assignment_rate(assignment, rate, *, actor=None):
    """Set or clear the per-assignment monthly-rate override (blank clears it)."""
    assignment.rate_override = None if rate in (None, "") else Decimal(rate)
    assignment.save(update_fields=["rate_override"])
    record_event(
        actor, "accommodation.assignment_rate_set", target=assignment,
        rate=("" if assignment.rate_override is None else str(assignment.rate_override)),
    )
    return assignment


def accommodation_cost_report():
    """Per-accommodation occupancy + monthly cost, plus a company total.

    Two figures per accommodation, both dynamic (never hardcoded):
    - ``room_cost`` — the standing monthly cost of the rooms (Σ room.monthly_rate);
    - ``assigned_cost`` — the amount attributed to housed workers
      (Σ effective_rate over active assignments, i.e. override or room rate).

    Reporting only — no automatic deduction is created (Q1 pending confirmation).
    """
    rows = []
    company = {"rooms": 0, "capacity": 0, "occupancy": 0,
               "room_cost": Decimal("0"), "assigned_cost": Decimal("0")}
    for acc in Accommodation.objects.prefetch_related("rooms__assignments"):
        rooms = list(acc.rooms.all())
        capacity = sum(r.capacity for r in rooms)
        room_cost = sum((r.monthly_rate for r in rooms), Decimal("0"))
        occupancy = 0
        assigned_cost = Decimal("0")
        for r in rooms:
            for a in r.assignments.all():
                if a.status == RoomAssignmentStatus.ACTIVE:
                    occupancy += 1
                    assigned_cost += a.effective_rate
        rows.append({
            "accommodation": acc, "rooms": len(rooms), "capacity": capacity,
            "occupancy": occupancy, "room_cost": room_cost, "assigned_cost": assigned_cost,
        })
        company["rooms"] += len(rooms)
        company["capacity"] += capacity
        company["occupancy"] += occupancy
        company["room_cost"] += room_cost
        company["assigned_cost"] += assigned_cost
    return {"rows": rows, "company": company}


@transaction.atomic
def assign_room(person, room, *, actor=None):
    """Assign a person to a room, enforcing capacity (one active room per person)."""
    # Re-check capacity against currently active assignments (excludes this person's
    # existing active room, which we are about to close).
    active = room.assignments.filter(status=RoomAssignmentStatus.ACTIVE).exclude(person=person)
    if active.count() >= room.capacity:
        raise CapacityError("Room is at full capacity.")

    today = timezone.localdate()
    for existing in person.room_assignments.filter(status=RoomAssignmentStatus.ACTIVE):
        existing.status = RoomAssignmentStatus.ENDED
        existing.end_date = today
        existing.save(update_fields=["status", "end_date"])
        record_event(actor, "room.released", target=existing, reason="reassigned")

    assignment = RoomAssignment.objects.create(
        person=person,
        room=room,
        status=RoomAssignmentStatus.ACTIVE,
        start_date=today,
        assigned_by=actor if getattr(actor, "is_authenticated", False) else None,
    )
    record_event(actor, "room.assigned", target=assignment, room=str(room))
    return assignment


@transaction.atomic
def release_room(person, *, actor=None):
    today = timezone.localdate()
    assignment = person.room_assignments.filter(status=RoomAssignmentStatus.ACTIVE).first()
    if assignment is not None:
        assignment.status = RoomAssignmentStatus.ENDED
        assignment.end_date = today
        assignment.save(update_fields=["status", "end_date"])
        record_event(actor, "room.released", target=assignment)
    return assignment


def issued_equipment_value(person=None):
    """Total value of currently-issued equipment (qty x unit_price), optionally
    scoped to one person. Latest-manual-price valuation (round-4 confirmed)."""
    from decimal import Decimal

    from django.db.models import DecimalField, ExpressionWrapper, F, Sum

    qs = EquipmentIssue.objects.filter(status=EquipmentIssueStatus.ISSUED)
    if person is not None:
        qs = qs.filter(person=person)
    total = qs.aggregate(
        value=Sum(
            ExpressionWrapper(
                F("quantity") * F("item__unit_price"),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            )
        )
    )["value"]
    return total or Decimal("0")


@transaction.atomic
def issue_equipment(person, item, quantity=1, *, actor=None):
    issue = EquipmentIssue.objects.create(
        person=person,
        item=item,
        quantity=max(1, int(quantity or 1)),
        status=EquipmentIssueStatus.ISSUED,
        issued_by=actor if getattr(actor, "is_authenticated", False) else None,
    )
    record_event(actor, "equipment.issued", target=issue, item=str(item))
    return issue


@transaction.atomic
def record_transport_week(project, week_start, headcount, *, actor=None, note: str = ""):
    """Record/update a project's weekly transport headcount."""
    week, _created = TransportWeek.objects.update_or_create(
        project=project,
        week_start=week_start,
        defaults={
            "headcount": max(0, int(headcount or 0)),
            "note": note,
            "recorded_by": actor if getattr(actor, "is_authenticated", False) else None,
        },
    )
    record_event(actor, "transport.week_recorded", target=week, project=project.code)
    return week


@transaction.atomic
def return_equipment(issue, *, actor=None):
    if issue.status == EquipmentIssueStatus.RETURNED:
        return issue
    issue.status = EquipmentIssueStatus.RETURNED
    issue.returned_at = timezone.now()
    issue.save(update_fields=["status", "returned_at"])
    record_event(actor, "equipment.returned", target=issue)
    return issue
