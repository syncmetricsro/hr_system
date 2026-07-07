from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.accounts.permissions import Action, require_action
from apps.audit.services import record_event
from apps.people.forms import PersonForm
from apps.accounts.permissions import can as user_can
from apps.people.models import InactiveReason, LifecycleError, LifecycleStatus, Person
from apps.people.permissions import can_view_sensitive
from apps.people.services import person_history, recycle_to_available
from apps.core import registry
from apps.projects.models import PillarState, Project, TrialOutcome
from apps.projects.services import get_or_create_readiness


@login_required
def people_list(request: HttpRequest) -> TemplateResponse:
    # Broad internal read: any authenticated role may see the operational list.
    query = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "").strip()
    people = Person.objects.filter(is_archived=False)
    if query:
        people = people.filter(search_name__contains=query.lower())
    if status in LifecycleStatus.values:
        people = people.filter(lifecycle_status=status)
    return TemplateResponse(
        request,
        "pages/people_list.html",
        {
            "people": people,
            "query": query,
            "status": status,
            "statuses": LifecycleStatus.choices,
        },
    )


@require_action(Action.INTAKE_CREATE_EDIT)
def person_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PersonForm(request.POST)
        if form.is_valid():
            person = form.save(commit=False)
            person.owning_recruiter = request.user
            person.save()
            record_event(request.user, "person.created", target=person)
            messages.success(request, _("Person added."))
            # Feature form-extensions run post-create (e.g. the blacklist
            # re-entry check, plan §12.13) — registered via the core registry.
            for extension in registry.person_form_extensions:
                extension.post_create(request, person, form.cleaned_data)
            return redirect("person_detail", pk=person.pk)
    else:
        form = PersonForm()
    return TemplateResponse(
        request, "pages/person_form.html",
        {"form": form, "form_action": reverse("person_create"), "heading": _("Add person")},
    )


@require_action(Action.INTAKE_CREATE_EDIT)
def person_edit(request: HttpRequest, pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=pk)
    if request.method == "POST":
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            record_event(request.user, "person.updated", target=person)
            messages.success(request, _("Person updated."))
            return redirect("person_detail", pk=person.pk)
    else:
        form = PersonForm(instance=person)
    return TemplateResponse(
        request, "pages/person_form.html",
        {"form": form, "form_action": reverse("person_edit", args=[person.pk]), "heading": _("Edit person")},
    )


@login_required
def person_detail(request: HttpRequest, pk: int) -> TemplateResponse:
    person = get_object_or_404(Person, pk=pk)
    assignment = person.current_assignment()
    pending_trial = person.trials.filter(outcome=TrialOutcome.PENDING).select_related("project").first()
    # A passed trial with no pending trial means the person is in the readiness step.
    passed_trial = (
        person.trials.filter(outcome=TrialOutcome.PASS).order_by("-created_at").first()
    )
    in_readiness = (
        person.lifecycle_status == LifecycleStatus.TRIAL_DAY
        and pending_trial is None
        and passed_trial is not None
    )
    readiness = None
    if in_readiness:
        readiness = get_or_create_readiness(person, passed_trial.project)
    return TemplateResponse(
        request,
        "pages/person_detail.html",
        {
            "person": person,
            "assignment": assignment,
            "show_sensitive": can_view_sensitive(request.user, person),
            "history": person_history(person),
            "pending_trial": pending_trial,
            "passed_trial": passed_trial,
            "in_readiness": in_readiness,
            "readiness": readiness,
            "is_ready": readiness.is_ready() if readiness else False,
            "PillarState": PillarState,
            "is_available": person.lifecycle_status == LifecycleStatus.AVAILABLE,
            "active_projects": Project.objects.filter(is_active=True),
            "person_banners": registry.person_banners(request, person),
            "person_panels": registry.person_panels(request, person),
            "can_exit": user_can(request.user, Action.EXIT_RECONCILE) and (
                person.lifecycle_status == LifecycleStatus.WORKING
                or registry.exit_relevant(person)
            ),
            "inactive_reasons": InactiveReason.objects.filter(is_active=True),
            "is_inactive": person.lifecycle_status == LifecycleStatus.INACTIVE,
            "can_recycle": (
                person.lifecycle_status == LifecycleStatus.INACTIVE
                and user_can(request.user, Action.PERSON_RECYCLE_AVAILABLE)
            ),
        },
    )


@require_POST
@require_action(Action.PERSON_RECYCLE_AVAILABLE)
def recycle_person(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    try:
        recycle_to_available(person, actor=request.user, reason=request.POST.get("reason", ""))
        messages.success(request, _("Recycled to Available."))
    except LifecycleError as exc:
        messages.error(request, str(exc))
    return redirect("person_detail", pk=person.pk)
