from __future__ import annotations

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from core.media import CertificateUploadError, process_certificate_document
from core.people.models import Person
from features.compliance.models import Certificate, CertificateCategory
from features.payslips.services import _simple_pdf

pytestmark = pytest.mark.django_db


def _jpeg_bytes(size=(1600, 1000), color=(60, 90, 140)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format="JPEG")
    return buffer.getvalue()


def _uploaded_jpeg(name="licence.jpg", **kwargs) -> SimpleUploadedFile:
    return SimpleUploadedFile(name, _jpeg_bytes(**kwargs), content_type="image/jpeg")


def _uploaded_pdf(name="licence.pdf") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, _simple_pdf(["Forklift licence"]), content_type="application/pdf")


@pytest.fixture
def make_user(django_user_model):
    def _make(role, email=None):
        return django_user_model.objects.create_user(
            email=email or f"{role}@demo.jober.test", password="x", role=role
        )
    return _make


# --- process_certificate_document -------------------------------------------

def test_process_certificate_document_keeps_aspect_ratio_for_images():
    content, ext = process_certificate_document(_uploaded_jpeg(size=(3200, 2000)))
    assert ext == "jpg"
    with Image.open(io.BytesIO(content.read())) as result:
        assert result.format == "JPEG"
        assert result.size == (2000, 1250)  # scaled down, ratio preserved, not cropped


def test_process_certificate_document_does_not_upscale_small_images():
    content, ext = process_certificate_document(_uploaded_jpeg(size=(400, 300)))
    with Image.open(io.BytesIO(content.read())) as result:
        assert result.size == (400, 300)


def test_process_certificate_document_accepts_pdf():
    content, ext = process_certificate_document(_uploaded_pdf())
    assert ext == "pdf"
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(content.read()))
    assert len(reader.pages) == 1


def test_process_certificate_document_rejects_garbage_pdf():
    garbage = SimpleUploadedFile("fake.pdf", b"not a pdf", content_type="application/pdf")
    with pytest.raises(CertificateUploadError):
        process_certificate_document(garbage)


def test_process_certificate_document_rejects_non_image_non_pdf():
    garbage = SimpleUploadedFile("fake.jpg", b"not an image", content_type="image/jpeg")
    with pytest.raises(CertificateUploadError):
        process_certificate_document(garbage)


def test_process_certificate_document_rejects_svg():
    svg = SimpleUploadedFile("evil.svg", b"<svg onload='alert(1)'></svg>", content_type="image/svg+xml")
    with pytest.raises(CertificateUploadError):
        process_certificate_document(svg)


def test_process_certificate_document_rejects_oversized_file():
    oversized = SimpleUploadedFile("big.jpg", b"x" * (10 * 1024 * 1024 + 1), content_type="image/jpeg")
    with pytest.raises(CertificateUploadError):
        process_certificate_document(oversized)


def test_process_certificate_document_strips_exif():
    exif = Image.Exif()
    exif[271] = "TestCameraMake"
    buffer = io.BytesIO()
    Image.new("RGB", (400, 300), (10, 20, 30)).save(buffer, format="JPEG", exif=exif)
    source = SimpleUploadedFile("with_exif.jpg", buffer.getvalue(), content_type="image/jpeg")

    content, _ext = process_certificate_document(source)
    with Image.open(io.BytesIO(content.read())) as result:
        assert not dict(result.getexif())


# --- Create / edit / delete views (RBAC) ------------------------------------

