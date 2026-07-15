from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from core.accounts.models import Role
from core.people.models import LifecycleStatus, Person
from core.projects.models import Project, TrialAssignment


def operable_projects(user):
    projects = Project.objects.filter(is_active=True)
    if getattr(user, "role", None) == Role.COORDINATOR:
        projects = projects.filter(responsible_coordinators=user)
    return projects.distinct().order_by("name")


class TrialCreateForm(forms.Form):
    person = forms.ModelChoiceField(
        label=_("Candidate"), queryset=Person.objects.none(),
        help_text=_("Only available candidates can be scheduled."),
    )
    project = forms.ModelChoiceField(label=_("Project"), queryset=Project.objects.none())
    scheduled_for = forms.DateTimeField(
        label=_("Arrival time"),
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}),
    )
    note = forms.CharField(
        label=_("Operational note"), required=False, max_length=300,
        widget=forms.Textarea(attrs={"rows": 2}),
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["person"].queryset = Person.objects.filter(
            lifecycle_status=LifecycleStatus.AVAILABLE
        ).order_by("last_name", "first_name")
        self.fields["project"].queryset = operable_projects(user)


class TrialEditForm(forms.Form):
    project = forms.ModelChoiceField(label=_("Project"), queryset=Project.objects.none())
    scheduled_for = forms.DateTimeField(
        label=_("Arrival time"),
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}),
    )
    note = forms.CharField(
        label=_("Operational note"), required=False, max_length=300,
        widget=forms.Textarea(attrs={"rows": 2}),
    )

    def __init__(self, *args, user, trial: TrialAssignment, **kwargs):
        kwargs.setdefault("initial", {
            "project": trial.project_id,
            "scheduled_for": trial.scheduled_for,
            "note": trial.note,
        })
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = operable_projects(user)
