# Deployment Journal

## 2026-07-28 - Rail, Help gating, Help pipeline and the seed correction deployed

Deployed **`4db5f99`** to `jober-staging` as `jober-platform:demo-4db5f99`,
carrying the worker status rail (#136), both J9 slices (#137 Help article
gating, #138 the screenshot pipeline plus the rail-overlap fix that pipeline
found), and the seed correction (#139). No migrations.

`seed_people` was re-run deliberately, to exercise the repair path rather than
only to refresh data: the recruiter correction applies on creation, so without
an explicit repair pass this database would have kept its old attribution
however often it was reseeded. It worked - Farrukh moved to the Győr recruiter
and Tran to the Dunajská Streda one, on rows that already existed.

Verified live:

| check | result |
|---|---|
| seeded ownership | 4 VM / 1 GYR / 1 DS across three recruiters |
| J2, Observer | 7 registered; recruiters 5 / 1 / 1 |
| J2, VM manager | 5 registered; the other offices' recruiters at 0, correctly scoped |
| J8 rail, VM manager | 5 of 7 workers; counts available 2, working 1, inactive 1, blacklisted 1 |
| J9 Help index | all nine articles, which is right for Jober |

**The staff-activity spread is thin and that is a property of the demo, not a
bug.** Seven people across three offices cannot produce a dramatic comparison;
5/1/1 is truthful where 7/0/0 was misleading. If the client wants the report to
*look* like the tool it is, the demo needs more seeded people, which is a
decision rather than a fix.

## 2026-07-28 - Five slices deployed; the audit filter finally works on real data

Deployed **`4d1f6e3`** to `jober-staging` as `jober-platform:demo-4d1f6e3`,
carrying J1 (audit filter), J3 (accommodation cost report), the ADR 0026
aggregate sweep, J7 (period control) + the real J10 fix, J5 (goods-receipt log)
and J2 (staff activity). Migrations had already been applied in the earlier
`2d393b9` deploy; this one reported none pending.

**`backfill_audit_persons` is the reason this deploy mattered.** The earlier
deploy of J1 looked successful and was not: the migration had attributed 8 of
900 events, so typing a worker's name into the audit filter still returned
**zero rows for every account** - the client's original complaint, unchanged.
The command attributed 25 more, all worker actions, and the filter now answers:

| worker | office | observer | VM manager | DS manager |
|---|---|---|---|---|
| Diana Horvathova | Velký Meder | 2 | 2 | 0 |
| Olha Kovalenko | Velký Meder | 10 | 10 | 0 |
| Farrukh Tashkentov | Győr | 2 | **0** | 0 |
| Tran Van Minh | Dunajská Streda | 15 | **0** | 15 |

Scoping and the person filter compose correctly in both directions, and
diacritic folding works live: `Horvathova`, `horvat`, `HORVAT` and
`diana horvat` all return the same 2 rows.

**Demo caveat worth knowing before a walkthrough:** `Mira Novakova` returns 0
for everyone, correctly - the seed creates her and never acts on her, so she
has no history to find. Anyone testing the filter should pick Olha, Tran or
Diana. A worker with no events looks identical to the bug that was just fixed.

Also verified live: J5 scoping (VM 3 receipts/58 units, DS 1/15, Observer
5/96 - the seed spread across months is visible), and J2 (VM manager 5 people
registered, Observer 7, with all three recruiters listed including the two
zeros).

**Seed observation for the demo:** every seeded person is attributed to the
Velký Meder recruiter, so the staff-activity table shows one recruiter with
everything and two with nothing. That demonstrates the zero rows but not the
"gap between two working recruiters" the feature exists for. Worth spreading in
a later seed pass, the same way the goods receipts were.

## 2026-07-27 - Activation approval deployed; deploy key made keyring-independent

- Deployed **`294b877`** to `jober-staging` as `jober-platform:demo-294b877`.
  One migration: `projects.0007_activationapproval`. Reseeded; `seed_demo`
  reported "Kept the existing password on 10 account(s)", so the owner's
  rotated password survived as designed.
- **Verified the control live, with the real demo accounts**, not locally:

  | check | result |
  |---|---|
  | seeded request | Tran → CARGO (DS), raised by `koordinator.ds` |
  | `manazer@` (VM) sees it | **no** — queue is office-scoped |
  | `manazer.ds@` sees it | yes |
  | `koordinator.ds@` decides | **403** — coordinators cannot approve |
  | `manazer@` decides a DS request | **403** — wrong office |
  | `manazer.ds@` approves | 302, approval `approved`, person `working`, decider recorded |

- **The verification consumed the demo fixture** - approving moved Tran to
  Working and emptied the queue, and `seed_demo_scenario` will not recreate a
  request for someone already Working. Restored deliberately rather than left
  broken: `exit_person` back to Available, delete the consumed approval, re-run
  the scenario seed. Confirmed afterwards that the pending request, both
  blacklist cases and all 7 people are intact. **Any future live walkthrough of
  this flow has the same one-shot problem** - it is the third demo fixture with
  that property, alongside Diana's blacklist case and Olha's equipment charge.
- **Observer gets 403 on the Activations queue.** Consistent with the blacklist
  queue, which is also gated on a manager-only action, and with both matrices
  giving Observer no `approval.activate`. Recorded because it is a reasonable
  thing to question: the all-offices oversight role cannot see a queue of
  pending commitments. Not changed unilaterally.
- **Deploy key replaced.** The GNOME-keyring-held key stopped signing mid-session
  ("agent refused operation") because the keyring locks on screen lock and
  `SSH_ASKPASS` is unset in the agent's environment. Replaced with a dedicated
  passphrase-less key plus `IdentityAgent none` in the host block - the second
  half is load-bearing, because without it ssh still asks the agent first, gets
  a refusal, and never falls back to the file. Registered with
  `dokku ssh-keys:add` rather than appending to `authorized_keys`, so it keeps
  the forced-command restriction: dokku subcommands only, no shell. Revoke with
  `dokku ssh-keys:remove claude-deploy` without touching the personal key.
- All five HTTPS smoke checks passed after the deploy.

## 2026-07-26 - Per-office staff deployed; six new accounts secured immediately

- Deployed **`534d961`** to `jober-staging` as `jober-platform:demo-534d961`
  (`sha256:43f211d5...`). No migrations. Re-ran `seed_demo` and `seed_people`:
  **6 accounts created, 4 updated**, with the four existing passwords preserved
  by the guard added earlier today ("Kept the existing password on 4
  account(s)").
- **The six new accounts were created with the published seed password**, which
  is a live exposure on a public URL for as long as it lasts. Closed within the
  same session by copying the password *hash* from `manazer@` - which already
  carried the owner's rotated value - onto the six. That gives all nine staff
  logins the owner's password without the plaintext ever being known here or
  typed into a terminal. Verified afterwards: **no** `@demo.jober.test` account
  accepts `demo-jober-2026`.
- Reciprocal boundary confirmed live, which was the point of the change:

  | account | badge | DHLBA / WEB / CARGO | people |
  |---|---|---|---|
  | `manazer@` | Velký Meder | 200 / 403 / 403 | 5 VM workers |
  | `manazer.gyor@` | Győr | 403 / 200 / 403 | Farrukh |
  | `manazer.ds@` | Dunajská Streda | 403 / 403 / 200 | Tran |
  | `pozorovatel@` | All offices | 200 / 200 / 200 | all 7 |

- Every project now resolves to a coordinator of its own office (checked all
  six), replacing the state where one Velky Meder coordinator was responsible
  for four projects they got a 403 on.
- Unchanged and re-verified: Slovak finance headings with no English left,
  warehouse 36 + 23 + 14 = 73 units / EUR 1 281.50 with zero orphans, 2025 and
  2026 finance totals, and all five HTTPS smoke checks.

## 2026-07-26 - PostgreSQL password rotated on jober-staging (and a brief outage)

Rotating `pg-jober-staging`'s password took the app down for a few minutes.
Worth recording exactly why, because the cause was a wrong assumption in the
procedure I wrote, not an execution mistake.

- **The app does not read `DATABASE_URL`.** `config/settings/base.py` builds
  the connection from `DB_NAME`/`DB_USER`/`DB_PASSWORD`/`DB_HOST`/`DB_PORT`;
  the string `DATABASE_URL` appears nowhere in the settings. So the documented
  `postgres:unlink` + `postgres:link` step - the part that re-issues
  `DATABASE_URL` - **could never have fixed anything**. The variable that
  matters is `DB_PASSWORD`, and nothing was updating it.
- Sequence as it actually ran: `ALTER ROLE` succeeded, so the *database* had
  the new password; the `PASSWORD` file was updated; `postgres:unlink`
  reported "Not linked to app jober-staging" and did nothing; `postgres:link`
  then created a *second* link under the alias `DOKKU_POSTGRES_AQUA_URL`,
  leaving the stale `DATABASE_URL` in place. The app kept reading the old
  `DB_PASSWORD` and failed authentication.
- **Fix:** `dokku config:set jober-staging DB_PASSWORD=<new>`, taking the value
  out of `DOKKU_POSTGRES_AQUA_URL` without echoing it. Back up immediately -
  `DB OK`, 7 people, 54 financial months, office scoping and all five HTTPS
  smoke checks confirmed unchanged.
- Removed the leftover `DATABASE_URL`: it held the now-invalid old password,
  nothing read it, and leaving a dead credential in an app's config is exactly
  the sort of thing that misleads the next person debugging.
- **An earlier attempt had failed silently and looked partly successful.**
  `docker exec` (permission denied on `docker.sock`) and the `PASSWORD` file
  write (permission denied) both failed, while the sudo'd unlink/link ran and
  printed a confident "Application deployed". Nothing had rotated. The tell was
  that the re-issued DSN carried the *same* password as before - which is the
  check worth doing after any rotation.
- **The correct minimal procedure** for this app is therefore: `ALTER USER` in
  the database, write the `PASSWORD` file, then `config:set DB_PASSWORD`. The
  unlink/link cycle is unnecessary here and is what introduced the alias mess.

## 2026-07-26 - Media serving, SMS allowlist and the office-guard fixes deployed

- Deployed **`197cf23`** to `jober-staging` as `jober-platform:demo-197cf23`
  (`sha256:f24620d0...`), covering PRs #115-#118: object-level office guards,
  permission-checked media delivery, SMS safety, and media hygiene. Built
  locally from pinned dependencies, streamed with `git:load-image`. One
  migration applied: `messaging.0002_alter_outboundmessage_status` (the new
  `BLOCKED` status).
- Set **`SMS_ALLOWED_RECIPIENTS`** on `jober-staging` from the existing
  `DEMO_SMS_PHONE`, then restarted (a `--no-restart` config change is not live
  until the containers are replaced - worth remembering, because the app would
  otherwise have looked unprotected while the variable was already set).
  Verified in the running app: an arbitrary number is **blocked**, the
  configured handset is **allowed**, and Twilio still reports configured.
- **The durability question is now closed with evidence rather than
  inference.** Uploaded an avatar and a certificate document, replaced the
  containers with `ps:restart`, and re-fetched: the file was still on disk and
  both fetches returned 200 (370 and 4 429 bytes). `/media/<name>` returned
  **404** in the same session, confirming there is no bypass around the
  permission-checked views.
- Permission behaviour verified live: a Velky Meder manager gets **403** on a
  Gyor person's avatar, and Observer gets **404** on the same URL - permitted,
  but no file. That ordering matters: the permission check runs before the
  existence check, so a cross-office request cannot be used to probe whether a
  file exists.
- One test premise of my own was wrong and is worth recording: Observer cannot
  upload an avatar (403), because `person_avatar_upload` requires
  `intake.create_edit`, which the read-only role does not hold. Correct
  behaviour; the verification script was wrong, not the app.
- Verification artifacts were removed afterwards, so the demo still shows the
  seeded illustrated avatars rather than solid-colour placeholders. Office
  scoping, the Slovak headings and all five HTTPS smoke checks re-confirmed
  after the deploy.
- Rollback target: `jober-platform:demo-a6ad9ad`.

## 2026-07-26 - Demo passwords rotated; seed guard deployed to jober-staging

- The owner rotated all four `@demo.jober.test` accounts on `jober-staging`
  off `demo-jober-2026`, the value this **public** repository publishes.
  Verified rather than assumed: the old password no longer authenticates on
  any of the four, and the hand-off command's `<your-password>` placeholder
  had not been pasted through literally - a failure the `rotated` success
  message would have hidden completely.
- Deployed **`a6ad9ad`** as `jober-platform:demo-a6ad9ad`
  (`sha256:2402ab17...`) to make the accompanying safety fix real on the
  machine. `seed_demo` previously called `set_password` on **every** run, so
  the next routine reseed would have silently restored the published value;
  it now sets the built-in password only on accounts it creates.
- **Proved the guard in production rather than trusting the unit tests.** Ran
  `python manage.py seed_demo` on staging - precisely the command that would
  previously have republished the password - and it reported "Kept the
  existing password on 4 account(s)", with the old password still failing on
  all four afterwards.
- Re-verified everything after the redeploy: office badges (`Velký Meder` /
  `All offices`), 5-of-7 people and 2-of-6 projects for the scoped roles
  against 7 and 6 for Observer, Győr 403 vs 200, the Slovak finance headings
  (`Mesačný trend podľa pobočiek`, `Zisk/strata podľa pobočiek`) with no
  English remaining, the Slovak `Pobočky` Help section, and all five
  `deploy_smoke.sh --https` checks.
- **Still no superuser on this app** (finding 12). Nothing in the demo needs
  one; `/admin/` stays unreachable until `ensure_superuser` is run by hand.
- Rollback target: `jober-platform:demo-3490f5d`.

## 2026-07-26 - Slovak i18n fix redeployed to jober-staging (demo language)

- Deployed **`3490f5d`** to `jober-staging` as `jober-platform:demo-3490f5d`
  (458 MB, `sha256:82d81475...`), built locally from pinned dependencies with
  the Node-artifact and vendor-asset checks green, then streamed with
  `git:load-image`. No VPS-side build, no build-time secrets. `migrate --check`
  reported nothing pending - this release changes templates and catalogs only.
- **Why it was needed:** the finance page a CEO is shown was rendering two
  headings in English inside an otherwise Slovak UI. Found by requesting the
  real `/sk/finance/` page on this app as the real demo accounts, not by
  reading the catalog - the entries existed but were *fuzzy*, and `msgfmt`
  compiles fuzzy entries away silently.
- Verified after the deploy, again by rendering rather than by inspecting
  files: the Observer's finance page now reads **`Mesačný trend podľa
  pobočiek`** and **`Zisk/strata podľa pobočiek`**, and a scan for the four
  previously-English office strings returns none. The Slovak `Pobočky` section
  of the Getting started Help article is live with its scoping paragraph.
- Re-confirmed the office boundary survived the redeploy: manager and
  coordinator badges read `Velký Meder`, Observer's reads `All offices`;
  5 of 7 people and 2 of 6 projects for the scoped roles against 7 and 6 for
  Observer; the Győr project returns 403 and 200 respectively. Data untouched
  (this deploy carried no migration or seed).
- `scripts/deploy_smoke.sh <url> --https` passed all five checks: healthz,
  login + CSRF, fingerprinted static CSS, X-Frame-Options, HSTS.
- `jober-platform:demo-d5b103d` remains the immediate rollback target via
  `git:from-image`.

## 2026-07-26 - ADR 0026 Phase B (office scoping) deployed to jober-staging, with a full database reset

- Deployed application revision **`d5b103d`** to `jober-staging` as
  `jober-platform:demo-d5b103d` (digest
  `sha256:26233d14…`, 458 MB). Built locally from pinned dependencies with
  `scripts/check_no_node_artifacts.py` and `scripts/verify_vendor_assets.py`
  green, then streamed with `git:load-image` — no VPS-side source build and
  no build-time secret access. CorvinumEU was **not** redeployed; this
  release is Jober demo preparation.
- Three new migrations applied cleanly: `people.0006_person_office`,
  `logistics.0010_accommodation_office`, and
  `logistics.0011_equipmentstockallocation_office_and_more`.
- **The staging database was dropped and rebuilt from scratch**, not merely
  reseeded. Re-running the (idempotent, repair-carrying) seeds over the
  existing database left pre-Phase-B residue that seeds cannot retract,
  because *seeds add and repair rows; they do not delete rows nobody seeds
  any more*. Two symptoms proved it:
  - **Warehouse stock did not reconcile.** The unscoped total read 111 units
    / €1,980.50 while the three offices summed to 76 / €1,344. The gap was
    the original *pooled* goods receipt of 2026-06-27 (`receipt#1`, from
    before stock was split per office) — 4 lots, 4 allocations and 8
    movements, all `office = NULL`, plus five issue/return movements made by
    hand during earlier live demo sessions.
  - **Five hand-created people** (Ilona Illés, Magdaléna Folker, Pista Tóth,
    Roger Folker, Teszt Személy) had no office. Scoping handled them exactly
    as ADR 0026 specifies — office-less people are visible to their owning
    recruiter — but that owner was `manazer@`, so the demo manager's People
    list showed 10 rows where the runbook scripts 5.
  The reset procedure: `postgres:export pg-jober-staging` to a local dump
  first (reversible), then `DROP SCHEMA public CASCADE; CREATE SCHEMA public`
  through the app container's Django connection, `migrate`, then all six
  seeds (`seed_demo seed_people seed_logistics seed_questionnaire
  seed_finance seed_demo_scenario`).
- Post-reset state: **7 people, every one with an office** and zero
  office-less; 6 projects, two per office; **54 financial months** (12 in
  2025 Nov–Dec, 42 across 2026 YTD) reading €90,890 revenue / €19,370 net
  for 2025 against €368,180 / €88,970 for 2026; and warehouse stock that
  reconciles exactly — 36 (VM) + 23 (GYR) + 14 (DS) = 73 units,
  €623.50 + €406.00 + €252.00 = €1,281.50, with **zero** orphan movements,
  lots or allocations.
- **Office scoping verified on staging itself**, with the real demo
  accounts rather than locally: `manazer@` and `koordinator@` badges read
  `Velký Meder` and Observer's reads `All offices`; manager and coordinator
  each see 5 of 7 people and 2 of 6 projects while Observer sees 7 and 6;
  the Győr project detail returns **403** for manager and coordinator and
  **200** for Observer, who also gets the executive finance dashboard.
- Verification gotcha worth keeping: the production settings set
  `SECURE_PROXY_SSL_HEADER`, so a Django test `Client` used against staging
  needs `HTTP_X_FORWARDED_PROTO="https"` and not merely `secure=True`, or
  every request answers 301. Also, `dokku run` does not forward stdin, so
  scripts must be passed inline (base64 + `exec`) rather than piped into
  `manage.py shell`.

## 2026-07-24 - Avatars, certificates, pill system, feedback flyer, Help area deployed (both apps)

- Merged PR **#89** and deployed application revision **`43da54c`** to
  `jober-staging` and `corvinum-staging` as the shared image
  `jober-platform:demo-43da54c` (digest
  `sha256:5a707691a08fc15ad38a4402320f0abb31f4093a49b145ab2ea25198d9b9ea1a`).
  The image was built locally from pinned dependencies (including the new
  Pillow and fpdf2/fonttools/defusedxml runtime deps, ADRs 0027/0028) with
  vendored assets verified (`scripts/verify_vendor_assets.py`, including the
  new DejaVu Sans font and the regenerated CorvinumEU Material Symbols
  subset), then streamed with `git:load-image`; no VPS-side source build or
  build-time secret access occurred.
- Both apps applied the same six new migrations cleanly (`offices.0001_initial`,
  `accounts.0003_user_offices`, `accounts.0004_user_avatar`,
  `compliance.0002_certificate_category_certificate_document`,
  `people.0005_person_avatar`, `projects.0006_remove_project_region_alter_project_office`).
  Notably, only `offices.0001_initial` (schema) ran against CorvinumEU's
  database, not a seed-data migration — confirming in production-like
  conditions the mid-session fix that keeps Jober-specific office names out
  of CorvinumEU's database (the seed data lives only in
  `clients/jober/demo/management/commands/seed_people.py`, a Jober-only
  management command, never in a migration).
