from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core.ui"

    def ready(self):
        # Platform-wide deploy checks. Registered from core because the outbound
        # email checks must run for every client, including ones that install no
        # messaging feature at all.
        from core import checks  # noqa: F401
