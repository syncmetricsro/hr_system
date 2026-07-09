from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from core.accounts.permissions import Action, require_action
from core.accounts.permissions import can as user_can
from features.finance.models import FinanceCategory, FinancialMonth
from features.finance.services import (
    FinanceError,
    company_totals,
    group_breakdown,
    lock_month,
    project_totals,
    recompute_month,
    record_financial_month,
    reopen_month,
    set_line_item,
    yearly_totals,
)
from core.projects.models import Project


@require_action(Action.FINANCE_VIEW_SUMMARY)
def finance_summary(request: HttpRequest) -> HttpResponse:
    months = FinancialMonth.objects.select_related("project")
    return TemplateResponse(
        request,
        "pages/finance_summary.html",
        {
            "months": months,
            "totals": company_totals(),
            "groups": group_breakdown(),
            "project_results": project_totals(),
            "years": yearly_totals(),
            "projects": Project.objects.filter(is_active=True),
        },
    )


@require_action(Action.FINANCE_VIEW_SUMMARY)
def finance_year(request: HttpRequest, year: int) -> HttpResponse:
    months = FinancialMonth.objects.select_related("project").filter(year=year)
    return TemplateResponse(
        request,
        "pages/finance_year.html",
        {
            "year": year,
            "months": months,
            "totals": company_totals(year),
            "groups": group_breakdown(list(months)),
            "project_results": project_totals(year),
        },
    )


@require_action(Action.FINANCE_VIEW_SUMMARY)
def finance_month_detail(request: HttpRequest, pk: int) -> HttpResponse:
    month = get_object_or_404(FinancialMonth.objects.select_related("project"), pk=pk)
    categories = FinanceCategory.objects.filter(is_active=True)
    amounts = {li.category_id: li.amount for li in month.line_items.all()}
    rows = [{"category": c, "amount": amounts.get(c.id, "")} for c in categories]
    can_manage = user_can(request.user, Action.FINANCE_MANAGE)
    return TemplateResponse(
        request,
        "pages/finance_month_detail.html",
        {
            "month": month,
            "rows": rows,
            "groups": group_breakdown([month]),
            "can_manage": can_manage,
            "editable": can_manage and not month.is_locked,
        },
    )


@require_POST
@require_action(Action.FINANCE_MANAGE)
def finance_month_save(request: HttpRequest, pk: int) -> HttpResponse:
    month = get_object_or_404(FinancialMonth, pk=pk)
    try:
        for category in FinanceCategory.objects.filter(is_active=True):
            raw = request.POST.get(f"cat_{category.pk}")
            if raw not in (None, ""):
                set_line_item(month, category, raw, actor=request.user)
        recompute_month(month, actor=request.user)
        messages.success(request, _("Saved and recalculated."))
    except (FinanceError, ValueError) as exc:
        messages.error(request, str(exc) or _("Invalid input."))
    return redirect("finance_month_detail", pk=month.pk)


@require_POST
@require_action(Action.FINANCE_MANAGE)
def finance_month_lock(request: HttpRequest, pk: int) -> HttpResponse:
    month = get_object_or_404(FinancialMonth, pk=pk)
    lock_month(month, actor=request.user)
    messages.success(request, _("Month locked."))
    return redirect("finance_month_detail", pk=month.pk)


@require_POST
@require_action(Action.FINANCE_MANAGE)
def finance_month_reopen(request: HttpRequest, pk: int) -> HttpResponse:
    month = get_object_or_404(FinancialMonth, pk=pk)
    try:
        reopen_month(month, reason=request.POST.get("reason"), actor=request.user)
        messages.success(request, _("Month reopened."))
    except FinanceError as exc:
        messages.error(request, str(exc))
    return redirect("finance_month_detail", pk=month.pk)


@require_POST
@require_action(Action.FINANCE_MANAGE)
def record_month(request: HttpRequest) -> HttpResponse:
    project = get_object_or_404(Project, pk=request.POST.get("project"))
    try:
        record_financial_month(
            project,
            int(request.POST.get("year")),
            int(request.POST.get("month")),
            request.POST.get("revenue") or 0,
            request.POST.get("cost") or 0,
            actor=request.user,
        )
        messages.success(request, _("Financial month saved."))
    except (FinanceError, ValueError, TypeError) as exc:
        messages.error(request, str(exc) or _("Invalid input."))
    return redirect("finance_summary")
