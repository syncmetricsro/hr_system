# Pill system — worker status, certificate validity, nav attention badges

Status: **Fully implemented 2026-07-24** (§1/§3 landed first; §2's deferred
Phase 2, described below, landed the same day). All three pieces —
worker status pill, certificate-validity icons, and nav attention badges —
are live on both clients, both themes.

- §1: `{% status_pill person size="dot"/"label" %}`
  (`core/ui/templatetags/avatars.py`), a new `--info`/`--info-soft` CSS
  token pair (`static/src/css/app.css`, reusing the already dataviz-validated
  `--chart-office-1` blue rather than deriving a new one), and
  `.avatar-stack`/`.status-pill*` CSS. Wired into the worker list (dot) and
  person-detail header (labeled pill), both clients, both themes.
- §3: a new generic `register_nav_badge(slot, context)` / `nav_badge(request,
  slot)` registry slot (`core/ui/registry.py`) — deliberately generic, not
  compliance/reviews-specific, so features register their own count provider
  from `apps.py` rather than `core/ui/templatetags/nav.py` importing
  `features.*` directly (that would violate the feature→core dependency
  direction `scripts/check_dependency_direction.py` enforces). Compliance
  registers `compliance_badge` (`features/compliance/panels.py`), Logistics
  registers `reviews_badge` (`features/logistics/panels.py`). Both providers
  short-circuit for an unauthenticated/unauthorized viewer *before* touching
  the DB — a real bug caught by the existing unit suite: `layouts/base.html`
  renders the nav (and therefore the badge tag) even on the anonymous login
  page, which broke non-DB-marked tests until the guard was added, and would
  otherwise have run `compliance_alerts()` against `AnonymousUser` on every
  login-page render in production.
- Reuses the existing `.notification-count`/`-alert`/`-update` pill styling
  verbatim, plus one new `.notification-count-warning` variant (amber, for
  Reviews' always-warning tone and Compliance's non-severe case) — corner-
  positioned per client shell (`.folder-tab .notification-count` for Jober,
  `.sb-item .notification-count` for CorvinumEU's sidebar, including rail/
  icon-only mode).
- `avatar-design.md`, which this doc builds on, and §2's `Certificate.category`
  schema addition (landed via `certificate-upload-design.md`) are both
  implemented too — see those docs' own status lines.

## Phase 2: certificate-validity icons (§2) — implemented 2026-07-24

Built exactly as §2 designs it, plus a real architecture addition and a
real font-engineering detour neither was fully anticipated at design time:

- New generic `register_person_badges`/`person_badges` registry slot
  (`core/ui/registry.py`) — the list-row extension point that didn't exist
  before. Used identically by both surfaces (worker list, dot-sized icons
  via `core/people/views.py::people_list`; person-detail header, larger
  icons) via one new `{% person_badges person as badges %}` template tag
  (`core/ui/templatetags/avatars.py`), rather than two separate mechanisms.
