from __future__ import annotations

from django.contrib import admin

from apps.people.models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "lifecycle_status", "owning_recruiter", "is_archived")
    list_filter = ("lifecycle_status", "has_disability", "is_archived")
    search_fields = ("search_name", "phone")
    readonly_fields = ("search_name", "created_at", "updated_at", "archived_at")
