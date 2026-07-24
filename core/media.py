"""Avatar upload path + validation (docs/product/avatar-design.md).

Shared by ``core.people.Person`` and ``core.accounts.User`` — both need the
identical validate → strip EXIF → center-crop → resize → re-encode pipeline,
so it lives once here rather than duplicated per app.
"""

from __future__ import annotations

import io
import uuid

from django.core.files.base import ContentFile

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5MB raw upload cap
MAX_INPUT_DIMENSION = 8000  # guards against decompression-bomb abuse
STORED_DIMENSION = 512
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class AvatarUploadError(Exception):
    """Raised when an uploaded file fails avatar validation."""


def avatar_upload_path(instance, filename: str) -> str:
    """``avatars/{model}/{uuid4}.webp`` — UUID names avoid path collisions/
    enumeration and bust browser cache automatically on replace. Always
    ``.webp`` regardless of the source format, since process_avatar_upload
    always re-encodes to WebP."""
    model_name = instance.__class__.__name__.lower()
    return f"avatars/{model_name}/{uuid.uuid4().hex}.webp"


def process_avatar_upload(uploaded_file) -> ContentFile:
    """Validate an uploaded avatar and return a re-encoded, ready-to-store
    WebP image: decode-and-verify it's a genuine image (not just a trusted
    extension), reject SVG/anything not JPEG/PNG/WebP outright
    (script-injection risk), strip EXIF (phone photos carry GPS tags —
    matters once the real-data/legal gate opens), center-crop to square,
    resize to a max stored dimension, and re-encode as WebP.

    Raises ``AvatarUploadError`` with a message safe to show the user on
    any invalid input — never lets a Pillow exception surface directly.
    """
    from PIL import Image, UnidentifiedImageError

    if uploaded_file.size > MAX_UPLOAD_BYTES:
        raise AvatarUploadError("Image is too large (max 5MB).")

    raw = uploaded_file.read()
    try:
        with Image.open(io.BytesIO(raw)) as probe:
            probe.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        raise AvatarUploadError("File is not a valid image.") from None

    # verify() leaves the file object unusable for further operations -
    # reopen fresh for the actual processing.
    try:
        image = Image.open(io.BytesIO(raw))
        image.load()
    except (UnidentifiedImageError, OSError, ValueError):
        raise AvatarUploadError("File is not a valid image.") from None

    if image.format not in ALLOWED_FORMATS:
        raise AvatarUploadError("Only JPEG, PNG, or WebP images are allowed.")
    if max(image.size) > MAX_INPUT_DIMENSION:
        raise AvatarUploadError("Image dimensions are too large.")

    # Re-encoding from decoded pixel data (not the original bytes) already
    # drops EXIF by construction - no separate strip step needed.
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    width, height = image.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    image = image.crop((left, top, left + side, top + side))
    if side > STORED_DIMENSION:
        image = image.resize((STORED_DIMENSION, STORED_DIMENSION), Image.LANCZOS)

    buffer = io.BytesIO()
    image.save(buffer, format="WEBP", quality=85)
    return ContentFile(buffer.getvalue())


# --- Certificate documents (docs/product/certificate-upload-design.md) -----

CERTIFICATE_MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10MB — scans run larger than avatars
CERTIFICATE_MAX_INPUT_DIMENSION = 8000  # guards against decompression-bomb abuse
CERTIFICATE_STORED_MAX_DIMENSION = 2000  # must stay legible - no center-crop
CERTIFICATE_IMAGE_EXTENSIONS = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp"}


class CertificateUploadError(Exception):
    """Raised when an uploaded certificate document fails validation."""


def certificate_upload_path(instance, filename: str) -> str:
    """``certificates/{uuid4}.{ext}`` — extension taken from the name passed
    to ``document.save()`` (itself derived from validated content, never the
    browser-supplied filename), same collision/enumeration/cache-busting
    reasoning as ``avatar_upload_path``."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    return f"certificates/{uuid.uuid4().hex}.{ext}"


def process_certificate_document(uploaded_file) -> tuple[ContentFile, str]:
    """Validate an uploaded certificate document — image or PDF — and return
    ``(content, extension)`` ready to store.

    Images are decode-verified, capped, stripped of EXIF by re-encoding from
    decoded pixel data, and capped to a max dimension — but, unlike avatars,
    never center-cropped, since the document must stay legible. PDFs are
    validated by instantiating ``pypdf.PdfReader`` and touching ``.pages``
    (the PDF equivalent of ``Image.verify()``) and stored unmodified.

    Raises ``CertificateUploadError`` with a message safe to show the user.
    """
    if uploaded_file.size > CERTIFICATE_MAX_UPLOAD_BYTES:
        raise CertificateUploadError("File is too large (max 10MB).")

    raw = uploaded_file.read()
    is_pdf = (uploaded_file.content_type or "").lower() == "application/pdf" or (
        uploaded_file.name or ""
    ).lower().endswith(".pdf")

    if is_pdf:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError

        try:
            reader = PdfReader(io.BytesIO(raw))
            if len(reader.pages) < 1:
                raise CertificateUploadError("PDF has no pages.")
        except (PdfReadError, ValueError, OSError, KeyError):
            raise CertificateUploadError("File is not a valid PDF.") from None
        return ContentFile(raw), "pdf"

    from PIL import Image, UnidentifiedImageError

    try:
        with Image.open(io.BytesIO(raw)) as probe:
            probe.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        raise CertificateUploadError("File is not a valid image or PDF.") from None

    try:
        image = Image.open(io.BytesIO(raw))
        image.load()
    except (UnidentifiedImageError, OSError, ValueError):
        raise CertificateUploadError("File is not a valid image or PDF.") from None

    if image.format not in CERTIFICATE_IMAGE_EXTENSIONS:
        raise CertificateUploadError("Only JPEG, PNG, WebP images or PDF documents are allowed.")
    if max(image.size) > CERTIFICATE_MAX_INPUT_DIMENSION:
        raise CertificateUploadError("Image dimensions are too large.")

    stored_format = image.format
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")
    if max(image.size) > CERTIFICATE_STORED_MAX_DIMENSION:
        scale = CERTIFICATE_STORED_MAX_DIMENSION / max(image.size)
        image = image.resize(
            (max(1, round(image.width * scale)), max(1, round(image.height * scale))),
            Image.LANCZOS,
        )

    buffer = io.BytesIO()
    save_kwargs = {"quality": 90} if stored_format in ("JPEG", "WEBP") else {}
    image.save(buffer, format=stored_format, **save_kwargs)
    return ContentFile(buffer.getvalue()), CERTIFICATE_IMAGE_EXTENSIONS[stored_format]
