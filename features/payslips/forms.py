from __future__ import annotations

from django import forms
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from core.offices.scoping import scope_people
from core.people.models import Person
from features.payslips.models import Payslip


class PayslipPersonChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        label = str(obj)
        if not obj.email:
            label += f" — {gettext('no email!')}"
        return label


class PayslipForm(forms.ModelForm):
    person = PayslipPersonChoiceField(queryset=Person.objects.none(), label=_("Person"))
    issue_date = forms.DateField(
        required=False,
        label=_("Payslip date (optional)"),
        help_text=_("If left blank, the creation date is used."),
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = Payslip
        fields = ("person", "period", "net_amount", "issue_date", "note")
        labels = {
            "period": _("Period (YYYY-MM)"),
            "net_amount": _("Net amount (EUR)"),
        }
        widgets = {
            "period": forms.TextInput(attrs={"placeholder": "2026-07"}),
            "net_amount": forms.NumberInput(attrs={"min": "0.01", "step": "0.01"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        """``user`` scopes the person picker (ADR 0026).

        Without it the dropdown offered every worker in the company, so a
        manager could record - and then email - a payslip against another
        office's person. Passed in rather than read from a global so the
        boundary stays visible in the view, where the request is.
        """
        super().__init__(*args, **kwargs)
        people = Person.objects.order_by("last_name", "first_name")
        if user is not None:
            people = scope_people(people, user)
        self.fields["person"].queryset = people
