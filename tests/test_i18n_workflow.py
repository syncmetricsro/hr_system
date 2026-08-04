from __future__ import annotations

from pathlib import Path

import pytest

from core.ui.management.commands.safe_makemessages import Command
from scripts.compile_po import main as compile_main
from scripts.i18n_catalog import (
    LANGUAGES,
    MessageIdentity,
    catalog_changes,
    catalog_paths,
    load_catalog,
    parse_catalog,
    preserve_catalog_metadata,
    report_extraction,
    restore_catalogs,
    snapshot_catalogs,
    validate_catalogs,
)

REPO = Path(__file__).resolve().parent.parent


def _catalog(
    *entries: str,
    plural_count: int = 2,
) -> str:
    body = "\n\n".join(entries)
    return f"""msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\\n"
"Plural-Forms: nplurals={plural_count}; plural=(n != 1);\\n"

{body}
"""


def _write_catalogs(root: Path, source: str) -> None:
    for path in catalog_paths(root).values():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")


def test_parser_handles_wrapped_context_plural_fuzzy_and_obsolete_entries():
    catalog = parse_catalog(
        _catalog(
            '''msgctxt "menu"
msgid ""
"Open "
"record"
msgstr "Otvoriť záznam"''',
            '''msgid "One item"
msgid_plural "Many items"
msgstr[0] "Jedna položka"
msgstr[1] "Viac položiek"''',
            '''#, fuzzy
msgid "Unsafe guess"
msgstr "Nesprávny odhad"''',
            '''#~ msgid "Removed"
#~ msgstr "Odstránené"''',
        )
    )

    assert MessageIdentity("menu", "Open record") in catalog.active
    assert MessageIdentity("", "One item", "Many items") in catalog.active
    assert catalog.active[MessageIdentity("", "Unsafe guess")].fuzzy
    assert MessageIdentity("", "Removed") in catalog.obsolete
    assert "Unsafe guess" not in catalog.messages()
    assert "Removed" not in catalog.messages()


def test_renamed_message_is_new_and_old_translation_becomes_obsolete():
    before = parse_catalog(
        _catalog('''msgid "Trial failed"
msgstr "Skúšobný deň neúspešný"''')
    )
    after = parse_catalog(
        _catalog(
            '''msgid "Trial waived"
msgstr ""''',
            '''#~ msgid "Trial failed"
#~ msgstr "Skúšobný deň neúspešný"''',
        )
    )

    changes = catalog_changes(before, after)
    assert changes.added == {MessageIdentity("", "Trial waived")}
    assert changes.newly_obsolete == {MessageIdentity("", "Trial failed")}
    assert not after.active[MessageIdentity("", "Trial waived")].fuzzy
    assert (
        after.obsolete[MessageIdentity("", "Trial failed")].translations[0]
        == "Skúšobný deň neúspešný"
    )


def test_report_refuses_unapproved_obsolete_change_and_snapshot_restores(
    tmp_path, capsys
):
    locale_root = tmp_path / "locale"
    snapshot_root = tmp_path / "snapshot"
    before = _catalog('''msgid "Existing"
msgstr "Preklad"''')
    after = _catalog(
        '''#~ msgid "Existing"
#~ msgstr "Preklad"'''
    )
    _write_catalogs(locale_root, before)
    snapshot_catalogs(locale_root, snapshot_root)
    _write_catalogs(locale_root, after)

    assert report_extraction(snapshot_root, locale_root, accept_obsolete=False) == 1
    assert "rerun with --accept-obsolete" in capsys.readouterr().err

    restore_catalogs(snapshot_root, locale_root)
    assert all(
        path.read_text(encoding="utf-8") == before
        for path in catalog_paths(locale_root).values()
    )


def test_report_accepts_obsolete_history_and_rejects_fuzzy_active_entry(
    tmp_path, capsys
):
    before_root = tmp_path / "before"
    after_root = tmp_path / "after"
    _write_catalogs(
        before_root,
        _catalog('''msgid "Existing"
msgstr "Preklad"'''),
    )
    _write_catalogs(
        after_root,
        _catalog(
            '''#~ msgid "Existing"
#~ msgstr "Preklad"'''
        ),
    )
    assert report_extraction(before_root, after_root, accept_obsolete=True) == 0
    assert "Newly obsolete: 1" in capsys.readouterr().out

    _write_catalogs(
        after_root,
        _catalog(
            '''#, fuzzy
msgid "Renamed"
msgstr "Nesprávny odhad"'''
        ),
    )
    assert report_extraction(before_root, after_root, accept_obsolete=True) == 1
    assert "fuzzy active entry" in capsys.readouterr().err


def test_extraction_preserves_non_semantic_creation_timestamp(tmp_path):
    before_root = tmp_path / "before"
    after_root = tmp_path / "after"
    before = _catalog('''msgid "Existing"
msgstr "Preklad"''').replace(
        '"Content-Type:',
        '"POT-Creation-Date: 2026-08-01 12:00+0200\\n"\n"Content-Type:',
    )
    after = before.replace(
        "2026-08-01 12:00+0200",
        "2026-08-04 12:00+0200",
    )
    _write_catalogs(before_root, before)
    _write_catalogs(after_root, after)

    preserve_catalog_metadata(before_root, after_root)

    assert all(
        path.read_text(encoding="utf-8") == before
        for path in catalog_paths(after_root).values()
    )


def test_validation_rejects_incomplete_plural_and_language_divergence(tmp_path):
    _write_catalogs(
        tmp_path,
        _catalog(
            '''msgid "One item"
msgid_plural "Many items"
msgstr[0] "Jedna položka"
msgstr[1] ""'''
        ),
    )
    hu_path = catalog_paths(tmp_path)["hu"]
    hu_path.write_text(
        _catalog('''msgid "Different"
msgstr "Eltérő"'''),
        encoding="utf-8",
    )

    errors = validate_catalogs(catalog_paths(tmp_path), require_translated=True)
    assert any("untranslated active entry" in error for error in errors)
    assert any("missing active entry" in error for error in errors)
    assert any("extra active entry" in error for error in errors)


def test_compiler_rejects_invalid_catalogs_and_check_detects_stale_mo(tmp_path):
    valid = _catalog('''msgid "Open"
msgstr "Otvoriť"''')
    _write_catalogs(tmp_path, valid)
    po_paths = [str(path) for path in catalog_paths(tmp_path).values()]

    assert compile_main(["compile_po.py", *po_paths]) == 0
    assert compile_main(["compile_po.py", "--check", *po_paths]) == 0

    catalog_paths(tmp_path)["hu"].with_suffix(".mo").write_bytes(b"stale")
    assert compile_main(["compile_po.py", "--check", *po_paths]) == 1

    catalog_paths(tmp_path)["hu"].write_text(
        _catalog('''msgid "Open"
msgstr ""'''),
        encoding="utf-8",
    )
    assert compile_main(["compile_po.py", *po_paths]) == 1


def test_safe_extractor_disables_fuzzy_matching_and_ignores_tests():
    assert "--no-fuzzy-matching" in Command.msgmerge_options
    workflow = (REPO / "scripts/compile_messages.sh").read_text(encoding="utf-8")
    assert "safe_makemessages" in workflow
    assert "-i tests" in workflow


@pytest.mark.parametrize("language", LANGUAGES)
def test_compile_po_fixtures_are_not_real_catalog_messages(language):
    active = load_catalog(catalog_paths(REPO / "locale")[language]).active
    assert MessageIdentity("menu", "Open") not in active
    assert MessageIdentity("", "One item", "Many items") not in active
