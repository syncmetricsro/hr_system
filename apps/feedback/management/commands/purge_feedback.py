from __future__ import annotations

import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.feedback.models import FeedbackSubmission


class Command(BaseCommand):
    help = "Delete feedback submissions older than FEEDBACK_RETENTION_DAYS (§11.11: ~1 month)."

    def handle(self, *args, **options):
        days = getattr(settings, "FEEDBACK_RETENTION_DAYS", 31)
        cutoff = timezone.now() - dt.timedelta(days=days)
        deleted, _ = FeedbackSubmission.objects.filter(created_at__lt=cutoff).delete()
        self.stdout.write(self.style.SUCCESS(f"Purged {deleted} feedback submission(s) older than {days} days."))
