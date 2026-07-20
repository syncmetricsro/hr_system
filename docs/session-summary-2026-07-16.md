# Session summary — Jober and CorvinumEU PeopleOps

**Period covered:** the product, demo-readiness, and staging work completed
through 2026-07-16.

This is a consolidated handoff for the long implementation and deployment
session. The detailed chronological records remain in
[BUILD_JOURNAL.md](../BUILD_JOURNAL.md),
[test_journal.md](../test_journal.md), and
[deployment_journal.md](../deployment_journal.md).

## Executive outcome

The shared Django platform now presents two clearly separated thin clients:

- **Jober** — the broader workforce platform with recruitment, logistics,
  compliance, finance, feedback, accommodation, transport, and Twilio SMS.
- **CorvinumEU PeopleOps** — the client-specific operational surface with
  recruitment trials, checklists/readiness, compliance, equipment, blacklist,
  ledger/advances, encrypted payslips, reports, notifications, and audit.

Both fictional-data staging applications are running independently on
**syncmetric-prime**, with separate Dokku apps, PostgreSQL services, settings,
hostnames, cookies, and Doppler scopes. Corvinum SMTP delivery was verified
with an encrypted fictional payslip. Jober Twilio credentials were synchronized
through a four-key allow-list; a distinct approved recipient still needs a
final outbound staging acceptance check before the live SMS act.

The real-data gate remains closed. No work in this session authorizes real
worker records.

## Product and workflow work completed

### Client and brand isolation

- Established the client-neutral `core/`, switchable `features/`, and
  client-owned `clients/` architecture without client branching in core.
- Ensured Jober and Corvinum use their own production settings, navigation,
  theme defaults, static branding, session/CSRF/language cookies, and demo
  data.
- Corrected authentication branding so login and two-factor screens always
  use the active client's name and logo. Tests guard against Jober identity
  appearing in Corvinum and vice versa.
- Added the approved Jober SVG logo and the Corvinum-owned brand treatment.

### Shared UI and accessibility

- Added **Light, Dark, and System** themes with browser-local persistence,
  cross-tab synchronization, live OS-theme changes, and client-specific
  palettes. Jober defaults to Light; Corvinum defaults to Dark.
- Refined Jober's night palette and theme-aware logo presentation.
- Added client-appropriate navigation icons and fixed Corvinum's icon-font
  preload/raw-ligature problem.
- Added consistent spacing between independently contributed panels so cards
  and operational sections no longer visually touch.
- Centered and constrained content to use wide screens more effectively while
  preserving responsive behavior.
- Added localized floating flash messages and confirmation dialogs for
  consequential/destructive actions.
- Fixed language-prefix switching so EN, SK, HU, and UK choices persist and
  navigate to the correct localized URL.

### Notifications and contextual guidance

- Added the shared floating session notification center with separate Problems
  and Updates groups, role/object scoping, manual refresh, individual
  dismissal, authorized destinations, and no idle polling.
- Actionable alerts return only when their underlying state changes; routine
  updates are session-scoped and exclude the viewer's own actions.
- Added shared theme-aware, keyboard-accessible tooltips that work after htmx
  swaps and do not delay touch actions.
- Replaced generic dashboard “Details” help with action-oriented headings and
  destination/filter descriptions.
- Made dashboard metrics and report rows genuine drill-downs, including active
  project, lifecycle-status, and inactive-reason filters.

### Recruitment, personnel, and readiness

- Added/updated guided, versioned intake with optional validated worker email
  for Corvinum and conditional disability fields.
- Ensured a fresh Corvinum demo seeds the published questionnaire so **Add
  person** works after every reset.
- Enabled shared trial-day scheduling and outcomes for Corvinum. Recruiters,
  coordinators, and managers can schedule; coordinators and managers can record
  outcomes; observers remain read-only.
- Added centralized trial lookup/create/edit workflows and role/project scope.
- Improved readiness screens by highlighting incomplete or suspicious fields
  and displaying specific translated activation blockers.
- Changed activation-checklist toggles to update their panel in place with
  htmx. Checking an item no longer reloads the person page or jumps to the top;
  the full-page CSRF-protected fallback remains available.

### Logistics and operational data entry

- Added manager-only accommodation location/room create, edit, deactivate, and
  capacity-safe management. Coordinators continue to assign people but cannot
  alter the catalogue.
