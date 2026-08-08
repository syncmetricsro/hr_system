from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

# Positive sign convention, same as features.profitability: money is never stored
# negative.
NON_NEGATIVE = [MinValueValidator(Decimal("0"))]


class MessageTemplate(models.Model):
    """Manager-managed SMS template (plan §11.12 / messaging spec)."""

    name = models.CharField(_("name"), max_length=120)
    body = models.TextField(_("body"))
    is_active = models.BooleanField(_("active"), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="message_templates",
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("message template")
        verbose_name_plural = _("message templates")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class OutboundMessage(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", _("Queued")
        SENT = "sent", _("Sent")
        FAILED = "failed", _("Failed")
        # Distinct from FAILED on purpose: the provider never saw this one.
        # A non-production allowlist stopped it, which is a configuration
        # outcome, not an error anyone should investigate.
        BLOCKED = "blocked", _("Blocked (recipient not allowed here)")

    person = models.ForeignKey(
        "people.Person",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
        verbose_name=_("person"),
    )
    to_number = models.CharField(_("to"), max_length=40)
    body = models.TextField(_("body"))
    status = models.CharField(
        _("status"), max_length=20, choices=Status.choices, default=Status.QUEUED
    )
    provider_sid = models.CharField(_("provider id"), max_length=64, blank=True)
    error = models.CharField(_("error"), max_length=300, blank=True)
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_messages",
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("outbound message")
        verbose_name_plural = _("outbound messages")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"-> {self.to_number} ({self.status})"


class InboundMessage(models.Model):
    from_number = models.CharField(_("from"), max_length=40)
    body = models.TextField(_("body"), blank=True)
    provider_sid = models.CharField(_("provider id"), max_length=64, blank=True)
    received_at = models.DateTimeField(_("received"), auto_now_add=True)

    class Meta:
        verbose_name = _("inbound message")
        verbose_name_plural = _("inbound messages")
        ordering = ("-received_at",)

    def __str__(self) -> str:
        return f"<- {self.from_number}"


# ---------------------------------------------------------------------------
# Offer emails (ADR 0029) — the second transport in this feature.
#
# Email is a *different product* from SMS, not a second driver behind one
# record: it carries a subject, long-form body, a recipient language, and no
# provider id. Per Jober_Messaging_Specs §3 the transport lives here rather
# than in a features/<transport> package of its own, but it gets its own
# models and its own Action. OutboundMessage stays phone-shaped.
# ---------------------------------------------------------------------------


def language_choices():
    """The locales this client serves.

    A callable rather than a literal so adding a language is a settings change,
    not a migration (Django resolves it at validation/form time).
    """
    return list(settings.LANGUAGES)


class JobOffer(models.Model):
    """A concrete opening a worker can be emailed about.

    Deliberately not merged into ``Project``: a project is a long-lived
    partner engagement, while an offer is a time-boxed recruiting pitch with
    its own wage, start date and terms, and several offers can hang off one
    project. ``office`` is its own column rather than being read through
    ``project`` so that office scoping (ADR 0026) never depends on a nullable
    relation.
    """

    class WageUnit(models.TextChoices):
        HOUR = "hour", _("per hour")
        MONTH = "month", _("per month")

    title = models.CharField(_("title"), max_length=120)
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="job_offers",
        verbose_name=_("project"),
    )
    office = models.ForeignKey(
        "offices.Office",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="job_offers",
        verbose_name=_("office"),
    )
    location = models.CharField(_("location"), max_length=120, blank=True)
    wage = models.DecimalField(
        _("wage"),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=NON_NEGATIVE,
    )
    wage_unit = models.CharField(
        _("wage unit"),
        max_length=10,
        choices=WageUnit.choices,
        default=WageUnit.HOUR,
        blank=True,
    )
    currency = models.CharField(_("currency"), max_length=3, default="EUR")
    start_date = models.DateField(_("start date"), null=True, blank=True)
    terms = models.TextField(_("terms"), blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="job_offers",
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("job offer")
        verbose_name_plural = _("job offers")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.title


class OfferEmailKind(models.TextChoices):
    """The kinds of offer email — the "different types of job offers".

    Module-level rather than nested so services, forms and views can name a
    kind without importing the template model.
    """

    NEW_OFFER = "new_offer", _("New job offer")
    REMINDER = "reminder", _("Offer reminder")
    SEASONAL = "seasonal", _("Seasonal campaign")
    CLOSING = "closing", _("Offer closing soon")


class OfferEmailTemplate(models.Model):
    """One (kind, language) body pair.

    Per-language *rows* rather than gettext: these are operator-authored texts,
    which ``docs/i18n-seeded-data.md`` explicitly keeps out of the message
    catalogs. This is also what lets a send honour ``Person.preferred_language``
    — the gap the SMS templates still have.
    """

    kind = models.CharField(_("kind"), max_length=20, choices=OfferEmailKind.choices)
    language = models.CharField(_("language"), max_length=10, choices=language_choices)
    subject = models.CharField(_("subject"), max_length=200)
    body = models.TextField(_("body"))
    is_active = models.BooleanField(_("active"), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="offer_email_templates",
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("offer email template")
        verbose_name_plural = _("offer email templates")
        ordering = ("kind", "language")
        constraints = [
            models.UniqueConstraint(
                fields=["kind", "language"], name="uniq_offer_template_kind_language"
            )
        ]

    def __str__(self) -> str:
        return f"{self.get_kind_display()} [{self.language}]"


class EmailBatch(models.Model):
    """One bulk send, so a campaign is a single auditable object.

    Without it "who emailed these 34 people, and was it one action or 34?" can
    only be reconstructed by clustering timestamps.
    """

    offer = models.ForeignKey(
        JobOffer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="batches",
        verbose_name=_("job offer"),
    )
    kind = models.CharField(_("kind"), max_length=20, choices=OfferEmailKind.choices)
    request_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    recipient_count = models.PositiveIntegerField(_("recipients"), default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="email_batches",
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("email batch")
        verbose_name_plural = _("email batches")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.offer} x{self.recipient_count}"


class OutboundEmail(models.Model):
    """Delivery ledger for offer emails.

    Separate from ``OutboundMessage`` on purpose (messaging spec §3): the
    columns genuinely differ (subject, language, no provider id), and widening
    the SMS record would make every existing phone-shaped query ambiguous.
    """

    class Status(models.TextChoices):
        QUEUED = "queued", _("Queued")
        SENT = "sent", _("Sent")
        FAILED = "failed", _("Failed")
        # Same distinction OutboundMessage draws: FAILED means the mail server
        # saw it and refused; BLOCKED means we never asked, because an opt-out,
        # the blacklist, or a non-production allowlist stopped it first.
        BLOCKED = "blocked", _("Blocked (not sent)")

    person = models.ForeignKey(
        "people.Person",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emails",
        verbose_name=_("person"),
    )
    offer = models.ForeignKey(
        JobOffer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emails",
        verbose_name=_("job offer"),
    )
    batch = models.ForeignKey(
        EmailBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emails",
        verbose_name=_("batch"),
    )
    kind = models.CharField(
        _("kind"), max_length=20, choices=OfferEmailKind.choices, blank=True
    )
    to_email = models.EmailField(_("to"), blank=True)
    language = models.CharField(_("language"), max_length=10, blank=True)
    subject = models.CharField(_("subject"), max_length=200, blank=True)
    body = models.TextField(_("body"), blank=True)
    status = models.CharField(
        _("status"), max_length=20, choices=Status.choices, default=Status.QUEUED
    )
    error = models.CharField(_("error"), max_length=300, blank=True)
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_emails",
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("outbound email")
        verbose_name_plural = _("outbound emails")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"-> {self.to_email} ({self.status})"
