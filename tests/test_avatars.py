from __future__ import annotations

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from core.media import AvatarUploadError, process_avatar_upload
from core.people.models import Person

pytestmark = pytest.mark.django_db


def _jpeg_bytes(size=(1200, 800), color=(200, 100, 50)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format="JPEG")
    return buffer.getvalue()


def _uploaded_jpeg(name="photo.jpg", **kwargs) -> SimpleUploadedFile:
    return SimpleUploadedFile(name, _jpeg_bytes(**kwargs), content_type="image/jpeg")


@pytest.fixture
def make_user(django_user_model):
    def _make(role, email=None):
        return django_user_model.objects.create_user(
            email=email or f"{role}@demo.jober.test", password="x", role=role
        )
    return _make


# --- process_avatar_upload -------------------------------------------------

def test_process_avatar_upload_reencodes_as_square_webp():
    processed = process_avatar_upload(_uploaded_jpeg(size=(1200, 800)))
    with Image.open(io.BytesIO(processed.read())) as result:
        assert result.format == "WEBP"
        assert result.size == (512, 512)


def test_process_avatar_upload_rejects_non_image_bytes():
    garbage = SimpleUploadedFile("fake.jpg", b"not an image", content_type="image/jpeg")
    with pytest.raises(AvatarUploadError):
        process_avatar_upload(garbage)


def test_process_avatar_upload_rejects_svg():
    svg = SimpleUploadedFile(
        "evil.svg", b"<svg onload='alert(1)'></svg>", content_type="image/svg+xml"
    )
    with pytest.raises(AvatarUploadError):
        process_avatar_upload(svg)


def test_process_avatar_upload_rejects_oversized_file():
    oversized = SimpleUploadedFile(
        "big.jpg", b"x" * (5 * 1024 * 1024 + 1), content_type="image/jpeg"
    )
    with pytest.raises(AvatarUploadError):
        process_avatar_upload(oversized)


def test_process_avatar_upload_strips_exif():
    exif = Image.Exif()
    exif[271] = "TestCameraMake"  # Make tag - stands in for GPS/other metadata
    buffer = io.BytesIO()
    Image.new("RGB", (400, 300), (10, 20, 30)).save(buffer, format="JPEG", exif=exif)
    source = SimpleUploadedFile("with_exif.jpg", buffer.getvalue(), content_type="image/jpeg")

    processed = process_avatar_upload(source)
    with Image.open(io.BytesIO(processed.read())) as result:
        assert not dict(result.getexif())


# --- Own avatar (User self-service) ----------------------------------------

def test_user_can_upload_own_avatar(client, make_user):
    user = make_user("recruiter")
    client.force_login(user)
    resp = client.post(
        reverse("avatar_upload"),
        {"avatar": _uploaded_jpeg(), "next": "/en/"},
    )
    assert resp.status_code == 302
    user.refresh_from_db()
    assert user.avatar


def test_user_cannot_upload_avatar_when_anonymous(client):
    resp = client.post(reverse("avatar_upload"), {"avatar": _uploaded_jpeg()})
    assert resp.status_code in (302, 401, 403)  # redirected to login


def test_invalid_avatar_upload_shows_error_and_does_not_crash(client, make_user):
    user = make_user("manager")
    client.force_login(user)
    garbage = SimpleUploadedFile("fake.jpg", b"not an image", content_type="image/jpeg")
    resp = client.post(reverse("avatar_upload"), {"avatar": garbage, "next": "/en/"})
    assert resp.status_code == 302
    user.refresh_from_db()
    assert not user.avatar


def test_user_can_remove_own_avatar(client, make_user):
    user = make_user("observer")
    client.force_login(user)
    client.post(reverse("avatar_upload"), {"avatar": _uploaded_jpeg(), "next": "/en/"})
    user.refresh_from_db()
    assert user.avatar
    client.post(reverse("avatar_remove"), {"next": "/en/"})
    user.refresh_from_db()
    assert not user.avatar


