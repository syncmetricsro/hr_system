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


def positive_amount(value) -> Decimal:
    """Coerce to Decimal and enforce the positive sign convention (confirmed with
    Jober 2026-06-29: costs and revenues are entered as positive numbers; the
    system computes net = revenue - cost). Negative input is rejected rather than
    silently flipped, so bad data can't invert a total."""
    amount = Decimal(value or 0)
    if amount < 0:
        raise FinanceError("Amounts use a positive convention; negative values are not allowed.")
    return amount


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


def project_totals(year=None):
    """Per-project results (revenue, cost, net) — dynamic over all months or one
    year. Costs/revenues never hardcoded; every project is included."""
    qs = FinancialMonth.objects.all()
    if year is not None:
        qs = qs.filter(year=year)
    rows = []
    for r in (
        qs.values("project_id", "project__name", "project__code")
        .annotate(revenue=Sum("revenue"), cost=Sum("cost"))
        .order_by("project__name")
    ):
        rev = r["revenue"] or Decimal("0")
        cost = r["cost"] or Decimal("0")
        rows.append({
            "project_id": r["project_id"], "name": r["project__name"],
            "code": r["project__code"], "revenue": rev, "cost": cost, "net": rev - cost,
        })
    return rows


def yearly_totals():
    """Company results rolled up per year (newest first)."""
    rows = []
    for r in (
        FinancialMonth.objects.values("year")
        .annotate(revenue=Sum("revenue"), cost=Sum("cost"))
        .order_by("-year")
    ):
        rev = r["revenue"] or Decimal("0")
        cost = r["cost"] or Decimal("0")
        rows.append({"year": r["year"], "revenue": rev, "cost": cost, "net": rev - cost})
    return rows


@transaction.atomic
def record_financial_month(project, year, month, revenue, cost, *, actor=None, note: str = ""):
    existing = FinancialMonth.objects.filter(project=project, year=year, month=month).first()
    if existing and existing.is_locked:
        raise FinanceError("This financial month is locked.")
    obj, _created = FinancialMonth.objects.update_or_create(
        project=project, year=year, month=month,
        defaults={
            "revenue": positive_amount(revenue),
            "cost": positive_amount(cost),
            "note": note,
            "recorded_by": actor if getattr(actor, "is_authenticated", False) else None,
        },
    )
    record_event(actor, "finance.month_recorded", target=obj, project=project.code)
    return obj


def company_totals(year=None):
    """Dynamic grand totals over every project/month (never hardcoded). Pass
    ``year`` to scope to a single year for the yearly rollup."""
    qs = FinancialMonth.objects.all()
    if year is not None:
        qs = qs.filter(year=year)
    agg = qs.aggregate(revenue=Sum("revenue"), cost=Sum("cost"))
    revenue = agg["revenue"] or Decimal("0")
    cost = agg["cost"] or Decimal("0")
    return {"revenue": revenue, "cost": cost, "net": revenue - cost}
