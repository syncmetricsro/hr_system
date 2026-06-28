# ADR 0017: English base language, Slovak default, compiled SK/HU/UK catalogs

Status: Accepted
Date: 2026-06-23

Supersedes the Phase 0 i18n stance (Slovak-authored source strings, catalogs
deferred — see the earlier "conservative Slovak shell labels" note in
`docs/product/open-decisions.md` and the catalog-deferral in the build journals).

## Context

Phase 0/1 authored all UI strings directly in **Slovak** as the gettext source
(`msgid`), with no compiled catalogs — so non-Slovak languages fell back to
Slovak. The product owner asked to (a) actually ship translations and (b) make
**English the default/base language** of the codebase. With Django i18n the
source string *is* the base-language text, so an English base means the source
`msgid`s must be English.

The end users are mixed (Ukrainian workers; Slovak/Hungarian operators), so the
*visible* default should stay Slovak even though the code base language is
English.

## Decision

- **Source strings are English.** All `{% trans %}` / `gettext_lazy` `msgid`s
  were rewritten to English; CLI/exception/dev messages were switched to plain
  English too.
- **`LANGUAGE_CODE = "sk"`** — visitors still default to Slovak; English is the
  base/fallback returned when a catalog has no entry.
- **Offered languages:** `en`, `sk`, `hu`, `uk` (English added to the switcher).
- **Catalogs:** `sk`, `hu`, `uk` shipped as `locale/<lang>/LC_MESSAGES/django.po`
  (source of truth, committed) compiled to `django.mo` (committed). `en` needs no
  catalog (it is the source). The Slovak catalog reproduces the previous Slovak
  source text exactly, so the default rendering — and existing tests — are
  unchanged.
- **Tooling:** gettext (`xgettext`/`msgfmt`) is not in the runtime/test images
  (and the runtime must stay minimal), so extraction/compilation runs the app
  image with gettext apt-installed at run time, via `scripts/compile_messages.sh`.
  The runtime image just `COPY`s the committed `locale/` (no gettext at runtime).

## Consequences

- The app is fully multilingual immediately (SK default, EN/HU/UK selectable).
- `.mo` files are committed (derived from reviewed `.po`); `scripts/compile_messages.sh`
  regenerates them. Keep `.po` and `.mo` in sync in the same commit.
- The HU/UK (and revised SK) translations are **AI-authored and need a
  fluent-speaker review** before client-facing use — tracked in the production
  readiness journal.
- Adding a language later: add it to `LANGUAGES`, run
  `scripts/compile_messages.sh --extract`, translate the new `.po`, recompile.
