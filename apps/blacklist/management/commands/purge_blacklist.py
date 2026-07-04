from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.blacklist.services import purge_expired


class Command(BaseCommand):
    help = "Retention purge: delete blacklist match fingerprints past their expiry."

    def handle(self, *args, **options):
        deleted = purge_expired()
        self.stdout.write(self.style.SUCCESS(f"Purged {deleted} expired fingerprint(s)."))
