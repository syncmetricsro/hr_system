from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.db.models import Count, Q, Sum
from django.utils.translation import gettext, gettext_lazy as _

from core.audit.services import record_event
from features.profitability.models import (
    FinanceCategoryKind,
    FinanceGroup,
    FinanceLineItem,
    FinancialMonth,
)


class FinanceError(Exception):
    """Raised on an invalid finance operation (e.g. editing a locked month)."""


def positive_amount(value) -> Decimal:
    """Coerce to Decimal and enforce the positive sign convention (confirmed with
    Jober 2026-06-29: costs and revenues are entered as positive numbers; the
    system computes net = revenue - cost). Negative input is rejected rather than
    silently flipped, so bad data can't invert a total."""
    amount = Decimal(value or 0)
    if amount < 0:
        raise FinanceError(
            "Amounts use a positive convention; negative values are not allowed."
        )
    return amount


def normalize_source_amount(kind, value) -> Decimal:
    """Validate workbook-facing signs and return a positive storage magnitude."""
    amount = Decimal(value or 0)
    if kind == FinanceCategoryKind.COST:
        if amount > 0:
            raise FinanceError("Costs must be entered as negative amounts.")
        return abs(amount)
    if kind == FinanceCategoryKind.REVENUE:
        if amount < 0:
            raise FinanceError("Revenues must be entered as positive amounts.")
        return amount
    raise FinanceError("Unknown finance category kind.")


def signed_amount(kind, amount) -> Decimal:
    magnitude = positive_amount(amount)
    return -magnitude if kind == FinanceCategoryKind.COST else magnitude


@transaction.atomic
def set_line_item(month, category, amount, *, actor=None):
    """Enter/update one line-item amount (positive) on a month. Does not
    recompute totals — that's the explicit 'calculate' action (Finance_Specs §5)."""
    if month.is_locked:
        raise FinanceError("This financial month is locked.")
    item, _created = FinanceLineItem.objects.update_or_create(
        month=month, category=category, defaults={"amount": positive_amount(amount)}
    )
    record_event(actor, "finance.line_item_set", target=item, category=category.label)
    return item


@transaction.atomic
def recompute_month(month, *, actor=None):
    """Roll the line items up into the month's revenue/cost totals — dynamically
    over the full set of line items (avoids the spreadsheet's off-by-one bug)."""
    if month.is_locked:
        raise FinanceError("This financial month is locked.")
    agg = month.line_items.values("category__kind").annotate(total=Sum("amount"))
    totals = {row["category__kind"]: row["total"] or Decimal("0") for row in agg}
    month.revenue = totals.get(FinanceCategoryKind.REVENUE, Decimal("0"))
    month.cost = totals.get(FinanceCategoryKind.COST, Decimal("0"))
    month.save(update_fields=["revenue", "cost", "updated_at"])
    record_event(actor, "finance.recomputed", target=month, net=str(month.net))
    return month


def group_breakdown(months=None, offices=None) -> list[dict]:
    """Per-group result (revenue - cost) across line items — for the manager's
    transport/accommodation/overhead view. Dynamic over the given months (or
    all). ``offices=None`` (ADR 0026 Phase A) means unrestricted (Observer) —
    never "all offices," since a real all-offices filter would exclude any
    project with no office assigned yet."""
    qs = FinanceLineItem.objects.all()
    if months is not None:
        qs = qs.filter(month__in=months)
    if offices is not None:
        qs = qs.filter(month__project__office__in=offices)
    by_group: dict[str, dict] = {}
    for row in qs.values("category__group", "category__kind").annotate(
        total=Sum("amount")
    ):
        group = row["category__group"]
        entry = by_group.setdefault(
            group, {"group": group, "revenue": Decimal("0"), "cost": Decimal("0")}
        )
        if row["category__kind"] == FinanceCategoryKind.REVENUE:
            entry["revenue"] += row["total"] or Decimal("0")
        else:
            entry["cost"] += row["total"] or Decimal("0")
    rows = []
    for entry in by_group.values():
        entry["net"] = entry["revenue"] - entry["cost"]
        try:
            entry["label"] = str(FinanceGroup(entry["group"]).label)
        except ValueError:
            entry["label"] = entry["group"]
        rows.append(entry)
    rows.sort(key=lambda e: e["label"])
    return rows


@transaction.atomic
def lock_month(month, *, actor=None):
    """Close a financial month: no further line-item edits until reopened."""
    month.is_locked = True
    month.save(update_fields=["is_locked", "updated_at"])
    record_event(actor, "finance.locked", target=month)
    return month


