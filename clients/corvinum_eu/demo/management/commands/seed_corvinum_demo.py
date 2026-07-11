from __future__ import annotations

import datetime as dt
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from core.accounts.models import Role, User
from core.people.models import Person
from core.projects.models import Project
from features.advances.models import EntryType, LedgerCategory, LedgerEntry
from features.advances.services import record_entry
from features.checklists.models import ChecklistItemTemplate, ChecklistTemplate
from features.logistics.models import EquipmentItem
from features.logistics.services import flag_unreturned, issue_equipment, review_deduction

# Obviously-fictional accounts only — the real-data gate (AGENTS.md) applies
# to every client, CorvinumEU included.
DEMO_PASSWORD = "demo-corvinum-2026"
DEMO_DOMAIN = "demo.corvinum.test"

DEMO_USERS = [
    ("recruiter", Role.RECRUITER, "Recruiter", "Demo"),
    ("coordinator", Role.COORDINATOR, "Coordinator", "Demo"),
    ("hradmin", Role.MANAGER, "HR Admin", "Demo"),
    ("observer", Role.OBSERVER, "Observer", "Demo"),
]

ACTIVATION_ITEMS = [
    ("Personal data complete", True),
    ("Identity document verified", True),
    ("Work/residence permit valid (if applicable)", True),
    ("Medical certificate valid", True),
    ("Safety training completed", True),
    ("Contract signed", True),
    ("Duplicate check resolved", True),
    ("Blacklist check resolved", True),
    ("Welcome call made", False),
]


class Command(BaseCommand):
    help = "Idempotent fictional demo scenario for the CorvinumEU thin client."

    @transaction.atomic
    def handle(self, *args, **options):
        for local_part, role, first, last in DEMO_USERS:
            email = f"{local_part}@{DEMO_DOMAIN}"
            assert email.endswith(f"@{DEMO_DOMAIN}")
            user, _ = User.objects.get_or_create(
                email=email, defaults={"first_name": first, "last_name": last, "role": role}
            )
            user.role, user.is_active = role, True
            user.set_password(DEMO_PASSWORD)
            user.save()
        hradmin = User.objects.get(email=f"hradmin@{DEMO_DOMAIN}")

        # Partner companies are the projects (§5.7: a worker belongs to one
        # company/project).
        alfa, _ = Project.objects.get_or_create(code="CV-ALFA", defaults={"name": "Alfa Metallwerk"})
        beta, _ = Project.objects.get_or_create(code="CV-BETA", defaults={"name": "Beta Logistik"})

        # Global activation checklist (§5.5).
        template, _ = ChecklistTemplate.objects.get_or_create(name="Global activation")
        for order, (label, critical) in enumerate(ACTIVATION_ITEMS, start=1):
            ChecklistItemTemplate.objects.get_or_create(
                template=template, label=label, defaults={"critical": critical, "order": order}
            )

        # People. The worker carries a fictional email — the payslip act
        # (corvinum-demo-runbook §6) sends the encrypted PDF to it.
        worker, _ = Person.objects.get_or_create(first_name="Marek", last_name="Skladník")
        if worker.email != "marek.skladnik@demo.corvinum.test":
            worker.email = "marek.skladnik@demo.corvinum.test"
            worker.save(update_fields=["email"])
        candidate, _ = Person.objects.get_or_create(first_name="Eszter", last_name="Varga")

        # Equipment with values (§5.8) + one approved charge that lands in the
        # ledger via the deduction-approved hook.
        boots, _ = EquipmentItem.objects.get_or_create(
            name="Safety boots", size="43", defaults={"unit_price": Decimal("35.00")}
        )
        if not worker.equipment_issues.filter(item=boots).exists():
            issue = issue_equipment(worker, boots, 1, actor=hradmin)
            flag_unreturned(issue, actor=hradmin)
            review_deduction(issue, "approve", actor=hradmin, note="left after two days")

        # Ledger rhythm (§5.10): an open advance for the Thursday summary,
        # travel money, and the equipment deduction from the hook above.
        if not LedgerEntry.objects.filter(person=worker, entry_type=EntryType.CASH_ADVANCE).exists():
            record_entry(
                worker, entry_type=EntryType.CASH_ADVANCE, category=LedgerCategory.CASH_ADVANCE,
                amount=Decimal("100.00"), actor=hradmin, project=alfa, note="cash Friday",
            )
        if not LedgerEntry.objects.filter(person=worker, category=LedgerCategory.TRAVEL_FUEL).exists():
            record_entry(
                worker, entry_type=EntryType.PAY_ADDITION, category=LedgerCategory.TRAVEL_FUEL,
                amount=Decimal("30.00"), actor=hradmin, project=alfa,
                entry_date=dt.date.today(), note="private-car commute (C-Q10 default)",
            )

        self.stdout.write(self.style.SUCCESS(
            f"CorvinumEU demo ready: 4 users @{DEMO_DOMAIN}, companies {alfa.code}/{beta.code}, "
            f"checklist '{template.name}', worker ledger seeded (candidate: {candidate})."
        ))
