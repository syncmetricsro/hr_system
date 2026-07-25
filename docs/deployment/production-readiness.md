# Production Readiness Journal

Tracks what must be true before the Jober app serves real users/data, and the
state of each gate. "Ready" = verified; "Open" = not done / needs a human or an
external input. Update this whenever a gate changes state.

Last updated: 2026-07-25

## Pre-production review findings (2026-07-25)

A cross-cutting review of the deployed staging state (both apps, live
inspection — not just static code reading) found the items below. None are
fixed by writing this list; each stays open until its own fix lands and is
verified the same way (live inspection, not just "the code looks right").
Recommended order (updated 2026-07-25 — items 5 and 7 are now done): lock
down staging/provider access first, then implement protected persistent
media, then schedule backups, then reconcile the stale backlog docs
(item 9, including this file's own pre-2026-07-25 rows below, which
predate several features shipped since — e.g. Dokku staging is live, not
"blocked/open" as those rows still say).

1. **Critical — public demo credentials can reach live Twilio.** The repo is
   public and publishes the Jober staging URL/password in `CLAUDE.md`;
   Jober staging currently has Twilio configured, and Recruiter/Coordinator/
   Manager can send SMS through `features/messaging/views.py`. Disable
   provider credentials on public staging, or put staging behind access
   control, then rotate demo passwords.
2. **Critical — uploaded media is not durable or served in production.**
   Neither Dokku app has a storage mount. Django only serves `/media/` under
   `DEBUG` (`config/urls.py`); production has no nginx alias yet. Avatars
   and certificate files uploaded to staging today will not survive a
   redeploy, and their URLs 404 right now.
3. **Critical — the planned media-serving design would expose certificate
   documents publicly.** `templates/panels/compliance_certificates.html`
   links directly to `certificate.document.url`; a bare nginx `/media/`
   alias (the design `avatar-design.md`/`certificate-upload-design.md`
   sketched) would serve that with no auth check at all — a UUID filename
   is obscurity, not authorization. Certificates need an authenticated,
   permission-checked download view; avatars need an explicit privacy
   decision (are they meant to be as-public-as-a-photo-badge, or not).
4. **High — neither PostgreSQL service has scheduled backups.** Live
   inspection shows no backup schedule on `pg-jober-staging` or
   `pg-corvinum-staging`. Tracked below under "DB backups / restore" since
   2026-06-29; still open.
