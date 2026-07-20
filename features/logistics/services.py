from __future__ import annotations

import calendar
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext as _

from core.audit.services import record_event
from features.logistics.models import (
    Accommodation,
    AccommodationCostPeriod,
    DeductionReviewStatus,
    EquipmentItem,
    EquipmentIssue,
    EquipmentIssueStatus,
    EquipmentStockAllocation,
    EquipmentStockLot,
    EquipmentStockMovement,
    EquipmentStockMovementType,
    EquipmentStockReceipt,
    EquipmentStockReceiptLine,
    RoomAssignment,
    RoomAssignmentStatus,
    TransportWeek,
)


class CapacityError(Exception):
    """Raised when a room is at capacity."""


class LogisticsWorkflowError(Exception):
    """Raised when logistics master data or history would be made inconsistent."""


class DeductionReviewError(Exception):
    """Raised on an invalid unreturned-equipment review transition."""


def stock_ledger_enabled() -> bool:
    return bool(getattr(settings, "EQUIPMENT_STOCK_LEDGER_ENABLED", False))


@transaction.atomic
def save_equipment_item(item: EquipmentItem, *, actor=None, old=None) -> EquipmentItem:
    """Save manager-maintained catalogue data with a concise audit trail."""
    creating = item._state.adding
    item.save()
    record_event(
        actor,
        "equipment.catalog_created" if creating else "equipment.catalog_updated",
        target=item,
        old=old or {},
        new={
            "name": item.name,
            "size": item.size,
            "unit_price": str(item.unit_price),
            "is_active": item.is_active,
        },
    )
    return item


def _non_negative(value) -> Decimal:
    """Positive sign convention (confirmed with Jober 2026-06-29): rates and
    charges are never negative."""
    amount = Decimal(value or 0)
    if amount < 0:
        raise ValueError(_("Amounts use a positive convention; negative values are not allowed."))
    return amount


@transaction.atomic
def set_room_rate(room, rate, *, actor=None):
    """Set a room's monthly rate (EUR). Recorded for reporting only (Q1)."""
    room.monthly_rate = _non_negative(rate)
    room.save(update_fields=["monthly_rate"])
    record_event(actor, "accommodation.rate_set", target=room, rate=str(room.monthly_rate))
    return room


@transaction.atomic
def set_assignment_rate(assignment, rate, *, actor=None):
    """Set or clear the per-assignment monthly-rate override (blank clears it)."""
    assignment.rate_override = None if rate in (None, "") else _non_negative(rate)
    assignment.save(update_fields=["rate_override"])
    record_event(
        actor, "accommodation.assignment_rate_set", target=assignment,
        rate=("" if assignment.rate_override is None else str(assignment.rate_override)),
    )
    return assignment


CENT = Decimal("0.01")


def _money(value):
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def accommodation_month_report(year, month):
    """Prorated per-head cost/payment report; never creates payroll effects."""
    start = date(year, month, 1)
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    days = Decimal((next_month - start).days)
    rows = []
    company = {
        "capacity": 0, "occupied_days": 0, "standing_cost": Decimal("0"),
        "occupied_cost": Decimal("0"), "payments": Decimal("0"),
        "empty_bed_loss": Decimal("0"), "margin": Decimal("0"),
    }
    accommodations = Accommodation.objects.prefetch_related("rooms__assignments", "cost_periods")
    for accommodation in accommodations:
        period = next((p for p in accommodation.cost_periods.all() if p.effective_month <= start), None)
        if period is None:
            rows.append({"accommodation": accommodation, "missing_period": True})
            continue
        occupied_days = 0
        payments = Decimal("0")
        for room in accommodation.rooms.all():
            for assignment in room.assignments.all():
                occupied_from = max(assignment.start_date or start, start)
                occupied_until = min(assignment.end_date or next_month, next_month)
                overlap = max(0, (occupied_until - occupied_from).days)
                if overlap:
                    occupied_days += overlap
                    payments += Decimal(assignment.worker_payment_monthly) * Decimal(overlap) / days
        standing = Decimal(period.capacity) * period.per_head_cost
        occupied_cost = period.per_head_cost * Decimal(occupied_days) / days
        empty_loss = max(Decimal("0"), standing - occupied_cost)
        row = {
            "accommodation": accommodation, "missing_period": False,
            "capacity": period.capacity, "occupied_days": occupied_days,
            "standing_cost": _money(standing), "occupied_cost": _money(occupied_cost),
            "payments": _money(payments), "empty_bed_loss": _money(empty_loss),
            "margin": _money(payments - standing),
        }
        rows.append(row)
        for key in company:
            if key in row:
                company[key] += row[key]
    for key in ("standing_cost", "occupied_cost", "payments", "empty_bed_loss", "margin"):
        company[key] = _money(company[key])
    return {"year": year, "month": month, "rows": rows, "company": company}


