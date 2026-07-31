from __future__ import annotations

import datetime as dt
import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import translation
from PIL import Image
from pypdf import PdfReader, PdfWriter

from core.media import CertificateUploadError, process_certificate_document
from core.people.models import Person
from features.compliance.models import (
    Certificate,
    CertificateCategory,
    CertificateRecordStatus,
)
from features.compliance.services import save_certificate

pytestmark = pytest.mark.django_db

TODAY = dt.date.today()


def _jpeg_bytes(size=(1600, 1000), color=(60, 90, 140)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format="JPEG")
    return buffer.getvalue()


def _uploaded_jpeg(name="licence.jpg", **kwargs) -> SimpleUploadedFile:
    return SimpleUploadedFile(name, _jpeg_bytes(**kwargs), content_type="image/jpeg")


def _uploaded_pdf(name="licence.pdf", *, pages=1) -> SimpleUploadedFile:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=300, height=200)
    buffer = io.BytesIO()
    writer.write(buffer)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="application/pdf")


def _post_data(category=CertificateCategory.FORKLIFT):
    return {
        "category": category,
        "issuer": "Training Centre",
        "certificate_number": "FL-100",
        "issue_date": TODAY.isoformat(),
        "expiry_date": (TODAY + dt.timedelta(days=365)).isoformat(),
    }


@pytest.fixture
def make_user(django_user_model):
    def _make(role, email=None):
        return django_user_model.objects.create_user(
            email=email or f"{role}@demo.jober.test", password="x", role=role
        )

    return _make


def test_process_certificate_document_keeps_aspect_ratio_and_strips_exif():
    exif = Image.Exif()
    exif[271] = "TestCameraMake"
    buffer = io.BytesIO()
    Image.new("RGB", (3200, 2000), (10, 20, 30)).save(buffer, format="JPEG", exif=exif)
    source = SimpleUploadedFile(
        "with-exif.jpg", buffer.getvalue(), content_type="image/jpeg"
    )

    content, extension = process_certificate_document(source)

    assert extension == "jpg"
    with Image.open(io.BytesIO(content.read())) as result:
        assert result.size == (2000, 1250)
        assert not dict(result.getexif())


def test_process_certificate_document_sanitizes_pdf_metadata():
    source = _uploaded_pdf()
    content, extension = process_certificate_document(source)

    assert extension == "pdf"
    result = PdfReader(io.BytesIO(content.read()))
    assert len(result.pages) == 1
    assert "/OpenAction" not in result.trailer["/Root"]
    assert "/Names" not in result.trailer["/Root"]


def test_process_certificate_document_rejects_interactive_pdf():
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=200)
    writer.add_js("app.alert('no')")
    buffer = io.BytesIO()
    writer.write(buffer)
    source = SimpleUploadedFile(
        "interactive.pdf", buffer.getvalue(), content_type="application/pdf"
    )

    with translation.override("en"):
        with pytest.raises(CertificateUploadError, match="Interactive PDFs"):
            process_certificate_document(source)


def test_process_certificate_document_rejects_more_than_four_pages():
    with translation.override("en"):
        with pytest.raises(CertificateUploadError, match="too many pages"):
            process_certificate_document(_uploaded_pdf(pages=5))


def test_back_side_rejects_pdf():
    with translation.override("en"):
        with pytest.raises(CertificateUploadError, match="back side"):
            process_certificate_document(_uploaded_pdf(), allow_pdf=False)


@pytest.mark.parametrize(
    "upload",
    [
        SimpleUploadedFile("fake.pdf", b"not a pdf", content_type="application/pdf"),
        SimpleUploadedFile("fake.jpg", b"not an image", content_type="image/jpeg"),
        SimpleUploadedFile(
            "evil.svg", b"<svg onload='alert(1)'></svg>", content_type="image/svg+xml"
        ),
    ],
)
def test_invalid_uploads_are_rejected(upload):
    with pytest.raises(CertificateUploadError):
        process_certificate_document(upload)


