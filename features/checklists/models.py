from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ChecklistKind(models.TextChoices):
    ACTIVATION = "activation", _("Activation")
    REACTIVATION = "reactivation", _("Reactivation")


class ChecklistTemplate(models.Model):
    """A named checklist definition (design doc §5.5). MVP ships the global
    activation checklist; project/position-specific templates are a later
    extension of the same shape."""

    name = models.CharField(_("name"), max_length=120)
    kind = models.CharField(
        _("kind"), max_length=20, choices=ChecklistKind.choices, default=ChecklistKind.ACTIVATION
    )
    is_active = models.BooleanField(_("active"), default=True)
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("checklist template")
        verbose_name_plural = _("checklist templates")

    def __str__(self) -> str:
        return self.name


class ChecklistItemTemplate(models.Model):
    template = models.ForeignKey(
        ChecklistTemplate, on_delete=models.CASCADE, related_name="items", verbose_name=_("template")
    )
    label = models.CharField(_("label"), max_length=200)
    critical = models.BooleanField(
        _("critical"), default=True, help_text=_("Critical items block activation; others only warn.")
    )
    order = models.PositiveSmallIntegerField(_("order"), default=0)

    class Meta:
        verbose_name = _("checklist item template")
        verbose_name_plural = _("checklist item templates")
        ordering = ("order", "id")

    def __str__(self) -> str:
        return self.label


class PersonChecklistItem(models.Model):
    """One checklist item instantiated for one person, with approval identity
    (§5.5: record who approved each item)."""

    person = models.ForeignKey(
        "people.Person", on_delete=models.CASCADE, related_name="checklist_items", verbose_name=_("person")
    )
    item_template = models.ForeignKey(
        ChecklistItemTemplate, on_delete=models.CASCADE, related_name="person_items", verbose_name=_("item")
    )
    done = models.BooleanField(_("done"), default=False)
    done_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name=_("done by"),
    )
    done_at = models.DateTimeField(_("done at"), null=True, blank=True)
    note = models.CharField(_("note"), max_length=200, blank=True)

    class Meta:
        verbose_name = _("person checklist item")
        verbose_name_plural = _("person checklist items")
        ordering = ("item_template__order", "item_template_id")
        constraints = [
            models.UniqueConstraint(fields=["person", "item_template"], name="uniq_person_checklist_item"),
        ]

    def __str__(self) -> str:
        return f"{self.item_template.label} — {self.person}"
