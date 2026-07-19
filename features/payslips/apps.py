from django.apps import AppConfig


class PayslipsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "features.payslips"
    verbose_name = "Payslips"

    def ready(self) -> None:
        from core.ui.registry import register_person_finance_series
        from features.payslips.providers import net_payslip_series

        register_person_finance_series(net_payslip_series, order=40)
