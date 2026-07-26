# Production Readiness Journal

Tracks what must be true before the Jober app serves real users/data, and the
state of each gate. "Ready" = verified; "Open" = not done / needs a human or an
external input. Update this whenever a gate changes state.

Last updated: 2026-07-26

## Pre-production review findings (2026-07-25)

A cross-cutting review of the deployed staging state (both apps, live
inspection — not just static code reading) found the items below. None are
fixed by writing this list; each stays open until its own fix lands and is
verified the same way (live inspection, not just "the code looks right").
Recommended order (updated 2026-07-26 — items 1, 2, 3, 5, 6, 7, 8 and 9 are
now done): **scheduled database backups (item 4) are the largest remaining
risk**, followed by the user/credential-management subsystem (item 11) and a
one-off sweep of media orphaned by pre-fix replacements (item 6).

1. 🟡 **Partly fixed 2026-07-26 — public demo credentials could reach live
   Twilio.** The repo is public and publishes `demo-jober-2026`; Jober
   staging has Twilio configured and Recruiter/Coordinator/Manager can send
   SMS through `features/messaging/views.py`.
   **Done:** all four `@demo.jober.test` accounts on `jober-staging` were
   rotated off the published value by the owner, verified by confirming the
   old password no longer authenticates on any of them. `seed_demo` was also
   changed so it no longer resets an existing account's password (it did on
   every run, so any reseed would have quietly republished the known value);
   `--reset-passwords` forces the old behaviour and the command reports when
   it preserves one. `CLAUDE.md` now marks the published value local-only.
   **Twilio: fixed 2026-07-26.** Two changes replaced the runbook's
   "don't press Send". A recipient allowlist (`SMS_ALLOWED_RECIPIENTS`,
   empty = unrestricted, so production is unaffected) blocks any non-listed
   number *before* the provider call — staging holds fictional worker data
   and real credentials, and a fictional record with a real number typed
   into it is indistinguishable from any other, so "the data is fake" was
   never a control. A blocked send records `BLOCKED`, not `FAILED`: the
   provider never saw it. And unsetting the credentials is now genuinely
   safe — `sms_configured()` drives a disabled control with a stated reason,
   where before an unconfigured app filed a FAILED message and looked broken.
   **Still open:** the demo password stays hardcoded in `seed_demo.py` and
   six e2e tests, so making it env-driven is the durable fix. **Owner
   action:** set `SMS_ALLOWED_RECIPIENTS` on both staging apps to the
   existing `DEMO_SMS_PHONE` value.
2. ~~**Critical — uploaded media is not durable or served in production.**~~
   **Half of this was wrong, and the rest is fixed 2026-07-26.**
   *Wrong:* "Neither Dokku app has a storage mount." Both apps **do** have
   one (`/var/lib/dokku/data/storage/<app>-media:/app/media`), and
   `MEDIA_ROOT` resolves to `/app/media` — verified by printing it from the
   running container. Uploads have always survived redeploys; the demo
   runbook's warning that they "vanish on redeploy" inherited this error and
   has been corrected.
   *Right, and now fixed:* nothing served them. `/media/` was routed only
   under `DEBUG` and no nginx alias exists, so an upload succeeded and then
   rendered as a broken image or a dead link. Files are now delivered by
   `core/media_views.py` (see item 3).
3. ~~**Critical — the planned media-serving design would expose certificate
   documents publicly.**~~ **Fixed 2026-07-26 — and it was never live.**
   The hole would have been *created* by building what the design docs
   specified (a bare nginx `/media/` alias), not by anything deployed:
   `nginx:show-config` confirmed no alias exists, so the exposure was
   still on paper. Both design docs have been reversed rather than left as
   a sketch someone implements later.
   Files now go through `core/media_views.py`: person avatars take the
   office boundary, staff headshots take plain authentication (colleagues
   appear in shared queues; a headshot is not office data), and certificate
   documents take the office boundary **and** `can_view_sensitive` — so an
   unconnected recruiter in the same office sees that a certificate exists
   and gets a 403 on the scan. The avatar privacy question this item asked
   for is answered: **not** as-public-as-a-photo-badge.
   The `DEBUG`-only `/media/` route was removed too — it meant local
   development bypassed every check while production served nothing, so a
   bypass was one settings flag away and invisible locally.
