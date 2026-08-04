"""Extract messages without allowing msgmerge to invent fuzzy translations."""

from django.core.management.commands.makemessages import Command as DjangoCommand


class Command(DjangoCommand):
    msgmerge_options = [
        *DjangoCommand.msgmerge_options,
        "--no-fuzzy-matching",
    ]
