from __future__ import annotations

from django.contrib import admin

from apps.finance.models import FinancialMonth


@admin.register(FinancialMonth)
class FinancialMonthAdmin(admin.ModelAdmin):
    list_display = ("project", "year", "month", "revenue", "cost", "net", "is_locked")
    list_filter = ("year", "is_locked", "project")
    search_fields = ("project__code",)
    readonly_fields = ("created_at", "updated_at")