- Added transport lookup, create/edit controls, and trend reporting.
- Added a manager-owned equipment catalogue with search, create, edit,
  deactivate, EUR unit prices, and audit. Coordinators remain limited to
  issue/return operations.
- Improved item prices and financial values so EUR is explicit throughout the
  relevant UI.
- Added clearer panel spacing and operational layouts in both clients.

### Reports, audit, and localization

- Merged passive overview information into interactive Reports workspaces in
  both clients and reduced redundant navigation.
- Made report metrics, lifecycle rows, finance panels, and relevant lists
  clickable with filters that match their tooltip promises.
- Localized lifecycle changes, audit-event labels, operational events, and new
  UI into EN, SK, HU, and UK.
- Kept the audit log append-only for ordinary users and filtered sensitive
  values from notifications and provider-facing messages.

### Blacklist re-entry protection

- Documented and demonstrated the HMAC-based blacklist identifier formula and
  data boundary. Raw identifiers are never stored as person fields, intake
  answers, or audit values.
- Added manager-only operational archive, explicitly separate from GDPR
  erasure. Archive preserves approved cases, fingerprints, and audit history.
- Added transient identifier/type inputs during intake. Re-entering the same
  fictional identifier creates a proposed match for manager review; it does
  not merge people or silently blacklist the new record.
- Added the full fictional propose → approve → archive → re-enter → decide
  walkthrough to the Corvinum presenter runbook.

### Payslips and email

- Added optional personnel email to Corvinum intake/editing.
- Verified encrypted PDF payslip delivery using the Corvinum staging SMTP
  configuration. The one-time PDF password is shown only in the application
  and must be delivered separately.
- Made resend use the last successful recipient and generate a new encrypted
  PDF/password.
- Converted SMTP/provider failures into safe translated UI errors instead of a
  raw server-error page.
- Jober currently has no enabled email-sending feature. Its staff emails are
  login identifiers and worker email is optional contact data. SMTP can be
  added later for password reset or invitations; authenticator-app TOTP itself
  does not require email.

## Demo and presenter material

- Rebuilt the Corvinum presenter walkthrough around the live client workflow:
  branded login/TOTP, interactive reports, fictional intake, trial scheduling,
  readiness/checklists, notifications, equipment/ledger, encrypted payslips,
  audit, and optional blacklist re-entry.
- Updated the Jober walkthrough with the current themes, notifications,
  tooltips, interactive reports, live controlled SMS act, and Twilio sender /
  recipient separation rule.
- Added recovery guidance for clean demo resets, TOTP rehearsal, SMTP fallback,
  risky-action cancellation, and public staging checks.

Primary presenter documents:

- [Corvinum demo walkthrough](deployment/corvinum-demo-runbook.md)
- [Jober demo walkthrough](deployment/jober-demo-runbook.md)
- [Shared syncmetric-prime staging runbook](deployment/syncmetric-prime-staging.md)
- [Jober Dokku staging runbook](deployment/jober-dokku-staging.md)

## Staging deployments

| Client | Dokku app / database | Settings | Deployed application revision | Provider state |
|---|---|---|---|---|
| CorvinumEU | `corvinum-staging` / `pg-corvinum-staging` | `clients.corvinum_eu.production` | `6abdb56` (`jober-platform:corvinum-demo-6abdb56`) | Seven allow-listed SMTP settings; encrypted fictional payslip delivery verified |
| Jober | `jober-staging` / `pg-jober-staging` | `config.settings.production` | `12d0735` | Four allow-listed Twilio settings; Jober email deliberately deferred |

Both applications:

- were built locally from committed, clean worktrees without runtime secrets;
- were streamed to Dokku with `git:load-image` rather than built on the VPS;
- use HTTPS, secure client-specific cookies, Gunicorn on port 8000, and separate
  fictional PostgreSQL databases;
- passed migrations and public health checks;
- remain fictional-data staging demonstrations, not production/real-data
  systems.

The latest Corvinum checklist release preserved its database and demo state,
required no migration or reseed, and passed Dokku health checks before the old
container was replaced.

## Doppler and provider boundaries

- Corvinum local SMTP demo: `hr_system/dev_corvinum_demo`.
- Corvinum staging SMTP: `hr_system/stg_corvinum-staging`.
- Jober staging Twilio: `hr_system/stg_jober-staging`.
- Service tokens are read-only and config-scoped. Secrets enter only the
  runtime that needs them, never the image, build stage, Git history, journals,
  or backup archives.
