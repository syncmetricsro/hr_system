"""Template context for the shared period picker (J7).

Kept apart from `periods.py` so the resolver stays pure date arithmetic with no
opinion about how it is rendered. This module knows about the control; the
resolver knows about time.
"""

from __future__ import annotations

import datetime as dt

from django.utils import formats, timezone

from core.reporting.periods import (
    GRANULARITIES,
    GRANULARITY_LABELS,
    MONTH,
    MONTHS,
    Period,
)

#: How far back the year dropdowns reach. Five years covers the client's stated
#: need ("the whole of 2026") with room for history, without rendering a list
#: nobody scrolls.
YEARS_BACK = 5
YEARS_FORWARD = 1


def _selected_months(period: Period) -> set[str]:
    if period.kind == MONTHS:
        return set(period.params.get("month") or [])
    if period.kind == MONTH:
        value = period.params.get("month")
        return {value} if value else set()
    return set()


def period_filter_context(
    period: Period,
    *,
    today: dt.date | None = None,
    extra_params: dict | None = None,
) -> dict:
    """Everything `partials/period_filter.html` needs to render and re-render.

    `extra_params` are carried through as hidden inputs so a page's other
    filters (a project, a supplier) survive a period change.
    """
    today = today or timezone.localdate()
    selected = _selected_months(period)

    # The checkbox grid shows one year at a time; default to the year the
    # current selection lives in so a submitted selection comes back visible.
    months_year = today.year
    if selected:
        months_year = int(sorted(selected)[0].split("-")[0])

    selectable_months = [
        {
            "value": f"{months_year:04d}-{month:02d}",
            "label": formats.date_format(dt.date(months_year, month, 1), "F"),
            "selected": f"{months_year:04d}-{month:02d}" in selected,
        }
        for month in range(1, 13)
    ]

    iso_year, iso_week, _weekday = today.isocalendar()

    return {
        "period": period,
        "granularities": [
            (value, GRANULARITY_LABELS[value]) for value in GRANULARITIES
        ],
        "today_iso": today.isoformat(),
        "this_week": f"{iso_year}-W{iso_week:02d}",
        "month_value": period.params.get("month")
        if period.kind == MONTH
        else f"{today:%Y-%m}",
        "months_year": months_year,
        "selectable_months": selectable_months,
        "selectable_years": list(
            range(today.year - YEARS_BACK, today.year + YEARS_FORWARD + 1)
        )[::-1],
        "extra_params": extra_params or {},
    }
