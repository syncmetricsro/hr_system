from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from django import forms
from django.db.models import Count, F, Q
from django.utils.translation import gettext_lazy as _

from core.accounts.models import Role
from core.projects.models import Project
from features.logistics.models import (
    Accommodation, AccommodationCostPeriod, EquipmentItem, Room,
    RoomAssignmentStatus, TransportWeek,
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
    """``capacity``/``per_head_cost`` are not model fields — filling both in on
    creation records an initial ``AccommodationCostPeriod`` for the current
    month (features/logistics/views.py::accommodation_create), the same data
    entered later, one step earlier. Left off ``accommodation_edit`` to avoid
    a bare pair of inputs on the edit form that silently do nothing."""

    capacity = forms.IntegerField(
        label=_("Capacity (beds)"), required=False, min_value=1,
    )
    per_head_cost = forms.DecimalField(
        label=_("Per-head monthly cost (EUR)"), required=False, min_value=Decimal("0"),
        decimal_places=2, widget=forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
    )

    class Meta:
        model = Accommodation
        fields = ("name", "address", "notes", "is_active")
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            del self.fields["capacity"]
            del self.fields["per_head_cost"]

    def clean(self):
        cleaned = super().clean()
        capacity = cleaned.get("capacity")
        per_head_cost = cleaned.get("per_head_cost")
        if "capacity" in self.fields and (capacity is None) != (per_head_cost is None):
            raise forms.ValidationError(
                _("Enter both capacity and per-head cost to record a cost period, or leave both blank.")
            )
        return cleaned

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


class AccommodationCostPeriodForm(forms.ModelForm):
    effective_month = forms.DateField(
        label=_("Effective month"), input_formats=["%Y-%m"],
        widget=forms.DateInput(format="%Y-%m", attrs={"type": "month"}),
    )

    class Meta:
        model = AccommodationCostPeriod
        fields = ("effective_month", "capacity", "per_head_cost")
        widgets = {
            "per_head_cost": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }

    def clean_effective_month(self):
        value = self.cleaned_data["effective_month"]
        return value.replace(day=1)


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


class EquipmentItemForm(forms.ModelForm):
    """Manager-maintained catalogue data; issuing remains a coordinator action."""

    class Meta:
        model = EquipmentItem
        fields = ("name", "size", "unit_price", "is_active")
        widgets = {
            "unit_price": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }


class StockReceiptForm(forms.Form):
    operation_key = forms.UUIDField(widget=forms.HiddenInput, initial=uuid4)
    received_on = forms.DateField(label=_("Received on"), widget=forms.DateInput(attrs={"type": "date"}))
    reference = forms.CharField(label=_("Reference"), max_length=120, required=False)
    supplier = forms.CharField(label=_("Supplier"), max_length=200, required=False)
    note = forms.CharField(label=_("Note"), max_length=300, required=False)


class StockReceiptLineForm(forms.Form):
    item = forms.ModelChoiceField(label=_("Item"), queryset=EquipmentItem.objects.none(), required=False)
    quantity = forms.IntegerField(label=_("Quantity"), min_value=1, required=False)
    total_value = forms.DecimalField(label=_("Total value"), min_value=0, decimal_places=2, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item"].queryset = EquipmentItem.objects.filter(is_active=True)

    def clean(self):
        cleaned = super().clean()
        values = (cleaned.get("item"), cleaned.get("quantity"), cleaned.get("total_value"))
        if any(value not in (None, "") for value in values) and not all(value not in (None, "") for value in values):
            raise forms.ValidationError(_("Complete the item, quantity, and total value."))
        return cleaned


StockReceiptLineFormSet = forms.formset_factory(StockReceiptLineForm, extra=4, max_num=12)


class StockAdjustmentForm(forms.Form):
    item = forms.ModelChoiceField(label=_("Item"), queryset=EquipmentItem.objects.none())
    occurred_on = forms.DateField(label=_("Date"), widget=forms.DateInput(attrs={"type": "date"}))
    quantity_delta = forms.IntegerField(label=_("Quantity adjustment"))
    value = forms.DecimalField(label=_("Value for positive adjustment"), min_value=0, decimal_places=2, required=False)
    reason = forms.CharField(label=_("Reason"), max_length=300)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item"].queryset = EquipmentItem.objects.filter(is_active=True)

    def clean(self):
        cleaned = super().clean()
        quantity = cleaned.get("quantity_delta")
        if quantity == 0:
            self.add_error("quantity_delta", _("The adjustment cannot be zero."))
        if quantity and quantity > 0 and cleaned.get("value") is None:
            self.add_error("value", _("A value is required when adding stock."))
        return cleaned


def assignable_rooms():
    return Room.objects.filter(
        is_active=True, accommodation__is_active=True,
    ).annotate(
        active_occupancy=Count(
            "assignments", filter=Q(assignments__status=RoomAssignmentStatus.ACTIVE)
        )
    ).filter(active_occupancy__lt=F("capacity")).select_related("accommodation")
