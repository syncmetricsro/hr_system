"""CorvinumEU client policies (Stage C0, ADR 0022).

Role grants and lifecycle transitions for the CorvinumEU flag set. Roles reuse
the core set; "HR Admin" maps to ``manager`` for MVP (C-Q9). The lifecycle is
the core lifecycle with the owner-approved demo trial-day workflow enabled.
The status set still awaits client confirmation (C-Q1). Grants cover only the
features CorvinumEU mounts; ledger/checklist actions join here in slices C1/C2.
"""

from __future__ import annotations

from core.accounts.models import Role
from core.accounts.permissions import Action
from core.people.models import LifecycleStatus

_RECRUITER = Role.RECRUITER
_COORDINATOR = Role.COORDINATOR
_MANAGER = Role.MANAGER
_OBSERVER = Role.OBSERVER

ACTION_ROLES: dict[Action, frozenset[Role]] = {
    # People / intake
    Action.INTAKE_CREATE_EDIT: frozenset({_RECRUITER, _MANAGER}),
    Action.INTAKE_ASSIGN_TRIAL: frozenset({_RECRUITER, _COORDINATOR, _MANAGER}),
    Action.PERSON_RECYCLE_AVAILABLE: frozenset({_RECRUITER, _COORDINATOR, _MANAGER}),
    Action.PERSON_ARCHIVE: frozenset({_MANAGER}),
    # Assignment / activation (partner company = project, §5.7)
    Action.PROJECT_ASSIGN: frozenset({_COORDINATOR, _MANAGER}),
    Action.TRIAL_RECORD_OUTCOME: frozenset({_COORDINATOR, _MANAGER}),
    Action.READINESS_COMPLETE: frozenset({_COORDINATOR, _MANAGER}),
    Action.APPROVAL_ACTIVATE: frozenset({_MANAGER}),
    Action.PROJECT_MANAGE: frozenset({_MANAGER}),
    Action.EXIT_RECONCILE: frozenset({_COORDINATOR, _MANAGER}),
    # Equipment (§5.8)
    Action.EQUIPMENT_ISSUE_RETURN: frozenset({_COORDINATOR, _MANAGER}),
    Action.EQUIPMENT_REVIEW_DEDUCTION: frozenset({_MANAGER}),
    # Approval checklists (§5.5)
    Action.CHECKLIST_TICK: frozenset({_COORDINATOR, _MANAGER}),
    # Advance & deduction ledger (§5.10) — office/HR/management only
    Action.LEDGER_ENTER: frozenset({_MANAGER}),
    Action.LEDGER_VIEW: frozenset({_MANAGER, _OBSERVER}),
    # Gross wage ledger — managers record; observers have oversight reads.
    Action.WAGE_MANAGE: frozenset({_MANAGER}),
    Action.WAGE_VIEW: frozenset({_MANAGER, _OBSERVER}),
    # Payslips (ADR 0023) — office/HR only
    Action.PAYSLIP_MANAGE: frozenset({_MANAGER}),
    Action.PAYSLIP_VIEW: frozenset({_MANAGER, _OBSERVER}),
    # Duplicate / blacklist (§5.6)
    Action.BLACKLIST_PROPOSE: frozenset({_COORDINATOR, _MANAGER}),
    Action.BLACKLIST_DECIDE: frozenset({_MANAGER}),
    Action.BLACKLIST_VIEW_REASON: frozenset({_MANAGER}),
    # Administration / oversight
    Action.CATALOG_MANAGE: frozenset({_MANAGER}),
    Action.USER_MANAGE: frozenset({_MANAGER}),
    Action.EXPORT_APPROVED: frozenset({_MANAGER, _OBSERVER}),
    Action.AUDIT_VIEW: frozenset({_MANAGER, _OBSERVER}),
}

# Core lifecycle with TRIAL_DAY enabled for the CorvinumEU demo (C-Q1).
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    LifecycleStatus.AVAILABLE: {
        LifecycleStatus.TRIAL_DAY,
        LifecycleStatus.WORKING,
        LifecycleStatus.INACTIVE,
        LifecycleStatus.BLACKLISTED,
    },
    LifecycleStatus.TRIAL_DAY: {
        LifecycleStatus.AVAILABLE,
        LifecycleStatus.WORKING,
        LifecycleStatus.INACTIVE,
        LifecycleStatus.BLACKLISTED,
    },
    LifecycleStatus.WORKING: {
        LifecycleStatus.AVAILABLE,
        LifecycleStatus.INACTIVE,
        LifecycleStatus.BLACKLISTED,
    },
    LifecycleStatus.INACTIVE: {
        LifecycleStatus.AVAILABLE,
        LifecycleStatus.BLACKLISTED,
    },
    LifecycleStatus.BLACKLISTED: {
        LifecycleStatus.AVAILABLE,
    },
}


def can_view_sensitive(viewer, person) -> bool:
    """Sensitive-field visibility (§4.2): managers/observers always; the
    recruiter who entered the person; the person's responsible coordinator."""
    if viewer is None or not getattr(viewer, "is_authenticated", False):
        return False
    if getattr(viewer, "is_superuser", False):
        return True

    try:
        role = Role(viewer.role)
    except (ValueError, AttributeError):
        return False

    if role in (Role.MANAGER, Role.OBSERVER):
        return True
    if person.owning_recruiter_id and viewer.pk == person.owning_recruiter_id:
        return True
    if role == Role.COORDINATOR and viewer.pk in person.responsible_coordinator_ids():
        return True
    return False
