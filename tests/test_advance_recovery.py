from __future__ import annotations

import datetime as dt
from decimal import Decimal

import pytest
from django.conf import settings

if "features.wage_ledger" not in settings.INSTALLED_APPS:
    pytest.skip(
        "features.wage_ledger is not installed for this client",
        allow_module_level=True,
    )

from django.contrib import admin  # noqa: E402
from django.core.exceptions import ValidationError  # noqa: E402
from django.db import IntegrityError, transaction  # noqa: E402
from django.urls import reverse  # noqa: E402

from core.audit.models import AuditEvent  # noqa: E402
from core.people.models import Person  # noqa: E402
from features.advances.models import (  # noqa: E402
    EntryType,
    LedgerCategory,
    LedgerEntry,
    SettlementStatus,
)
from features.advances.services import record_entry  # noqa: E402
from features.payslips.models import Payslip  # noqa: E402
from features.wage_ledger.models import AdvanceRecovery, WageEntry  # noqa: E402
from features.wage_ledger.services import (  # noqa: E402
    assign_recovery,
    compute_net,
    is_deferred,
    record_wage,
    suggested_recovery_period,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def staff(django_user_model):
    return {
        role: django_user_model.objects.create_user(
            email=f"recovery-{role}@demo.corvinum.test", password="x", role=role
        )
        for role in ("manager", "observer", "coordinator", "recruiter")
    }


@pytest.fixture
def person():
    return Person.objects.create(first_name="Fictional", last_name="Worker")


def _advance(person, *, amount="100.00", entry_date, actor=None) -> LedgerEntry:
    return record_entry(
        person,
        entry_type=EntryType.CASH_ADVANCE,
        category=LedgerCategory.CASH_ADVANCE,
        amount=Decimal(amount),
        entry_date=entry_date,
        actor=actor,
    )


# --- 1. Suggested-period rule -------------------------------------------------

@pytest.mark.parametrize(
    ("entry_date", "expected", "deferred"),
    [
        (dt.date(2026, 7, 1), "2026-07", False),
        (dt.date(2026, 7, 20), "2026-07", False),
        (dt.date(2026, 7, 21), "2026-08", True),
        (dt.date(2026, 7, 31), "2026-08", True),
        (dt.date(2026, 12, 20), "2026-12", False),
        (dt.date(2026, 12, 21), "2027-01", True),
    ],
)
def test_suggested_recovery_period(entry_date, expected, deferred):
    suggested = suggested_recovery_period(entry_date)
    assert suggested == expected
    assert is_deferred(entry_date, suggested) is deferred


def test_assignment_rejects_wage_month_before_cycle_end(person, staff):
    advance = _advance(person, entry_date=dt.date(2026, 7, 21))
    with pytest.raises(ValidationError):
        assign_recovery(advance, period="2026-07", actor=staff["manager"])
    advance.refresh_from_db()
    assert advance.settlement_status == SettlementStatus.OPEN

    later = assign_recovery(advance, period="2026-09", actor=staff["manager"])
    assert later.recovered_in_period == "2026-09"


# --- 2. Assignment is audited and drives settlement via advances --------------

def test_assignment_audited_and_settles_via_advances_service(person, staff):
    advance = _advance(person, entry_date=dt.date(2026, 7, 21))
    recovery = assign_recovery(advance, actor=staff["manager"])

    assert recovery.recovered_in_period == "2026-08"
    assert recovery.amount == advance.amount
    assert recovery.is_deferred is True

    advance.refresh_from_db()
    assert advance.settlement_status == SettlementStatus.INCLUDED_IN_CYCLE
    assert advance.cycle_key == "2026-08"

    assigned = AuditEvent.objects.get(action="wage.recovery_assigned")
    assert assigned.metadata["advance_id"] == advance.pk
    assert assigned.metadata["period"] == "2026-08"
    assert assigned.metadata["deferred"] is True
    assert AuditEvent.objects.filter(action="ledger.entry_included").exists()


def test_assignment_guards(person, staff):
    deduction = record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.EQUIPMENT,
        amount=Decimal("40.00"),
        entry_date=dt.date(2026, 7, 3),
    )
    with pytest.raises(ValidationError):
        assign_recovery(deduction, actor=staff["manager"])

    advance = _advance(person, entry_date=dt.date(2026, 7, 3))
    assign_recovery(advance, actor=staff["manager"])
    with pytest.raises(ValidationError):
        assign_recovery(advance, actor=staff["manager"])

    other = _advance(person, entry_date=dt.date(2026, 7, 4))
    with pytest.raises(ValidationError):
        assign_recovery(other, amount=Decimal("150.00"), actor=staff["manager"])
    with pytest.raises(ValidationError):
        assign_recovery(other, amount=Decimal("0"), actor=staff["manager"])
    partial = assign_recovery(other, amount=Decimal("60.00"), actor=staff["manager"])
    assert partial.amount == Decimal("60.00")


