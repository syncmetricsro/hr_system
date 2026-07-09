from __future__ import annotations

from django.http import HttpRequest, HttpResponse

from core.accounts.permissions import Action, require_action
from core.ui.exports import csv_response
from features.finance.models import FinancialMonth


@require_action(Action.FINANCE_VIEW_SUMMARY)
def finance_csv(request: HttpRequest) -> HttpResponse:
    response, writer = csv_response("finance.csv")
    writer.writerow(["project", "year", "month", "revenue", "cost", "net"])
    for month in FinancialMonth.objects.select_related("project"):
        writer.writerow([
            month.project.code, month.year, month.month,
            month.revenue, month.cost, month.net,
        ])
    return response
