from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class Certificate(models.Model):
    """A worker certificate/document with an expiry (plan §11.9, metadata only —
    no file storage; matches the demo decision of dates-only certificates)."""

    person = models.ForeignKey(
        "people.Person", on_delete=models.CASCADE, related_name="certificates", verbose_name=_("person")
    )
    name = models.CharField(_("name"), max_length=120)
    issue_date = models.DateField(_("issue date"), null=True, blank=True)
    expiry_date = models.DateField(_("expiry date"), null=True, blank=True)
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("certificate")
        verbose_name_plural = _("certificates")
        ordering = ("expiry_date",)

    def __str__(self) -> str:
        return f"{self.name} ({self.person})"
