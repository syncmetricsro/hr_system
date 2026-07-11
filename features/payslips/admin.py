from django.contrib import admin

from features.payslips.models import Payslip


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ("person", "period", "net_amount", "currency", "sent_at", "sent_to")
    list_filter = ("period",)
    raw_id_fields = ("person",)
