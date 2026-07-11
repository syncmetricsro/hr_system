"""Translatable msgids for the seeded blacklist categories (0002 migration).

The DB stores the canonical English label; templates render it through the
``db_trans`` filter. This file exists so makemessages extracts the strings —
never edit the applied migration (house rule).
"""

from django.utils.translation import gettext_noop as _

SEEDED_CATEGORY_LABELS = [
    _("Fraud / dishonesty"),
    _("Safety violation"),
    _("Repeated no-show"),
    _("Serious misconduct"),
    _("Other"),
]