@transaction.atomic
def reopen_month(month, *, reason, actor=None):
    """Reopen a locked month. A reason is mandatory and is recorded in the audit
    trail (Finance_Specs §5: reopening a closed month needs a reason + audit)."""
    reason = (reason or "").strip()
    if not reason:
        raise FinanceError("A reason is required to reopen a locked month.")
    month.is_locked = False
    month.save(update_fields=["is_locked", "updated_at"])
    record_event(actor, "finance.reopened", target=month, reason=reason)
    return month


def project_totals(year=None, offices=None):
    """Per-project results (revenue, cost, net) — dynamic over all months or one
    year. Costs/revenues never hardcoded; every project is included.
    ``offices=None`` (ADR 0026 Phase A) means unrestricted (Observer)."""
    qs = FinancialMonth.objects.filter(project__financial_reporting_eligible=True)
    if year is not None:
        qs = qs.filter(year=year)
    if offices is not None:
        qs = qs.filter(project__office__in=offices)
    rows = []
    for r in (
        qs.values(
            "project_id", "project__name", "project__code", "project__office__name"
        )
        .annotate(revenue=Sum("revenue"), cost=Sum("cost"))
        .order_by("project__name")
    ):
        rev = r["revenue"] or Decimal("0")
        cost = r["cost"] or Decimal("0")
        rows.append(
            {
                "project_id": r["project_id"],
                "name": r["project__name"],
                "code": r["project__code"],
                "office": r["project__office__name"],
                "revenue": rev,
                "cost": cost,
                "net": rev - cost,
            }
        )
    return rows


def monthly_totals(year=None, offices=None) -> list[dict]:
    """Company results per calendar month, oldest first (a trend series — unlike
    yearly_totals' newest-first drill-down list, don't reverse this to match).
    ``all_locked`` is True only when every contributing project-month for that
    bucket is locked, for a filled-vs-hollow point style, not a gate.
    ``offices=None`` (ADR 0026 Phase A) means unrestricted (Observer)."""
    qs = FinancialMonth.objects.filter(project__financial_reporting_eligible=True)
    if year is not None:
        qs = qs.filter(year=year)
    if offices is not None:
        qs = qs.filter(project__office__in=offices)
    rows = []
    for r in (
        qs.values("year", "month")
        .annotate(
            revenue=Sum("revenue"),
            cost=Sum("cost"),
            locked_count=Count("pk", filter=Q(is_locked=True)),
            total_count=Count("pk"),
        )
        .order_by("year", "month")
    ):
        revenue = r["revenue"] or Decimal("0")
        cost = r["cost"] or Decimal("0")
        rows.append(
            {
                "year": r["year"],
                "month": r["month"],
                "revenue": revenue,
                "cost": cost,
                "net": revenue - cost,
                "all_locked": r["total_count"] > 0
                and r["locked_count"] == r["total_count"],
            }
        )
    return rows


def yearly_totals(offices=None):
    """Company results rolled up per year (newest first).
    ``offices=None`` (ADR 0026 Phase A) means unrestricted (Observer)."""
    qs = FinancialMonth.objects.filter(project__financial_reporting_eligible=True)
    if offices is not None:
        qs = qs.filter(project__office__in=offices)
    rows = []
    for r in (
        qs.values("year")
        .annotate(revenue=Sum("revenue"), cost=Sum("cost"))
        .order_by("-year")
    ):
        rev = r["revenue"] or Decimal("0")
        cost = r["cost"] or Decimal("0")
        rows.append(
            {"year": r["year"], "revenue": rev, "cost": cost, "net": rev - cost}
        )
    return rows


@transaction.atomic
def record_financial_month(
    project, year, month, revenue, cost, *, actor=None, note: str = ""
):
    existing = FinancialMonth.objects.filter(
        project=project, year=year, month=month
    ).first()
    if existing and existing.is_locked:
        raise FinanceError("This financial month is locked.")
    obj, _created = FinancialMonth.objects.update_or_create(
        project=project,
        year=year,
        month=month,
        defaults={
            "revenue": positive_amount(revenue),
            "cost": positive_amount(cost),
            "note": note,
            "recorded_by": actor if getattr(actor, "is_authenticated", False) else None,
        },
    )
    record_event(actor, "finance.month_recorded", target=obj, project=project.code)
    return obj


