"""Replacing an upload must not leave the old file behind, and a bomb must be
refused before it is decoded.

Both are production-readiness findings (6 and 8). The orphan one is the
GDPR-relevant half: `FieldFile.save()` mints a new name and never touches the
predecessor, so every replacement left an unreachable file on disk still
holding a photo or a scan of someone's documents — with no row pointing at it,
nothing would ever find it again to delete it.
Note on `django_capture_on_commit_callbacks`: the delete is deliberately
deferred to commit, so that a rolled-back transaction cannot destroy the file
the row still points at. pytest-django rolls every test back, so without
executing the callbacks these tests would pass vacuously — the deletion simply
would never run.
"""

from __future__ import annotations

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from core.media import (
    MAX_INPUT_DIMENSION,
    AvatarUploadError,
    process_avatar_upload,
    save_replacing,
)
from core.people.models import Person

pytestmark = pytest.mark.django_db


def _jpeg(size=(600, 400)) -> SimpleUploadedFile:
    buffer = io.BytesIO()
    Image.new("RGB", size, (10, 120, 200)).save(buffer, format="JPEG")
    return SimpleUploadedFile("p.jpg", buffer.getvalue(), content_type="image/jpeg")


# --- orphaned files on replace ---------------------------------------------


def test_replacing_an_avatar_deletes_the_file_it_replaced(
    django_user_model, django_capture_on_commit_callbacks
):
    user = django_user_model.objects.create_user(
        email="rep@demo.jober.test", password="x", role="manager"
    )
    save_replacing(user.avatar, "avatar.webp", process_avatar_upload(_jpeg()))
    first_name = user.avatar.name
    storage = user.avatar.storage
    assert storage.exists(first_name)

    with django_capture_on_commit_callbacks(execute=True):
        save_replacing(user.avatar, "avatar.webp", process_avatar_upload(_jpeg()))
    second_name = user.avatar.name

    assert second_name != first_name
    assert storage.exists(second_name)
    assert not storage.exists(first_name), "the replaced file was left orphaned"


def test_replacing_through_the_view_leaves_no_orphan(
    client, django_user_model, django_capture_on_commit_callbacks
):
    """The end-to-end version: the helper is only useful if the views use it."""
    user = django_user_model.objects.create_user(
        email="view@demo.jober.test", password="x", role="manager"
    )
    client.force_login(user)
    client.post(reverse("avatar_upload"), {"avatar": _jpeg(), "next": "/en/"})
    user.refresh_from_db()
    first_name = user.avatar.name
    storage = user.avatar.storage

    with django_capture_on_commit_callbacks(execute=True):
        client.post(reverse("avatar_upload"), {"avatar": _jpeg(), "next": "/en/"})
    user.refresh_from_db()

    assert user.avatar.name != first_name
    assert not storage.exists(first_name)


def test_a_first_upload_deletes_nothing(django_user_model):
    """Guard the off-by-one: with no predecessor there is nothing to remove,
    and an over-eager helper would delete the file it just stored."""
    user = django_user_model.objects.create_user(
        email="first@demo.jober.test", password="x", role="manager"
    )
    save_replacing(user.avatar, "avatar.webp", process_avatar_upload(_jpeg()))
    assert user.avatar.storage.exists(user.avatar.name)


@pytest.mark.jober_only
def test_replacing_a_person_avatar_leaves_no_orphan(
    client, django_user_model, django_capture_on_commit_callbacks
):
    person = Person.objects.create(first_name="Olha", last_name="K")
    recruiter = django_user_model.objects.create_user(
        email="rec@demo.jober.test", password="x", role="recruiter"
    )
    client.force_login(recruiter)
    client.post(reverse("person_avatar_upload", args=[person.pk]), {"avatar": _jpeg()})
    person.refresh_from_db()
    first_name = person.avatar.name
    storage = person.avatar.storage

    with django_capture_on_commit_callbacks(execute=True):
        client.post(
            reverse("person_avatar_upload", args=[person.pk]), {"avatar": _jpeg()}
        )
    person.refresh_from_db()

    assert person.avatar.name != first_name
    assert not storage.exists(first_name)


# --- decompression bombs ---------------------------------------------------


def test_oversized_dimensions_are_rejected_before_decoding(monkeypatch):
    """The check must read the header, not the decoded pixels. Patching
    ``Image.Image.load`` to explode proves nothing was decoded — the original
    code called ``load()`` first and only then measured, so the bomb had
    already been expanded in memory by the time it was refused."""
    from PIL import Image as PILImage

    buffer = io.BytesIO()
    Image.new("RGB", (MAX_INPUT_DIMENSION + 10, 10), (1, 2, 3)).save(
        buffer, format="PNG"
    )
    oversized = SimpleUploadedFile(
        "bomb.png", buffer.getvalue(), content_type="image/png"
    )

    def explode(self):  # pragma: no cover - must never run
        raise AssertionError("image was decoded before the dimension check")

    monkeypatch.setattr(PILImage.Image, "load", explode)

    with pytest.raises(AvatarUploadError):
        process_avatar_upload(oversized)


def test_normal_sized_image_still_processes():
    processed = process_avatar_upload(_jpeg(size=(900, 600)))
    with Image.open(io.BytesIO(processed.read())) as result:
        assert result.size == (512, 512)
