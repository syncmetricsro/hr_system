from __future__ import annotations

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory

from core.accounts.models import Role, User
from core.accounts.permissions import (
    ACTION_ROLES,
    ROLE_ACTIONS,
    Action,
    can,
    require_action,
)

# Jober-specific URLs/policies/languages — excluded from the corvinum lane.
pytestmark = pytest.mark.jober_only


def _user(role: Role) -> User:
    # Unsaved instance is enough: can() only reads .is_authenticated and .role.
    return User(email=f"{role.value}@demo.jober.test", role=role)


@pytest.mark.parametrize(
    "role,action,expected",
    [
        (Role.MANAGER, Action.APPROVAL_ACTIVATE, True),
        (Role.COORDINATOR, Action.APPROVAL_ACTIVATE, False),
        (Role.RECRUITER, Action.APPROVAL_ACTIVATE, False),
        (Role.OBSERVER, Action.APPROVAL_ACTIVATE, False),
        (Role.RECRUITER, Action.INTAKE_CREATE_EDIT, True),
        (Role.COORDINATOR, Action.INTAKE_CREATE_EDIT, False),
        (Role.COORDINATOR, Action.TRIAL_RECORD_OUTCOME, True),
        (Role.RECRUITER, Action.TRIAL_RECORD_OUTCOME, False),
        (Role.OBSERVER, Action.FINANCE_VIEW_SUMMARY, True),
        (Role.OBSERVER, Action.SMS_SEND, False),
        (Role.MANAGER, Action.BLACKLIST_VIEW_REASON, True),
        (Role.COORDINATOR, Action.BLACKLIST_VIEW_REASON, True),
        (Role.RECRUITER, Action.BLACKLIST_VIEW_REASON, False),
        (Role.COORDINATOR, Action.BLACKLIST_PROPOSE, True),
        (Role.COORDINATOR, Action.BLACKLIST_DECIDE, False),
    ],
)
def test_can_matches_matrix(role, action, expected):
    assert can(_user(role), action) is expected


def test_anonymous_can_do_nothing():
    anon = AnonymousUser()
    assert all(not can(anon, action) for action in Action)


def test_role_actions_is_consistent_inverse_of_action_roles():
    for action, roles in ACTION_ROLES.items():
        for role in Role:
            assert (action in ROLE_ACTIONS[role]) == (role in roles)


def test_every_action_is_mapped():
    assert set(ACTION_ROLES) == set(Action)


# --- require_action decorator -------------------------------------------------

def _gated_view():
    @require_action(Action.PROJECT_MANAGE)
    def view(request):
        return HttpResponse("ok")

    return view


def test_require_action_redirects_anonymous():
    request = RequestFactory().get("/projekty/")
    request.user = AnonymousUser()
    response = _gated_view()(request)
    assert response.status_code == 302


def test_require_action_forbids_wrong_role():
    request = RequestFactory().get("/projekty/")
    request.user = _user(Role.OBSERVER)
    with pytest.raises(PermissionDenied):
        _gated_view()(request)


def test_require_action_allows_permitted_role():
    request = RequestFactory().get("/projekty/")
    request.user = _user(Role.MANAGER)
    response = _gated_view()(request)
    assert response.status_code == 200
    assert response.content == b"ok"
