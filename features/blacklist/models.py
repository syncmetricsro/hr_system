from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class BlacklistCategory(models.Model):
    """Configurable catalog of blacklist reason categories (plan §11.14).

    Kept configurable + seeded with **neutral** placeholders because reason
    categories can edge into special-category data; the final list is pending
    Jober/lawyer confirmation. Same pattern as ``people.InactiveReason``.
    """

    label = models.CharField(_("label"), max_length=120, unique=True)
    is_active = models.BooleanField(_("active"), default=True)
    order = models.PositiveIntegerField(_("order"), default=0)

    class Meta:
        verbose_name = _("blacklist category")
        verbose_name_plural = _("blacklist categories")
        ordering = ("order", "label")

    def __str__(self) -> str:
        return self.label


class BlacklistCaseStatus(models.TextChoices):
    PROPOSED = "proposed", _("Proposed")
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")
    REMOVED = "removed", _("Removed")


class BlacklistCase(models.Model):
    """A blacklist decision record (plan §11.14). "Warning, not silent merge":
    a proposed case does not change the person's lifecycle — only a manager's
    approval moves them to BLACKLISTED. The ``restricted_reason`` is visible to
    coordinator + manager only (RBAC ``blacklist.view_reason``).
    """

    person = models.ForeignKey(
        "people.Person", on_delete=models.PROTECT, related_name="blacklist_cases",
        verbose_name=_("person"),
    )
    status = models.CharField(
        _("status"), max_length=20,
        choices=BlacklistCaseStatus.choices, default=BlacklistCaseStatus.PROPOSED,
    )
    category = models.ForeignKey(
        BlacklistCategory, on_delete=models.PROTECT, null=True, blank=True,
        related_name="cases", verbose_name=_("category"),
    )
    restricted_reason = models.TextField(_("restricted reason"), blank=True)
    proposed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="proposed_blacklist_cases", verbose_name=_("proposed by"),
    )
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="decided_blacklist_cases", verbose_name=_("decided by"),
    )
    decided_at = models.DateTimeField(_("decided at"), null=True, blank=True)
    expiry_date = models.DateField(_("expiry date"), null=True, blank=True)
    created_at = models.DateTimeField(_("created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated"), auto_now=True)

    class Meta:
        verbose_name = _("blacklist case")
        verbose_name_plural = _("blacklist cases")
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["status"])]

    def __str__(self) -> str:
        return f"{self.person} ({self.status})"

    @property
    def is_open(self) -> bool:
        """Proposed or approved — an unresolved case that hard-gates activation."""
        return self.status in (BlacklistCaseStatus.PROPOSED, BlacklistCaseStatus.APPROVED)


class IdentifierType(models.TextChoices):
    NATIONAL_ID = "national_id", _("National ID")
    PASSPORT = "passport", _("Passport")
    OTHER = "other", _("Other")


class MatchFingerprint(models.Model):
    """A keyed HMAC of a person's identifier for re-entry matching (plan §11.14).

    The **raw identifier is never stored** — only the HMAC. ``key_version`` indexes
    ``settings.BLACKLIST_HMAC_KEYS`` so keys can rotate without re-hashing.
    Company-wide (no office scoping).
    """

    case = models.ForeignKey(
        BlacklistCase, on_delete=models.CASCADE, related_name="fingerprints",
        verbose_name=_("case"),
    )
    person = models.ForeignKey(
        "people.Person", on_delete=models.PROTECT, related_name="match_fingerprints",
        verbose_name=_("person"),
    )
    identifier_type = models.CharField(
        _("identifier type"), max_length=20, choices=IdentifierType.choices,
        default=IdentifierType.NATIONAL_ID,
    )
    hmac = models.CharField(_("HMAC"), max_length=64, db_index=True)
    key_version = models.PositiveIntegerField(_("key version"), default=0)
    is_active = models.BooleanField(_("active"), default=True)
    created_at = models.DateTimeField(_("created"), auto_now_add=True)
    expires_at = models.DateField(_("expires at"), null=True, blank=True)

    class Meta:
        verbose_name = _("match fingerprint")
        verbose_name_plural = _("match fingerprints")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.get_identifier_type_display()} · {self.hmac[:8]}…"
