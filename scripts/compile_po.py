#!/usr/bin/env python3
"""Compile GNU gettext PO catalogs to MO with the Python standard library.

The repository's runtime and test images intentionally omit the gettext OS
package.  This small compiler keeps catalog regeneration dependency-free and
does not extract or merge messages; the committed PO files remain the source
of truth.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

try:
    from scripts.i18n_catalog import load_catalog, parse_catalog, validate_catalogs
except ModuleNotFoundError:  # Direct execution adds scripts/, not the repo root.
    from i18n_catalog import load_catalog, parse_catalog, validate_catalogs


def parse_po(source: str) -> dict[str, str]:
    return parse_catalog(source).messages()


def mo_bytes(po_path: Path) -> bytes:
    messages = load_catalog(po_path).messages()
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
    return header + tables + originals + translations


def compile_po(po_path: Path, mo_path: Path) -> None:
    target = mo_path.with_suffix(mo_path.suffix + ".tmp")
    target.write_bytes(mo_bytes(po_path))
    target.replace(mo_path)


def main(argv: list[str]) -> int:
    arguments = argv[1:]
    check = bool(arguments and arguments[0] == "--check")
    if check:
        arguments = arguments[1:]
    if not arguments:
        print(
            "usage: scripts/compile_po.py [--check] locale/.../django.po [...]",
            file=sys.stderr,
        )
        return 2
    po_paths = [Path(value) for value in arguments]
    errors = validate_catalogs(
        {path.parent.parent.name: path for path in po_paths},
        require_translated=True,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    stale: list[Path] = []
    for po_path in po_paths:
        mo_path = po_path.with_suffix(".mo")
        if check:
            if not mo_path.exists() or mo_path.read_bytes() != mo_bytes(po_path):
                stale.append(mo_path)
        else:
            compile_po(po_path, mo_path)
            print(f"compiled {po_path} -> {mo_path}")
    if stale:
        for path in stale:
            print(f"ERROR: stale or missing MO catalog: {path}", file=sys.stderr)
        return 1
    if check:
        print(f"validated {len(po_paths)} PO/MO catalog pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
