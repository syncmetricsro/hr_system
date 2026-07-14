from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class NotificationDismissal(models.Model):
    """A user's dismissal of one exact notification state.

    Notification content is deliberately recomputed and never copied here, so
    this table cannot become a second store of worker or financial data.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_dismissals",
        verbose_name=_("user"),
    )
    item_key = models.CharField(_("item key"), max_length=200)
    item_version = models.CharField(_("item version"), max_length=200)
    dismissed_at = models.DateTimeField(_("dismissed at"), auto_now_add=True)

    class Meta:
        verbose_name = _("notification dismissal")
        verbose_name_plural = _("notification dismissals")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "item_key", "item_version"],
                name="unique_notification_dismissal_state",
            )
        ]
        indexes = [models.Index(fields=["user", "item_key"])]

    def __str__(self) -> str:
        return f"{self.user_id}: {self.item_key}@{self.item_version}"