- Re-ran two idempotent seeds on `jober-staging` only, matching this
  release's actual content: `seed_people` (creates the 3 real offices this
  release's RBAC foundation depends on) and `seed_demo_scenario` (adds
  Mira Novakova's expired Health certificate, so the new certificate-
  validity icons have a second category/severity to show in the demo, not
  just Olha's pre-existing forklift one). No CorvinumEU reseed — this
  release doesn't touch CorvinumEU's seed data.
- Both Dokku processes passed `ps:report` (running) and
  `scripts/deploy_smoke.sh --https` (healthz, login page + CSRF,
  fingerprinted static CSS, X-Frame-Options, HSTS) — verified independently
  from both the agent session and the owner's own terminal.
- The prior shared image `jober-platform:demo-b9d0fb1` remains the immediate
  rollback target for both apps via `git:from-image`. The known Dokku
  default-bridge deprecation warning remains non-blocking host maintenance.

## 2026-07-23 - Reconciled demo backlog deployed (both apps)

- Merged PR **#87** and deployed application revision **`b9d0fb1`** to
  `jober-staging` and `corvinum-staging` as the shared image
  `jober-platform:demo-b9d0fb1` (digest
  `sha256:2ab3f1deea0e49cc19aa6fd90ae551f19105fdd7b2f19ba4bb3486f8dbdb1051`).
  The image was built locally from pinned dependencies and verified vendored
  assets, then streamed with `git:load-image`; no VPS-side source build or
  build-time secret access occurred.
