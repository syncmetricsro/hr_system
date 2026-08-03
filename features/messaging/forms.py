"""Forms for offer authoring and offer-email sending (ADR 0029)."""

from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from features.messaging.models import JobOffer, OfferEmailKind, OfferEmailTemplate


class JobOfferForm(forms.ModelForm):
    class Meta:
        model = JobOffer
        fields = [
            "title",
            "project",
            "office",
            "location",
            "wage",
            "wage_unit",
            "currency",
            "start_date",
            "terms",
            "is_active",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "terms": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, office_queryset=None, project_queryset=None, **kwargs):
        """``office_queryset``/``project_queryset`` are the caller's *scoped*
        querysets. Passing them in keeps ADR 0026 in the view, where the request
        user is in hand — a form that fetched all offices itself would hand a
        manager a dropdown of every other office."""
        super().__init__(*args, **kwargs)
        if office_queryset is not None:
            self.fields["office"].queryset = office_queryset
        if project_queryset is not None:
            self.fields["project"].queryset = project_queryset

    def clean(self):
        cleaned = super().clean()
        project = cleaned.get("project")
        office = cleaned.get("office")
        # An offer on a project belongs to that project's office. Silently
        # allowing a mismatch would let an offer be authored in one office and
        # be invisible to the people who own the work.
        if (
            project is not None
            and office is not None
            and project.office_id != office.pk
        ):
            self.add_error("office", _("This project belongs to a different office."))
        if project is not None and office is None:
            cleaned["office"] = project.office
            self.instance.office = project.office
        return cleaned


class OfferEmailTemplateForm(forms.ModelForm):
    class Meta:
        model = OfferEmailTemplate
        fields = ["kind", "language", "subject", "body", "is_active"]
        widgets = {"body": forms.Textarea(attrs={"rows": 12})}


class SendOfferEmailForm(forms.Form):
    """The per-person panel form."""

    offer = forms.ModelChoiceField(
        label=_("job offer"), queryset=JobOffer.objects.none()
    )
    kind = forms.ChoiceField(label=_("email type"), choices=OfferEmailKind.choices)

    def __init__(self, *args, offer_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if offer_queryset is not None:
            self.fields["offer"].queryset = offer_queryset


class BulkOfferEmailForm(forms.Form):
    """The bulk send page. ``confirm`` is required so reaching this URL with a
    replayed POST cannot start a campaign."""

    kind = forms.ChoiceField(label=_("email type"), choices=OfferEmailKind.choices)
    lifecycle_status = forms.ChoiceField(
        label=_("lifecycle status"), choices=(), required=False
    )
    office = forms.ModelChoiceField(
        label=_("office"),
        queryset=None,
        required=False,
        empty_label=_("All my offices"),
    )
    confirm = forms.BooleanField(
        label=_("I have reviewed the recipient list"), required=True
    )

    def __init__(self, *args, office_queryset=None, status_choices=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["lifecycle_status"].choices = [("", _("Any"))] + list(
            status_choices
        )
        if office_queryset is not None:
            self.fields["office"].queryset = office_queryset
        else:
            self.fields.pop("office")
