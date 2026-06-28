from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.accounts.permissions import Action, require_action
from apps.logistics.models import Accommodation, EquipmentIssue, EquipmentItem, Room
from apps.logistics.services import (
    CapacityError,
    assign_room,
    issue_equipment,
    record_transport_week,
    release_room,
    return_equipment,
)
from apps.people.models import Person
from apps.projects.models import Project


@login_required
def accommodation_list(request: HttpRequest) -> TemplateResponse:
    accommodations = Accommodation.objects.prefetch_related("rooms")
    return TemplateResponse(
        request, "pages/accommodation_list.html", {"accommodations": accommodations}
    )


@login_required
def accommodation_detail(request: HttpRequest, pk: int) -> TemplateResponse:
    accommodation = get_object_or_404(Accommodation, pk=pk)
    return TemplateResponse(
        request,
        "pages/accommodation_detail.html",
        {"accommodation": accommodation, "rooms": accommodation.rooms.all()},
    )


@require_POST
@require_action(Action.ROOM_ASSIGN)
def assign_room_view(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    room = get_object_or_404(Room, pk=request.POST.get("room"))
    try:
        assign_room(person, room, actor=request.user)
        messages.success(request, _("Room assigned."))
    except CapacityError as exc:
        messages.error(request, str(exc))
    return redirect("person_detail", pk=person.pk)


@require_POST
@require_action(Action.ROOM_ASSIGN)
def release_room_view(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    release_room(person, actor=request.user)
    messages.success(request, _("Room released."))
    return redirect("person_detail", pk=person.pk)


@require_POST
@require_action(Action.EQUIPMENT_ISSUE_RETURN)
def issue_equipment_view(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    item = get_object_or_404(EquipmentItem, pk=request.POST.get("item"))
    issue_equipment(person, item, request.POST.get("quantity", 1), actor=request.user)
    messages.success(request, _("Equipment issued."))
    return redirect("person_detail", pk=person.pk)


@require_POST
@require_action(Action.EQUIPMENT_ISSUE_RETURN)
def return_equipment_view(request: HttpRequest, issue_pk: int) -> HttpResponse:
    issue = get_object_or_404(EquipmentIssue, pk=issue_pk)
    return_equipment(issue, actor=request.user)
    messages.success(request, _("Equipment returned."))
    return redirect("person_detail", pk=issue.person_id)


@require_POST
@require_action(Action.TRANSPORT_RECORD)
def record_transport_view(request: HttpRequest, project_pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=project_pk)
    week_start = request.POST.get("week_start")
    if week_start:
        record_transport_week(
            project, week_start, request.POST.get("headcount", 0),
            actor=request.user, note=request.POST.get("note", ""),
        )
        messages.success(request, _("Transport week recorded."))
    else:
        messages.error(request, _("Week start is required."))
    return redirect("project_detail", pk=project.pk)
