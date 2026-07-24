from __future__ import annotations

from django import forms

from features.compliance.models import Certificate


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ["category", "name", "issue_date", "expiry_date"]
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
        }
