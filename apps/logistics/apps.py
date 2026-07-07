from django.apps import AppConfig


class LogisticsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.logistics"
    verbose_name = "Logistics"

    def ready(self):
        # Register this feature's exit-reconciliation into the core hook
        # (feature -> core dependency direction, ADR 0021).
        from apps.logistics.services import exit_reconcile
        from apps.projects.services import register_exit_hook

        register_exit_hook(exit_reconcile)
