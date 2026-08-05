"""Small date helpers with no app dependencies.

``add_months`` began in ``features/compliance`` because expiry was only ever a
compliance concern. Activation now has to ask the same question — is this
medical still valid? — and core may not import from a feature
(``scripts/check_dependency_direction.py``), so the arithmetic lives here and
compliance imports it from core like everything else.
"""

from __future__ import annotations

import datetime as dt


def add_months(day: dt.date, months: int) -> dt.date:
    """Add whole months to a date, clamping the day of month.

    31 January plus one month is 28 (or 29) February, not an error and not
    3 March: a certificate issued on the 31st expires on the last day of the
    target month.
    """
    month_index = day.month - 1 + months
    year = day.year + month_index // 12
    month = month_index % 12 + 1
    next_month_first = dt.date(year + (month // 12), (month % 12) + 1, 1)
    last_day = (next_month_first - dt.timedelta(days=1)).day
    return dt.date(year, month, min(day.day, last_day))
