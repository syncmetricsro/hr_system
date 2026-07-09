from django.apps import AppConfig


class FinanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.finance"
    verbose_name = "Finance"

    def ready(self):
        # Feature -> core registrations (ADR 0021).
        from apps.core.registry import register_report_panel
        from apps.finance.panels import company_totals_panel

        register_report_panel(
            "panels/finance_company_totals.html", company_totals_panel, order=10
        )
