from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse

from apps.accounts.models import Role
from apps.accounts.permissions import Action
from apps.accounts.permissions import can as user_can
from apps.compliance.services import compliance_alerts
from apps.finance.services import company_totals
from apps.logistics.models import Room, RoomAssignment, RoomAssignmentStatus
from apps.logistics.services import issued_equipment_value
from apps.people.models import LifecycleStatus, Person
from apps.people.services import inactive_by_reason
from apps.projects.models import Project, TrialAssignment, TrialOutcome


def healthz(_request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok", content_type="text/plain")


@login_required
def reports(request: HttpRequest) -> TemplateResponse:
    """Read-only operational summary across modules (plan §3)."""
    people = Person.objects.filter(is_archived=False)
    status_counts = [
        (label, people.filter(lifecycle_status=value).count())
        for value, label in LifecycleStatus.choices
    ]
    capacity = sum(Room.objects.values_list("capacity", flat=True))
    occupied = RoomAssignment.objects.filter(status=RoomAssignmentStatus.ACTIVE).count()
    can_finance = user_can(request.user, Action.FINANCE_VIEW_SUMMARY)
    return TemplateResponse(
        request,
        "pages/reports.html",
        {
            "active_projects": Project.objects.filter(is_active=True).count(),
            "total_people": people.count(),
            "pending_trials": TrialAssignment.objects.filter(outcome=TrialOutcome.PENDING).count(),
            "compliance_count": len(compliance_alerts(request.user)),
            "capacity": capacity,
            "occupied": occupied,
            "free": max(capacity - occupied, 0),
            "equipment_value": issued_equipment_value(),
            "status_counts": status_counts,
            "inactive_by_reason": inactive_by_reason(),
            "finance": company_totals() if can_finance else None,
        },
    )


@login_required
def dashboard(request: HttpRequest) -> TemplateResponse:
    people = Person.objects.filter(is_archived=False)
    pending_trials = (
        TrialAssignment.objects.filter(outcome=TrialOutcome.PENDING)
        .select_related("person", "project")
        .order_by("scheduled_date")
    )
    # Coordinators see only their own projects' pending trials (routing).
    if getattr(request.user, "role", None) == Role.COORDINATOR:
        pending_trials = pending_trials.filter(project__responsible_coordinators=request.user)
    metrics = {
        "active_projects": Project.objects.filter(is_active=True).count(),
        "available": people.filter(lifecycle_status=LifecycleStatus.AVAILABLE).count(),
        "working": people.filter(lifecycle_status=LifecycleStatus.WORKING).count(),
        "awaiting_outcome": pending_trials.count(),
    }
    return TemplateResponse(
        request,
        "pages/dashboard.html",
        {"metrics": metrics, "pending_trials": pending_trials[:8]},
    )
