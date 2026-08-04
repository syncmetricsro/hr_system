from django.apps import AppConfig


class ProfitabilityConfig(AppConfig):
    """Jober's per-project P&L (Jober_Finance_Specs §2).

    The module is ``features.profitability`` — the placement the spec names, and
    the name the ``profitability`` feature flag has always used.

    ``label`` is pinned to the historic ``finance`` on purpose. Django derives an
    app label from the module's last component, and letting it change would
    rename every table (``finance_*``), invalidate the ``to='finance.…'``
    references inside this app's own migrations, and require rewriting
    ``django_migrations.app`` and ``django_content_type.app_label`` on every
    database that already holds data — including staging. None of that is
    visible to anyone. The label is an internal key; the module path is what the
    spec and the flag care about.

    Renaming the label is possible later as its own slice with its own restore
    drill. It is deliberately not bundled with a feature change.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "features.profitability"
    label = "finance"
    verbose_name = "Profitability"
