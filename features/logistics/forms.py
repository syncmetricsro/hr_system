from __future__ import annotations

from django import forms
from django.db.models import Count, F, Q
from django.utils.translation import gettext_lazy as _

from core.accounts.models import Role
from core.projects.models import Project
from features.logistics.models import (
    Accommodation, Room, RoomAssignmentStatus, TransportWeek,
)


def transport_projects(user):
    projects = Project.objects.filter(is_active=True)
    if getattr(user, "role", None) == Role.COORDINATOR:
        projects = projects.filter(responsible_coordinators=user)
    return projects.distinct().order_by("name")


class TransportWeekForm(forms.ModelForm):
    class Meta:
        model = TransportWeek
        fields = ("project", "week_start", "headcount", "note")
        widgets = {
            "week_start": forms.DateInput(attrs={"type": "date"}),
            "note": forms.Textarea(attrs={"rows": 2}),
        }
        labels = {"note": _("Operational note")}

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = transport_projects(user)


class AccommodationForm(forms.ModelForm):
    class Meta:
        model = Accommodation
        fields = ("name", "address", "notes", "is_active")
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def clean_is_active(self):
        active = self.cleaned_data["is_active"]
        if (
            not active and self.instance.pk
            and self.instance.rooms.filter(
                assignments__status=RoomAssignmentStatus.ACTIVE
            ).exists()
        ):
            raise forms.ValidationError(_("Release all occupants before deactivating this location."))
        return active


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ("label", "capacity", "monthly_rate", "is_active")
        widgets = {"monthly_rate": forms.NumberInput(attrs={"step": "0.01", "min": "0"})}

    def clean(self):
        cleaned = super().clean()
        if not self.instance.pk:
            return cleaned
        occupancy = self.instance.occupancy()
        capacity = cleaned.get("capacity")
        if capacity is not None and capacity < occupancy:
            self.add_error("capacity", _("Capacity cannot be lower than current occupancy."))
        if cleaned.get("is_active") is False and occupancy:
            self.add_error("is_active", _("Release all occupants before deactivating this room."))
        return cleaned


def assignable_rooms():
    return Room.objects.filter(
        is_active=True, accommodation__is_active=True,
    ).annotate(
        active_occupancy=Count(
            "assignments", filter=Q(assignments__status=RoomAssignmentStatus.ACTIVE)
        )
    ).filter(active_occupancy__lt=F("capacity")).select_related("accommodation")
