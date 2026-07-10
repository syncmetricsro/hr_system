from __future__ import annotations

import datetime as dt

from django.conf import settings
from django.utils import timezone

from features.feedback.models import FeedbackSubmission


def purge_feedback() -> int:
    """Delete submissions older than FEEDBACK_RETENTION_DAYS (§11.11 ≈ 1 month).
    Returns the number deleted. Registered with core.retention."""
    days = getattr(settings, "FEEDBACK_RETENTION_DAYS", 31)
    cutoff = timezone.now() - dt.timedelta(days=days)
    deleted, _ = FeedbackSubmission.objects.filter(created_at__lt=cutoff).delete()
    return deleted
