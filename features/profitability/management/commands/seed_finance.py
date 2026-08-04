from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand

from core.accounts.models import User
from features.profitability.models import (
    FinanceCategory,
    FinanceCategoryKind,
    FinanceGroup,
)
from features.profitability.services import (
    recompute_month,
    record_financial_month,
    set_line_item,
)
from core.projects.models import Project

# Catalog from Jober_Finance_Specs.md §2 (English glosses + group tags).
COST = FinanceCategoryKind.COST
REV = FinanceCategoryKind.REVENUE
G = FinanceGroup

CATEGORIES = [
    # (label, kind, group, key)
    ("Gross wage", COST, G.LABOUR, "gross_wage"),
    ("Sole-trader (SZČO)", COST, G.LABOUR, "szco"),
    ("Payroll levies", COST, G.LABOUR, "levies"),
    ("Driver", COST, G.TRANSPORT, "driver"),
    ("Damage (cost)", COST, G.DAMAGE, "damage_cost"),
    ("Forklift training", COST, G.COMPLIANCE, "forklift_training"),
    ("Forklift licence", COST, G.COMPLIANCE, "forklift_licence"),
    ("Accommodation", COST, G.ACCOMMODATION, "accommodation_cost"),
    ("Insurance", COST, G.COMPLIANCE, "insurance"),
    ("Medical", COST, G.COMPLIANCE, "medical"),
    ("Coordinators", COST, G.OVERHEAD, "coordinators"),
    ("Leasing", COST, G.TRANSPORT, "leasing"),
    ("Fuel", COST, G.TRANSPORT, "fuel"),
    ("Toll", COST, G.TRANSPORT, "toll"),
    ("Factoring", COST, G.OVERHEAD, "factoring"),
    ("Office", COST, G.OVERHEAD, "office"),
    ("Recruitment", COST, G.OVERHEAD, "recruitment"),
    ("HR", COST, G.OVERHEAD, "hr"),
    ("Clothing/equipment", COST, G.EQUIPMENT, "clothing"),
    ("Other extraordinary costs", COST, G.OTHER, "other_extraordinary"),
    ("Client invoices", REV, G.REVENUE, "invoices"),
    ("Deductions received from employees", REV, G.REVENUE, "worker_deductions"),
    ("Meals", REV, G.WELFARE, "meals"),
    ("Accommodation charged", REV, G.ACCOMMODATION, "accommodation_revenue"),
    ("Damage recovered", REV, G.DAMAGE, "damage_recovered"),
]

# Jan-Jul 2026 (year to date), one distinct growth curve per project/office
# so the executive dashboard's multi-series office-trend chart (ADR 0026
# Phase A) actually shows three differently-shaped lines rather than
# parallel copies: DHLBA is a steady grower, WEB dips mid-year then
# recovers, CARGO is a fast-ramping newer project.
MONTHLY_DATA = {
    # Two projects per office (six total) so "Profit/loss by office" is a real
    # roll-up rather than a restatement of one project, and each office's
    # trend is the sum of two differently-shaped contracts.
    #   Velký Meder   DHLBA (steady grower)  + MINIT (seasonal, summer peak)
    #   Győr          WEB   (dips, recovers) + MEVIS (flat, dependable)
    #   Dunajská Streda CARGO (fast ramp)    + RLS   (small, slowly declining)
    "DHLBA": [
        (1, "14000", "10200"),
        (2, "14400", "10450"),
        (3, "14800", "10600"),
        (4, "15200", "10800"),
        (5, "15700", "11000"),
        (6, "16100", "11200"),
        (7, "16600", "11450"),
    ],
    "MINIT": [
        (1, "6200", "5100"),
        (2, "6100", "5050"),
        (3, "6900", "5400"),
        (4, "8100", "6050"),
        (5, "9400", "6800"),
        (6, "10600", "7400"),
        (7, "11200", "7700"),
    ],
    "WEB": [
        (1, "9600", "7300"),
        (2, "9400", "7250"),
        (3, "8800", "7400"),
        (4, "8600", "7350"),
        (5, "9100", "7300"),
        (6, "9700", "7350"),
        (7, "10200", "7450"),
    ],
    "MEVIS": [
        (1, "7400", "5900"),
        (2, "7350", "5880"),
        (3, "7500", "5960"),
        (4, "7420", "5910"),
        (5, "7560", "6000"),
        (6, "7480", "5950"),
        (7, "7620", "6040"),
    ],
    "CARGO": [
        (1, "5000", "4300"),
        (2, "5800", "4700"),
        (3, "6700", "5200"),
        (4, "7600", "5750"),
        (5, "8600", "6300"),
        (6, "9700", "6900"),
        (7, "10800", "7500"),
    ],
    "RLS": [
        (1, "4800", "3900"),
        (2, "4700", "3860"),
        (3, "4550", "3800"),
        (4, "4400", "3760"),
        (5, "4300", "3720"),
        (6, "4150", "3660"),
        (7, "4050", "3620"),
    ],
}

