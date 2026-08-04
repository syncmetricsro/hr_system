from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from core.accounts.models import Role
from core.accounts.permissions import user_office_scope
from core.offices.forms import apply_office_scope
from core.people.models import LifecycleStatus, Person
from core.projects.models import Project, TrialAssignment
from core.ui.forms import datetime_input


def operable_projects(user):
    projects = Project.objects.filter(is_active=True)
    if getattr(user, "role", None) == Role.COORDINATOR:
        projects = projects.filter(responsible_coordinators=user)
    scope = user_office_scope(user)
    if scope is not None:
        projects = projects.filter(office__in=scope)
    return projects.distinct().order_by("name")


class TrialCreateForm(forms.Form):
    person = forms.ModelChoiceField(
        label=_("Candidate"),
        queryset=Person.objects.none(),
        help_text=_("Only available candidates can be scheduled."),
    )
    project = forms.ModelChoiceField(
        label=_("Project"), queryset=Project.objects.none()
    )
    scheduled_for = forms.DateTimeField(
        label=_("Arrival time"),
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=datetime_input(format="%Y-%m-%dT%H:%M"),
    )
    note = forms.CharField(
        label=_("Operational note"),
        required=False,
        max_length=300,
        widget=forms.Textarea(attrs={"rows": 2}),
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["person"].queryset = Person.objects.filter(
            lifecycle_status=LifecycleStatus.AVAILABLE
        ).order_by("last_name", "first_name")
        self.fields["project"].queryset = operable_projects(user)


class TrialEditForm(forms.Form):
    project = forms.ModelChoiceField(
        label=_("Project"), queryset=Project.objects.none()
    )
    scheduled_for = forms.DateTimeField(
        label=_("Arrival time"),
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=datetime_input(format="%Y-%m-%dT%H:%M"),
    )
    note = forms.CharField(
        label=_("Operational note"),
        required=False,
        max_length=300,
        widget=forms.Textarea(attrs={"rows": 2}),
    )

    def __init__(self, *args, user, trial: TrialAssignment, **kwargs):
        kwargs.setdefault(
            "initial",
            {
                "project": trial.project_id,
                "scheduled_for": trial.scheduled_for,
                "note": trial.note,
            },
        )
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = operable_projects(user)


class ProjectForm(forms.ModelForm):
    """Create/edit a project (production-readiness item 15).

    `Action.PROJECT_MANAGE` was granted to Manager in both clients and
    implemented nowhere: there were no create, edit or archive routes, so a
    project could only be added through the demo seed, a shell, or Django admin
    - which needs a superuser no client role has, and bypasses the service
    layer, so it wrote no audit event and honoured no office boundary.

    Mirrors `features.logistics.forms.AccommodationForm`, which is the same
    shape: a manager-managed, office-scoped master record.

    Two fields carry more weight than they look like they do:

    * ``code`` is ``unique=True``. A duplicate must surface as a field error
      rather than an IntegrityError - ModelForm gives that for free, and a test
      pins it so it stays that way.
    * ``responsible_coordinators`` is restricted to coordinators of the chosen
      office. A coordinator from elsewhere would be formally responsible for a
      project they get a 403 on, which "reads as broken data the moment anyone
      asks who runs the Győr contracts" - the exact bug corrected in the demo
      seed on 2026-07-26. The form must not reintroduce it by hand.
    """

    class Meta:
        model = Project
        fields = [
            "name",
            "partner",
            "code",
            "office",
            "responsible_coordinators",
            "financial_reporting_eligible",
            "notes",
            "is_active",
        ]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}
        labels = {"financial_reporting_eligible": _("Include this project in Finance")}
        help_texts = {
            "code": _("Short unique reference, for example DHLBA. Cannot be reused."),
            "financial_reporting_eligible": _(
                "Unticking hides this project's months from Finance. The figures "
                "are kept, not deleted."
            ),
            "responsible_coordinators": _(
                "Only coordinators of the selected office can be chosen."
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        apply_office_scope(self, user)
        self.fields["responsible_coordinators"].queryset = self._coordinators(user)
        self.fields["responsible_coordinators"].required = False
        if "office" not in self.fields:
            # No offices exist, so the picker is gone and the help text that
            # promised office narrowing would describe a boundary the install
            # does not have.
            self.fields["responsible_coordinators"].help_text = _(
                "Coordinators responsible for this project."
            )

    def _coordinators(self, user):
        """Coordinators the chosen office may draw on.

        Narrowed to the project's own office once one is known - from the
        instance on edit, from the posted value on a resubmitted create. Before
        either exists, fall back to the coordinators this user could pick at
        all, so a blank form is never silently empty.
        """
        from core.accounts.models import User

        coordinators = User.objects.filter(role=Role.COORDINATOR, is_active=True)
        office_id = self.data.get("office") or getattr(self.instance, "office_id", None)
        if office_id:
            return coordinators.filter(offices__id=office_id).distinct()
        scope = user_office_scope(user)
        if scope is not None:
            return coordinators.filter(offices__in=scope).distinct()
        return coordinators.distinct()

    def clean(self):
        cleaned = super().clean()
        office = cleaned.get("office")
        chosen = cleaned.get("responsible_coordinators")
        if office and chosen:
            stray = [c for c in chosen if not c.offices.filter(pk=office.pk).exists()]
            if stray:
                self.add_error(
                    "responsible_coordinators",
                    _(
                        "%(names)s do not belong to this office and would have no "
                        "access to the project."
                    )
                    % {"names": ", ".join(str(c) for c in stray)},
                )
        return cleaned
