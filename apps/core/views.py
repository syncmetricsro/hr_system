from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse

from apps.accounts.models import Role
from apps.people.models import LifecycleStatus, Person
from apps.projects.models import Project, TrialAssignment, TrialOutcome


def healthz(_request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok", content_type="text/plain")


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
