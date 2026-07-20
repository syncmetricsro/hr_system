from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from core.people.models import Person
from features.wage_ledger.models import WageEntry


class WageEntryForm(forms.ModelForm):
    class Meta:
        model = WageEntry
        fields = ("person", "period", "gross_amount", "note")
        labels = {
            "period": _("Wage month (YYYY-MM)"),
            "gross_amount": _("Gross wage (EUR)"),
        }
        widgets = {
            "period": forms.TextInput(attrs={"placeholder": "2026-07"}),
            "gross_amount": forms.NumberInput(attrs={"min": "0.01", "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["person"].queryset = Person.objects.filter(
            is_archived=False
        ).order_by("last_name", "first_name")
