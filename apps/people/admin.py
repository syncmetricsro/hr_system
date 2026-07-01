from __future__ import annotations

from django.contrib import admin

from apps.people.models import InactiveReason, Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "lifecycle_status", "inactive_reason", "owning_recruiter", "is_archived")
    list_filter = ("lifecycle_status", "inactive_reason", "has_disability", "is_archived")
    search_fields = ("search_name", "phone")
    readonly_fields = ("search_name", "created_at", "updated_at", "archived_at")


@admin.register(InactiveReason)
class InactiveReasonAdmin(admin.ModelAdmin):
    list_display = ("label", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("label",)