def accommodation_cost_report():
    """Legacy room-rate report retained for historical records and other clients."""
    rows = []
    company = {
        "rooms": 0, "capacity": 0, "occupancy": 0,
        "room_cost": Decimal("0"), "assigned_cost": Decimal("0"),
    }
    for accommodation in Accommodation.objects.prefetch_related("rooms__assignments"):
        rooms = list(accommodation.rooms.all())
        capacity = sum(room.capacity for room in rooms)
        room_cost = sum((room.monthly_rate for room in rooms), Decimal("0"))
        active = [
            assignment
            for room in rooms
            for assignment in room.assignments.all()
            if assignment.status == RoomAssignmentStatus.ACTIVE
        ]
        assigned_cost = sum((assignment.effective_rate for assignment in active), Decimal("0"))
        row = {
            "accommodation": accommodation, "rooms": len(rooms),
            "capacity": capacity, "occupancy": len(active),
            "room_cost": room_cost, "assigned_cost": assigned_cost,
        }
        rows.append(row)
        for key in company:
            company[key] += row[key]
    return {"rows": rows, "company": company}


@transaction.atomic
def set_accommodation_cost_period(accommodation, *, effective_month, capacity,
                                  per_head_cost, actor=None):
    period, _created = AccommodationCostPeriod.objects.update_or_create(
        accommodation=accommodation, effective_month=effective_month.replace(day=1),
        defaults={
            "capacity": int(capacity), "per_head_cost": _non_negative(per_head_cost),
            "recorded_by": _actor(actor),
        },
    )
    record_event(actor, "accommodation.cost_period_set", target=period)
    return period


@transaction.atomic
def set_assignment_payment(assignment, amount, *, actor=None):
    assignment.worker_payment_monthly = _non_negative(amount)
    assignment.save(update_fields=("worker_payment_monthly",))
    record_event(
        actor, "accommodation.worker_payment_set", target=assignment,
        amount=str(assignment.worker_payment_monthly),
    )
    return assignment


@transaction.atomic
def assign_room(person, room, *, actor=None, worker_payment_monthly=0):
    """Assign a person to a room, enforcing capacity (one active room per person)."""
    # Re-check capacity against currently active assignments (excludes this person's
    # existing active room, which we are about to close).
    if not room.is_active or not room.accommodation.is_active:
        raise CapacityError(_("Only active rooms in active locations can be assigned."))
    active = room.assignments.filter(status=RoomAssignmentStatus.ACTIVE).exclude(person=person)
    if active.count() >= room.capacity:
        raise CapacityError(_("Room is at full capacity."))

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
        worker_payment_monthly=_non_negative(worker_payment_monthly),
    )
    record_event(actor, "room.assigned", target=assignment, room=str(room))
    return assignment


def exit_reconcile(person, *, actor=None):
    """Exit-hook (registered in LogisticsConfig.ready): release the room and
    return un-flagged issued equipment; items flagged for deduction review stay
    (Q2). Idempotent — safe if exit runs twice. Sub-feature flags gate each part."""
    from django.conf import settings

    flags = getattr(settings, "FEATURE_FLAGS", {})
    if flags.get("accommodation", True):
        release_room(person, actor=actor)
    if flags.get("equipment", True):
        if stock_ledger_enabled():
            return
        for issue in person.equipment_issues.filter(
            status=EquipmentIssueStatus.ISSUED, review_status=DeductionReviewStatus.NONE
        ):
            return_equipment(issue, actor=actor)


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

    from django.db.models import Case, DecimalField, ExpressionWrapper, F, Sum, When

    qs = EquipmentIssue.objects.filter(status=EquipmentIssueStatus.ISSUED)
    if person is not None:
        qs = qs.filter(person=person)
    total = qs.aggregate(
        value=Sum(
            Case(
                When(issued_stock_value__isnull=False, then=F("issued_stock_value")),
                default=ExpressionWrapper(
                    F("quantity") * F("item__unit_price"),
                    output_field=DecimalField(max_digits=14, decimal_places=2),
                ),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            )
        )
    )["value"]
    return total or Decimal("0")