def ensure_financial_month(project, year, month, *, actor=None):
    """The month a grid cell belongs to, created empty if it does not exist.

    Distinct from ``record_financial_month``, which sets revenue and cost
    outright: here the totals are about to be recomputed from line items, so
    creating at zero is correct and overwriting an existing month's totals
    would not be. The audit event fires only on creation — a save that touches
    an existing month should not look like the month was re-recorded.
    """
    obj, created = FinancialMonth.objects.get_or_create(
        project=project,
        year=year,
        month=month,
        defaults={
            "revenue": Decimal("0"),
            "cost": Decimal("0"),
            "recorded_by": actor if getattr(actor, "is_authenticated", False) else None,
        },
    )
    if created:
        record_event(actor, "finance.month_recorded", target=obj, project=project.code)
    return obj


@transaction.atomic
def save_project_year(project, year, submitted, *, actor=None):
    """Write a year of the project grid back through its twelve months.

    ``submitted`` maps ``(month, category_pk)`` to the raw workbook-signed
    string the operator typed. Returns what happened, because the caller has to
    tell them: months written, months skipped for being locked, and cells that
    were already correct.

    Three rules earn their place here:

    * **Only changed cells are written.** A full grid is 24 categories x 12
      months; saving it unchanged would otherwise write 288 rows and 288 audit
      events recording that nothing happened.
    * **A month is created only if one of its cells is actually filled.** The
      grid promises that an unrecorded month shows a dash rather than a zero,
      and a save must not quietly turn eleven empty columns into recorded
      months.
    * **A locked month is skipped, not fatal.** Closing January must not stop
      February being entered, and silently dropping it would read as data loss
      — so the skipped months are reported back.
    """
    categories = {c.pk: c for c in _ordered_categories()}
    existing_months = {
        m.month: m for m in FinancialMonth.objects.filter(project=project, year=year)
    }
    current = {}
    for item in FinanceLineItem.objects.filter(
        month__project=project, month__year=year
    ).select_related("month"):
        current[(item.month.month, item.category_id)] = item.amount

    skipped_locked = sorted(
        {
            month
            for (month, _category_pk), raw in submitted.items()
            if raw not in (None, "")
            and month in existing_months
            and existing_months[month].is_locked
        }
    )

    # Validate every cell before writing any of them. One bad sign in a grid of
    # 300 boxes must not half-save a year, and reporting the offenders one per
    # attempt would make pasting a column an afternoon's work.
    changed_by_month: dict[int, list] = {}
    rejected: list[str] = []
    for (month_number, category_pk), raw in sorted(submitted.items()):
        if raw in (None, ""):
            continue
        category = categories.get(category_pk)
        if category is None:
            continue
        if month_number in skipped_locked:
            continue
        try:
            amount = normalize_source_amount(category.kind, raw)
        except (FinanceError, ArithmeticError, ValueError):
            rejected.append(
                _("%(category)s (month %(month)s)")
                % {"category": gettext(category.label), "month": month_number}
            )
            continue
        if current.get((month_number, category_pk)) == amount:
            continue
        changed_by_month.setdefault(month_number, []).append((category, amount))

    if rejected:
        raise FinanceError(
            _(
                "Costs are entered as negative amounts and revenues as positive. "
                "Check: %(cells)s."
            )
            % {"cells": ", ".join(rejected)}
        )

    for month_number, changes in sorted(changed_by_month.items()):
        month = existing_months.get(month_number) or ensure_financial_month(
            project, year, month_number, actor=actor
        )
        for category, amount in changes:
            set_line_item(month, category, amount, actor=actor)
        recompute_month(month, actor=actor)

    return {
        "months_written": sorted(changed_by_month),
        "months_locked": skipped_locked,
        "cells_written": sum(len(v) for v in changed_by_month.values()),
    }


def company_totals(year=None, offices=None):
    """Dynamic grand totals over every project/month (never hardcoded). Pass
    ``year`` to scope to a single year for the yearly rollup.
    ``offices=None`` (ADR 0026 Phase A) means unrestricted (Observer) —
    never "all offices," since that would exclude projects with no office
    assigned yet."""
    qs = FinancialMonth.objects.filter(project__financial_reporting_eligible=True)
    if year is not None:
        qs = qs.filter(year=year)
    if offices is not None:
        qs = qs.filter(project__office__in=offices)
    agg = qs.aggregate(revenue=Sum("revenue"), cost=Sum("cost"))
    revenue = agg["revenue"] or Decimal("0")
    cost = agg["cost"] or Decimal("0")
    return {"revenue": revenue, "cost": cost, "net": revenue - cost}


def margin_pct(totals: dict) -> Decimal:
    """Net as a percentage of revenue, for the margin gauge — zero-guarded,
    not a hardcoded/estimated figure."""
    if not totals["revenue"]:
        return Decimal("0")
    return (totals["net"] / totals["revenue"] * 100).quantize(Decimal("0.1"))


