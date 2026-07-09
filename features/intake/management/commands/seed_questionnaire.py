from __future__ import annotations

from django.core.management.base import BaseCommand

from features.intake.models import (
    IntakePanel,
    IntakeQuestion,
    IntakeQuestionnaireVersion,
    QuestionnaireStatus,
    QuestionType,
)

NEGATIVES = ["nie", "none", "žiadne", "ziadne", "nincs", "ні", "немає"]


class Command(BaseCommand):
    help = "Seed a published recruiter intake questionnaire (idempotent)."

    def handle(self, *args, **options):
        version, created = IntakeQuestionnaireVersion.objects.get_or_create(
            name="Recruiter intake",
            version=1,
            defaults={"status": QuestionnaireStatus.PUBLISHED},
        )
        if not created:
            self.stdout.write("Questionnaire already present.")
            return

        identity = IntakePanel.objects.create(questionnaire=version, title="Identity", order=0)
        contact = IntakePanel.objects.create(questionnaire=version, title="Contact", order=1)
        compliance = IntakePanel.objects.create(questionnaire=version, title="Compliance", order=2)

        def q(panel, key, label, **kw):
            IntakeQuestion.objects.create(panel=panel, stable_key=key, label=label, **kw)

        q(identity, "first_name", "First name", type=QuestionType.TEXT, required=True, order=0)
        q(identity, "last_name", "Last name", type=QuestionType.TEXT, required=True, order=1)
        q(identity, "date_of_birth", "Date of birth", type=QuestionType.DATE, order=2)
        q(identity, "place_of_birth", "Place of birth", type=QuestionType.TEXT, order=3)

        q(contact, "phone", "Phone", type=QuestionType.TEXT, required=True, order=0)
        q(contact, "address", "Address", type=QuestionType.TEXT, order=1)
        q(contact, "nationality", "Nationality", type=QuestionType.TEXT, order=2)
        q(contact, "preferred_language", "Preferred language", type=QuestionType.SELECT,
          options=["en", "sk", "hu", "uk"], order=3)

        q(compliance, "disability", "Disability — type 'nie' if none",
          type=QuestionType.TEXT, required=True, order=0,
          requires_typed_negative=True, accepted_negatives=NEGATIVES)
        q(compliance, "disability_type", "Disability type",
          type=QuestionType.TEXT, required=True, order=1, conditional_on="disability")

        self.stdout.write(self.style.SUCCESS("Seeded published 'Recruiter intake' v1."))
