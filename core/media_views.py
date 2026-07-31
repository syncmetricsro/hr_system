"""Permission-checked delivery of uploaded media.

Uploaded files live on a Dokku-mounted volume and are **never** served by a
bare nginx alias. `docs/product/avatar-design.md` and
`certificate-upload-design.md` originally sketched one; that would have made
every certificate scan readable by anyone holding the URL, because a UUID
filename is obscurity, not authorization (production-readiness item 3).

So `/media/` has no route at all, and each file is reached through a view that
re-runs the same checks as the page it appears on:

* person avatars — the office boundary (ADR 0026), same as the person's record
* user avatars — any authenticated colleague; staff appear in queues across
  offices, and a staff headshot is not office data
* certificate documents — the office boundary **and** ``can_view_sensitive``,
  the rule already decided for DOB and identifiers. The *existence* of a
  certificate is a broad read; the scan itself is not.

If per-request cost ever matters, the upgrade path is ``X-Accel-Redirect``
(Django authorizes, nginx sends the bytes) via a Dokku ``nginx-includes``
file. That keeps the permission check. Do not replace this with a plain alias.
"""

from __future__ import annotations

import mimetypes
from pathlib import PurePosixPath

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.http import http_date
from django.views.decorators.http import require_safe

from core.accounts.models import User
from core.offices.scoping import assert_person_in_scope
from core.people.models import Person
from core.people.permissions import can_view_sensitive

# Uploads are re-encoded to a known set on the way in (core.media), so the
# content type is derived from our own stored name, never from anything the
# browser claimed.
INLINE_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}

# Private: correct for per-user-authorized content behind a shared proxy.
# Short enough that a revoked permission stops mattering quickly, long enough
# that a list of 50 avatars is not 50 round trips on every navigation.
CACHE_SECONDS = 300


def _serve(fieldfile, *, download_name: str | None = None) -> FileResponse:
    """Stream a stored file, or 404 if the row points at a file that is gone.

    A missing file is a data problem, not a crash: it happens after a restore
    from a database dump taken without the media volume, and it must not
    500 the page that embeds it.
    """
    if not fieldfile:
        raise Http404("No file")
    try:
        handle = fieldfile.open("rb")
    except (FileNotFoundError, OSError, ValueError):
        raise Http404("File is missing from storage") from None

    stored_name = PurePosixPath(fieldfile.name).name
    content_type = mimetypes.guess_type(stored_name)[0] or "application/octet-stream"
    response = FileResponse(
        handle,
        content_type=content_type,
        as_attachment=content_type not in INLINE_TYPES,
        filename=download_name or stored_name,
    )
    response["Cache-Control"] = f"private, max-age={CACHE_SECONDS}"
    try:
        response["Last-Modified"] = http_date(
            fieldfile.storage.get_modified_time(fieldfile.name).timestamp()
        )
        response["ETag"] = f'"{fieldfile.size}-{stored_name}"'
    except (NotImplementedError, OSError, ValueError):
        # Storage backends need not support modified time; the response is
        # still correct without a validator.
        pass
    return response


@require_safe
@login_required
def person_avatar(request: HttpRequest, pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=pk)
    assert_person_in_scope(request.user, person)
    return _serve(person.avatar)


@require_safe
@login_required
def user_avatar(request: HttpRequest, pk: int) -> HttpResponse:
    """Staff headshots are not office data - a coordinator in one office sees
    colleagues from another in shared queues and audit rows - so this needs
    authentication but no office check."""
    user = get_object_or_404(User, pk=pk)
    return _serve(user.avatar)


@require_safe
@login_required
def certificate_document(request: HttpRequest, pk: int) -> HttpResponse:
    from features.compliance.models import Certificate

    certificate = get_object_or_404(Certificate.objects.select_related("person"), pk=pk)
    assert_person_in_scope(request.user, certificate.person)
    if not can_view_sensitive(request.user, certificate.person):
        # Same rule as DOB/identifiers: a scan of an occupational licence is
        # more than the broad read that shows the certificate row exists.
        raise PermissionDenied("Not permitted to view this document.")
    person = certificate.person
    suffix = PurePosixPath(certificate.front_document.name or "").suffix
    return _serve(
        certificate.front_document,
        download_name=f"{person.last_name}-{certificate.name}{suffix}".replace(
            " ", "-"
        ),
    )


@require_safe
@login_required
def certificate_back_document(request: HttpRequest, pk: int) -> HttpResponse:
    from features.compliance.models import Certificate

    certificate = get_object_or_404(Certificate.objects.select_related("person"), pk=pk)
    assert_person_in_scope(request.user, certificate.person)
    if not can_view_sensitive(request.user, certificate.person):
        raise PermissionDenied("Not permitted to view this document.")
    person = certificate.person
    suffix = PurePosixPath(certificate.back_document.name or "").suffix
    return _serve(
        certificate.back_document,
        download_name=f"{person.last_name}-{certificate.name}-back{suffix}".replace(
            " ", "-"
        ),
    )
