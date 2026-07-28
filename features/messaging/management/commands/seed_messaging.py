"""Seed a few SMS templates (production-readiness item 16).

`Action.SMS_MANAGE_TEMPLATES` is granted to Manager and implemented nowhere, so
`MessageTemplate` is reachable only through Django admin - which needs a
superuser no client role has. Worse, **no templates were seeded either**, and
the SMS panel renders its picker behind `{% if panel.message_templates %}`. The
control therefore never appeared at all, and the demo runbook's "pick a
template" step had nothing to pick.

The backlog's cheapest useful answer was to seed two or three and keep
management in admin. This is that.

**Bodies are Slovak.** `views.py` sends `template.body` verbatim -
`Person.preferred_language` exists and messaging never reads it - so a template
goes out in whatever language it was written in regardless of who receives it.
Slovak is the company's operating language and the application default, which
makes it the least wrong single choice, but it is a choice rather than a
solution. Recorded as its own backlog item.

Idempotent: matched on `name`, so re-running updates the body rather than
creating duplicates.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from features.messaging.models import MessageTemplate

#: Short enough to stay inside one SMS segment where possible, and written as
#: something a coordinator would actually send rather than lorem ipsum - a
#: template nobody would send teaches the demo audience nothing.
TEMPLATES = [
    (
        "Pripomienka - zajtrajšia zmena",
        "Dobrý deň, pripomíname zajtrajšiu zmenu. V prípade otázok nás "
        "kontaktujte. Ďakujeme.",
    ),
    (
        "Chýbajúci dokument",
        "Dobrý deň, k Vášmu nástupu nám ešte chýba jeden dokument. "
        "Prosím, doneste ho pri najbližšej návšteve. Ďakujeme.",
    ),
    (
        "Potvrdenie ubytovania",
        "Dobrý deň, Vaše ubytovanie je potvrdené. Podrobnosti Vám odovzdá "
        "koordinátor na mieste.",
    ),
]


class Command(BaseCommand):
    help = "Seed demo SMS templates so the message picker has something to offer."

    def handle(self, *args, **options):
        created = 0
        for name, body in TEMPLATES:
            _obj, was_created = MessageTemplate.objects.update_or_create(
                name=name, defaults={"body": body, "is_active": True}
            )
            created += int(was_created)
        self.stdout.write(
            self.style.SUCCESS(
                f"SMS templates: {created} created, "
                f"{MessageTemplate.objects.count()} total."
            )
        )
