from django.apps import AppConfig


class AdvancesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "features.advances"
    verbose_name = "Advances & deductions"

    def ready(self):
        # Feature -> core registration (ADR 0022): person-card ledger panel.
        from django.apps import apps as django_apps

        from core.ui.registry import register_person_panel
        from features.advances.panels import ledger_panel

        register_person_panel("panels/advances_ledger.html", ledger_panel, order=45)

        # Feature -> feature (flag-guarded): approved equipment charges land
        # in the ledger as linked PAY_DEDUCTIONs (§5.8). Only when logistics
        # is installed for this client.
        if django_apps.is_installed("features.logistics"):
            from features.advances.hooks import equipment_charge_to_ledger
            from features.logistics.services import register_deduction_approved_hook

            register_deduction_approved_hook(equipment_charge_to_ledger)
