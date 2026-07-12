from __future__ import annotations

import os

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.accounts.models import User
from features.blacklist.models import BlacklistCategory
from features.blacklist.services import decide_case, propose_case
from features.compliance.models import Certificate
from features.finance.models import FinanceCategory, FinanceCategoryKind, FinancialMonth
from features.finance.services import recompute_month, set_line_item
from features.logistics.models import EquipmentItem
from features.logistics.services import flag_unreturned, issue_equipment
from core.people.models import InactiveReason, LifecycleStatus, Person

DEMO_DOMAIN = "demo.jober.test"
# Obviously-fictional demo identifier for the live blacklist re-entry moment.
DEMO_BLACKLIST_ID = "SK-DEMO-BL-001"


class Command(BaseCommand):
    help = (
        "Populate every module screen for the customer demo — finance line items, "
        "a flagged equipment review, a blacklisted person (+ a proposed case), an "
        "inactive reason, a compliance alert, and a phone. Idempotent; fictional only. "
        "Run after seed_demo + seed_people + seed_finance."
    )

    def handle(self, *args, **options):
        manager = User.objects.filter(email=f"manazer@{DEMO_DOMAIN}").first()
        coordinator = User.objects.filter(email=f"koordinator@{DEMO_DOMAIN}").first()
        recruiter = User.objects.filter(email=f"naborar@{DEMO_DOMAIN}").first()
        today = timezone.localdate()

        # --- Finance: line items on DHLBA 2026-05 (positive convention, Q4) -----
        month = FinancialMonth.objects.filter(project__code="DHLBA", year=2026, month=5).first()
        if month and not month.is_locked and not month.line_items.exists():
            line_items = [
                ("Gross wage", FinanceCategoryKind.COST, "9000"),
                ("Fuel", FinanceCategoryKind.COST, "1200"),
                ("Accommodation", FinanceCategoryKind.COST, "1800"),
                ("Client invoices", FinanceCategoryKind.REVENUE, "18000"),
                ("Accommodation charged", FinanceCategoryKind.REVENUE, "900"),
            ]
            for label, kind, amount in line_items:
                category = FinanceCategory.objects.filter(label=label, kind=kind).first()
                if category:
                    set_line_item(month, category, amount, actor=manager)
            recompute_month(month, actor=manager)

        # --- Equipment: issue two items to the Working worker, flag one ---------
        olha = Person.objects.filter(first_name="Olha", last_name="Kovalenko").first()
        if olha and not olha.equipment_issues.exists():
            boots = EquipmentItem.objects.filter(name="Work boots").first()
            vest = EquipmentItem.objects.filter(name="High-visibility vest").first()
            if boots:
                issue_equipment(olha, boots, 1, actor=coordinator)
            if vest:
                issue = issue_equipment(olha, vest, 1, actor=coordinator)
                flag_unreturned(issue, actor=coordinator)  # -> manager Reviews queue (Q2)

        # --- Phone for the optional live SMS demo ------------------------------
        # DEMO_SMS_PHONE (Doppler) points at a number whose inbox the presenter
        # can actually show (Twilio Virtual Phone) — the live SMS act lands
        # visibly. Unset -> keep the fictional placeholder.
        demo_phone = os.environ.get("DEMO_SMS_PHONE", "").strip()
        if olha and demo_phone and olha.phone != demo_phone:
            olha.phone = demo_phone
            olha.save(update_fields=["phone", "updated_at"])
        elif olha and not olha.phone:
            olha.phone = "+421900000000"
            olha.save(update_fields=["phone", "updated_at"])

        # --- Inactive reason for Bohdan (already Inactive) -> report (Q5) -------
        bohdan = Person.objects.filter(first_name="Bohdan", last_name="Melnyk").first()
        if (
            bohdan
            and bohdan.lifecycle_status == LifecycleStatus.INACTIVE
            and bohdan.inactive_reason is None
        ):
            bohdan.inactive_reason = InactiveReason.objects.filter(label="Sick").first()
            bohdan.inactive_since = today - timedelta(days=20)
            bohdan.save(update_fields=["inactive_reason", "inactive_since", "updated_at"])

        # --- Compliance: an expiring certificate -------------------------------
        if olha and not olha.certificates.exists():
            Certificate.objects.create(
                person=olha, name="Forklift licence",
                issue_date=today - timedelta(days=350),
                expiry_date=today + timedelta(days=15),
            )

        # --- Blacklist: an approved (blacklisted) person for the re-entry demo --
        blocked = Person.objects.filter(first_name="Ivan", last_name="Zablokovaný").first()
        if blocked is None:
            blocked = Person.objects.create(
                first_name="Ivan", last_name="Zablokovaný", owning_recruiter=recruiter
            )
            category = BlacklistCategory.objects.filter(label="Fraud / dishonesty").first()
            case = propose_case(
                blocked, category=category, reason="Demo: prior fraud on site",
                identifier=DEMO_BLACKLIST_ID, actor=manager,
            )
            decide_case(case, "approve", actor=manager)

        # --- Blacklist: a proposed case for the manager to decide live ---------
        diana = Person.objects.filter(first_name="Diana", last_name="Horvathova").first()
        if diana and not diana.blacklist_cases.exists():
            category = BlacklistCategory.objects.filter(label="Repeated no-show").first()
            propose_case(diana, category=category, reason="Demo: repeated no-shows", actor=coordinator)

        self.stdout.write(self.style.SUCCESS(
            f"Demo scenario seeded. Live blacklist re-entry ID: {DEMO_BLACKLIST_ID}"
        ))
