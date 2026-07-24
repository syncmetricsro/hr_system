from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.media import certificate_upload_path


class CertificateCategory(models.TextChoices):
    HEALTH = "HEALTH", _("Health")
    FORKLIFT = "FORKLIFT", _("Forklift")
    CRANE = "CRANE", _("Crane")
    WELDING = "WELDING", _("Welding")
    OTHER = "OTHER", _("Other")


class Certificate(models.Model):
    """A worker certificate/document with an expiry (plan §11.9). Supports an
    optional uploaded document — image or PDF, validated and re-encoded on
    upload (docs/product/certificate-upload-design.md) — alongside the
    dates-only metadata this model started with."""

    person = models.ForeignKey(
        "people.Person", on_delete=models.CASCADE, related_name="certificates", verbose_name=_("person")
    )
    category = models.CharField(
        _("category"), max_length=20, choices=CertificateCategory.choices, default=CertificateCategory.OTHER
    )
    name = models.CharField(_("name"), max_length=120)
    issue_date = models.DateField(_("issue date"), null=True, blank=True)
    expiry_date = models.DateField(_("expiry date"), null=True, blank=True)
    document = models.FileField(_("document"), upload_to=certificate_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("certificate")
        verbose_name_plural = _("certificates")
        ordering = ("expiry_date",)

    def __str__(self) -> str:
        return f"{self.name} ({self.person})"
