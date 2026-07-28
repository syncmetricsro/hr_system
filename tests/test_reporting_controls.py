"""Context for the shared period picker.

The interesting property is round-tripping: whatever a user selects has to come
back *selected* when the page re-renders, or the control silently disagrees with
the report beside it. That is the bug the client hit in the original filter -
picking a year and getting a month picker back.
"""

from __future__ import annotations

import datetime as dt

from django.http import QueryDict
from django.utils import translation

from core.reporting.controls import period_filter_context
from core.reporting.periods import GRANULARITIES, resolve_period

TODAY = dt.date(2026, 7, 14)


def _context(query: str, **kwargs):
    period = resolve_period(QueryDict(query), today=TODAY)
    return period_filter_context(period, today=TODAY, **kwargs)


def test_every_granularity_is_offered():
    context = _context("")
    assert [value for value, _label in context["granularities"]] == list(GRANULARITIES)


def test_a_selected_month_comes_back_ticked():
    context = _context("period=months&month=2026-03&month=2026-05")
    ticked = [m["value"] for m in context["selectable_months"] if m["selected"]]
    assert ticked == ["2026-03", "2026-05"]


def test_the_grid_opens_on_the_year_that_was_selected():
    """Selecting months in 2025 and getting a 2026 grid back would hide the
    user's own selection."""
    context = _context("period=months&month=2025-11&month=2025-12")
    assert context["months_year"] == 2025
    assert [m["value"] for m in context["selectable_months"] if m["selected"]] == [
        "2025-11",
        "2025-12",
    ]


def test_the_grid_always_offers_twelve_months():
    context = _context("")
    assert len(context["selectable_months"]) == 12


def test_month_labels_are_localised():
    with translation.override("en"):
        assert _context("")["selectable_months"][0]["label"] == "January"
    with translation.override("sk"):
        assert _context("")["selectable_months"][0]["label"] != "January"


def test_selectable_years_span_back_and_forward_newest_first():
    years = _context("")["selectable_years"]
    assert years[0] > years[-1]
    assert TODAY.year in years
    assert TODAY.year + 1 in years


def test_a_single_month_selection_prefills_the_month_input():
    assert _context("period=month&month=2026-02")["month_value"] == "2026-02"


def test_the_month_input_defaults_to_this_month_for_other_granularities():
    assert _context("period=year&year=2026")["month_value"] == "2026-07"


def test_this_week_is_offered_in_iso_form():
    assert _context("")["this_week"] == "2026-W29"


def test_extra_params_are_carried_through():
    """A page's other filters must survive a period change, or changing the
    month silently resets the supplier you were looking at."""
    context = _context("", extra_params={"supplier": "7"})
    assert context["extra_params"] == {"supplier": "7"}


def test_extra_params_default_to_empty_not_none():
    assert _context("")["extra_params"] == {}
