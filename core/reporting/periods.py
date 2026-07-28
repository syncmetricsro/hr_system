"""Reusable reporting periods (J7).

Three surfaces need the same granularities and the fix list is explicit that
they must not be implemented three times: the warehouse report (J7), the
goods-receipt log (J5) and staff activity statistics (J2). The client asked for
day, week, month, several months at once, and a full year.

**Several months means several months.** A selection of January and March
resolves to two disjoint ranges, not to January-through-March; the whole point
of the request was that picking a year stops collapsing back into months, and
quietly widening a gapped selection would be the same class of surprise. Ranges
that happen to touch are merged, so a contiguous run costs one range and one
`BETWEEN`.

Nothing here touches the database. `filter_q()` hands callers a `Q` for
whichever date field they store, so a period can filter movements, receipts,
person-creation events or room assignments without this module knowing about
any of them.

Bad input resolves to the current month rather than raising: these values come
from a query string a user can edit, and a report that 500s on a typo is worse
than one that shows this month.
"""

from __future__ import annotations

import calendar
import datetime as dt
from dataclasses import dataclass, field

from django.db.models import Q
from django.utils import formats, timezone
from django.utils.translation import gettext_lazy as _

DAY = "day"
WEEK = "week"
MONTH = "month"
MONTHS = "months"
YEAR = "year"

#: Order matters - it is the order the picker renders.
GRANULARITIES = (DAY, WEEK, MONTH, MONTHS, YEAR)

GRANULARITY_LABELS = {
    DAY: _("Day"),
    WEEK: _("Week"),
    MONTH: _("Month"),
    MONTHS: _("Several months"),
    YEAR: _("Year"),
}


@dataclass(frozen=True)
class Period:
    """One or more inclusive date ranges, plus how to re-render the control."""

    kind: str
    ranges: tuple[tuple[dt.date, dt.date], ...]
    label: str
    params: dict = field(default_factory=dict)

    @property
    def start(self) -> dt.date:
        return self.ranges[0][0]

    @property
    def end(self) -> dt.date:
        return self.ranges[-1][1]

    @property
    def is_contiguous(self) -> bool:
        """False when the selection has gaps - a caller computing anything
        span-based (an opening balance, a rate per day) needs to know."""
        return len(self.ranges) == 1

    def filter_q(self, field_name: str) -> Q:
        """A ``Q`` over ``field_name`` covering every range in this period."""
        query = Q()
        for start, end in self.ranges:
            query |= Q(**{f"{field_name}__range": (start, end)})
        return query

    def __str__(self) -> str:
        return self.label


def _month_bounds(year: int, month: int) -> tuple[dt.date, dt.date]:
    return (
        dt.date(year, month, 1),
        dt.date(year, month, calendar.monthrange(year, month)[1]),
    )


def _merge(ranges: list[tuple[dt.date, dt.date]]) -> tuple:
    """Sort and coalesce ranges that touch or overlap.

    January+February become one range so the common contiguous case costs a
    single BETWEEN, while January+March stay two and `is_contiguous` stays
    honest about it.
    """
    merged: list[list[dt.date]] = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1] + dt.timedelta(days=1):
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return tuple((start, end) for start, end in merged)


def _month_label(day: dt.date) -> str:
    return formats.date_format(day, "YEAR_MONTH_FORMAT")


def _parse_month(value: str) -> tuple[int, int] | None:
    try:
        year, month = value.split("-", 1)
        year, month = int(year), int(month)
    except (AttributeError, TypeError, ValueError):
        return None
    if not (1 <= month <= 12) or not (dt.MINYEAR <= year <= dt.MAXYEAR):
        return None
    return year, month


def _current_month(today: dt.date) -> Period:
    start, end = _month_bounds(today.year, today.month)
    return Period(
        kind=MONTH,
        ranges=((start, end),),
        label=_month_label(start),
        params={"period": MONTH, "month": f"{today:%Y-%m}"},
    )


def _resolve_day(params, today: dt.date) -> Period | None:
    raw = (params.get("date") or "").strip()
    try:
        day = dt.date.fromisoformat(raw)
    except ValueError:
        return None
    return Period(
        kind=DAY,
        ranges=((day, day),),
        label=formats.date_format(day, "DATE_FORMAT"),
        params={"period": DAY, "date": day.isoformat()},
    )


def _resolve_week(params, today: dt.date) -> Period | None:
    raw = (params.get("week") or "").strip()
    try:
        year_part, week_part = raw.split("-W", 1)
        year, week = int(year_part), int(week_part)
        monday = dt.date.fromisocalendar(year, week, 1)
    except (TypeError, ValueError):
        return None
    return Period(
        kind=WEEK,
        ranges=((monday, monday + dt.timedelta(days=6)),),
        label=_("Week %(week)s, %(year)s") % {"week": week, "year": year},
        params={"period": WEEK, "week": f"{year}-W{week:02d}"},
    )


def _resolve_month(params, today: dt.date) -> Period | None:
    parsed = _parse_month((params.get("month") or "").strip())
    if parsed is None:
        return None
    year, month = parsed
    start, end = _month_bounds(year, month)
    return Period(
        kind=MONTH,
        ranges=((start, end),),
        label=_month_label(start),
        params={"period": MONTH, "month": f"{year:04d}-{month:02d}"},
    )


def _resolve_months(params, today: dt.date) -> Period | None:
    getlist = getattr(params, "getlist", None)
    if getlist:
        raw_values = getlist("month")
    else:
        # A plain mapping (a service call, a test) may hold either one value or
        # an already-unpacked list; QueryDict is not the only caller.
        raw = params.get("month")
        raw_values = list(raw) if isinstance(raw, (list, tuple)) else [raw]
    parsed = sorted(
        {p for p in (_parse_month((v or "").strip()) for v in raw_values) if p}
    )
    if not parsed:
        return None
    if len(parsed) == 1:
        return _resolve_month(
            {"month": f"{parsed[0][0]:04d}-{parsed[0][1]:02d}"}, today
        )
    ranges = _merge([_month_bounds(year, month) for year, month in parsed])
    return Period(
        kind=MONTHS,
        ranges=ranges,
        # Every selected month is named, gaps included: the label is the only
        # place a user can see that February was left out.
        label=", ".join(_month_label(dt.date(y, m, 1)) for y, m in parsed),
        params={
            "period": MONTHS,
            "month": [f"{year:04d}-{month:02d}" for year, month in parsed],
        },
    )


def _resolve_year(params, today: dt.date) -> Period | None:
    try:
        year = int((params.get("year") or "").strip())
    except (TypeError, ValueError):
        return None
    if not (dt.MINYEAR <= year <= dt.MAXYEAR):
        return None
    return Period(
        kind=YEAR,
        ranges=((dt.date(year, 1, 1), dt.date(year, 12, 31)),),
        # A year stays one period; the client's complaint was that selecting a
        # year collapsed back into a month picker.
        label=str(year),
        params={"period": YEAR, "year": str(year)},
    )


_RESOLVERS = {
    DAY: _resolve_day,
    WEEK: _resolve_week,
    MONTH: _resolve_month,
    MONTHS: _resolve_months,
    YEAR: _resolve_year,
}


def resolve_period(params, *, today: dt.date | None = None) -> Period:
    """Read a period out of query parameters, falling back to this month.

    ``params`` is normally ``request.GET``; any mapping works, and ``getlist``
    is used when present so several ``month=`` values can be selected.
    """
    today = today or timezone.localdate()
    resolver = _RESOLVERS.get((params.get("period") or "").strip())
    if resolver is None:
        return _current_month(today)
    return resolver(params, today) or _current_month(today)