- `features/compliance/panels.py::certificate_badges` groups a person's
  certificates by category, picks the most relevant row per category via
  new `features/compliance/services.py::most_relevant_certificate` (exactly
  §2's rule: soonest-expiring valid row, else most-expired), and tints by
  `_severity()` — same severity language as the status pill and compliance
  alerts.
- Five new category icons: Jober gets hand-drawn SVG symbols in
  `templates/partials/jober_nav_icons.html` (`cert-health`, `cert-forklift`,
  `cert-crane`, `cert-welding`, `cert-other`), matching the existing
  stroke-icon style. CorvinumEU needed real font engineering, not just a
  CSS mapping: its Material Symbols webfont is a hand-picked 44-glyph
  subset with no medical/forklift/welding-adjacent glyphs at all. Presented
  with "reuse an imperfect existing glyph" vs. "properly expand the font
  subset," the user chose the latter. New `scripts/subset_corvinum_icons.py`
  downloads the official variable font, pins it to the shipped "24pt
  Regular" instance, and — the real finding — prunes the GSUB ligature
  table at the Python data-structure level before subsetting, because a
  plain `fonttools subset --text=` pass keeps the *entire* same-first-letter
  ligature group once anything in it matches (subsetting for just
  "medical_services" alone pulled in 66 unrelated glyphs). Verified with a
  real headless-browser render of all 49 ligature names, not just a glyph
  count check. New icon mapping: `medical_services`, `forklift`,
  `construction`, `factory`, `badge` — `forklift` is a genuine exact-name
  match in Material Symbols; `construction`/`factory` are the closest
  available stand-ins for crane/welding (no dedicated icons exist for
  either), which is fine since every icon carries a tooltip naming the
  actual certificate.
- New `.badge-danger` CSS class (as this doc's open items listed) and
  `.cert-badges`/`.cert-badge-expired`/`.cert-badge-expiring` for the icon
  tint — no class needed for "valid"/no-expiry, which inherits the
  surrounding ink color.
- Demo data: `clients/jober/demo/management/commands/seed_demo_scenario.py`
  gained a second certificate (Mira Novakova, expired Health check) so the
  demo shows two different category icons in two different severity tints,
  not just one.
- `compliance_list.html`'s severity-label restyle with the new
  `.badge-danger` class, noted as optional in this doc's original open
  items, was left as-is — genuinely not required scope.

## Why this doc exists

Three related but distinct pieces of UI were requested, all under the
umbrella of "pills":

1. A colored **status pill** anchored to each worker's avatar.
2. Small **certificate-validity icons** next to a worker's avatar, one per
   certificate type they hold.
3. **Attention-count badges** on the "Megfelelőség" (Compliance) and
   "Ellenőrzések" (Reviews) nav tabs.

The good news: most of the *counting and severity logic* already exists —
`features/compliance/services.py::compliance_alerts()` and
`features/logistics/services.py::pending_deduction_reviews()` are already
computed today and already feed the notification bell
(`features/compliance/notifications.py`,
`features/logistics/notifications.py`, via
`core.notifications.registry.register_alert_provider`) and a dashboard tile
(`features/compliance/panels.py`). This feature is mostly new UI surface
wired to existing computations, plus one small schema addition.

**Explicitly out of scope, noted for awareness only:** uploading the actual
forklift/crane/welding certificate files. That's a real future feature. It
will reuse the avatar doc's storage decision (filesystem + Dokku volume +
image/PDF validation) for the certificate document itself, and it will reuse
the `Certificate.category` field this doc introduces (§2) as its type
vocabulary — so nothing here needs rework when that feature is built.

## 1. Worker status pill

Source: `Person.lifecycle_status` (`core/people/models.py`) — the existing
`LifecycleStatus` choices, unchanged:

| Value | Current label |
|---|---|
| `AVAILABLE` | Available |
| `TRIAL_DAY` | Trial day |
| `WORKING` | Working |
| `INACTIVE` | Inactive |
| `BLACKLISTED` | Blacklisted |

No new field — this is a visual reskin of a value already shown unguarded
today (`{{ person.get_lifecycle_status_display }}` in
`templates/pages/people_list.html`), so it carries no new RBAC concern: if a
viewer can already see the person, they can already see this status as
plain text.

**Color mapping:**

| Status | Treatment | Token |
|---|---|---|
| `WORKING` | success/green | `--success` / `--success-soft` (exist) |
| `TRIAL_DAY` | warning/amber | `--warning` / `--warning-soft` (exist) |
| `AVAILABLE` | info/blue | **new token needed** — no blue exists in `:root` today (only `--n*` grays, `--success`, `--warning`, `--danger`); add `--info` / `--info-soft` |
| `INACTIVE` | neutral/gray | `--n300`/`--n500` (exist) |
| `BLACKLISTED` | danger/red | `--danger` / `--danger-soft` (exist) |

**Placement:** overlapping the bottom edge of the avatar circle — the
familiar Slack/Teams presence-dot convention — not a separate text row.

**Sizing:**
- Worker-list thumbnail (~40px avatar): a plain colored dot, no text —
  there's no room for a legible label at that size.
- Person-detail avatar (~96px): a labeled pill (short text, e.g.
  "Working").
- The navbar avatar (an admin's own, per the avatar doc) never gets a
  status pill — lifecycle status is a `Person` concept, not a `User` one.

## 2. Certificate-validity icons

**Schema change (the one real migration in this feature):** add `category`
to `Certificate` (`features/compliance/models.py`), a `TextChoices` field:
`HEALTH` / `FORKLIFT` / `CRANE` / `WELDING` / `OTHER`, default `OTHER`.
Additive and backward-compatible — existing rows backfill to `OTHER`.

This is needed because `Certificate.name` today is free text
(`CharField(max_length=120)`, no fixed vocabulary) — "Forklift Licence" vs.
"Fork-lift cert" wouldn't reliably resolve to the same icon by keyword
matching. A real `category` field is the reliable option, and it happens to
be exactly the type vocabulary the deferred certificate-upload feature will
need too.

**Icon set:** extend the existing hand-rolled inline SVG sprite
(`templates/partials/jober_nav_icons.html`) with one symbol per category
plus a generic fallback for `OTHER` — consistent with how every other icon
in the app is built (no icon library, no raster assets). This is a
different visual subsystem from the avatar's illustrated-raster defaults —
these are small monochrome UI glyphs, not profile pictures.

**Validity tint:** reuse `features/compliance/services.py::_severity()`
(already ranks `expired` / `expiring` / valid) to tint each icon —
red/amber/green, same language as the status pill. Concretely this needs a
new `.badge-danger` CSS class (`static/src/css/app.css` already has
`--danger`/`--danger-soft` tokens — they're used by
`.notification-count-alert` — but no badge variant uses them yet; only
`.badge` (warning), `.badge-success` (green), and `.badge-neutral` (gray)
exist). Once `.badge-danger` exists, `templates/pages/compliance_list.html`'s
plain-text severity labels (`{% if a.severity == "expired" %}...`, currently
unstyled text) are a natural, low-risk place to adopt the same classes for
visual consistency — a nice-to-have alignment, not required scope for this
feature.

**Display rule:** only render an icon for a certificate the person actually
holds — no icon, and no "missing" placeholder, for categories they have no
record of. This matches the "in case they have one" framing from the
request; a "you're missing X" indicator is a different feature (arguably
what the Compliance alert list already does for medical records) and isn't
part of this pill.

**Placement:** a small icon row beside the avatar, on the same two surfaces
as the avatar itself — worker list row and person detail header. Each icon
carries a tooltip (existing `partials/tooltip.html` / `data-tooltip`
convention used throughout the nav) naming the certificate and its expiry
date — a bare icon row isn't self-explanatory on its own.

## 3. Nav attention-count badges

Confirmed via `locale/hu/LC_MESSAGES/django.po`:
- **"Megfelelőség" = Compliance tab** (`msgid "Compliance"` →
  `msgstr "Megfelelőség"`) — `compliance_list`, `features/compliance`.
- **"Ellenőrzések" = Reviews tab** (`msgid "Reviews"` →
  `msgstr "Ellenőrzések"`) — `equipment_reviews`, the equipment-deduction
  review queue in `features/logistics`. (Not audit, not blacklist — those
  are separate, unrelated msgids.)

Both tabs already exist in `templates/layouts/base.html`, and CorvinumEU
ships both too in its own copy
(`clients/corvinum_eu/templates/layouts/base.html`) — the badge needs to
land once, in a form both base templates render (a shared partial/template
tag), not duplicated per client.

**Count sourcing** — call the exact functions the notification providers
already call, directly, rather than going through the notification registry:

- Compliance: `len(compliance_alerts(request.user))`.
- Reviews: `len(pending_deduction_reviews()["issues"])`.

**Why not reuse `core.notifications.registry`:** that system's counts are
dismissal-filtered (`visible_items()` excludes anything the user dismissed
in the bell panel) and aggregate multiple providers into one total. The nav
badge needs one section's *true, undismissed* count — dismissing a bell
item declutters that transient feed, it doesn't mean the compliance/review
queue shrank, so the tab badge shouldn't imply that either. Calling the
underlying service functions directly sidesteps both problems and keeps a
single source of truth for the actual numbers (the providers and the badge
both ultimately call the same two functions).

**Severity/color:** mirrors what each provider already computes, so the tab
badge and the bell-panel item never disagree:
- Compliance badge: red if any `expired`/`missing` item exists in the
  result of `compliance_alerts()`, amber otherwise — same `severe` check
  `compliance_notification_provider` already does.
- Reviews badge: always amber/warning — `logistics_notification_provider`
  never escalates this to danger, so neither does the badge.

**Gating:** exactly matches how the tabs are already gated in the template
— `{% flag_on 'documents' %}` for Compliance, `{% can
'equipment.review_deduction' %}` + `{% flag_on 'equipment' %}` for Reviews —
so the badge only queries when the tab itself would render. No wasted
queries for roles or clients without that section.

**Visual:** reuse the existing `.notification-count` /
`.notification-count-alert` CSS pill verbatim (already red-on-white,
already used on the bell icon) rather than inventing new badge styling.
Needs one small addition: `.notification-count` is currently positioned for
the bell trigger button, not a nav tab, so a corner-positioning rule for
`.folder-tab .notification-count` (`position: absolute`, top-right corner)
is a small, scoped CSS addition.

## Open items for the implementation slice

- Add `--info` / `--info-soft` CSS custom properties for the `AVAILABLE`
  status pill (no blue token exists in `:root` today).
- Add `.badge-danger` CSS class using the already-existing
  `--danger`/`--danger-soft` tokens.
- `Certificate.category` migration, plus updating any seed data
  (`clients/*/demo/management/commands/seed_*`) that creates certificates
  with recognizable names (e.g. "Forklift training" in
  `clients/jober/demo/management/commands/seed_demo_scenario.py`) to set a
  matching category so the demo data actually exercises the new icons.
- Confirm whether `templates/pages/compliance_list.html`'s severity labels
  should be restyled with the new badge classes in the same slice, or left
  as a separate follow-up.
