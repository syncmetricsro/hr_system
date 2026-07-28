"""Logistics' contributions to the Staff activity page (J2).

Registered through `core.ui.registry.register_staff_activity_panel` so core can
render the page without importing this feature.

Both figures come from the domain models, not the audit log. `EquipmentIssue`
already recorded `issued_by`, and `RoomAssignment` already recorded
`assigned_by` and `created_at` - so this needed no migration. That matters
beyond convenience: `core.retention` will eventually purge audit rows for GDPR,
and statistics built on the log alone would empty themselves.
"""

from __future__ import annotations

from django.db.models import Count, Sum

from core.offices.scoping import scope_people
from features.logistics.models import RoomAssignment, EquipmentIssue


def coordinator_issuance(period, user):
    """How many items each coordinator issued in the period, by item.

    The client asked for the breakdown by item, not only a total: two
    coordinators issuing the same count of very different things is not the
    same activity.
    """
    issues = scope_people(
        EquipmentIssue.objects.filter(period.filter_q("issued_at__date")),
        user,
        prefix="person__",
    )
    rows = (
        issues.values("issued_by", "issued_by__email", "item__name", "item__size")
        .annotate(issues=Count("id"), quantity=Sum("quantity"))
        .order_by("issued_by__email", "item__name", "item__size")
    )
    by_person: dict = {}
    for row in rows:
        entry = by_person.setdefault(
            row["issued_by"],
            {"coordinator": row["issued_by__email"] or "—", "items": [], "quantity": 0},
        )
        entry["items"].append(
            {
                "item": row["item__name"],
                "size": row["item__size"],
                "quantity": row["quantity"] or 0,
            }
        )
        entry["quantity"] += row["quantity"] or 0
    return sorted(by_person.values(), key=lambda e: -e["quantity"])


def accommodation_transfers(period, user):
    """Who moved which worker, from where to where, in the period.

    A transfer is an assignment created while the worker already had an earlier
    one; a first placement is not a transfer. The previous accommodation is
    read from that earlier assignment rather than stored, so nothing here
    depends on a denormalised trail.
    """
    assignments = scope_people(
        RoomAssignment.objects.filter(period.filter_q("created_at__date")),
        user,
        prefix="person__",
    ).select_related("person", "room__accommodation", "assigned_by")

    rows = []
    for assignment in assignments.order_by("-created_at"):
        previous = (
            RoomAssignment.objects.filter(
                person=assignment.person, created_at__lt=assignment.created_at
            )
            .select_related("room__accommodation")
            .order_by("-created_at")
            .first()
        )
        if previous is None:
            continue  # a first placement, not a transfer
        rows.append(
            {
                "person": assignment.person,
                "moved_from": previous.room.accommodation,
                "moved_to": assignment.room.accommodation,
                "by": assignment.assigned_by,
                "when": assignment.created_at,
            }
        )
    return rows


def staff_activity_panel(request):
    """Context for this feature's panels, or None when it contributes nothing.

    The period arrives on the request rather than as an argument: the registry
    calls every contribution with `(request)` alone, and the Staff activity view
    attaches `request.reporting_period` before rendering.
    """
    from core.ui.registry import flag_enabled

    period = getattr(request, "reporting_period", None)
    if period is None:
        return None
    if not flag_enabled("equipment") and not flag_enabled("accommodation"):
        return None
    context = {}
    if flag_enabled("equipment"):
        context["coordinator_issuance"] = coordinator_issuance(period, request.user)
    if flag_enabled("accommodation"):
        context["accommodation_transfers"] = accommodation_transfers(
            period, request.user
        )
    return context or None
