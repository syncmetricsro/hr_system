"""Reports contribution of the finance/profitability feature."""

from __future__ import annotations

from apps.accounts.permissions import Action
from apps.accounts.permissions import can as user_can
from apps.core.registry import flag_enabled
from apps.finance.services import company_totals


def company_totals_panel(request):
    if not flag_enabled("profitability"):
        return None
    if not user_can(request.user, Action.FINANCE_VIEW_SUMMARY):
        return None
    return {"finance": company_totals()}
