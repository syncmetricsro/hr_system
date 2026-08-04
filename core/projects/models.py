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
    office = models.ForeignKey(
        "offices.Office",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="projects",
        verbose_name=_("office"),
    )
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
    assignment_reason = models.CharField(
        _("assignment reason"), max_length=300, blank=True
    )
    # Snapshot of responsible coordinators at assignment time (audit trail).
    coordinator_snapshot = models.CharField(
        _("coordinator snapshot"), max_length=300, blank=True
    )

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
        "people.Person",
        on_delete=models.PROTECT,
        related_name="trials",
        verbose_name=_("person"),
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="trials",
        verbose_name=_("project"),
    )
    scheduled_date = models.DateField(_("scheduled date"), null=True, blank=True)
    # The legacy date is retained for historic records. New trial scheduling
    # records the actual arrival appointment with timezone support.
    scheduled_for = models.DateTimeField(_("scheduled for"), null=True, blank=True)
    state = models.CharField(
        _("state"),
        max_length=20,
        choices=TrialState.choices,
        default=TrialState.SCHEDULED,
    )
    outcome = models.CharField(
        _("outcome"),
        max_length=20,
        choices=TrialOutcome.choices,
        default=TrialOutcome.PENDING,
    )
    note = models.CharField(_("note"), max_length=300, blank=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scheduled_trials",
        verbose_name=_("assigned by"),
    )
    outcome_recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_trials",
        verbose_name=_("outcome recorded by"),
    )
    outcome_recorded_at = models.DateTimeField(
        _("outcome recorded at"), null=True, blank=True
    )
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
        "people.Person",
        on_delete=models.PROTECT,
        related_name="readiness_records",
        verbose_name=_("person"),
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="readiness_records",
        verbose_name=_("project"),
    )
    medical_state = models.CharField(
        _("medical"),
        max_length=20,
        choices=PillarState.choices,
        default=PillarState.INCOMPLETE,
    )
    gear_state = models.CharField(
        _("gear"),
        max_length=20,
        choices=PillarState.choices,
        default=PillarState.INCOMPLETE,
    )
    accommodation_state = models.CharField(
        _("accommodation"),
        max_length=20,
        choices=PillarState.choices,
        default=PillarState.INCOMPLETE,
    )
    transport_state = models.CharField(
        _("transport"),
        max_length=20,
        choices=PillarState.choices,
        default=PillarState.INCOMPLETE,
    )
    accommodation_na_reason = models.CharField(
        _("accommodation N/A reason"), max_length=200, blank=True
    )
    transport_na_reason = models.CharField(
        _("transport N/A reason"), max_length=200, blank=True
    )
    entry_medical_date = models.DateField(
        _("entry medical date"), null=True, blank=True
    )
    #: A manager started readiness on an Available person, skipping the trial
    #: day (ADR 0031). Stored rather than derived: it is what keeps the readiness
    #: panel open for a person who is still Available, and it is the record's own
    #: answer to "did this worker ever do a trial?". The pillars still apply —
    #: only the trial is waived.
    trial_waived = models.BooleanField(_("trial waived"), default=False)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_readiness",
        verbose_name=_("submitted by"),
    )
    submitted_at = models.DateTimeField(_("submitted at"), null=True, blank=True)
    created_at = models.DateTimeField(_("created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated"), auto_now=True)

    class Meta:
        verbose_name = _("readiness record")
        verbose_name_plural = _("readiness records")
        constraints = [
            models.UniqueConstraint(
                fields=["person", "project"], name="unique_readiness_per_person_project"
            )
        ]

    def __str__(self) -> str:
        return f"Readiness {self.person} @ {self.project}"

    def is_ready(self) -> bool:
        """Required pillars complete; optional pillars complete or N/A (§11.6)."""
        required_ok = (
            self.medical_state == PillarState.COMPLETE
            and self.gear_state == PillarState.COMPLETE
        )
        accommodation_ok = self.accommodation_state == PillarState.COMPLETE or (
            self.accommodation_state == PillarState.NOT_APPLICABLE
            and bool(self.accommodation_na_reason.strip())
        )
        transport_enabled = getattr(settings, "FEATURE_FLAGS", {}).get(
            "transport", True
        )
        transport_ok = not transport_enabled or (
            self.transport_state == PillarState.COMPLETE
            or (
                self.transport_state == PillarState.NOT_APPLICABLE
                and bool(self.transport_na_reason.strip())
            )
        )
        return required_ok and accommodation_ok and transport_ok


class ActivationApprovalStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")


class ActivationApproval(models.Model):
    """A manager's decision on activating a worker to Working (plan §12.4).

    Separation of duties: the coordinator who completes readiness requests
    activation, and a *different* authority - a manager of that office -
    decides. Before this existed the same coordinator could tick the four
    pillars and activate in the next click, so nobody ever checked the
    checker (production-readiness item 14).

    ``pillar_snapshot`` records what the readiness record said at the moment
    the request was raised. Readiness stays editable afterwards, so without a
    snapshot a manager would be approving whatever the record happens to say
    when they open it - which is not what they were asked to approve.
    """

    person = models.ForeignKey(
        "people.Person",
        on_delete=models.PROTECT,
        related_name="activation_approvals",
        verbose_name=_("person"),
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="activation_approvals",
        verbose_name=_("project"),
    )
    readiness = models.ForeignKey(
        ReadinessRecord,
        on_delete=models.PROTECT,
        related_name="activation_approvals",
        verbose_name=_("readiness record"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=ActivationApprovalStatus.choices,
        default=ActivationApprovalStatus.PENDING,
    )
    pillar_snapshot = models.JSONField(_("pillar snapshot"), default=dict, blank=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_activations",
        verbose_name=_("requested by"),
    )
    requested_at = models.DateTimeField(_("requested at"), auto_now_add=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="decided_activations",
        verbose_name=_("decided by"),
    )
    decided_at = models.DateTimeField(_("decided at"), null=True, blank=True)
    decision_reason = models.CharField(_("decision reason"), max_length=300, blank=True)

    class Meta:
        verbose_name = _("activation approval")
        verbose_name_plural = _("activation approvals")
        ordering = ["-requested_at"]
        constraints = [
            # One open request per person/project. Re-requesting while one is
            # already pending would give a manager two rows for one decision.
            models.UniqueConstraint(
                fields=["person", "project"],
                condition=models.Q(status="pending"),
                name="unique_pending_activation_per_person_project",
            )
        ]

    def __str__(self) -> str:
        return f"{self.person} → {self.project} ({self.get_status_display()})"
