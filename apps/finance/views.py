from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.accounts.permissions import Action, require_action
from apps.accounts.permissions import can as user_can
from apps.finance.models import FinanceCategory, FinancialMonth
from apps.finance.services import (
    FinanceError,
    company_totals,
    group_breakdown,
    recompute_month,
    record_financial_month,
    set_line_item,
)
from apps.projects.models import Project


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
            "projects": Project.objects.filter(is_active=True),
        },
    )


@require_action(Action.FINANCE_VIEW_SUMMARY)
def finance_month_detail(request: HttpRequest, pk: int) -> HttpResponse:
    month = get_object_or_404(FinancialMonth.objects.select_related("project"), pk=pk)
    categories = FinanceCategory.objects.filter(is_active=True)
    amounts = {li.category_id: li.amount for li in month.line_items.all()}
    rows = [{"category": c, "amount": amounts.get(c.id, "")} for c in categories]
    return TemplateResponse(
        request,
        "pages/finance_month_detail.html",
        {
            "month": month,
            "rows": rows,
            "groups": group_breakdown([month]),
            "can_manage": user_can(request.user, Action.FINANCE_MANAGE),
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