def test_create_accepts_front_and_back_images(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    manager = make_user("manager")
    client.force_login(manager)

    response = client.post(
        reverse("certificate_create", args=[person.pk]),
        {
            **_post_data(),
            "front_upload": _uploaded_jpeg(),
            "back_upload": _uploaded_jpeg("back.jpg"),
        },
    )

    assert response.status_code == 302
    certificate = person.certificates.get()
    assert certificate.name == "Forklift licence"
    assert certificate.front_document
    assert certificate.back_document
    assert certificate.record_status == CertificateRecordStatus.ACTIVE


def test_create_accepts_one_pdf(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    manager = make_user("manager")
    client.force_login(manager)

    response = client.post(
        reverse("certificate_create", args=[person.pk]),
        {**_post_data(), "front_upload": _uploaded_pdf()},
    )

    assert response.status_code == 302
    assert person.certificates.get().front_document.name.endswith(".pdf")


def test_create_requires_a_file(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    manager = make_user("manager")
    client.force_login(manager)

    response = client.post(
        reverse("certificate_create", args=[person.pk]), _post_data()
    )

    assert response.status_code == 200
    assert not person.certificates.exists()


@pytest.mark.parametrize(
    "category", [CertificateCategory.HEALTH, CertificateCategory.OTHER]
)
def test_crafted_post_cannot_upload_disallowed_category(client, make_user, category):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    manager = make_user("manager")
    client.force_login(manager)

    response = client.post(
        reverse("certificate_create", args=[person.pk]),
        {**_post_data(category), "front_upload": _uploaded_jpeg()},
    )

    assert response.status_code == 200
    assert not person.certificates.exists()


def test_pdf_and_back_image_are_rejected(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    manager = make_user("manager")
    client.force_login(manager)

    response = client.post(
        reverse("certificate_create", args=[person.pk]),
        {
            **_post_data(),
            "front_upload": _uploaded_pdf(),
            "back_upload": _uploaded_jpeg("back.jpg"),
        },
    )

    assert response.status_code == 200
    assert not person.certificates.exists()


def test_unconnected_recruiter_cannot_manage_certificate(client, make_user):
    owner = make_user("recruiter", "owner@demo.jober.test")
    outsider = make_user("recruiter", "outsider@demo.jober.test")
    person = Person.objects.create(
        first_name="Olha", last_name="Kovalenko", owning_recruiter=owner
    )
    client.force_login(outsider)

    response = client.get(reverse("certificate_create", args=[person.pk]))

    assert response.status_code == 403


def test_owning_recruiter_can_manage_certificate(client, make_user):
    owner = make_user("recruiter", "owner@demo.jober.test")
    person = Person.objects.create(
        first_name="Olha", last_name="Kovalenko", owning_recruiter=owner
    )
    client.force_login(owner)

    response = client.get(reverse("certificate_create", args=[person.pk]))

    assert response.status_code == 200


def test_renewal_supersedes_previous_certificate(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    manager = make_user("manager")
    previous = Certificate(
        person=person,
        category=CertificateCategory.FORKLIFT,
        name="Forklift licence",
        expiry_date=TODAY + dt.timedelta(days=20),
    )
    save_certificate(
        previous, actor=manager, front_upload=_uploaded_jpeg(), creating=True
    )
    client.force_login(manager)

    response = client.post(
        reverse("certificate_renew", args=[previous.pk]),
        {**_post_data(), "front_upload": _uploaded_jpeg("renewed.jpg")},
    )

    assert response.status_code == 302
    previous.refresh_from_db()
    renewed = person.certificates.exclude(pk=previous.pk).get()
    assert previous.record_status == CertificateRecordStatus.SUPERSEDED
    assert renewed.supersedes == previous
    assert renewed.record_status == CertificateRecordStatus.ACTIVE


def test_archive_preserves_record_and_file(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    manager = make_user("manager")
    certificate = Certificate(
        person=person,
        category=CertificateCategory.FORKLIFT,
        name="Forklift licence",
        expiry_date=TODAY + dt.timedelta(days=20),
    )
    save_certificate(
        certificate, actor=manager, front_upload=_uploaded_jpeg(), creating=True
    )
    stored_name = certificate.front_document.name
    storage = certificate.front_document.storage
    client.force_login(manager)

    response = client.post(
        reverse("certificate_archive", args=[certificate.pk]),
        {"reason": "No longer required"},
    )

    assert response.status_code == 302
    certificate.refresh_from_db()
    assert certificate.record_status == CertificateRecordStatus.ARCHIVED
    assert storage.exists(stored_name)


def test_manager_purge_deletes_files_after_commit(
    client, make_user, django_capture_on_commit_callbacks
):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    manager = make_user("manager")
    certificate = Certificate(
        person=person,
        category=CertificateCategory.FORKLIFT,
        name="Forklift licence",
        expiry_date=TODAY + dt.timedelta(days=20),
    )
    save_certificate(
        certificate,
        actor=manager,
        front_upload=_uploaded_jpeg(),
        back_upload=_uploaded_jpeg("back.jpg"),
        creating=True,
    )
    names = [certificate.front_document.name, certificate.back_document.name]
    storage = certificate.front_document.storage
    client.force_login(manager)

    with django_capture_on_commit_callbacks(execute=True):
        response = client.post(
            reverse("certificate_purge_files", args=[certificate.pk]),
            {"reason": "Wrong person's document"},
        )

    assert response.status_code == 302
    certificate.refresh_from_db()
    assert certificate.record_status == CertificateRecordStatus.ARCHIVED
    assert not certificate.front_document
    assert not certificate.back_document
    assert all(not storage.exists(name) for name in names)


def test_recruiter_cannot_purge_files(client, make_user):
    owner = make_user("recruiter")
    person = Person.objects.create(
        first_name="Olha", last_name="Kovalenko", owning_recruiter=owner
    )
    certificate = Certificate.objects.create(
        person=person,
        category=CertificateCategory.FORKLIFT,
        name="Forklift licence",
        expiry_date=TODAY + dt.timedelta(days=20),
    )
    client.force_login(owner)

    response = client.post(
        reverse("certificate_purge_files", args=[certificate.pk]),
        {"reason": "No"},
    )

    assert response.status_code == 403


def test_certificate_events_include_before_and_after(client, make_user):
    from core.audit.models import AuditEvent

    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    manager = make_user("manager")
    client.force_login(manager)
    client.post(
        reverse("certificate_create", args=[person.pk]),
        {**_post_data(), "front_upload": _uploaded_jpeg()},
    )
    certificate = person.certificates.get()
    client.post(
        reverse("certificate_edit", args=[certificate.pk]),
        {
            **_post_data(),
            "issuer": "Updated issuer",
            "front_upload": _uploaded_jpeg("clearer.jpg"),
        },
    )

    created, updated = AuditEvent.objects.filter(
        actor=manager, action__in=["certificate.created", "certificate.updated"]
    ).order_by("pk")
    assert created.metadata["before"] is None
    assert created.metadata["after"]["has_front"] is True
    assert updated.metadata["before"]["issuer"] == "Training Centre"
    assert updated.metadata["after"]["issuer"] == "Updated issuer"
    assert updated.metadata["files_changed"] == ["front"]


def test_person_detail_shows_current_and_history(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    Certificate.objects.create(
        person=person,
        name="Forklift licence",
        category=CertificateCategory.FORKLIFT,
        expiry_date=TODAY + dt.timedelta(days=30),
    )
    Certificate.objects.create(
        person=person,
        name="Old crane licence",
        category=CertificateCategory.CRANE,
        record_status=CertificateRecordStatus.ARCHIVED,
        expiry_date=TODAY - dt.timedelta(days=30),
    )
    manager = make_user("manager")
    client.force_login(manager)

    response = client.get(reverse("person_detail", args=[person.pk]))

    assert response.status_code == 200
    panel = next(
        item
        for item in response.context["person_panels"]
        if item["template"] == "panels/compliance_certificates.html"
    )
    assert [item.category for item in panel["certificates"]] == [
        CertificateCategory.FORKLIFT
    ]
    assert [item.category for item in panel["certificate_history"]] == [
        CertificateCategory.CRANE
    ]
