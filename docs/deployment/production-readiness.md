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
Recommended order (updated 2026-07-26 — items 5, 7 and 9 are now done): lock
down staging/provider access first (item 1, the only one that is urgent while
the repo is public), then implement protected persistent media (items 2 and
3), then schedule backups (item 4).

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
   **Still open:** the Twilio decision itself. The credentials remain live on
   a public-URL staging app. Note that *unsetting* them is not free — with
   them absent, `send_sms` records the message as FAILED rather than raising,
   so the send button would look broken on screen; the demo runbook instead
   tells the presenter to avoid it. Also still open: the value stays
   hardcoded in `seed_demo.py` and six e2e tests, so making it env-driven is
   the durable fix.
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
