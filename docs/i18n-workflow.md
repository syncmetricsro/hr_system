# i18n workflow — editing, compiling, and retrieving translations (Platform)

How to hand-edit translation catalogs, compile them, add new translatable
strings, and check translation state. For how *seeded database data*
(checklist items, blacklist categories, finance categories, inactive
reasons, intake questions, equipment names) stays localized, see
`i18n-seeded-data.md` — that's a separate pattern from the one below and
this doc doesn't repeat it.

## Overview

- Source strings in code/templates are authored in **English** (the base/
  fallback language); the active default shown to visitors is **Slovak**
  (`config/settings/base.py:110-119`).
- Three shipped catalogs: `sk`, `hu`, `uk` (`LANGUAGES` in the same
  settings block). There is no `locale/en` — English is the literal
  `msgid` text, not a translated catalog.
- Each catalog lives at `locale/<lang>/LC_MESSAGES/django.{po,mo}`
  (`LOCALE_PATHS = [BASE_DIR / "locale"]`):
  - **`.po`** — human-readable source of truth, hand-edited, committed.
  - **`.mo`** — compiled binary the running app actually loads. Editing
    `.po` alone does nothing until you recompile.
- GNU gettext is **not installed in the runtime/test images**. Extraction
  temporarily installs it inside the app image; validation and deterministic
  MO compilation use the repository's standard-library tooling. Always use
  `scripts/compile_messages.sh` rather than calling Django's management
  commands directly.

## Editing an existing translation

1. Open the relevant `locale/<lang>/LC_MESSAGES/django.po` and find the
   `msgid` block (search for the English source string).
2. Edit the `msgstr` line.
3. Check for a `#, fuzzy` flag on that entry (it can sit 1-3 lines above
   the `msgid`, sometimes with `#|` previous-value lines in between) — if
   present, remove it once you've confirmed the translation is correct.
   A leftover fuzzy flag marks the entry as needing review.
4. Compile:
   ```bash
   scripts/compile_messages.sh
   ```
   No `--extract` needed — you didn't change which strings need
   translation, only the value of an existing one.

## Adding a new translatable string

1. Mark the string in source: `{% translate "..." %}` / `{% blocktranslate %}`
   in templates, `gettext(...)` / `gettext_lazy(...)` in Python.
2. Re-extract without compiling:
   ```bash
   scripts/compile_messages.sh --extract
   ```
   This updates all three `.po` files from runtime source while excluding
   `tests`, `demo`, `test-artifacts`, `vendor`, and `staticfiles`. It
   disables msgmerge fuzzy matching, prints semantic active/obsolete/addition
   counts, and deliberately does not compile.
3. If extraction would make an active message obsolete, it lists every
   affected msgid, restores all three catalogs byte-for-byte, and fails.
   Confirm the source really was removed, then rerun explicitly:
   ```bash
   scripts/compile_messages.sh --extract --accept-obsolete
   ```
   Approved removed translations stay in the PO files as recoverable `#~`
   history; they are not active and therefore do not enter the MO files.
4. Translate every added msgid in **all three** catalogs (SK/HU/UK) before
   shipping — a missing translation just falls back to showing the raw
   English `msgid`.
5. Validate and compile:
   ```bash
   scripts/compile_messages.sh
   ```
   Compilation fails on an active fuzzy or untranslated entry, an incomplete
   plural, or different active msgid sets between the three languages.
6. Confirm the committed binaries match the reviewed PO sources:
   ```bash
   scripts/compile_messages.sh --check
   ```
   This is read-only and fails on a missing or stale MO file.

## Seeded / database catalog data

Checklist items, blacklist categories, finance categories, inactive
reasons, intake questions, and seeded equipment names are **not** template/
code msgids — they're rows in the database rendered through a `db_trans`
filter, with their translatable strings registered separately in each
app's `catalog_i18n.py`. Full pattern, the list of existing registries, and
the add-new-seeded-string checklist: **`docs/i18n-seeded-data.md`**.

## Audit log: `action` is translated, `reason` is partially translated

The audit log (`core/audit/`) has two text fields that are easy to
conflate but need different treatment:

- **`action`** (e.g. `"finance.locked"`) is a closed, fixed set of
  machine codes — fully translated via `AUDIT_ACTION_LABELS` in
  `core/audit/presentation.py`, which maps every known code to a
  `gettext_lazy()` string. No further work needed here.
- **`reason`** (`core/audit/models.py`, a free `TextField`) is **mostly**
  free text — user-typed (archive/exit/reopen-month/blacklist-removal
  reasons, typed into a plain `<input>`) or programmatically-interpolated
  data strings (amounts, periods) — but a handful of call sites pass one
  of a small set of **fixed English literals** as a default reason (e.g.
  `reason or "activation"`, `reason="superseded"`). Those are genuinely a
  closed vocabulary, so as of 2026-07-25 they're translated the same way
  `action` is: `AUDIT_REASON_LABELS` + `audit_reason_label()` in
  `core/audit/presentation.py` map each known literal to a
  `gettext_lazy()` string; anything not in that dict (the actual free
  text) passes through unchanged. `core/audit/views.py`'s `audit_log`
  view resolves `event.reason_label` per row (mirroring
  `event.action_label`), and `templates/pages/audit_log.html` renders
  `reason_label`, not the raw `reason`. When adding a new fixed-literal
  `reason=` default anywhere in the codebase, add its English text to
  `AUDIT_REASON_LABELS` and translate it in all three catalogs — the same
  checklist as any other new msgid, above.

## Retrieving / verifying translation state

- **Whole-catalog completeness and MO synchronization:**
  ```bash
  scripts/compile_messages.sh --check
  ```
  The committed parser understands wrapped messages, contexts, plurals,
  fuzzy flags, and obsolete entries. Do not count `msgid` or `msgstr` lines:
  wrapped blocks make line-oriented counts incorrect.
- **Extraction report:** `--extract` prints active, translated, fuzzy,
  obsolete, added, newly-obsolete and revived counts. An obsolete entry is
  retained translation history, not an active UI string and not a deleted PO
  block.
- **Viewing a specific language at runtime:** URLs are language-prefixed —
  `/sk/`, `/hu/`, `/uk/` (an unprefixed root request redirects to the
  Slovak default, `/sk/`).

## Testing

Tests run under the Slovak default locale. Assertions on translated string
content need to pin the language explicitly:

```python
from django.utils import translation
with translation.override("en"):
    ...
```

See `tests/test_i18n.py` (language-prefix routing) and
`tests/test_i18n_catalog.py` / `tests/test_checklists.py` (label-text
assertions) for the pattern in use.

## Gotchas

- Raw msgmerge fuzzy matching has paired unrelated strings such as "trial
  waived" and "Trial failed". The committed extractor disables fuzzy matching;
  never replace it with a direct `makemessages` invocation.
- Test fixtures are not product UI and are excluded from extraction. Runtime
  code or a `catalog_i18n.py` registry must own every shipped msgid.
- Wrapped `.po` entries can't be patched with single-line regexes — edit
  the whole wrapped block.
- gettext isn't in the runtime/test images — don't try to run extraction
  outside `scripts/compile_messages.sh`.
