from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

# Positive sign convention (confirmed with Jober 2026-06-29): rates, prices, and
# equipment charges are never negative.
NON_NEGATIVE = [MinValueValidator(Decimal("0"))]


class Accommodation(models.Model):
    """A place where workers are housed (plan §11.7).

    Cost is tracked as a per-room ``monthly_rate`` with an optional
    per-assignment override (``RoomAssignment.rate_override``). This is the Q1
    safe default (docs/product/jober-phase3-4-open-questions.md): a monthly rate per
    room, **recorded for reporting only — no automatic payroll deduction** —
    pending Jober's confirmation. The room-rate-plus-override shape stays robust
    whether the eventual answer is per-room, per-bed, or per-person, so this is
    not blocked on the answer.
    """

    name = models.CharField(_("name"), max_length=200)
    address = models.CharField(_("address"), max_length=300, blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    notes = models.TextField(_("notes"), blank=True)
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("accommodation")
        verbose_name_plural = _("accommodations")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class AccommodationCostPeriod(models.Model):
    accommodation = models.ForeignKey(
        Accommodation, on_delete=models.PROTECT, related_name="cost_periods",
        verbose_name=_("accommodation"),
    )
    effective_month = models.DateField(_("effective month"))
    capacity = models.PositiveIntegerField(_("capacity"), validators=[MinValueValidator(1)])
    per_head_cost = models.DecimalField(
        _("per-head monthly cost"), max_digits=10, decimal_places=2, validators=NON_NEGATIVE,
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="accommodation_cost_periods", verbose_name=_("recorded by"),
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        ordering = ("-effective_month", "-id")
        constraints = [
            models.UniqueConstraint(
                fields=("accommodation", "effective_month"),
                name="unique_accommodation_cost_effective_month",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.accommodation} {self.effective_month:%Y-%m}"


class Room(models.Model):
    accommodation = models.ForeignKey(
        Accommodation, on_delete=models.CASCADE, related_name="rooms", verbose_name=_("accommodation")
    )
    label = models.CharField(_("label"), max_length=100)
    capacity = models.PositiveIntegerField(_("capacity"), default=1)
    is_active = models.BooleanField(_("active"), default=True)
    # Per-room monthly cost (EUR). Q1 safe default; recorded for reporting only.
    monthly_rate = models.DecimalField(
        _("monthly rate"), max_digits=10, decimal_places=2, default=Decimal("0"), validators=NON_NEGATIVE
    )

    class Meta:
        verbose_name = _("room")
        verbose_name_plural = _("rooms")
        ordering = ("accommodation__name", "label")
        constraints = [
            models.UniqueConstraint(
                fields=["accommodation", "label"], name="unique_room_label_per_accommodation"
            )
        ]

    def __str__(self) -> str:
        return f"{self.accommodation.name} · {self.label}"

    def occupancy(self) -> int:
        return self.assignments.filter(status=RoomAssignmentStatus.ACTIVE).count()

    def is_full(self) -> bool:
        return self.occupancy() >= self.capacity


class RoomAssignmentStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    ENDED = "ended", _("Ended")


class RoomAssignment(models.Model):
    person = models.ForeignKey(
        "people.Person", on_delete=models.PROTECT, related_name="room_assignments", verbose_name=_("person")
    )
    room = models.ForeignKey(
        Room, on_delete=models.PROTECT, related_name="assignments", verbose_name=_("room")
    )
    status = models.CharField(_("status"), max_length=20, choices=RoomAssignmentStatus.choices, default=RoomAssignmentStatus.ACTIVE)
    start_date = models.DateField(_("start date"), null=True, blank=True)
    end_date = models.DateField(_("end date"), null=True, blank=True)
    # Optional per-assignment override of the room's monthly rate (Q1).
    rate_override = models.DecimalField(
        _("rate override"), max_digits=10, decimal_places=2, null=True, blank=True, validators=NON_NEGATIVE
    )
    worker_payment_monthly = models.DecimalField(
        _("worker monthly payment"), max_digits=10, decimal_places=2,
        default=Decimal("0"), validators=NON_NEGATIVE,
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="created_room_assignments", verbose_name=_("assigned by"),
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("room assignment")
        verbose_name_plural = _("room assignments")
        ordering = ("-created_at",)
        constraints = [
            # A person holds at most one active room at a time.
            models.UniqueConstraint(
                fields=["person"], condition=Q(status="active"), name="unique_active_room_per_person"
            )
        ]

    def __str__(self) -> str:
        return f"{self.person} -> {self.room} ({self.status})"

    @property
    def effective_rate(self) -> Decimal:
        """The monthly amount attributed to this assignment: the per-assignment
        override if set, otherwise the room's rate."""
        return self.rate_override if self.rate_override is not None else self.room.monthly_rate


class EquipmentItem(models.Model):
    """Catalog item (plan §11.8, minimal Phase 1: no valuation/pricing)."""

    name = models.CharField(_("name"), max_length=200)
    size = models.CharField(_("size"), max_length=50, blank=True)
    # Valuation: latest price at order date, entered manually (round-4 confirmed:
    # no weighted-average). The price *value* is operator data; the method is fixed.
    unit_price = models.DecimalField(_("unit price"), max_digits=10, decimal_places=2, default=0, validators=NON_NEGATIVE)
    is_active = models.BooleanField(_("active"), default=True)
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("equipment item")
        verbose_name_plural = _("equipment items")
        ordering = ("name", "size")

    def __str__(self) -> str:
        return f"{self.name} {self.size}".strip()


class EquipmentIssueStatus(models.TextChoices):
    ISSUED = "issued", _("Issued")
    RETURNED = "returned", _("Returned")


class DeductionReviewStatus(models.TextChoices):
    """Charge-review lifecycle for an unreturned item (Q2 safe default).

    Separate from the physical ``status``: a flagged item is still ISSUED (not
    returned) but its *charge* is under manager review. No payroll deduction is
    ever executed — APPROVED only records the manager's decision to recover.
    """

    NONE = "none", _("None")
    PENDING = "pending", _("Pending review")
    APPROVED = "approved", _("Charge approved")
    WAIVED = "waived", _("Waived")


class EquipmentIssue(models.Model):
    person = models.ForeignKey(
        "people.Person", on_delete=models.PROTECT, related_name="equipment_issues", verbose_name=_("person")
    )
    item = models.ForeignKey(
        EquipmentItem, on_delete=models.PROTECT, related_name="issues", verbose_name=_("item")
    )
    quantity = models.PositiveIntegerField(_("quantity"), default=1)
    status = models.CharField(_("status"), max_length=20, choices=EquipmentIssueStatus.choices, default=EquipmentIssueStatus.ISSUED)
    # Unreturned-item deduction review (Q2). Flagging snapshots the value; the
    # manager approves or waives. No automatic payroll deduction is performed.
    review_status = models.CharField(
        _("review status"), max_length=20,
        choices=DeductionReviewStatus.choices, default=DeductionReviewStatus.NONE,
    )
    charge_amount = models.DecimalField(
        _("charge amount"), max_digits=12, decimal_places=2, null=True, blank=True, validators=NON_NEGATIVE
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="reviewed_equipment_deductions", verbose_name=_("reviewed by"),
    )
    reviewed_at = models.DateTimeField(_("reviewed at"), null=True, blank=True)
    review_note = models.CharField(_("review note"), max_length=300, blank=True)
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="issued_equipment", verbose_name=_("issued by"),
    )
    issued_at = models.DateTimeField(_("issued at"), auto_now_add=True)
    returned_at = models.DateTimeField(_("returned at"), null=True, blank=True)
    operation_key = models.UUIDField(_("operation key"), null=True, blank=True, unique=True)
    issued_stock_value = models.DecimalField(
        _("issued stock value"), max_digits=12, decimal_places=2, null=True, blank=True,
        validators=NON_NEGATIVE,
    )
    return_disposition = models.CharField(_("return disposition"), max_length=20, blank=True)

    class Meta:
        verbose_name = _("equipment issue")
        verbose_name_plural = _("equipment issues")
        ordering = ("-issued_at",)

    def __str__(self) -> str:
        return f"{self.item} -> {self.person} ({self.status})"


class EquipmentStockReceipt(models.Model):
    operation_key = models.UUIDField(_("operation key"), default=uuid4, unique=True, editable=False)
    received_on = models.DateField(_("received on"))
    reference = models.CharField(_("reference"), max_length=120, blank=True)
    supplier = models.CharField(_("supplier"), max_length=200, blank=True)
    note = models.CharField(_("note"), max_length=300, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="equipment_stock_receipts", verbose_name=_("recorded by"),
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        ordering = ("-received_on", "-id")

    def __str__(self) -> str:
        return self.reference or f"Receipt {self.pk}"


class EquipmentStockReceiptLine(models.Model):
    receipt = models.ForeignKey(
        EquipmentStockReceipt, on_delete=models.PROTECT, related_name="lines",
        verbose_name=_("receipt"),
    )
    item = models.ForeignKey(
        EquipmentItem, on_delete=models.PROTECT, related_name="stock_receipt_lines",
        verbose_name=_("item"),
    )
    quantity = models.PositiveIntegerField(_("quantity"), validators=[MinValueValidator(1)])
    total_value = models.DecimalField(
        _("total value"), max_digits=12, decimal_places=2, validators=NON_NEGATIVE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("receipt", "item"), name="unique_item_per_stock_receipt"),
        ]


class EquipmentStockMovementType(models.TextChoices):
    RECEIPT = "receipt", _("Receipt")
    ISSUE = "issue", _("Issue")
    RETURN = "return", _("Return")
    ADJUSTMENT = "adjustment", _("Adjustment")


class EquipmentStockMovement(models.Model):
    item = models.ForeignKey(
        EquipmentItem, on_delete=models.PROTECT, related_name="stock_movements",
        verbose_name=_("item"),
    )
    movement_type = models.CharField(
        _("movement type"), max_length=20, choices=EquipmentStockMovementType.choices,
    )
    occurred_on = models.DateField(_("occurred on"))
    quantity_delta = models.IntegerField(_("quantity delta"))
    value_delta = models.DecimalField(_("value delta"), max_digits=12, decimal_places=2)
    receipt_line = models.ForeignKey(
        EquipmentStockReceiptLine, on_delete=models.PROTECT, null=True, blank=True,
        related_name="movements", verbose_name=_("receipt line"),
    )
    issue = models.ForeignKey(
        EquipmentIssue, on_delete=models.PROTECT, null=True, blank=True,
        related_name="stock_movements", verbose_name=_("issue"),
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="equipment_stock_movements", verbose_name=_("actor"),
    )
    reason = models.CharField(_("reason"), max_length=300, blank=True)
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        ordering = ("occurred_on", "id")
        constraints = [
            models.CheckConstraint(
                condition=~Q(quantity_delta=0), name="stock_movement_quantity_nonzero"
            ),
            models.UniqueConstraint(
                fields=("movement_type", "receipt_line"),
                condition=Q(receipt_line__isnull=False),
                name="unique_stock_movement_per_receipt_line_type",
            ),
            models.UniqueConstraint(
                fields=("movement_type", "issue"),
                condition=Q(issue__isnull=False),
                name="unique_stock_movement_per_issue_type",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise ValueError("Stock movements are immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Stock movements are immutable.")


class EquipmentStockLot(models.Model):
    inbound_movement = models.OneToOneField(
        EquipmentStockMovement, on_delete=models.PROTECT, related_name="stock_lot",
        verbose_name=_("inbound movement"),
    )
    item = models.ForeignKey(
        EquipmentItem, on_delete=models.PROTECT, related_name="stock_lots",
        verbose_name=_("item"),
    )
    received_on = models.DateField(_("received on"))
    initial_quantity = models.PositiveIntegerField(_("initial quantity"))
    initial_value = models.DecimalField(_("initial value"), max_digits=12, decimal_places=2)
    remaining_quantity = models.PositiveIntegerField(_("remaining quantity"))
    remaining_value = models.DecimalField(_("remaining value"), max_digits=12, decimal_places=2)

    class Meta:
        ordering = ("received_on", "id")


class EquipmentStockAllocation(models.Model):
    outbound_movement = models.ForeignKey(
        EquipmentStockMovement, on_delete=models.PROTECT, related_name="allocations",
        verbose_name=_("outbound movement"),
    )
    lot = models.ForeignKey(
        EquipmentStockLot, on_delete=models.PROTECT, related_name="allocations",
        verbose_name=_("lot"),
    )
    quantity = models.PositiveIntegerField(_("quantity"), validators=[MinValueValidator(1)])
    value = models.DecimalField(_("value"), max_digits=12, decimal_places=2, validators=NON_NEGATIVE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("outbound_movement", "lot"), name="unique_stock_allocation_lot"),
        ]


class TransportWeek(models.Model):
    """Weekly transport headcount per project (plan §11.10, minimal)."""

    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="transport_weeks", verbose_name=_("project")
    )
    week_start = models.DateField(_("week start"))
    headcount = models.PositiveIntegerField(_("headcount"), default=0)
    note = models.CharField(_("note"), max_length=300, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="recorded_transport_weeks", verbose_name=_("recorded by"),
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("transport week")
        verbose_name_plural = _("transport weeks")
        ordering = ("-week_start",)
        constraints = [
            models.UniqueConstraint(fields=["project", "week_start"], name="unique_transport_week_per_project")
        ]

    def __str__(self) -> str:
        return f"{self.project} {self.week_start}: {self.headcount}"
