# In-app Help area

Status: **implemented on the Help release branch, 2026-08-01; staging release
pending review and green CI**.

The Help area is shared platform code with client-specific availability and
imagery. Every authenticated role can read it. Feature flags determine which
articles exist for the running thin client; an unsupported article is absent
from the index and returns 404 when addressed directly.

## Article set

Each client exposes exactly 12 focused workflow cards:

| Article | Jober | CorvinumEU |
|---|:---:|:---:|
| Getting started | yes | yes |
| People and intake | yes | yes |
| Projects and assignments | yes | yes |
| Trials, readiness and activation | yes | yes |
| Certificates and compliance | yes | yes |
| Equipment | yes | yes |
| Accommodation | yes | — |
| Reports and staff activity | yes | yes |
| Finance | yes | — |
| Feedback | yes | — |
| Ledger | — | yes |
| Payslips | — | yes |
| Gross wages | — | yes |
| Blacklist | yes | yes |
| Audit | yes | yes |

Existing article URLs are retained where their topic still exists. The former
`/help/logistics/` route is an unlisted permanent redirect to
`/help/equipment/`; Logistics is not an index card.

## Architecture and gating

`core/ui/help.py` is the single code-backed registry. It contains translated
titles, summaries, purpose text, role notes, workflow steps, boundaries,
semantic icon concepts, related topics, route coverage, and screenshot
metadata. No database model or content-management dependency is involved.

The registry remains client-neutral:

- ordinary module feature flags decide article availability;
- conditional steps use feature flags such as `checklists` and
  `equipment_returns`, or the generic `EQUIPMENT_STOCK_LEDGER_ENABLED`
  setting;
- `HELP_ASSET_NAMESPACE` selects `jober` or `corvinum` imagery and must be a
  safe path component;
- `core/` never compares a client name or imports a client package.

Help is feature-gated, never role-gated. An article can explain a Manager-only
action to a Recruiter or Observer, while the real action continues to enforce
server-side authorization.

## Index and article presentation

The dashboard Help index groups fully clickable cards into Start here,
Workforce workflows, Safety and resources, and Reporting and pay. Every card
has a client-themed semantic icon, a 16:9 screenshot thumbnail, title, concise
summary, visible keyboard focus, and a touch target larger than 44 pixels.
Images are lazy-loaded; the grid is three columns on wide screens and one
column on mobile.

All articles use `templates/help/article.html` and the same text-first
instructional structure:

1. purpose;
2. an anchor-linked On this page list;
3. roles and permissions;
4. numbered workflow steps;
5. an important operational, privacy, or security boundary;
6. a client-specific screenshot with translated HTML callouts;
7. related topics filtered to articles available for that client.

Getting started uses a real fictional client shell rather than a hand-built
mock. Equipment prose follows the enabled stock-ledger or return workflow, so
Jober describes receipts and stock reconciliation while CorvinumEU describes
returns. Readiness and financial guidance follow the same capability-aware
rule.

Icons extend only the vocabularies already shipped: Jober SVG sprite symbols
and Corvinum Material ligatures. The Material subset is not regenerated.

## Screenshot assets

The committed files live under:

```text
static/help/screens/jober/<slug>.webp
static/help/screens/jober/<slug>-thumb.webp
static/help/screens/corvinum/<slug>.webp
static/help/screens/corvinum/<slug>-thumb.webp
```

There are 24 primary images and 24 thumbnails. Primary images are 1280×720;
thumbnails are 640×360. They are cropped from 1440×900 browser captures and
converted by the already-pinned Pillow dependency. Conversion removes EXIF
and writes WebP without retaining a second source format.

Only the committed Playwright capture workflow may refresh these assets.
Jober is captured in Slovak and CorvinumEU in Hungarian using seeded fictional
records. Numbered annotations are translated HTML overlays, not pixels baked
into the file. The Audit image contains no event rows. TOTP setup, one-time
payslip passwords, provider credentials, logs, and non-fictional records must
never be captured. The exact capture and review procedure is in
`static/help/README.md`.

## Localization

English is the source msgid language. Every Help msgid has a reviewed,
non-empty SK, HU, and UK catalog entry; Hungarian receives the primary client
terminology review. CorvinumEU continues to expose SK/HU only, while the UK
catalog remains complete for the shared platform.

The repository includes `scripts/compile_po.py`, a standard-library PO-to-MO
compiler because the runtime/test images intentionally omit the gettext OS
package and installing host packages is prohibited. It compiles committed PO
sources without extracting or guessing translations, supports contexts and
plurals, and skips fuzzy entries.

## Security and privacy boundaries

- Screenshots and prose use fictional data only until the real-data gate is
  complete.
- Compliance documents are limited to allowed forklift, crane, and welding
  certificates. Passports, identity cards, birth/residence documents,
  financial records, medical reports, and health-certificate scans are not
  upload content.
- Help states that allowed files are sanitized but not individually encrypted
  by Django on disk; protected server storage and encrypted backups remain
  production gates.
- Payslip Help never reveals, records, or pictures a one-time password and
  explains that it must travel over a channel separate from the encrypted PDF.
- Audit Help distinguishes traceability from staff-activity reporting and its
  screenshot contains filters only, not log contents.

## Verification and release

Automated coverage pins the exact 12-card set for both settings modules,
unsupported 404 behavior, registry metadata, navigation coverage, namespace
isolation, conditional prose, static asset discovery, complete translations,
article structure, desktop/mobile layouts, keyboard navigation, all card
links, lazy image loading, annotations, and light/dark legibility.

Before release, run both complete unit lanes, migration checks, Ruff,
production-image/static checks, and the complete two-client Playwright suite.
Manually review all 48 WebPs, build the final production image after the assets
are present, and follow the staging acceptance section of the staging runbook.
Do not deploy Help until the Help-only PR and both-client CI are green.

## Out of scope

Full-text search, video, user-editable documentation, external or stock
imagery, and a new content dependency remain out of scope.
