from __future__ import annotations

from django.contrib import admin

from apps.messaging.models import InboundMessage, MessageTemplate, OutboundMessage


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
