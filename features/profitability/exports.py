from __future__ import annotations

from django.http import HttpRequest, HttpResponse

from core.accounts.permissions import Action, require_action, user_office_scope
from core.ui.exports import csv_response
from features.profitability.models import FinanceLineItem
from features.profitability.services import company_totals, office_totals, signed_amount

#: Jober_Finance_Specs §8. Code and name are separate columns, and so are
#: category key and label: a bookkeeper reads the names, anything downstream
#: joins on the keys, and the keys survive a label being retranslated. Every
#: row — including the summaries — is written at this width, or the file stops
#: being machine-readable whatever the header claims.
COLUMNS = [
    "row_type",
    "period",
    "office",
    "project_code",
    "project_name",
    "category_key",
    "category_label",
    "kind",
    "group",
    "amount_eur",
]


def _row(**values) -> list:
    """One CSV row, always the full width, in the declared column order."""
    return [values.get(column, "") for column in COLUMNS]


@require_action(Action.FINANCE_VIEW_SUMMARY)
def finance_csv(request: HttpRequest) -> HttpResponse:
    scope = user_office_scope(request.user)
    response, writer = csv_response("finance.csv")
    writer.writerow(COLUMNS)

    line_items = FinanceLineItem.objects.select_related(
        "month", "month__project", "month__project__office", "category"
    ).filter(month__project__financial_reporting_eligible=True)
    if scope is not None:
        line_items = line_items.filter(month__project__office__in=scope)

    for item in line_items:
        project = item.month.project
        writer.writerow(
            _row(
                row_type="line",
                period=f"{item.month.year}-{item.month.month:02d}",
                office=project.office.name if project.office else "",
                project_code=project.code,
                project_name=project.name,
                category_key=item.category.key,
                category_label=item.category.label,
                kind=item.category.kind,
                group=item.category.group,
                # Signed for the reader, matching the source workbook; storage
                # keeps the magnitude with `kind` carrying the sign.
                amount_eur=signed_amount(item.category.kind, item.amount),
            )
        )

    # Summary rows are derived here and never read from a stored total
    # (Jober_Finance_Specs §6, and §7 for why that matters).
    for office in office_totals(offices=scope):
        writer.writerow(
            _row(
                row_type="office_summary",
                period="all",
                office=office["office"],
                category_label="profit/loss",
                kind="summary",
                amount_eur=office["net"],
            )
        )

    totals = company_totals(offices=scope)
    for label, amount in (
        ("revenue", totals["revenue"]),
        ("cost", -totals["cost"]),
        ("profit/loss", totals["net"]),
    ):
        writer.writerow(
            _row(
                row_type="grand_summary",
                period="all",
                category_label=label,
                kind="summary",
                amount_eur=amount,
            )
        )
    return response
