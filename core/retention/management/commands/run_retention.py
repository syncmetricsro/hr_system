from __future__ import annotations

from django.core.management.base import BaseCommand

from core.retention.services import run_all


class Command(BaseCommand):
    help = "Run every registered retention purge (feedback, blacklist, ...)."

    def handle(self, *args, **options):
        results = run_all()
        if not results:
            self.stdout.write("No retention jobs registered.")
            return
        for name, result in results.items():
            self.stdout.write(f"  {name}: {result}")
        self.stdout.write(self.style.SUCCESS(f"Retention complete ({len(results)} job(s))."))