- Both databases reported no pending migrations and both Django system checks
  passed. Refreshed only CorvinumEU's idempotent fictional seed because this
  release makes its Thursday-summary cutoff fixture deterministic; existing
  Jober staging data was preserved.
- Runtime assertions confirmed Jober profitability, feedback, equipment stock,
  and the fingerprinted Chart.js asset are active while transport and the wage
  ledger remain off. CorvinumEU retains payslips, advances, and wage ledger,
  keeps profitability/feedback/transport off, and loads the Hungarian
  `Bérlapok` payslip label.
- Both Dokku processes passed replacement-container uptime and port checks.
  The full HTTPS smoke suite passed health, login/CSRF, fingerprinted static
  CSS, X-Frame-Options, and HSTS for both public staging URLs.
- The known Dokku default-bridge deprecation warning remains non-blocking host
  maintenance. The prior shared image `jober-platform:demo-c6d5785` remains
  the immediate rollback target for both apps.

## 2026-07-21 - Hungarian catalog fuzzy-match cleanup deployed (both apps)

- Merged PR **#85** and deployed application revision **`c6d5785`** to both
  `corvinum-staging` and `jober-staging` as the shared image
  `jober-platform:demo-c6d5785`, streamed via `git:load-image` (no VPS-side
  build, no secrets in the image). Deployed to both apps since the fix
  touches `features/logistics`/`core/people` (shared by both clients), not
  just the CorvinumEU-only checklist/advances panel help text.
