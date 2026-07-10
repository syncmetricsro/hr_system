from django.apps import AppConfig


class AdvancesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "features.advances"
    verbose_name = "Advances & deductions"

    def ready(self):
        # Feature -> core registration (ADR 0022): person-card ledger panel.
        from core.ui.registry import register_person_panel
        from features.advances.panels import ledger_panel

        register_person_panel("panels/advances_ledger.html", ledger_panel, order=45)
