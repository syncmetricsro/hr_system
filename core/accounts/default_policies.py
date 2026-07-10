"""Neutral core policies — deny-by-default (Stage B3, ADR 0021).

Used when no client supplies ``CLIENT_POLICIES``: no role holds any gated
action (superusers still pass ``can()``'s explicit bypass), the lifecycle
workflow is permissive between the defined statuses, and sensitive fields are
visible to superusers only. A real client (e.g. ``clients.jober.policies``)
overrides all three.
"""

from __future__ import annotations

from core.accounts.models import Role
from core.accounts.permissions import Action

# No grants: authorization is restrictive by default.
ACTION_ROLES: dict[Action, frozenset[Role]] = {action: frozenset() for action in Action}

# Workflow is permissive by default: any transition between defined statuses.
# (Authorization above is what actually restricts who may do things.)
ALLOWED_TRANSITIONS: dict[str, set[str]] | None = None  # None = allow all


def can_view_sensitive(viewer, person) -> bool:
    return bool(getattr(viewer, "is_superuser", False))
