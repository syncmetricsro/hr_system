"""Translatable msgids for the seeded finance categories (seed_finance).

DB stores canonical English; templates render via ``db_trans``. Labels pend
Jober's one-real-filled-month reconciliation (phase3-4 Q&A) — keep this list
in sync with seed_finance.CATEGORIES when that lands.
"""

from django.utils.translation import gettext_noop as _

SEEDED_FINANCE_CATEGORIES = [
    _("Gross wage"),
    _("Sole-trader (SZČO)"),
    _("Payroll levies"),
    _("Driver"),
    _("Damage (cost)"),
    _("Forklift training"),
    _("Forklift licence"),
    _("Accommodation"),
    _("Insurance"),
    _("Medical"),
    _("Coordinators"),
    _("Leasing"),
    _("Fuel"),
    _("Toll"),
    _("Factoring"),
    _("Office"),
    _("Recruitment"),
    _("Clothing/equipment"),
    _("Other extraordinary costs"),
    _("Client invoices"),
    _("Deductions received from employees"),
    _("Meals"),
    _("Accommodation charged"),
    _("Damage recovered"),
]
