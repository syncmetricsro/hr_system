from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from core.accounts.models import Role
from core.accounts.permissions import Action, require_action, user_office_scope
from core.accounts.permissions import can as user_can
from core.projects.models import Project
from core.ui.chart_data import net_bar_payload
from features.profitability.models import (
    FinanceCategory,
    FinanceCategoryKind,
    FinancialMonth,
)
from features.profitability.services import (
    FinanceError,
    cell_field_name,
    company_totals,
    group_breakdown,
    lock_month,
    margin_pct,
    monthly_totals,
    normalize_source_amount,
    office_monthly_totals,
    office_totals,
    project_totals,
    project_year_grid,
    recompute_month,
    save_project_year,
    record_financial_month,
    reopen_month,
    set_line_item,
    signed_amount,
    workbook_grid,
    workbook_year_grid,
    yearly_totals,
)


def _trend_chart_data(rows: list[dict]) -> dict:
    return {
        "labels": [f"{r['year']}-{r['month']:02d}" for r in rows],
        "revenue": [r["revenue"] for r in rows],
        "cost": [-r["cost"] for r in rows],
        "net": [r["net"] for r in rows],
        "locked": [r["all_locked"] for r in rows],
    }


def _office_trend_chart_data(rows: list[dict]) -> dict:
    """Reshape office_monthly_totals()'s flat (year, month, office) rows into
    one labeled series per office, for the multi-series executive chart."""
    labels = sorted({f"{r['year']}-{r['month']:02d}" for r in rows})
    by_office: dict[str, dict[str, float]] = {}
    for row in rows:
        label = f"{row['year']}-{row['month']:02d}"
        by_office.setdefault(row["office"], {})[label] = row["net"]
    series = [
        {
            "label": office,
            "data": [float(points.get(label, 0)) for label in labels],
        }
        for office, points in sorted(by_office.items())
    ]
    return {"labels": labels, "series": series}


def _latest_period(months) -> dict:
    """Newest recorded (year, month) in scope, falling back to today."""
    newest = months.order_by("-year", "-month").values("year", "month").first()
    if newest:
        return {"workbook_year": newest["year"], "workbook_month": newest["month"]}
    today = timezone.localdate()
    return {"workbook_year": today.year, "workbook_month": today.month}


def _assert_month_in_scope(request: HttpRequest, month: FinancialMonth) -> None:
    """ADR 0026 Phase A: a non-Observer can't act on another office's month,
    even by guessing/POSTing a PK directly — the office-scope check must be
    enforced here too, not just hidden from the UI."""
    scope = user_office_scope(request.user)
    if scope is None:
        return
    if not scope.filter(pk=month.project.office_id).exists():
        raise PermissionDenied("This financial month belongs to another office.")


def _scoped_finance_projects(scope):
    """Active finance columns visible inside an already-resolved office scope."""
    projects = Project.objects.filter(
        is_active=True, financial_reporting_eligible=True
    ).select_related("office")
    if scope is not None:
        projects = projects.filter(office__in=scope)
    return projects.order_by("office__name", "name")


@require_action(Action.FINANCE_VIEW_SUMMARY)
def finance_summary(request: HttpRequest) -> HttpResponse:
    if request.user.role == Role.OBSERVER:
        totals = company_totals()
        margin = margin_pct(totals)
        offices = office_totals()
        return TemplateResponse(
            request,
            "pages/finance_executive.html",
            {
                "totals": totals,
                "margin_pct": margin,
                "office_results": offices,
                "years": yearly_totals(),
                "gauge_chart_data": {**totals, "margin_pct": margin},
                "office_chart_data": net_bar_payload(offices, label_key="office"),
                "office_trend_chart_data": _office_trend_chart_data(
                    office_monthly_totals()
                ),
            },
        )

    scope = user_office_scope(request.user)
    months = FinancialMonth.objects.select_related("project")
    # `scope` is None for an unrestricted caller *and* on a tenant with no
    # Office rows at all - which is exactly the empty instance handed to a
    # client for their trial. `office__in=None` raises, so this must guard.
    if scope is not None:
        months = months.filter(project__office__in=scope)
    totals = company_totals(offices=scope)
    groups = group_breakdown(offices=scope)
    margin = margin_pct(totals)
    offices = office_totals(offices=scope)
    scoped_projects = _scoped_finance_projects(scope)
    return TemplateResponse(
        request,
        "pages/finance_summary.html",
        {
            "months": months.filter(project__financial_reporting_eligible=True),
            "totals": totals,
            "margin_pct": margin,
            "groups": groups,
            "project_results": project_totals(offices=scope),
            "regional_results": offices,
            "years": yearly_totals(offices=scope),
            "projects": scoped_projects,
            "trend_chart_data": _trend_chart_data(monthly_totals(offices=scope)),
            "gauge_chart_data": {**totals, "margin_pct": margin},
            "group_chart_data": net_bar_payload(groups),
            "regional_chart_data": net_bar_payload(offices, label_key="office"),
            # The workbook link needs a period. Use the newest month that has
            # data in scope rather than today: an empty grid for the current
            # month is a worse first impression than the last real one.
            **_latest_period(months),
        },
    )


