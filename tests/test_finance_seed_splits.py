"""The demo finance seed's split tables must sum to exactly 1.00.

``recompute_month`` (features/finance/services.py) derives a month's revenue
and cost *from its line items*, so the figures in MONTHLY_DATA/PRIOR_YEAR_DATA
are only the initial record - the line items are what survive. A split that
sums to 0.98 therefore does not raise anything; it silently seeds a month 2%
cheaper than the table says, and the demo quietly shows wrong numbers.

Cheap to assert, and the kind of thing that only bites when someone edits a
fraction months later.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from features.finance.management.commands.seed_finance import (
    COST_SPLIT,
    MONTHLY_DATA,
    PRIOR_YEAR_DATA,
    REVENUE_SPLIT,
)

ONE = Decimal("1.00")


@pytest.mark.parametrize("code", sorted(COST_SPLIT))
def test_cost_split_sums_to_exactly_one(code):
    assert sum(f for _, f in COST_SPLIT[code]) == ONE


@pytest.mark.parametrize("code", sorted(REVENUE_SPLIT))
def test_revenue_split_sums_to_exactly_one(code):
    assert sum(f for _, f in REVENUE_SPLIT[code]) == ONE


def test_every_seeded_project_has_both_splits():
    """A project in the monthly tables with no split would raise KeyError at
    seed time - catch it here rather than in front of the client."""
    seeded = set(MONTHLY_DATA) | set(PRIOR_YEAR_DATA)
    assert seeded <= set(COST_SPLIT), seeded - set(COST_SPLIT)
    assert seeded <= set(REVENUE_SPLIT), seeded - set(REVENUE_SPLIT)


def test_both_years_cover_the_same_projects():
    """The year-on-year comparison is only honest if 2025 and 2026 contain the
    same six projects - a partial 2025 is what this backfill replaced."""
    assert set(PRIOR_YEAR_DATA) == set(MONTHLY_DATA)


def test_prior_year_sits_below_the_january_2026_level():
    """The 2025 tail should read as 'slightly smaller, then growth into 2026',
    not as a discontinuity."""
    for code, rows in PRIOR_YEAR_DATA.items():
        december = Decimal(dict((m, r) for m, r, _c in rows)[12])
        january = Decimal(next(r for m, r, _c in MONTHLY_DATA[code] if m == 1))
        # RLS is the deliberately declining contract, so it runs the other way.
        if code == "RLS":
            assert december > january, code
        else:
            assert december < january, code
