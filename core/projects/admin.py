from __future__ import annotations

from django.contrib import admin

from core.projects.models import (
    Project,
    ProjectAssignment,
    ReadinessRecord,
    TrialAssignment,
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "region", "office", "is_active", "financial_reporting_eligible")
    list_filter = ("is_active", "office")
    search_fields = ("name", "code", "partner", "region")
    filter_horizontal = ("responsible_coordinators",)


@admin.register(ProjectAssignment)
class ProjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ("person", "project", "status", "start_date", "end_date", "assigned_by")
    list_filter = ("status", "project")
    search_fields = ("person__search_name", "project__code")
    readonly_fields = ("coordinator_snapshot", "created_at", "updated_at")


@admin.register(TrialAssignment)
class TrialAssignmentAdmin(admin.ModelAdmin):
    list_display = ("person", "project", "scheduled_date", "state", "outcome", "outcome_recorded_by")
    list_filter = ("state", "outcome", "project")
    search_fields = ("person__search_name", "project__code")
    readonly_fields = ("outcome_recorded_at", "created_at")


@admin.register(ReadinessRecord)
class ReadinessRecordAdmin(admin.ModelAdmin):
    list_display = ("person", "project", "medical_state", "gear_state", "accommodation_state", "transport_state")
    list_filter = ("project",)
    search_fields = ("person__search_name", "project__code")
    readonly_fields = ("submitted_at", "created_at", "updated_at")
