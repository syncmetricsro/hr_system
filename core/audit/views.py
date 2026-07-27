"""Audit log browser (production-readiness slice, 2026-07-12).

Every mutation already lands in the append-only ``AuditEvent`` table via
``record_event``; this read-only page makes "who did what" visible to the
oversight roles (``audit.view`` — managers and observers in both clients).
"""

from __future__ import annotations

import datetime as dt

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from core.accounts.permissions import Action, require_action
from core.audit.models import AuditEvent
from core.audit.presentation import audit_action_label, audit_reason_label
from core.people.naming import fold_name
from core.offices.scoping import people_scope_q

PAGE_SIZE = 50


def _parse_date(value: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


@require_action(Action.AUDIT_VIEW)
def audit_log(request: HttpRequest) -> HttpResponse:
    events = AuditEvent.objects.select_related("actor", "person")

    # Office scoping (ADR 0026). The audit log had none: a Velky Meder manager
    # could read every action taken on Gyor and Dunajska Streda workers, which
    # is the same boundary breach the People and Finance surfaces already close.
    #
    # Events with no attributed person stay visible to everyone. They are
    # configuration and system actions - catalogue edits, logins, seeds - which
    # carry no worker's data and belong to no office; hiding them would blind a
    # manager to their own app's history to no benefit. Decision recorded here
    # rather than left implicit, per J1.
    person_scope = people_scope_q(request.user, prefix="person__")
    if person_scope is not None:
        events = events.filter(person_scope | Q(person__isnull=True))

    actor = request.GET.get("actor", "").strip()
    if actor:
        events = events.filter(actor__email__icontains=actor)

    action = request.GET.get("action", "").strip()
    if action:
        events = events.filter(action=action)

    target = request.GET.get("target", "").strip()
    if target:
        events = events.filter(target_type__iexact=target)

    worker = request.GET.get("worker", "").strip()
    if worker:
        # Match on the attributed person, not on target_type="Person". A
        # certificate upload targets the Certificate and an equipment issue the
        # EquipmentIssue; both are events *about* a worker, and the old filter
        # found neither - which is what made it look broken (J1).
        #
        # Folded comparison so "horvat" finds "Horváthová": Slovak and
        # Hungarian names carry accents that people routinely omit when typing.
        events = events.filter(person__search_fold__contains=fold_name(worker))

    date_from = _parse_date(request.GET.get("from", ""))
    if date_from:
        events = events.filter(created_at__date__gte=date_from)
    date_to = _parse_date(request.GET.get("to", ""))
    if date_to:
        events = events.filter(created_at__date__lte=date_to)

    page = Paginator(events, PAGE_SIZE).get_page(request.GET.get("page"))
    for event in page:
        event.action_label = audit_action_label(event.action)
        event.reason_label = audit_reason_label(event.reason)

    known_actions = (
        AuditEvent.objects.order_by("action")
        .values_list("action", flat=True)
        .distinct()
    )

    return render(
        request,
        "pages/audit_log.html",
        {
            "page": page,
            "filters": {
                "actor": actor,
                "action": action,
                "target": target,
                "worker": worker,
                "from": request.GET.get("from", ""),
                "to": request.GET.get("to", ""),
            },
            # Values remain immutable action codes; only their displayed labels are
            # localized. Distinct values keep the filter dropdowns honest.
            "known_actions": [
                {"value": value, "label": audit_action_label(value)}
                for value in known_actions
            ],
            "known_targets": AuditEvent.objects.exclude(target_type="")
            .order_by("target_type")
            .values_list("target_type", flat=True)
            .distinct(),
        },
    )
