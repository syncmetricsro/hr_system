from __future__ import annotations

import datetime as dt
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from core.accounts.models import Role, User
from core.people.models import Person
from core.projects.models import Project
from features.advances.models import EntryType, LedgerCategory, LedgerEntry
from features.advances.services import record_entry, week_cutoff
from features.checklists.models import ChecklistItemTemplate, ChecklistTemplate
from features.logistics.models import EquipmentItem
from features.logistics.services import flag_unreturned, issue_equipment, review_deduction
from features.payslips.models import Payslip
from features.payslips.services import record_payslip
from features.wage_ledger.models import WageEntry
from features.wage_ledger.services import record_wage

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

# Labels are canonical English; msgids registered in clients/corvinum_eu/
# catalog_i18n.py (makemessages ignores demo paths). Rendered via db_trans.
ACTIVATION_ITEMS = [
    (("Personal data complete"), True),
    (("Identity document verified"), True),
    (("Work/residence permit valid (if applicable)"), True),
    (("Medical certificate valid"), True),
    (("Safety training completed"), True),
    (("Contract signed"), True),
    (("Duplicate check resolved"), True),
    (("Blacklist check resolved"), True),
    (("Welcome call made"), False),
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

        # People. A fresh seed uses a fictional address. Do not overwrite an
        # address deliberately changed to a controlled demo inbox: the runner
        # may be re-applied during rehearsal and a resend must remain safe.
        worker, _ = Person.objects.get_or_create(
            first_name="Marek",
            last_name="Skladník",
            defaults={"email": "marek.skladnik@demo.corvinum.test"},
        )
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
            advance = record_entry(
                worker, entry_type=EntryType.CASH_ADVANCE, category=LedgerCategory.CASH_ADVANCE,
                amount=Decimal("100.00"), actor=hradmin, project=alfa, note="cash Friday",
            )
            # Cash advances after this week's Thursday 14:00 roll to next
            # week and never retro-insert (C-Q2) — so seeding this demo on a
            # Thursday afternoon would silently drop it from the Thursday
            # summary the seed comment above promises. Pin it just inside
            # this week's window so the summary always has something to show,
            # regardless of what day/time the demo happens to be seeded.
            cutoff = week_cutoff(dt.date.today())
            if advance.created_at > cutoff:
                LedgerEntry.objects.filter(pk=advance.pk).update(
                    created_at=cutoff - dt.timedelta(hours=1)
                )
        if not LedgerEntry.objects.filter(person=worker, category=LedgerCategory.TRAVEL_FUEL).exists():
            record_entry(
                worker, entry_type=EntryType.PAY_ADDITION, category=LedgerCategory.TRAVEL_FUEL,
                amount=Decimal("30.00"), actor=hradmin, project=alfa,
                entry_date=dt.date.today(), note="private-car commute (C-Q10 default)",
            )

        # Two independently recorded source series aligned by calendar month.
        # These are fictional presentation values, not client payroll figures.
        pay_rows = [
            ("2026-06", Decimal("1920.00"), Decimal("1450.00"), dt.date(2026, 7, 5)),
            ("2026-07", Decimal("2050.00"), Decimal("1540.00"), dt.date(2026, 7, 20)),
        ]
        for period, gross_amount, net_amount, issue_date in pay_rows:
            if not WageEntry.objects.filter(person=candidate, period=period).exists():
                record_wage(
                    candidate,
                    period=period,
                    gross_amount=gross_amount,
                    note="Fictional gross source value",
                    actor=hradmin,
                )
            if not Payslip.objects.filter(person=candidate, period=period).exists():
                record_payslip(
                    candidate,
                    period=period,
                    net_amount=net_amount,
                    note="Fictional net payslip source value",
                    issue_date=issue_date,
                    actor=hradmin,
                )
            else:
                Payslip.objects.filter(person=candidate, period=period).update(
                    issue_date=issue_date
                )

        self.stdout.write(self.style.SUCCESS(
            f"CorvinumEU demo ready: 4 users @{DEMO_DOMAIN}, companies {alfa.code}/{beta.code}, "
            f"checklist '{template.name}', worker ledger and pay sources seeded "
            f"(candidate: {candidate})."
        ))
