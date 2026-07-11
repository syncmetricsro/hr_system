"""Jober client policies (Stage B3, ADR 0021).

The role grants (mirrored by docs/permissions/jober-permission-matrix.md), the
lifecycle transition values (plan §9.3/§12), and the sensitive-field visibility
rule (phase1-open-questions Q4) — moved verbatim from core. The mechanisms
(``Action``, ``can()``, ``set_status``, panels) stay in core and resolve this
module via ``settings.CLIENT_POLICIES``.
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
    Action.INTAKE_CREATE_EDIT: frozenset({_RECRUITER, _MANAGER}),
    Action.INTAKE_ASSIGN_TRIAL: frozenset({_RECRUITER, _MANAGER}),
    Action.PERSON_RECYCLE_AVAILABLE: frozenset({_RECRUITER, _COORDINATOR, _MANAGER}),
    Action.SMS_SEND: frozenset({_RECRUITER, _COORDINATOR, _MANAGER}),
    Action.PROJECT_ASSIGN: frozenset({_COORDINATOR, _MANAGER}),
    Action.TRIAL_RECORD_OUTCOME: frozenset({_COORDINATOR, _MANAGER}),
    Action.READINESS_COMPLETE: frozenset({_COORDINATOR, _MANAGER}),
    Action.ROOM_ASSIGN: frozenset({_COORDINATOR, _MANAGER}),
    Action.EQUIPMENT_ISSUE_RETURN: frozenset({_COORDINATOR, _MANAGER}),
    Action.TRANSPORT_RECORD: frozenset({_COORDINATOR, _MANAGER}),
    Action.EXIT_RECONCILE: frozenset({_COORDINATOR, _MANAGER}),
    Action.APPROVAL_ACTIVATE: frozenset({_MANAGER}),
    Action.PROJECT_MANAGE: frozenset({_MANAGER}),
    Action.ACCOMMODATION_MANAGE: frozenset({_MANAGER}),
    Action.EQUIPMENT_REVIEW_DEDUCTION: frozenset({_MANAGER}),
    Action.CATALOG_MANAGE: frozenset({_MANAGER}),
    Action.USER_MANAGE: frozenset({_MANAGER}),
    Action.BLACKLIST_PROPOSE: frozenset({_COORDINATOR, _MANAGER}),
    Action.BLACKLIST_DECIDE: frozenset({_MANAGER}),
    Action.SMS_MANAGE_TEMPLATES: frozenset({_MANAGER}),
    # Checklists feature is off for Jober (Stage C, ADR 0022); grant mirrors
    # the coordinator/manager pattern should Jober ever enable it.
    Action.CHECKLIST_TICK: frozenset({_COORDINATOR, _MANAGER}),
    # Advances ledger is off for Jober (Stage C, ADR 0022); grants mirror the
    # finance pattern should Jober ever enable it.
    Action.LEDGER_ENTER: frozenset({_MANAGER}),
    Action.LEDGER_VIEW: frozenset({_MANAGER, _OBSERVER}),
    Action.PAYSLIP_MANAGE: frozenset({_MANAGER}),
    Action.FINANCE_MANAGE: frozenset({_MANAGER}),
    Action.EXPORT_APPROVED: frozenset({_MANAGER, _OBSERVER}),
    Action.BLACKLIST_VIEW_REASON: frozenset({_COORDINATOR, _MANAGER}),
    Action.FEEDBACK_VIEW: frozenset({_MANAGER}),
    Action.FINANCE_VIEW_SUMMARY: frozenset({_MANAGER, _OBSERVER}),
    Action.AUDIT_VIEW: frozenset({_MANAGER}),
}

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


def can_view_sensitive(viewer, person) -> bool:
    """Whether ``viewer`` may see a person's sensitive fields.

    Per plan §8.1 and phase1-open-questions Q4: sensitive fields (DOB, place of
    birth, disability flag/type, identifiers) are visible to managers, observers,
    the recruiter who entered the person, and the person's responsible
    coordinator(s) — and hidden from unconnected recruiters/coordinators.
    """
    if viewer is None or not getattr(viewer, "is_authenticated", False):
        return False
    if getattr(viewer, "is_superuser", False):
        return True

    try:
        role = Role(viewer.role)
    except (ValueError, AttributeError):
        return False

    # Oversight roles always see sensitive data.
    if role in (Role.MANAGER, Role.OBSERVER):
        return True

    # The recruiter who entered the person.
    if person.owning_recruiter_id and viewer.pk == person.owning_recruiter_id:
        return True

    # A coordinator responsible for the person's current project.
    if role == Role.COORDINATOR and viewer.pk in person.responsible_coordinator_ids():
        return True

    return False
