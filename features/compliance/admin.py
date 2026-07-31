from __future__ import annotations

from django.contrib import admin

from features.compliance.models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "person",
        "record_status",
        "issue_date",
        "expiry_date",
    )
    list_filter = ("category", "record_status")
    search_fields = ("name", "issuer", "certificate_number", "person__search_name")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
