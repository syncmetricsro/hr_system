from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from apps.audit.services import record_event
from apps.finance.models import (
    FinanceCategoryKind,
    FinanceGroup,
    FinanceLineItem,
    FinancialMonth,
)


class FinanceError(Exception):
    """Raised on an invalid finance operation (e.g. editing a locked month)."""


@transaction.atomic
def set_line_item(month, category, amount, *, actor=None):
    """Enter/update one line-item amount (positive) on a month. Does not
    recompute totals — that's the explicit 'calculate' action (Finance_Specs §5)."""
    if month.is_locked:
        raise FinanceError("This financial month is locked.")
    item, _created = FinanceLineItem.objects.update_or_create(
        month=month, category=category, defaults={"amount": Decimal(amount or 0)}
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


def group_breakdown(months=None) -> list[dict]:
    """Per-group result (revenue - cost) across line items — for the manager's
    transport/accommodation/overhead view. Dynamic over the given months (or all)."""
    qs = FinanceLineItem.objects.all()
    if months is not None:
        qs = qs.filter(month__in=months)
    by_group: dict[str, dict] = {}
    for row in qs.values("category__group", "category__kind").annotate(total=Sum("amount")):
        group = row["category__group"]
        entry = by_group.setdefault(group, {"group": group, "revenue": Decimal("0"), "cost": Decimal("0")})
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
def record_financial_month(project, year, month, revenue, cost, *, actor=None, note: str = ""):
    existing = FinancialMonth.objects.filter(project=project, year=year, month=month).first()
    if existing and existing.is_locked:
        raise FinanceError("This financial month is locked.")
    obj, _created = FinancialMonth.objects.update_or_create(
        project=project, year=year, month=month,
        defaults={
            "revenue": Decimal(revenue or 0),
            "cost": Decimal(cost or 0),
            "note": note,
            "recorded_by": actor if getattr(actor, "is_authenticated", False) else None,
        },
    )
    record_event(actor, "finance.month_recorded", target=obj, project=project.code)
    return obj


def company_totals():
    """Dynamic grand totals over every project/month (never hardcoded)."""
    agg = FinancialMonth.objects.aggregate(revenue=Sum("revenue"), cost=Sum("cost"))
    revenue = agg["revenue"] or Decimal("0")
    cost = agg["cost"] or Decimal("0")
    return {"revenue": revenue, "cost": cost, "net": revenue - cost}
