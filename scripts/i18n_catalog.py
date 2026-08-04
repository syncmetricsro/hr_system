#!/usr/bin/env python3
"""Inspect and compare GNU gettext PO catalogs without third-party packages."""

from __future__ import annotations

import argparse
import ast
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

LANGUAGES = ("sk", "hu", "uk")
DOMAIN = "django"
_NPLURALS_RE = re.compile(r"(?:^|\n)Plural-Forms:\s*nplurals=(\d+);")


def _unquote(value: str) -> str:
    parsed = ast.literal_eval(value)
    if not isinstance(parsed, str):
        raise ValueError(f"Expected a PO string, got {value!r}")
    return parsed


@dataclass(frozen=True, order=True)
class MessageIdentity:
    context: str = ""
    msgid: str = ""
    plural: str = ""

    @property
    def gettext_key(self) -> str:
        key = self.msgid
        if self.context:
            key = f"{self.context}\x04{key}"
        if self.plural:
            key = f"{key}\x00{self.plural}"
        return key

    @property
    def display(self) -> str:
        value = repr(self.msgid)
        if self.context:
            value = f"context={self.context!r} {value}"
        if self.plural:
            value = f"{value} / {self.plural!r}"
        return value


@dataclass
class CatalogEntry:
    identity: MessageIdentity
    translations: dict[int, str] = field(default_factory=dict)
    flags: frozenset[str] = frozenset()
    references: tuple[str, ...] = ()
    obsolete: bool = False

    @property
    def fuzzy(self) -> bool:
        return "fuzzy" in self.flags

    def translated(self, nplurals: int) -> bool:
        if self.identity.msgid == "":
            return bool(self.translations.get(0, ""))
        if self.identity.plural:
            return all(self.translations.get(index, "") for index in range(nplurals))
        return bool(self.translations.get(0, ""))


@dataclass
class Catalog:
    entries: list[CatalogEntry]

    @property
    def header(self) -> CatalogEntry:
        for entry in self.entries:
            if not entry.obsolete and entry.identity.msgid == "":
                return entry
        raise ValueError("PO catalog has no active header entry")

    @property
    def nplurals(self) -> int:
        match = _NPLURALS_RE.search(self.header.translations.get(0, ""))
        if not match:
            raise ValueError("PO header has no valid Plural-Forms nplurals value")
        return int(match.group(1))

    @property
    def active(self) -> dict[MessageIdentity, CatalogEntry]:
        return {
            entry.identity: entry
            for entry in self.entries
            if not entry.obsolete and entry.identity.msgid != ""
        }

    @property
    def obsolete(self) -> dict[MessageIdentity, CatalogEntry]:
        return {
            entry.identity: entry
            for entry in self.entries
            if entry.obsolete and entry.identity.msgid != ""
        }

    def messages(self) -> dict[str, str]:
        messages: dict[str, str] = {}
        nplurals = self.nplurals
        for entry in self.entries:
            if entry.obsolete or entry.fuzzy or not entry.translated(nplurals):
                continue
            if entry.identity.plural:
                translated = "\x00".join(
                    entry.translations[index] for index in range(nplurals)
                )
            else:
                translated = entry.translations.get(0, "")
            messages[entry.identity.gettext_key] = translated
        return messages


