from __future__ import annotations

import pytest
from django.core.management import call_command

from apps.blacklist.models import BlacklistCaseStatus, MatchFingerprint
from apps.blacklist.services import check_match
from apps.compliance.services import compliance_alerts
from apps.finance.models import FinancialMonth
from apps.logistics.models import DeductionReviewStatus, EquipmentIssue
from apps.people.models import LifecycleStatus, Person
from apps.people.services import inactive_by_reason

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

    # Finance line items + recomputed net (positive convention).
    from decimal import Decimal
    month = FinancialMonth.objects.get(project__code="DHLBA", year=2026, month=5)
    assert month.line_items.exists()
    assert month.cost == Decimal("12000")      # 9000 + 1200 + 1800, stored positive
    assert month.revenue == Decimal("18900")   # 18000 + 900
    assert month.net == Decimal("6900")        # revenue - cost

    # Equipment: one issued item flagged for the review queue.
    assert EquipmentIssue.objects.filter(review_status=DeductionReviewStatus.PENDING).exists()

    # Inactive-by-reason has a named bucket (not just "No reason").
    labels = {row["label"] for row in inactive_by_reason()}
    assert "Sick" in labels

    # A blacklisted person exists with an active fingerprint, and the demo ID matches.
    blocked = Person.objects.get(first_name="Ivan", last_name="Zablokovaný")
    assert blocked.lifecycle_status == LifecycleStatus.BLACKLISTED
    assert MatchFingerprint.objects.filter(person=blocked, is_active=True).exists()
    assert check_match("SK-DEMO-BL-001").exists()

    # A proposed case is waiting in the manager queue.
    from apps.blacklist.models import BlacklistCase
    assert BlacklistCase.objects.filter(status=BlacklistCaseStatus.PROPOSED).exists()

    # A compliance alert fires (expiring certificate and/or missing medical).
    assert compliance_alerts() != []

    # Olha has a phone (SMS panel).
    assert Person.objects.get(first_name="Olha", last_name="Kovalenko").phone


def test_scenario_is_idempotent():
    _seed()
    call_command("seed_demo_scenario")  # second run
    call_command("seed_demo_scenario")  # third run
    # No duplicate blacklisted person / fingerprints / flagged items.
    assert Person.objects.filter(first_name="Ivan", last_name="Zablokovaný").count() == 1
    assert MatchFingerprint.objects.filter(is_active=True).count() == 1
    assert EquipmentIssue.objects.filter(review_status=DeductionReviewStatus.PENDING).count() == 1
