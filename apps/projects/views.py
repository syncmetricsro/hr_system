from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.accounts.models import Role
from apps.accounts.permissions import Action, require_action
from apps.people.models import Person
from apps.projects.models import (
    AssignmentStatus,
    Project,
    TrialAssignment,
    TrialOutcome,
)
from apps.projects.services import (
    WorkflowError,
    activate_from_readiness,
    get_or_create_readiness,
    record_trial_outcome,
    schedule_trial,
    update_readiness,
)


@login_required
def project_list(request: HttpRequest) -> TemplateResponse:
    projects = Project.objects.all().prefetch_related("responsible_coordinators")
    return TemplateResponse(request, "pages/project_list.html", {"projects": projects})


@login_required
def project_detail(request: HttpRequest, pk: int) -> TemplateResponse:
    project = get_object_or_404(
        Project.objects.prefetch_related("responsible_coordinators"), pk=pk
    )
    workers = (
        project.assignments.filter(status=AssignmentStatus.ACTIVE)
        .select_related("person")
        .order_by("person__last_name")
    )
    transport_weeks = project.transport_weeks.all()[:8]
    return TemplateResponse(
        request,
        "pages/project_detail.html",
        {"project": project, "workers": workers, "transport_weeks": transport_weeks},
    )


@login_required
def trials_queue(request: HttpRequest) -> TemplateResponse:
    """Coordinator field view: trials awaiting an outcome.

    A coordinator sees only their own projects' trials (routing); managers,
    observers, and recruiters see all (broad read)."""
    trials = (
        TrialAssignment.objects.filter(outcome=TrialOutcome.PENDING)
        .select_related("person", "project")
        .order_by("scheduled_date")
    )
    scoped = getattr(request.user, "role", None) == Role.COORDINATOR
    if scoped:
        trials = trials.filter(project__responsible_coordinators=request.user)
    return TemplateResponse(request, "pages/trials_queue.html", {"trials": trials, "scoped": scoped})


@require_POST
@require_action(Action.INTAKE_ASSIGN_TRIAL)
def assign_trial(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    project = get_object_or_404(Project, pk=request.POST.get("project"))
    try:
        schedule_trial(person, project, actor=request.user, note=request.POST.get("note", ""))
        messages.success(request, _("Trial scheduled."))
    except WorkflowError as exc:
        messages.error(request, str(exc))
    return redirect("person_detail", pk=person.pk)


@require_POST
@require_action(Action.TRIAL_RECORD_OUTCOME)
def trial_outcome(request: HttpRequest, trial_pk: int) -> HttpResponse:
    trial = get_object_or_404(TrialAssignment, pk=trial_pk)
    try:
        record_trial_outcome(trial, request.POST.get("outcome", ""), actor=request.user)
        messages.success(request, _("Trial outcome recorded."))
    except WorkflowError as exc:
        messages.error(request, str(exc))
    return redirect("person_detail", pk=trial.person_id)


@require_POST
@require_action(Action.READINESS_COMPLETE)
def readiness_update(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    project = get_object_or_404(Project, pk=request.POST.get("project"))
    readiness = get_or_create_readiness(person, project)
    states = {
        pillar: request.POST.get(pillar)
        for pillar in ("medical", "gear", "accommodation", "transport")
    }
    try:
        update_readiness(readiness, actor=request.user, states=states)
        messages.success(request, _("Readiness saved."))
    except WorkflowError as exc:
        messages.error(request, str(exc))
    return redirect("person_detail", pk=person.pk)


@require_POST
@require_action(Action.PROJECT_ASSIGN)
def activate_person(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    project = get_object_or_404(Project, pk=request.POST.get("project"))
    try:
        activate_from_readiness(person, project, actor=request.user)
        messages.success(request, _("Activated — now Working."))
    except WorkflowError as exc:
        messages.error(request, str(exc))
    return redirect("person_detail", pk=person.pk)