- `corvinum-staging`: `migrate --noinput` reported no pending migrations.
  `jober-staging`: applied `payslips.0002_payslip_issue_date`, which had not
  yet landed there from an earlier Corvinum-only release — additive,
  non-destructive, no data affected.
- Both Dokku containers passed `ps:report` (running) and `/healthz/` (200).
  The full HTTPS smoke suite (`scripts/deploy_smoke.sh --https`) passed for
  both: healthz, login page + CSRF, fingerprinted static CSS,
  X-Frame-Options, HSTS.
- Manually confirmed the Hungarian catalog loads cleanly on both live apps
  post-recompile: `/hu/` renders `Bejelentkezés · CorvinumEU PeopleOps` and
  `Bejelentkezés · Jober` respectively at HTTP 200 with a valid CSRF token —
  no corruption from the 47 hand-edited `.po` entries.
- No reseed run (translation/help-text content change only, no new seed
  data). Previous image tags (`jober-platform:corvinum-demo-819f28b` and
  `jober-platform:jober-demo-64d30ac`) remain the rollback targets for their
  respective apps via `git:from-image`.

## 2026-07-21 - Corvinum ledger panel-order correction deployed

- Merged corrective PR **#83** and deployed application revision **`819f28b`**
  to `corvinum-staging` as `jober-platform:corvinum-demo-819f28b` (local image
  digest
  `sha256:23eba197426d31cf351bfaad6d9b8feac950f8268ed3749483937c8318472477`).
