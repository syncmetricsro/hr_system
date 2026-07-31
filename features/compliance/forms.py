from __future__ import annotations

from pathlib import PurePath

from django import forms
from django.utils.translation import gettext_lazy as _

from features.compliance.models import (
    CANONICAL_CERTIFICATE_NAMES,
    FILE_ALLOWED_CATEGORIES,
    Certificate,
    CertificateCategory,
)


OCCUPATIONAL_CATEGORY_CHOICES = [
    choice
    for choice in CertificateCategory.choices
    if choice[0] in FILE_ALLOWED_CATEGORIES
]


def _looks_like_pdf(uploaded_file) -> bool:
    return (uploaded_file.content_type or "").lower() == "application/pdf" or (
        uploaded_file.name or ""
    ).lower().endswith(".pdf")


class CertificateForm(forms.ModelForm):
    category = forms.ChoiceField(
        label=_("certificate type"), choices=OCCUPATIONAL_CATEGORY_CHOICES
    )
    front_upload = forms.FileField(
        label=_("front, paper scan, or PDF"),
        required=False,
        widget=forms.ClearableFileInput(
            attrs={"accept": "image/jpeg,image/png,image/webp,application/pdf"}
        ),
    )
    back_upload = forms.FileField(
        label=_("back (image only)"),
        required=False,
        widget=forms.ClearableFileInput(
            attrs={"accept": "image/jpeg,image/png,image/webp"}
        ),
    )
    remove_back = forms.BooleanField(label=_("remove the current back"), required=False)

    class Meta:
        model = Certificate
        fields = [
            "category",
            "issuer",
            "certificate_number",
            "issue_date",
            "expiry_date",
            "never_expires",
        ]
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        locked_category = kwargs.pop("locked_category", None)
        super().__init__(*args, **kwargs)
        if self.instance.pk or locked_category:
            category = locked_category or self.instance.category
            self.fields["category"].disabled = True
            self.fields["category"].choices = [
                (
                    category,
                    dict(CertificateCategory.choices)[category],
                )
            ]
            self.initial["category"] = category
        if self.instance.pk:
            if not self.instance.back_document:
                self.fields.pop("remove_back")
        else:
            self.fields["front_upload"].required = True
            self.fields.pop("remove_back")

    def clean(self):
        cleaned = super().clean()
        front = cleaned.get("front_upload")
        back = cleaned.get("back_upload")
        remove_back = cleaned.get("remove_back", False)
        self.instance._pending_front_document = bool(front)  # noqa: SLF001
        self.instance._pending_back_document = bool(back)  # noqa: SLF001

        if back and _looks_like_pdf(back):
            self.add_error("back_upload", _("The back side must be an image."))

        front_is_pdf = bool(front and _looks_like_pdf(front))
        existing_front_is_pdf = bool(
            self.instance.pk
            and self.instance.front_document
            and PurePath(self.instance.front_document.name).suffix.lower() == ".pdf"
        )
        if back and (front_is_pdf or (not front and existing_front_is_pdf)):
            self.add_error(
                "back_upload", _("A PDF must be the only file for a certificate.")
            )
        if front_is_pdf and self.instance.back_document and not remove_back:
            self.add_error(
                "front_upload",
                _(
                    "Remove the current back side before replacing the certificate with a PDF."
                ),
            )

        if cleaned.get("never_expires"):
            cleaned["expiry_date"] = None
        elif not cleaned.get("expiry_date"):
            self.add_error(
                "expiry_date", _("Enter an expiry date or select does not expire.")
            )

        category = cleaned.get("category")
        if category in CANONICAL_CERTIFICATE_NAMES:
            self.instance.name = CANONICAL_CERTIFICATE_NAMES[category]
        return cleaned


class CertificateReasonForm(forms.Form):
    reason = forms.CharField(
        label=_("reason"),
        max_length=500,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
