"""The reusable period resolver (J7).

The client's complaint was specific: selecting a year collapsed back into a
month picker, so "the whole of 2026" could not be asked for. He also wanted
several months reported together. Both are covered here, along with the part
that is easy to get wrong - a *gapped* selection must stay gapped. Silently
widening January+March into January-through-March would be the same surprise
in the other direction.

No database: this module is pure date arithmetic, deliberately, so the three
surfaces that need it (warehouse, goods-receipt log, staff activity) can share
it without sharing a query.
"""

from __future__ import annotations

import datetime as dt

import pytest
from django.http import QueryDict
from django.utils import translation

from core.reporting.periods import (
    DAY,
    MONTH,
    WEEK,
    YEAR,
    Period,
    resolve_period,
)

TODAY = dt.date(2026, 7, 14)  # a Tuesday, ISO week 29


def _get(query: str) -> QueryDict:
    return QueryDict(query)


def _as_query(params: dict) -> QueryDict:
    """Rebuild a QueryDict from a period's `params`, the way the rendered
    control does - list values become repeated keys."""
    query = QueryDict("", mutable=True)
    for key, value in params.items():
        if isinstance(value, list):
            query.setlist(key, value)
        else:
            query[key] = value
    return query


# --- the granularities the client named --------------------------------------


def test_day():
    period = resolve_period(_get("period=day&date=2026-07-14"), today=TODAY)
    assert period.kind == DAY
    assert period.ranges == ((dt.date(2026, 7, 14), dt.date(2026, 7, 14)),)


def test_week_covers_monday_to_sunday():
    period = resolve_period(_get("period=week&week=2026-W29"), today=TODAY)
    assert period.kind == WEEK
    assert period.ranges == ((dt.date(2026, 7, 13), dt.date(2026, 7, 19)),)


def test_month_ends_on_the_real_last_day():
    period = resolve_period(_get("period=month&month=2026-02"), today=TODAY)
    assert period.ranges == ((dt.date(2026, 2, 1), dt.date(2026, 2, 28)),)


def test_february_in_a_leap_year():
    period = resolve_period(_get("period=month&month=2024-02"), today=TODAY)
    assert period.ranges == ((dt.date(2024, 2, 1), dt.date(2024, 2, 29)),)


def test_year_is_one_period_not_twelve():
    """The actual complaint: selecting a year collapsed back into months."""
    period = resolve_period(_get("period=year&year=2026"), today=TODAY)
    assert period.kind == YEAR
    assert period.ranges == ((dt.date(2026, 1, 1), dt.date(2026, 12, 31)),)
    assert period.is_contiguous


# --- several months, the part with a trap ------------------------------------


def test_adjacent_months_merge_into_one_range():
    period = resolve_period(
        _get("period=months&month=2026-01&month=2026-02&month=2026-03"), today=TODAY
    )
    assert period.ranges == ((dt.date(2026, 1, 1), dt.date(2026, 3, 31)),)
    assert period.is_contiguous


def test_a_gapped_selection_stays_gapped():
    """January and March must not quietly become January-through-March."""
    period = resolve_period(
        _get("period=months&month=2026-01&month=2026-03"), today=TODAY
    )
    assert period.ranges == (
        (dt.date(2026, 1, 1), dt.date(2026, 1, 31)),
        (dt.date(2026, 3, 1), dt.date(2026, 3, 31)),
    )
    assert not period.is_contiguous


def test_months_merge_across_a_year_boundary():
    period = resolve_period(
        _get("period=months&month=2025-12&month=2026-01"), today=TODAY
    )
    assert period.ranges == ((dt.date(2025, 12, 1), dt.date(2026, 1, 31)),)


def test_months_are_order_and_duplicate_insensitive():
    period = resolve_period(
        _get("period=months&month=2026-03&month=2026-01&month=2026-03"), today=TODAY
    )
    assert period.ranges == (
        (dt.date(2026, 1, 1), dt.date(2026, 1, 31)),
        (dt.date(2026, 3, 1), dt.date(2026, 3, 31)),
    )


