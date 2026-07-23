from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from core.accounts.permissions import Action, require_action
from core.accounts.permissions import can as user_can
from features.logistics.forms import (
    AccommodationCostPeriodForm, AccommodationForm, EquipmentItemForm, RoomForm, StockAdjustmentForm,
    StockReceiptForm, StockReceiptLineFormSet, TransportWeekForm,
    transport_projects,
)
from features.logistics.models import (
    Accommodation,
    EquipmentIssue,
    EquipmentItem,
    Room,
    RoomAssignment,
    TransportWeek,
)
from features.logistics.services import (
    CapacityError,
    DeductionReviewError,
    LogisticsWorkflowError,
    adjust_stock,
    accommodation_month_report,
    assign_room,
    create_transport_week,
    equipment_month_report,
    equipment_stock_balance,
    flag_unreturned,
    issue_equipment,
    pending_deduction_reviews,
    record_transport_week,
    receive_stock,
    release_room,
    return_equipment,
    review_deduction,
    save_equipment_item,
    set_assignment_rate,
    set_room_rate,
    save_accommodation,
    save_room,
    set_accommodation_cost_period,
    set_assignment_payment,
    stock_ledger_enabled,
    update_transport_week,
)
from core.people.models import Person
from core.projects.models import Project


def _valid_date(value: str) -> bool:
    try:
        return bool(parse_date(value))
    except ValueError:
        return False


@login_required
def _transport_context(request, *, form=None, editing=None):
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
    records = TransportWeek.objects.select_related("project")
    project_filter = (request.GET.get("project") or "").strip()
    week_from = (request.GET.get("week_from") or "").strip()
    week_to = (request.GET.get("week_to") or "").strip()
    if project_filter.isdigit():
        records = records.filter(project_id=project_filter)
    else:
        project_filter = ""
    if week_from and _valid_date(week_from):
        records = records.filter(week_start__gte=week_from)
    else:
        week_from = ""
    if week_to and _valid_date(week_to):
        records = records.filter(week_start__lte=week_to)
    else:
        week_to = ""
    may_record = user_can(request.user, Action.TRANSPORT_RECORD)
    return {
        "series": series, "company": company, "records": records[:100],
        "projects": transport_projects(request.user) if may_record else Project.objects.filter(is_active=True),
        "project_filter": project_filter, "week_from": week_from, "week_to": week_to,
        "may_record": may_record, "form": form, "editing": editing,
    }


@login_required
def transport_trends(request: HttpRequest) -> TemplateResponse:
    form = None
    editing = None
    if request.GET.get("create") == "1" and user_can(request.user, Action.TRANSPORT_RECORD):
        form = TransportWeekForm(user=request.user)
    edit_value = (request.GET.get("edit") or "").strip()
    if edit_value.isdigit() and user_can(request.user, Action.TRANSPORT_RECORD):
        editing = get_object_or_404(
            TransportWeek, pk=edit_value, project__in=transport_projects(request.user)
        )
        form = TransportWeekForm(user=request.user, instance=editing)
    return TemplateResponse(
        request, "pages/transport_trends.html",
        _transport_context(request, form=form, editing=editing),
    )


@login_required
def accommodation_list(request: HttpRequest) -> TemplateResponse:
    accommodations = Accommodation.objects.prefetch_related("rooms")
    query = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "active").strip()
    if query:
        accommodations = accommodations.filter(Q(name__icontains=query) | Q(address__icontains=query))
    if status == "active":
        accommodations = accommodations.filter(is_active=True)
    elif status == "inactive":
        accommodations = accommodations.filter(is_active=False)
    else:
        status = "all"
    return TemplateResponse(
        request, "pages/accommodation_list.html", {
            "accommodations": accommodations, "query": query, "status_filter": status,
            "can_manage": user_can(request.user, Action.ACCOMMODATION_MANAGE),
        }
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
            "cost_periods": accommodation.cost_periods.all(),
            "cost_form": AccommodationCostPeriodForm(initial={"effective_month": timezone.localdate().replace(day=1)}),
            "can_manage": user_can(request.user, Action.ACCOMMODATION_MANAGE),
        },
    )


def _model_values(instance, fields):
    values = {}
    for field in fields:
        value = getattr(instance, field)
        values[field] = value if value is None or isinstance(value, (str, int, float, bool)) else str(value)
    return values


