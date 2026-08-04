from django.apps import AppConfig


class WageLedgerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "features.wage_ledger"
    verbose_name = "Wage ledger"

    def ready(self) -> None:
        from core.ui.registry import register_person_finance_series
        from features.wage_ledger.providers import gross_wage_series

        # role="gross": the figure core subtracts ledger deductions from when
        # both columns are present.
        register_person_finance_series(gross_wage_series, order=10, role="gross")