@require_action(Action.FINANCE_VIEW_SUMMARY)
def finance_year(request: HttpRequest, year: int) -> HttpResponse:
    scope = user_office_scope(request.user)
    months = FinancialMonth.objects.select_related("project").filter(
        year=year, project__financial_reporting_eligible=True
    )
    if scope is not None:
        months = months.filter(project__office__in=scope)
    project_results = project_totals(year, offices=scope)
    return TemplateResponse(
        request,
        "pages/finance_year.html",
        {
            "year": year,
            "months": months,
            "totals": company_totals(year, offices=scope),
            "groups": group_breakdown(list(months), offices=scope),
            "project_results": project_results,
            "regional_results": office_totals(year, offices=scope),
            "trend_chart_data": _trend_chart_data(monthly_totals(year, offices=scope)),
            "project_chart_data": net_bar_payload(project_results, label_key="name"),
            "projects": _scoped_finance_projects(scope),
        },
    )


@require_action(Action.FINANCE_VIEW_SUMMARY)
def finance_month_detail(request: HttpRequest, pk: int) -> HttpResponse:
    month = get_object_or_404(FinancialMonth.objects.select_related("project"), pk=pk)
    _assert_month_in_scope(request, month)
    categories = FinanceCategory.objects.filter(is_active=True)
    amounts = {
        li.category_id: signed_amount(li.category.kind, li.amount)
        for li in month.line_items.select_related("category")
    }
    rows = [{"category": c, "amount": amounts.get(c.id, "")} for c in categories]
    can_manage = user_can(request.user, Action.FINANCE_MANAGE)
    groups = group_breakdown([month])
    return TemplateResponse(
        request,
        "pages/finance_month_detail.html",
        {
            "month": month,
            "rows": rows,
            "groups": groups,
            "can_manage": can_manage,
            "editable": can_manage and not month.is_locked,
            "group_chart_data": net_bar_payload(groups),
        },
    )


@require_POST
@require_action(Action.FINANCE_MANAGE)
def finance_month_save(request: HttpRequest, pk: int) -> HttpResponse:
    month = get_object_or_404(FinancialMonth.objects.select_related("project"), pk=pk)
    _assert_month_in_scope(request, month)
    try:
        with transaction.atomic():
            for category in FinanceCategory.objects.filter(is_active=True):
                raw = request.POST.get(f"cat_{category.pk}")
                if raw not in (None, ""):
                    set_line_item(
                        month,
                        category,
                        normalize_source_amount(category.kind, raw),
                        actor=request.user,
                    )
            recompute_month(month, actor=request.user)
        messages.success(request, _("Saved and recalculated."))
    except (FinanceError, ValueError) as exc:
        messages.error(request, str(exc) or _("Invalid input."))
    return redirect("finance_month_detail", pk=month.pk)


@require_POST
@require_action(Action.FINANCE_MANAGE)
def finance_month_lock(request: HttpRequest, pk: int) -> HttpResponse:
    month = get_object_or_404(FinancialMonth.objects.select_related("project"), pk=pk)
    _assert_month_in_scope(request, month)
    lock_month(month, actor=request.user)
    messages.success(request, _("Month locked."))
    return redirect("finance_month_detail", pk=month.pk)


@require_POST
@require_action(Action.FINANCE_MANAGE)
def finance_month_reopen(request: HttpRequest, pk: int) -> HttpResponse:
    month = get_object_or_404(FinancialMonth.objects.select_related("project"), pk=pk)
    _assert_month_in_scope(request, month)
    try:
        reopen_month(month, reason=request.POST.get("reason"), actor=request.user)
        messages.success(request, _("Month reopened."))
    except FinanceError as exc:
        messages.error(request, str(exc))
    return redirect("finance_month_detail", pk=month.pk)


