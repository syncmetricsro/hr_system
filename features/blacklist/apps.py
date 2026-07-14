from django.apps import AppConfig


class BlacklistConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "features.blacklist"
    verbose_name = "Blacklist"

    def ready(self):
        # Feature -> core registrations (ADR 0021): activation hard-gate
        # (plan §12.13), person-card banner + case panel, intake-form extension.
        from features.blacklist.panels import (
            IntakeMatchExtension,
            case_panel,
            open_case_banner,
        )
        from features.blacklist.services import activation_gate
        from core.ui.registry import (
            register_person_banner,
            register_person_form_extension,
            register_person_panel,
        )
        from core.projects.services import register_activation_check

        from core.retention.services import register_retention
        from features.blacklist.services import purge_expired

        register_activation_check(activation_gate)
        register_retention("blacklist_fingerprints", purge_expired)
        register_person_banner("panels/blacklist_banner.html", open_case_banner, order=10)
        register_person_panel("panels/blacklist_case.html", case_panel, order=40)
        register_person_form_extension(IntakeMatchExtension())
        from core.notifications.registry import register_alert_provider
        from features.blacklist.notifications import blacklist_notification_provider

        register_alert_provider(blacklist_notification_provider)
