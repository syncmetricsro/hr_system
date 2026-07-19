from __future__ import annotations

from django.utils.translation import gettext as _

from core.accounts.permissions import Action, can
from core.ui.registry import flag_enabled
from features.payslips.models import Payslip


def net_payslip_series(request, person) -> dict | None:
    if not flag_enabled("payslips") or not can(request.user, Action.PAYSLIP_VIEW):
        return None
    rows = Payslip.objects.filter(person=person).only("period", "net_amount", "currency")
    return {
        "label": _("Net payslip"),
        "kind": "recorded_net",
        "periods": {row.period: (row.net_amount, row.currency) for row in rows},
    }
