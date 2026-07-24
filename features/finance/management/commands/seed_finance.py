from __future__ import annotations

from decimal import Decimal

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

# Jan-Jul 2026 (year to date), one distinct growth curve per project/office
# so the executive dashboard's multi-series office-trend chart (ADR 0026
# Phase A) actually shows three differently-shaped lines rather than
# parallel copies: DHLBA is a steady grower, WEB dips mid-year then
# recovers, CARGO is a fast-ramping newer project.
MONTHLY_DATA = {
    "DHLBA": [
        (1, "14000", "10200"), (2, "14400", "10450"), (3, "14800", "10600"),
        (4, "15200", "10800"), (5, "15700", "11000"), (6, "16100", "11200"),
        (7, "16600", "11450"),
    ],
    "WEB": [
        (1, "9600", "7300"), (2, "9400", "7250"), (3, "8800", "7400"),
        (4, "8600", "7350"), (5, "9100", "7300"), (6, "9700", "7350"),
        (7, "10200", "7450"),
    ],
    "CARGO": [
        (1, "5000", "4300"), (2, "5800", "4700"), (3, "6700", "5200"),
        (4, "7600", "5750"), (5, "8600", "6300"), (6, "9700", "6900"),
        (7, "10800", "7500"),
    ],
}

# Cost-category split (fractions of that month's total cost), reused across
# all 7 months per project — gives the Group-breakdown chart real category
# variety without hand-writing 21 unique line-item sets.
COST_SPLIT = {
    "DHLBA": [
        ("Gross wage", Decimal("0.62")), ("Accommodation", Decimal("0.16")),
        ("Clothing/equipment", Decimal("0.09")), ("Fuel", Decimal("0.08")),
        ("Other extraordinary costs", Decimal("0.05")),
    ],
    "WEB": [
        ("Gross wage", Decimal("0.58")), ("Accommodation", Decimal("0.14")),
        ("Office", Decimal("0.10")), ("Medical", Decimal("0.09")),
        ("Other extraordinary costs", Decimal("0.09")),
    ],
    "CARGO": [
        ("Gross wage", Decimal("0.55")), ("Accommodation", Decimal("0.18")),
        ("Forklift training", Decimal("0.12")), ("Clothing/equipment", Decimal("0.10")),
        ("Other extraordinary costs", Decimal("0.05")),
    ],
}


class Command(BaseCommand):
    help = "Seed the finance category catalog and demo financial months (idempotent)."

    def handle(self, *args, **options):
        created = 0
        for order, (label, kind, group) in enumerate(CATEGORIES):
            _obj, was_created = FinanceCategory.objects.get_or_create(
                label=label, kind=kind, defaults={"group": group, "order": order}
            )
            created += int(was_created)

        coordinator = User.objects.filter(email="koordinator@demo.jober.test").first()

        # Historical single month (Nov 2025) - kept as-is for yearly-rollup contrast.
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

        # Year-to-date Jan-Jul 2026 across all three projects/offices.
        months_seeded = 0
        for code, rows in MONTHLY_DATA.items():
            project = Project.objects.filter(code=code).first()
            if not project:
                continue
            for month, rev, cost in rows:
                financial_month = record_financial_month(
                    project, 2026, month, rev, cost, actor=coordinator
                )
                cost_decimal = Decimal(cost)
                for label, fraction in COST_SPLIT[code]:
                    category = FinanceCategory.objects.get(label=label, kind=COST)
                    amount = (cost_decimal * fraction).quantize(Decimal("0.01"))
                    set_line_item(financial_month, category, amount, actor=coordinator)
                invoices = FinanceCategory.objects.get(label="Client invoices", kind=REV)
                set_line_item(financial_month, invoices, rev, actor=coordinator)
                recompute_month(financial_month, actor=coordinator)
                months_seeded += 1

        self.stdout.write(self.style.SUCCESS(
            f"Finance categories: {created} created, {FinanceCategory.objects.count()} total. "
            f"Financial months seeded (2026 YTD): {months_seeded}."
        ))
