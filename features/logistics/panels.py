"""Person-card and reports contributions of the logistics feature."""

from __future__ import annotations

from uuid import uuid4

from django.urls import reverse
from django.utils.translation import gettext as _

from core.accounts.permissions import Action, user_office_scope
from core.accounts.permissions import can as user_can
from core.ui.registry import flag_enabled
from features.logistics.forms import assignable_rooms
from features.logistics.models import (
    EquipmentItem,
    EquipmentIssueStatus,
    Room,
    RoomAssignment,
    RoomAssignmentStatus,
)
from features.logistics.services import (
    equipment_stock_balance,
    issued_equipment_value,
    pending_deduction_reviews,
    stock_ledger_enabled,
)


def room_panel(request, person):
    if not flag_enabled("accommodation"):
        return None
    return {
        "current_room": person.room_assignments.filter(
            status=RoomAssignmentStatus.ACTIVE
        )
        .select_related("room__accommodation")
        .first(),
        "rooms": assignable_rooms(request.user),
    }


def equipment_panel(request, person):
    if not flag_enabled("equipment"):
        return None
    stock_enabled = stock_ledger_enabled()
    items = list(EquipmentItem.objects.filter(is_active=True))
    # Availability is the person's *own* office's stock (ADR 0026 Phase B) -
    # that is the only warehouse issue_equipment will draw from, so showing a
    # company-wide number here would promise stock the issue would reject.
    available = (
        {
            row["item_id"]: row["quantity"]
            for row in equipment_stock_balance(offices=user_office_scope(request.user))[
                "rows"
            ]
        }
        if stock_enabled
        else {}
    )
    for item in items:
        item.available_quantity = available.get(item.pk, 0)
    return {
        "issued_equipment": person.equipment_issues.filter(
            status=EquipmentIssueStatus.ISSUED
        ).select_related("item"),
        "equipment_items": items,
        "issued_value": issued_equipment_value(person, user=request.user),
        "show_person_value": not stock_enabled,
        "stock_enabled": stock_enabled,
        "operation_key": uuid4(),
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
    # ADR 0026 Phase B: an aggregate over other offices' rooms is still a read
    # of their accommodation data - scope the tile the same as the list it
    # links to, or a VM manager's dashboard would silently count Győr's beds.
    scope = user_office_scope(request.user)
    rooms = Room.objects.all()
    assignments = RoomAssignment.objects.filter(status=RoomAssignmentStatus.ACTIVE)
    if scope is not None:
        rooms = rooms.filter(accommodation__office__in=scope)
        assignments = assignments.filter(room__accommodation__office__in=scope)
    capacity = sum(rooms.values_list("capacity", flat=True))
    occupied = assignments.count()
    tile = {"label": _("Occupancy"), "value": f"{occupied}/{capacity}"}
    if user_can(request.user, Action.ACCOMMODATION_MANAGE):
        tile["url"] = reverse("accommodation_costs")
        tile["tooltip_heading"] = _("Review accommodation occupancy")
        tile["tooltip_body"] = _(
            "Open accommodation costs, occupied places, and assigned costs."
        )
    return tile


def reviews_badge(request):
    if not flag_enabled("equipment"):
        return None
    if not user_can(request.user, Action.EQUIPMENT_REVIEW_DEDUCTION):
        return None
    count = pending_deduction_reviews(request.user)["issues"].count()
    if not count:
        return None
    return {"count": count, "severe": False}


def equipment_value_tile(request):
    if not flag_enabled("equipment"):
        return None
    if stock_ledger_enabled():
        balance = equipment_stock_balance(offices=user_office_scope(request.user))
        tile = {"label": _("Warehouse stock"), "value": f"{balance['value']} EUR"}
        if user_can(request.user, Action.EQUIPMENT_VIEW_STOCK):
            tile["url"] = reverse("equipment_stock")
            tile["tooltip_heading"] = _("Review warehouse stock")
            tile["tooltip_body"] = _(
                "Open current quantities, value, and monthly stock movements."
            )
        return tile
    value = issued_equipment_value(user=request.user)
    tile = {"label": _("Equipment value"), "value": f"{value} EUR"}
    if user_can(request.user, Action.EQUIPMENT_REVIEW_DEDUCTION):
        tile["url"] = reverse("equipment_reviews")
        tile["tooltip_heading"] = _("Review equipment exceptions")
        tile["tooltip_body"] = _(
            "Open issued equipment awaiting return or a deduction decision."
        )
    return tile
