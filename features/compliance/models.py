from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.media import certificate_upload_path


class CertificateCategory(models.TextChoices):
    HEALTH = "HEALTH", _("Health")
    FORKLIFT = "FORKLIFT", _("Forklift")
    CRANE = "CRANE", _("Crane")
    WELDING = "WELDING", _("Welding")
    OTHER = "OTHER", _("Other")


class CertificateRecordStatus(models.TextChoices):
    ACTIVE = "ACTIVE", _("Active")
    SUPERSEDED = "SUPERSEDED", _("Superseded")
    ARCHIVED = "ARCHIVED", _("Archived")


FILE_ALLOWED_CATEGORIES = frozenset(
    {
        CertificateCategory.FORKLIFT,
        CertificateCategory.CRANE,
        CertificateCategory.WELDING,
    }
)

CANONICAL_CERTIFICATE_NAMES = {
    CertificateCategory.FORKLIFT: "Forklift licence",
    CertificateCategory.CRANE: "Crane licence",
    CertificateCategory.WELDING: "Welding licence",
}


class Certificate(models.Model):
    """Occupational-certificate files plus historical metadata-only rows.

    New active forklift/crane/welding records require a validated primary
    file. Historical health/other rows remain readable without becoming a
    generic attachment path (docs/product/certificate-upload-design.md).
    """

    person = models.ForeignKey(
        "people.Person",
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name=_("person"),
    )
    category = models.CharField(
        _("category"),
        max_length=20,
        choices=CertificateCategory.choices,
        default=CertificateCategory.OTHER,
    )
    name = models.CharField(_("name"), max_length=120)
    issuer = models.CharField(_("issuer"), max_length=160, blank=True)
    certificate_number = models.CharField(
        _("certificate number"), max_length=100, blank=True
    )
    issue_date = models.DateField(_("issue date"), null=True, blank=True)
    expiry_date = models.DateField(_("expiry date"), null=True, blank=True)
    never_expires = models.BooleanField(_("does not expire"), default=False)
    front_document = models.FileField(
        _("front or PDF"), upload_to=certificate_upload_path, blank=True, null=True
    )
    back_document = models.FileField(
        _("back"), upload_to=certificate_upload_path, blank=True, null=True
    )
    record_status = models.CharField(
        _("record status"),
        max_length=20,
        choices=CertificateRecordStatus.choices,
        default=CertificateRecordStatus.ACTIVE,
    )
    supersedes = models.OneToOneField(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="renewed_by",
        verbose_name=_("supersedes"),
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("certificate")
        verbose_name_plural = _("certificates")
        ordering = ("expiry_date",)

    def __str__(self) -> str:
        return f"{self.name} ({self.person})"

    @property
    def allows_document_upload(self) -> bool:
        return self.category in FILE_ALLOWED_CATEGORIES

    @property
    def is_current(self) -> bool:
        return self.record_status == CertificateRecordStatus.ACTIVE

    def clean(self) -> None:
        super().clean()
        errors: dict[str, str] = {}
        non_field_errors: list[str] = []
        pending_front = bool(
            self.front_document or getattr(self, "_pending_front_document", False)
        )
        pending_back = bool(
            self.back_document or getattr(self, "_pending_back_document", False)
        )

        if self.never_expires and self.expiry_date:
            errors["expiry_date"] = _(
                "Choose an expiry date or mark the certificate as not expiring, not both."
            )
        elif not self.never_expires and not self.expiry_date:
            errors["expiry_date"] = _(
                "Enter an expiry date or mark the certificate as not expiring."
            )

        if self.category not in FILE_ALLOWED_CATEGORIES:
            if pending_front or pending_back:
                non_field_errors.append(
                    _(
                        "Files are allowed only for forklift, crane, and welding certificates."
                    )
                )
            if self.category == CertificateCategory.OTHER and self._state.adding:
                errors["category"] = _(
                    "Choose a supported occupational certificate type."
                )
        elif self.record_status == CertificateRecordStatus.ACTIVE and not pending_front:
            non_field_errors.append(_("Upload the certificate front, scan, or PDF."))

        if pending_back and not pending_front:
            non_field_errors.append(_("Upload the front before adding the back."))

        front_name = (getattr(self.front_document, "name", "") or "").lower()
        back_name = (getattr(self.back_document, "name", "") or "").lower()
        if pending_back and (front_name.endswith(".pdf") or back_name.endswith(".pdf")):
            non_field_errors.append(
                _("A PDF must be the only file; the back side must be an image.")
            )

        if self.supersedes_id and self.supersedes_id == self.pk:
            errors["supersedes"] = _("A certificate cannot supersede itself.")

        if errors or non_field_errors:
            if non_field_errors:
                errors["__all__"] = non_field_errors
            raise ValidationError(errors)
