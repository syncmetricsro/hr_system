"""RFC 6238 TOTP — pure stdlib (Stage B4b, ADR 0021; no new dependencies).

HMAC-SHA1, 30-second step, 6 digits, ±1 step verification window. QR rendering
is intentionally absent (an image library would need a vendored asset + ADR);
setup shows the otpauth:// URI and the manual-entry secret instead.
"""

from __future__ import annotations

import base64
import hmac
import secrets
import struct
import time
from hashlib import sha1
from urllib.parse import quote

STEP_SECONDS = 30
DIGITS = 6


def generate_secret() -> str:
    """A new 160-bit secret, base32-encoded (the authenticator-app format)."""
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii")


def totp_at(secret_b32: str, timestamp: int) -> str:
    """The 6-digit code for a given unix time (RFC 6238 / RFC 4226)."""
    key = base64.b32decode(secret_b32, casefold=True)
    counter = int(timestamp) // STEP_SECONDS
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return str(code % (10 ** DIGITS)).zfill(DIGITS)


def verify(secret_b32: str, code: str, *, at: int | None = None, window: int = 1) -> bool:
    """Constant-time comparison across the ±window steps."""
    if not code or not code.strip().isdigit():
        return False
    now = int(time.time()) if at is None else int(at)
    candidate = code.strip()
    ok = False
    for offset in range(-window, window + 1):
        expected = totp_at(secret_b32, now + offset * STEP_SECONDS)
        # No early exit: check every step to keep timing uniform.
        ok = hmac.compare_digest(expected, candidate) or ok
    return ok


def provisioning_uri(secret_b32: str, *, account: str, issuer: str) -> str:
    """otpauth:// URI for authenticator apps (manual entry / future QR)."""
    label = f"{quote(issuer)}:{quote(account)}"
    return (
        f"otpauth://totp/{label}?secret={secret_b32}"
        f"&issuer={quote(issuer)}&algorithm=SHA1&digits={DIGITS}&period={STEP_SECONDS}"
    )
