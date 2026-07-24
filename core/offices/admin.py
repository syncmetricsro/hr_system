from __future__ import annotations

from django.contrib import admin

from core.offices.models import Office


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "country")
    search_fields = ("name", "code")