- Corvinum synchronizes only its seven approved `DJANGO_EMAIL_*` values.
- Jober synchronizes only `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`,
  `TWILIO_FROM_NUMBER`, and `DEMO_SMS_PHONE`.
- `DEMO_SMS_PHONE` must be a distinct approved recipient from
  `TWILIO_FROM_NUMBER`. Twilio error `21266` identified a same-number attempt;
  it was a provider rule rather than an application, CSRF, or deployment fault.
- The Jober inbound webhook must be configured against public HTTPS and remains
  signature-verified/fail-closed.

No credential, token, sender number, recipient number, worker address, or
one-time payslip password is recorded in this summary.

## Production and backup planning

- Selected a cost-first **FORPSI Basic Linux VPS** for initial low-traffic
  Corvinum production, with documented resource, disk, swap, and restore-time
  upgrade triggers.
- Selected **Contabo Storage VPS 10** in the EU as the encrypted independent
  backup target, without the Object Storage add-on.
- Defined encrypted nightly PostgreSQL/release-manifest backups, future media
  inclusion, 35 daily + 12 monthly retention, 26-hour freshness checks, 60%
  capacity threshold, and monthly restricted restore drills.
- Added deployment-host scripts that intentionally exclude Dokku/Doppler
  configuration and therefore cannot archive secrets.
- Staging is designed to be on-demand on the future cost-conscious Corvinum
  production host.

See [Corvinum Basic production operations](deployment/corvinum-basic-production.md)
for the complete provider and backup plan.

## Verification completed

- Latest focused checklist slice: **8 passed**.
- Latest complete Playwright suite: **39 passed**.
- The browser regression verifies the checklist mutation keeps the same URL
  and scroll position while preserving CSRF and updating attribution.
- Relevant Ruff checks and whitespace validation passed.
- Corvinum public staging health, Slovak login, compiled CSS, migration
  idempotency, and Dokku replacement-container checks passed.
- Earlier focused suites covered client branding, role/feature boundaries,
  intake email, trial permissions, blacklist re-entry, equipment catalogue,
  SMTP failure handling, notifications, themes, tooltips, translations, and
  deployment-script contracts. Exact counts and commands are retained in
  [test_journal.md](../test_journal.md).

## Current Git state at handoff

- Branch: `agent/corvinum-operations-and-deployment`
- Draft pull request: [#73 — Expand Corvinum operations and deployment](https://github.com/syncmetricsro/hr_system/pull/73)
- Latest application commit deployed to Corvinum: `6abdb56`
- Latest committed deployment record before this summary: `d959622`

This summary file itself should be committed separately after review. Its
addition does not require another application deployment.

## Remaining work and gates

### Before the client demonstrations

- Run one harmless Jober outbound SMS to a distinct approved test recipient and
  confirm delivery in Twilio.
- Configure and test the Jober public inbound webhook after outbound acceptance.
- Rehearse both current public staging walkthroughs in fresh private browser
  profiles.
- Keep fictional data and controlled provider recipients only.

### Before production or real data

- Complete and sign the applicable DPAs and confirm provider data locations.
- Complete the blacklist legitimate-interest assessment and written contractual
  language; confirm category and retention decisions.
- Review sensitive-field visibility, permissions, and retention rules with the
  clients and legal/security owners.
- Order and harden the production/backup infrastructure, establish recovery-key
  custody, configure monitoring, and pass a production restore drill.
- Complete native-speaker review of SK/HU/UK translations.
- Resolve the remaining Corvinum C-Q decisions, especially payroll/ledger cycle
  policy, mandatory documents, retention, and final role mapping.
- Keep staging data fictional and separate from production.

### Operational maintenance

- Replace/revoke staging Doppler service tokens according to the agreed token
  lifecycle.
- Move Dokku applications away from the deprecated default Docker bridge
  linking model during planned host maintenance.
- Add Jober SMTP only when an approved email workflow such as password reset or
  staff invitations is implemented and security-reviewed.

## Journal status

Yes—the build journal was updated throughout the session. The newest entries
cover the checklist scroll-position fix, public Corvinum staging release,
payslip failure handling, equipment catalogue, optional intake email, trials,
blacklist re-entry, production backup operations, client-auth branding, and
demo bootstrap. Deployment outcomes and provider acceptance are in
`deployment_journal.md`; test evidence is in `test_journal.md`.
