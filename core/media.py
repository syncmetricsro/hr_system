"""Avatar upload path + validation (docs/product/avatar-design.md).

Shared by ``core.people.Person`` and ``core.accounts.User`` — both need the
identical validate → strip EXIF → center-crop → resize → re-encode pipeline,
so it lives once here rather than duplicated per app.
"""

from __future__ import annotations

import io
import uuid

from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.translation import gettext as _

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5MB raw upload cap
MAX_INPUT_DIMENSION = 8000  # guards against decompression-bomb abuse
STORED_DIMENSION = 512
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class AvatarUploadError(Exception):
    """Raised when an uploaded file fails avatar validation."""


def save_replacing(fieldfile, name: str, content) -> None:
    """Store ``content`` on ``fieldfile``, deleting the file it replaced.

    ``FieldFile.save()`` allocates a *new* name (upload_to mints a fresh UUID)
    and never touches the old file, so every replacement used to leave an
    orphan on disk with no row referencing it - unreachable, un-auditable, and
    still holding personal data. Only an explicit *remove* deleted anything.

    The delete runs on commit: if the surrounding transaction rolls back, the
    row still points at the old file, and deleting it eagerly would have
    destroyed the live copy.
    """
    old_name = fieldfile.name or ""
    storage = fieldfile.storage
    fieldfile.save(name, content, save=True)
    if old_name and old_name != fieldfile.name:
        transaction.on_commit(lambda: storage.delete(old_name))


def _cap_pillow_pixels(image_module) -> None:
    """Second line of defence behind the header check.

    Pillow raises ``DecompressionBombError`` past ``MAX_IMAGE_PIXELS``. Its
    default (~89M pixels) is far more generous than anything this app stores,
    and the header check above can only catch a *dimension* that is too large
    - not, say, 7999 x 7999, which passes both dimension caps while decoding
    to ~64M pixels.
    """
    image_module.MAX_IMAGE_PIXELS = MAX_INPUT_DIMENSION * MAX_INPUT_DIMENSION // 2


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

    _cap_pillow_pixels(Image)

    if uploaded_file.size > MAX_UPLOAD_BYTES:
        raise AvatarUploadError("Image is too large (max 5MB).")

    raw = uploaded_file.read()
    try:
        with Image.open(io.BytesIO(raw)) as probe:
            # Dimensions come from the header, so this rejects a
            # decompression bomb *before* anything decodes it. Checking after
            # image.load() - as this did originally - meant the bomb had
            # already been expanded in memory by the time it was refused.
            probe_size = probe.size
            probe.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        raise AvatarUploadError("File is not a valid image.") from None

    if max(probe_size) > MAX_INPUT_DIMENSION:
        raise AvatarUploadError("Image dimensions are too large.")

    # verify() leaves the file object unusable for further operations -
    # reopen fresh for the actual processing.
    try:
        image = Image.open(io.BytesIO(raw))
        image.load()
    except (UnidentifiedImageError, OSError, ValueError):
        raise AvatarUploadError("File is not a valid image.") from None

    if image.format not in ALLOWED_FORMATS:
        raise AvatarUploadError("Only JPEG, PNG, or WebP images are allowed.")

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
CERTIFICATE_MAX_PDF_PAGES = 4
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


def process_certificate_document(
    uploaded_file, *, allow_pdf: bool = True
) -> tuple[ContentFile, str]:
    """Validate an uploaded certificate document — image or PDF — and return
    ``(content, extension)`` ready to store.

    Images are decode-verified, capped, stripped of EXIF by re-encoding from
    decoded pixel data, and capped to a max dimension — but, unlike avatars,
    never center-cropped, since the document must stay legible. PDFs are
    validated by instantiating ``pypdf.PdfReader`` and touching ``.pages``
    (the PDF equivalent of ``Image.verify()``), rejected if interactive, and
    rebuilt from its page content to discard catalogue actions and metadata.

    Raises ``CertificateUploadError`` with a message safe to show the user.
    """
    if uploaded_file.size > CERTIFICATE_MAX_UPLOAD_BYTES:
        raise CertificateUploadError(_("File is too large (max 10MB)."))

    raw = uploaded_file.read()
    is_pdf = (uploaded_file.content_type or "").lower() == "application/pdf" or (
        uploaded_file.name or ""
    ).lower().endswith(".pdf")

    if is_pdf:
        if not allow_pdf:
            raise CertificateUploadError(_("The back side must be an image."))

        from pypdf import PdfReader, PdfWriter
        from pypdf.errors import PdfReadError

        try:
            reader = PdfReader(io.BytesIO(raw))
            if reader.is_encrypted:
                raise CertificateUploadError(_("Encrypted PDFs are not allowed."))
            page_count = len(reader.pages)
            if page_count < 1:
                raise CertificateUploadError(_("PDF has no pages."))
            if page_count > CERTIFICATE_MAX_PDF_PAGES:
                raise CertificateUploadError(_("PDF has too many pages (max 4)."))

            root = reader.trailer.get("/Root", {})
            forbidden_root_keys = {"/AA", "/AcroForm", "/Names", "/OpenAction"}
            if any(key in root for key in forbidden_root_keys):
                raise CertificateUploadError(
                    _("Interactive PDFs or PDFs with attachments are not allowed.")
                )
            for page in reader.pages:
                if "/AA" in page or "/Annots" in page:
                    raise CertificateUploadError(
                        _("Interactive PDFs or PDFs with attachments are not allowed.")
                    )

            # Rebuild from page content rather than retaining the source
            # catalogue. This drops document metadata and catalogue-level
            # actions/attachments while preserving the scanned pages.
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            buffer = io.BytesIO()
            writer.write(buffer)
        except (PdfReadError, ValueError, OSError, KeyError):
            raise CertificateUploadError(_("File is not a valid PDF.")) from None
        return ContentFile(buffer.getvalue()), "pdf"

    from PIL import Image, UnidentifiedImageError

    _cap_pillow_pixels(Image)

    try:
        with Image.open(io.BytesIO(raw)) as probe:
            probe_size = probe.size  # header only - see process_avatar_upload
            probe.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        raise CertificateUploadError(_("File is not a valid image or PDF.")) from None

    if max(probe_size) > CERTIFICATE_MAX_INPUT_DIMENSION:
        raise CertificateUploadError(_("Image dimensions are too large."))

    try:
        image = Image.open(io.BytesIO(raw))
        image.load()
    except (UnidentifiedImageError, OSError, ValueError):
        raise CertificateUploadError(_("File is not a valid image or PDF.")) from None

    if image.format not in CERTIFICATE_IMAGE_EXTENSIONS:
        raise CertificateUploadError(
            _("Only JPEG, PNG, WebP images or PDF documents are allowed.")
        )

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
