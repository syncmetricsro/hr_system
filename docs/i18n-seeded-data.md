# Seeded data & i18n — how demo data stays localized (Platform)

Established 2026-07-11 (Stage C i18n sweeps). gettext translates **msgids in
code and templates — never database rows**. Seeded catalog data (checklist
items, blacklist categories, finance categories, inactive reasons, intake
questions, equipment names) therefore needs its own pattern, or demos show
English rows inside a translated UI.

## The pattern (three parts, all required)

1. **Seed the canonical English string.** Seeds/migrations store English
   labels — never a translation. English is the stable key; translations
   live in the catalogs where they belong.
2. **Render through `db_trans`.** The template filter
   (`core/ui/templatetags/nav.py`) runs the value through `gettext` at
   request time: known catalog strings localize into the viewer's language;
   **operator-entered free text falls through unchanged by design** (a size
   "43", a custom item name, a note — that's data, not UI).
   In Python (error messages, generated notes), call `gettext` on the label
   directly — see `features/checklists/services.missing_critical_labels`
   and `features/advances/hooks.py`.
3. **Register the msgids in a `catalog_i18n.py`.** makemessages only
   extracts marked strings from scanned files — and it must NOT come from
   the seed itself in two common cases: applied **migrations are never
   edited** (house rule), and `scripts/compile_messages.sh` **ignores
   `demo` paths**. So each app with seeded catalogs keeps a
   `catalog_i18n.py` of `gettext_noop(...)` entries, kept in sync with the
   seed by hand:

   | Registry | Covers |
   |---|---|
   | `core/people/catalog_i18n.py` | inactive reasons (migration 0003) |
   | `features/blacklist/catalog_i18n.py` | blacklist categories (migration 0002) |
   | `features/finance/catalog_i18n.py` | finance categories (`seed_finance`) |
   | `features/intake/catalog_i18n.py` | questionnaire panels + question labels |
   | `features/logistics/catalog_i18n.py` | seeded equipment names |
   | `clients/corvinum_eu/catalog_i18n.py` | corvinum checklist items + equipment |

## Adding new seeded catalog data — checklist

1. Seed the **English** string (idempotent `get_or_create` by label).
2. Add the same string to the app's `catalog_i18n.py` (create one if the
   app has none — copy any existing header).
3. Render sites: `{{ obj.label|db_trans }}` (load the `nav` tag library);
   Python messages: `gettext(label)`.
4. `scripts/compile_messages.sh --extract`, translate **SK/HU/UK** (check
   every msgmerge fuzzy — they pair wrong more often than right), compile.
5. Verify with `msgfmt --statistics` (regex greps false-positive on wrapped
   entries): all three catalogs must report zero untranslated/fuzzy.
6. Tests asserting label text run under the Slovak default locale — pin
   with `translation.override("en")` (see tests/test_checklists.py).
7. **Reseeding an existing demo DB**: seeds `get_or_create` by label, so a
   renamed label would duplicate rows — after changing seed labels, rebuild
   the stack DB (`scripts/dev_app.sh down && … up`, or
   `corvinum_app.sh down && up`), don't reseed in place.

## What is deliberately NOT translated

- Operator-entered rows (custom equipment, SMS template names/bodies,
  notes, person/project names) — they are data; `db_trans` passes them
  through.
- CSV **exports** keep canonical values (stable for spreadsheets/imports).
- Journal history and legal texts.

Native-speaker review of all AI-drafted translations (both products) remains
the standing human task before customer demos.
