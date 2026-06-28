from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.accounts.permissions import Action, require_action
from apps.logistics.models import Accommodation, Room
from apps.logistics.services import CapacityError, assign_room, release_room
from apps.people.models import Person


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
