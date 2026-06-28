from __future__ import annotations

from django.contrib import admin

from apps.logistics.models import Accommodation, Room, RoomAssignment


class RoomInline(admin.TabularInline):
    model = Room
    extra = 0


@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "address")
    inlines = [RoomInline]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("accommodation", "label", "capacity")
    list_filter = ("accommodation",)


@admin.register(RoomAssignment)
class RoomAssignmentAdmin(admin.ModelAdmin):
    list_display = ("person", "room", "status", "start_date", "end_date")
    list_filter = ("status",)
    search_fields = ("person__search_name",)
