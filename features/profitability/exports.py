from __future__ import annotations

from io import BytesIO

import xlsxwriter
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext as _
from django.utils.translation import gettext

from core.accounts.permissions import Action, require_action, user_office_scope
from core.ui.exports import csv_response
from features.profitability.models import FinanceLineItem
from features.profitability.services import (
    company_totals,
    monthly_totals,
    office_totals,
    signed_amount,
    workbook_year_grid,
)

XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
EXCEL_MAX_ROWS = 1_048_576
EXCEL_MAX_COLUMNS = 16_384

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


def _assert_excel_bounds(grid) -> None:
    """Fail before XlsxWriter can create a structurally truncated workbook."""
    year_columns = 1 + len(grid["columns"])
    year_rows = (
        12 + len(grid["cost_rows"]) + len(grid["revenue_rows"]) + len(grid["offices"])
    )
    if year_columns > EXCEL_MAX_COLUMNS or year_rows > EXCEL_MAX_ROWS:
        raise ValueError("Finance data exceeds the XLSX worksheet limits.")


def _write_section_label(worksheet, row, last_column, label, cell_format) -> None:
    if last_column:
        worksheet.merge_range(row, 0, row, last_column, label, cell_format)
    else:
        worksheet.write_string(row, 0, label, cell_format)


def _write_grid_values(worksheet, row, values, money_format) -> None:
    for column, value in enumerate(values, start=1):
        if value is None:
            worksheet.write_blank(row, column, None, money_format)
        else:
            worksheet.write_number(row, column, value, money_format)


