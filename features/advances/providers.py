"""Person finance-series contribution: cycle-keyed ledger totals.

The series value for a period is the net payroll withholding of that cycle
(Σ DEDUCT − Σ ADD over entries settled in the cycle, both from positive
magnitudes). Keyed by the existing ``cycle_key``, which maps 1:1 to a
calendar month, so core can align it with the calendar-month wage series.
"""

from __future__ import annotations

from decimal import Decimal

from django.utils.translation import gettext as _

from core.accounts.permissions import Action, can
from core.ui.registry import flag_enabled
from features.advances.models import LedgerEntry, PayEffect, SettlementStatus


def advances_cycle_series(request, person) -> dict | None:
    if not flag_enabled("advances") or not can(request.user, Action.LEDGER_VIEW):
        return None
    entries = (
        LedgerEntry.objects.filter(person=person)
        .exclude(cycle_key="")
        .exclude(settlement_status=SettlementStatus.CANCELLED)
        .exclude(pay_effect=PayEffect.NONE)
        .only("cycle_key", "amount", "pay_effect", "currency")
    )
    periods: dict[str, tuple[Decimal, str]] = {}
    for entry in entries:
        total, currency = periods.get(entry.cycle_key, (Decimal("0"), entry.currency))
        if entry.pay_effect == PayEffect.DEDUCT:
            total += entry.amount
        else:
            total -= entry.amount
        periods[entry.cycle_key] = (total, currency)
    return {"label": _("Advances & deductions"), "periods": periods}
