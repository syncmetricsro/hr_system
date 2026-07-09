"""Reports contribution of the finance/profitability feature."""

from __future__ import annotations

from core.accounts.permissions import Action
from core.accounts.permissions import can as user_can
from core.ui.registry import flag_enabled
from features.finance.services import company_totals


def company_totals_panel(request):
    if not flag_enabled("profitability"):
        return None
    if not user_can(request.user, Action.FINANCE_VIEW_SUMMARY):
        return None
    return {"finance": company_totals()}
