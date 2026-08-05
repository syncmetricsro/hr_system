from __future__ import annotations

from django.utils.translation import gettext as _

from core.accounts.permissions import Action, can
from core.ui.registry import flag_enabled
from features.payslips.models import Payslip


def net_payslip_series(request, people) -> dict | None:
    if not flag_enabled("payslips") or not can(request.user, Action.PAYSLIP_VIEW):
        return None
    rows = Payslip.objects.filter(person__in=people).only(
        "person_id", "period", "net_amount", "currency"
    )
    by_person: dict[int, dict] = {}
    for row in rows:
        by_person.setdefault(row.person_id, {})[row.period] = (
            row.net_amount,
            row.currency,
        )
    return {"label": _("Recorded net payslip"), "by_person": by_person}
