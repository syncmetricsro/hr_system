from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from core.accounts.models import Role
from core.accounts.permissions import Action, require_action, user_office_scope
from core.offices.scoping import may_see_person
from core.accounts.permissions import can as user_can
from core.people.models import InactiveReason, Person
from core.projects.forms import (
    ProjectForm,
    TrialCreateForm,
    TrialEditForm,
    operable_projects,
)
from core.projects.models import (
    ActivationApproval,
    ActivationApprovalStatus,
    AssignmentStatus,
    Project,
    TrialAssignment,
    TrialOutcome,
)
from core.projects.services import (
    WorkflowError,
    decide_activation,
    exit_person,
    get_or_create_readiness,
    record_entry_medical,
    record_trial_outcome,
    request_activation,
    save_project,
    set_project_active,
    schedule_trial,
    update_pending_trial,
    update_readiness,
    waive_trial,
)


def _valid_date(value: str) -> bool:
    try:
        return bool(parse_date(value))
    except ValueError:
        return False


def _assert_project_in_scope(request: HttpRequest, project: Project) -> None:
    """ADR 0026 Phase B: a non-Observer can't view/act on another office's
    project by guessing a URL, mirroring finance's _assert_month_in_scope."""
    scope = user_office_scope(request.user)
    if scope is not None and not scope.filter(pk=project.office_id).exists():
        raise PermissionDenied("This project belongs to another office.")


def _assert_person_in_scope(request: HttpRequest, person: Person) -> None:
    if not may_see_person(request.user, person):
        raise PermissionDenied("This person belongs to another office.")


@login_required
def project_list(request: HttpRequest) -> TemplateResponse:
    status = (request.GET.get("status") or "").strip()
    projects = Project.objects.all().prefetch_related("responsible_coordinators")
    scope = user_office_scope(request.user)
    if scope is not None:
        projects = projects.filter(office__in=scope)
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
    _assert_project_in_scope(request, project)
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
            "project": project,
            "workers": workers,
            "transport_weeks": transport_weeks,
            "transport_enabled": transport_enabled,
            "may_transport": transport_enabled
            and user_can(request.user, Action.TRANSPORT_RECORD)
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
    office_scope = user_office_scope(request.user)
    if office_scope is not None:
        trials = trials.filter(project__office__in=office_scope)
    scoped = (
        getattr(request.user, "role", None) == Role.COORDINATOR
        or office_scope is not None
    )
    if getattr(request.user, "role", None) == Role.COORDINATOR:
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
    # The read-only filter dropdown for roles that cannot schedule. Only
    # Observer lacks INTAKE_ASSIGN_TRIAL in today's policies, and Observer is
    # unrestricted anyway - but scope it regardless, so this stays correct by
    # construction rather than by coincidence of the current role matrix
    # (matching what _transport_context already does for its own dropdown).
    other_projects = Project.objects.filter(is_active=True)
    if office_scope is not None:
        other_projects = other_projects.filter(office__in=office_scope)
    return {
        "trials": trials,
        "scoped": scoped,
        "query": query,
        "project_filter": project_value,
        "date_from": date_from,
        "date_to": date_to,
        "projects": operable_projects(request.user) if may_schedule else other_projects,
        "may_schedule": may_schedule,
        "form": form,
        "editing": editing,
    }


@login_required
def trials_queue(request: HttpRequest) -> TemplateResponse:
    form = None
    editing = None
    if request.GET.get("create") == "1" and user_can(
        request.user, Action.INTAKE_ASSIGN_TRIAL
    ):
        form = TrialCreateForm(user=request.user)
    edit_value = (request.GET.get("edit") or "").strip()
    if edit_value.isdigit() and user_can(request.user, Action.INTAKE_ASSIGN_TRIAL):
        editing = get_object_or_404(
            TrialAssignment,
            pk=edit_value,
            outcome=TrialOutcome.PENDING,
            project__in=operable_projects(request.user),
        )
        form = TrialEditForm(user=request.user, trial=editing)
    return TemplateResponse(
        request,
        "pages/trials_queue.html",
        _trial_queue_context(request, form=form, editing=editing),
    )


@require_POST
@require_action(Action.INTAKE_ASSIGN_TRIAL)
def trial_create(request: HttpRequest) -> HttpResponse:
    form = TrialCreateForm(request.POST, user=request.user)
    if form.is_valid():
        try:
            schedule_trial(
                form.cleaned_data["person"],
                form.cleaned_data["project"],
                actor=request.user,
                scheduled_for=form.cleaned_data["scheduled_for"],
                note=form.cleaned_data["note"],
            )
            messages.success(request, _("Trial scheduled."))
            return redirect("trials_queue")
        except WorkflowError as exc:
            form.add_error(None, exc)
    return TemplateResponse(
        request,
        "pages/trials_queue.html",
        _trial_queue_context(request, form=form),
        status=400,
    )


