from django.contrib import admin

from features.advances.models import LedgerEntry


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = (
        "person", "entry_type", "category", "amount", "pay_effect",
        "settlement_status", "entry_date", "cycle_key",
    )
    list_filter = ("entry_type", "settlement_status", "category")
    raw_id_fields = ("person", "project", "reversal_of")
    date_hierarchy = "entry_date"

    def has_delete_permission(self, request, obj=None):
        # No hard deletes anywhere (C-Q5): corrections are cancellations or
        # reversal entries, both audited.
        return False