# --- 3. One active recovery per advance ---------------------------------------

def test_one_active_recovery_per_advance_constraint(person):
    advance = _advance(person, entry_date=dt.date(2026, 7, 3))
    AdvanceRecovery.objects.create(
        advance=advance, recovered_in_period="2026-07", amount=Decimal("100.00")
    )
    with pytest.raises(IntegrityError), transaction.atomic():
        AdvanceRecovery.objects.create(
            advance=advance, recovered_in_period="2026-08", amount=Decimal("100.00")
        )
    # Inactive rows are exempt: the constraint is a drop away from partial
    # recovery, not a remodel.
    AdvanceRecovery.objects.create(
        advance=advance,
        recovered_in_period="2026-08",
        amount=Decimal("100.00"),
        is_active=False,
    )


# --- 4. Derived net -----------------------------------------------------------

def test_compute_net_mixed_entries_and_never_persisted(person, staff):
    record_wage(person, period="2026-07", gross_amount="1500.00", actor=staff["manager"])
    advance = _advance(person, entry_date=dt.date(2026, 7, 10))
    assign_recovery(advance, actor=staff["manager"])

    from features.advances.services import include_entry

    deduction = record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.EQUIPMENT,
        amount=Decimal("50.00"),
        entry_date=dt.date(2026, 7, 5),
    )
    include_entry(deduction, cycle_key="2026-07")
    addition = record_entry(
        person,
        entry_type=EntryType.PAY_ADDITION,
        category=LedgerCategory.OTHER,
        amount=Decimal("30.00"),
        entry_date=dt.date(2026, 7, 6),
    )
    include_entry(addition, cycle_key="2026-07")

    # 1500 gross − 100 recovered advance − 50 deduction + 30 addition
    assert compute_net(person, "2026-07") == Decimal("1380.00")
    assert compute_net(person, "2026-06") is None

    field_names = {field.name for field in WageEntry._meta.get_fields()}
    assert "net_amount" not in field_names
    assert "net" not in field_names


# --- 7. No admin side door for money models -----------------------------------

def test_money_models_have_no_admin_registration():
    for model in (WageEntry, AdvanceRecovery, LedgerEntry, Payslip):
        assert model not in admin.site._registry


# --- Recovery assignment view -------------------------------------------------

def test_recovery_assignment_view_permissions_and_flow(client, person, staff):
    advance = _advance(person, entry_date=dt.date(2026, 7, 22))

    client.force_login(staff["manager"])
    listing = client.get(reverse("wage_list"))
    assert listing.status_code == 200
    assert b"2026-08" in listing.content  # suggested month, flagged as deferred

    for role in ("observer", "coordinator", "recruiter"):
        client.force_login(staff[role])
        response = client.post(
            reverse("wage_recovery_assign"),
            {"advance": advance.pk, "period": "2026-08"},
        )
        assert response.status_code == 403

    client.force_login(staff["manager"])
    response = client.post(
        reverse("wage_recovery_assign"),
        {"advance": advance.pk, "period": "2026-08"},
    )
    assert response.status_code == 302
    recovery = AdvanceRecovery.objects.get(advance=advance)
    assert recovery.assigned_by == staff["manager"]
    assert recovery.recovered_in_period == "2026-08"
