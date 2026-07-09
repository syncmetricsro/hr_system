from __future__ import annotations

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


def _new_token() -> str:
    return uuid.uuid4().hex[:12]


class FeedbackLink(models.Model):
    """A tokenized public feedback entry point (plan §10.1 /feedback/<token>).

    The QR code simply encodes the public URL for this token. No worker account
    is created."""

    token = models.SlugField(_("token"), max_length=32, unique=True, default=_new_token)
    label = models.CharField(_("label"), max_length=120)
    project = models.ForeignKey(
        "projects.Project", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="feedback_links", verbose_name=_("project"),
    )
    is_active = models.BooleanField(_("active"), default=True)
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("feedback link")
        verbose_name_plural = _("feedback links")
        ordering = ("label",)

    def __str__(self) -> str:
        return self.label


class FeedbackSubmission(models.Model):
    """An anonymous worker feedback submission (manager-only to read; §8.1).

    Retained for a short window only (FEEDBACK_RETENTION_DAYS) — see the
    purge_feedback command."""

    link = models.ForeignKey(
        FeedbackLink, on_delete=models.CASCADE, related_name="submissions", verbose_name=_("link")
    )
    message = models.TextField(_("message"))
    rating = models.PositiveSmallIntegerField(_("rating"), null=True, blank=True)
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("feedback submission")
        verbose_name_plural = _("feedback submissions")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Feedback #{self.pk}"