def office_totals(year=None, offices=None):
    """Roll-up by the project's real ``Office`` (ADR 0026 Phase A — replaces
    the old region-based roll-up now that ``Project.office`` is a real FK).
    ``offices=None`` means unrestricted (Observer); a scoped caller (manager,
    coordinator, recruiter) passes the offices they belong to."""
    qs = FinancialMonth.objects.filter(project__financial_reporting_eligible=True)
    if year is not None:
        qs = qs.filter(year=year)
    if offices is not None:
        qs = qs.filter(project__office__in=offices)
    rows = []
    for row in (
        qs.values("project__office__name")
        .annotate(revenue=Sum("revenue"), cost=Sum("cost"))
        .order_by("project__office__name")
    ):
        revenue = row["revenue"] or Decimal("0")
        cost = row["cost"] or Decimal("0")
        rows.append(
            {
                "office": row["project__office__name"] or "Unassigned",
                "revenue": revenue,
                "cost": -cost,
                "net": revenue - cost,
            }
        )
    return rows


def office_monthly_totals(year=None, offices=None) -> list[dict]:
    """Per-office monthly trend (ADR 0026 Phase A) — the data source for the
    executive dashboard's multi-series chart (one line per office). Rows are
    one per (year, month, office) bucket, oldest first, matching
    ``monthly_totals``'s ordering convention. ``offices=None`` means
    unrestricted (Observer)."""
    qs = FinancialMonth.objects.filter(project__financial_reporting_eligible=True)
    if year is not None:
        qs = qs.filter(year=year)
    if offices is not None:
        qs = qs.filter(project__office__in=offices)
    rows = []
    for r in (
        qs.values("year", "month", "project__office__name")
        .annotate(revenue=Sum("revenue"), cost=Sum("cost"))
        .order_by("year", "month", "project__office__name")
    ):
        revenue = r["revenue"] or Decimal("0")
        cost = r["cost"] or Decimal("0")
        rows.append(
            {
                "year": r["year"],
                "month": r["month"],
                "office": r["project__office__name"] or "Unassigned",
                "revenue": revenue,
                "cost": cost,
                "net": revenue - cost,
            }
        )
    return rows


# ---------------------------------------------------------------------------
# Workbook-shaped grids (Jober_Finance_Specs §3, §6)
#
# The client's `HV 202510.xlsx` presents one period as projects across the top
# and categories down the side, with a subtotal per office and a grand total.
# These two builders produce that shape from stored line items. Neither reads a
# cached total: spec §7 records a real formula defect in the source workbook
# (`C24=SUM(C3:C22)` drops one row), and the whole point of computing here is
# that the same category set is applied to every column.
# ---------------------------------------------------------------------------


def _ordered_categories():
    """Rows of the grid, in workbook order: costs first, then revenues."""
    from features.profitability.models import FinanceCategory

    return list(
        FinanceCategory.objects.filter(is_active=True).order_by(
            "kind", "order", "label"
        )
    )