- This template-only replacement puts the compact Cycle card beside Record
  entry and the larger Thursday summary + Entries card full-width below. No
  migration or seed refresh was required; `migrate --check` passed.
- Dokku uptime and port checks passed. A runtime template assertion confirmed
  Cycle precedes Activity and the activity partial still contains both summary
  and Entries. Public HTTPS health, login/secure CSRF, fingerprinted CSS,
  X-Frame-Options, and HSTS checks passed. Logs contain normal Gunicorn startup
  output only.
- The previous `corvinum-demo-07cd2a1` image remains the immediate rollback
  target. The known Dokku default-bridge warning remains non-blocking host
  maintenance.

## 2026-07-21 - Corvinum payslip-date and ledger-layout release

- Merged PR **#81** and deployed application revision **`07cd2a1`** to the
  isolated `corvinum-staging` app as
  `jober-platform:corvinum-demo-07cd2a1` (local image digest
  `sha256:5fa5853360ef639c7c76aa3a73fc7820db845e5d930cc150f65549d6a23f6b48`).
  The production image was built locally without runtime credentials and
  streamed directly to Dokku; the VPS did not build application source.
- Dokku's replacement container passed uptime and port-8000 checks. Applied
  `payslips.0002_payslip_issue_date`, ran Django's system check, and refreshed
  the idempotent fictional Corvinum seed so Eszter's June/July issue-date
  fixtures are `2026-07-05` and `2026-07-20`.
- Runtime assertions confirmed payslips and advances remain ON, transport
  remains OFF, and both the payslip and ledger routes resolve. The deployed
  release adds optional payslip issue dates and the compact ledger workspace;
  it does not change PDF content or ledger calculations.
- The public HTTPS smoke suite passed health, login/secure CSRF, fingerprinted
  CSS, X-Frame-Options, and HSTS at
  `https://corvinum-staging.80.211.210.46.sslip.io`. Application logs contain
  only normal Gunicorn startup output. The known Dokku default-bridge
  deprecation warning remains non-blocking host maintenance.

## 2026-07-21 - Latest Jober thin client deployed

- Deployed application revision **`64d30ac`** to the isolated
  `jober-staging` app as `jober-platform:jober-demo-64d30ac` (local image
  digest `sha256:8c680fbb48e50a265b9f8776f7abb9ac650d93902e20ae7a427eafe3dde73c8a`).
  The image was built locally without runtime credentials and streamed directly
  to Dokku; the VPS did not build application source.
- Dokku's replacement container passed uptime and port-8000 checks. Jober's
  migration set was already current and `manage.py check` reported no issues.
  Existing fictional staging records were preserved; no routine reseed ran.
- Runtime assertions confirmed the Jober boundary: transport OFF,
  profitability and warehouse stock ON, and the Corvinum-only wage ledger both
  uninstalled and unrouted.
- The public HTTPS smoke suite passed health, login/secure CSRF, fingerprinted
  CSS, X-Frame-Options, and HSTS at
  `https://jober-staging.80.211.210.46.sslip.io`. The known Dokku
  default-bridge deprecation warning remains non-blocking host maintenance.

## 2026-07-20 - Corvinum wage release staging-data reconciliation

- The first PR #77 staging release applied `wage_ledger.0001` and passed the
  public HTTPS smoke suite, but acceptance found Marek's existing, sent
  `2026-07` fictional payslip from an earlier manual rehearsal. The idempotent
  seed correctly did not overwrite or delete that audited record.
- Moved the deterministic wage-versus-payslip checkpoint to fictional candidate
  Eszter Varga. Marek remains the encrypted-delivery example; no historical
  payslip, delivery timestamp, recipient, or audit event was changed.
