from django.apps import AppConfig


class LogisticsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.logistics"
    verbose_name = "Logistics"

    def ready(self):
        # Feature -> core registrations (ADR 0021).
        from apps.core.registry import (
            register_exit_relevance,
            register_person_panel,
            register_report_tile,
        )
        from apps.logistics.panels import (
            equipment_panel,
            equipment_value_tile,
            holds_resources,
            occupancy_tile,
            room_panel,
        )
        from apps.logistics.services import exit_reconcile
        from apps.projects.services import register_exit_hook

        register_exit_hook(exit_reconcile)
        register_person_panel("panels/logistics_room.html", room_panel, order=10)
        register_person_panel("panels/logistics_equipment.html", equipment_panel, order=20)
        register_exit_relevance(holds_resources)
        register_report_tile(occupancy_tile, order=20)
        register_report_tile(equipment_value_tile, order=30)