# Nov-Dec 2025 for the same six projects, so the year view offers an honest
# partial-year comparison and the yearly roll-up has something to roll up.
# Each figure sits just below that project's Jan-2026 level, so the step into
# 2026 reads as growth rather than a discontinuity. Deliberately only two
# months: this is the tail of the prior year, not an invented full history.
PRIOR_YEAR_DATA = {
    "DHLBA": [(11, "13400", "9850"), (12, "13700", "10000")],
    "MINIT": [(11, "5900", "4950"), (12, "6050", "5020")],
    "WEB": [(11, "9200", "7100"), (12, "9400", "7180")],
    "MEVIS": [(11, "7180", "5780"), (12, "7260", "5820")],
    "CARGO": [(11, "4200", "3800"), (12, "4600", "4020")],
    "RLS": [(11, "5050", "4020"), (12, "4950", "3980")],
}

COST_SPLIT = {
    # Each project's split spans a different mix of groups so the
    # Group-breakdown chart and the per-month drill-in show real variety
    # rather than the same five bars three times. Fractions per project sum
    # to exactly 1.00 — recompute_month() derives the month total from the
    # line items, so a split that doesn't sum to 1 silently changes the
    # month's cost.
    "DHLBA": [  # mature warehouse contract: labour-heavy, own fleet
        ("Gross wage", Decimal("0.40")),
        ("Payroll levies", Decimal("0.12")),
        ("Sole-trader (SZČO)", Decimal("0.06")),
        ("Accommodation", Decimal("0.13")),
        ("Fuel", Decimal("0.06")),
        ("Leasing", Decimal("0.05")),
        ("Toll", Decimal("0.03")),
        ("Clothing/equipment", Decimal("0.05")),
        ("Coordinators", Decimal("0.04")),
        ("Insurance", Decimal("0.02")),
        ("Medical", Decimal("0.02")),
        ("Other extraordinary costs", Decimal("0.02")),
    ],
    "MINIT": [  # food production: compliance-heavy, high welfare spend
        ("Gross wage", Decimal("0.44")),
        ("Payroll levies", Decimal("0.13")),
        ("Accommodation", Decimal("0.11")),
        ("Medical", Decimal("0.07")),
        ("Forklift training", Decimal("0.04")),
        ("Insurance", Decimal("0.04")),
        ("Clothing/equipment", Decimal("0.06")),
        ("Driver", Decimal("0.05")),
        ("HR", Decimal("0.03")),
        ("Office", Decimal("0.03")),
    ],
    "WEB": [  # automotive tier-1: overhead-heavy, factored invoices
        ("Gross wage", Decimal("0.42")),
        ("Payroll levies", Decimal("0.12")),
        ("Accommodation", Decimal("0.12")),
        ("Office", Decimal("0.07")),
        ("Factoring", Decimal("0.06")),
        ("Recruitment", Decimal("0.05")),
        ("Coordinators", Decimal("0.05")),
        ("Medical", Decimal("0.04")),
        ("Clothing/equipment", Decimal("0.04")),
        ("Damage (cost)", Decimal("0.03")),
    ],
    "MEVIS": [  # precision components: training and equipment intensive
        ("Gross wage", Decimal("0.41")),
        ("Payroll levies", Decimal("0.12")),
        ("Accommodation", Decimal("0.12")),
        ("Forklift training", Decimal("0.06")),
        ("Forklift licence", Decimal("0.04")),
        ("Clothing/equipment", Decimal("0.08")),
        ("Insurance", Decimal("0.05")),
        ("Coordinators", Decimal("0.05")),
        ("HR", Decimal("0.04")),
        ("Other extraordinary costs", Decimal("0.03")),
    ],
    "CARGO": [  # newer transport contract: fleet-heavy, ramping
        ("Gross wage", Decimal("0.36")),
        ("Payroll levies", Decimal("0.11")),
        ("Driver", Decimal("0.10")),
        ("Fuel", Decimal("0.11")),
        ("Toll", Decimal("0.06")),
        ("Leasing", Decimal("0.08")),
        ("Accommodation", Decimal("0.08")),
        ("Damage (cost)", Decimal("0.04")),
        ("Clothing/equipment", Decimal("0.03")),
        ("Recruitment", Decimal("0.03")),
    ],
    "RLS": [  # smallest contract: lean, mostly labour and overhead
        ("Gross wage", Decimal("0.46")),
        ("Payroll levies", Decimal("0.14")),
        ("Accommodation", Decimal("0.14")),
        ("Coordinators", Decimal("0.07")),
        ("Office", Decimal("0.06")),
        ("Clothing/equipment", Decimal("0.05")),
        ("Medical", Decimal("0.04")),
        ("Other extraordinary costs", Decimal("0.04")),
    ],
}

