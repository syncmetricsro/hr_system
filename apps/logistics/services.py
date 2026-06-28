from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.audit.services import record_event
from apps.logistics.models import RoomAssignment, RoomAssignmentStatus


class CapacityError(Exception):
    """Raised when a room is at capacity."""


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
