from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class WageEntry(models.Model):
    person = models.ForeignKey(
        "people.Person",
        on_delete=models.PROTECT,
        related_name="wage_entries",
        verbose_name=_("person"),
    )
    period = models.CharField(
        _("period"),
        max_length=7,
        validators=[
            RegexValidator(
                r"^\d{4}-(0[1-9]|1[0-2])$", _("Use the YYYY-MM format.")
            )
        ],
    )
    gross_amount = models.DecimalField(
        _("gross amount"),
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    currency = models.CharField(_("currency"), max_length=3, default="EUR")
    note = models.CharField(_("note"), max_length=200, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("created by"),
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("wage entry")
        verbose_name_plural = _("wage entries")
        ordering = ("-period", "person__last_name")
        constraints = [
            models.UniqueConstraint(
                fields=["person", "period"],
                name="uniq_wage_person_period",
                violation_error_message=_(
                    "A wage is already recorded for this person and period."
                ),
            )
        ]

    def __str__(self) -> str:
        return f"{self.person} — {self.period} ({self.gross_amount} {self.currency})"
