from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.audit.services import record_event
from apps.people.models import LifecycleStatus
from apps.projects.models import (
    AssignmentStatus,
    PillarState,
    ProjectAssignment,
    ReadinessRecord,
    TrialAssignment,
    TrialOutcome,
    TrialState,
)


class WorkflowError(Exception):
    """Raised when a workflow step is attempted from an invalid state."""


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
def schedule_trial(person, project, *, actor=None, scheduled_date=None, note: str = ""):
    """Recruiter sends an Available person to a project trial (handoff §12.2)."""
    if person.lifecycle_status != LifecycleStatus.AVAILABLE:
        raise WorkflowError("Only an Available person can be sent to a trial.")
    trial = TrialAssignment.objects.create(
        person=person,
        project=project,
        scheduled_date=scheduled_date or timezone.localdate(),
        note=note,
        assigned_by=actor if getattr(actor, "is_authenticated", False) else None,
    )
    person.set_status(LifecycleStatus.TRIAL_DAY, actor=actor, reason="trial scheduled")
    record_event(actor, "trial.scheduled", target=trial, project=project.code)
    return trial


@transaction.atomic
def record_trial_outcome(trial, outcome, *, actor=None, note: str = ""):
    """Coordinator marks pass / fail / no-show (§12.3). Fail/no-show recycles."""
    if trial.outcome != TrialOutcome.PENDING:
        raise WorkflowError("This trial already has an outcome.")
    if outcome not in {TrialOutcome.PASS, TrialOutcome.FAIL, TrialOutcome.NO_SHOW}:
        raise WorkflowError(f"Invalid trial outcome: {outcome}")

    trial.outcome = outcome
    trial.state = TrialState.COMPLETED
    trial.outcome_recorded_by = actor if getattr(actor, "is_authenticated", False) else None
    trial.outcome_recorded_at = timezone.now()
    if note:
        trial.note = note
    trial.save()
    record_event(actor, "trial.outcome_recorded", target=trial, outcome=outcome)

    person = trial.person
    if outcome in {TrialOutcome.FAIL, TrialOutcome.NO_SHOW}:
        # Recycling: back to the recruiter pool.
        if person.lifecycle_status == LifecycleStatus.TRIAL_DAY:
            person.set_status(LifecycleStatus.AVAILABLE, actor=actor, reason=f"trial {outcome}")
    # On pass the person stays TRIAL_DAY and enters the readiness workflow.
    return trial


def get_or_create_readiness(person, project) -> ReadinessRecord:
    readiness, _created = ReadinessRecord.objects.get_or_create(person=person, project=project)
    return readiness


@transaction.atomic
def update_readiness(readiness, *, actor=None, states: dict, na_reasons: dict | None = None, entry_medical_date=None):
    """Set the four pillar states (§11.6). Medical and gear cannot be N/A;
    accommodation/transport require an explicit reason when marked N/A."""
    from django.utils.dateparse import parse_date

    na_reasons = na_reasons or {}
    valid = set(PillarState.values)
    for pillar in ("medical", "gear", "accommodation", "transport"):
        value = states.get(pillar)
        if value is None:
            continue
        if value not in valid:
            raise WorkflowError(f"Invalid pillar state: {value}")
        if pillar in {"medical", "gear"} and value == PillarState.NOT_APPLICABLE:
            raise WorkflowError("Medical and gear cannot be marked not-applicable.")
        setattr(readiness, f"{pillar}_state", value)
        if pillar in {"accommodation", "transport"}:
            if value == PillarState.NOT_APPLICABLE:
                reason = (na_reasons.get(pillar) or "").strip()
                if not reason:
                    raise WorkflowError(f"A reason is required to mark {pillar} not-applicable.")
                setattr(readiness, f"{pillar}_na_reason", reason)
            else:
                setattr(readiness, f"{pillar}_na_reason", "")

    if entry_medical_date is not None:
        readiness.entry_medical_date = (
            parse_date(entry_medical_date) if isinstance(entry_medical_date, str) else entry_medical_date
        )
    readiness.submitted_by = actor if getattr(actor, "is_authenticated", False) else None
    readiness.submitted_at = timezone.now()
    readiness.save()
    record_event(actor, "readiness.updated", target=readiness, ready=readiness.is_ready())
    return readiness


@transaction.atomic
def activate_from_readiness(person, project, *, actor=None):
    """Coordinator activation with the system-enforced four-pillar gate (ADR 0018)."""
    readiness = ReadinessRecord.objects.filter(person=person, project=project).first()
    if readiness is None or not readiness.is_ready():
        raise WorkflowError("Readiness is not complete; cannot activate.")
    return activate_on_project(person, project, actor=actor, reason="readiness met")


@transaction.atomic
def exit_person(person, *, actor=None, reason: str = "", outcome: str = "available",
                inactive_reason=None):
    """Exit reconciliation (plan §11.13): end the active project assignment,
    release the room, return all issued equipment, and recycle the person to
    Available (default) or mark them Inactive.

    Items already flagged as unreturned (review_status != NONE) are left for the
    manager deduction-review queue (Q2 safe default) rather than auto-returned.

    When exiting to Inactive, a structured ``inactive_reason`` (InactiveReason,
    Q5 catalog) and the since-date are recorded on the person.
    """
    from django.utils import timezone

    from apps.logistics.models import DeductionReviewStatus, EquipmentIssueStatus
    from apps.logistics.services import release_room, return_equipment

    end_assignment(person, actor=actor, reason=reason or "exit")
    release_room(person, actor=actor)
    for issue in person.equipment_issues.filter(
        status=EquipmentIssueStatus.ISSUED, review_status=DeductionReviewStatus.NONE
    ):
        return_equipment(issue, actor=actor)

    if outcome == "inactive" and person.lifecycle_status == LifecycleStatus.AVAILABLE:
        person.set_status(LifecycleStatus.INACTIVE, actor=actor, reason=reason or "exit")
        person.inactive_reason = inactive_reason
        person.inactive_since = timezone.localdate()
        person.save(update_fields=["inactive_reason", "inactive_since", "updated_at"])

    record_event(
        actor, "person.exited", target=person, reason=reason, outcome=outcome,
        inactive_reason=(inactive_reason.label if inactive_reason else ""),
    )
    return person


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