@require_POST
@require_action(Action.FINANCE_MANAGE)
def record_month(request: HttpRequest) -> HttpResponse:
    project = get_object_or_404(
        Project, pk=request.POST.get("project"), financial_reporting_eligible=True
    )
    scope = user_office_scope(request.user)
    if scope is not None and not scope.filter(pk=project.office_id).exists():
        raise PermissionDenied("This project belongs to another office.")
    try:
        record_financial_month(
            project,
            int(request.POST.get("year")),
            int(request.POST.get("month")),
            normalize_source_amount(
                FinanceCategoryKind.REVENUE, request.POST.get("revenue") or 0
            ),
            normalize_source_amount(
                FinanceCategoryKind.COST, request.POST.get("cost") or 0
            ),
            actor=request.user,
        )
        messages.success(request, _("Financial month saved."))
    except (FinanceError, ValueError, TypeError) as exc:
        messages.error(request, str(exc) or _("Invalid input."))
    return redirect("finance_summary")


@require_action(Action.FINANCE_VIEW_SUMMARY)
def finance_workbook(request: HttpRequest, year: int, month: int) -> HttpResponse:
    """One period laid out the way Jober's own workbook draws it.

    Projects across, categories down, a subtotal per office and a grand total —
    the shape of `HV 202510.xlsx` (Jober_Finance_Specs §3). Read-only: entry
    stays on `finance_month_detail`, so there is one write path, not two.

    Office-scoped through `user_office_scope`, which the workbook has no concept
    of and the product does: a Velký Meder manager sees Velký Meder columns.
    """
    if not 1 <= month <= 12:
        raise Http404("Month must be between 1 and 12.")
    grid = workbook_grid(year, month, offices=user_office_scope(request.user))
    return TemplateResponse(
        request,
        "pages/finance_workbook.html",
        {"grid": grid},
    )


@require_action(Action.FINANCE_VIEW_SUMMARY)
def finance_workbook_year(request: HttpRequest, year: int) -> HttpResponse:
    """All months in one read-only category × project workbook."""
    grid = workbook_year_grid(year, offices=user_office_scope(request.user))
    return TemplateResponse(
        request,
        "pages/finance_workbook_year.html",
        {"grid": grid},
    )


def _project_in_scope(request: HttpRequest, pk: int):
    """The project behind a grid URL, or 403.

    Same reasoning as `_assert_month_in_scope`: these views take a pk, so
    filtering some other list is not the boundary.
    """
    project = get_object_or_404(
        Project.objects.select_related("office"),
        pk=pk,
        financial_reporting_eligible=True,
    )
    scope = user_office_scope(request.user)
    if scope is not None and not scope.filter(pk=project.office_id).exists():
        raise PermissionDenied("This project belongs to another office.")
    return project


@require_action(Action.FINANCE_VIEW_SUMMARY)
def finance_project_year(request: HttpRequest, pk: int, year: int) -> HttpResponse:
    """One project across a whole year: categories down, twelve months across.

    A view over the `FinancialMonth` rows that already exist — no annual
    storage, and no annual figure that could disagree with the months it
    summarises. Since 2026-08-05 it is also where those months get typed in:
    the cells write back through the same twelve records, so the year still
    cannot disagree with itself.
    """
    project = _project_in_scope(request, pk)
    return TemplateResponse(
        request,
        "pages/finance_project_year.html",
        {
            "grid": project_year_grid(project, year),
            "can_manage": user_can(request.user, Action.FINANCE_MANAGE),
        },
    )


@require_POST
@require_action(Action.FINANCE_MANAGE)
def finance_project_year_save(request: HttpRequest, pk: int, year: int) -> HttpResponse:
    """Save the whole year grid in one go."""
    project = _project_in_scope(request, pk)
    submitted = {}
    for category in FinanceCategory.objects.filter(is_active=True):
        for month in range(1, 13):
            raw = request.POST.get(cell_field_name(month, category.pk))
            if raw not in (None, ""):
                submitted[(month, category.pk)] = raw
    try:
        result = save_project_year(project, year, submitted, actor=request.user)
    except (FinanceError, ValueError) as exc:
        messages.error(request, str(exc) or _("Invalid input."))
        return redirect("finance_project_year", pk=project.pk, year=year)

    if result["cells_written"]:
        messages.success(
            request,
            _("%(cells)s amounts saved across %(months)s month(s).")
            % {
                "cells": result["cells_written"],
                "months": len(result["months_written"]),
            },
        )
    else:
        messages.success(request, _("Nothing changed."))
    if result["months_locked"]:
        # Never silent: a skipped month that nobody mentions reads as data loss.
        messages.error(
            request,
            _("Locked and left untouched: month(s) %(months)s. Reopen them to edit.")
            % {"months": ", ".join(str(m) for m in result["months_locked"])},
        )
    return redirect("finance_project_year", pk=project.pk, year=year)
