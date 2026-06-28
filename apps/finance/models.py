from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class FinancialMonth(models.Model):
    """A minimal monthly financial record per project (plan §11.15).

    SIGN CONVENTION ASSUMPTION: net = revenue - cost. Jober must confirm from one
    filled month whether costs are entered negative or stored positive and
    subtracted (Phase 4 blocker, docs/product/open-decisions.md). Full line items
    live in finance_module_spec.md. Totals are always summed dynamically over all
    projects/months — never hardcoded — to avoid the manager's spreadsheet bugs.
    """

    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="financial_months", verbose_name=_("project")
    )
    year = models.PositiveIntegerField(_("year"))
    month = models.PositiveSmallIntegerField(_("month"))
    revenue = models.DecimalField(_("revenue"), max_digits=12, decimal_places=2, default=Decimal("0"))
    cost = models.DecimalField(_("cost"), max_digits=12, decimal_places=2, default=Decimal("0"))
    note = models.CharField(_("note"), max_length=300, blank=True)
    is_locked = models.BooleanField(_("locked"), default=False)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="recorded_financial_months", verbose_name=_("recorded by"),
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated"), auto_now=True)

    class Meta:
        verbose_name = _("financial month")
        verbose_name_plural = _("financial months")
        ordering = ("-year", "-month", "project__name")
        constraints = [
            models.UniqueConstraint(fields=["project", "year", "month"], name="unique_financial_month_per_project")
        ]

    def __str__(self) -> str:
        return f"{self.project} {self.year}-{self.month:02d}"

    @property
    def net(self) -> Decimal:
        # Assumption: revenue - cost (see class docstring; confirm in Phase 4).
        return self.revenue - self.cost
