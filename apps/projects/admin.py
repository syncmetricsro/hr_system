from __future__ import annotations

from django.contrib import admin

from apps.projects.models import Project, ProjectAssignment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "office", "is_active", "financial_reporting_eligible")
    list_filter = ("is_active", "office")
    search_fields = ("name", "code", "partner")
    filter_horizontal = ("responsible_coordinators",)


@admin.register(ProjectAssignment)
class ProjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ("person", "project", "status", "start_date", "end_date", "assigned_by")
    list_filter = ("status", "project")
    search_fields = ("person__search_name", "project__code")
    readonly_fields = ("coordinator_snapshot", "created_at", "updated_at")
