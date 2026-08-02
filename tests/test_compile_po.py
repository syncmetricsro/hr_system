from __future__ import annotations

import gettext

from scripts.compile_po import compile_po, parse_po


def test_compile_po_supports_context_plurals_and_skips_fuzzy_entries(tmp_path):
    po_path = tmp_path / "messages.po"
    mo_path = tmp_path / "messages.mo"
    po_path.write_text(
        """msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"

msgctxt "menu"
msgid "Open"
msgstr "Otvoriť"

msgid "One item"
msgid_plural "Many items"
msgstr[0] "Jedna položka"
msgstr[1] "Viac položiek"

#, fuzzy
msgid "Discard me"
msgstr "Nepoužiť"
""",
        encoding="utf-8",
    )

    parsed = parse_po(po_path.read_text(encoding="utf-8"))
    assert "Discard me" not in parsed
    compile_po(po_path, mo_path)

    with mo_path.open("rb") as stream:
        catalog = gettext.GNUTranslations(stream)
    assert catalog.pgettext("menu", "Open") == "Otvoriť"
    assert catalog.ngettext("One item", "Many items", 1) == "Jedna položka"
    assert catalog.ngettext("One item", "Many items", 2) == "Viac položiek"
