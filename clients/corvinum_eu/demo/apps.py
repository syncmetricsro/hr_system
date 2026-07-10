from django.apps import AppConfig


class CorvinumDemoConfig(AppConfig):
    """CorvinumEU demo assets (client layer, ADR 0022): fictional seed data
    for the thin-client walkthrough. The client layer may import core and
    features freely."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "clients.corvinum_eu.demo"
    label = "corvinum_demo"
    verbose_name = "CorvinumEU demo assets"
