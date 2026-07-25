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
- `gettext` (`msgfmt`/`msgmerge`, used by Django's `makemessages`/
  `compilemessages`) is **not installed in the runtime/test images** —
  `scripts/compile_messages.sh` apt-installs it inside the app image at
  run time, so always use that script rather than calling Django's
  management commands directly on the host.

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
2. Re-extract and compile:
   ```bash
   scripts/compile_messages.sh --extract
   ```
   This runs `makemessages` first (updates all three `.po` files with
   new/changed msgids from source — excluding `demo`, `test-artifacts`,
   `vendor`, `staticfiles`), then compiles.
3. **Check every new/changed msgid.** `makemessages`/`msgmerge` fuzzy-
   matches are wrong more often than right (e.g. it has paired "Reject"
   with "Projekt" before) — fix the `msgstr` and clear the `#, fuzzy` flag
   for anything it guessed at.
4. Translate the new msgid in **all three** catalogs (SK/HU/UK) before
   shipping — a missing translation just falls back to showing the raw
   English `msgid`.

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

- **Per-catalog completeness:**
  ```bash
  msgfmt --statistics locale/<lang>/LC_MESSAGES/django.po
  ```
  Reports translated/fuzzy/untranslated counts. Prefer this over grepping
  the raw `.po` — long/wrapped entries (`msgid ""` + continuation lines)
  make single-line regex checks unreliable.
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

- msgmerge fuzzy matches pair unrelated strings more often than not —
  always review, never trust-and-compile.
- Wrapped `.po` entries can't be patched with single-line regexes — edit
  the whole wrapped block.
- gettext isn't in the runtime/test images — don't try to run
  `makemessages`/`compilemessages` outside `scripts/compile_messages.sh`.
