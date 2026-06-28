from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    """A client project workers are assigned to (plan §11.4)."""

    name = models.CharField(_("name"), max_length=200)
    partner = models.CharField(_("partner"), max_length=200, blank=True)
    code = models.CharField(_("code"), max_length=50, unique=True)
    office = models.CharField(_("office"), max_length=100, blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    # project <-> coordinator is many-to-many (e.g. DHL BA has three coordinators).
    responsible_coordinators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="coordinated_projects",
        blank=True,
        verbose_name=_("responsible coordinators"),
    )
    notes = models.TextField(_("notes"), blank=True)
    financial_reporting_eligible = models.BooleanField(
        _("financial reporting eligible"), default=True
    )

    created_at = models.DateTimeField(_("created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated"), auto_now=True)

    class Meta:
        verbose_name = _("project")
        verbose_name_plural = _("projects")
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class AssignmentStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    ENDED = "ended", _("Ended")
    CANCELLED = "cancelled", _("Cancelled")


class ProjectAssignment(models.Model):
    """A worker's assignment to a project. At most one ACTIVE per person.

    History is retained: ending an assignment keeps the row (plan §11.4).
    """

    person = models.ForeignKey(
        "people.Person",
        on_delete=models.PROTECT,
        related_name="assignments",
        verbose_name=_("person"),
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="assignments",
        verbose_name=_("project"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=AssignmentStatus.choices,
        default=AssignmentStatus.ACTIVE,
    )
    start_date = models.DateField(_("start date"), null=True, blank=True)
    end_date = models.DateField(_("end date"), null=True, blank=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_assignments",
        verbose_name=_("assigned by"),
    )
    assignment_reason = models.CharField(_("assignment reason"), max_length=300, blank=True)
    # Snapshot of responsible coordinators at assignment time (audit trail).
    coordinator_snapshot = models.CharField(_("coordinator snapshot"), max_length=300, blank=True)

    created_at = models.DateTimeField(_("created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated"), auto_now=True)

    class Meta:
        verbose_name = _("project assignment")
        verbose_name_plural = _("project assignments")
        ordering = ("-created_at",)
        constraints = [
            # Only one active assignment per person (plan §11.4, round-4 confirmed).
            models.UniqueConstraint(
                fields=["person"],
                condition=Q(status="active"),
                name="unique_active_assignment_per_person",
            )
        ]

    def __str__(self) -> str:
        return f"{self.person} -> {self.project} ({self.status})"


class TrialState(models.TextChoices):
    SCHEDULED = "scheduled", _("Scheduled")
    COMPLETED = "completed", _("Completed")
    CANCELLED = "cancelled", _("Cancelled")


class TrialOutcome(models.TextChoices):
    PENDING = "pending", _("Pending")
    PASS = "pass", _("Pass")
    FAIL = "fail", _("Fail")
    NO_SHOW = "no_show", _("No-show")


class TrialAssignment(models.Model):
    """A trial-day workflow record (plan §11.5). History is append-preserving:
    a new attempt creates a new record."""

    person = models.ForeignKey(
        "people.Person", on_delete=models.PROTECT, related_name="trials", verbose_name=_("person")
    )
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="trials", verbose_name=_("project")
    )
    scheduled_date = models.DateField(_("scheduled date"), null=True, blank=True)
    state = models.CharField(_("state"), max_length=20, choices=TrialState.choices, default=TrialState.SCHEDULED)
    outcome = models.CharField(_("outcome"), max_length=20, choices=TrialOutcome.choices, default=TrialOutcome.PENDING)
    note = models.CharField(_("note"), max_length=300, blank=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="scheduled_trials", verbose_name=_("assigned by"),
    )
    outcome_recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="recorded_trials", verbose_name=_("outcome recorded by"),
    )
    outcome_recorded_at = models.DateTimeField(_("outcome recorded at"), null=True, blank=True)
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("trial assignment")
        verbose_name_plural = _("trial assignments")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.person} @ {self.project} ({self.outcome})"


class PillarState(models.TextChoices):
    INCOMPLETE = "incomplete", _("Incomplete")
    COMPLETE = "complete", _("Complete")
    NOT_APPLICABLE = "not_applicable", _("Not applicable")


class ReadinessRecord(models.Model):
    """Four-pillar readiness for a person on a project (plan §11.6).

    Medical and gear are always required (cannot be N/A); accommodation and
    transport may be N/A. Activation is system-enforced via ``is_ready`` (ADR 0018).
    """

    person = models.ForeignKey(
        "people.Person", on_delete=models.PROTECT, related_name="readiness_records", verbose_name=_("person")
    )
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="readiness_records", verbose_name=_("project")
    )
    medical_state = models.CharField(_("medical"), max_length=20, choices=PillarState.choices, default=PillarState.INCOMPLETE)
    gear_state = models.CharField(_("gear"), max_length=20, choices=PillarState.choices, default=PillarState.INCOMPLETE)
    accommodation_state = models.CharField(_("accommodation"), max_length=20, choices=PillarState.choices, default=PillarState.INCOMPLETE)
    transport_state = models.CharField(_("transport"), max_length=20, choices=PillarState.choices, default=PillarState.INCOMPLETE)
    entry_medical_date = models.DateField(_("entry medical date"), null=True, blank=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="submitted_readiness", verbose_name=_("submitted by"),
    )
    submitted_at = models.DateTimeField(_("submitted at"), null=True, blank=True)
    created_at = models.DateTimeField(_("created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated"), auto_now=True)

    class Meta:
        verbose_name = _("readiness record")
        verbose_name_plural = _("readiness records")
        constraints = [
            models.UniqueConstraint(fields=["person", "project"], name="unique_readiness_per_person_project")
        ]

    def __str__(self) -> str:
        return f"Readiness {self.person} @ {self.project}"

    def is_ready(self) -> bool:
        """Required pillars complete; optional pillars complete or N/A (§11.6)."""
        required_ok = (
            self.medical_state == PillarState.COMPLETE
            and self.gear_state == PillarState.COMPLETE
        )
        optional_ok = (
            self.accommodation_state in {PillarState.COMPLETE, PillarState.NOT_APPLICABLE}
            and self.transport_state in {PillarState.COMPLETE, PillarState.NOT_APPLICABLE}
        )
        return required_ok and optional_ok
