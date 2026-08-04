from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from django.utils.translation import gettext as _

from core.accounts.permissions import Action, can
from core.ui.registry import flag_enabled
from features.advances.models import LedgerEntry, PayEffect, SettlementStatus
from features.advances.services import settling_cycle_key


def ledger_deduction_series(request, person) -> dict | None:
    """What this office took off the worker's pay, per calendar month.

    Keyed by **the payroll run that collects it**, not by the entry date's
    calendar month. An advance handed over on 25 July is recovered from the
    August pay, so showing it against July described a payslip that had already
    been paid — the reported problem this column now answers correctly
    (ADR 0032). Runs are keyed by their end month, so the key still lines up
    with the gross wage and payslip columns beside it.

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
        .only("entry_date", "amount", "currency", "pay_effect", "cycle_key")
    )
    totals: dict[str, Decimal] = defaultdict(Decimal)
    currencies: dict[str, str] = {}
    for row in rows:
        period = settling_cycle_key(row)
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
