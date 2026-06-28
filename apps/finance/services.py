from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from apps.audit.services import record_event
from apps.finance.models import FinancialMonth


class FinanceError(Exception):
    """Raised on an invalid finance operation (e.g. editing a locked month)."""


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
