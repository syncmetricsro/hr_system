from django.apps import AppConfig


class FeedbackConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "features.feedback"
    verbose_name = "Feedback"

    def ready(self):
        # Feature -> core registration (ADR 0021): retention purge.
        from core.retention.services import register_retention
        from features.feedback.services import purge_feedback

        register_retention("feedback", purge_feedback)
        from core.notifications.registry import register_alert_provider
        from features.feedback.notifications import feedback_notification_provider

        register_alert_provider(feedback_notification_provider)