- Merged the correction as PR **#78** and deployed application revision
  **`67bcfae`** to `corvinum-staging` as
  `jober-platform:corvinum-demo-67bcfae` (local image digest
  `sha256:ea8eed4632886882c4b62a5beeba2250032ebf84ff4aea0014cb92982b136a3a`).
- Dokku's replacement container passed uptime and port-8000 checks. Migrations
  are current, the idempotent fictional seed completed, and a read-only runtime
  assertion confirmed Eszter's exact source rows: June `1920.00 / 1450.00 EUR`
  and July `2050.00 / 1540.00 EUR`; wage ledger and payslips are ON while
  Corvinum transport remains OFF.
- The public HTTPS smoke suite passed health, login/secure CSRF, fingerprinted
  CSS, X-Frame-Options, and HSTS. The app remains available at
  `https://corvinum-staging.80.211.210.46.sslip.io`. The known Dokku
  default-bridge deprecation warning remains non-blocking host maintenance.

## 2026-07-20 — Jober amendments and latest Corvinum demo deployed

- Merged PR **#73** (shared platform/Corvinum work) and PR **#75** (Jober
  interview amendments) into `main`; the deployed application revision is
  **`cd28ac8`**.
- Built the npm-free production image locally without runtime credentials and
  streamed the same tag, **`jober-platform:demo-cd28ac8`** (local image digest
  `sha256:dbfc9c29680e929a76ce42b6e8e66efa863a2a23f246a879f5feba1607126198`),
  to both `jober-staging` and `corvinum-staging` on syncmetric-prime.
- Both Dokku replacement containers passed their uptime and port checks. Applied
  migrations through `projects.0005` and `logistics.0009`; `migrate --check`
  then passed for both isolated databases.
- Refreshed only fictional, idempotent demo data. Jober received the updated
  warehouse stock, accommodation-cost, regional-finance, and age-warning
  scenario; Corvinum retained its separate intake, checklist, equipment, and
  worker-ledger scenario.
- Runtime policy checks confirmed Jober transport OFF with profitability and
  warehouse stock ON, and Corvinum transport, profitability, and warehouse
  stock OFF. The public HTTPS smoke suite passed health, login/CSRF,
  fingerprinted static assets, X-Frame-Options, and HSTS for both apps.
- Public demos: `https://jober-staging.80.211.210.46.sslip.io` and
  `https://corvinum-staging.80.211.210.46.sslip.io`. The known Dokku
  default-bridge deprecation warning remains host maintenance; it did not
  affect either release.

## 2026-07-16 — Corvinum checklist in-place update deployed

- Built committed revision **`6abdb56`** in a detached clean worktree without
  runtime credentials and streamed
  `jober-platform:corvinum-demo-6abdb56` directly to the isolated
  `corvinum-staging` Dokku app.
- Dokku's replacement container passed its uptime and port-8000 checks before
  replacing the prior web process. The existing PostgreSQL service and
  fictional staging data were preserved; no reseeding was performed.
- The idempotent migration step reported no migrations to apply. Public HTTPS
  acceptance passed for `/healthz/`, the Slovak login page, and the compiled
  CSS asset.
- This release changes activation-checklist toggles to an in-place htmx panel
  refresh, preserving the user's URL and scroll position while retaining the
  full-page POST/redirect fallback.
- The known Dokku default-bridge deprecation warning remains tracked as host
  maintenance and did not affect the release.

## 2026-07-16 — Jober public fictional-data staging and Twilio configuration

- Deployed the committed release **`12d0735`** to the isolated Dokku app
  **`jober-staging`** on **syncmetric-prime**, with its separate
  `pg-jober-staging` PostgreSQL service, Jober settings module, temporary
  HTTPS hostname, and fictional-only seed data. Django checks and migrations
  completed cleanly; the public health endpoint returned `ok` after restart.
- Created the separate read-only Doppler scope `hr_system/stg_jober-staging`
  and synchronized exactly the four approved Jober SMS runtime keys:
  `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`, and
  `DEMO_SMS_PHONE`. Jober email remains intentionally deferred for this demo.
  No Doppler token, provider credential, sender, or recipient value is
  recorded here.
- Initial SMS troubleshooting confirmed that Twilio error **21266** means the
  configured recipient matched the configured sender. This is a provider
  safety rule, not a Dokku, CSRF, or application error. The controlled demo
  recipient must be a distinct, approved SMS-capable/verified number; do not
  use `TWILIO_FROM_NUMBER` as `DEMO_SMS_PHONE`.
- Before presenting SMS, send one harmless controlled test message and confirm
  delivery in Twilio. Configure and test the signed inbound webhook only after
  that outbound check succeeds.

## 2026-07-15 — CorvinumEU public fictional-data staging demo deployed

- Deployed the committed release **`12d0735`** (`jober-platform:corvinum-demo-12d0735`)
  to the isolated Dokku app **`corvinum-staging`** on
  **syncmetric-prime** (Dokku 0.38.23). The public temporary demo URL is
  `https://corvinum-staging.80.211.210.46.sslip.io/sk/prihlasenie/`; it is not
  a production CorvinumEU domain.
- The app uses `clients.corvinum_eu.production`, the separate linked PostgreSQL
  service `pg-corvinum-staging`, and the existing explicit `http:80:8000` port
  mapping. The image was built locally without secrets and streamed directly to
  Dokku with `git:load-image`; no source checkout or application build ran on
  the VPS.
- Applied migrations and seeded only the published **Recruiter intake v3** and
  the fictional CorvinumEU scenario. The four `@demo.corvinum.test` accounts,
  projects, checklist, equipment/ledger records, and questionnaire are staging
  demonstration data only.
- Verified externally: HTTPS login route returns 200 with a Secure Corvinum
  CSRF cookie; `/sk/` correctly redirects unauthenticated visitors to login;
  CSS returns `200 text/css`; and Gunicorn is running on port 8000 without
  application errors in the Dokku log.
