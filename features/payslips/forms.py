from __future__ import annotations

from django import forms
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from core.offices.scoping import scope_people
from core.people.models import Person
from core.ui.forms import date_input, month_text_input
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
        widget=date_input(),
    )

    class Meta:
        model = Payslip
        fields = ("person", "period", "net_amount", "issue_date", "note")
        labels = {
            "period": _("Pay month"),
            "net_amount": _("Net amount (EUR)"),
        }
        help_texts = {
            "period": _(
                "The calendar month this payslip pays for, not the month it was "
                "issued in. One payslip per person per month."
            ),
            "net_amount": _(
                "The net figure printed on the payslip, as paid. It is shown "
                "beside the gross wage and the ledger deductions for the same "
                "month; the system does not calculate it."
            ),
        }
        widgets = {
            # A month picker rather than a text box: the model's YYYY-MM
            # validator accepts exactly what this posts, and the office no
            # longer has to know the format to record a payslip for July.
            "period": month_text_input(),
            "net_amount": forms.NumberInput(
                attrs={"min": "0.01", "step": "0.01", "inputmode": "decimal"}
            ),
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
