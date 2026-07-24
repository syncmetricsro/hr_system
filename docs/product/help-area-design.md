# In-app Help area

Status: **Implemented 2026-07-24** — the full 8-module set plus Getting
Started, fully translated in SK/HU/UK, exactly as designed below.

- New `core/ui/help.py` (article registry: slug, title, group — no
  database model, matching the "hand-authored templates" decision) and
  `core/ui/views.py::help_index`/`help_article`, mounted unconditionally
  (`config/urls.py`, no `Action`/`flag_on` gate) at `help/` and
  `help/<slug>/`.
- New nav tab in both shells, right after Reports as recommended — a new
  `nav-icon-help` SVG symbol for Jober, and CorvinumEU reuses its
  already-subsetted `info` Material Symbol rather than triggering another
  font-subset regeneration (docs/product/pill-system-design.md §2) for a
  single icon.
- `templates/help/_base.html` is a shared wrapper (title/heading blocks +
  a back-to-index link) that each of the 9 article templates extends,
  rather than repeating the page-head boilerplate 9 times.
- Translation was done as one combined authoring+translation pass, not
  sequential phases, per this doc's own guidance. 72 new msgids (39 short
  titles/headings + 33 paragraphs) translated into SK/HU/UK by hand, not
  machine-translated. The extraction step's `msgmerge` fuzzy-matched
  several of them against unrelated existing strings (e.g. "Getting
  started" → the Slovak translation of a pre-existing, unrelated "started"
  msgid) — caught and fixed per the CLAUDE.md fuzzy-match caution rather
  than accepted blind, using `polib` (installed transiently, not an app
  dependency) to apply the reviewed translations and clear the fuzzy flags
  precisely rather than hand-editing ~250 `.po` entries across 3 files.

## Known follow-up, not fixed in this slice

Every article is visible to every client regardless of that client's
feature flags — CorvinumEU sees the "Feedback: links, QR codes, and
submissions" article even though CorvinumEU has `feedback: False` and no
Feedback tab at all. The content itself is accurate (it describes how
Jober's feedback feature works); it's just not relevant to a CorvinumEU
reader. This doc didn't originally scope per-client article filtering, and
building it now — mapping each article to a required feature flag, hiding
it from the index, and 404ing the slug when unsupported — is a real,
separable follow-up, not a bug in what shipped.

## Why this doc exists

Jober's people-ops web app has no built-in guidance beyond
`docs/product/contextual-tooltips.md`'s in-context hover/focus tooltips —
useful for "what does this button do," not for "how do I complete this
workflow end to end." This doc plans a dedicated Help section: a real,
navigable set of documentation pages inside the app itself.

Decisions confirmed with the user:
- **Hand-authored Django templates, not Markdown.** No Markdown-rendering
  library (`markdown`/`mistune`) exists as a dependency today, and adding
  one would need its own ADR under AGENTS.md §3.1 ("Approval gate. New
  PyPI package → ADR... No silent `uv add`"). Writing help content as
  ordinary Django templates avoids that entirely and reuses the existing
  template/i18n system directly — more manual to author than Markdown,
  but zero approval-gate friction.
- **Fully translated SK/HU/UK from day one**, matching how the rest of
  the UI already works. Flagged explicitly: this is a real, sizable
  translation commitment. The existing `.po` catalogs
  (`locale/{sk,hu,uk}/LC_MESSAGES/django.po`) are already ~4800-4900
  lines each of short UI labels — help *prose* (multi-sentence
  explanations, step-by-step instructions) is a different scale and
  character of content to translate than a button label, and should be
  budgeted for accordingly, not treated as "a few more msgids."

## Design

### 1. Navigation

A new, **always-visible** "Help" nav tab in both shells —
`templates/layouts/base.html` (Jober's folder-tabs) and
`clients/corvinum_eu/templates/layouts/base.html` (Corvinum's sidebar) —
unconditional like People/Projects/Reports, **not** gated by an `Action`
or `flag_on` check. Every existing nav tab besides those three is
permission/feature-gated; Help is deliberately the exception, since every
role needs documentation regardless of what else they can see. Suggested
placement: right after Reports, before Audit — keeps it visually grouped
with the other always-present, non-operational tabs.

### 2. Content structure

- New `templates/help/` directory, one template per article, keyed by a
  slug (e.g. `templates/help/people-intake.html`,
  `templates/help/finance-recording-a-month.html`).
- A single `help_article(request, slug)` view resolves a slug to its
  template (404 on an unknown slug) — simple and extensible; no database
  model needed for content itself, since it's hand-authored, not
  user-editable.
- A `help_index` landing page groups articles by module, mirroring the
  nav's own organization: People, Projects, Compliance, Logistics
  (accommodation/equipment/transport), Finance, Feedback, Blacklist,
  Audit — plus a "Getting started" article that isn't tied to one module.
- No RBAC gating on reading — every authenticated role can read every
  article (some articles may only be *relevant* to certain roles, e.g. a
  Manager-only workflow, but nothing about reading documentation should
  be permission-restricted; the article's own text can simply note which
  role a described action requires, consistent with how the rest of the
  app already surfaces role-gated actions).

### 3. i18n

Every string goes through the existing `{% trans %}`/`{% blocktrans %}`
mechanism — no new i18n infrastructure. New msgids get picked up by the
standard `scripts/compile_messages.sh --extract` workflow already used
for everything else, with the same `msgmerge` fuzzy-match caution
CLAUDE.md already documents (fuzzy matches pair unrelated strings and
need manual correction, not blind acceptance). Given the confirmed
decision to translate fully from day one, plan the initial content
authoring and its SK/HU/UK translation as one combined piece of work, not
sequential phases — a partially-translated Help section would be worse
than not having one, since a user landing on an untranslated article mid-
read is a worse experience than a small, clearly-scoped section that's
complete in every language.

### 4. Initial content scope (a starting set, not exhaustive)

- Getting started / navigating the app
- People: intake, lifecycle statuses, trial scheduling, activation
- Projects: assignments, readiness pillars
- Compliance: certificates, expiry alerts (cross-reference the pill/
  certificate-upload designs once those exist)
- Logistics: accommodation, equipment issue/return, transport
- Finance: recording a month, locking/reopening, reading the reports
- Feedback: creating a link, reviewing submissions
- Blacklist: what it is, how a case is proposed/decided
- Audit: what's logged and why

## Explicitly deferred (not part of the first version)

- Full-text search across articles.
- Screenshot or video embeds (would need an asset-storage decision,
  echoing the same considerations as `docs/product/avatar-design.md`'s
  storage design).
- Per-app-release content versioning (i.e., "this article describes the
  July 2026 UI") — start with content that's kept current by hand, revisit
  if drift becomes a real problem.

## Open items for the implementation slice

- Confirm exact initial article list and who owns writing the source
  (English) content before translation begins.
- Confirm nav placement precisely (this doc recommends after Reports,
  before Audit) with a look at the rendered nav on both narrow/mobile and
  wide layouts, since Help added to an already-long tab list may need the
  same responsive treatment already applied elsewhere.
