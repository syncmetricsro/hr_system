"""Audit log browser (production-readiness slice, 2026-07-12).

Every mutation already lands in the append-only ``AuditEvent`` table via
``record_event``; this read-only page makes "who did what" visible to the
oversight roles (``audit.view`` — managers and observers in both clients).
"""

from __future__ import annotations

import datetime as dt

from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from core.accounts.permissions import Action, require_action
from core.audit.models import AuditEvent

PAGE_SIZE = 50


def _parse_date(value: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


@require_action(Action.AUDIT_VIEW)
def audit_log(request: HttpRequest) -> HttpResponse:
    events = AuditEvent.objects.select_related("actor")

    actor = request.GET.get("actor", "").strip()
    if actor:
        events = events.filter(actor__email__icontains=actor)

    action = request.GET.get("action", "").strip()
    if action:
        events = events.filter(action=action)

    target = request.GET.get("target", "").strip()
    if target:
        events = events.filter(target_type__iexact=target)

    date_from = _parse_date(request.GET.get("from", ""))
    if date_from:
        events = events.filter(created_at__date__gte=date_from)
    date_to = _parse_date(request.GET.get("to", ""))
    if date_to:
        events = events.filter(created_at__date__lte=date_to)

    page = Paginator(events, PAGE_SIZE).get_page(request.GET.get("page"))

    return render(request, "pages/audit_log.html", {
        "page": page,
        "filters": {
            "actor": actor,
            "action": action,
            "target": target,
            "from": request.GET.get("from", ""),
            "to": request.GET.get("to", ""),
        },
        # Distinct values keep the filter dropdowns honest without hardcoding.
        "known_actions": AuditEvent.objects.order_by("action").values_list("action", flat=True).distinct(),
        "known_targets": AuditEvent.objects.exclude(target_type="").order_by("target_type").values_list("target_type", flat=True).distinct(),
    })
