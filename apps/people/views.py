from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

from apps.accounts.permissions import Action, require_action
from apps.audit.services import record_event
from apps.people.forms import PersonForm
from apps.people.models import LifecycleStatus, Person
from apps.people.permissions import can_view_sensitive
from apps.logistics.models import (
    EquipmentItem,
    EquipmentIssueStatus,
    Room,
    RoomAssignmentStatus,
)
from apps.projects.models import PillarState, Project, TrialOutcome
from apps.projects.services import get_or_create_readiness


@login_required
def people_list(request: HttpRequest) -> TemplateResponse:
    # Broad internal read: any authenticated role may see the operational list.
    query = (request.GET.get("q") or "").strip()
    people = Person.objects.filter(is_archived=False)
    if query:
        people = people.filter(search_name__contains=query.lower())
    return TemplateResponse(
        request,
        "pages/people_list.html",
        {"people": people, "query": query},
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
            return redirect("person_detail", pk=person.pk)
    else:
        form = PersonForm()
    return TemplateResponse(request, "pages/person_form.html", {"form": form})


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
            "pending_trial": pending_trial,
            "passed_trial": passed_trial,
            "in_readiness": in_readiness,
            "readiness": readiness,
            "is_ready": readiness.is_ready() if readiness else False,
            "PillarState": PillarState,
            "is_available": person.lifecycle_status == LifecycleStatus.AVAILABLE,
            "active_projects": Project.objects.filter(is_active=True),
            "current_room": person.room_assignments.filter(
                status=RoomAssignmentStatus.ACTIVE
            ).select_related("room__accommodation").first(),
            "rooms": Room.objects.select_related("accommodation").filter(
                accommodation__is_active=True
            ),
            "issued_equipment": person.equipment_issues.filter(
                status=EquipmentIssueStatus.ISSUED
            ).select_related("item"),
            "equipment_items": EquipmentItem.objects.filter(is_active=True),
        },
    )
