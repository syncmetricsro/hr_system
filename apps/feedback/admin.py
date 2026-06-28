from __future__ import annotations

from django.contrib import admin

from apps.feedback.models import FeedbackLink, FeedbackSubmission


@admin.register(FeedbackLink)
class FeedbackLinkAdmin(admin.ModelAdmin):
    list_display = ("label", "token", "project", "is_active")
    list_filter = ("is_active",)
    readonly_fields = ("token",)


@admin.register(FeedbackSubmission)
class FeedbackSubmissionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "link", "rating")
    list_filter = ("link", "rating")
    readonly_fields = ("link", "message", "rating", "created_at")
