"""Translatable msgids for the seeded equipment items (seed_logistics).

DB stores canonical English names; panels render via ``db_trans``.
Operator-entered items are data and fall through untranslated by design.
"""

from django.utils.translation import gettext_noop as _

SEEDED_EQUIPMENT_NAMES = [
    _("Work boots"),
    _("High-visibility vest"),
    _("Safety helmet"),
]
