from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse

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
