from __future__ import annotations

from django.core.management.base import BaseCommand

from core.accounts.models import User
from features.finance.models import FinanceCategory, FinanceCategoryKind, FinanceGroup
from features.finance.services import recompute_month, record_financial_month, set_line_item
from core.projects.models import Project

# Catalog from Jober_Finance_Specs.md §2 (English glosses + group tags).
COST = FinanceCategoryKind.COST
REV = FinanceCategoryKind.REVENUE
G = FinanceGroup

CATEGORIES = [
    # (label, kind, group)
    ("Gross wage", COST, G.LABOUR),
    ("Sole-trader (SZČO)", COST, G.LABOUR),
    ("Payroll levies", COST, G.LABOUR),
    ("Driver", COST, G.TRANSPORT),
    ("Damage (cost)", COST, G.DAMAGE),
    ("Forklift training", COST, G.COMPLIANCE),
    ("Forklift licence", COST, G.COMPLIANCE),
    ("Accommodation", COST, G.ACCOMMODATION),
    ("Insurance", COST, G.COMPLIANCE),
    ("Medical", COST, G.COMPLIANCE),
    ("Coordinators", COST, G.OVERHEAD),
    ("Leasing", COST, G.TRANSPORT),
    ("Fuel", COST, G.TRANSPORT),
    ("Toll", COST, G.TRANSPORT),
    ("Factoring", COST, G.OVERHEAD),
    ("Office", COST, G.OVERHEAD),
    ("Recruitment", COST, G.OVERHEAD),
    ("HR", COST, G.OVERHEAD),
    ("Clothing/equipment", COST, G.EQUIPMENT),
    ("Other extraordinary costs", COST, G.OTHER),
    ("Client invoices", REV, G.REVENUE),
    ("Deductions received from employees", REV, G.REVENUE),
    ("Meals", REV, G.WELFARE),
    ("Accommodation charged", REV, G.ACCOMMODATION),
    ("Damage recovered", REV, G.DAMAGE),
]


class Command(BaseCommand):
    help = "Seed the finance category catalog from Jober_Finance_Specs.md (idempotent)."

    def handle(self, *args, **options):
        created = 0
        for order, (label, kind, group) in enumerate(CATEGORIES):
            _obj, was_created = FinanceCategory.objects.get_or_create(
                label=label, kind=kind, defaults={"group": group, "order": order}
            )
            created += int(was_created)
        # Minimal demo financial months (positive convention, Q4-confirmed).
        coordinator = User.objects.filter(email="koordinator@demo.jober.test").first()
        for code, month, rev, cost in [("DHLBA", 11, "14600", "10850"), ("WEB", 11, "9800", "7650")]:
            project = Project.objects.filter(code=code).first()
            if project:
                financial_month = record_financial_month(
                    project, 2025, month, rev, cost, actor=coordinator
                )
                values = (
                    [("Gross wage", COST, "7200"), ("Accommodation", COST, "1650"),
                     ("Clothing/equipment", COST, "480"),
                     ("Other extraordinary costs", COST, "200"),
                     ("Client invoices", REV, rev)]
                    if code == "DHLBA" else
                    [("Gross wage", COST, "5100"), ("Accommodation", COST, "1250"),
                     ("Office", COST, "320"), ("Client invoices", REV, rev)]
                )
                for label, kind, amount in values:
                    category = FinanceCategory.objects.get(label=label, kind=kind)
                    set_line_item(financial_month, category, amount, actor=coordinator)
                recompute_month(financial_month, actor=coordinator)

        self.stdout.write(self.style.SUCCESS(
            f"Finance categories: {created} created, {FinanceCategory.objects.count()} total."
        ))