def _parse_block(lines: list[str]) -> CatalogEntry | None:
    values: dict[str, str] = {}
    translations: dict[int, str] = {}
    flags: set[str] = set()
    references: list[str] = []
    active_field: tuple[str, int | None] | None = None
    obsolete = False

    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("#~"):
            obsolete = True
            line = line[2:].lstrip()
        if not line:
            continue
        if line.startswith("#,"):
            flags.update(value.strip() for value in line[2:].split(","))
            continue
        if line.startswith("#:"):
            references.extend(line[2:].strip().split())
            continue
        if line.startswith("#"):
            continue
        if line.startswith("msgctxt "):
            values["msgctxt"] = _unquote(line[8:].strip())
            active_field = ("msgctxt", None)
        elif line.startswith("msgid_plural "):
            values["msgid_plural"] = _unquote(line[13:].strip())
            active_field = ("msgid_plural", None)
        elif line.startswith("msgid "):
            values["msgid"] = _unquote(line[6:].strip())
            active_field = ("msgid", None)
        elif line.startswith("msgstr["):
            index_text, value = line[7:].split("]", 1)
            index = int(index_text)
            translations[index] = _unquote(value.strip())
            active_field = ("msgstr", index)
        elif line.startswith("msgstr "):
            translations[0] = _unquote(line[7:].strip())
            active_field = ("msgstr", 0)
        elif line.startswith('"') and active_field is not None:
            value = _unquote(line)
            field_name, index = active_field
            if field_name == "msgstr":
                assert index is not None
                translations[index] = translations.get(index, "") + value
            else:
                values[field_name] = values.get(field_name, "") + value
        else:
            raise ValueError(f"Unsupported PO line: {raw_line!r}")

    if "msgid" not in values:
        return None
    return CatalogEntry(
        identity=MessageIdentity(
            context=values.get("msgctxt", ""),
            msgid=values["msgid"],
            plural=values.get("msgid_plural", ""),
        ),
        translations=translations,
        flags=frozenset(flags),
        references=tuple(references),
        obsolete=obsolete,
    )


def parse_catalog(source: str) -> Catalog:
    entries: list[CatalogEntry] = []
    block: list[str] = []
    for line in [*source.splitlines(), ""]:
        if line.strip():
            block.append(line)
            continue
        if block:
            entry = _parse_block(block)
            if entry is not None:
                entries.append(entry)
            block = []
    return Catalog(entries)


def load_catalog(path: Path) -> Catalog:
    return parse_catalog(path.read_text(encoding="utf-8"))


def catalog_paths(root: Path) -> dict[str, Path]:
    return {
        language: root / language / "LC_MESSAGES" / f"{DOMAIN}.po"
        for language in LANGUAGES
    }


def validate_catalogs(paths: dict[str, Path], *, require_translated: bool) -> list[str]:
    errors: list[str] = []
    catalogs: dict[str, Catalog] = {}
    for language, path in paths.items():
        try:
            catalog = load_catalog(path)
            nplurals = catalog.nplurals
        except (OSError, ValueError, SyntaxError) as exc:
            errors.append(f"{language}: cannot read {path}: {exc}")
            continue
        catalogs[language] = catalog
        for identity, entry in sorted(catalog.active.items()):
            if entry.fuzzy:
                errors.append(f"{language}: fuzzy active entry: {identity.display}")
            if require_translated and not entry.translated(nplurals):
                errors.append(
                    f"{language}: untranslated active entry: {identity.display}"
                )

    if catalogs:
        first_language = next(iter(catalogs))
        expected = set(catalogs[first_language].active)
        for language, catalog in catalogs.items():
            actual = set(catalog.active)
            for identity in sorted(expected - actual):
                errors.append(
                    f"{language}: missing active entry present in {first_language}: "
                    f"{identity.display}"
                )
            for identity in sorted(actual - expected):
                errors.append(
                    f"{language}: extra active entry absent from {first_language}: "
                    f"{identity.display}"
                )
    return errors


@dataclass(frozen=True)
class CatalogChanges:
    added: frozenset[MessageIdentity]
    newly_obsolete: frozenset[MessageIdentity]
    revived: frozenset[MessageIdentity]


def catalog_changes(before: Catalog, after: Catalog) -> CatalogChanges:
    before_active = set(before.active)
    after_active = set(after.active)
    return CatalogChanges(
        added=frozenset(after_active - before_active),
        newly_obsolete=frozenset(before_active - after_active),
        revived=frozenset(set(before.obsolete) & after_active),
    )


def _print_identities(label: str, identities: Iterable[MessageIdentity]) -> None:
    values = sorted(identities)
    print(f"{label}: {len(values)}")
    for identity in values:
        print(f"  - {identity.display}")