def workbook_grid(year, month, *, offices=None):
    """One period as the workbook draws it.

    Returns projects (columns), categories (rows), a cell lookup keyed
    ``(project_id, category_id)``, per-project cost/revenue/net, per-office
    subtotals and a grand total. ``offices=None`` means unrestricted — the
    established sentinel, never "every office".

    Amounts are signed for display (costs negative), matching the source; the
    database keeps magnitudes with ``kind`` carrying the sign.
    """
    from core.projects.models import Project

    projects = Project.objects.filter(
        is_active=True, financial_reporting_eligible=True
    ).select_related("office")
    if offices is not None:
        projects = projects.filter(office__in=offices)
    projects = list(projects.order_by("office__name", "name"))

    categories = _ordered_categories()
    months = FinancialMonth.objects.filter(
        year=year, month=month, project__in=projects
    ).select_related("project")
    month_by_project = {m.project_id: m for m in months}
    # Keyed by month id, not project id. These are different sequences, and they
    # only coincide on a database where both happen to have been created in
    # lockstep - which is true of a fresh test database and false of every real
    # one, so mixing them up fails nowhere until it fails everywhere.
    project_by_month = {m.pk: m.project_id for m in months}

    cells = {}
    for item in FinanceLineItem.objects.filter(month__in=months).select_related(
        "category"
    ):
        project_id = project_by_month[item.month_id]
        cells[(project_id, item.category_id)] = signed_amount(
            item.category.kind, item.amount
        )

    columns, by_office = [], {}
    for project in projects:
        cost = sum(
            (
                cells.get((project.pk, c.pk), Decimal("0"))
                for c in categories
                if c.kind == FinanceCategoryKind.COST
            ),
            Decimal("0"),
        )
        revenue = sum(
            (
                cells.get((project.pk, c.pk), Decimal("0"))
                for c in categories
                if c.kind == FinanceCategoryKind.REVENUE
            ),
            Decimal("0"),
        )
        column = {
            "project": project,
            "month": month_by_project.get(project.pk),
            "cost": cost,  # negative or zero
            "revenue": revenue,  # positive or zero
            "net": cost + revenue,  # spec §6: P/L is their sum
        }
        columns.append(column)
        office = project.office.name if project.office else "Unassigned"
        by_office.setdefault(office, []).append(column)

    offices_rows = [
        {
            "office": name,
            "columns": cols,
            "cost": sum((c["cost"] for c in cols), Decimal("0")),
            "revenue": sum((c["revenue"] for c in cols), Decimal("0")),
            "net": sum((c["net"] for c in cols), Decimal("0")),
        }
        for name, cols in sorted(by_office.items())
    ]

    # Rows carry their values already aligned to `columns`. Django templates
    # cannot look a dict up by a variable key, and a custom filter to do it
    # would push grid arithmetic into the template — the one place it cannot be
    # tested.
    def rows_for(kind):
        return [
            {
                "category": category,
                "values": [
                    cells.get((column["project"].pk, category.pk)) for column in columns
                ],
            }
            for category in categories
            if category.kind == kind
        ]

    return {
        "year": year,
        "month": month,
        "categories": categories,
        "columns": columns,
        "cells": cells,
        "cost_rows": rows_for(FinanceCategoryKind.COST),
        "revenue_rows": rows_for(FinanceCategoryKind.REVENUE),
        "offices": offices_rows,
        "grand": {
            "cost": sum((c["cost"] for c in columns), Decimal("0")),
            "revenue": sum((c["revenue"] for c in columns), Decimal("0")),
            "net": sum((c["net"] for c in columns), Decimal("0")),
        },
    }


def cell_field_name(month: int, category_pk: int) -> str:
    """The grid's input name. Shared so the writer parses what the reader drew."""
    return f"cell_{month}_{category_pk}"


def project_year_grid(project, year):
    """One project across a whole year: categories down, 12 months across.

    The caller is responsible for having checked the project is in scope — this
    takes an object, not a filter, so the office guard belongs in the view where
    the request is (the pattern `_assert_month_in_scope` already follows).
    """
    categories = _ordered_categories()
    months = {
        m.month: m for m in FinancialMonth.objects.filter(project=project, year=year)
    }

    cells = {}
    for item in FinanceLineItem.objects.filter(
        month__project=project, month__year=year
    ).select_related("category", "month"):
        cells[(item.month.month, item.category_id)] = signed_amount(
            item.category.kind, item.amount
        )

    locked = {m: month.is_locked for m, month in months.items()}

    rows = []
    for category in categories:
        by_month = [cells.get((m, category.pk)) for m in range(1, 13)]
        rows.append(
            {
                "category": category,
                "months": by_month,
                # The same twelve values with what the template needs to draw an
                # input: a stable field name and whether this month accepts one.
                # An unrecorded month is editable — that is how a year gets
                # filled in — but a locked one is shown, not typed into.
                "cells": [
                    {
                        "value": by_month[m - 1],
                        "month": m,
                        "name": cell_field_name(m, category.pk),
                        "editable": not locked.get(m, False),
                    }
                    for m in range(1, 13)
                ],
                "total": sum((v for v in by_month if v is not None), Decimal("0")),
            }
        )

    def column_total(month_number, kind=None):
        return sum(
            (
                cells.get((month_number, c.pk), Decimal("0"))
                for c in categories
                if kind is None or c.kind == kind
            ),
            Decimal("0"),
        )

    month_totals = [
        {
            "month": m,
            "recorded": m in months,
            "locked": locked.get(m, False),
            "pk": months[m].pk if m in months else None,
            "cost": column_total(m, FinanceCategoryKind.COST),
            "revenue": column_total(m, FinanceCategoryKind.REVENUE),
            "net": column_total(m),
        }
        for m in range(1, 13)
    ]

    return {
        "project": project,
        "year": year,
        "categories": categories,
        "rows": rows,
        "has_recorded_months": bool(months),
        "month_totals": month_totals,
        "year_total": {
            "cost": sum((t["cost"] for t in month_totals), Decimal("0")),
            "revenue": sum((t["revenue"] for t in month_totals), Decimal("0")),
            "net": sum((t["net"] for t in month_totals), Decimal("0")),
        },
    }