@require_action(Action.ACCOMMODATION_MANAGE)
def accommodation_create(request: HttpRequest) -> HttpResponse:
    form = AccommodationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        accommodation = form.save(commit=False)
        save_accommodation(accommodation, actor=request.user)
        capacity = form.cleaned_data.get("capacity")
        per_head_cost = form.cleaned_data.get("per_head_cost")
        if capacity is not None and per_head_cost is not None:
            set_accommodation_cost_period(
                accommodation, effective_month=timezone.localdate(),
                capacity=capacity, per_head_cost=per_head_cost, actor=request.user,
            )
        messages.success(request, _("Accommodation created. Add rooms to make it assignable."))
        return redirect("accommodation_detail", pk=accommodation.pk)
    return TemplateResponse(request, "pages/accommodation_form.html", {"form": form})


@require_action(Action.ACCOMMODATION_MANAGE)
def accommodation_edit(request: HttpRequest, pk: int) -> HttpResponse:
    accommodation = get_object_or_404(Accommodation, pk=pk)
    old = _model_values(accommodation, ("name", "address", "notes", "is_active"))
    form = AccommodationForm(request.POST or None, instance=accommodation)
    if request.method == "POST" and form.is_valid():
        save_accommodation(form.save(commit=False), actor=request.user, old=old)
        messages.success(request, _("Accommodation updated."))
        return redirect("accommodation_detail", pk=accommodation.pk)
    return TemplateResponse(
        request, "pages/accommodation_form.html",
        {"form": form, "accommodation": accommodation},
    )


@require_action(Action.ACCOMMODATION_MANAGE)
def room_create(request: HttpRequest, accommodation_pk: int) -> HttpResponse:
    accommodation = get_object_or_404(Accommodation, pk=accommodation_pk)
    form = RoomForm(request.POST or None)
    form.instance.accommodation = accommodation
    if request.method == "POST" and form.is_valid():
        room = form.save(commit=False)
        room.accommodation = accommodation
        save_room(room, actor=request.user)
        messages.success(request, _("Room created."))
        return redirect("accommodation_detail", pk=accommodation.pk)
    return TemplateResponse(
        request, "pages/room_form.html", {"form": form, "accommodation": accommodation},
    )


@require_action(Action.ACCOMMODATION_MANAGE)
def room_edit(request: HttpRequest, pk: int) -> HttpResponse:
    room = get_object_or_404(Room.objects.select_related("accommodation"), pk=pk)
    old = _model_values(room, ("label", "capacity", "monthly_rate", "is_active"))
    form = RoomForm(request.POST or None, instance=room)
    if request.method == "POST" and form.is_valid():
        save_room(form.save(commit=False), actor=request.user, old=old)
        messages.success(request, _("Room updated."))
        return redirect("accommodation_detail", pk=room.accommodation_id)
    return TemplateResponse(
        request, "pages/room_form.html",
        {"form": form, "accommodation": room.accommodation, "room": room},
    )


@require_action(Action.ACCOMMODATION_MANAGE)
def accommodation_costs(request: HttpRequest) -> TemplateResponse:
    """Prorated monthly per-head report; reporting only, never payroll."""
    today = timezone.localdate()
    month_value = (request.GET.get("month") or f"{today:%Y-%m}").strip()
    try:
        year, month = (int(part) for part in month_value.split("-", 1))
        if month not in range(1, 13):
            raise ValueError
    except (TypeError, ValueError):
        year, month = today.year, today.month
        month_value = f"{year:04d}-{month:02d}"
    context = accommodation_month_report(year, month)
    context["month_value"] = month_value
    return TemplateResponse(
        request, "pages/accommodation_costs.html", context
    )


@require_POST
@require_action(Action.ACCOMMODATION_MANAGE)
def accommodation_cost_period(request: HttpRequest, accommodation_pk: int) -> HttpResponse:
    accommodation = get_object_or_404(Accommodation, pk=accommodation_pk)
    form = AccommodationCostPeriodForm(request.POST)
    if form.is_valid():
        set_accommodation_cost_period(
            accommodation, effective_month=form.cleaned_data["effective_month"],
            capacity=form.cleaned_data["capacity"], per_head_cost=form.cleaned_data["per_head_cost"],
            actor=request.user,
        )
        messages.success(request, _("Accommodation cost period saved."))
    else:
        messages.error(request, _("Review the accommodation cost details."))
    return redirect("accommodation_detail", pk=accommodation.pk)


@require_POST
@require_action(Action.ACCOMMODATION_MANAGE)
def set_room_rate_view(request: HttpRequest, pk: int) -> HttpResponse:
    room = get_object_or_404(Room, pk=pk)
    try:
        set_room_rate(room, request.POST.get("monthly_rate") or 0, actor=request.user)
        messages.success(request, _("Room rate saved."))
    except (ValueError, ArithmeticError) as exc:
        messages.error(request, str(exc) or _("Invalid amount."))
    return redirect("accommodation_detail", pk=room.accommodation_id)


