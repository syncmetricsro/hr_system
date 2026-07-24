from django.apps import AppConfig


class ComplianceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "features.compliance"
    verbose_name = "Compliance"

    def ready(self):
        # Feature -> core registrations (ADR 0021).
        from features.compliance.panels import (
            certificate_badges,
            certificate_panel,
            compliance_badge,
            compliance_tile,
        )
        from core.ui.registry import (
            register_nav_badge,
            register_person_badges,
            register_person_panel,
            register_report_tile,
        )

        register_report_tile(compliance_tile, order=10)
        register_person_panel("panels/compliance_certificates.html", certificate_panel, order=30)
        register_nav_badge("compliance", compliance_badge)
        register_person_badges(certificate_badges)
        from core.notifications.registry import register_alert_provider
        from features.compliance.notifications import compliance_notification_provider

        register_alert_provider(compliance_notification_provider)
