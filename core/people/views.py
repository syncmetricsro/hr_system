from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.accounts.permissions import Action, require_action
from core.audit.services import record_event
from core.people.forms import PersonForm
from core.accounts.permissions import can as user_can
from core.people.models import InactiveReason, LifecycleError, LifecycleStatus, Person
from core.people.permissions import can_view_sensitive
from core.people.services import person_history, recycle_to_available
from core.ui import registry
from core.projects.models import PillarState, Project, TrialOutcome
from core.projects.services import get_or_create_readiness, readiness_blockers


@login_required
def people_list(request: HttpRequest) -> TemplateResponse:
    # Broad internal read: any authenticated role may see the operational list.
    query = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "").strip()
    inactive_reason = (request.GET.get("inactive_reason") or "").strip()
    inactive_reasons = InactiveReason.objects.all()
    people = Person.objects.filter(is_archived=False)
    if query:
        people = people.filter(search_name__contains=query.lower())
    if status in LifecycleStatus.values:
        people = people.filter(lifecycle_status=status)
    else:
        status = ""
    if status == LifecycleStatus.INACTIVE:
        if inactive_reason == "none":
            people = people.filter(inactive_reason__isnull=True)
        elif inactive_reason.isdecimal() and inactive_reasons.filter(
            pk=int(inactive_reason)
        ).exists():
            people = people.filter(inactive_reason_id=int(inactive_reason))
        else:
            inactive_reason = ""
    else:
        inactive_reason = ""
    return TemplateResponse(
        request,
        "pages/people_list.html",
        {
            "people": people,
            "query": query,
            "status": status,
            "statuses": LifecycleStatus.choices,
            "inactive_reason": inactive_reason,
            "inactive_reasons": inactive_reasons,
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
    readiness_issues = []
    if in_readiness:
        readiness = get_or_create_readiness(person, passed_trial.project)
        readiness_issues = readiness_blockers(readiness)
        if readiness.entry_medical_date and readiness.entry_medical_date > timezone.localdate():
            readiness_issues.append({"field": "entry_medical_date", "label": _("Entry medical date"), "message": _("Review this future date.")})
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
            "readiness_issues": readiness_issues,
            "readiness_future_medical_date": bool(
                readiness and readiness.entry_medical_date and readiness.entry_medical_date > timezone.localdate()
            ),
            "is_ready": readiness.is_ready() if readiness else False,
            "PillarState": PillarState,
            "is_available": person.lifecycle_status == LifecycleStatus.AVAILABLE,
            "active_projects": Project.objects.filter(is_active=True),
            "person_banners": registry.person_banners(request, person),
            "person_panels": registry.person_panels(request, person),
            "person_finance_overview": registry.person_finance_overview(
                request, person
            ),
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
            "can_archive": (
                not person.is_archived
                and user_can(request.user, Action.PERSON_ARCHIVE)
            ),
        },
    )


@require_POST
@require_action(Action.PERSON_ARCHIVE)
def archive_person(request: HttpRequest, person_pk: int) -> HttpResponse:
    """Operational archive, not data erasure.

    A linked blacklist case/fingerprint intentionally remains so an archived
    person cannot be reintroduced without the protected re-entry check.
    Retention and lawful erasure are separate controlled processes.
    """
    person = get_object_or_404(Person, pk=person_pk)
    person.archive(actor=request.user, reason=request.POST.get("reason", ""))
    messages.success(request, _("Person archived. Blacklist protection remains in place."))
    return redirect("people_list")


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
