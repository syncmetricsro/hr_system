from __future__ import annotations

import os

from datetime import timedelta
from uuid import NAMESPACE_URL, uuid5

from django.core.management.base import BaseCommand
import datetime as dt

from django.utils import timezone

from core.accounts.models import User
from core.offices.models import Office
from features.blacklist.models import BlacklistCategory
from features.blacklist.services import decide_case, propose_case
from features.compliance.models import Certificate, CertificateCategory
from features.profitability.models import (
    FinanceCategory,
    FinanceCategoryKind,
    FinancialMonth,
)
from features.profitability.services import recompute_month, set_line_item
from features.logistics.models import EquipmentItem
from core.ui.registry import flag_enabled
from features.logistics.services import (
    flag_unreturned,
    issue_equipment,
    return_equipment,
)
from core.people.models import InactiveReason, LifecycleStatus, Person
from core.projects.models import (
    ActivationApprovalStatus,
    PillarState,
    Project,
    TrialOutcome,
)
from core.projects.services import (
    get_or_create_readiness,
    record_trial_outcome,
    request_activation,
    schedule_trial,
    update_readiness,
)

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
        month = FinancialMonth.objects.filter(
            project__code="DHLBA", year=2026, month=5
        ).first()
        if month and not month.is_locked and not month.line_items.exists():
            line_items = [
                ("Gross wage", FinanceCategoryKind.COST, "9000"),
                ("Fuel", FinanceCategoryKind.COST, "1200"),
                ("Accommodation", FinanceCategoryKind.COST, "1800"),
                ("Client invoices", FinanceCategoryKind.REVENUE, "18000"),
                ("Accommodation charged", FinanceCategoryKind.REVENUE, "900"),
            ]
            for label, kind, amount in line_items:
                category = FinanceCategory.objects.filter(
                    label=label, kind=kind
                ).first()
                if category:
                    set_line_item(month, category, amount, actor=manager)
            recompute_month(month, actor=manager)

        # --- Equipment: issue two items to the Working worker, flag one ---------
        olha = Person.objects.filter(first_name="Olha", last_name="Kovalenko").first()
        if olha and not olha.equipment_issues.exists():
            boots = EquipmentItem.objects.filter(name="Work boots").first()
            vest = EquipmentItem.objects.filter(name="High-visibility vest").first()
            if boots:
                issue_equipment(
                    olha,
                    boots,
                    1,
                    actor=coordinator,
                    operation_key=uuid5(NAMESPACE_URL, "jober-demo-olha-boots-v1"),
                )
            if vest:
                issue = issue_equipment(
                    olha,
                    vest,
                    1,
                    actor=coordinator,
                    operation_key=uuid5(NAMESPACE_URL, "jober-demo-olha-vest-v1"),
                )
                flag_unreturned(
                    issue, actor=coordinator
                )  # -> manager Reviews queue (Q2)

        # Returned-stock examples retain the FIFO issue value: one reusable,
        # one physically retired. Deterministic keys keep repeated seeds safe.
        demo_returner = Person.objects.filter(
            first_name="Tran", last_name="Van Minh"
        ).first()
        helmet = EquipmentItem.objects.filter(name="Safety helmet").first()
        # Only seed returns for a client that has them. Jober retired the path
        # (J6, "what we issue, stays out"), and seeding two returned helmets
        # there would leave a worker holding items they had no way to return -
        # demo data implying a capability the UI does not offer.
        if flag_enabled("equipment_returns") and demo_returner and helmet:
            for suffix, disposition in (("restock", "restock"), ("retire", "retire")):
                issue = issue_equipment(
                    demo_returner,
                    helmet,
                    1,
                    actor=coordinator,
                    operation_key=uuid5(
                        NAMESPACE_URL, f"jober-demo-return-{suffix}-v1"
                    ),
                )
                if issue.status == "issued":
                    return_equipment(issue, actor=coordinator, disposition=disposition)

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
            bohdan.save(
                update_fields=["inactive_reason", "inactive_since", "updated_at"]
            )

        # --- Compliance: an expiring certificate -------------------------------
        if olha and not olha.certificates.exists():
            Certificate.objects.create(
                person=olha,
                name="Forklift licence",
                category=CertificateCategory.FORKLIFT,
                issue_date=today - timedelta(days=350),
                expiry_date=today + timedelta(days=15),
            )

        # --- Compliance: an expired certificate (pill-system-design.md §2 demo) -
        mira = Person.objects.filter(first_name="Mira", last_name="Novakova").first()
        if mira and not mira.certificates.exists():
            Certificate.objects.create(
                person=mira,
                name="Medical fitness check",
                category=CertificateCategory.HEALTH,
                issue_date=today - timedelta(days=400),
                expiry_date=today - timedelta(days=10),
            )

        # --- Blacklist: an approved (blacklisted) person for the re-entry demo --
        # Office matters here (ADR 0026 Phase B): the blacklist re-entry
        # walkthrough is presented as the manager, and an office-less person is
        # visible only to their owning recruiter, so leaving it unset 403s the
        # demo. Velký Meder = where the demo staff accounts are.
        velky_meder = Office.objects.filter(code="VM").first()
        blocked = Person.objects.filter(
            first_name="Ivan", last_name="Zablokovaný"
        ).first()
        if blocked is not None and blocked.office_id is None and velky_meder:
            # Repair a database seeded before offices existed - this block is
            # otherwise create-only, so an existing demo DB would keep the 403.
            blocked.office = velky_meder
            blocked.save(update_fields=["office", "updated_at"])
        if blocked is None:
            blocked = Person.objects.create(
                first_name="Ivan",
                last_name="Zablokovaný",
                owning_recruiter=recruiter,
                office=velky_meder,
            )
            category = BlacklistCategory.objects.filter(
                label="Fraud / dishonesty"
            ).first()
            case = propose_case(
                blocked,
                category=category,
                reason="Demo: prior fraud on site",
                identifier=DEMO_BLACKLIST_ID,
                actor=manager,
            )
            decide_case(case, "approve", actor=manager)

        # --- An activation request awaiting a manager's decision ---------------
        # Deliberately in Dunajska Streda rather than Velky Meder: it gives the
        # DS manager a non-empty Activations queue while the VM manager's stays
        # empty, which demonstrates that the queue is office-scoped as well as
        # demonstrating the approval itself. The live walkthrough uses Farrukh's
        # pending Gyor trial instead, so the two do not collide.
        tran = Person.objects.filter(first_name="Tran", last_name="Van Minh").first()
        ds_coordinator = User.objects.filter(
            email="koordinator.ds@demo.jober.test"
        ).first()
        cargo = Project.objects.filter(code="CARGO").first()
        if (
            tran
            and ds_coordinator
            and cargo
            and not tran.activation_approvals.filter(
                status=ActivationApprovalStatus.PENDING
            ).exists()
            and tran.lifecycle_status
            in (LifecycleStatus.AVAILABLE, LifecycleStatus.TRIAL_DAY)
        ):
            trial = tran.trials.filter(outcome=TrialOutcome.PENDING).first()
            if (
                trial is None
                and not tran.trials.filter(outcome=TrialOutcome.PASS).exists()
            ):
                trial = schedule_trial(
                    tran, cargo, actor=ds_coordinator, scheduled_for=timezone.now()
                )
            if trial is not None:
                record_trial_outcome(trial, TrialOutcome.PASS, actor=ds_coordinator)
            readiness = get_or_create_readiness(tran, cargo)
            update_readiness(
                readiness,
                actor=ds_coordinator,
                states={
                    "medical": PillarState.COMPLETE,
                    "gear": PillarState.COMPLETE,
                    "accommodation": PillarState.COMPLETE,
                    "transport": PillarState.NOT_APPLICABLE,
                },
                na_reasons={"transport": "own car"},
                # Required alongside a complete Medical: it is what the annual
                # expiry counts from, and what the compliance alert reads.
                entry_medical_date=timezone.localdate() - dt.timedelta(days=30),
            )
            request_activation(tran, cargo, actor=ds_coordinator)

        # --- Blacklist: a proposed case for the manager to decide live ---------
        diana = Person.objects.filter(
            first_name="Diana", last_name="Horvathova"
        ).first()
        if diana and not diana.blacklist_cases.exists():
            category = BlacklistCategory.objects.filter(
                label="Repeated no-show"
            ).first()
            propose_case(
                diana,
                category=category,
                reason="Demo: repeated no-shows",
                actor=coordinator,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo scenario seeded. Live blacklist re-entry ID: {DEMO_BLACKLIST_ID}"
            )
        )
