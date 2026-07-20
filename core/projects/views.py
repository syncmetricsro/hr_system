from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from core.accounts.models import Role
from core.accounts.permissions import Action, require_action
from core.accounts.permissions import can as user_can
from core.people.models import InactiveReason, Person
from core.projects.forms import TrialCreateForm, TrialEditForm, operable_projects
from core.projects.models import (
    AssignmentStatus,
    Project,
    TrialAssignment,
    TrialOutcome,
)
from core.projects.services import (
    WorkflowError,
    activate_from_readiness,
    exit_person,
    get_or_create_readiness,
    record_trial_outcome,
    schedule_trial,
    update_pending_trial,
    update_readiness,
)


def _valid_date(value: str) -> bool:
    try:
        return bool(parse_date(value))
    except ValueError:
        return False


@login_required
def project_list(request: HttpRequest) -> TemplateResponse:
    status = (request.GET.get("status") or "").strip()
    projects = Project.objects.all().prefetch_related("responsible_coordinators")
    if status == "active":
        projects = projects.filter(is_active=True)
    elif status == "inactive":
        projects = projects.filter(is_active=False)
    else:
        status = ""
    return TemplateResponse(
        request,
        "pages/project_list.html",
        {"projects": projects, "project_status": status},
    )


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
    transport_enabled = getattr(settings, "FEATURE_FLAGS", {}).get("transport", True)
    transport_weeks = project.transport_weeks.all()[:8] if transport_enabled else []
    return TemplateResponse(
        request,
        "pages/project_detail.html",
        {
            "project": project, "workers": workers, "transport_weeks": transport_weeks,
            "transport_enabled": transport_enabled,
            "may_transport": transport_enabled and user_can(request.user, Action.TRANSPORT_RECORD)
            and operable_projects(request.user).filter(pk=project.pk).exists(),
        },
    )


@login_required
def _trial_queue_context(request, *, form=None, editing=None):
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
    query = (request.GET.get("q") or "").strip()
    project_value = (request.GET.get("project") or "").strip()
    date_from = (request.GET.get("date_from") or "").strip()
    date_to = (request.GET.get("date_to") or "").strip()
    if query:
        trials = trials.filter(person__search_name__icontains=query)
    if project_value.isdigit():
        trials = trials.filter(project_id=project_value)
    else:
        project_value = ""
    if date_from and _valid_date(date_from):
        trials = trials.filter(scheduled_date__gte=date_from)
    else:
        date_from = ""
    if date_to and _valid_date(date_to):
        trials = trials.filter(scheduled_date__lte=date_to)
    else:
        date_to = ""
    may_schedule = user_can(request.user, Action.INTAKE_ASSIGN_TRIAL)
    return {
        "trials": trials, "scoped": scoped, "query": query,
        "project_filter": project_value, "date_from": date_from, "date_to": date_to,
        "projects": operable_projects(request.user) if may_schedule else Project.objects.filter(is_active=True),
        "may_schedule": may_schedule, "form": form, "editing": editing,
    }


@login_required
def trials_queue(request: HttpRequest) -> TemplateResponse:
    form = None
    editing = None
    if request.GET.get("create") == "1" and user_can(request.user, Action.INTAKE_ASSIGN_TRIAL):
        form = TrialCreateForm(user=request.user)
    edit_value = (request.GET.get("edit") or "").strip()
    if edit_value.isdigit() and user_can(request.user, Action.INTAKE_ASSIGN_TRIAL):
        editing = get_object_or_404(
            TrialAssignment, pk=edit_value, outcome=TrialOutcome.PENDING,
            project__in=operable_projects(request.user),
        )
        form = TrialEditForm(user=request.user, trial=editing)
    return TemplateResponse(request, "pages/trials_queue.html", _trial_queue_context(request, form=form, editing=editing))


