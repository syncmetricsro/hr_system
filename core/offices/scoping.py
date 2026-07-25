"""Who may see a Person, given office scoping (ADR 0026 Phase B).

Most scoped models answer this with a plain ``office__in=scope``. ``Person``
needs one extra rule, decided 2026-07-25: a person with **no office** is
visible to the recruiter who owns them (and to unrestricted roles), but to
nobody else.

Why the exception exists: intake only infers an office when the recruiter
belongs to exactly one, so a recruiter working several offices creates people
with ``office=None``. Under a plain ``office__in`` filter those records would
be invisible to *everyone* except Observer - including the recruiter who just
created them - which orphans them in practice. Making them universally
visible instead would punch a hole in the boundary, so ownership is the
middle ground.

Kept in one module so the rule is stated once rather than re-derived at each
of the ~8 call sites that need it.
"""

from __future__ import annotations

from django.db.models import Q

from core.accounts.permissions import user_office_scope


def people_scope_q(user, prefix: str = "") -> Q | None:
    """``Q`` restricting a queryset to the people ``user`` may see.

    Returns ``None`` for unrestricted callers - the established "don't
    filter" sentinel, matching ``user_office_scope``. ``prefix`` names the
    ORM path to ``Person`` for querysets rooted elsewhere (e.g.
    ``"person__"`` when filtering checklist items).
    """
    scope = user_office_scope(user)
    if scope is None:
        return None
    if user is None or not user.is_authenticated:
        # Fail closed: never match. (Guarding here keeps callers from having
        # to special-case anonymous before building a Q against `user`.)
        return Q(pk__in=[])
    return Q(**{f"{prefix}office__in": scope}) | Q(
        **{f"{prefix}office__isnull": True, f"{prefix}owning_recruiter": user}
    )


def scope_people(queryset, user, prefix: str = ""):
    """Apply :func:`people_scope_q` to ``queryset`` (a no-op when unrestricted)."""
    condition = people_scope_q(user, prefix)
    if condition is None:
        return queryset
    return queryset.filter(condition)


def may_see_person(user, person) -> bool:
    """Object-level equivalent of :func:`people_scope_q`, for 403 guards."""
    scope = user_office_scope(user)
    if scope is None:
        return True
    if user is None or not user.is_authenticated:
        return False
    if person.office_id is None:
        return person.owning_recruiter_id == user.pk
    return scope.filter(pk=person.office_id).exists()
