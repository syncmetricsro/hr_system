from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class LifecycleStatus(models.TextChoices):
    """The one canonical person lifecycle status (plan §9.1)."""

    AVAILABLE = "available", _("Available")
    TRIAL_DAY = "trial_day", _("Trial day")
    WORKING = "working", _("Working")
    INACTIVE = "inactive", _("Inactive")
    BLACKLISTED = "blacklisted", _("Blacklisted")


# Allowed lifecycle transitions (plan §9.3, §12). Enforced in Person.set_status.
# BLACKLISTED is reachable from any state (manager action, Phase 3); removal from
# the blacklist is manager-only and also lands in Phase 3.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    LifecycleStatus.AVAILABLE: {
        LifecycleStatus.TRIAL_DAY,
        LifecycleStatus.WORKING,      # CARGO manager override / direct activation
        LifecycleStatus.INACTIVE,
        LifecycleStatus.BLACKLISTED,
    },
    LifecycleStatus.TRIAL_DAY: {
        LifecycleStatus.AVAILABLE,    # fail / no-show recycling
        LifecycleStatus.WORKING,      # pass -> readiness -> activation
        LifecycleStatus.INACTIVE,
        LifecycleStatus.BLACKLISTED,
    },
    LifecycleStatus.WORKING: {
        LifecycleStatus.AVAILABLE,    # exit / reassignment
        LifecycleStatus.INACTIVE,
        LifecycleStatus.BLACKLISTED,
    },
    LifecycleStatus.INACTIVE: {
        LifecycleStatus.AVAILABLE,
        LifecycleStatus.BLACKLISTED,
    },
    LifecycleStatus.BLACKLISTED: {
        LifecycleStatus.AVAILABLE,    # manager removal (Phase 3)
    },
}

# Fields restricted to: owning recruiter, responsible coordinator, managers,
# observers (plan §8.1 + phase1-open-questions Q4). See apps.people.permissions.
SENSITIVE_FIELDS = ("date_of_birth", "place_of_birth", "has_disability", "disability_type")


class LifecycleError(Exception):
    """Raised on a disallowed lifecycle transition."""


class InactiveReason(models.Model):
    """Configurable catalog of reasons a person is marked Inactive (Q5 safe
    default: a configurable list, seeded with a few placeholders). Editable in
    admin; seeded by migration."""

    label = models.CharField(_("label"), max_length=120, unique=True)
    is_active = models.BooleanField(_("active"), default=True)
    order = models.PositiveIntegerField(_("order"), default=0)

    class Meta:
        verbose_name = _("inactive reason")
        verbose_name_plural = _("inactive reasons")
        ordering = ("order", "label")

    def __str__(self) -> str:
        return self.label


class Person(models.Model):
    """A worker/candidate. Fictional data only until the real-data legal gate."""

    # Identity
    first_name = models.CharField(_("first name"), max_length=120)
    last_name = models.CharField(_("last name"), max_length=120)
    date_of_birth = models.DateField(_("date of birth"), null=True, blank=True)
    place_of_birth = models.CharField(_("place of birth"), max_length=200, blank=True)
    phone = models.CharField(_("phone"), max_length=40, blank=True)
    address = models.CharField(_("address"), max_length=300, blank=True)
    nationality = models.CharField(_("nationality"), max_length=100, blank=True)
    preferred_language = models.CharField(
        _("preferred language"), max_length=10, blank=True
    )

    # Disability: flag only, no documents (phase1-open-questions Q1).
    has_disability = models.BooleanField(_("has disability"), default=False)
    disability_type = models.CharField(_("disability type"), max_length=200, blank=True)

    # Lifecycle
    lifecycle_status = models.CharField(
        _("lifecycle status"),
        max_length=20,
        choices=LifecycleStatus.choices,
        default=LifecycleStatus.AVAILABLE,
    )

    # Inactive metadata (Q5): structured reason + since-date, set when marked
    # Inactive and cleared on recycle back to Available.
    inactive_reason = models.ForeignKey(
        InactiveReason, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="people", verbose_name=_("inactive reason"),
    )
    inactive_since = models.DateField(_("inactive since"), null=True, blank=True)

    # Ownership / eligibility
    owning_recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_people",
        verbose_name=_("owning recruiter"),
        help_text=_("The recruiter who entered this person."),
    )
    rehire_eligible = models.BooleanField(_("rehire eligible"), default=True)

    # Archive metadata
    is_archived = models.BooleanField(_("archived"), default=False)
    archived_at = models.DateTimeField(_("archived at"), null=True, blank=True)

    # Search
    search_name = models.CharField(_("search name"), max_length=255, db_index=True, blank=True)

    created_at = models.DateTimeField(_("created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated"), auto_now=True)

    class Meta:
        verbose_name = _("person")
        verbose_name_plural = _("people")
        ordering = ("last_name", "first_name")
        indexes = [models.Index(fields=["lifecycle_status"])]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def save(self, *args, **kwargs):
        self.search_name = f"{self.first_name} {self.last_name}".strip().lower()
        super().save(*args, **kwargs)

    # --- lifecycle ---------------------------------------------------------

    def can_transition_to(self, new_status: str) -> bool:
        if new_status == self.lifecycle_status:
            return True
        return new_status in ALLOWED_TRANSITIONS.get(self.lifecycle_status, set())

    def set_status(self, new_status: str, *, actor=None, reason: str = "") -> None:
        """Validate, apply, and audit a lifecycle transition."""
        from apps.audit.services import record_event

        if new_status not in LifecycleStatus.values:
            raise LifecycleError(f"Unknown lifecycle status: {new_status}")
        if not self.can_transition_to(new_status):
            raise LifecycleError(
                f"Disallowed transition: {self.lifecycle_status} -> {new_status}"
            )
        previous = self.lifecycle_status
        if previous == new_status:
            return
        self.lifecycle_status = new_status
        self.save(update_fields=["lifecycle_status", "updated_at", "search_name"])
        record_event(
            actor,
            "person.lifecycle_changed",
            target=self,
            reason=reason,
            from_status=previous,
            to_status=new_status,
        )

    # --- current assignment / coordinators ---------------------------------

    def current_assignment(self):
        """The single active project assignment, if any (plan §11.4)."""
        return self.assignments.filter(status="active").select_related("project").first()

    def responsible_coordinator_ids(self) -> set[int]:
        """IDs of coordinators responsible via the current project assignment."""
        assignment = self.current_assignment()
        if assignment is None:
            return set()
        return set(
            assignment.project.responsible_coordinators.values_list("id", flat=True)
        )

    def archive(self, *, actor=None, reason: str = "") -> None:
        from apps.audit.services import record_event

        if self.is_archived:
            return
        self.is_archived = True
        self.archived_at = timezone.now()
        self.save(update_fields=["is_archived", "archived_at", "updated_at", "search_name"])
        record_event(actor, "person.archived", target=self, reason=reason)
