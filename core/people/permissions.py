from __future__ import annotations

from core.accounts.policies import get_policies


def can_view_sensitive(viewer, person) -> bool:
    """Sensitive-field visibility is client policy (Stage B3, ADR 0021): the
    rule lives in the CLIENT_POLICIES module (Jober: clients/jober/policies.py,
    per phase1-open-questions Q4); this core shim keeps the call sites stable."""
    return get_policies().can_view_sensitive(viewer, person)