@require_POST
@require_action(Action.ACCOMMODATION_MANAGE)
def set_assignment_rate_view(request: HttpRequest, pk: int) -> HttpResponse:
    assignment = get_object_or_404(RoomAssignment, pk=pk)
    try:
        set_assignment_rate(assignment, request.POST.get("rate_override"), actor=request.user)
        messages.success(request, _("Rate override saved."))
    except (ValueError, ArithmeticError) as exc:
        messages.error(request, str(exc) or _("Invalid amount."))
    return redirect("person_detail", pk=assignment.person_id)


@require_POST
@require_action(Action.ACCOMMODATION_MANAGE)
def set_assignment_payment_view(request: HttpRequest, pk: int) -> HttpResponse:
    assignment = get_object_or_404(RoomAssignment, pk=pk)
    try:
        set_assignment_payment(assignment, request.POST.get("worker_payment_monthly") or 0, actor=request.user)
        messages.success(request, _("Worker accommodation payment saved."))
    except (ValueError, ArithmeticError) as exc:
        messages.error(request, str(exc) or _("Invalid amount."))
    return redirect("person_detail", pk=assignment.person_id)


@require_POST
@require_action(Action.ROOM_ASSIGN)
def assign_room_view(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    room = get_object_or_404(Room, pk=request.POST.get("room"))
    try:
        assign_room(
            person, room, actor=request.user,
            worker_payment_monthly=request.POST.get("worker_payment_monthly") or 0,
        )
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


@require_action(Action.CATALOG_MANAGE)
def equipment_catalog(request: HttpRequest) -> TemplateResponse:
    """Manager-only master-data page; inactive entries remain visible for history."""
    items = EquipmentItem.objects.all()
    query = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "active").strip()
    if query:
        items = items.filter(Q(name__icontains=query) | Q(size__icontains=query))
    if status == "active":
        items = items.filter(is_active=True)
    elif status == "inactive":
        items = items.filter(is_active=False)
    else:
        status = "all"
    return TemplateResponse(
        request,
        "pages/equipment_catalog.html",
        {
            "items": items, "query": query, "status_filter": status,
            "stock_enabled": stock_ledger_enabled(),
        },
    )


@require_action(Action.EQUIPMENT_VIEW_STOCK)
def equipment_stock(request: HttpRequest) -> TemplateResponse:
    today = timezone.localdate()
    month_value = (request.GET.get("month") or f"{today:%Y-%m}").strip()
    try:
        year, month = (int(part) for part in month_value.split("-", 1))
        if month < 1 or month > 12:
            raise ValueError
    except (TypeError, ValueError):
        year, month = today.year, today.month
        month_value = f"{year:04d}-{month:02d}"
    return TemplateResponse(
        request,
        "pages/equipment_stock.html",
        {
            "balance": equipment_stock_balance(),
            "report": equipment_month_report(year, month),
            "month_value": month_value,
            "can_manage": user_can(request.user, Action.EQUIPMENT_MANAGE_STOCK),
        },
    )


@require_action(Action.EQUIPMENT_MANAGE_STOCK)
def equipment_stock_receive(request: HttpRequest) -> HttpResponse:
    form = StockReceiptForm(request.POST or None, initial={"received_on": timezone.localdate()})
    lines = StockReceiptLineFormSet(request.POST or None, prefix="lines")
    if request.method == "POST" and form.is_valid() and lines.is_valid():
        prepared = [
            row for row in (line.cleaned_data for line in lines)
            if row.get("item") is not None
        ]
        try:
            receive_stock(
                received_on=form.cleaned_data["received_on"], lines=prepared,
                operation_key=form.cleaned_data["operation_key"],
                supplier=form.cleaned_data["supplier"], reference=form.cleaned_data["reference"],
                note=form.cleaned_data["note"], actor=request.user,
            )
            messages.success(request, _("Stock receipt recorded."))
            return redirect("equipment_stock")
        except LogisticsWorkflowError as exc:
            form.add_error(None, exc)
    return TemplateResponse(
        request, "pages/equipment_stock_receive.html", {"form": form, "lines": lines},
        status=400 if request.method == "POST" else 200,
    )


@require_POST
@require_action(Action.EQUIPMENT_MANAGE_STOCK)
def equipment_stock_adjust(request: HttpRequest) -> HttpResponse:
    form = StockAdjustmentForm(request.POST)
    if form.is_valid():
        try:
            adjust_stock(
                form.cleaned_data["item"], form.cleaned_data["quantity_delta"],
                occurred_on=form.cleaned_data["occurred_on"], value=form.cleaned_data["value"],
                reason=form.cleaned_data["reason"], actor=request.user,
            )
            messages.success(request, _("Stock adjustment recorded."))
        except LogisticsWorkflowError as exc:
            messages.error(request, str(exc))
    else:
        messages.error(request, _("Review the stock adjustment and try again."))
    return redirect("equipment_stock")