@require_POST
@require_action(Action.INTAKE_ASSIGN_TRIAL)
def trial_create(request: HttpRequest) -> HttpResponse:
    form = TrialCreateForm(request.POST, user=request.user)
    if form.is_valid():
        try:
            schedule_trial(
                form.cleaned_data["person"], form.cleaned_data["project"], actor=request.user,
                scheduled_for=form.cleaned_data["scheduled_for"], note=form.cleaned_data["note"],
            )
            messages.success(request, _("Trial scheduled."))
            return redirect("trials_queue")
        except WorkflowError as exc:
            form.add_error(None, exc)
    return TemplateResponse(request, "pages/trials_queue.html", _trial_queue_context(request, form=form), status=400)


@require_POST
@require_action(Action.INTAKE_ASSIGN_TRIAL)
def trial_edit(request: HttpRequest, trial_pk: int) -> HttpResponse:
    trial = get_object_or_404(
        TrialAssignment, pk=trial_pk, outcome=TrialOutcome.PENDING,
        project__in=operable_projects(request.user),
    )
    form = TrialEditForm(request.POST, user=request.user, trial=trial)
    if form.is_valid():
        try:
            update_pending_trial(
                trial, project=form.cleaned_data["project"],
                scheduled_for=form.cleaned_data["scheduled_for"],
                note=form.cleaned_data["note"], actor=request.user,
            )
            messages.success(request, _("Trial updated."))
            return redirect("trials_queue")
        except WorkflowError as exc:
            form.add_error(None, exc)
    return TemplateResponse(
        request, "pages/trials_queue.html",
        _trial_queue_context(request, form=form, editing=trial), status=400,
    )


@require_POST
@require_action(Action.INTAKE_ASSIGN_TRIAL)
def assign_trial(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    project = get_object_or_404(Project, pk=request.POST.get("project"))
    schedule_form = TrialCreateForm(
        {**request.POST.dict(), "person": person.pk}, user=request.user,
    )
    try:
        if not schedule_form.is_valid():
            raise WorkflowError(_("Review the trial details and try again."))
        schedule_trial(
            person, project, actor=request.user,
            scheduled_for=schedule_form.cleaned_data["scheduled_for"], note=request.POST.get("note", ""),
        )
        messages.success(request, _("Trial scheduled."))
    except WorkflowError as exc:
        messages.error(request, str(exc))
    return redirect("person_detail", pk=person.pk)


@require_POST
@require_action(Action.TRIAL_RECORD_OUTCOME)
def trial_outcome(request: HttpRequest, trial_pk: int) -> HttpResponse:
    trials = TrialAssignment.objects.all()
    if getattr(request.user, "role", None) == Role.COORDINATOR:
        trials = trials.filter(project__responsible_coordinators=request.user)
    trial = get_object_or_404(trials, pk=trial_pk)
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
    pillars = ["medical", "gear", "accommodation"]
    if getattr(settings, "FEATURE_FLAGS", {}).get("transport", True):
        pillars.append("transport")
    states = {
        pillar: request.POST.get(pillar)
        for pillar in pillars
    }
    na_reasons = {
        "accommodation": request.POST.get("accommodation_na_reason", ""),
        "transport": request.POST.get("transport_na_reason", ""),
    }
    try:
        update_readiness(
            readiness, actor=request.user, states=states, na_reasons=na_reasons,
            entry_medical_date=request.POST.get("entry_medical_date") or None,
        )
        messages.success(request, _("Readiness saved."))
    except WorkflowError as exc:
        messages.error(request, str(exc))
    return redirect("person_detail", pk=person.pk)


@require_POST
@require_action(Action.EXIT_RECONCILE)
def exit_view(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    outcome = "inactive" if request.POST.get("outcome") == "inactive" else "available"
    reason_obj = None
    if outcome == "inactive" and request.POST.get("inactive_reason"):
        reason_obj = InactiveReason.objects.filter(
            pk=request.POST.get("inactive_reason"), is_active=True
        ).first()
    exit_person(
        person, actor=request.user, reason=request.POST.get("reason", ""),
        outcome=outcome, inactive_reason=reason_obj,
    )
    messages.success(request, _("Exit completed."))
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