def test_avatar_upload_records_added_then_replaced_audit_events(client, make_user):
    from core.audit.models import AuditEvent

    user = make_user("recruiter")
    client.force_login(user)
    client.post(reverse("avatar_upload"), {"avatar": _uploaded_jpeg(), "next": "/en/"})
    client.post(reverse("avatar_upload"), {"avatar": _uploaded_jpeg(), "next": "/en/"})
    actions = list(
        AuditEvent.objects.filter(actor=user, action__startswith="user.avatar_")
        .order_by("pk").values_list("action", flat=True)
    )
    assert actions == ["user.avatar_added", "user.avatar_replaced"]


# --- Worker avatar (staff-uploaded) -----------------------------------------

@pytest.mark.jober_only  # role grants below are asserted against Jober's policy
def test_recruiter_can_upload_worker_avatar(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    recruiter = make_user("recruiter")
    client.force_login(recruiter)
    resp = client.post(
        reverse("person_avatar_upload", args=[person.pk]),
        {"avatar": _uploaded_jpeg()},
    )
    assert resp.status_code == 302
    person.refresh_from_db()
    assert person.avatar


@pytest.mark.jober_only
def test_coordinator_cannot_upload_worker_avatar(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    coordinator = make_user("coordinator")
    client.force_login(coordinator)
    resp = client.post(
        reverse("person_avatar_upload", args=[person.pk]),
        {"avatar": _uploaded_jpeg()},
    )
    assert resp.status_code == 403
    person.refresh_from_db()
    assert not person.avatar


@pytest.mark.jober_only
def test_manager_can_remove_worker_avatar(client, make_user):
    person = Person.objects.create(first_name="Olha", last_name="Kovalenko")
    manager = make_user("manager")
    client.force_login(manager)
    client.post(reverse("person_avatar_upload", args=[person.pk]), {"avatar": _uploaded_jpeg()})
    person.refresh_from_db()
    assert person.avatar
    client.post(reverse("person_avatar_remove", args=[person.pk]))
    person.refresh_from_db()
    assert not person.avatar


# --- {% avatar %} template tag ----------------------------------------------

def test_avatar_tag_renders_worker_default_for_person_with_no_photo():
    from core.ui.templatetags.avatars import avatar

    person = Person(first_name="No", last_name="Photo")
    html = avatar(person, size="md")
    assert "<img" in html
    assert "default_worker.webp" in html


@pytest.mark.parametrize("role", ["recruiter", "coordinator", "manager", "observer"])
def test_avatar_tag_renders_matching_role_default_for_user_with_no_photo(make_user, role):
    from core.ui.templatetags.avatars import avatar

    user = make_user(role, email=f"nophoto-{role}@demo.jober.test")
    html = avatar(user, size="md")
    assert "<img" in html
    assert f"default_{role}.webp" in html


@pytest.mark.parametrize(
    "role", ["worker", "recruiter", "coordinator", "manager", "observer"]
)
def test_default_avatar_file_is_actually_discoverable_by_staticfiles(role):
    """{% static %} builds a URL string without checking the file exists -
    this is the real check. Catches the exact mistake this feature shipped
    with once already: the files were first placed under core/static/core/
    avatars/, which STATICFILES_DIRS never scans (only the top-level
    static/ dir and each client's static/ dir) - `static()` still happily
    returned a URL for a file nothing would ever actually serve."""
    from django.contrib.staticfiles.finders import find

    assert find(f"avatars/default_{role}.webp") is not None


def test_avatar_tag_renders_image_when_photo_present(make_user):
    user = make_user("manager", email="withphoto@demo.jober.test")
    user.avatar.save("avatar.webp", process_avatar_upload(_uploaded_jpeg()), save=True)
    from core.ui.templatetags.avatars import avatar

    html = avatar(user, size="sm")
    assert "<img" in html
    assert user.avatar.url in html
