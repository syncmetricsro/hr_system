from __future__ import annotations

from django.contrib import admin

from features.finance.models import FinanceCategory, FinanceLineItem, FinancialMonth


@admin.register(FinancialMonth)
class FinancialMonthAdmin(admin.ModelAdmin):
    list_display = ("project", "year", "month", "revenue", "cost", "net", "is_locked")
    list_filter = ("year", "is_locked", "project")
    search_fields = ("project__code",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(FinanceCategory)
class FinanceCategoryAdmin(admin.ModelAdmin):
    list_display = ("label", "kind", "group", "order", "is_active")
    list_filter = ("kind", "group", "is_active")
    search_fields = ("label",)


@admin.register(FinanceLineItem)
class FinanceLineItemAdmin(admin.ModelAdmin):
    list_display = ("month", "category", "amount")
    list_filter = ("category__kind", "category__group")
    search_fields = ("category__label", "month__project__code")
