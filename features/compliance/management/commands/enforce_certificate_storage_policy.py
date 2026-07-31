from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

from core.audit.services import record_event
from features.compliance.models import FILE_ALLOWED_CATEGORIES, Certificate


class Command(BaseCommand):
    help = (
        "Report certificate files attached to disallowed categories; optionally "
        "purge them from a confirmed fictional-data environment."
    )

    def add_arguments(self, parser):
        parser.add_argument("--purge-disallowed", action="store_true")
        parser.add_argument("--confirm-fictional-data", action="store_true")

    def handle(self, *args, **options):
        has_front = Q(front_document__isnull=False) & ~Q(front_document="")
        has_back = Q(back_document__isnull=False) & ~Q(back_document="")
        disallowed = Certificate.objects.exclude(
            category__in=FILE_ALLOWED_CATEGORIES
        ).filter(has_front | has_back)
        rows = list(disallowed.order_by("pk"))
        self.stdout.write(f"Disallowed certificate records with files: {len(rows)}")
        for certificate in rows:
            self.stdout.write(
                f"- certificate={certificate.pk} person={certificate.person_id} "
                f"category={certificate.category} front={bool(certificate.front_document)} "
                f"back={bool(certificate.back_document)}"
            )

        if not options["purge_disallowed"]:
            return
        if not options["confirm_fictional_data"]:
            raise CommandError(
                "Refusing to delete files without --confirm-fictional-data."
            )

        with transaction.atomic():
            for certificate in rows:
                for field in (
                    certificate.front_document,
                    certificate.back_document,
                ):
                    if field:
                        name = field.name
                        storage = field.storage
                        transaction.on_commit(lambda n=name, s=storage: s.delete(n))
                certificate.front_document = None
                certificate.back_document = None
                certificate.save(update_fields=["front_document", "back_document"])
                record_event(
                    None,
                    "certificate.files_purged",
                    target=certificate,
                    person=certificate.person_id,
                    reason="disallowed category in fictional-data remediation",
                )
        self.stdout.write(self.style.SUCCESS(f"Purged {len(rows)} record(s)."))
