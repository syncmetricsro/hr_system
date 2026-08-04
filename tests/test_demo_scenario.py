from __future__ import annotations

import pytest
from django.apps import apps as django_apps

if not django_apps.is_installed("features.profitability"):
    pytest.skip(
        "features.profitability is not installed for this client",
        allow_module_level=True,
    )


import pytest
from django.core.management import call_command

from core.ui.registry import flag_enabled
from features.blacklist.models import BlacklistCaseStatus, MatchFingerprint
from features.blacklist.services import check_match
from features.compliance.services import compliance_alerts
from features.profitability.models import FinancialMonth
from features.logistics.models import (
    DeductionReviewStatus,
    EquipmentIssue,
    EquipmentStockMovement,
    RoomAssignment,
)
from core.projects.models import TrialAssignment, TrialOutcome
from core.people.models import LifecycleStatus, Person
from core.people.services import inactive_by_reason

pytestmark = pytest.mark.django_db


def _seed():
    # The scenario builds on the standard demo seeds.
    call_command("seed_demo")
    call_command("seed_people")
    call_command("seed_logistics")
    call_command("seed_finance")
    call_command("seed_demo_scenario")


def test_scenario_populates_every_module():
    _seed()

    # Finance totals are recomputed from the line items, never stored ahead of
    # them - so assert that relationship rather than a hardcoded figure, which
    # is what previously broke when the seed's 2025 tail was rewritten.
    from decimal import Decimal

    month = FinancialMonth.objects.get(project__code="DHLBA", year=2025, month=11)
    assert month.line_items.exists()
    costs = sum(
        (i.amount for i in month.line_items.all() if i.category.kind == "cost"),
        Decimal("0"),
    )
    revenues = sum(
        (i.amount for i in month.line_items.all() if i.category.kind == "revenue"),
        Decimal("0"),
    )
    assert month.cost == costs
    assert month.revenue == revenues
    assert month.net == revenues - costs
    # The 2025 tail must carry the same category depth as 2026, not a stub.
    assert month.line_items.count() >= 8

    # Equipment: one issued item flagged for the review queue.
    assert EquipmentIssue.objects.filter(
        review_status=DeductionReviewStatus.PENDING
    ).exists()
    assert EquipmentStockMovement.objects.filter(movement_type="receipt").exists()
    # Returns are per-client (J6). Jober retired them, so the scenario no
    # longer seeds a returned helmet there - seeding one would leave a worker
    # holding items they had no way to return. Clients that keep returns must
    # still get both dispositions, so the demo exercises restock and retire.
    if flag_enabled("equipment_returns"):
        assert EquipmentIssue.objects.filter(return_disposition="restock").exists()
        assert EquipmentIssue.objects.filter(return_disposition="retire").exists()
    else:
        assert not EquipmentIssue.objects.exclude(return_disposition="").exists()

    # Inactive-by-reason has a named bucket (not just "No reason").
    labels = {row["label"] for row in inactive_by_reason()}
    assert "Sick" in labels

    # A blacklisted person exists with an active fingerprint, and the demo ID matches.
    blocked = Person.objects.get(first_name="Ivan", last_name="Zablokovaný")
    assert blocked.lifecycle_status == LifecycleStatus.BLACKLISTED
    assert MatchFingerprint.objects.filter(person=blocked, is_active=True).exists()
    assert check_match("SK-DEMO-BL-001").exists()

    # A proposed case is waiting in the manager queue.
    from features.blacklist.models import BlacklistCase

    assert BlacklistCase.objects.filter(status=BlacklistCaseStatus.PROPOSED).exists()

    # A compliance alert fires (expiring certificate and/or missing medical).
    assert compliance_alerts() != []

    # Olha has a phone (SMS panel).
    assert Person.objects.get(first_name="Olha", last_name="Kovalenko").phone

    # Operational workspaces contain records produced by their real services.
    assert TrialAssignment.objects.filter(outcome=TrialOutcome.PENDING).exists()
    assert RoomAssignment.objects.filter(worker_payment_monthly__gt=0).exists()
    assert Person.objects.get(first_name="Mira", last_name="Novakova").date_of_birth


def test_scenario_is_idempotent():
    _seed()
    call_command("seed_demo_scenario")  # second run
    call_command("seed_demo_scenario")  # third run
    # No duplicate blacklisted person / fingerprints / flagged items.
    assert (
        Person.objects.filter(first_name="Ivan", last_name="Zablokovaný").count() == 1
    )
    assert MatchFingerprint.objects.filter(is_active=True).count() == 1
    assert (
        EquipmentIssue.objects.filter(
            review_status=DeductionReviewStatus.PENDING
        ).count()
        == 1
    )


def test_demo_sms_phone_env_overrides_olha(monkeypatch, django_user_model):
    """DEMO_SMS_PHONE (Doppler) points Olha at the presenter-visible Twilio
    number; the seed is idempotent and re-applies on change."""
    from django.core.management import call_command

    monkeypatch.setenv("DEMO_SMS_PHONE", "+15005550006")
    call_command("seed_demo")
    call_command("seed_people")
    call_command("seed_logistics")
    call_command("seed_demo_scenario")
    from core.people.models import Person

    olha = Person.objects.get(first_name="Olha", last_name="Kovalenko")
    assert olha.phone == "+15005550006"