4. **High — neither PostgreSQL service has scheduled backups.** Still open,
   and now the largest remaining risk here. Prepared 2026-07-26; **blocked on
   the owner** for two concrete things, not on design.
   *What was wrong with the plan:* the runbook told you to run
   `dokku postgres:backup-schedule <service> <cron> <off-site-or-local>`.
   That command is **S3-only** — `postgres:backup-auth` takes AWS keys and the
   third argument is a bucket. There is no local-target variant, and it backs
   up only the database, not the media volume (which now holds real uploads)
   or a release manifest.
   *What is ready:* `scripts/offsite_backup.sh` (generalised from the
   CorvinumEU-specific version, so one script now covers any Dokku app) plus
   `scripts/backup_health.sh`. Encrypts with GPG before transfer, verifies the
   remote checksum, keeps 35 daily + 12 monthly, includes the media volume,
   and never exports Dokku config because that carries Doppler secrets. Exact
   env files and cron lines are in
   `docs/deployment/syncmetric-prime-staging.md` §"Phase 6 — Backups".
   *Blocked on:* **(a)** an off-site host on a different provider (open
   question **D6**), **(b)** a GPG public key whose private half lives on
   neither server, and **(c)** root shell on the Dokku host — the agent SSH
   key is restricted to `dokku` commands and cannot install cron entries.
   *Interim:* manual `dokku postgres:export` dumps were taken for both
   services on 2026-07-26. That is a point-in-time safety net, not a backup
   system.
   **This item stays open even once a schedule runs, until a restore drill
   has actually been performed** (`scripts/backup_restore_drill.sh`) and
   logged. A backup nobody has restored is a hypothesis.
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
6. ~~**High — media replacement leaves old PII files behind.**~~ **Fixed
   2026-07-26.** `core.media.save_replacing` now stores the new file and
   deletes the one it replaced, used by all three call sites (own avatar,
   person avatar, certificate document). The delete runs in
   `transaction.on_commit`, so a rolled-back transaction cannot destroy the
   file the row still points at.
   **Still open, and different:** files orphaned by replacements made
   *before* this fix are still on the volumes, and there is still no
   hard-delete/anonymization hook for erasure requests — the broader gap
   `avatar-design.md`'s open items flagged. A one-off sweep comparing
   storage against `FileField` values would clear the historical orphans;
   nothing does that yet.
7. ~~**Medium — no real GitHub CI gate.**~~ **Fixed** (per user, 2026-07-25).
8. ~~**Medium — upload dimension checks happen after full image decoding.**~~
   **Fixed 2026-07-26.** Both handlers now read `.size` from the header in
   the probe block and reject before anything decodes; a test monkeypatches
   `Image.load` to raise, so it asserts *nothing was decoded* rather than
   *the error message looks right*. `Image.MAX_IMAGE_PIXELS` is also capped
   as a second line of defence, because a dimension check alone still admits
   7999 × 7999 (~64M pixels).
9. ~~**Medium — backlog documentation is materially stale.**~~ **Fixed
   2026-07-26.** `docs/platform/client-feature-matrix.md` was reconciled
   against `main` — each claim re-checked in the code rather than assumed:
   warehouse stock ships (and is per-office), `core/people/services.py::
   age_warning` ships, and Jober transport is `False` in
   `clients/jober/settings.py`, so the recorded flag mismatch was already
   resolved. Office-scoped RBAC gained a row, and the People, Accommodation
   and Profitability rows gained the office dimension. The legacy "region"
   vocabulary was swept in the same pass: `Jober_Finance_Specs.md` and
   `docs/product/jober-requirements-supplement.md` keep their interview and
   workbook text as historical provenance (that is what makes them useful
   for the sign convention) but now carry a banner stating that regions
   became `Office` in ADR 0026 and that `Project.region` no longer exists;
   their "can the region list grow?" open questions are marked answered.
   `docs/security/security-review-2026-06-29.md` keeps its dated text with
   an inline note that ADR 0026 superseded "offices are filters, not access
   boundaries", and ADR 0008 now carries a forward-pointer to 0026.
   This file's own stale rows were corrected in the same pass and verified
   against the live app rather than against the journal: "Dokku staging
   deploy" and "HTTPS + secure cookies on real host" are now Ready, the
   latter confirmed by inspecting the actual response headers and cookie
   flags.
   *Deliberately left for later:* the last legacy "region" naming is in
   **code**, not docs — `features/finance/views.py` still passes
   `regional_results`/`regional_chart_data`, read by
   `templates/pages/finance_summary.html` and `finance_year.html` (including
   the DOM id `chart-data-finance-summary-regional`). The data is already
   per-office; only the names are stale. It is a mechanical rename across one
   view and two templates, needing both unit lanes plus e2e, and was not worth
   running the day before the CEO demo for a change no user can see.
10. **Low — client Help content leaks unsupported features.** CorvinumEU
    users can read the Jober-only Feedback/profitability/accommodation/
    transport Help articles even though CorvinumEU has none of those
    features enabled. Already acknowledged as a known follow-up in
    `help-area-design.md`.