5. ~~**High — office scoping protects Finance only.**~~ **Fixed
   2026-07-25** (ADR 0026 Phase B, PRs #95–#101). People, Projects,
   Reports, Compliance, Checklists, notifications, accommodation,
   transport and exports are all office-scoped, and the equipment stock
   ledger was split from one pooled company-wide FIFO inventory into
   independent per-office warehouses. The fix went beyond what this item
   asked for: cross-office access to a Person/Project/Accommodation/
   FinancialMonth detail or mutation view now returns a hard **403**
   rather than merely being filtered out of a list, and the shell shows
   which office bounds the current view. Two leaks found while verifying
   completeness — a dashboard occupancy tile aggregating every office's
   rooms, and office-less people being invisible to everyone including
   their own recruiter — were fixed in the same programme. Blacklist
   remains deliberately company-wide (ADR 0026 point 3).
6. **High — media replacement leaves old PII files behind.** Avatar/
   certificate replacement (`core/accounts/views.py`,
   `features/compliance/services.py`) saves the new upload but never
   deletes the file it replaced — only an explicit *remove* deletes the
   *current* file. Every past replacement leaves an orphaned file with no
   remaining reference, and no cleanup path exists yet (this is the same
   "no hard-delete/anonymization hook" gap `avatar-design.md`'s open items
   already flagged, now confirmed to also apply to routine replacement, not
   just erasure).
7. ~~**Medium — no real GitHub CI gate.**~~ **Fixed** (per user, 2026-07-25).
8. **Medium — upload dimension checks happen after full image decoding.**
   `core/media.py`'s avatar and certificate handlers call `image.load()`
   before enforcing the 8000px cap — decompression-bomb protection is
   weaker than it looks, since the image is already fully decoded in
   memory by the time the size check runs. Reorder to check dimensions from
   header/metadata before a full `load()`.
9. **Medium — backlog documentation is materially stale.**
   `docs/platform/client-feature-matrix.md` still lists age warnings and
   warehouse stock as unimplemented and Jober transport as enabled; this
   file's own pre-2026-07-25 rows still say Dokku staging/TLS are
   unavailable. Zero open GitHub issues means there's no separate
   executable backlog to fall back on either — this file (and
   `docs/platform/client-feature-matrix.md`) needs a real reconciliation
   pass against current `main`, not just this list of new findings.
10. **Low — client Help content leaks unsupported features.** CorvinumEU
    users can read the Jober-only Feedback/profitability/accommodation/
    transport Help articles even though CorvinumEU has none of those
    features enabled. Already acknowledged as a known follow-up in
    `help-area-design.md`.
11. **Decision needed — old `agent/corvinum-wage-ledger` branch.** Confirmed
    still present (local + remote), 5 commits ahead of `main`, containing a
    unique `AdvanceRecovery` model and derived-net behavior not on `main`.
    Do not merge it wholesale — it may conflict with the agreed recorded-
    gross/independent-net wage-ledger boundary. Needs an explicit accept-or-
    reject decision, then delete the branch either way rather than leaving
    it stale.

Status at the time of this review: `main` clean at `948aff0`; both staging
apps running the latest deploy and passing fresh HTTPS smoke checks (528
Jober unit tests, 326 CorvinumEU tests, 50 Playwright tests; ruff, vendor
hashes, no-Node check, Django checks, and migration consistency all green).
None of that verifies the 11 items above — they're gaps the standard test/
smoke suite doesn't cover.

## Serving & runtime

| Gate | State | Notes |
|---|---|---|
| Static files served in production | ✅ Ready (2026-06-21) | WhiteNoise under gunicorn (ADR 0016). Regression test `test_static_css_is_served`. Found because Phase 0 smoke never requested an asset. |
| HTTPS + secure cookies on real host | ⚠️ Open | `SECURE_SSL_REDIRECT`/`SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE` default secure; **must not** set the `DJANGO_*_=0` overrides on staging/prod (those exist only for the HTTP smoke network). Verify once Dokku TLS is live. |
| Dokku staging deploy | ⚠️ Open | Blocked on external staging app/domain/PostgreSQL service names. Runbook: `docs/deployment/jober-dokku-staging.md`. |
| DB migrations on deploy | ✅ Ready | `accounts`/`audit` initial migrations run cleanly on pinned PostgreSQL 17. |
| Initial admin user | ✅ Ready (2026-06-21) | `manage.py ensure_superuser` — idempotent, env-driven (`DJANGO_SUPERUSER_EMAIL`/`_PASSWORD`), audited; wired into the Dokku release steps (`docs/deployment/jober-dokku-staging.md`). `seed_demo` remains fictional/staging only — never against a real-data DB. |
| Secret management | 🟡 Partial (2026-06-29) | **Doppler** is the secrets source (project `hr_system`, config `dev`); `doppler run --project hr_system --config dev -- scripts/dev_app.sh up` injects env locally (`doppler.yaml`, `docs/deployment/jober-twilio-setup.md`). Still to confirm: prod Doppler config + Dokku wiring (sync or service token) and `DJANGO_SECRET_KEY`/DB-cred rotation. |
| DB backups / restore | ⚠️ Open | Not yet defined for the Dokku PostgreSQL service. |

## Integrations

| Gate | State | Notes |
|---|---|---|
| Twilio SMS | 🟡 Verified live (2026-06-29) | End-to-end delivery confirmed through the app using live credentials via Doppler and a controlled Twilio Virtual Phone recipient; no phone values are recorded here. Code: stdlib client, signature-verified webhook (ADR 0019). **Remaining (ops, not code):** use a recipient distinct from the configured sender (Twilio rejects same-number attempts with `21266`), upgrade the account to allow non-verified recipients, and point the inbound webhook at public staging/TLS. Real worker numbers stay behind the real-data gate. |

## Product / legal gates (block real data, not code)

| Gate | State | Notes |
|---|---|---|
| Real worker PII | ⚠️ Open (blocked) | Fictional data only until the legal/security real-data gate (Handoff.md, AGENTS.md). |
| DPA / EU hosting / blacklist legal basis / leasing docs | ⚠️ Open | Lawyer items; block go-live, not coding. |
| Finance sign convention | ⚠️ Open | Needs one filled month (Phase 4). |
| Translation catalogs (EN/SK/HU/UK) | ⚠️ Partial (2026-06-23) | English base language; SK/HU/UK catalogs compiled and shipped (ADR 0017). All four render. **HU/UK + revised SK are AI-authored — need a fluent-speaker review** before client-facing use. Recompile via `scripts/compile_messages.sh`. |

## RBAC / audit posture

| Gate | State | Notes |
|---|---|---|
| Action-gated RBAC, office-bounded reads | ✅ Ready | `core/accounts/permissions.py` + `core/offices/scoping.py`, mirrored by `docs/permissions/jober-permission-matrix.md` (ADR 0008/0015, amended by 0026). Reads are broad *within* a user's office(s); Observer spans all offices by role bypass. |
| Append-only audit | ✅ Ready | `core/audit` immutable `AuditEvent`; wired into login/logout. Extend `record_event` to every sensitive action as modules land. |
| Recruiter/coordinator read-scope (GDPR) | ⚠️ Open | Still held behind `BROAD_INTERNAL_READS`; do not hardcode a role split until Jober confirms. Note a *second*, independent boundary now applies regardless of that flag: office scoping (ADR 0026), which already narrows every non-Observer role to its own office(s). |