def test_one_month_selected_under_months_behaves_as_a_month():
    period = resolve_period(_get("period=months&month=2026-05"), today=TODAY)
    assert period.kind == MONTH
    assert period.ranges == ((dt.date(2026, 5, 1), dt.date(2026, 5, 31)),)


# --- filter_q ----------------------------------------------------------------


def test_filter_q_has_one_clause_per_range():
    contiguous = resolve_period(
        _get("period=months&month=2026-01&month=2026-02"), today=TODAY
    )
    gapped = resolve_period(
        _get("period=months&month=2026-01&month=2026-03"), today=TODAY
    )
    assert len(contiguous.filter_q("occurred_on").children) == 1
    assert len(gapped.filter_q("occurred_on").children) == 2


def test_filter_q_names_the_callers_own_field():
    """The resolver knows nothing about any model; the caller says which
    date column this period applies to."""
    period = resolve_period(_get("period=month&month=2026-07"), today=TODAY)
    assert "registered_on__range" in str(period.filter_q("registered_on"))


# --- bad input falls back rather than raising --------------------------------


@pytest.mark.parametrize(
    "query",
    [
        "",
        "period=nonsense",
        "period=month&month=2026-13",
        "period=month&month=not-a-month",
        "period=month",
        "period=day&date=2026-02-30",
        "period=day&date=yesterday",
        "period=week&week=2026-W99",
        "period=week&week=garbage",
        "period=year&year=twenty-six",
        "period=months&month=nope",
    ],
)
def test_unparseable_input_falls_back_to_the_current_month(query):
    """These values come from a query string a user can edit by hand. A report
    that 500s on a typo is worse than one that shows this month."""
    period = resolve_period(_get(query), today=TODAY)
    assert period.kind == MONTH
    assert period.ranges == ((dt.date(2026, 7, 1), dt.date(2026, 7, 31)),)


# --- labels ------------------------------------------------------------------


def test_a_gapped_label_names_every_selected_month():
    """The label is the only place a user can see February was left out."""
    with translation.override("en"):
        period = resolve_period(
            _get("period=months&month=2026-01&month=2026-03"), today=TODAY
        )
        assert "January" in period.label
        assert "March" in period.label
        assert "February" not in period.label


def test_year_label_is_just_the_year():
    period = resolve_period(_get("period=year&year=2026"), today=TODAY)
    assert period.label == "2026"


# --- params round-trip so the control can re-render itself -------------------


@pytest.mark.parametrize(
    "query",
    [
        "period=day&date=2026-07-14",
        "period=week&week=2026-W29",
        "period=month&month=2026-07",
        "period=year&year=2026",
    ],
)
def test_params_round_trip(query):
    """Feeding a period's own `params` back in must reproduce it - that is what
    the rendered control does on every submit."""
    first = resolve_period(_get(query), today=TODAY)
    second = resolve_period(_as_query(first.params), today=TODAY)
    assert first.params == second.params
    assert first.ranges == second.ranges


def test_gapped_months_round_trip():
    first = resolve_period(
        _get("period=months&month=2026-01&month=2026-03"), today=TODAY
    )
    second = resolve_period(_as_query(first.params), today=TODAY)
    assert second.ranges == first.ranges
    assert not second.is_contiguous


def test_months_params_keep_every_selection():
    period = resolve_period(
        _get("period=months&month=2026-01&month=2026-03"), today=TODAY
    )
    assert period.params["month"] == ["2026-01", "2026-03"]


def test_start_and_end_span_the_whole_selection():
    period = resolve_period(
        _get("period=months&month=2026-01&month=2026-03"), today=TODAY
    )
    assert period.start == dt.date(2026, 1, 1)
    assert period.end == dt.date(2026, 3, 31)


def test_period_is_immutable():
    """Periods get passed into services and templates; a shared mutable one
    would be a bug that only shows up under load."""
    period = resolve_period(_get("period=year&year=2026"), today=TODAY)
    with pytest.raises(Exception):
        period.kind = DAY  # type: ignore[misc]
    assert isinstance(period, Period)
