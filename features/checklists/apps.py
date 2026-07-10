from django.apps import AppConfig


class ChecklistsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "features.checklists"
    verbose_name = "Checklists"

    def ready(self):
        # Feature -> core registrations (ADR 0022): activation hard-stop on
        # open critical items (§5.5) + person-card panel. Both no-op unless
        # the "checklists" flag is on for the running client.
        from core.projects.services import register_activation_check
        from core.ui.registry import register_person_panel
        from features.checklists.panels import checklist_panel
        from features.checklists.services import activation_gate

        register_activation_check(activation_gate)
        register_person_panel("panels/checklists_items.html", checklist_panel, order=35)
