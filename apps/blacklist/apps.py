from django.apps import AppConfig


class BlacklistConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.blacklist"
    verbose_name = "Blacklist"

    def ready(self):
        # Register the unresolved-case hard-gate into the core activation hook
        # (plan §12.13; feature -> core dependency direction, ADR 0021).
        from apps.blacklist.services import activation_gate
        from apps.projects.services import register_activation_check

        register_activation_check(activation_gate)
