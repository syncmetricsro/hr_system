from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.people.models import Person


class PersonForm(forms.ModelForm):
    """Simplified recruiter intake (the full hard-gated questionnaire is later)."""

    class Meta:
        model = Person
        fields = [
            "first_name", "last_name", "phone", "address", "nationality",
            "preferred_language", "date_of_birth", "place_of_birth",
            "has_disability", "disability_type",
        ]
        labels = {
            "first_name": _("First name"),
            "last_name": _("Last name"),
            "phone": _("Phone"),
            "address": _("Address"),
            "nationality": _("Nationality"),
            "preferred_language": _("Preferred language"),
            "date_of_birth": _("Date of birth"),
            "place_of_birth": _("Place of birth"),
            "has_disability": _("Has disability"),
            "disability_type": _("Disability type"),
        }
        widgets = {"date_of_birth": forms.DateInput(attrs={"type": "date"})}
