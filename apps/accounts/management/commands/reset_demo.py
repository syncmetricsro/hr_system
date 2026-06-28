from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from apps.accounts.management.commands.seed_demo import DEMO_DOMAIN
from apps.accounts.models import User


class Command(BaseCommand):
    help = "Delete the fictional demo users created by seed_demo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Confirm deletion without an interactive prompt.",
        )

    def handle(self, *args, **options):
        if not options["yes"]:
            raise CommandError("Pass --yes to confirm deletion of the demo users.")

        deleted, _ = User.objects.filter(email__endswith=f"@{DEMO_DOMAIN}").delete()
        self.stdout.write(self.style.SUCCESS(f"Demo objects deleted: {deleted}"))
