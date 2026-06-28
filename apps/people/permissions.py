from __future__ import annotations

from apps.accounts.models import Role


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
