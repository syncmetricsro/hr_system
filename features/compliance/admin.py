from __future__ import annotations

from django.contrib import admin

from features.compliance.models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("name", "person", "issue_date", "expiry_date")
    list_filter = ("name",)
    search_fields = ("name", "person__search_name")
