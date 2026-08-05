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

# The per-item help text (what the tick claims). Kept in sync with the same
# seed list by hand, exactly like the labels above — the strings must match
# character for character or db_trans falls through to English.
SEEDED_CHECKLIST_HELP = [
    _(
        "Name, date of birth, address and phone are all filled in, "
        "and they match the document you were shown rather than what "
        "was said on the phone."
    ),
    _(
        "You have seen the ID card or passport yourself, it is valid "
        "today, and the name matches this record. No scan is kept "
        "here — this tick is the record that you checked."
    ),
    _(
        "For a non-EU worker: the permit covers the whole planned "
        "assignment, not just the start date. An EU national needs "
        "none — tick it and move on."
    ),
    _(
        "A fitness certificate exists, is less than a year old, and "
        "its date is recorded on this worker. Until the date is "
        "entered, Compliance keeps reporting the medical as missing."
    ),
    _(
        "The worker has attended the safety training for the site "
        "they are going to, and whoever gave it has confirmed they "
        "were there."
    ),
    _(
        "Both sides have signed and the office holds its copy. A "
        "contract sent but not signed back is not this item."
    ),
    _(
        "You have searched for this person under other spellings of "
        "the name and under their phone number, and confirmed there "
        "is no second record for them."
    ),
    _(
        "The blacklist check has been run and either found nothing, "
        "or a manager has decided the case. An open match is not "
        "resolved."
    ),
    _(
        "Somebody has called the worker to confirm the start date, "
        "how they get there and what to bring. Not critical — but it "
        "prevents most no-shows."
    ),
]

SEEDED_EQUIPMENT_NAMES = [
    _("Safety boots"),
]
