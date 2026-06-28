from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.audit.services import record_event
from apps.people.models import LifecycleStatus
from apps.projects.models import AssignmentStatus, ProjectAssignment


def _coordinator_snapshot(project) -> str:
    emails = project.responsible_coordinators.values_list("email", flat=True)
    return ", ".join(sorted(emails))


@transaction.atomic
def activate_on_project(person, project, *, actor=None, reason: str = "", start_date=None):
    """Place a person on a project as their active assignment and set them WORKING.

    Coordinator-driven (phase1-open-questions Q2). Closes any existing active
    assignment first, so the one-active-assignment rule holds. History is kept.

    NOTE: the system-enforced four-pillar readiness gate (medical + gear required;
    accommodation + transport may be N/A) attaches here once ReadinessRecord
    lands; the CARGO manager override bypasses it. Tracked for the readiness slice.
    """
    today = timezone.localdate()
    existing = person.assignments.filter(status=AssignmentStatus.ACTIVE)
    for assignment in existing:
        assignment.status = AssignmentStatus.ENDED
        assignment.end_date = today
        assignment.save(update_fields=["status", "end_date", "updated_at"])
        record_event(actor, "assignment.ended", target=assignment, reason="superseded")

    assignment = ProjectAssignment.objects.create(
        person=person,
        project=project,
        status=AssignmentStatus.ACTIVE,
        start_date=start_date or today,
        assigned_by=actor if getattr(actor, "is_authenticated", False) else None,
        assignment_reason=reason,
        coordinator_snapshot=_coordinator_snapshot(project),
    )
    record_event(actor, "assignment.created", target=assignment, project=project.code)

    if person.lifecycle_status != LifecycleStatus.WORKING:
        person.set_status(LifecycleStatus.WORKING, actor=actor, reason=reason or "activation")
    return assignment


@transaction.atomic
def end_assignment(person, *, actor=None, reason: str = ""):
    """End the active assignment and return the person to AVAILABLE."""
    today = timezone.localdate()
    assignment = person.assignments.filter(status=AssignmentStatus.ACTIVE).first()
    if assignment is not None:
        assignment.status = AssignmentStatus.ENDED
        assignment.end_date = today
        assignment.save(update_fields=["status", "end_date", "updated_at"])
        record_event(actor, "assignment.ended", target=assignment, reason=reason)

    if person.lifecycle_status == LifecycleStatus.WORKING:
        person.set_status(LifecycleStatus.AVAILABLE, actor=actor, reason=reason or "exit")
    return assignment
