from __future__ import annotations

from django.utils.translation import gettext as _

from core.accounts.permissions import Action, can
from core.ui.registry import flag_enabled
from features.wage_ledger.models import WageEntry
from features.wage_ledger.services import compute_net


def gross_wage_series(request, person) -> dict | None:
    if not flag_enabled("wage_ledger") or not can(request.user, Action.WAGE_VIEW):
        return None
    rows = WageEntry.objects.filter(person=person).only(
        "period", "gross_amount", "currency"
    )
    return {
        "label": _("Gross wage"),
        "periods": {row.period: (row.gross_amount, row.currency) for row in rows},
    }


def computed_net_series(request, person) -> dict | None:
    """Derived net per wage month (gross − recoveries/deductions + additions).
    Tagged ``computed_net`` so core can reconcile it against the recorded
    payslip net without knowing how either number is produced."""
    if not flag_enabled("wage_ledger") or not can(request.user, Action.WAGE_VIEW):
        return None
    periods = {}
    for row in WageEntry.objects.filter(person=person).only("period", "currency"):
        net = compute_net(person, row.period)
        if net is not None:
            periods[row.period] = (net, row.currency)
    return {"label": _("Computed net"), "kind": "computed_net", "periods": periods}