@require_POST
@require_action(Action.INTAKE_ASSIGN_TRIAL)
def trial_edit(request: HttpRequest, trial_pk: int) -> HttpResponse:
    trial = get_object_or_404(
        TrialAssignment,
        pk=trial_pk,
        outcome=TrialOutcome.PENDING,
        project__in=operable_projects(request.user),
    )
    form = TrialEditForm(request.POST, user=request.user, trial=trial)
    if form.is_valid():
        try:
            update_pending_trial(
                trial,
                project=form.cleaned_data["project"],
                scheduled_for=form.cleaned_data["scheduled_for"],
                note=form.cleaned_data["note"],
                actor=request.user,
            )
            messages.success(request, _("Trial updated."))
            return redirect("trials_queue")
        except WorkflowError as exc:
            form.add_error(None, exc)
    return TemplateResponse(
        request,
        "pages/trials_queue.html",
        _trial_queue_context(request, form=form, editing=trial),
        status=400,
    )


@require_POST
@require_action(Action.INTAKE_ASSIGN_TRIAL)
def assign_trial(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    _assert_person_in_scope(request, person)
    project = get_object_or_404(Project, pk=request.POST.get("project"))
    _assert_project_in_scope(request, project)
    schedule_form = TrialCreateForm(
        {**request.POST.dict(), "person": person.pk},
        user=request.user,
    )
    try:
        if not schedule_form.is_valid():
            raise WorkflowError(_("Review the trial details and try again."))
        schedule_trial(
            person,
            project,
            actor=request.user,
            scheduled_for=schedule_form.cleaned_data["scheduled_for"],
            note=request.POST.get("note", ""),
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
    _assert_project_in_scope(request, trial.project)
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
    _assert_person_in_scope(request, person)
    project = get_object_or_404(Project, pk=request.POST.get("project"))
    _assert_project_in_scope(request, project)
    readiness = get_or_create_readiness(person, project)
    pillars = ["medical", "gear", "accommodation"]
    if getattr(settings, "FEATURE_FLAGS", {}).get("transport", True):
        pillars.append("transport")
    states = {pillar: request.POST.get(pillar) for pillar in pillars}
    na_reasons = {
        "accommodation": request.POST.get("accommodation_na_reason", ""),
        "transport": request.POST.get("transport_na_reason", ""),
    }
    try:
        update_readiness(
            readiness,
            actor=request.user,
            states=states,
            na_reasons=na_reasons,
            entry_medical_date=request.POST.get("entry_medical_date") or None,
        )
        messages.success(request, _("Readiness saved."))
    except WorkflowError as exc:
        messages.error(request, str(exc))
    return redirect("person_detail", pk=person.pk)


@require_POST
@require_action(Action.ACTIVATION_WAIVE_TRIAL)
def readiness_waive_trial(request: HttpRequest, person_pk: int) -> HttpResponse:
    """Open readiness on an Available person without a trial day (ADR 0031).

    Manager-only, and office-scoped on both sides: hiding the button is not a
    control, and a manager must not waive a worker into another office's
    project.
    """
    person = get_object_or_404(Person, pk=person_pk)
    _assert_person_in_scope(request, person)
    project = get_object_or_404(Project, pk=request.POST.get("project"))
    _assert_project_in_scope(request, project)
    try:
        waive_trial(person, project, actor=request.user)
        messages.success(
            request, _("Trial day waived — complete readiness to activate.")
        )
    except WorkflowError as exc:
        messages.error(request, str(exc))
    return redirect("person_detail", pk=person.pk)


@require_POST
@require_action(Action.READINESS_COMPLETE)
def medical_record(request: HttpRequest, person_pk: int) -> HttpResponse:
    """Record or renew the entry medical date for someone already working.

    The readiness form only exists on the way in, so before this there was no
    screen anywhere that could set this field for an activated worker - and the
    medical expires annually, so every worker eventually needed one.
    """
    person = get_object_or_404(Person, pk=person_pk)
    _assert_person_in_scope(request, person)
    assignment = person.current_assignment()
    if assignment is None:
        messages.error(
            request, _("This worker has no active assignment to record a medical for.")
        )
        return redirect("person_detail", pk=person.pk)
    _assert_project_in_scope(request, assignment.project)
    try:
        record_entry_medical(
            person,
            assignment.project,
            request.POST.get("entry_medical_date", ""),
            actor=request.user,
        )
        messages.success(request, _("Entry medical date recorded."))
    except WorkflowError as exc:
        messages.error(request, str(exc))
    return redirect("person_detail", pk=person.pk)


@require_POST
@require_action(Action.EXIT_RECONCILE)
def exit_view(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    _assert_person_in_scope(request, person)
    outcome = "inactive" if request.POST.get("outcome") == "inactive" else "available"
    reason_obj = None
    if outcome == "inactive" and request.POST.get("inactive_reason"):
        reason_obj = InactiveReason.objects.filter(
            pk=request.POST.get("inactive_reason"), is_active=True
        ).first()
    exit_person(
        person,
        actor=request.user,
        reason=request.POST.get("reason", ""),
        outcome=outcome,
        inactive_reason=reason_obj,
    )
    messages.success(request, _("Exit completed."))
    return redirect("person_detail", pk=person.pk)


@require_POST
@require_action(Action.PROJECT_ASSIGN)
def activate_person(request: HttpRequest, person_pk: int) -> HttpResponse:
    """Coordinator (or manager) *requests* activation. It no longer activates.

    Separation of duties (plan §12.4, production-readiness item 14): whoever
    completed readiness asks, and a manager of that office decides. Keeping the
    URL name means existing links and the readiness panel keep working.
    """
    person = get_object_or_404(Person, pk=person_pk)
    _assert_person_in_scope(request, person)
    project = get_object_or_404(Project, pk=request.POST.get("project"))
    _assert_project_in_scope(request, project)
    try:
        request_activation(person, project, actor=request.user)
        messages.success(request, _("Activation requested — a manager will decide."))
    except WorkflowError as exc:
        messages.error(request, str(exc))
    return redirect("person_detail", pk=person.pk)


@require_action(Action.APPROVAL_ACTIVATE)
def activation_queue(request: HttpRequest) -> TemplateResponse:
    """Manager review queue for pending activation requests, office-scoped."""
    approvals = ActivationApproval.objects.filter(
        status=ActivationApprovalStatus.PENDING
    ).select_related(
        "person", "project", "project__office", "requested_by", "readiness"
    )
    scope = user_office_scope(request.user)
    if scope is not None:
        approvals = approvals.filter(project__office__in=scope)
    return TemplateResponse(
        request, "pages/activation_queue.html", {"approvals": approvals}
    )


@require_POST
@require_action(Action.APPROVAL_ACTIVATE)
def activation_decide(request: HttpRequest, pk: int) -> HttpResponse:
    approval = get_object_or_404(
        ActivationApproval.objects.select_related("person", "project"), pk=pk
    )
    _assert_person_in_scope(request, approval.person)
    _assert_project_in_scope(request, approval.project)
    try:
        decide_activation(
            approval,
            request.POST.get("decision"),
            actor=request.user,
            reason=request.POST.get("reason", ""),
        )
        messages.success(request, _("Decision recorded."))
    except WorkflowError as exc:
        messages.error(request, str(exc))
    return redirect("activation_queue")


@require_action(Action.PROJECT_MANAGE)
def project_create(request: HttpRequest) -> HttpResponse:
    """Create a project (production-readiness item 15).

    The office picker is already narrowed to what this user may choose
    (`apply_office_scope`), so a manager cannot file a project against another
    office by selecting one - and cannot do it by posting one either, because
    the field's queryset is the validation.
    """
    form = ProjectForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        project = save_project(form.save(commit=False), actor=request.user)
        form.save_m2m()
        messages.success(request, _("Project created."))
        return redirect("project_detail", pk=project.pk)
    return TemplateResponse(
        request, "pages/project_form.html", {"form": form, "project": None}
    )


@require_action(Action.PROJECT_MANAGE)
def project_edit(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    _assert_project_in_scope(request, project)
    old = {
        field: getattr(project, field)
        for field in ("name", "partner", "code", "is_active")
    }
    form = ProjectForm(request.POST or None, instance=project, user=request.user)
    if request.method == "POST" and form.is_valid():
        save_project(form.save(commit=False), actor=request.user, old=old)
        form.save_m2m()
        messages.success(request, _("Project updated."))
        return redirect("project_detail", pk=project.pk)
    return TemplateResponse(
        request, "pages/project_form.html", {"form": form, "project": project}
    )


@require_POST
@require_action(Action.PROJECT_MANAGE)
def project_set_active(request: HttpRequest, pk: int) -> HttpResponse:
    """Deactivate or reactivate. Never delete - four models PROTECT a project,
    so a used one cannot be removed and pretending otherwise would only fail
    at the database."""
    project = get_object_or_404(Project, pk=pk)
    _assert_project_in_scope(request, project)
    active = request.POST.get("active") == "1"
    set_project_active(project, active=active, actor=request.user)
    messages.success(
        request, _("Project reactivated.") if active else _("Project deactivated.")
    )
    return redirect("project_detail", pk=project.pk)
