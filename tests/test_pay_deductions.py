"""Showing a worker what was taken off their gross wage.

The customer could not demonstrate this because the product refused to do it:
gross wage and net payslip were recorded as two independent source values and
nothing joined them (C-Q17). Since 2026-08-04 the overview also shows the
office's **own** ledger deductions and a derived *after deductions* column.

The line these tests defend is what that column is **not**. It is arithmetic on
figures this office typed in — gross minus advances, damage and equipment. It is
not net pay: no tax, no levy, no jurisdiction. The separately recorded payslip
keeps its own column precisely so the two can disagree visibly.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

import pytest
from django.conf import settings

# All three apps are needed: the deduction column comes from advances, the
# gross figure from wage_ledger, and the comparison column from payslips.
# Jober installs none of them, so guard on the whole set rather than one.
_REQUIRED = ("features.advances", "features.wage_ledger", "features.payslips")
if any(app not in settings.INSTALLED_APPS for app in _REQUIRED):
    pytest.skip(
        "the CorvinumEU pay stack is not installed for this client",
        allow_module_level=True,
    )

from django.urls import reverse  # noqa: E402

from core.people.models import Person  # noqa: E402
from features.advances.models import EntryType, LedgerCategory  # noqa: E402
from features.advances.services import (  # noqa: E402
    LedgerError,
    cycle_for,
    include_cycle,
    record_entry,
)
from features.payslips.services import record_payslip  # noqa: E402
from features.wage_ledger.services import record_wage  # noqa: E402

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager(django_user_model):
    return django_user_model.objects.create_user(
        email="pay-mgr@demo.corvinum.test", password="x", role="manager"
    )


@pytest.fixture
def person():
    return Person.objects.create(first_name="Fictional", last_name="Worker")


def _cells(client, person):
    response = client.get(reverse("person_detail", args=[person.pk]))
    return response.context["person_finance_overview"]["rows"][0]["cells"]


# --- the demo this exists for ----------------------------------------------


def test_gross_minus_ledger_deductions_is_shown(client, person, manager):
    """The walkthrough in the Corvinum runbook, as a test."""
    record_wage(person, period="2026-07", gross_amount="1800", actor=manager)
    record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.CASH_ADVANCE,
        amount="200",
        actor=manager,
        entry_date=dt.date(2026, 7, 10),
    )
    record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.EQUIPMENT,
        amount="50",
        actor=manager,
        entry_date=dt.date(2026, 7, 18),
    )
    record_payslip(person, period="2026-07", net_amount="1512.40", actor=manager)
    client.force_login(manager)

    gross, deducted, after, payslip = _cells(client, person)
    assert gross["amount"] == Decimal("1800.00")
    assert deducted["amount"] == Decimal("250.00")
    assert after["amount"] == Decimal("1550.00")
    assert after["derived"] is True
    # The payslip is *not* the derived figure, and must not be overwritten by
    # it — the gap is statutory deductions, which this product does not model.
    assert payslip["amount"] == Decimal("1512.40")
    assert payslip["derived"] is False


def test_a_pay_addition_reduces_what_was_deducted(client, person, manager):
    """Both directions land in one column, so it reads as a single number."""
    record_wage(person, period="2026-07", gross_amount="1800", actor=manager)
    record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.CASH_ADVANCE,
        amount="300",
        actor=manager,
        entry_date=dt.date(2026, 7, 10),
    )
    record_entry(
        person,
        entry_type=EntryType.PAY_ADDITION,
        category=LedgerCategory.TRAVEL_FUEL,
        amount="120",
        actor=manager,
        entry_date=dt.date(2026, 7, 12),
    )
    client.force_login(manager)

    _gross, deducted, after, _payslip = _cells(client, person)
    assert deducted["amount"] == Decimal("180.00")
    assert after["amount"] == Decimal("1620.00")


def test_the_derived_column_is_absent_without_a_gross_figure(client, person, manager):
    """Nothing to subtract from is not the same as zero, and printing a
    negative 'after deductions' with no wage recorded would be a lie."""
    record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.CASH_ADVANCE,
        amount="200",
        actor=manager,
        entry_date=dt.date(2026, 7, 10),
    )
    client.force_login(manager)

    cells = _cells(client, person)
    assert cells[2] is None, "after-deductions should be empty with no gross wage"


def test_deductions_are_grouped_by_calendar_month_not_by_cycle(
    client, person, manager
):
    """The settlement cycle runs 21st to 20th, but this table's other columns
    are calendar months. Mixing the two would silently misalign the rows."""
    record_wage(person, period="2026-07", gross_amount="1800", actor=manager)
    # The 25th settles in the August cycle but is still a July calendar entry.
    record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.CASH_ADVANCE,
        amount="90",
        actor=manager,
        entry_date=dt.date(2026, 7, 25),
    )
    client.force_login(manager)

    assert cycle_for(dt.date(2026, 7, 25)) == (2026, 8)
    _gross, deducted, after, _payslip = _cells(client, person)
    assert deducted["amount"] == Decimal("90.00")
    assert after["amount"] == Decimal("1710.00")


# --- recording an entry against the month it belongs to ---------------------


def test_the_entry_date_can_be_set_from_the_form(client, person, manager):
    """Without this the office could only ever record 'today', so a July
    deduction was impossible to enter in August — and impossible to demo."""
    client.force_login(manager)
    response = client.post(
        reverse("ledger_record"),
        {
            "person": person.pk,
            "entry_type": EntryType.PAY_DEDUCTION,
            "category": LedgerCategory.CASH_ADVANCE,
            "amount": "75",
            "entry_date": "2026-07-03",
            "note": "advance handed over on site",
        },
    )

    assert response.status_code == 302
    assert person.ledger_entries.get().entry_date == dt.date(2026, 7, 3)


def test_backdating_into_a_settled_cycle_is_refused(person, manager):
    """`include_cycle` sweeps a window once and the windows are disjoint, so an
    entry backdated into a swept window would be created OPEN and never picked
    up again — sitting forever in a period whose payroll has already gone out."""
    record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.CASH_ADVANCE,
        amount="100",
        actor=manager,
        entry_date=dt.date(2026, 7, 10),
    )
    include_cycle(2026, 7, actor=manager)

    with pytest.raises(LedgerError, match="2026-07"):
        record_entry(
            person,
            entry_type=EntryType.PAY_DEDUCTION,
            category=LedgerCategory.EQUIPMENT,
            amount="40",
            actor=manager,
            entry_date=dt.date(2026, 7, 12),
        )


def test_an_open_cycle_still_accepts_a_backdated_entry(person, manager):
    """The guard must not turn into 'no backdating at all' — recording last
    week's advance this week is the normal case."""
    entry = record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.CASH_ADVANCE,
        amount="60",
        actor=manager,
        entry_date=dt.date(2026, 7, 5),
    )
    assert entry.entry_date == dt.date(2026, 7, 5)


def test_a_reversal_is_never_blocked_by_the_settled_guard(person, manager):
    """Reversal is the sanctioned correction path for a settled cycle (C-Q5).
    If the guard caught reversals there would be no correction path at all."""
    original = record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.CASH_ADVANCE,
        amount="100",
        actor=manager,
        entry_date=dt.date(2026, 7, 10),
    )
    include_cycle(2026, 7, actor=manager)
    original.refresh_from_db()

    from features.advances.services import reverse_entry

    reversal = reverse_entry(original, actor=manager, reason="entered twice")
    assert reversal.pk and reversal.reversal_of_id == original.pk


@pytest.mark.parametrize(
    "day,expected",
    [
        (dt.date(2026, 7, 1), (2026, 7)),
        (dt.date(2026, 7, 20), (2026, 7)),
        (dt.date(2026, 7, 21), (2026, 8)),
        (dt.date(2026, 12, 21), (2027, 1)),  # the year boundary
    ],
)
def test_cycle_for_matches_the_21st_to_20th_window(day, expected):
    assert cycle_for(day) == expected
