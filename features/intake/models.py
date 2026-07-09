from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class QuestionnaireStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    PUBLISHED = "published", _("Published")
    RETIRED = "retired", _("Retired")


class QuestionType(models.TextChoices):
    TEXT = "text", _("Text")
    TEXTAREA = "textarea", _("Long text")
    BOOL = "bool", _("Yes/No")
    DATE = "date", _("Date")
    NUMBER = "number", _("Number")
    SELECT = "select", _("Choice")


class IntakeQuestionnaireVersion(models.Model):
    name = models.CharField(_("name"), max_length=200)
    version = models.PositiveIntegerField(_("version"), default=1)
    status = models.CharField(_("status"), max_length=20, choices=QuestionnaireStatus.choices, default=QuestionnaireStatus.DRAFT)
    effective_date = models.DateField(_("effective date"), null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_questionnaires"
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("intake questionnaire version")
        verbose_name_plural = _("intake questionnaire versions")
        ordering = ("-version",)
        constraints = [
            models.UniqueConstraint(fields=["name", "version"], name="unique_questionnaire_name_version")
        ]

    def __str__(self) -> str:
        return f"{self.name} v{self.version} ({self.status})"


class IntakePanel(models.Model):
    questionnaire = models.ForeignKey(
        IntakeQuestionnaireVersion, on_delete=models.CASCADE, related_name="panels", verbose_name=_("questionnaire")
    )
    title = models.CharField(_("title"), max_length=200)
    help_text = models.CharField(_("help"), max_length=300, blank=True)
    order = models.PositiveIntegerField(_("order"), default=0)

    class Meta:
        verbose_name = _("intake panel")
        verbose_name_plural = _("intake panels")
        ordering = ("order",)

    def __str__(self) -> str:
        return f"{self.questionnaire} · {self.title}"


class IntakeQuestion(models.Model):
    panel = models.ForeignKey(IntakePanel, on_delete=models.CASCADE, related_name="questions", verbose_name=_("panel"))
    stable_key = models.CharField(_("stable key"), max_length=60)
    label = models.CharField(_("label"), max_length=300)
    type = models.CharField(_("type"), max_length=20, choices=QuestionType.choices, default=QuestionType.TEXT)
    required = models.BooleanField(_("required"), default=False)
    order = models.PositiveIntegerField(_("order"), default=0)
    options = models.JSONField(_("options"), default=list, blank=True)
    requires_typed_negative = models.BooleanField(_("requires typed negative"), default=False)
    accepted_negatives = models.JSONField(_("accepted negatives"), default=list, blank=True)
    # Conditional: this question is shown/required only when another question's
    # answer (by stable_key) is "positive" (non-negative, non-empty).
    conditional_on = models.CharField(_("conditional on"), max_length=60, blank=True)

    class Meta:
        verbose_name = _("intake question")
        verbose_name_plural = _("intake questions")
        ordering = ("order",)
        constraints = [
            models.UniqueConstraint(fields=["panel", "stable_key"], name="unique_question_key_per_panel")
        ]

    def __str__(self) -> str:
        return f"{self.stable_key} ({self.type})"


class RecruitmentIntake(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        COMPLETED = "completed", _("Completed")

    questionnaire = models.ForeignKey(
        IntakeQuestionnaireVersion, on_delete=models.PROTECT, related_name="intakes", verbose_name=_("questionnaire")
    )
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="intakes"
    )
    person = models.ForeignKey(
        "people.Person", on_delete=models.SET_NULL, null=True, blank=True, related_name="intakes", verbose_name=_("person")
    )
    status = models.CharField(_("status"), max_length=20, choices=Status.choices, default=Status.DRAFT)
    current_panel_order = models.PositiveIntegerField(_("current panel"), default=0)
    started_at = models.DateTimeField(_("started"), auto_now_add=True)
    completed_at = models.DateTimeField(_("completed"), null=True, blank=True)

    class Meta:
        verbose_name = _("recruitment intake")
        verbose_name_plural = _("recruitment intakes")
        ordering = ("-started_at",)

    def __str__(self) -> str:
        return f"Intake #{self.pk} ({self.status})"


class IntakeAnswer(models.Model):
    intake = models.ForeignKey(RecruitmentIntake, on_delete=models.CASCADE, related_name="answers", verbose_name=_("intake"))
    question = models.ForeignKey(IntakeQuestion, on_delete=models.PROTECT, related_name="answers", verbose_name=_("question"))
    value = models.TextField(_("value"), blank=True)
    normalized_value = models.TextField(_("normalized value"), blank=True)
    answered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="intake_answers"
    )
    answered_at = models.DateTimeField(_("answered at"), auto_now=True)

    class Meta:
        verbose_name = _("intake answer")
        verbose_name_plural = _("intake answers")
        constraints = [
            models.UniqueConstraint(fields=["intake", "question"], name="unique_answer_per_question")
        ]

    def __str__(self) -> str:
        return f"{self.question.stable_key}={self.value!r}"
