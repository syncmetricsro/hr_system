from django.contrib import admin

from features.checklists.models import (
    ChecklistItemTemplate,
    ChecklistTemplate,
    PersonChecklistItem,
)


class ChecklistItemTemplateInline(admin.TabularInline):
    model = ChecklistItemTemplate
    extra = 0


@admin.register(ChecklistTemplate)
class ChecklistTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "is_active")
    inlines = [ChecklistItemTemplateInline]


@admin.register(PersonChecklistItem)
class PersonChecklistItemAdmin(admin.ModelAdmin):
    list_display = ("person", "item_template", "done", "done_by", "done_at")
    list_filter = ("done",)
    raw_id_fields = ("person",)
