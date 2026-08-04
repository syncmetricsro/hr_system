from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from django.utils.translation import gettext as _

from core.accounts.permissions import Action, can
from core.ui.registry import flag_enabled
from features.advances.models import LedgerEntry, PayEffect, SettlementStatus


def ledger_deduction_series(request, person) -> dict | None:
    """What this office took off the worker's pay, per calendar month.

    Keyed by the **entry date's** calendar month rather than by the 21st-to-20th
    settlement cycle, because this column sits beside a gross wage and a payslip
    that are both calendar-month figures, and a table whose columns mean
    different periods is worse than no table.

    Cancelled entries are excluded — they were never acted on. Reversals are
    not: a reversal is a real ``PAY_ADDITION`` and nets itself off through the
    additions below, which is exactly what the office wants to see.
    """
    if not flag_enabled("advances") or not can(request.user, Action.LEDGER_VIEW):
        return None

    rows = (
        LedgerEntry.objects.filter(person=person)
        .exclude(settlement_status=SettlementStatus.CANCELLED)
        .exclude(pay_effect=PayEffect.NONE)
        .only("entry_date", "amount", "currency", "pay_effect")
    )
    totals: dict[str, Decimal] = defaultdict(Decimal)
    currencies: dict[str, str] = {}
    for row in rows:
        period = f"{row.entry_date.year:04d}-{row.entry_date.month:02d}"
        # Stored positive; pay_effect carries the direction. An addition
        # reduces the amount deducted, so the column stays a single number.
        if row.pay_effect == PayEffect.DEDUCT:
            totals[period] += row.amount
        else:
            totals[period] -= row.amount
        currencies.setdefault(period, row.currency)

    return {
        "label": _("Ledger deductions"),
        "periods": {
            period: (amount, currencies[period])
            for period, amount in totals.items()
            if amount
        },
    }
