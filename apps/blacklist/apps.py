from django.apps import AppConfig


class BlacklistConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.blacklist"
    verbose_name = "Blacklist"

    def ready(self):
        # Feature -> core registrations (ADR 0021): activation hard-gate
        # (plan §12.13), person-card banner + case panel, intake-form extension.
        from apps.blacklist.panels import (
            IntakeMatchExtension,
            case_panel,
            open_case_banner,
        )
        from apps.blacklist.services import activation_gate
        from apps.core.registry import (
            register_person_banner,
            register_person_form_extension,
            register_person_panel,
        )
        from apps.projects.services import register_activation_check

        register_activation_check(activation_gate)
        register_person_banner("panels/blacklist_banner.html", open_case_banner, order=10)
        register_person_panel("panels/blacklist_case.html", case_panel, order=40)
        register_person_form_extension(IntakeMatchExtension())
