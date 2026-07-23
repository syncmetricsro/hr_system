"""Reports contribution of the finance/profitability feature."""

from __future__ import annotations

from core.accounts.permissions import Action
from core.accounts.permissions import can as user_can
from core.ui.chart_data import net_bar_payload
from core.ui.registry import flag_enabled
from features.finance.services import company_totals, margin_pct, regional_totals


def company_totals_panel(request):
    if not flag_enabled("profitability"):
        return None
    if not user_can(request.user, Action.FINANCE_VIEW_SUMMARY):
        return None
    totals = company_totals()
    margin = margin_pct(totals)
    regions = regional_totals()
    return {
        "finance": totals,
        "margin_pct": margin,
        "gauge_chart_data": {**totals, "margin_pct": margin},
        "regional_chart_data": net_bar_payload(regions, label_key="region"),
    }
