from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AuditError(Exception):
    """Raised on any attempt to mutate or delete an existing audit event."""


class AuditEvent(models.Model):
    """Append-only record of a sensitive action.

    Append-only is enforced in application code: an existing row cannot be
    updated and no row can be deleted. The only sanctioned write path is
    ``apps.audit.services.record_event``.
    """

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="audit_events",
        verbose_name=_("aktér"),
    )
    action = models.CharField(_("akcia"), max_length=100)
    target_type = models.CharField(_("typ cieľa"), max_length=100, blank=True)
    target_id = models.CharField(_("identifikátor cieľa"), max_length=100, blank=True)
    reason = models.TextField(_("dôvod"), blank=True)
    metadata = models.JSONField(_("metadáta"), default=dict, blank=True)
    created_at = models.DateTimeField(_("vytvorené"), auto_now_add=True)

    class Meta:
        verbose_name = _("audítny záznam")
        verbose_name_plural = _("audítne záznamy")
        ordering = ("-created_at", "-id")
        indexes = [
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["target_type", "target_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.action}"

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise AuditError("Audítne záznamy sú nemenné a nedajú sa upraviť.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise AuditError("Audítne záznamy sa nedajú vymazať.")
