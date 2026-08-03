from __future__ import annotations

from django.contrib import admin

from features.messaging.models import (
    EmailBatch,
    InboundMessage,
    JobOffer,
    MessageTemplate,
    OfferEmailTemplate,
    OutboundEmail,
    OutboundMessage,
)


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_by")
    list_filter = ("is_active",)
    search_fields = ("name", "body")


@admin.register(OutboundMessage)
class OutboundMessageAdmin(admin.ModelAdmin):
    list_display = ("to_number", "status", "person", "sent_by", "created_at")
    list_filter = ("status",)
    search_fields = ("to_number", "body")
    readonly_fields = ("provider_sid", "created_at")


@admin.register(InboundMessage)
class InboundMessageAdmin(admin.ModelAdmin):
    list_display = ("from_number", "received_at")
    search_fields = ("from_number", "body")
    readonly_fields = ("received_at",)


# Offer emails (ADR 0029). Unlike SMS templates these are also editable by a
# manager in the app itself, so admin here is a convenience, not the only door.
@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "office", "start_date", "is_active")
    list_filter = ("is_active", "office")
    search_fields = ("title", "location", "terms")


@admin.register(OfferEmailTemplate)
class OfferEmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("kind", "language", "subject", "is_active")
    list_filter = ("kind", "language", "is_active")
    search_fields = ("subject", "body")


@admin.register(OutboundEmail)
class OutboundEmailAdmin(admin.ModelAdmin):
    list_display = ("to_email", "status", "person", "offer", "sent_by", "created_at")
    list_filter = ("status", "kind", "language")
    search_fields = ("to_email", "subject", "body")
    readonly_fields = ("created_at",)


@admin.register(EmailBatch)
class EmailBatchAdmin(admin.ModelAdmin):
    list_display = ("offer", "kind", "recipient_count", "created_by", "created_at")
    list_filter = ("kind",)
    readonly_fields = ("created_at",)
