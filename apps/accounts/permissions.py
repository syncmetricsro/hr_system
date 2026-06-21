from __future__ import annotations

from enum import Enum
from functools import wraps
from typing import Callable

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse

from apps.accounts.models import Role


class Action(str, Enum):
    """Gated write/sensitive actions, derived directly from plan §8.2–8.5.

    Reads are NOT listed here: per ADR 0008 the platform grants broad internal
    read visibility, so any authenticated internal role may read ordinary
    operational records. Only the actions below are restricted, and the
    ``ROLE_ACTIONS`` map below is the single source mirrored by
    docs/permissions/permission-matrix.md.
    """

    # Recruiter intake / candidate routing
    INTAKE_CREATE_EDIT = "intake.create_edit"
    INTAKE_ASSIGN_TRIAL = "intake.assign_trial"
    PERSON_RECYCLE_AVAILABLE = "person.recycle_available"
    SMS_SEND = "sms.send"

    # Coordinator field operations
    TRIAL_RECORD_OUTCOME = "trial.record_outcome"
    READINESS_COMPLETE = "readiness.complete"
    ROOM_ASSIGN = "room.assign"
    EQUIPMENT_ISSUE_RETURN = "equipment.issue_return"
    TRANSPORT_RECORD = "transport.record"
    EXIT_RECONCILE = "exit.reconcile"

    # Manager / Administrator only
    APPROVAL_ACTIVATE = "approval.activate"
    PROJECT_MANAGE = "project.manage"
    ACCOMMODATION_MANAGE = "accommodation.manage"
    CATALOG_MANAGE = "catalog.manage"
    USER_MANAGE = "user.manage"
    BLACKLIST_DECIDE = "blacklist.decide"
    SMS_MANAGE_TEMPLATES = "sms.manage_templates"
    FINANCE_MANAGE = "finance.manage"
    EXPORT_APPROVED = "export.approved"

    # Sensitive reads (carved out of the broad-read default)
    BLACKLIST_VIEW_REASON = "blacklist.view_reason"
    FEEDBACK_VIEW = "feedback.view"
    FINANCE_VIEW_SUMMARY = "finance.view_summary"
    AUDIT_VIEW = "audit.view"


# Action -> set of roles permitted to perform it. Manager is listed explicitly
# (not special-cased) so the mapping stays a literal mirror of the matrix doc.
_RECRUITER = Role.RECRUITER
_COORDINATOR = Role.COORDINATOR
_MANAGER = Role.MANAGER
_OBSERVER = Role.OBSERVER

ACTION_ROLES: dict[Action, frozenset[Role]] = {
    Action.INTAKE_CREATE_EDIT: frozenset({_RECRUITER, _MANAGER}),
    Action.INTAKE_ASSIGN_TRIAL: frozenset({_RECRUITER, _MANAGER}),
    Action.PERSON_RECYCLE_AVAILABLE: frozenset({_RECRUITER, _COORDINATOR, _MANAGER}),
    Action.SMS_SEND: frozenset({_RECRUITER, _COORDINATOR, _MANAGER}),
    Action.TRIAL_RECORD_OUTCOME: frozenset({_COORDINATOR, _MANAGER}),
    Action.READINESS_COMPLETE: frozenset({_COORDINATOR, _MANAGER}),
    Action.ROOM_ASSIGN: frozenset({_COORDINATOR, _MANAGER}),
    Action.EQUIPMENT_ISSUE_RETURN: frozenset({_COORDINATOR, _MANAGER}),
    Action.TRANSPORT_RECORD: frozenset({_COORDINATOR, _MANAGER}),
    Action.EXIT_RECONCILE: frozenset({_COORDINATOR, _MANAGER}),
    Action.APPROVAL_ACTIVATE: frozenset({_MANAGER}),
    Action.PROJECT_MANAGE: frozenset({_MANAGER}),
    Action.ACCOMMODATION_MANAGE: frozenset({_MANAGER}),
    Action.CATALOG_MANAGE: frozenset({_MANAGER}),
    Action.USER_MANAGE: frozenset({_MANAGER}),
    Action.BLACKLIST_DECIDE: frozenset({_MANAGER}),
    Action.SMS_MANAGE_TEMPLATES: frozenset({_MANAGER}),
    Action.FINANCE_MANAGE: frozenset({_MANAGER}),
    Action.EXPORT_APPROVED: frozenset({_MANAGER, _OBSERVER}),
    Action.BLACKLIST_VIEW_REASON: frozenset({_MANAGER}),
    Action.FEEDBACK_VIEW: frozenset({_MANAGER}),
    Action.FINANCE_VIEW_SUMMARY: frozenset({_MANAGER, _OBSERVER}),
    Action.AUDIT_VIEW: frozenset({_MANAGER}),
}

# Inverted view for convenience: role -> set of actions it may perform.
ROLE_ACTIONS: dict[Role, frozenset[Action]] = {
    role: frozenset(action for action, roles in ACTION_ROLES.items() if role in roles)
    for role in Role
}


def can(user, action: Action) -> bool:
    """True if an authenticated user's role permits ``action``."""
    if user is None or not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False):
        return True
    try:
        role = Role(user.role)
    except ValueError:
        return False
    return action in ROLE_ACTIONS.get(role, frozenset())


def can_read_internal(user) -> bool:
    """Broad internal read gate.

    Defaults to allowing any authenticated internal role to read ordinary
    operational records (plan §8.1 / ADR 0008). Kept behind a single config
    switch so the still-open GDPR recruiter/coordinator read-scope decision can
    be narrowed later WITHOUT hardcoding a split now (open-decisions.md).
    """
    if user is None or not user.is_authenticated:
        return False
    if getattr(settings, "BROAD_INTERNAL_READS", True):
        return True
    # Future narrower split would be wired here once Jober confirms the scope.
    return True


def require_action(action: Action) -> Callable:
    """View decorator: redirect anonymous to login, 403 authenticated-but-denied."""

    def decorator(view: Callable) -> Callable:
        @wraps(view)
        def wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            user = getattr(request, "user", None)
            if user is None or not user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not can(user, action):
                raise PermissionDenied(f"Rola nemá oprávnenie: {action.value}")
            return view(request, *args, **kwargs)

        return wrapped

    return decorator