# Callables (issue, actor=None) run after a deduction charge is APPROVED.
# Other features (e.g. the advances ledger, ADR 0022 §5.8) register here to
# turn the approved charge into their own linked record. Handlers must be
# idempotent per issue; review_deduction's PENDING guard fires them once.
deduction_approved_hooks: list = []


def register_deduction_approved_hook(fn) -> None:
    if fn not in deduction_approved_hooks:
        deduction_approved_hooks.append(fn)


@transaction.atomic
def flag_unreturned(issue, *, actor=None):
    """Flag an issued-but-not-returned item for manager review (Q2 safe default).

    Snapshots the charge at the item's current unit price × quantity. Does not
    deduct anything — it only opens a review for a manager to approve or waive.
    """
    if issue.status != EquipmentIssueStatus.ISSUED:
        raise DeductionReviewError("Only an issued item can be flagged as unreturned.")
    if issue.review_status != DeductionReviewStatus.NONE:
        raise DeductionReviewError("This item is already under review.")
    issue.review_status = DeductionReviewStatus.PENDING
    issue.charge_amount = (
        issue.issued_stock_value
        if issue.issued_stock_value is not None
        else Decimal(issue.item.unit_price) * issue.quantity
    )
    issue.save(update_fields=["review_status", "charge_amount"])
    record_event(actor, "equipment.flagged_unreturned", target=issue, amount=str(issue.charge_amount))
    return issue


@transaction.atomic
def review_deduction(issue, decision, *, actor=None, note: str = ""):
    """Manager decision on a pending unreturned-item charge: ``approve`` records
    the charge as approved-for-recovery (no automatic payroll deduction), ``waive``
    drops it. Both are audited."""
    if issue.review_status != DeductionReviewStatus.PENDING:
        raise DeductionReviewError("This item is not pending review.")
    if decision == "approve":
        issue.review_status = DeductionReviewStatus.APPROVED
    elif decision == "waive":
        issue.review_status = DeductionReviewStatus.WAIVED
    else:
        raise DeductionReviewError("Decision must be 'approve' or 'waive'.")
    issue.reviewed_by = actor if getattr(actor, "is_authenticated", False) else None
    issue.reviewed_at = timezone.now()
    issue.review_note = note or ""
    issue.save(update_fields=["review_status", "reviewed_by", "reviewed_at", "review_note"])
    record_event(actor, "equipment.deduction_reviewed", target=issue, decision=decision)
    if issue.review_status == DeductionReviewStatus.APPROVED:
        for hook in deduction_approved_hooks:
            hook(issue, actor=actor)
    return issue


def pending_deduction_reviews():
    """Manager review queue: items flagged unreturned and awaiting a decision,
    with the outstanding charge total (dynamic)."""
    qs = (
        EquipmentIssue.objects.filter(review_status=DeductionReviewStatus.PENDING)
        .select_related("person", "item")
        .order_by("-issued_at")
    )
    total = sum((i.charge_amount or Decimal("0") for i in qs), Decimal("0"))
    return {"issues": qs, "total": total}


def _actor(actor):
    return actor if getattr(actor, "is_authenticated", False) else None


def _create_inbound_lot(*, item, movement_type, occurred_on, quantity, value,
                        actor=None, reason="", receipt_line=None, issue=None):
    movement = EquipmentStockMovement.objects.create(
        item=item, movement_type=movement_type, occurred_on=occurred_on,
        quantity_delta=quantity, value_delta=value, actor=_actor(actor),
        reason=reason, receipt_line=receipt_line, issue=issue,
    )
    EquipmentStockLot.objects.create(
        inbound_movement=movement, item=item, received_on=occurred_on,
        initial_quantity=quantity, initial_value=value,
        remaining_quantity=quantity, remaining_value=value,
    )
    return movement


