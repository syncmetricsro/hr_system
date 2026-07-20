from __future__ import annotations

from decimal import Decimal

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

    class Meta:
        verbose_name = _("equipment issue")
        verbose_name_plural = _("equipment issues")
        ordering = ("-issued_at",)

    def __str__(self) -> str:
        return f"{self.item} -> {self.person} ({self.status})"


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