def report_extraction(
    before_root: Path, after_root: Path, *, accept_obsolete: bool
) -> int:
    before_paths = catalog_paths(before_root)
    after_paths = catalog_paths(after_root)
    errors = validate_catalogs(after_paths, require_translated=False)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    changes_by_language: dict[str, CatalogChanges] = {}
    for language in LANGUAGES:
        before = load_catalog(before_paths[language])
        after = load_catalog(after_paths[language])
        changes_by_language[language] = catalog_changes(before, after)
        translated = sum(
            entry.translated(after.nplurals) for entry in after.active.values()
        )
        fuzzy = sum(entry.fuzzy for entry in after.active.values())
        print(
            f"{language}: active={len(after.active)}, translated={translated}, "
            f"fuzzy={fuzzy}, obsolete={len(after.obsolete)}"
        )

    baseline = changes_by_language[LANGUAGES[0]]
    for language, changes in changes_by_language.items():
        if changes.added != baseline.added:
            print(
                f"ERROR: {language}: added active set differs from sk", file=sys.stderr
            )
            return 1
        if changes.newly_obsolete != baseline.newly_obsolete:
            print(
                f"ERROR: {language}: newly obsolete set differs from sk",
                file=sys.stderr,
            )
            return 1
        if changes.revived != baseline.revived:
            print(f"ERROR: {language}: revived set differs from sk", file=sys.stderr)
            return 1

    _print_identities("Added active", baseline.added)
    _print_identities("Newly obsolete", baseline.newly_obsolete)
    _print_identities("Revived", baseline.revived)

    if baseline.newly_obsolete and not accept_obsolete:
        print(
            "ERROR: extraction would make active messages obsolete. "
            "Review the list, then rerun with --accept-obsolete.",
            file=sys.stderr,
        )
        return 1
    return 0


def snapshot_catalogs(source_root: Path, snapshot_root: Path) -> None:
    for language, source in catalog_paths(source_root).items():
        destination = catalog_paths(snapshot_root)[language]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def restore_catalogs(snapshot_root: Path, destination_root: Path) -> None:
    for language, source in catalog_paths(snapshot_root).items():
        destination = catalog_paths(destination_root)[language]
        shutil.copy2(source, destination)


def preserve_catalog_metadata(source_root: Path, destination_root: Path) -> None:
    """Keep non-semantic creation timestamps from making extraction non-idempotent."""
    for language, source_path in catalog_paths(source_root).items():
        destination_path = catalog_paths(destination_root)[language]
        source = source_path.read_text(encoding="utf-8")
        destination = destination_path.read_text(encoding="utf-8")
        prefix = '"POT-Creation-Date:'
        source_line = next(
            (line for line in source.splitlines() if line.startswith(prefix)),
            None,
        )
        destination_line = next(
            (line for line in destination.splitlines() if line.startswith(prefix)),
            None,
        )
        if source_line is None or destination_line is None:
            raise ValueError(
                f"{language}: cannot preserve missing POT-Creation-Date header"
            )
        destination_path.write_text(
            destination.replace(destination_line, source_line, 1),
            encoding="utf-8",
        )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate")
    validate.add_argument("--allow-untranslated", action="store_true")
    validate.add_argument("root", type=Path)

    report = subparsers.add_parser("report")
    report.add_argument("--before", type=Path, required=True)
    report.add_argument("--after", type=Path, required=True)
    report.add_argument("--accept-obsolete", action="store_true")

    snapshot = subparsers.add_parser("snapshot")
    snapshot.add_argument("--source", type=Path, required=True)
    snapshot.add_argument("--destination", type=Path, required=True)

    restore = subparsers.add_parser("restore")
    restore.add_argument("--source", type=Path, required=True)
    restore.add_argument("--destination", type=Path, required=True)

    preserve = subparsers.add_parser("preserve-metadata")
    preserve.add_argument("--source", type=Path, required=True)
    preserve.add_argument("--destination", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "validate":
        errors = validate_catalogs(
            catalog_paths(args.root), require_translated=not args.allow_untranslated
        )
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return int(bool(errors))
    if args.command == "report":
        return report_extraction(
            args.before, args.after, accept_obsolete=args.accept_obsolete
        )
    if args.command == "snapshot":
        snapshot_catalogs(args.source, args.destination)
        return 0
    if args.command == "restore":
        restore_catalogs(args.source, args.destination)
        return 0
    if args.command == "preserve-metadata":
        preserve_catalog_metadata(args.source, args.destination)
        return 0
    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
