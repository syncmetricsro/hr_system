from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class MessageTemplate(models.Model):
    """Manager-managed SMS template (plan §11.12 / messaging spec)."""

    name = models.CharField(_("name"), max_length=120)
    body = models.TextField(_("body"))
    is_active = models.BooleanField(_("active"), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="message_templates"
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("message template")
        verbose_name_plural = _("message templates")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class OutboundMessage(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", _("Queued")
        SENT = "sent", _("Sent")
        FAILED = "failed", _("Failed")

    person = models.ForeignKey(
        "people.Person", on_delete=models.SET_NULL, null=True, blank=True, related_name="messages", verbose_name=_("person")
    )
    to_number = models.CharField(_("to"), max_length=40)
    body = models.TextField(_("body"))
    status = models.CharField(_("status"), max_length=20, choices=Status.choices, default=Status.QUEUED)
    provider_sid = models.CharField(_("provider id"), max_length=64, blank=True)
    error = models.CharField(_("error"), max_length=300, blank=True)
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_messages"
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("outbound message")
        verbose_name_plural = _("outbound messages")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"-> {self.to_number} ({self.status})"


class InboundMessage(models.Model):
    from_number = models.CharField(_("from"), max_length=40)
    body = models.TextField(_("body"), blank=True)
    provider_sid = models.CharField(_("provider id"), max_length=64, blank=True)
    received_at = models.DateTimeField(_("received"), auto_now_add=True)

    class Meta:
        verbose_name = _("inbound message")
        verbose_name_plural = _("inbound messages")
        ordering = ("-received_at",)

    def __str__(self) -> str:
        return f"<- {self.from_number}"
