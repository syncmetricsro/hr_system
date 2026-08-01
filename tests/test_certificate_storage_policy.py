from __future__ import annotations

import io

import pytest
from django.core.files.base import ContentFile
from django.core.management import CommandError, call_command
from PIL import Image

from core.audit.models import AuditEvent
from core.people.models import Person
from features.compliance.models import Certificate, CertificateCategory

pytestmark = pytest.mark.django_db


def _image_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (100, 80), (20, 30, 40)).save(buffer, format="JPEG")
    return buffer.getvalue()


def test_policy_command_reports_without_changing_disallowed_file(capsys):
    person = Person.objects.create(first_name="Mira", last_name="Novakova")
    certificate = Certificate.objects.create(
        person=person,
        category=CertificateCategory.HEALTH,
        name="Historical health metadata",
        never_expires=True,
    )
    certificate.front_document.save(
        "historical.jpg", ContentFile(_image_bytes()), save=True
    )

    call_command("enforce_certificate_storage_policy")

    certificate.refresh_from_db()
    assert certificate.front_document
    assert "Disallowed certificate records with files: 1" in capsys.readouterr().out


def test_policy_command_requires_explicit_fictional_data_confirmation():
    with pytest.raises(CommandError, match="confirm-fictional-data"):
        call_command("enforce_certificate_storage_policy", purge_disallowed=True)


def test_policy_command_purges_disallowed_file_after_commit(
    django_capture_on_commit_callbacks,
):
    person = Person.objects.create(first_name="Mira", last_name="Novakova")
    certificate = Certificate.objects.create(
        person=person,
        category=CertificateCategory.HEALTH,
        name="Historical health metadata",
        never_expires=True,
    )
    certificate.front_document.save(
        "historical.jpg", ContentFile(_image_bytes()), save=True
    )
    stored_name = certificate.front_document.name
    storage = certificate.front_document.storage

    with django_capture_on_commit_callbacks(execute=True):
        call_command(
            "enforce_certificate_storage_policy",
            purge_disallowed=True,
            confirm_fictional_data=True,
        )

    certificate.refresh_from_db()
    assert not certificate.front_document
    assert not storage.exists(stored_name)
    assert AuditEvent.objects.filter(
        action="certificate.files_purged", person=person
    ).exists()
