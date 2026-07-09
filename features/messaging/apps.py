from django.apps import AppConfig


class MessagingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "features.messaging"
    verbose_name = "Messaging"

    def ready(self):
        # Feature -> core registrations (ADR 0021).
        from core.ui.registry import register_person_panel
        from features.messaging.panels import sms_panel

        register_person_panel("panels/messaging_sms.html", sms_panel, order=30)
