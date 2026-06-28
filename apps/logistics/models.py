from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class Accommodation(models.Model):
    """A place where workers are housed (plan §11.7, minimal Phase 1: no rates)."""

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

    class Meta:
        verbose_name = _("room")
        verbose_name_plural = _("rooms")
        ordering = ("accommodation__name", "label")

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


class EquipmentItem(models.Model):
    """Catalog item (plan §11.8, minimal Phase 1: no valuation/pricing)."""

    name = models.CharField(_("name"), max_length=200)
    size = models.CharField(_("size"), max_length=50, blank=True)
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


class EquipmentIssue(models.Model):
    person = models.ForeignKey(
        "people.Person", on_delete=models.PROTECT, related_name="equipment_issues", verbose_name=_("person")
    )
    item = models.ForeignKey(
        EquipmentItem, on_delete=models.PROTECT, related_name="issues", verbose_name=_("item")
    )
    quantity = models.PositiveIntegerField(_("quantity"), default=1)
    status = models.CharField(_("status"), max_length=20, choices=EquipmentIssueStatus.choices, default=EquipmentIssueStatus.ISSUED)
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
