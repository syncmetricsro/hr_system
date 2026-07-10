from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand

from features.feedback.services import purge_feedback


class Command(BaseCommand):
    help = "Delete feedback submissions older than FEEDBACK_RETENTION_DAYS (§11.11: ~1 month)."

    def handle(self, *args, **options):
        days = getattr(settings, "FEEDBACK_RETENTION_DAYS", 31)
        deleted = purge_feedback()
        self.stdout.write(self.style.SUCCESS(f"Purged {deleted} feedback submission(s) older than {days} days."))