def build_finance_xlsx(year: int, *, offices=None) -> bytes:
    """Build a formula-free, office-scoped snapshot of one finance year."""
    grid = workbook_year_grid(year, offices=offices)
    months = {row["month"]: row for row in monthly_totals(year, offices=offices)}
    _assert_excel_bounds(grid)

    output = BytesIO()
    workbook = xlsxwriter.Workbook(
        output,
        {
            "in_memory": True,
            # Database labels are data, never spreadsheet instructions.
            "strings_to_formulas": False,
            "strings_to_urls": False,
        },
    )

    title_format = workbook.add_format(
        {"bold": True, "font_size": 16, "font_color": "#FFFFFF", "bg_color": "#1E3A5F"}
    )
    header_format = workbook.add_format(
        {
            "bold": True,
            "font_color": "#FFFFFF",
            "bg_color": "#2563A6",
            "border": 1,
            "text_wrap": True,
            "valign": "vcenter",
        }
    )
    section_format = workbook.add_format(
        {"bold": True, "bg_color": "#DCEBFA", "border": 1}
    )
    label_format = workbook.add_format({"border": 1})
    money_format = workbook.add_format(
        {"num_format": '#,##0.00 "EUR";[Red]-#,##0.00 "EUR"', "border": 1}
    )
    total_label_format = workbook.add_format(
        {"bold": True, "top": 1, "bottom": 1, "bg_color": "#EDF4FC"}
    )
    total_money_format = workbook.add_format(
        {
            "bold": True,
            "num_format": '#,##0.00 "EUR";[Red]-#,##0.00 "EUR"',
            "top": 1,
            "bottom": 1,
            "bg_color": "#EDF4FC",
        }
    )

    year_sheet_name = str(_("Year"))[:31]
    months_sheet_name = str(_("Months"))[:31]
    year_sheet = workbook.add_worksheet(year_sheet_name)
    months_sheet = workbook.add_worksheet(months_sheet_name)

    # Year: the same category x project data returned to the HTML workbook.
    last_project_column = len(grid["columns"])
    _write_section_label(
        year_sheet,
        0,
        last_project_column,
        _("Finance — %(year)s") % {"year": year},
        title_format,
    )
    year_sheet.write_string(1, 0, str(_("Category")), header_format)
    for column_index, column in enumerate(grid["columns"], start=1):
        project = column["project"]
        office = project.office.name if project.office else "—"
        year_sheet.write_string(
            1, column_index, f"{project.name}\n{office}", header_format
        )
    year_sheet.set_row(1, 34)
    year_sheet.freeze_panes(2, 1)
    year_sheet.set_column(0, 0, 34)
    if last_project_column:
        year_sheet.set_column(1, last_project_column, 16)

    row_index = 2
    _write_section_label(
        year_sheet,
        row_index,
        last_project_column,
        str(_("Costs")),
        section_format,
    )
    row_index += 1
    for row in grid["cost_rows"]:
        year_sheet.write_string(
            row_index, 0, gettext(row["category"].label), label_format
        )
        _write_grid_values(year_sheet, row_index, row["values"], money_format)
        row_index += 1
    year_sheet.write_string(row_index, 0, str(_("Total costs")), total_label_format)
    _write_grid_values(
        year_sheet,
        row_index,
        [column["cost"] for column in grid["columns"]],
        total_money_format,
    )
    row_index += 1

    _write_section_label(
        year_sheet,
        row_index,
        last_project_column,
        str(_("Revenues")),
        section_format,
    )
    row_index += 1
    for row in grid["revenue_rows"]:
        year_sheet.write_string(
            row_index, 0, gettext(row["category"].label), label_format
        )
        _write_grid_values(year_sheet, row_index, row["values"], money_format)
        row_index += 1
    year_sheet.write_string(row_index, 0, str(_("Total revenues")), total_label_format)
    _write_grid_values(
        year_sheet,
        row_index,
        [column["revenue"] for column in grid["columns"]],
        total_money_format,
    )
    row_index += 1
    year_sheet.write_string(row_index, 0, str(_("Profit/loss")), total_label_format)
    _write_grid_values(
        year_sheet,
        row_index,
        [column["net"] for column in grid["columns"]],
        total_money_format,
    )

    # The HTML workbook shows the office roll-up below the project grid. Keep
    # that shape so the downloaded snapshot can be reconciled row for row.
    row_index += 2
    _write_section_label(year_sheet, row_index, 3, str(_("By office")), section_format)
    row_index += 1
    for column_index, label in enumerate(
        (_("Office"), _("Costs"), _("Revenues"), _("Profit/loss"))
    ):
        year_sheet.write_string(row_index, column_index, str(label), header_format)
    row_index += 1
    for office in grid["offices"]:
        year_sheet.write_string(row_index, 0, office["office"], label_format)
        for column_index, key in enumerate(("cost", "revenue", "net"), start=1):
            year_sheet.write_number(row_index, column_index, office[key], money_format)
        row_index += 1
    year_sheet.write_string(row_index, 0, str(_("Total")), total_label_format)
    for column_index, key in enumerate(("cost", "revenue", "net"), start=1):
        year_sheet.write_number(
            row_index, column_index, grid["grand"][key], total_money_format
        )

    # Months: always twelve buckets, including explicit zeroes where nobody
    # recorded a month, so the chart's time axis cannot silently skip periods.
    for column_index, label in enumerate(
        (_("Month"), _("Revenue"), _("Cost"), _("Net"))
    ):
        months_sheet.write_string(0, column_index, str(label), header_format)
    for month_number in range(1, 13):
        monthly = months.get(month_number)
        values = (
            monthly["revenue"] if monthly else 0,
            -monthly["cost"] if monthly else 0,
            monthly["net"] if monthly else 0,
        )
        months_sheet.write_string(
            month_number, 0, f"{year}-{month_number:02d}", label_format
        )
        for column_index, value in enumerate(values, start=1):
            months_sheet.write_number(month_number, column_index, value, money_format)

    project_table_column = 5
    months_sheet.write_string(0, project_table_column, str(_("Project")), header_format)
    months_sheet.write_string(0, project_table_column + 1, str(_("Net")), header_format)
    for project_row, column in enumerate(grid["columns"], start=1):
        months_sheet.write_string(
            project_row, project_table_column, column["project"].name, label_format
        )
        months_sheet.write_number(
            project_row, project_table_column + 1, column["net"], money_format
        )

    months_sheet.freeze_panes(1, 1)
    months_sheet.set_column(0, 0, 13)
    months_sheet.set_column(1, 3, 16)
    months_sheet.set_column(project_table_column, project_table_column, 28)
    months_sheet.set_column(project_table_column + 1, project_table_column + 1, 16)

    trend_chart = workbook.add_chart({"type": "column"})
    for column_index, label in enumerate((_("Revenue"), _("Cost"), _("Net")), start=1):
        trend_chart.add_series(
            {
                "name": str(label),
                "categories": [months_sheet_name, 1, 0, 12, 0],
                "values": [months_sheet_name, 1, column_index, 12, column_index],
            }
        )
    trend_chart.set_title({"name": str(_("Revenue, cost, and net by month"))})
    trend_chart.set_y_axis({"num_format": '#,##0 "EUR"'})
    trend_chart.set_legend({"position": "bottom"})
    months_sheet.insert_chart(14, 0, trend_chart, {"x_scale": 1.35, "y_scale": 1.15})

    if grid["columns"]:
        project_chart = workbook.add_chart({"type": "bar"})
        project_chart.add_series(
            {
                "name": str(_("Net")),
                "categories": [
                    months_sheet_name,
                    1,
                    project_table_column,
                    len(grid["columns"]),
                    project_table_column,
                ],
                "values": [
                    months_sheet_name,
                    1,
                    project_table_column + 1,
                    len(grid["columns"]),
                    project_table_column + 1,
                ],
            }
        )
        project_chart.set_title({"name": str(_("Net by project"))})
        project_chart.set_x_axis({"num_format": '#,##0 "EUR"'})
        project_chart.set_legend({"none": True})
        months_sheet.insert_chart(
            14, 8, project_chart, {"x_scale": 1.25, "y_scale": 1.15}
        )

    workbook.close()
    return output.getvalue()


@require_action(Action.EXPORT_APPROVED)
def finance_xlsx(request: HttpRequest, year: int) -> HttpResponse:
    content = build_finance_xlsx(year, offices=user_office_scope(request.user))
    response = HttpResponse(content, content_type=XLSX_CONTENT_TYPE)
    response["Content-Disposition"] = f'attachment; filename="finance-{year}.xlsx"'
    return response
