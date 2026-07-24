from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from core.accounts.models import Role
from core.accounts.permissions import Action, require_action, user_office_scope
from core.accounts.permissions import can as user_can
from core.ui.chart_data import net_bar_payload
from features.finance.models import FinanceCategory, FinanceCategoryKind, FinancialMonth
from features.finance.services import (
    FinanceError,
    company_totals,
    group_breakdown,
    lock_month,
    margin_pct,
    monthly_totals,
    normalize_source_amount,
    office_monthly_totals,
    office_totals,
    project_totals,
    recompute_month,
    record_financial_month,
    reopen_month,
    set_line_item,
    signed_amount,
    yearly_totals,
)
from core.projects.models import Project


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


def _assert_month_in_scope(request: HttpRequest, month: FinancialMonth) -> None:
    """ADR 0026 Phase A: a non-Observer can't act on another office's month,
    even by guessing/POSTing a PK directly — the office-scope check must be
    enforced here too, not just hidden from the UI."""
    scope = user_office_scope(request.user)
    if scope is None:
        return
    if not scope.filter(pk=month.project.office_id).exists():
        raise PermissionDenied("This financial month belongs to another office.")


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
                "office_trend_chart_data": _office_trend_chart_data(office_monthly_totals()),
            },
        )

    scope = user_office_scope(request.user)
    months = FinancialMonth.objects.select_related("project").filter(project__office__in=scope)
    totals = company_totals(offices=scope)
    groups = group_breakdown(offices=scope)
    margin = margin_pct(totals)
    offices = office_totals(offices=scope)
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
            "projects": Project.objects.filter(
                is_active=True, financial_reporting_eligible=True, office__in=scope
            ),
            "trend_chart_data": _trend_chart_data(monthly_totals(offices=scope)),
            "gauge_chart_data": {**totals, "margin_pct": margin},
            "group_chart_data": net_bar_payload(groups),
            "regional_chart_data": net_bar_payload(offices, label_key="office"),
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
                        month, category, normalize_source_amount(category.kind, raw),
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
