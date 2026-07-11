"""Translatable msgids for the seeded inactive reasons (0003 migration).

DB stores canonical English; templates render via ``db_trans``. Registered
here because applied migrations are never edited (house rule).
"""

from django.utils.translation import gettext_noop as _

SEEDED_INACTIVE_REASONS = [
    _("Sick"),
    _("Quit / left"),
    _("Suspended"),
    _("Military service"),
    _("Other"),
]
