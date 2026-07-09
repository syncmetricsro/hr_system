from __future__ import annotations

from django.contrib import admin

from features.intake.models import (
    IntakePanel,
    IntakeQuestion,
    IntakeQuestionnaireVersion,
    RecruitmentIntake,
)


class IntakeQuestionInline(admin.TabularInline):
    model = IntakeQuestion
    extra = 0


class IntakePanelInline(admin.TabularInline):
    model = IntakePanel
    extra = 0


@admin.register(IntakeQuestionnaireVersion)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "status", "effective_date")
    list_filter = ("status",)
    inlines = [IntakePanelInline]


@admin.register(IntakePanel)
class PanelAdmin(admin.ModelAdmin):
    list_display = ("questionnaire", "title", "order")
    inlines = [IntakeQuestionInline]


@admin.register(RecruitmentIntake)
class RecruitmentIntakeAdmin(admin.ModelAdmin):
    list_display = ("id", "questionnaire", "recruiter", "status", "current_panel_order", "person")
    list_filter = ("status",)
