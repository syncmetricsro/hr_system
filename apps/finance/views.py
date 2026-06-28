from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.accounts.permissions import Action, require_action
from apps.finance.models import FinancialMonth
from apps.finance.services import FinanceError, company_totals, record_financial_month
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
            "projects": Project.objects.filter(is_active=True),
        },
    )


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
