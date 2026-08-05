from __future__ import annotations

import datetime as dt

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.translation import gettext as _

from core.audit.services import record_event
from core.dates import add_months
from core.people.models import LifecycleStatus
from core.projects.models import (
    ActivationApproval,
    ActivationApprovalStatus,
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


# --- platform hooks (Stage B, ADR 0021) -----------------------------------
# Core defines the extension points; feature apps register into them from
# AppConfig.ready(). Dependencies therefore point feature -> core only.

# Callables (person) -> None that raise WorkflowError to block activation.
activation_checks: list = []
# Callables (person, *, actor=None) run during exit reconciliation.
exit_hooks: list = []


def register_activation_check(fn) -> None:
    if fn not in activation_checks:
        activation_checks.append(fn)


def register_exit_hook(fn) -> None:
    if fn not in exit_hooks:
        exit_hooks.append(fn)


def _coordinator_snapshot(project) -> str:
    emails = project.responsible_coordinators.values_list("email", flat=True)
    return ", ".join(sorted(emails))


@transaction.atomic
def activate_on_project(
    person, project, *, actor=None, reason: str = "", start_date=None
):
    """Place a person on a project as their active assignment and set them WORKING.

    Coordinator-driven (phase1-open-questions Q2). Closes any existing active
    assignment first, so the one-active-assignment rule holds. History is kept.

    NOTE: the system-enforced four-pillar readiness gate (medical + gear required;
    accommodation + transport may be N/A) attaches here once ReadinessRecord
    lands; the CARGO manager override bypasses it. Tracked for the readiness slice.
    """
    # Hard-gates registered by feature apps (e.g. the blacklist's unresolved-case
    # check, plan §12.13; CorvinumEU's checklist hard-stops later).
    for check in activation_checks:
        check(person)

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
        person.set_status(
            LifecycleStatus.WORKING, actor=actor, reason=reason or "activation"
        )
    return assignment


@transaction.atomic
def schedule_trial(
    person,
    project,
    *,
    actor=None,
    scheduled_for=None,
    scheduled_date=None,
    note: str = "",
):
    """Send an Available person to a project trial at a recorded appointment."""
    if person.lifecycle_status != LifecycleStatus.AVAILABLE:
        raise WorkflowError("Only an Available person can be sent to a trial.")
    trial = TrialAssignment.objects.create(
        person=person,
        project=project,
        # Keep the date column populated for old reports/records while new UI
        # displays the precise, timezone-aware appointment.
        scheduled_date=scheduled_date
        or (
            timezone.localdate(scheduled_for) if scheduled_for else timezone.localdate()
        ),
        scheduled_for=scheduled_for or timezone.now(),
        note=note,
        assigned_by=actor if getattr(actor, "is_authenticated", False) else None,
    )
    person.set_status(LifecycleStatus.TRIAL_DAY, actor=actor, reason="trial scheduled")
    record_event(actor, "trial.scheduled", target=trial, project=project.code)
    return trial


@transaction.atomic
def update_pending_trial(trial, *, project, scheduled_for, note: str = "", actor=None):
    """Edit routing details while preserving the candidate and completed history."""
    if trial.outcome != TrialOutcome.PENDING or trial.state != TrialState.SCHEDULED:
        raise WorkflowError(_("Only pending trials can be edited."))
    if not project.is_active:
        raise WorkflowError(_("Trials can only be scheduled for active projects."))
    old = {
        "project": trial.project.code,
        "scheduled_for": trial.scheduled_for.isoformat() if trial.scheduled_for else "",
        "note": trial.note,
    }
    trial.project = project
    trial.scheduled_for = scheduled_for
    trial.scheduled_date = timezone.localdate(scheduled_for)
    trial.note = note or ""
    trial.save(update_fields=["project", "scheduled_for", "scheduled_date", "note"])
    record_event(
        actor,
        "trial.updated",
        target=trial,
        old=old,
        new={
            "project": project.code,
            "scheduled_for": scheduled_for.isoformat(),
            "note": trial.note,
        },
    )
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
    trial.outcome_recorded_by = (
        actor if getattr(actor, "is_authenticated", False) else None
    )
    trial.outcome_recorded_at = timezone.now()
    if note:
        trial.note = note
    trial.save()
    record_event(actor, "trial.outcome_recorded", target=trial, outcome=outcome)

    person = trial.person
    if outcome in {TrialOutcome.FAIL, TrialOutcome.NO_SHOW}:
        # Recycling: back to the recruiter pool.
        if person.lifecycle_status == LifecycleStatus.TRIAL_DAY:
            person.set_status(
                LifecycleStatus.AVAILABLE, actor=actor, reason=f"trial {outcome}"
            )
    # On pass the person stays TRIAL_DAY and enters the readiness workflow.
    return trial


def get_or_create_readiness(person, project) -> ReadinessRecord:
    readiness, _created = ReadinessRecord.objects.get_or_create(
        person=person, project=project
    )
    return readiness


@transaction.atomic
def waive_trial(person, project, *, actor=None) -> ReadinessRecord:
    """Open readiness for an Available person without a trial day (ADR 0031).

    For a known or returning worker the trial is a detour, and an office with a
    single administrator has nobody to hand the steps to. This skips **only**
    the trial: the four pillars still gate activation through ``_assert_ready``,
    so medical and gear must still be complete and the entry medical date is
    still recorded.

    The person deliberately stays Available. Moving them to Trial-day would make
    the lifecycle claim a trial that never happened, and ``AVAILABLE ->
    WORKING`` is already a permitted transition in both clients.
    """
    if person.lifecycle_status != LifecycleStatus.AVAILABLE:
        raise WorkflowError(
            _("Only an available person can be activated without a trial day.")
        )
    readiness = get_or_create_readiness(person, project)
    if not readiness.trial_waived:
        readiness.trial_waived = True
        readiness.save(update_fields=["trial_waived", "updated_at"])
    record_event(
        actor,
        "readiness.trial_waived",
        target=readiness,
        person=str(person),
        project=project.code,
    )
    return readiness


def _clean_entry_medical_date(value):
    """Parse and sanity-check an entry medical date. Shared, because it is now
    set from two places: the readiness form and a working person's profile."""
    parsed = parse_date(value) if isinstance(value, str) else value
    if parsed is None:
        raise WorkflowError(_("Entry medical date is invalid."))
    if parsed > timezone.localdate():
        raise WorkflowError(_("Entry medical date cannot be in the future."))
    return parsed


@transaction.atomic
def record_entry_medical(person, project, entry_medical_date, *, actor=None):
    """Record or renew a working person's entry medical date.

    Readiness is only editable on the way *in* — the form disappears once the
    person is Working. The medical expires annually, so without this there was
    no way to record a renewal, and no way to clear a compliance alert on
    anyone already activated. The date is the only thing this touches; the
    pillars belong to the activation workflow.
    """
    readiness = get_or_create_readiness(person, project)
    readiness.entry_medical_date = _clean_entry_medical_date(entry_medical_date)
    readiness.save(update_fields=["entry_medical_date", "updated_at"])
    record_event(
        actor,
        "readiness.entry_medical_recorded",
        target=readiness,
        person=str(person),
        project=project.code,
        reason=str(readiness.entry_medical_date),
    )
    return readiness


def readiness_blockers(readiness: ReadinessRecord) -> list[dict[str, str]]:
    """Return the concrete operational reasons activation is blocked.

    This is deliberately shared by the readiness UI and the activation gate so
    staff see the same explanation before and after attempting activation.
    """
    blockers = []
    checks = (
        ("medical", _("Medical"), _("Medical clearance is incomplete.")),
        ("gear", _("Gear"), _("Required equipment is incomplete.")),
        ("accommodation", _("Accommodation"), _("Accommodation is incomplete.")),
        ("transport", _("Transport"), _("Transport is incomplete.")),
    )
    transport_enabled = getattr(settings, "FEATURE_FLAGS", {}).get("transport", True)
    for pillar, label, incomplete_message in checks:
        if pillar == "transport" and not transport_enabled:
            continue
        state = getattr(readiness, f"{pillar}_state")
        if state == PillarState.INCOMPLETE:
            blockers.append(
                {"field": pillar, "label": label, "message": incomplete_message}
            )
        elif (
            state == PillarState.NOT_APPLICABLE
            and not getattr(readiness, f"{pillar}_na_reason", "").strip()
        ):
            blockers.append(
                {
                    "field": f"{pillar}_reason",
                    "label": label,
                    "message": _("A reason is required when this is not applicable."),
                }
            )

    expiry = medical_expiry(readiness)
    if (
        readiness.medical_state == PillarState.COMPLETE
        and expiry
        and expiry < timezone.localdate()
    ):
        # A ticked pillar says "we checked"; the date says when. Without this,
        # a medical from three years ago activates cleanly and then shows as
        # expired in Compliance a second later, with nothing having stopped it.
        blockers.append(
            {
                "field": "entry_medical_date",
                "label": _("Medical"),
                "message": _(
                    "The entry medical expired on %(date)s. Record the current "
                    "certificate date before activating."
                )
                % {"date": expiry},
            }
        )
    return blockers


def medical_expiry(readiness) -> dt.date | None:
    """When the recorded entry medical runs out, or None if none is recorded.

    One definition, used by the activation gate, the readiness screen and the
    compliance alerts — three places that disagreed about the same date is how
    an unclearable alert got shipped once already.
    """
    if not readiness or not readiness.entry_medical_date:
        return None
    months = getattr(settings, "MEDICAL_VALIDITY_MONTHS", 12)
    return add_months(readiness.entry_medical_date, months)


@transaction.atomic
def update_readiness(
    readiness,
    *,
    actor=None,
    states: dict,
    na_reasons: dict | None = None,
    entry_medical_date=None,
):
    """Set the four pillar states (§11.6). Medical and gear cannot be N/A;
    accommodation/transport require an explicit reason when marked N/A."""
    na_reasons = na_reasons or {}
    valid = set(PillarState.values)
    transport_enabled = getattr(settings, "FEATURE_FLAGS", {}).get("transport", True)
    for pillar in ("medical", "gear", "accommodation", "transport"):
        if pillar == "transport" and not transport_enabled:
            readiness.transport_state = PillarState.NOT_APPLICABLE
            readiness.transport_na_reason = "Feature disabled"
            continue
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
                    raise WorkflowError(
                        f"A reason is required to mark {pillar} not-applicable."
                    )
                setattr(readiness, f"{pillar}_na_reason", reason)
            else:
                setattr(readiness, f"{pillar}_na_reason", "")

    if entry_medical_date is not None:
        readiness.entry_medical_date = _clean_entry_medical_date(entry_medical_date)

    # A ticked Medical with no date passes activation and then leaves a
    # compliance alert nobody can clear: the alert keys on the date, and once
    # the person is Working the readiness form is no longer shown. It is also
    # what the annual expiry counts from, so a blank date has no expiry at all.
    if (
        readiness.medical_state == PillarState.COMPLETE
        and not readiness.entry_medical_date
    ):
        raise WorkflowError(
            _("Record the entry medical date before marking Medical complete.")
        )
    readiness.submitted_by = (
        actor if getattr(actor, "is_authenticated", False) else None
    )
    readiness.submitted_at = timezone.now()
    readiness.save()
    record_event(
        actor, "readiness.updated", target=readiness, ready=readiness.is_ready()
    )
    return readiness


def _assert_ready(person, project):
    """The four-pillar gate (ADR 0018). Shared by request and decision, because
    readiness stays editable after a request is raised - a pillar can regress
    between the two, and approving a no-longer-ready worker would defeat the
    gate the approval exists to double-check."""
    readiness = ReadinessRecord.objects.filter(person=person, project=project).first()
    if readiness is None:
        raise WorkflowError(
            _(
                "Cannot activate this worker because no readiness record has been completed."
            )
        )
    blockers = readiness_blockers(readiness)
    if blockers:
        raise WorkflowError(
            _("Cannot activate this worker until: %(items)s")
            % {
                "items": "; ".join(str(blocker["message"]) for blocker in blockers),
            }
        )
    return readiness


@transaction.atomic
def request_activation(person, project, *, actor=None):
    """Raise a manager-decidable activation request (plan §12.4).

    This does **not** change the person's status - that is the whole point.
    The coordinator who completed readiness asks; a manager decides.
    """
    readiness = _assert_ready(person, project)
    existing = ActivationApproval.objects.filter(
        person=person, project=project, status=ActivationApprovalStatus.PENDING
    ).first()
    if existing is not None:
        raise WorkflowError(_("An activation request is already awaiting a decision."))

    approval = ActivationApproval.objects.create(
        person=person,
        project=project,
        readiness=readiness,
        requested_by=actor if getattr(actor, "is_authenticated", False) else None,
        # What the manager is being asked to approve, frozen at request time.
        pillar_snapshot={
            "medical": readiness.medical_state,
            "gear": readiness.gear_state,
            "accommodation": readiness.accommodation_state,
            "transport": readiness.transport_state,
            "accommodation_na_reason": readiness.accommodation_na_reason,
            "transport_na_reason": readiness.transport_na_reason,
            "entry_medical_date": (
                readiness.entry_medical_date.isoformat()
                if readiness.entry_medical_date
                else None
            ),
        },
    )
    record_event(
        actor,
        "activation.requested",
        target=approval,
        person=str(person),
        project=project.code,
    )
    return approval


@transaction.atomic
def decide_activation(approval, decision, *, actor=None, reason=""):
    """Manager decision on a pending activation request.

    ``approve`` moves the person to Working; ``reject`` closes the request and
    leaves them in readiness so the coordinator can fix what was wrong and ask
    again. A rejection must say why - that sentence is the entire value of a
    rejection to whoever has to act on it.
    """
    if approval.status != ActivationApprovalStatus.PENDING:
        raise WorkflowError(_("Only a pending activation request can be decided."))
    # Separation of duties used to be enforced here by refusing the decision.
    # An office can have a single administrator, and refusing left activation
    # permanently impossible for them (ADR 0031). The control is now visibility
    # rather than prevention: the decision goes through and the audit event says
    # it was self-approved.
    actor_pk = getattr(actor, "pk", None)
    self_approved = actor_pk is not None and approval.requested_by_id == actor_pk

    if decision == "approve":
        # Re-check the gate: readiness may have regressed since the request.
        _assert_ready(approval.person, approval.project)
        approval.status = ActivationApprovalStatus.APPROVED
        activate_on_project(
            approval.person, approval.project, actor=actor, reason="activation approved"
        )
    elif decision == "reject":
        if not (reason or "").strip():
            raise WorkflowError(_("A rejection must state a reason."))
        approval.status = ActivationApprovalStatus.REJECTED
    else:
        raise WorkflowError(_("Decision must be 'approve' or 'reject'."))

    approval.decision_reason = (reason or "").strip()[:300]
    approval.decided_by = actor if getattr(actor, "is_authenticated", False) else None
    approval.decided_at = timezone.now()
    approval.save(
        update_fields=["status", "decision_reason", "decided_by", "decided_at"]
    )
    # Only carried when true, so the ordinary two-person decision stays quiet
    # and a search for self-approvals returns exactly them.
    extra = {"self_approved": True} if self_approved else {}
    record_event(
        actor,
        f"activation.{approval.status}",
        target=approval,
        person=str(approval.person),
        project=approval.project.code,
        **extra,
    )
    return approval


@transaction.atomic
def exit_person(
    person,
    *,
    actor=None,
    reason: str = "",
    outcome: str = "available",
    inactive_reason=None,
):
    """Exit reconciliation (plan §11.13): end the active project assignment,
    release the room, return all issued equipment, and recycle the person to
    Available (default) or mark them Inactive.

    Reconciliation steps owned by feature apps — room release, equipment return
    (flagged items stay for the deduction-review queue, Q2) — run via the
    registered ``exit_hooks``, so core carries no feature imports (ADR 0021).

    When exiting to Inactive, a structured ``inactive_reason`` (InactiveReason,
    Q5 catalog) and the since-date are recorded on the person.
    """
    from django.utils import timezone

    end_assignment(person, actor=actor, reason=reason or "exit")
    for hook in exit_hooks:
        hook(person, actor=actor)

    # A waiver is spent once it has been used. Leaving it set would reopen the
    # readiness panel the moment this person is recycled to Available, on a
    # record describing work they have already finished (ADR 0031).
    ReadinessRecord.objects.filter(person=person, trial_waived=True).update(
        trial_waived=False
    )

    if outcome == "inactive" and person.lifecycle_status == LifecycleStatus.AVAILABLE:
        person.set_status(
            LifecycleStatus.INACTIVE, actor=actor, reason=reason or "exit"
        )
        person.inactive_reason = inactive_reason
        person.inactive_since = timezone.localdate()
        person.save(update_fields=["inactive_reason", "inactive_since", "updated_at"])

    record_event(
        actor,
        "person.exited",
        target=person,
        reason=reason,
        outcome=outcome,
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
        person.set_status(
            LifecycleStatus.AVAILABLE, actor=actor, reason=reason or "exit"
        )
    return assignment


@transaction.atomic
def save_project(project, *, actor=None, old=None):
    """Create or update a project, audited.

    Mirrors `features.logistics.services.save_accommodation`. Exists so project
    master data goes through the service layer like everything else - Django
    admin was the only way to write one before, and it records no audit event.
    """
    project.save()
    record_event(
        actor,
        "project.updated" if old else "project.created",
        target=project,
        old=old or {},
        new={
            "name": project.name,
            "partner": project.partner,
            "code": project.code,
            "office": str(project.office) if project.office_id else "",
            "financial_reporting_eligible": project.financial_reporting_eligible,
            "is_active": project.is_active,
        },
    )
    return project


@transaction.atomic
def set_project_active(project, *, active, actor=None):
    """Deactivate or reactivate a project.

    Deletion is not offered and cannot be: ProjectAssignment, TrialAssignment,
    FinancialMonth and TransportWeek all PROTECT their project. Deactivation is
    the honest equivalent, and the project list already filters on it.
    """
    if project.is_active == active:
        return project
    project.is_active = active
    project.save(update_fields=["is_active", "updated_at"])
    record_event(
        actor,
        "project.reactivated" if active else "project.deactivated",
        target=project,
        code=project.code,
    )
    return project