@pytest.mark.jober_only
def test_recruiter_can_add_certificate(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    recruiter = make_user("recruiter")
    client.force_login(recruiter)
    resp = client.post(
        reverse("certificate_create", args=[person.pk]),
        {"category": CertificateCategory.FORKLIFT, "name": "Forklift licence", "document": _uploaded_jpeg()},
    )
    assert resp.status_code == 302
    cert = person.certificates.get()
    assert cert.category == CertificateCategory.FORKLIFT
    assert cert.document


@pytest.mark.jober_only
def test_coordinator_can_add_certificate(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    coordinator = make_user("coordinator")
    client.force_login(coordinator)
    resp = client.post(
        reverse("certificate_create", args=[person.pk]),
        {"category": CertificateCategory.OTHER, "name": "Health check"},
    )
    assert resp.status_code == 302
    assert person.certificates.count() == 1


@pytest.mark.jober_only
def test_observer_cannot_add_certificate(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    observer = make_user("observer")
    client.force_login(observer)
    resp = client.post(
        reverse("certificate_create", args=[person.pk]),
        {"category": CertificateCategory.OTHER, "name": "Health check"},
    )
    assert resp.status_code == 403
    assert person.certificates.count() == 0


def test_certificate_upload_without_document_is_allowed(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    manager = make_user("manager")
    client.force_login(manager)
    resp = client.post(
        reverse("certificate_create", args=[person.pk]),
        {"category": CertificateCategory.HEALTH, "name": "Health check"},
    )
    assert resp.status_code == 302
    cert = person.certificates.get()
    assert not cert.document


def test_invalid_document_upload_shows_error_and_does_not_create(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    manager = make_user("manager")
    client.force_login(manager)
    garbage = SimpleUploadedFile("fake.jpg", b"not an image", content_type="image/jpeg")
    resp = client.post(
        reverse("certificate_create", args=[person.pk]),
        {"category": CertificateCategory.OTHER, "name": "Bad upload", "document": garbage},
    )
    assert resp.status_code == 200
    assert person.certificates.count() == 0


def test_manager_can_replace_certificate_document(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    manager = make_user("manager")
    client.force_login(manager)
    cert = Certificate.objects.create(person=person, name="Forklift licence", category=CertificateCategory.FORKLIFT)
    resp = client.post(
        reverse("certificate_edit", args=[cert.pk]),
        {"category": CertificateCategory.FORKLIFT, "name": "Forklift licence", "document": _uploaded_pdf()},
    )
    assert resp.status_code == 302
    cert.refresh_from_db()
    assert cert.document
    assert cert.document.name.endswith(".pdf")


def test_manager_can_delete_certificate(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    manager = make_user("manager")
    client.force_login(manager)
    cert = Certificate.objects.create(person=person, name="Health check")
    resp = client.post(reverse("certificate_delete", args=[cert.pk]))
    assert resp.status_code == 302
    assert not Certificate.objects.filter(pk=cert.pk).exists()


# --- Audit -------------------------------------------------------------------

def test_certificate_upload_records_uploaded_then_replaced_audit_events(client, make_user):
    from core.audit.models import AuditEvent

    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    manager = make_user("manager")
    client.force_login(manager)
    client.post(
        reverse("certificate_create", args=[person.pk]),
        {"category": CertificateCategory.OTHER, "name": "Health check", "document": _uploaded_jpeg()},
    )
    cert = person.certificates.get()
    client.post(
        reverse("certificate_edit", args=[cert.pk]),
        {"category": CertificateCategory.OTHER, "name": "Health check", "document": _uploaded_jpeg()},
    )
    actions = list(
        AuditEvent.objects.filter(actor=manager, action__startswith="certificate.")
        .order_by("pk").values_list("action", flat=True)
    )
    assert actions == ["certificate.uploaded", "certificate.replaced"]


def test_certificate_delete_records_audit_event_with_metadata(client, make_user):
    from core.audit.models import AuditEvent

    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    manager = make_user("manager")
    client.force_login(manager)
    cert = Certificate.objects.create(person=person, name="Health check")
    client.post(reverse("certificate_delete", args=[cert.pk]))
    event = AuditEvent.objects.get(actor=manager, action="certificate.deleted")
    assert event.metadata["person"] == person.pk
    assert event.metadata["name"] == "Health check"


# --- Person-detail panel ------------------------------------------------------

def test_person_detail_shows_certificate_panel(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    Certificate.objects.create(person=person, name="Forklift licence", category=CertificateCategory.FORKLIFT)
    manager = make_user("manager")
    client.force_login(manager)
    resp = client.get(reverse("person_detail", args=[person.pk]))
    assert resp.status_code == 200
    assert b"Forklift licence" in resp.content


def test_observer_does_not_see_add_certificate_button(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    observer = make_user("observer")
    client.force_login(observer)
    resp = client.get(reverse("person_detail", args=[person.pk]))
    assert resp.status_code == 200
    assert reverse("certificate_create", args=[person.pk]).encode() not in resp.content
