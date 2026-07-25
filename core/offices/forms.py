"""Shared form helper for office-scoped choice fields (ADR 0026 Phase B).

Several forms across core and features offer an ``office`` picker that must
show only the offices the acting user belongs to. Rather than repeat the same
queryset/initial dance in each one, they call ``apply_office_scope`` from
their ``__init__``.
"""

from __future__ import annotations

from core.accounts.permissions import user_office_scope
from core.offices.models import Office


def apply_office_scope(form, user, field_name: str = "office") -> None:
    """Restrict ``form``'s office field to what ``user`` may pick.

    Unrestricted callers (Observer, superuser) and installs with no offices at
    all see every office. A user belonging to exactly one office gets it
    pre-selected, since that is nearly always the intended value - it stays
    editable for the occasional cross-office entry.
    """
    scope = user_office_scope(user)
    field = form.fields[field_name]
    field.queryset = Office.objects.all() if scope is None else scope
    if scope is not None and not form.initial.get(field_name) and scope.count() == 1:
        field.initial = scope.first()
