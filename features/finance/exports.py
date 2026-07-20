from __future__ import annotations

from django.http import HttpRequest, HttpResponse

from core.accounts.permissions import Action, require_action
from core.ui.exports import csv_response
from features.finance.models import FinanceLineItem
from features.finance.services import company_totals, regional_totals, signed_amount


@require_action(Action.FINANCE_VIEW_SUMMARY)
def finance_csv(request: HttpRequest) -> HttpResponse:
    response, writer = csv_response("finance.csv")
    writer.writerow(["row_type", "period", "region", "project", "category", "kind", "group", "amount_eur"])
    line_items = FinanceLineItem.objects.select_related(
        "month", "month__project", "category"
    ).filter(month__project__financial_reporting_eligible=True)
    for item in line_items:
        writer.writerow([
            "line", f"{item.month.year}-{item.month.month:02d}",
            item.month.project.region, item.month.project.code,
            item.category.label, item.category.kind, item.category.group,
            signed_amount(item.category.kind, item.amount),
        ])
    for region in regional_totals():
        writer.writerow(["region_summary", "all", region["region"], "", "profit/loss", "summary", "", region["net"]])
    totals = company_totals()
    for label, amount in (("revenue", totals["revenue"]), ("cost", -totals["cost"]), ("profit/loss", totals["net"])):
        writer.writerow(["grand_summary", "all", "", "", label, "summary", "", amount])
    return response
