from django.apps import AppConfig


class MessagingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "features.messaging"
    verbose_name = "Messaging"

    def ready(self):
        # Feature -> core registrations (ADR 0021).
        from core.retention.services import register_retention
        from core.ui.registry import register_person_panel
        from features.messaging.panels import offer_email_panel, sms_panel
        from features.messaging.services import purge_offer_emails

        register_person_panel("panels/messaging_sms.html", sms_panel, order=30)
        register_person_panel(
            "panels/messaging_offer_email.html", offer_email_panel, order=35
        )
        register_retention("offer_emails", purge_offer_emails)
