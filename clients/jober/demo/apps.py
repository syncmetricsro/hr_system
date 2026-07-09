from django.apps import AppConfig


class JoberDemoConfig(AppConfig):
    """Jober demo assets (client layer, ADR 0021): the cross-feature demo
    scenario seed. The client layer may import core and features freely."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "clients.jober.demo"
    label = "jober_demo"
    verbose_name = "Jober demo assets"
