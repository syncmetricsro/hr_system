from __future__ import annotations

from django.utils.translation import gettext as _

from core.accounts.permissions import Action, can
from core.ui.registry import flag_enabled
from features.wage_ledger.models import WageEntry


def gross_wage_series(request, person) -> dict | None:
    if not flag_enabled("wage_ledger") or not can(request.user, Action.WAGE_VIEW):
        return None
    rows = WageEntry.objects.filter(person=person).only(
        "period", "gross_amount", "currency"
    )
    return {
        "label": _("Recorded gross wage"),
        "periods": {row.period: (row.gross_amount, row.currency) for row in rows},
    }
