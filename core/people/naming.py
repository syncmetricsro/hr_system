"""Canonical name folding, shared by blacklist matching and name search.

Moved out of ``features/blacklist/services.py`` on 2026-07-27 so ``core`` can
use it too - dependencies point feature -> core only (ADR 0021), so the audit
log and People search could not have imported it where it was.

**This function feeds HMAC fingerprints.** Changing what it returns silently
invalidates every stored blacklist fingerprint, which fails open: a barred
person stops matching and is quietly admitted. It was moved verbatim, and
``tests/test_blacklist.py`` pins the canonical form for exactly that reason.
Treat any edit here as a data migration, not a refactor.
"""

from __future__ import annotations

import re
import unicodedata

# Latin letters NFKD cannot decompose to base + combining mark; folded
# explicitly so names like Groß/Łukasz survive normalization. Anything still
# non-ASCII afterwards (Cyrillic, CJK, …) is stripped by the final regex.
_FOLD = str.maketrans(
    {
        "ß": "SS",
        "ẞ": "SS",
        "Đ": "D",
        "đ": "D",
        "Ø": "O",
        "ø": "O",
        "Ł": "L",
        "ł": "L",
        "Æ": "AE",
        "æ": "AE",
        "Œ": "OE",
        "œ": "OE",
    }
)


def fold_name(identifier: str) -> str:
    """Uppercase, transliterate diacritics, and strip non-alphanumerics so
    trivial formatting/spelling differences (spaces, slashes in a rodné číslo,
    Kováč vs Kovac) don't defeat matching.

    Pure ASCII-alphanumeric input passes through unchanged, so fingerprints of
    existing stored ID codes are stable across this normalizer.

    Stripping spaces also makes it usable for substring search: "horvat" folds
    to a substring of "DIANAHORVATHOVA", and so does "diana horvat".
    """
    text = (identifier or "").upper().translate(_FOLD)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^A-Za-z0-9]", "", text)
