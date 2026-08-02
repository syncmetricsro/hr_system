#!/usr/bin/env python3
"""Compile GNU gettext PO catalogs to MO with the Python standard library.

The repository's runtime and test images intentionally omit the gettext OS
package.  This small compiler keeps catalog regeneration dependency-free and
does not extract or merge messages; the committed PO files remain the source
of truth.
"""

from __future__ import annotations

import ast
import struct
import sys
from pathlib import Path


def _unquote(value: str) -> str:
    parsed = ast.literal_eval(value)
    if not isinstance(parsed, str):
        raise ValueError(f"Expected a PO string, got {value!r}")
    return parsed


def parse_po(source: str) -> dict[str, str]:
    messages: dict[str, str] = {}
    entry: dict[str, object] = {}
    active: tuple[str, int | None] | None = None

    def flush() -> None:
        nonlocal entry, active
        msgid = entry.get("msgid")
        if msgid is None or entry.get("fuzzy"):
            entry = {}
            active = None
            return

        key = str(msgid)
        context = entry.get("msgctxt")
        if context is not None:
            key = f"{context}\x04{key}"
        plural = entry.get("msgid_plural")
        translations = entry.get("msgstr", {})
        if plural is not None:
            key = f"{key}\x00{plural}"
            values = translations if isinstance(translations, dict) else {}
            translated = "\x00".join(str(values[index]) for index in sorted(values))
        else:
            values = translations if isinstance(translations, dict) else {}
            translated = str(values.get(0, ""))
        if translated or key == "":
            messages[key] = translated
        entry = {}
        active = None

    for raw_line in [*source.splitlines(), ""]:
        line = raw_line.strip()
        if not line:
            flush()
            continue
        if line.startswith("#,") and "fuzzy" in line:
            entry["fuzzy"] = True
            continue
        if line.startswith("#"):
            continue
        if line.startswith("msgctxt "):
            entry["msgctxt"] = _unquote(line[8:].strip())
            active = ("msgctxt", None)
        elif line.startswith("msgid_plural "):
            entry["msgid_plural"] = _unquote(line[13:].strip())
            active = ("msgid_plural", None)
        elif line.startswith("msgid "):
            entry["msgid"] = _unquote(line[6:].strip())
            active = ("msgid", None)
        elif line.startswith("msgstr["):
            index_text, value = line[7:].split("]", 1)
            index = int(index_text)
            translations = entry.setdefault("msgstr", {})
            assert isinstance(translations, dict)
            translations[index] = _unquote(value.strip())
            active = ("msgstr", index)
        elif line.startswith("msgstr "):
            translations = entry.setdefault("msgstr", {})
            assert isinstance(translations, dict)
            translations[0] = _unquote(line[7:].strip())
            active = ("msgstr", 0)
        elif line.startswith('"') and active is not None:
            value = _unquote(line)
            field, index = active
            if field == "msgstr":
                translations = entry.setdefault("msgstr", {})
                assert isinstance(translations, dict) and index is not None
                translations[index] = str(translations.get(index, "")) + value
            else:
                entry[field] = str(entry.get(field, "")) + value
        else:
            raise ValueError(f"Unsupported PO line: {raw_line!r}")
    return messages


def compile_po(po_path: Path, mo_path: Path) -> None:
    messages = parse_po(po_path.read_text(encoding="utf-8"))
    pairs = sorted(
        (key.encode("utf-8"), value.encode("utf-8")) for key, value in messages.items()
    )
    count = len(pairs)
    originals = b""
    translations = b""
    original_table = []
    translation_table = []
    original_offset = 28 + (count * 16)

    for original, _translated in pairs:
        original_table.append((len(original), original_offset + len(originals)))
        originals += original + b"\x00"
    translation_offset = original_offset + len(originals)
    for _original, translated in pairs:
        translation_table.append(
            (len(translated), translation_offset + len(translations))
        )
        translations += translated + b"\x00"

    header = struct.pack(
        "<7I",
        0x950412DE,
        0,
        count,
        28,
        28 + count * 8,
        0,
        0,
    )
    tables = b"".join(struct.pack("<2I", *row) for row in original_table)
    tables += b"".join(struct.pack("<2I", *row) for row in translation_table)
    target = mo_path.with_suffix(mo_path.suffix + ".tmp")
    target.write_bytes(header + tables + originals + translations)
    target.replace(mo_path)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(
            "usage: scripts/compile_po.py locale/.../django.po [...]", file=sys.stderr
        )
        return 2
    for value in argv[1:]:
        po_path = Path(value)
        mo_path = po_path.with_suffix(".mo")
        compile_po(po_path, mo_path)
        print(f"compiled {po_path} -> {mo_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