- Created a Doppler **read-only, config-scoped service token**, synchronized
  only the seven `DJANGO_EMAIL_*` values into this Dokku app, and completed one
  controlled fictional payslip-email test successfully. The encrypted PDF
  reached the controlled test inbox; no recipient address, SMTP credential,
  one-time PDF password, or token value is recorded here. No real recipient or
  real personal data is authorized.
- The Dokku default-bridge-network deprecation warning is recorded as post-demo
  host maintenance; it did not affect this deployment. Revoke or replace the
  staging service token after the demo according to the retention decision.
- Documented the repeatable image-stream release and rollback procedure for
  `corvinum-staging`, plus the planned isolated `jober-staging` app/database,
  hostname, provider boundary, fictional seeding, and acceptance checks on the
  same Dokku host. Jober has not yet been created or deployed there.
- Clarified the Jober-specific staging sheet: `config.settings.production`
  selects Jober, while a separately scoped `TWILIO_*` configuration enables
  only its controlled SMS demonstration. Corvinum's SMTP configuration and
  service token must not be reused.
- Documented Jober's exact staging release boundary: derive explicit `DB_*`
  values from the linked service without recording them, run migrations and
  `ensure_superuser` after an image deployment, and use the repository's real
  fictional seed sequence only for a deliberate reset. Same-origin HTTPS does
  not require an unused `DJANGO_CSRF_TRUSTED_ORIGINS` setting in this codebase.

## 2026-07-15 — CorvinumEU recruitment trials enabled

- Enabled the shared recruitment-trial feature for CorvinumEU’s demo. Recruiters,
  coordinators, and managers may schedule a trial; coordinators and managers
  may record its outcome. Observers remain read-only.
- Added Trial day transitions to Corvinum’s client policy and updated the
  client-demo walkthrough to show scheduling, outcome, and the subsequent
  readiness/checklist gate.

## 2026-07-15 — Corvinum blacklist archive and re-entry demo

- Added a manager-only operational archive action. It is explicitly not GDPR
  erasure: it hides the original record from the People list while retaining
  its blacklist case, active HMAC fingerprint, and audit history.
- The guided intake now accepts a transient blacklist identifier and type on
  its final panel. The raw identifier is validated and matched but never
  persisted as an intake answer. A match creates a new proposed case for
  manager review and blocks activation; it never merges or auto-blacklists.
- The Corvinum runbook now contains the full fictional propose → approve →
  archive → re-enter → manager-decision scenario.

## 2026-07-15 — CorvinumEU cost-conscious production operating model

- Recorded the owner decision for a low-traffic **FORPSI Basic** production
  VPS (2 vCPU / 4 GB / 40 GB NVMe), with `corvinum-staging` stopped except for
  rehearsals, deployment checks, and restore drills. Standard is the defined
  upgrade path for continuous staging, resource pressure/OOMs, recurring swap,
  or a restore that exceeds four business hours.
- Added `docs/deployment/corvinum-basic-production.md`: provider choices,
  external DPA and data-location gates, encrypted off-site retention, disk
  thresholds, website Supabase backup boundary, and a restricted monthly
  restore procedure.
- Added deployment-host scripts for an encrypted PostgreSQL/release-manifest
  backup, backup-age/capacity monitoring, and explicit staging start/stop.
  The scripts retain 35 daily and 12 monthly archives, fail at 26-hour backup
  age or 60% target use, and intentionally never export Doppler/Dokku config.
- Still owner-controlled and not claimed complete: VPS orders, DPA signatures,
  SSH/firewall/DNS setup, GPG recovery-key custody, monitoring delivery, and
  least-privilege Supabase database/private-bucket export automation.

## 2026-07-15 — Corvinum intake seed correction

- Corvinum local and fictional staging bootstrap instructions now seed the
  published personnel-intake questionnaire before the client scenario. Clean
  resets no longer leave the visible **Add person** action without a usable
  questionnaire.
- Production remains unaffected: demo seeds must never run against a real-data
  environment.

## 2026-07-15 — Corvinum client-demo rehearsal runbook

- Refreshed `docs/deployment/corvinum-demo-runbook.md` into a rehearsal-safe
  20–25 minute walkthrough with a ten-minute fallback route, exact demo
  accounts, presenter checkpoints, recovery steps, and a clean disposable-DB
  reset between practice and the client call.
- Corrected the demonstrated scope to match Corvinum's active feature flags:
  recruitment trials, accommodation, transport, profitability, messaging, and
  feedback are not mounted in this thin client.
- Corrected the local payslip demonstration: the console backend proves the
  fictional recipient and attachment output but is not a clickable mailbox;
  real provider-backed testing remains Doppler-injected.

## 2026-07-14 — Operations workspace migration

- Deploy includes logistics migration `0008_room_is_active_and_unique_label`.
  It adds an active flag to rooms and enforces unique room labels within each
  accommodation. Existing rooms default active; no record is deleted.
- Run the normal migration step before serving the new accommodation forms.
  The production image remains npm-free and contains no new runtime dependency.

## 2026-07-12 (later)

Staging deploy target chosen and runbook written.

- **Target: syncmetric-prime** — fresh VPS, Dokku to be installed. Scope: **staging only, both clients** on fictional data (`jober-staging`, `corvinum-staging`) under **per-client subdomains of one parent domain**. Execution: owner runs commands, I guide.
- **`docs/deployment/syncmetric-prime-staging.md`** written — concrete phased command sequence (assess/DNS → pinned no-pipe-to-shell Dokku install → build+`docker save|ssh load` transfer → per-app create/config/TLS → migrate+seed → `deploy_smoke.sh --https` verify → backups). Honors AGENTS §3.4 (download+checksum+review the Dokku bootstrap, never `wget|bash`).
- Asks updated: D1 names the box; D2/D3 record the subdomain choice. Production apps + real PII remain gated on D8.