@require_action(Action.CATALOG_MANAGE)
def equipment_create(request: HttpRequest) -> HttpResponse:
    form = EquipmentItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        save_equipment_item(form.save(commit=False), actor=request.user)
        messages.success(request, _("Equipment item created."))
        return redirect("equipment_catalog")
    return TemplateResponse(request, "pages/equipment_form.html", {"form": form})


@require_action(Action.CATALOG_MANAGE)
def equipment_edit(request: HttpRequest, pk: int) -> HttpResponse:
    item = get_object_or_404(EquipmentItem, pk=pk)
    old = {
        "name": item.name,
        "size": item.size,
        "unit_price": str(item.unit_price),
        "is_active": item.is_active,
    }
    form = EquipmentItemForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        save_equipment_item(form.save(commit=False), actor=request.user, old=old)
        messages.success(request, _("Equipment item updated."))
        return redirect("equipment_catalog")
    return TemplateResponse(
        request, "pages/equipment_form.html", {"form": form, "item": item}
    )


@require_POST
@require_action(Action.EQUIPMENT_ISSUE_RETURN)
def issue_equipment_view(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    item = get_object_or_404(EquipmentItem, pk=request.POST.get("item"), is_active=True)
    try:
        operation_key = UUID(request.POST["operation_key"]) if request.POST.get("operation_key") else None
        issue_equipment(
            person, item, request.POST.get("quantity", 1), actor=request.user,
            operation_key=operation_key,
        )
        messages.success(request, _("Equipment issued."))
    except (LogisticsWorkflowError, ValueError) as exc:
        messages.error(request, str(exc) or _("Invalid equipment issue."))
    return redirect("person_detail", pk=person.pk)


@require_POST
@require_action(Action.EQUIPMENT_ISSUE_RETURN)
def return_equipment_view(request: HttpRequest, issue_pk: int) -> HttpResponse:
    issue = get_object_or_404(EquipmentIssue, pk=issue_pk)
    try:
        return_equipment(issue, actor=request.user, disposition=request.POST.get("disposition"))
        messages.success(request, _("Equipment returned."))
    except LogisticsWorkflowError as exc:
        messages.error(request, str(exc))
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
    project = get_object_or_404(transport_projects(request.user), pk=project_pk)
    form = TransportWeekForm({**request.POST.dict(), "project": project.pk}, user=request.user)
    if form.is_valid():
        record_transport_week(
            project, form.cleaned_data["week_start"], form.cleaned_data["headcount"],
            actor=request.user, note=form.cleaned_data["note"],
        )
        messages.success(request, _("Transport week recorded."))
    else:
        messages.error(request, _("Review the transport details and try again."))
    return redirect("project_detail", pk=project.pk)


@require_POST
@require_action(Action.TRANSPORT_RECORD)
def transport_create(request: HttpRequest) -> HttpResponse:
    form = TransportWeekForm(request.POST, user=request.user)
    if form.is_valid():
        try:
            create_transport_week(
                project=form.cleaned_data["project"], week_start=form.cleaned_data["week_start"],
                headcount=form.cleaned_data["headcount"], note=form.cleaned_data["note"], actor=request.user,
            )
            messages.success(request, _("Transport week recorded."))
            return redirect("transport_trends")
        except LogisticsWorkflowError as exc:
            form.add_error(None, exc)
    return TemplateResponse(
        request, "pages/transport_trends.html", _transport_context(request, form=form), status=400,
    )


@require_POST
@require_action(Action.TRANSPORT_RECORD)
def transport_edit(request: HttpRequest, pk: int) -> HttpResponse:
    week = get_object_or_404(TransportWeek, pk=pk, project__in=transport_projects(request.user))
    form = TransportWeekForm(request.POST, user=request.user, instance=week)
    if form.is_valid():
        try:
            # ModelForm validation assigns cleaned values to its instance; reload
            # so the service can audit the persisted old values accurately.
            week.refresh_from_db()
            update_transport_week(
                week, project=form.cleaned_data["project"], week_start=form.cleaned_data["week_start"],
                headcount=form.cleaned_data["headcount"], note=form.cleaned_data["note"], actor=request.user,
            )
            messages.success(request, _("Transport record updated."))
            return redirect("transport_trends")
        except LogisticsWorkflowError as exc:
            form.add_error(None, exc)
    return TemplateResponse(
        request, "pages/transport_trends.html",
        _transport_context(request, form=form, editing=week), status=400,
    )
