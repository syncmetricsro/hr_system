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

from django.core.exceptions import PermissionDenied
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


def assert_person_in_scope(user, person) -> None:
    """Raise ``PermissionDenied`` if ``user`` may not see ``person``.

    Filtering a list does not stop someone typing another office's URL, so
    every view taking a person (or an object hanging off one) needs this too.
    It lives here rather than in one app's ``views.py`` because messaging,
    compliance and people all need the identical check - the first two shipped
    without it precisely because it was a private helper somewhere else.
    """
    if not may_see_person(user, person):
        raise PermissionDenied("This person belongs to another office.")


def assert_office_in_scope(user, office) -> None:
    """``assert_person_in_scope`` for a plain office-carrying object.

    ``office`` may be ``None``, which only unrestricted roles may reach - an
    office-less *non-Person* record has no owning-recruiter fallback to make
    it visible to anyone else.
    """
    scope = user_office_scope(user)
    if scope is None:
        return
    if user is None or not user.is_authenticated:
        raise PermissionDenied("Authentication required.")
    office_id = getattr(office, "pk", office)
    if office_id is None or not scope.filter(pk=office_id).exists():
        raise PermissionDenied("This record belongs to another office.")
