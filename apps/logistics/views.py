from __future__ import annotations

from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.accounts.permissions import Action, require_action
from apps.accounts.permissions import can as user_can
from apps.logistics.models import (
    Accommodation,
    EquipmentIssue,
    EquipmentItem,
    Room,
    RoomAssignment,
    TransportWeek,
)
from apps.logistics.services import (
    CapacityError,
    DeductionReviewError,
    accommodation_cost_report,
    assign_room,
    flag_unreturned,
    issue_equipment,
    pending_deduction_reviews,
    record_transport_week,
    release_room,
    return_equipment,
    review_deduction,
    set_assignment_rate,
    set_room_rate,
)
from apps.people.models import Person
from apps.projects.models import Project


@login_required
def transport_trends(request: HttpRequest) -> TemplateResponse:
    """Weekly transport headcount trends per project + company total (plan §11.10).

    Rendered as dependency-free CSS bars (no JS charting library)."""
    weeks = sorted(set(TransportWeek.objects.values_list("week_start", flat=True)))[-12:]
    rows = TransportWeek.objects.filter(week_start__in=weeks).select_related("project")

    by_project: dict = defaultdict(dict)
    totals = {week: 0 for week in weeks}
    max_headcount = 1
    for row in rows:
        by_project[row.project][row.week_start] = row.headcount
        totals[row.week_start] += row.headcount
        max_headcount = max(max_headcount, row.headcount)
    max_total = max(list(totals.values()) or [1]) or 1

    def pct(value: int, ceiling: int) -> int:
        return int(value * 100 / ceiling) if ceiling else 0

    series = []
    for project, week_map in by_project.items():
        series.append({
            "project": project,
            "weeks": [
                {"week": w, "headcount": week_map.get(w, 0), "pct": pct(week_map.get(w, 0), max_headcount)}
                for w in weeks
            ],
        })
    company = [{"week": w, "total": totals[w], "pct": pct(totals[w], max_total)} for w in weeks]
    return TemplateResponse(
        request, "pages/transport_trends.html", {"series": series, "company": company},
    )


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
        {
            "accommodation": accommodation,
            "rooms": accommodation.rooms.all(),
            "can_manage": user_can(request.user, Action.ACCOMMODATION_MANAGE),
        },
    )


@require_action(Action.ACCOMMODATION_MANAGE)
def accommodation_costs(request: HttpRequest) -> TemplateResponse:
    """Occupancy + monthly-cost report per accommodation (reporting only, Q1)."""
    return TemplateResponse(
        request, "pages/accommodation_costs.html", accommodation_cost_report()
    )


@require_POST
@require_action(Action.ACCOMMODATION_MANAGE)
def set_room_rate_view(request: HttpRequest, pk: int) -> HttpResponse:
    room = get_object_or_404(Room, pk=pk)
    set_room_rate(room, request.POST.get("monthly_rate") or 0, actor=request.user)
    messages.success(request, _("Room rate saved."))
    return redirect("accommodation_detail", pk=room.accommodation_id)


@require_POST
@require_action(Action.ACCOMMODATION_MANAGE)
def set_assignment_rate_view(request: HttpRequest, pk: int) -> HttpResponse:
    assignment = get_object_or_404(RoomAssignment, pk=pk)
    set_assignment_rate(assignment, request.POST.get("rate_override"), actor=request.user)
    messages.success(request, _("Rate override saved."))
    return redirect("person_detail", pk=assignment.person_id)


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
@require_action(Action.EQUIPMENT_ISSUE_RETURN)
def flag_unreturned_view(request: HttpRequest, issue_pk: int) -> HttpResponse:
    issue = get_object_or_404(EquipmentIssue, pk=issue_pk)
    try:
        flag_unreturned(issue, actor=request.user)
        messages.success(request, _("Flagged for deduction review."))
    except DeductionReviewError as exc:
        messages.error(request, str(exc))
    return redirect("person_detail", pk=issue.person_id)


@require_action(Action.EQUIPMENT_REVIEW_DEDUCTION)
def equipment_reviews(request: HttpRequest) -> TemplateResponse:
    """Manager queue of unreturned items awaiting an approve/waive decision (Q2)."""
    return TemplateResponse(
        request, "pages/equipment_reviews.html", pending_deduction_reviews()
    )


@require_POST
@require_action(Action.EQUIPMENT_REVIEW_DEDUCTION)
def review_deduction_view(request: HttpRequest, issue_pk: int) -> HttpResponse:
    issue = get_object_or_404(EquipmentIssue, pk=issue_pk)
    try:
        review_deduction(
            issue, request.POST.get("decision"),
            actor=request.user, note=request.POST.get("note", ""),
        )
        messages.success(request, _("Review recorded."))
    except DeductionReviewError as exc:
        messages.error(request, str(exc))
    return redirect("equipment_reviews")


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