# Revenue split (fractions of that month's revenue). Client invoices always
# dominate, but seeding the recharge/recovery categories too means the
# revenue side of the Group breakdown isn't a single bar — and it exercises
# the accommodation-charged and damage-recovered categories the workbook
# actually uses. Sums to exactly 1.00 per project.
REVENUE_SPLIT = {
    "DHLBA": [
        ("Client invoices", Decimal("0.90")),
        ("Accommodation charged", Decimal("0.06")),
        ("Deductions received from employees", Decimal("0.02")),
        ("Damage recovered", Decimal("0.02")),
    ],
    "MINIT": [
        ("Client invoices", Decimal("0.89")),
        ("Accommodation charged", Decimal("0.05")),
        ("Meals", Decimal("0.04")),
        ("Deductions received from employees", Decimal("0.02")),
    ],
    "WEB": [
        ("Client invoices", Decimal("0.92")),
        ("Accommodation charged", Decimal("0.05")),
        ("Deductions received from employees", Decimal("0.03")),
    ],
    "MEVIS": [
        ("Client invoices", Decimal("0.91")),
        ("Accommodation charged", Decimal("0.05")),
        ("Meals", Decimal("0.02")),
        ("Damage recovered", Decimal("0.02")),
    ],
    "CARGO": [
        ("Client invoices", Decimal("0.88")),
        ("Accommodation charged", Decimal("0.06")),
        ("Damage recovered", Decimal("0.04")),
        ("Deductions received from employees", Decimal("0.02")),
    ],
    "RLS": [
        ("Client invoices", Decimal("0.93")),
        ("Accommodation charged", Decimal("0.05")),
        ("Meals", Decimal("0.02")),
    ],
}


def _apply_splits(financial_month, code, rev, cost, actor):
    """Write one month's line items from the per-project split tables.

    Shared by the 2025 and 2026 loops so both years get identical category
    depth. ``recompute_month`` then derives the month's revenue/cost totals
    back out of these items - which is why each split must sum to exactly
    1.00 (guarded by tests/test_finance_seed_splits.py).
    """
    cost_decimal = Decimal(cost)
    for label, fraction in COST_SPLIT[code]:
        category = FinanceCategory.objects.get(label=label, kind=COST)
        set_line_item(
            financial_month,
            category,
            (cost_decimal * fraction).quantize(Decimal("0.01")),
            actor=actor,
        )
    revenue_decimal = Decimal(rev)
    for label, fraction in REVENUE_SPLIT[code]:
        category = FinanceCategory.objects.get(label=label, kind=REV)
        set_line_item(
            financial_month,
            category,
            (revenue_decimal * fraction).quantize(Decimal("0.01")),
            actor=actor,
        )
    recompute_month(financial_month, actor=actor)


class Command(BaseCommand):
    help = "Seed the finance category catalog and demo financial months (idempotent)."

    def handle(self, *args, **options):
        created = 0
        for order, (label, kind, group, key) in enumerate(CATEGORIES):
            # `key` is repaired on every run, not only on create: a catalogue
            # seeded before the key existed must gain one, or the importer and
            # the export have nothing stable to join on.
            _obj, was_created = FinanceCategory.objects.update_or_create(
                label=label,
                kind=kind,
                defaults={"group": group, "order": order, "key": key},
            )
            created += int(was_created)

        coordinator = User.objects.filter(email="koordinator@demo.jober.test").first()

        # Prior-year tail (Nov-Dec 2025), same six projects and the same
        # category splits as 2026 - so the comparison is like-for-like rather
        # than a thin two-project stub next to a fully-populated year.
        prior_seeded = 0
        for code, rows in PRIOR_YEAR_DATA.items():
            project = Project.objects.filter(code=code).first()
            if not project:
                continue
            for month, rev, cost in rows:
                financial_month = record_financial_month(
                    project, 2025, month, rev, cost, actor=coordinator
                )
                _apply_splits(financial_month, code, rev, cost, coordinator)
                prior_seeded += 1

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
                _apply_splits(financial_month, code, rev, cost, coordinator)
                months_seeded += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Finance categories: {created} created, {FinanceCategory.objects.count()} total. "
                f"Financial months seeded: {prior_seeded} (2025 Nov-Dec) "
                f"+ {months_seeded} (2026 YTD)."
            )
        )
