"""Signing a CorvinumEU manager in, from any test, in any order.

Managers have 2FA enforced on this client, and the enrolment secret is shown
**once** — on the setup screen, to whichever test reaches it first. Every later
login lands on the verify screen instead, where the secret is not displayed, so
a helper that only knows how to enrol works exactly until a second test needs
the same account.

That is not hypothetical: `test_z_certificate_uploads` and
`test_zz_card_layout` both drive `hradmin`, and whichever ran second failed with
a locator timeout on a page it never reached.

So the secret is cached here, in the process both tests share. Whoever enrols
stores it; whoever arrives later computes a code from it. Order stops mattering,
which is better than encoding an order in filenames.
"""

from __future__ import annotations

import base64
import hmac
import struct
import time
from hashlib import sha1

MANAGER_EMAIL = "hradmin@demo.corvinum.test"
PASSWORD = "demo-corvinum-2026"

#: email -> base32 TOTP secret, captured at enrolment. Process-local on purpose:
#: the browser stack is reseeded per run, so a stale secret can never outlive it.
_SECRETS: dict[str, str] = {}


def totp_at(secret: str, timestamp: int) -> str:
    key = base64.b32decode(secret, casefold=True)
    digest = hmac.new(key, struct.pack(">Q", timestamp // 30), sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(code % 1_000_000).zfill(6)


def _submit_code(page, secret: str) -> None:
    page.fill("input[name='code']", totp_at(secret, int(time.time())))
    page.locator("main form.stack button[type='submit']").click()
    page.wait_for_load_state("networkidle")


def login_manager(
    page, *, app_url: str, email: str = MANAGER_EMAIL, password: str = PASSWORD
) -> None:
    page.goto(f"{app_url}/prihlasenie/")
    page.fill("input[name='email']", email)
    page.fill("input[name='password']", password)
    page.click("form button[type='submit']")
    page.wait_for_load_state("networkidle")

    if "/2fa/setup/" in page.url:
        secret = page.locator(".detail-grid code").inner_text()
        _SECRETS[email] = secret
        _submit_code(page, secret)
    elif "/2fa/verify/" in page.url:
        secret = _SECRETS.get(email)
        if secret is None:
            raise RuntimeError(
                f"{email} is already enrolled but no test in this process "
                "captured the secret. Sign in through login_manager() "
                "everywhere so the first caller records it."
            )
        _submit_code(page, secret)