11. **High — no in-app user or credential management at all.** Confirmed
    2026-07-26 while rotating the staging demo password: that required a
    shell command against the Dokku host, because **no route in the
    product can change any password.** `core/accounts/` has no `urls.py`
    or `forms.py`; the only account routes are login, logout, the two 2FA
    views and avatar upload/remove. `Action.USER_MANAGE` is granted to
    Manager in both clients' `policies.py` but has no view behind it.
    There is no self-service password change, no administrator-initiated
    reset, no deactivation path (`User.is_active` exists and Django
    honours it, but nothing sets it), and no way to clear a lost 2FA
    enrolment — which matters because CorvinumEU turns 2FA on for
    managers. Django admin is not a fallback for a client: it needs a
    superuser, and no Jober role is one. Designed but unbuilt in
    `docs/product/jober-multi-office-scoping.md` §3a (invitation) and
    §3b (credential lifecycle); the authority model is office-scoped like
    everything else — Observer over every office, a manager over their
    own. **This is the largest functional gap in the product** and blocks
    real users more directly than it blocks the demo, which uses seeded
    accounts throughout.
12. **Medium — no superuser exists on `jober-staging`.** The 2026-07-26
    database reset removed it and nothing restores it: the `Procfile`
    declares only a `web:` process, there is no `app.json`, and
    `DJANGO_SUPERUSER_EMAIL`/`_PASSWORD` are not in the app's config. The
    "Initial admin user" row below claimed `ensure_superuser` is "wired
    into the Dokku release steps" — it is not, and never was; it has only
    ever been run by hand. Nothing in the demo depends on it, but `/admin/`
    is unreachable until someone runs the command again.
13. **Decision needed — old `agent/corvinum-wage-ledger` branch.** Confirmed
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
None of that verifies the 13 items above — they're gaps the standard test/
smoke suite doesn't cover.

## Serving & runtime

| Gate | State | Notes |
|---|---|---|
| Static files served in production | ✅ Ready (2026-06-21) | WhiteNoise under gunicorn (ADR 0016). Regression test `test_static_css_is_served`. Found because Phase 0 smoke never requested an asset. |
| HTTPS + secure cookies on real host | ✅ Ready (verified live 2026-07-26) | `SECURE_SSL_REDIRECT`/`SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE` default secure; **must not** set the `DJANGO_*_=0` overrides on staging/prod (those exist only for the HTTP smoke network). Confirmed against `https://jober-staging.…sslip.io`: HTTP redirects to HTTPS, `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, and the CSRF cookie carries `Secure; HttpOnly; SameSite=Lax`. Minor cleanup left: nginx emits a *second*, shorter HSTS header (`max-age=15724800`) alongside Django's — harmless but duplicated. Production settings also set `SECURE_PROXY_SSL_HEADER`, so anything speaking to the app directly must send `X-Forwarded-Proto`. |
| Dokku staging deploy | ✅ Ready (2026-07-26) | No longer blocked — the names exist and both apps are live: `jober-staging` and `corvinum-staging` on host `syncmetric-prime-dokku`, backed by `pg-jober-staging` / `pg-corvinum-staging`. Images are built locally from pinned deps and streamed with `git:load-image`, so the VPS never builds source or sees build-time secrets. Runbook: `docs/deployment/syncmetric-prime-staging.md`; per-deploy record in `deployment_journal.md`. **Production** deployment remains open (C-Q14, real server names). |
| DB migrations on deploy | ✅ Ready | `accounts`/`audit` initial migrations run cleanly on pinned PostgreSQL 17. |
| Initial admin user | ⚠️ Open (corrected 2026-07-26) | `manage.py ensure_superuser` — idempotent, env-driven (`DJANGO_SUPERUSER_EMAIL`/`_PASSWORD`), audited. **It is not wired into any release step**, contrary to what this row previously claimed: the `Procfile` declares only `web:`, there is no `app.json`, and the superuser env vars are not in either app's config. It has only ever been run by hand, so a database reset silently leaves the app with no superuser — which is the current state of `jober-staging` (finding 12). Either add a release step with the vars supplied from Doppler, or accept that it is a manual post-reset step and say so in the runbook. `seed_demo` remains fictional/staging only — never against a real-data DB. |
| Secret management | 🟡 Partial (2026-06-29) | **Doppler** is the secrets source (project `hr_system`, config `dev`); `doppler run --project hr_system --config dev -- scripts/dev_app.sh up` injects env locally (`doppler.yaml`, `docs/deployment/jober-twilio-setup.md`). Still to confirm: prod Doppler config + Dokku wiring (sync or service token) and `DJANGO_SECRET_KEY`/DB-cred rotation. |
| DB backups / restore | ⚠️ Open — **defined, not installed** (2026-07-26) | Scripts and cron lines are ready (`scripts/offsite_backup.sh`, `scripts/backup_health.sh`; env and schedule in `syncmetric-prime-staging.md` §Phase 6). Blocked on an off-site host (D6), a GPG recipient key, and root shell on the Dokku host. The plugin's own `postgres:backup-schedule` is **S3-only** and covers the database only — not the media volume. Manual dumps taken 2026-07-26 as an interim. Stays open until a restore drill is run and logged. |

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
