from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from core.people.models import Person
from core.ui.forms import month_text_input
from features.wage_ledger.models import WageEntry


class WageEntryForm(forms.ModelForm):
    class Meta:
        model = WageEntry
        fields = ("person", "period", "gross_amount", "note")
        labels = {
            "period": _("Wage month"),
            "gross_amount": _("Gross wage (EUR)"),
        }
        help_texts = {
            "person": _(
                "The worker who earned this wage. One gross figure per person "
                "per month."
            ),
            "period": _(
                "The calendar month the wage was earned in, not the month it "
                "was paid out."
            ),
            "gross_amount": _(
                "Gross, before anything is taken off. Ledger deductions are "
                "subtracted from this on the worker's pay overview; tax and "
                "levies are not calculated here."
            ),
            "note": _(
                "Where this figure came from - a contract, a timesheet, the "
                "accountant. It is what the next reader checks it against."
            ),
        }
        widgets = {
            "period": month_text_input(),
            "gross_amount": forms.NumberInput(
                attrs={"min": "0.01", "step": "0.01", "inputmode": "decimal"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["person"].queryset = Person.objects.filter(
            is_archived=False
        ).order_by("last_name", "first_name")
