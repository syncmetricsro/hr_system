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