def _consume_fifo(*, item, quantity, movement_type, occurred_on, actor=None,
                  reason="", issue=None):
    lots = list(
        EquipmentStockLot.objects.select_for_update()
        .filter(item=item, remaining_quantity__gt=0)
        .order_by("received_on", "id")
    )
    available = sum(lot.remaining_quantity for lot in lots)
    if available < quantity:
        raise LogisticsWorkflowError(
            _("Only %(available)s units are available in stock.") % {"available": available}
        )
    remaining = quantity
    allocations = []
    total_value = Decimal("0")
    for lot in lots:
        if not remaining:
            break
        take = min(remaining, lot.remaining_quantity)
        if take == lot.remaining_quantity:
            value = lot.remaining_value
        else:
            value = (lot.remaining_value * Decimal(take) / Decimal(lot.remaining_quantity)).quantize(Decimal("0.01"))
        lot.remaining_quantity -= take
        lot.remaining_value -= value
        lot.save(update_fields=("remaining_quantity", "remaining_value"))
        allocations.append((lot, take, value))
        total_value += value
        remaining -= take
    movement = EquipmentStockMovement.objects.create(
        item=item, movement_type=movement_type, occurred_on=occurred_on,
        quantity_delta=-quantity, value_delta=-total_value, actor=_actor(actor),
        reason=reason, issue=issue,
    )
    EquipmentStockAllocation.objects.bulk_create([
        EquipmentStockAllocation(outbound_movement=movement, lot=lot, quantity=take, value=value)
        for lot, take, value in allocations
    ])
    return movement, total_value


@transaction.atomic
def receive_stock(*, received_on, lines, operation_key, supplier="", reference="",
                  note="", actor=None):
    existing = EquipmentStockReceipt.objects.filter(operation_key=operation_key).first()
    if existing:
        return existing
    prepared = []
    for line in lines:
        quantity = int(line["quantity"])
        value = _non_negative(line["total_value"])
        if quantity < 1:
            raise LogisticsWorkflowError(_("Receipt quantities must be at least one."))
        prepared.append((line["item"], quantity, value))
    if not prepared:
        raise LogisticsWorkflowError(_("Add at least one receipt line."))
    receipt = EquipmentStockReceipt.objects.create(
        operation_key=operation_key, received_on=received_on, supplier=supplier,
        reference=reference, note=note, recorded_by=_actor(actor),
    )
    for item, quantity, value in prepared:
        line = EquipmentStockReceiptLine.objects.create(
            receipt=receipt, item=item, quantity=quantity, total_value=value,
        )
        _create_inbound_lot(
            item=item, movement_type=EquipmentStockMovementType.RECEIPT,
            occurred_on=received_on, quantity=quantity, value=value,
            actor=actor, receipt_line=line,
        )
    record_event(actor, "equipment.stock_received", target=receipt, lines=len(prepared))
    return receipt


@transaction.atomic
def adjust_stock(item, quantity_delta, *, occurred_on, value=None, reason, actor=None):
    quantity_delta = int(quantity_delta)
    if not reason.strip() or quantity_delta == 0:
        raise LogisticsWorkflowError(_("A non-zero adjustment and reason are required."))
    if quantity_delta > 0:
        amount = _non_negative(value)
        movement = _create_inbound_lot(
            item=item, movement_type=EquipmentStockMovementType.ADJUSTMENT,
            occurred_on=occurred_on, quantity=quantity_delta, value=amount,
            actor=actor, reason=reason,
        )
    else:
        movement, _value = _consume_fifo(
            item=item, quantity=-quantity_delta,
            movement_type=EquipmentStockMovementType.ADJUSTMENT,
            occurred_on=occurred_on, actor=actor, reason=reason,
        )
    record_event(actor, "equipment.stock_adjusted", target=movement, reason=reason)
    return movement


def equipment_stock_balance(*, as_of=None):
    qs = EquipmentStockMovement.objects.select_related("item")
    if as_of is not None:
        qs = qs.filter(occurred_on__lte=as_of)
    grouped = qs.values("item_id", "item__name", "item__size").annotate(
        quantity=Sum("quantity_delta"), value=Sum("value_delta")
    ).order_by("item__name", "item__size")
    rows = list(grouped)
    return {
        "rows": rows,
        "quantity": sum((row["quantity"] or 0 for row in rows), 0),
        "value": sum((row["value"] or Decimal("0") for row in rows), Decimal("0")),
    }


def equipment_month_report(year, month):
    start = date(year, month, 1)
    end = date(year, month, calendar.monthrange(year, month)[1])
    opening = equipment_stock_balance(as_of=start - timedelta(days=1))
    closing = equipment_stock_balance(as_of=end)
    movements = EquipmentStockMovement.objects.filter(
        occurred_on__range=(start, end)
    ).values("movement_type").annotate(
        quantity=Sum("quantity_delta"), value=Sum("value_delta")
    )
    by_type = {row["movement_type"]: row for row in movements}
    return {"year": year, "month": month, "opening": opening, "closing": closing, "by_type": by_type}


