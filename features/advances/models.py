from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class EntryType(models.TextChoices):
    """What happened (design doc §5.10) — cash movement and payroll effect are
    never conflated in one signed number."""

    CASH_ADVANCE = "cash_advance", _("Cash advance")
    PAY_DEDUCTION = "pay_deduction", _("Pay deduction")
    PAY_ADDITION = "pay_addition", _("Pay addition")


class PayEffect(models.TextChoices):
    NONE = "none", _("No payroll effect")
    DEDUCT = "deduct", _("Deduct from pay")
    ADD = "add", _("Add to pay")


class SettlementStatus(models.TextChoices):
    OPEN = "open", _("Open")
    INCLUDED_IN_CYCLE = "included", _("Included in cycle")
    DEDUCTED = "deducted", _("Settled with pay")
    CANCELLED = "cancelled", _("Cancelled")


class LedgerCategory(models.TextChoices):
    CASH_ADVANCE = "cash_advance", _("Cash advance")
    CLOTHING = "clothing", _("Clothing")
    FOOTWEAR = "footwear", _("Footwear")
    EQUIPMENT = "equipment", _("Equipment")
    MEDICAL = "medical", _("Medical")
    TRAVEL_FUEL = "travel_fuel", _("Travel / fuel")
    OTHER = "other", _("Other")


# entry_type -> the only pay_effect it may carry (§5.10 typical mapping;
# NONE is reserved for entries with no payroll impact, allowed everywhere).
TYPE_PAY_EFFECTS = {
    EntryType.CASH_ADVANCE: PayEffect.DEDUCT,
    EntryType.PAY_DEDUCTION: PayEffect.DEDUCT,
    EntryType.PAY_ADDITION: PayEffect.ADD,
}


class LedgerEntry(models.Model):
    """One advance/deduction/addition against a person (§5.10).

    Amounts are always positive ``Decimal``; meaning lives in the explicit
    fields. Entries are never hard-deleted: pre-inclusion edits are audited,
    post-inclusion corrections happen only via reversal entries (C-Q5).
    """

    person = models.ForeignKey(
        "people.Person", on_delete=models.PROTECT, related_name="ledger_entries", verbose_name=_("person")
    )
    project = models.ForeignKey(
        "projects.Project", null=True, blank=True, on_delete=models.PROTECT,
        related_name="ledger_entries", verbose_name=_("company / project"),
    )
    entry_type = models.CharField(_("entry type"), max_length=20, choices=EntryType.choices)
    category = models.CharField(_("category"), max_length=20, choices=LedgerCategory.choices)
    amount = models.DecimalField(
        _("amount"), max_digits=9, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    currency = models.CharField(_("currency"), max_length=3, default="EUR")
    pay_effect = models.CharField(_("pay effect"), max_length=10, choices=PayEffect.choices)
    settlement_status = models.CharField(
        _("settlement"), max_length=10, choices=SettlementStatus.choices, default=SettlementStatus.OPEN
    )
    entry_date = models.DateField(_("entry date"))
    cycle_key = models.CharField(
        _("cycle"), max_length=7, blank=True, default="",
        help_text=_("20th-to-20th cycle the entry settles in, keyed by the end month (e.g. 2026-07)."),
    )
    note = models.CharField(_("note"), max_length=200, blank=True)
    reversal_of = models.OneToOneField(
        "self", null=True, blank=True, on_delete=models.PROTECT,
        related_name="reversed_by", verbose_name=_("reversal of"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name=_("entered by"),
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("ledger entry")
        verbose_name_plural = _("ledger entries")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["entry_date"]),
            models.Index(fields=["cycle_key"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_entry_type_display()} {self.amount} {self.currency} — {self.person}"

    @property
    def is_locked(self) -> bool:
        """Locked once part of a sent summary/cycle (C-Q5 immutability)."""
        return self.settlement_status in (
            SettlementStatus.INCLUDED_IN_CYCLE,
            SettlementStatus.DEDUCTED,
        )
