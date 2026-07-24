from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class Office(models.Model):
    """A physical Jober office (ADR 0026). Nullable/unused by CorvinumEU
    (single-site) — this is a core, client-agnostic concept, not Jober-only
    code, just Jober-only data (ADR 0021/0022: no client branching in core)."""

    name = models.CharField(_("name"), max_length=100)
    code = models.CharField(_("code"), max_length=10, unique=True)
    country = models.CharField(_("country"), max_length=2)

    class Meta:
        verbose_name = _("office")
        verbose_name_plural = _("offices")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name