## 2026-07-12

Release tooling landed (production-readiness §2 complete).

- **`scripts/deploy_smoke.sh <url> [--https]`** — post-deploy gate: healthz, login+CSRF, fingerprinted static with immutable caching, X-Frame-Options; with `--https` also HSTS + Secure cookies. Passed against both local stacks.
- **`scripts/backup_restore_drill.sh`** — dump → scratch restore → exact per-table row-count comparison. First drills PASSED: jober (47 tables/395 rows), corvinum (39 tables/298 rows). Dumps kept under `backups/` (gitignored); off-site copy pends D6.
- Also landed this cycle: console error logging (`django.request` → container logs), the corvinum-flags test lane (`scripts/test_corvinum.sh`). Remaining before staging: owner asks D1–D4.

## 2026-07-11

Deployment architecture decided and documented.

- **Owner decision:** Dokku on the existing VPS; four apps (`jober[-staging]`, `corvinum[-staging]`) from the **same image tag**, `DJANGO_SETTINGS_MODULE` selects the client; per-app Postgres/domain/Let's Encrypt/secrets/backups. Full plan + one-time setup commands + rollout order: `docs/deployment/deployment-plan.md`.
- **Execution blocked on asks D1–D8** (SSH/hostname, four domains, Doppler tokens, SMTP for payslips, backup target, Twilio upgrade, legal gates). Staging is one working session once D1–D4 land.
- Guardrails restated: production never runs demo seeds; fictional data only until each client's legal gate; secrets Doppler → `dokku config:set`, never git.

## 2026-06-29

Secrets + Twilio SMS go-live readiness.

- **Secrets via Doppler.** Project `hr_system`, config `dev` holds the Twilio creds. Local runs use `doppler run -- scripts/dev_app.sh up` (dev_app forwards `TWILIO_*` into the container; committed `doppler.yaml` selects the project/config). No secrets in git. See `docs/deployment/twilio-setup.md`.
- **Twilio SMS verified live** end-to-end through the app: live SID/token + a trial number delivered to the Twilio Virtual Phone (`Delivered` in Messaging Logs). Test-credential magic-number path also verified.
- New deploy-time env vars: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` (from Doppler/secret store, never the repo).
- **Remaining for SMS prod:** upgrade the Twilio account (removes the trial prefix; allows arbitrary recipients), and configure the inbound webhook (`/webhooks/twilio/inbound/`) once a public HTTPS host exists (Dokku staging or a tunnel). For Dokku, inject Doppler secrets via sync (`doppler secrets download … | dokku config:set`) or a service token (`doppler run -- gunicorn …`).

## 2026-06-21

Phase 1 deployment-relevant changes.

- **Static serving fixed (production-readiness).** The production image runs gunicorn, which does not serve static files; nothing else did either, so all `/static/...` assets returned the HTML 404 page (`text/html`) and the shell rendered unstyled. Adopted WhiteNoise (ADR 0016): middleware + `CompressedManifestStaticFilesStorage` in production settings only; hash-pinned in `runtime.lock`/`test.lock`. Verified the live image serves `app.css` as `200 text/css` with a fingerprinted URL. A Playwright regression now guards it. See `docs/deployment/production-readiness.md`.
- **Deploy steps now include migrations:** `accounts` and `audit` initial migrations must run on deploy (custom `AUTH_USER_MODEL`).
- **New deploy-time env vars:** `JOBER_BROAD_INTERNAL_READS` (default on), and `DJANGO_SESSION_COOKIE_SECURE` / `DJANGO_CSRF_COOKIE_SECURE` (default **secure**). The `=0` overrides exist only for the HTTP-only smoke network and must never be set on staging/production.
- **No production superuser path yet** — `seed_demo` creates fictional users for local/staging only and must not run against a real-data DB. A `createsuperuser` (custom email user) step is required before go-live.

Correction to the 2026-06-17 entry below: its "Current blocker" (Python lock + digest-pinned base images) was **resolved later in Phase 0** — `Dockerfile`, hash-pinned `runtime.lock`/`test.lock`, and digest-pinned Python/PostgreSQL/Playwright images all landed and the image builds/migrates/serves. The remaining deployment blocker is Dokku staging, pending external app/domain/PostgreSQL service names.

## 2026-06-17

Phase 0 production deployment direction:
- The static demo deployment notes below are historical and apply only to the old design reference.
- Production target is a Jober-only Django app deployed to Dokku with PostgreSQL.
- Added `docs/deployment/dokku-staging.md` as the staging shell/runbook.
- No Dockerfile was added yet because `AGENTS.md` requires base images pinned by digest, and those digests have not been resolved from a trusted source.
- No Tailwind binary was added; `vendor/tailwind/REQUEST.md` records the human-supplied artifact and checksum requirement.
- No Python dependency install was run on the host.

Current blocker:
- Generate the hash-pinned Python dependency lock and choose digest-pinned base images inside an approved container/CI path before staging can run.

## 2026-06-13

Current deployment method:
- Static files only.
- Primary previews:
  - Internal combined build: open `demo/internal/index.html`.
  - CorvinumEU client build: open `demo/corvinum/index.html`.
  - Jober client build: open `demo/jober/index.html`.
- Optional local server: run `python3 -m http.server` from `demo/`, then open:
  - `http://127.0.0.1:8000/internal/`
  - `http://127.0.0.1:8000/corvinum/`
  - `http://127.0.0.1:8000/jober/`

Verified today:
- The demo is split into the three static build folders above.
- Browser verification is recorded in `test_journal.md`.

No deployment artifacts, backend service, package files, or build output are required.
