from __future__ import annotations

from django.http import HttpRequest, HttpResponse

from core.accounts.permissions import Action, require_action, user_office_scope
from core.ui.exports import csv_response
from features.finance.models import FinanceLineItem
from features.finance.services import company_totals, office_totals, signed_amount


@require_action(Action.FINANCE_VIEW_SUMMARY)
def finance_csv(request: HttpRequest) -> HttpResponse:
    scope = user_office_scope(request.user)
    response, writer = csv_response("finance.csv")
    writer.writerow(["row_type", "period", "office", "project", "category", "kind", "group", "amount_eur"])
    line_items = FinanceLineItem.objects.select_related(
        "month", "month__project", "month__project__office", "category"
    ).filter(month__project__financial_reporting_eligible=True)
    if scope is not None:
        line_items = line_items.filter(month__project__office__in=scope)
    for item in line_items:
        project_office = item.month.project.office
        writer.writerow([
            "line", f"{item.month.year}-{item.month.month:02d}",
            project_office.name if project_office else "", item.month.project.code,
            item.category.label, item.category.kind, item.category.group,
            signed_amount(item.category.kind, item.amount),
        ])
    for office in office_totals(offices=scope):
        writer.writerow(["office_summary", "all", office["office"], "", "profit/loss", "summary", "", office["net"]])
    totals = company_totals(offices=scope)
    for label, amount in (("revenue", totals["revenue"]), ("cost", -totals["cost"]), ("profit/loss", totals["net"])):
        writer.writerow(["grand_summary", "all", "", "", label, "summary", "", amount])
    return response