@transaction.atomic
def issue_equipment(person, item, quantity=1, *, actor=None, operation_key=None):
    if not item.is_active:
        raise LogisticsWorkflowError(_("This equipment item is inactive and cannot be issued."))
    if stock_ledger_enabled() and operation_key is None:
        raise LogisticsWorkflowError(_("An operation key is required for stock-tracked issuance."))
    if operation_key:
        existing = EquipmentIssue.objects.filter(operation_key=operation_key).first()
        if existing:
            return existing
    quantity = max(1, int(quantity or 1))
    issue = EquipmentIssue.objects.create(
        person=person,
        item=item,
        quantity=quantity,
        status=EquipmentIssueStatus.ISSUED,
        issued_by=_actor(actor),
        operation_key=operation_key,
    )
    if stock_ledger_enabled():
        _movement, value = _consume_fifo(
            item=item, quantity=quantity, movement_type=EquipmentStockMovementType.ISSUE,
            occurred_on=timezone.localdate(), actor=actor, issue=issue,
        )
        issue.issued_stock_value = value
        issue.save(update_fields=("issued_stock_value",))
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
def create_transport_week(*, project, week_start, headcount, note: str = "", actor=None):
    if TransportWeek.objects.filter(project=project, week_start=week_start).exists():
        raise LogisticsWorkflowError(_("A transport record already exists for this project and week."))
    week = TransportWeek.objects.create(
        project=project, week_start=week_start, headcount=headcount, note=note,
        recorded_by=actor if getattr(actor, "is_authenticated", False) else None,
    )
    record_event(
        actor, "transport.week_created", target=week,
        new={"project": project.code, "week_start": str(week_start), "headcount": headcount, "note": note},
    )
    return week


@transaction.atomic
def update_transport_week(week, *, project, week_start, headcount, note: str = "", actor=None):
    duplicate = TransportWeek.objects.filter(project=project, week_start=week_start).exclude(pk=week.pk)
    if duplicate.exists():
        raise LogisticsWorkflowError(_("A transport record already exists for this project and week."))
    old = {
        "project": week.project.code, "week_start": str(week.week_start),
        "headcount": week.headcount, "note": week.note,
    }
    week.project = project
    week.week_start = week_start
    week.headcount = headcount
    week.note = note
    week.recorded_by = actor if getattr(actor, "is_authenticated", False) else None
    week.save()
    record_event(
        actor, "transport.week_updated", target=week, old=old,
        new={"project": project.code, "week_start": str(week_start), "headcount": headcount, "note": note},
    )
    return week


@transaction.atomic
def save_accommodation(accommodation, *, actor=None, old=None):
    accommodation.save()
    record_event(
        actor, "accommodation.updated" if old else "accommodation.created",
        target=accommodation, old=old or {},
        new={
            "name": accommodation.name, "address": accommodation.address,
            "notes": accommodation.notes, "is_active": accommodation.is_active,
        },
    )
    return accommodation


@transaction.atomic
def save_room(room, *, actor=None, old=None):
    room.save()
    record_event(
        actor, "room.updated" if old else "room.created", target=room, old=old or {},
        new={
            "accommodation": room.accommodation_id, "label": room.label,
            "capacity": room.capacity, "monthly_rate": str(room.monthly_rate),
            "is_active": room.is_active,
        },
    )
    return room


@transaction.atomic
def return_equipment(issue, *, actor=None, disposition=None):
    if issue.status == EquipmentIssueStatus.RETURNED:
        return issue
    if stock_ledger_enabled() and disposition not in {"restock", "retire"}:
        raise LogisticsWorkflowError(_("Choose whether the returned equipment is reusable or retired."))
    issue.status = EquipmentIssueStatus.RETURNED
    issue.returned_at = timezone.now()
    issue.return_disposition = disposition or "legacy"
    issue.save(update_fields=["status", "returned_at", "return_disposition"])
    if stock_ledger_enabled() and disposition == "restock":
        value = issue.issued_stock_value or Decimal(issue.item.unit_price) * issue.quantity
        _create_inbound_lot(
            item=issue.item, movement_type=EquipmentStockMovementType.RETURN,
            occurred_on=timezone.localdate(), quantity=issue.quantity, value=value,
            actor=actor, issue=issue,
        )
    record_event(actor, "equipment.returned", target=issue, disposition=issue.return_disposition)
    return issue
