from __future__ import annotations

from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.accounts.permissions import user_office_scope
from core.offices.models import Office
from core.ui import registry
from core.people.models import Person


class PersonForm(forms.ModelForm):
    """Simplified recruiter intake (the full hard-gated questionnaire is later).

    Feature apps contribute extra, non-persisted fields (e.g. the blacklist's
    ID-check field) via the core registry's form extensions — the fields are
    injected here and their post-create handlers run in ``person_create``.
    """

    class Meta:
        model = Person
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "nationality",
            "preferred_language",
            "date_of_birth",
            "place_of_birth",
            "has_disability",
            "disability_type",
            "office",
        ]
        labels = {
            "first_name": _("First name"),
            "last_name": _("Last name"),
            "email": _("Email"),
            "phone": _("Phone"),
            "address": _("Address"),
            "nationality": _("Nationality"),
            "preferred_language": _("Preferred language"),
            "date_of_birth": _("Date of birth"),
            "place_of_birth": _("Place of birth"),
            "has_disability": _("Has disability"),
            "disability_type": _("Disability type"),
            "office": _("Office"),
        }
        widgets = {"date_of_birth": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        for extension in registry.person_form_extensions:
            self.fields.update(extension.fields())
        # Alpine only controls this local presentation state.  The clean()
        # method below remains the server-side authority for the data.
        self.fields["has_disability"].widget.attrs["x-model"] = "hasDisability"
        self.fields["disability_type"].widget.attrs["x-bind:disabled"] = (
            "!hasDisability"
        )
        # Office scoping (ADR 0026 Phase B): offer only the offices the acting
        # user themself belongs to; unrestricted roles (Observer, superuser)
        # or installs with no offices at all (CorvinumEU) see every office.
        scope = user_office_scope(user)
        offices = Office.objects.all() if scope is None else scope
        self.fields["office"].queryset = offices
        if scope is not None and not self.initial.get("office") and scope.count() == 1:
            self.fields["office"].initial = scope.first()

    def clean(self):
        cleaned_data = super().clean()
        # Do not retain sensitive disability-detail data after the operator
        # explicitly says that the person does not have a disability.
        if not cleaned_data.get("has_disability"):
            cleaned_data["disability_type"] = ""
        return cleaned_data

    def clean_date_of_birth(self):
        value = self.cleaned_data.get("date_of_birth")
        if value and value > timezone.localdate():
            raise forms.ValidationError(_("Date of birth cannot be in the future."))
        return value
