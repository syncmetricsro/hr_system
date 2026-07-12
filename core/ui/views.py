from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse

from core.accounts.models import Role
from core.ui import registry
from core.people.models import LifecycleStatus, Person
from core.people.services import inactive_by_reason
from core.projects.models import Project, TrialAssignment, TrialOutcome


def healthz(_request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok", content_type="text/plain")


@login_required
def reports(request: HttpRequest) -> TemplateResponse:
    """The single operational overview and drill-down reporting surface."""
    people = Person.objects.filter(is_archived=False)
    has_trials = registry.flag_enabled("recruitment_trials")
    pending_trials = TrialAssignment.objects.filter(outcome=TrialOutcome.PENDING)
    if getattr(request.user, "role", None) == Role.COORDINATOR:
        pending_trials = pending_trials.filter(project__responsible_coordinators=request.user)
    status_counts = [
        {
            "value": value,
            "label": label,
            "count": people.filter(lifecycle_status=value).count(),
        }
        for value, label in LifecycleStatus.choices
    ]
    return TemplateResponse(
        request,
        "pages/reports.html",
        {
            "active_projects": Project.objects.filter(is_active=True).count(),
            "total_people": people.count(),
            "pending_trials": pending_trials.count(),
            "has_trials": has_trials,
            "status_counts": status_counts,
            "inactive_by_reason": inactive_by_reason(),
            # Feature contributions (registered via the core registry).
            "report_tiles": registry.report_tiles(request),
            "report_panels": registry.report_panels(request),
        },
    )


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Compatibility route for the former separate Overview page."""
    return reports(request)
