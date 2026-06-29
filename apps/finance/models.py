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


class FinanceCategoryKind(models.TextChoices):
    COST = "cost", _("Cost")
    REVENUE = "revenue", _("Revenue")


class FinanceGroup(models.TextChoices):
    LABOUR = "labour", _("Labour")
    TRANSPORT = "transport", _("Transport")
    ACCOMMODATION = "accommodation", _("Accommodation")
    COMPLIANCE = "compliance", _("Compliance")
    OVERHEAD = "overhead", _("Overhead")
    EQUIPMENT = "equipment", _("Equipment")
    DAMAGE = "damage", _("Damage")
    WELFARE = "welfare", _("Welfare")
    REVENUE = "revenue", _("Revenue")
    OTHER = "other", _("Other")


class FinanceCategory(models.Model):
    """A finance line-item category (the configurable catalog, Finance_Specs §2).

    Amounts are stored positive; the sign comes from ``kind`` (cost vs revenue),
    so net = revenues - costs regardless of the spreadsheet's sign convention
    (still to confirm with one filled month). ``group`` powers the manager's
    transport/accommodation/overhead breakdowns."""

    label = models.CharField(_("label"), max_length=120)
    kind = models.CharField(_("kind"), max_length=10, choices=FinanceCategoryKind.choices)
    group = models.CharField(_("group"), max_length=20, choices=FinanceGroup.choices, default=FinanceGroup.OTHER)
    is_active = models.BooleanField(_("active"), default=True)
    order = models.PositiveIntegerField(_("order"), default=0)

    class Meta:
        verbose_name = _("finance category")
        verbose_name_plural = _("finance categories")
        ordering = ("kind", "order", "label")
        constraints = [
            models.UniqueConstraint(fields=["label", "kind"], name="unique_finance_category_label_kind")
        ]

    def __str__(self) -> str:
        return f"{self.label} ({self.kind})"


class FinanceLineItem(models.Model):
    """One amount for one category on one project-month. Amount is positive."""

    month = models.ForeignKey(
        FinancialMonth, on_delete=models.CASCADE, related_name="line_items", verbose_name=_("month")
    )
    category = models.ForeignKey(
        FinanceCategory, on_delete=models.PROTECT, related_name="line_items", verbose_name=_("category")
    )
    amount = models.DecimalField(_("amount"), max_digits=12, decimal_places=2, default=Decimal("0"))

    class Meta:
        verbose_name = _("finance line item")
        verbose_name_plural = _("finance line items")
        ordering = ("category__kind", "category__order")
        constraints = [
            models.UniqueConstraint(fields=["month", "category"], name="unique_line_item_per_month_category")
        ]

    def __str__(self) -> str:
        return f"{self.category.label}: {self.amount}"
