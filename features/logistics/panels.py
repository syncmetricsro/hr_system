"""Person-card and reports contributions of the logistics feature."""

from __future__ import annotations

from django.urls import reverse
from django.utils.translation import gettext as _

from core.accounts.permissions import Action
from core.accounts.permissions import can as user_can
from core.ui.registry import flag_enabled
from features.logistics.models import (
    EquipmentItem,
    EquipmentIssueStatus,
    Room,
    RoomAssignment,
    RoomAssignmentStatus,
)
from features.logistics.services import issued_equipment_value


def room_panel(request, person):
    if not flag_enabled("accommodation"):
        return None
    return {
        "current_room": person.room_assignments.filter(
            status=RoomAssignmentStatus.ACTIVE
        ).select_related("room__accommodation").first(),
        "rooms": Room.objects.select_related("accommodation").filter(
            accommodation__is_active=True
        ),
    }


def equipment_panel(request, person):
    if not flag_enabled("equipment"):
        return None
    return {
        "issued_equipment": person.equipment_issues.filter(
            status=EquipmentIssueStatus.ISSUED
        ).select_related("item"),
        "equipment_items": EquipmentItem.objects.filter(is_active=True),
        "issued_value": issued_equipment_value(person),
    }


def holds_resources(person) -> bool:
    """Exit is relevant while the person still holds a room or issued gear."""
    return (
        person.room_assignments.filter(status=RoomAssignmentStatus.ACTIVE).exists()
        or person.equipment_issues.filter(status=EquipmentIssueStatus.ISSUED).exists()
    )


def occupancy_tile(request):
    if not flag_enabled("accommodation"):
        return None
    capacity = sum(Room.objects.values_list("capacity", flat=True))
    occupied = RoomAssignment.objects.filter(status=RoomAssignmentStatus.ACTIVE).count()
    tile = {"label": _("Occupancy"), "value": f"{occupied}/{capacity}"}
    if user_can(request.user, Action.ACCOMMODATION_MANAGE):
        tile["url"] = reverse("accommodation_costs")
    return tile


def equipment_value_tile(request):
    if not flag_enabled("equipment"):
        return None
    tile = {"label": _("Equipment value"), "value": f"{issued_equipment_value()} EUR"}
    if user_can(request.user, Action.EQUIPMENT_REVIEW_DEDUCTION):
        tile["url"] = reverse("equipment_reviews")
    return tile
