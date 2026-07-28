"""Staff activity statistics (J2) - the core half.

The client accepted that the audit log is a traceability tool and not a
reporting one, then asked for the reporting separately. This is that reporting:
read-only aggregation over records the app already keeps, with no denormalised
counters anywhere.

Only the recruiter figures live here, because they come from `core.people`.
Anything drawn from a feature's own records - equipment issuance, accommodation
transfers - arrives through `core.ui.registry.register_staff_activity_panel`,
so core never imports a feature in order to report on it.

The stated purpose of the recruiter table is **spotting a large gap between two
recruiters**, so every recruiter is listed, including those who registered
nobody in the period. A table that silently drops its zero rows cannot answer
the question it exists for.
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import Count, Q

from core.accounts.models import Role
from core.accounts.permissions import user_office_scope
from core.people.models import Person


def _registration_filter(period, scope):
    """People registered inside the period, narrowed to the caller's offices.

    Built from `period.ranges` rather than start..end so a gapped selection
    ("January and March") does not quietly count February.
    """
    condition = Q()
    for start, end in period.ranges:
        condition |= Q(owned_people__created_at__date__range=(start, end))
    if scope is not None:
        condition &= Q(owned_people__office__in=scope)
    return condition


def recruiter_productivity(period, user):
    """How many people each recruiter registered in `period`, comparable side
    by side.

    `user` is required: this aggregates every office's registrations, and a
    company-wide table is a cross-office read even though it opens no single
    record (ADR 0026).
    """
    scope = user_office_scope(user)
    condition = _registration_filter(period, scope)

    rows = (
        get_user_model()
        .objects.filter(Q(role=Role.RECRUITER) | Q(owned_people__isnull=False))
        .distinct()
        .annotate(registered=Count("owned_people", filter=condition, distinct=True))
        .order_by("-registered", "email")
    )
    return [{"recruiter": row, "registered": row.registered} for row in rows]


def people_registered(period, user):
    """The same population as one headline figure."""
    scope = user_office_scope(user)
    people = Person.objects.filter(period.filter_q("created_at__date"))
    if scope is not None:
        people = people.filter(office__in=scope)
    return people.count()
