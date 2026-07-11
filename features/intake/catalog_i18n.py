"""Translatable msgids for the seeded intake questionnaire (seed_questionnaire).

DB stores canonical English panel titles / question labels; the intake panel
renders them via ``db_trans``. Keep in sync with seed_questionnaire.
"""

from django.utils.translation import gettext_noop as _

SEEDED_INTAKE_STRINGS = [
    _("Identity"),
    _("Contact"),
    _("Compliance"),
    _("First name"),
    _("Last name"),
    _("Date of birth"),
    _("Place of birth"),
    _("Phone"),
    _("Address"),
    _("Nationality"),
    _("Preferred language"),
    _("Disability — type 'nie' if none"),
    _("Disability type"),
]
