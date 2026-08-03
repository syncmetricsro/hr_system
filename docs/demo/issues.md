**Findings**

1. **Critical: public demo credentials can reach live Twilio.** The repository is public, publishes the Jober staging URL/password in [CLAUDE.md](/home/disane/Dev/hr_system/CLAUDE.md:46), and Jober staging currently has Twilio configured. Recruiter, coordinator, and manager roles can send SMS through [views.py](/home/disane/Dev/hr_system/features/messaging/views.py:16). Disable provider credentials on public staging or put staging behind access control immediately; then rotate demo passwords.

2. **Critical: uploaded media is not durable or currently served in production.** Neither Dokku app has a storage mount. Production only serves media through a planned nginx alias, while Django serves it only under `DEBUG` in [urls.py](/home/disane/Dev/hr_system/config/urls.py:243). Avatars and certificate files will disappear on deployment and their `/media/` URLs will currently fail.

3. **Critical: the proposed media-serving design exposes certificate documents publicly.** Certificates link directly to `certificate.document.url` in [compliance_certificates.html](/home/disane/Dev/hr_system/templates/panels/compliance_certificates.html:23). An nginx `/media/` alias would bypass authentication entirely. UUID filenames are not authorization. Certificates need an authenticated, permission-checked download endpoint; avatars need an explicit privacy decision.

4. **High: neither PostgreSQL service has scheduled backups.** Live inspection reports no schedule for `pg-jober-staging` or `pg-corvinum-staging`. This remains listed as open in [production-readiness.md](/home/disane/Dev/hr_system/docs/deployment/production-readiness.md:19).

5. **High: office scoping protects finance only.** People, projects, reports, compliance, logistics, notifications, and exports remain company-wide. For example, Reports queries every person/project in [views.py](/home/disane/Dev/hr_system/core/ui/views.py:61). The limitation is acknowledged in [ADR 0026](/home/disane/Dev/hr_system/docs/adr/0026-office-scoped-rbac.md:31), but it is now a privacy boundary, not optional polish.

6. **High: media replacement leaves old PII files behind.** Avatar and certificate replacement saves a new UUID path without deleting the previous file in [account views](/home/disane/Dev/hr_system/core/accounts/views.py:164) and [certificate services](/home/disane/Dev/hr_system/features/compliance/services.py:108). Removing the current file does not remove historical orphaned versions.

7. **Medium: there is no real GitHub CI gate.** Local checks are strong, but GitHub runs only a legacy Pages build. Every recent Pages run fails on Django template syntax inside Markdown, and no Actions workflow validates tests, migrations, dependencies, or production images. GitHub Pages is also publishing an obsolete June build.

8. **Medium: upload dimension checks happen after full image decoding.** Both avatar and certificate handlers call `image.load()` before enforcing the 8000-pixel limit in [media.py](/home/disane/Dev/hr_system/core/media.py:59). This weakens decompression-bomb protection.

9. **Medium: backlog documentation is materially stale.** The [feature matrix](/home/disane/Dev/hr_system/docs/platform/client-feature-matrix.md:28) still says age warnings and warehouse stock are unimplemented and Jober transport is enabled. [production-readiness.md](/home/disane/Dev/hr_system/docs/deployment/production-readiness.md:7) still says staging/TLS are unavailable. GitHub has zero open issues, so there is no reliable executable backlog.

10. **Low: client Help content leaks unsupported features.** Corvinum users see Jober-only Feedback, profitability, accommodation, and transport guidance. This is already acknowledged in [help-area-design.md](/home/disane/Dev/hr_system/docs/product/help-area-design.md:30).

11. **Decision needed: old wage-ledger branch.** `agent/corvinum-wage-ledger` contains unique `AdvanceRecovery` and derived-net behavior absent from `main`. Do not merge it wholesale: it may violate the agreed recorded-gross/independent-net boundary. Explicitly accept or reject that behavior, then delete the stale branch.

**Current Status**

`main` is clean at `948aff0`; both staging apps are running and passed fresh HTTPS smoke checks. Latest recorded verification is 528 Jober unit tests, 326 Corvinum tests, and 50 Playwright tests. Ruff, vendor hashes, no-Node checks, Django checks, and migration consistency passed again today.

Recommended order: lock down staging/provider access, implement protected persistent media, schedule backups, finish office scoping, then establish CI and reconcile the backlog documents.