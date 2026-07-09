from __future__ import annotations

from django.contrib import admin

from features.blacklist.models import BlacklistCase, BlacklistCategory, MatchFingerprint


@admin.register(BlacklistCategory)
class BlacklistCategoryAdmin(admin.ModelAdmin):
    list_display = ("label", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("label",)


@admin.register(BlacklistCase)
class BlacklistCaseAdmin(admin.ModelAdmin):
    list_display = ("person", "status", "category", "proposed_by", "decided_by", "decided_at", "expiry_date")
    list_filter = ("status", "category")
    search_fields = ("person__search_name",)
    readonly_fields = ("created_at", "updated_at", "decided_at")


@admin.register(MatchFingerprint)
class MatchFingerprintAdmin(admin.ModelAdmin):
    # Raw identifiers are never stored — only the keyed HMAC is shown.
    list_display = ("identifier_type", "hmac", "key_version", "is_active", "expires_at")
    list_filter = ("identifier_type", "is_active")
    search_fields = ("hmac",)
    readonly_fields = ("hmac", "key_version", "created_at")
