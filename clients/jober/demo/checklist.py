"""Jober's activation checklist: the template, and the ticks the seed needs.

Lives outside the management commands because **two** of them need it and the
order between them decides whether seeding works at all.

`seed_people` activates the seeded working people, and `activate_on_project`
runs every registered activation check — including the checklist gate. So the
moment a template with critical items exists, seeding a working person raises
`Activation blocked by open checklist items` unless the items are ticked first.
CorvinumEU never hit this because its seed activates nobody.

Both entry points therefore call `ensure_checklist_template()` (idempotent), and
`seed_people` calls `complete_for()` before it activates anyone — which is also
what an office would actually have done before putting somebody on a project.

Labels and help text are canonical English; the msgids are registered in
`clients/jober/catalog_i18n.py` (makemessages ignores `demo` paths) and rendered
through `db_trans`. They are byte-identical to CorvinumEU's on purpose — see
that file's header before changing a word here.
"""

from __future__ import annotations

from core.ui.registry import flag_enabled

TEMPLATE_NAME = "Global activation"

# (label, critical, help text) — kept in sync with clients/jober/catalog_i18n.py
ACTIVATION_ITEMS = [
    (
        "Personal data complete",
        True,
        "Name, date of birth, address and phone are all filled in, and they "
        "match the document you were shown rather than what was said on the "
        "phone.",
    ),
    (
        "Identity document verified",
        True,
        "You have seen the ID card or passport yourself, it is valid today, "
        "and the name matches this record. No scan is kept here — this tick "
        "is the record that you checked.",
    ),
    (
        "Work/residence permit valid (if applicable)",
        True,
        "For a non-EU worker: the permit covers the whole planned assignment, "
        "not just the start date. An EU national needs none — tick it and "
        "move on.",
    ),
    (
        "Medical certificate valid",
        True,
        "A fitness certificate exists, is less than a year old, and its date "
        "is recorded on this worker. Until the date is entered, Compliance "
        "keeps reporting the medical as missing.",
    ),
    (
        "Safety training completed",
        True,
        "The worker has attended the safety training for the site they are "
        "going to, and whoever gave it has confirmed they were there.",
    ),
    (
        "Contract signed",
        True,
        "Both sides have signed and the office holds its copy. A contract "
        "sent but not signed back is not this item.",
    ),
    (
        "Duplicate check resolved",
        True,
        "You have searched for this person under other spellings of the name "
        "and under their phone number, and confirmed there is no second "
        "record for them.",
    ),
    (
        "Blacklist check resolved",
        True,
        "The blacklist check has been run and either found nothing, or a "
        "manager has decided the case. An open match is not resolved.",
    ),
    (
        "Welcome call made",
        False,
        "Somebody has called the worker to confirm the start date, how they "
        "get there and what to bring. Not critical — but it prevents most "
        "no-shows.",
    ),
]


def ensure_checklist_template():
    """Create or repair Jober's activation checklist. Returns None when off.

    Repair, not only create: a database seeded before the help text existed
    already holds all nine rows, so `defaults` would never reach them.
    """
    if not flag_enabled("checklists"):
        return None
    from features.checklists.models import ChecklistItemTemplate, ChecklistTemplate

    template, _created = ChecklistTemplate.objects.get_or_create(name=TEMPLATE_NAME)
    for order, (label, critical, help_text) in enumerate(ACTIVATION_ITEMS, start=1):
        item, created = ChecklistItemTemplate.objects.get_or_create(
            template=template,
            label=label,
            defaults={"critical": critical, "order": order, "help_text": help_text},
        )
        if not created and item.help_text != help_text:
            item.help_text = help_text
            item.save(update_fields=["help_text"])
    return template


def complete_for(person, *, actor=None):
    """Tick this person's critical items, as the office would have before
    putting them on a project. Without it the seed's own activation is refused.

    Ticked through the service rather than by a bulk update, so the demo shows
    a real approval identity and audit trail against each item.
    """
    if not flag_enabled("checklists"):
        return
    from features.checklists.services import ensure_person_checklist, set_item_state

    for item in ensure_person_checklist(person):
        if item.item_template.critical and not item.done:
            set_item_state(item, done=True, actor=actor)
