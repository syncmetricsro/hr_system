"""Translatable msgids for CorvinumEU seeded catalog data.

The demo seed (clients/corvinum_eu/demo/…) stores these canonical English
strings in the DB; templates/services render them through ``db_trans``.
They are registered HERE because makemessages ignores ``demo`` paths
(scripts/compile_messages.sh) — keep this list in sync with the seed.
"""

from django.utils.translation import gettext_noop as _

SEEDED_CHECKLIST_LABELS = [
    _("Personal data complete"),
    _("Identity document verified"),
    _("Work/residence permit valid (if applicable)"),
    _("Medical certificate valid"),
    _("Safety training completed"),
    _("Contract signed"),
    _("Duplicate check resolved"),
    _("Blacklist check resolved"),
    _("Welcome call made"),
]

SEEDED_EQUIPMENT_NAMES = [
    _("Safety boots"),
]
