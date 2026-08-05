# Deployment Journal

## 2026-08-05 - Five slices: correction, consequence, and the medical

Deployed the exact `main` merge **`a91844d`** to `jober-staging` and
`corvinum-staging` as `jober-platform:demo-a91844d` (image ID
`sha256:aeb0e1528eec9e475209f394d7b6aa9ce19f6b9cd6f1a2f4538f863f0880a5e0`),
streamed with `git:load-image`. Staging had fallen five merges behind.

The release, in the order the work was asked for:

- **The ledger offered a reversal it would then refuse** (`108b70f`). The
  button showed on any locked entry without asking whether a reversal already
  existed, and neither side of a reversed pair was marked.
- **C-Q5 answered: an entry is deletable until the money is paid** (ADR 0033).
  Blanket immutability was rejected by the owner; the line is payment, not
  cycle inclusion. Deletion is audited with everything the row held, reversal
  stays for corrections after settlement, and a cycle closed by mistake can be
  reopened while its own window still runs — after that the refusal names the
  next run and its dates.
- **Buttons that reach outside the application look like it** (ADR 0034).
  Sixteen buttons across four families — money and sending, physical handover,
  a person has to be somewhere, paper in hand — carry an amber striped button,
  a fixed *Real-world action* tooltip heading, and a visible consequence line.
  The stripe is a shape, not only a colour, so it survives greyscale and colour
  vision deficiency.
- **The medical is a date, so the product now chases it.** A health badge
  synthesised from `entry_medical_date`, activation refused for a medical that
  has already expired (naming the date), and lapsed dates reported for anyone
  still on the books rather than only `WORKING` people.
- **Nine checkboxes, nine explanations.** Each activation checklist item says
  what its tick claims, headed by its own name, instead of one repeated
  sentence about how ticking works.

**One migration**, `checklists.0002_checklistitemtemplate_help_text` — an
additive blank `TextField`. Applied cleanly on both apps.

**The help text needed a separate step, and that is the interesting part of
this release.** The column ships empty; the words live in the seed. Both
staging databases already held all nine rows, so `get_or_create(defaults=…)`
would never have reached them — the same trap the code fix addresses. The
runbook forbids `seed_corvinum_demo` as a routine release action, so the repair
was applied surgically, importing `ACTIVATION_ITEMS` from the seed module so
the text is the source of truth rather than a retyped copy:

```
before: 9 items, 0 with help text
after:  9 items, 9 with help text
        Personal data complete | Name, date of birth, address and phone are all filled in, an…
```

Verified on the live apps rather than inferred from a green build:

```
corvinum-staging  delete_entry / reopen_cycle present:   True True
corvinum-staging  medical expiries computed:             5 ['2027-07-13', '2027-08-04', …]
corvinum-staging  compliance alerts:                     1 ['missing'] ['working']
jober-staging     compliance alerts:                     3 ['expired', 'expiring', 'missing']
both hosts        stylesheet app.5ecd259c7e2f.css serves
                  action-consequence, button-physical, confirm-physical
```

No lapsed medical exists on CorvinumEU staging today — every recorded date
expires in 2027 — so the widened alert scope changes nothing there yet, which
is the correct outcome rather than a missing one. Jober staging shows all three
severities, so the path is exercised.

Pre-deploy on `a91844d`: Jober **1120 passed / 19 skipped**, CorvinumEU
**721 passed / 23 skipped**, Playwright **70 passed**; `ruff check` clean and
`ruff format --check` clean across all 26 changed Python files since the last
release; `check_no_node_artifacts`, `verify_vendor_assets` and
`check_dependency_direction` all clean — the last one matters this time,
because `add_months` moved into `core/dates.py` so the activation gate and
compliance could share one definition of expiry.

Both `deploy_smoke.sh --https` runs passed health, login/CSRF, fingerprinted
static, X-Frame-Options and HSTS.

Rollback target:

```bash
ssh syncmetric-prime-dokku "git:from-image <app> jober-platform:demo-0cadfa3"
```

## 2026-08-05 - The medical renewal path and readable flash messages

Deployed the exact `main` merge **`0cadfa3`** to `jober-staging` and
`corvinum-staging` as `jober-platform:demo-0cadfa3` (image ID
`sha256:3c71c814f35d67f2928a22f877a4b54bbb1ac6f9c2b6ef79733ac25b717700c3`),
streamed with `git:load-image`.

Two reported problems:

- **A compliance alert that could not be cleared.** Activation checked the
  Medical pillar *state* while the alert reads the *date*, and nothing required
  them to agree. Marking Medical complete now requires the date, and a working
  person's profile carries a panel that records or renews it - the screen that
  never existed, and the reason `MEDICAL_VALIDITY_MONTHS = 12` was previously
  unservable for anyone already activated.
- **Flash messages ran for three seconds**, which is not long enough to read two
  lines. Now ten, with a dismiss button, and the timer holds while the pointer
  or keyboard focus is on the message. The markup moved out of both client
  shells into one partial.

**No migrations.** The migration diff since `73cdce7` is empty.

Verified on the live app rather than inferred:

```
person: Olena StagingDemo-1784572547 | lifecycle: working
medical panel URL: /sk/people/6/medical/
entry_medical_date now: None
open Medical alerts: 1
```

The route now exists for the worker whose alert prompted the change, and the
alert is still open - deliberately. It will be cleared **through the UI**, which
is the proof the fix works; setting the date directly in the database would only
have proved the database accepts dates. Both hosts serve
`app.3bbf7c7f0f3c.css`.

Pre-deploy suites on `0cadfa3`: Jober **1083 passed / 16 skipped**, CorvinumEU
**671 passed / 23 skipped**, Playwright **70 passed**; ruff check and
`ruff format --check` clean. `test_themes` cross-tab sync failed once on the
first browser run and passed 3/3 in isolation plus a clean full rerun - the same
storage-event race seen on 2026-08-04, not a regression. Both
`deploy_smoke.sh --https` runs passed, and `migrate --check` exits 0 on both.

Rollback target:

```bash
ssh syncmetric-prime-dokku "git:from-image <app> jober-platform:demo-73cdce7"
```


## 2026-08-05 - Carry-forward, the upload guard and the equipment unblock

Deployed the exact `main` merge **`73cdce7`** to `jober-staging` and
`corvinum-staging` as `jober-platform:demo-73cdce7` (image ID
`sha256:8b92f2f90ff3caa0c85610db4cfd9ba7f45c8bb4ab98cfac1c43ae4bc4e937c0`),
streamed with `git:load-image`. Staging had fallen three fixes behind.

The release carries, in the order they were reported:

- **The certificate upload could be submitted twice** and `Certificate` has no
  uniqueness constraint, so the second press created a second row. Measured:
  2 create requests before the guard, 1 after.
- **The settled-cycle refusal blocked equipment issuing.** Equipment charges
  reach the ledger with no date and default to today, so once the current run
  was closed nothing could be issued. Withdrawn entirely, not narrowed.
- **An advance given in July was never recovered from the August salary** - and
  never recovered at all, because the sweep windows are disjoint. A run now
  collects everything outstanding at its cutoff (ADR 0032).

**No migrations.** The migration diff since the previously deployed `ca94dc4`
and `29f5984` is empty; this release is application logic, one stylesheet rule,
a template and translations.

**Behaviour verified on the live app, not inferred from a green build.** Read
from `corvinum-staging` after release:

```
carry-forward code live: True
next run: 2026-08   closed already? True
a 25 July advance would be collected by: 2026-09
still outstanding: 4
```

That last line is the reported bug answered correctly in production shape: a
July advance whose August run has gone out is now collected by September rather
than never.

**The catch-up was forecast before shipping**, because carry-forward sweeps
historical strays by design. Four outstanding entries on CorvinumEU, all dated
2026-08-04, all pay additions - the reversals created while testing Sztornó. No
surprise deduction was waiting for anyone, which is why this was safe to deploy
without a data migration or a cut-off date.

Pre-deploy suites on `73cdce7`: Jober **1076 passed / 16 skipped**, CorvinumEU
**665 passed / 23 skipped**, Playwright **70 passed**; ruff check and
`ruff format --check` clean. Both `deploy_smoke.sh --https` runs passed health,
login/CSRF, fingerprinted static, X-Frame-Options and HSTS.

Rollback target is the previous shared image:

```bash
ssh syncmetric-prime-dokku "git:from-image <app> jober-platform:demo-29f5984"
```


## 2026-08-04 - Card layout and the worker-rail gutter deployed to both clients

Deployed the exact `main` merge **`29f5984`** to `jober-staging` and
`corvinum-staging` as `jober-platform:demo-29f5984` (image ID
`sha256:f31b8267f8980fef6b9e60ab8ed7d78e126c9af49261ec188444d0079761b018`),
streamed with `git:load-image`. Second release today, after `ca94dc4`.

Two layout fixes, both in the shared stylesheet, so both clients get them:

- **Decision cards** no longer squeeze their own form. Measured before and
  after on the activation queue: the reason input went from **99px to 320px**
  at 1280px. Seven templates gave the two-column `.field-card` three children;
  one `:nth-child(n+3)` rule spans the third across both columns.
- **The worker status rail** no longer reserves its 20rem gutter on a phone.
  Reported as a ledger heading wrapping one character per line; measured from
  the reporter's browser as `.cv-main` computing `padding-right: 320px` at a
  375px viewport, leaving a **39px content box**. The `max-width: 1100px`
  release never worked because `:has()` carries its argument's specificity and
  media queries add none. Now scoped with `min-width: 1101px`.

**No migrations.** The migration diff since `ca94dc4` is empty; this release is
CSS, three template class attributes, and tests.

Verified on the live hosts rather than assumed: both serve
`app.1b7a2ad4f58d.css`, which contains `min-width:1101px` and
`field-card-decision`, and no longer contains the ineffective
`max-width:1100px` release. Both `deploy_smoke.sh --https` runs passed health,
login/CSRF, fingerprinted static, X-Frame-Options and HSTS.

Pre-deploy suites on `29f5984`: Jober **1076 passed / 16 skipped**, CorvinumEU
**658 passed / 23 skipped**, Playwright **68 passed**; ruff check and
`ruff format --check` clean.

Both new browser tests were confirmed to fail without their fix - 99px for the
card, and `padding-right: 320px` with a 39px content box for the rail - because
a layout test that has never failed is not measuring anything. The rail one has
to **expand the rail first**: it ships collapsed, every previous responsive test
left it collapsed, and the bug only exists while it is open.

Rollback target is the previous shared image:

```bash
ssh syncmetric-prime-dokku "git:from-image <app> jober-platform:demo-ca94dc4"
```


## 2026-08-04 - CorvinumEU pre-demo batch deployed to both staging clients

Deployed the exact `main` merge **`ca94dc4`** to `jober-staging` and
`corvinum-staging` as the shared image `jober-platform:demo-ca94dc4` (local
image ID
`sha256:186ff753417e10665910cdbd96798789dab5b2b9ee2bea3d11cacb2fce5eb08f`),
streamed with `git:load-image`. No VPS-side source build, no build-time
secrets.

The release carries the ten-item CorvinumEU pre-demo batch: the ledger
deduction column and derived **After deductions** total on the pay overview,
an entry date on the ledger form with a settled-cycle guard, month pickers for
payslip and wage periods, Audit and Staff activity narrowed to the Observer,
the office picker removed where no offices exist, bounded date inputs in both
clients, tooltips on money and approval controls, and a per-field reference in
Help. Documentation-only additions: C-Q20, C-Q21 and
`docs/unreviewed-branches.md`.

**No migrations.** `git diff 742f4f2..ca94dc4 -- '*/migrations/*.py'` is empty
and `migrate --check` exits 0 on both apps, so this release changed no schema
and needed no database work. Recorded because it is the reason the deploy
carried unusually little risk, not because nothing was checked.

**Cross-client isolation verified by query, not by inference.** Read from each
running app rather than trusted from the test suite:

| Check | jober-staging | corvinum-staging |
|---|---|---|
| `audit.view` | Manager + Observer | **Observer only** |
| `staff_activity.view` | Manager + Observer | **Observer only** |
| `activation.waive_trial` | Manager | Manager |
| `Office` rows | 3 | **0** (so the picker is absent) |

The office behaviour is data-driven, so the two answers above come from the
same code path reading different data — which is the property worth confirming
on real databases.

Both `deploy_smoke.sh --https` runs passed health, login/CSRF, fingerprinted
static (`app.549ea0e7ad7e.css`), X-Frame-Options and HSTS. `check --deploy`
exits 0 on both, the last 40 log lines of each app contain no traceback or
error, and `/sk/wages/`, `/sk/ledger/`, `/sk/payslips/` and Jober's
`/sk/finance/` all redirect to login while anonymous.

**Pre-deploy suites, all on `ca94dc4`:** Jober **1076 passed / 16 skipped**,
CorvinumEU **658 passed / 23 skipped / 261 deselected**, Playwright **65
passed**; ruff check, `ruff format --check` on changed files, and the
dependency-direction check clean.

The browser suite earned its place as rollout step 0 on its first outing: it
caught a stale assertion in `test_corvinum_shell.py` expecting three columns on
the pay overview where there are now five. Fixed in `aad0ba9` before the
deploy. That is exactly the class of miss the pre-deploy gate exists for now
that e2e has left the per-slice loop.

Two operational notes worth keeping. `sudo` on the administrative account
requires a password, so the release used the restricted `dokku@` account
throughout - `git:load-image`, `run`, `ps:report`, `logs` - and no interactive
step was needed. And running the Jober and CorvinumEU unit lanes concurrently
against the shared `jober-dev-db` produces dozens of spurious
`DuplicateDatabase` failures; they must run sequentially.

No seed, purge, SMS, Telegram, SMTP send, payslip send, provider configuration,
runtime-secret change or production action ran. Both databases remain
fictional staging data. The prior shared image `jober-platform:demo-742f4f2`
remains the immediate rollback target:

```bash
ssh syncmetric-prime-dokku "git:from-image <app> jober-platform:demo-742f4f2"
```


## 2026-08-04 - Extraction safety, activation and profitability deployed to both staging clients

Merged **#163, #164 and #162** in that order and deployed exact `main` merge
**`742f4f2`** to `jober-staging` and `corvinum-staging` as the shared image
`jober-platform:demo-742f4f2` (local image ID
`sha256:0956d3487134d9d33538e3c6a47a37195aea387a4da8cae8391fe757b5e93b57`).
The release adds trial-waiver/self-approval behavior, the safe translation
extraction workflow, and Jober's profitability workbook, year grid and
command-line HV importer. The client workbook remains gitignored; no client
data entered the image or repository.

The final Application CI run **30904085083** was green before merge: browser
passed in 3m22s and the full quality/unit lane in 12m58s. Local release checks
also passed the no-Node rule, vendor checks, deterministic PO/MO synchronization
and production-runtime artifact inspection. The final suites recorded **1061
passed / 15 skipped** for Jober, **631 passed / 23 skipped / 261 deselected**
for CorvinumEU and **65 passed** in Playwright.

**Migrations.** Jober applied `finance.0004_financecategory_key` and
`projects.0008_readinessrecord_trial_waived`. CorvinumEU applied only the
shared `projects.0008` migration; profitability remains uninstalled and its
`/en/finance/` route returns 404, while Jober's route redirects to login as
expected. The optional Jober `ensure_superuser` command refused safely because
`DJANGO_SUPERUSER_EMAIL` and `DJANGO_SUPERUSER_PASSWORD` remain unset; it made
no database change and the known manual-superuser readiness gap remains open.

Both certificate-policy reports found **0** disallowed records with files,
both `manage.py check --deploy` runs reported no issues, and each app has one
running web process. The public HTTPS smoke suites passed health, login/CSRF,
fingerprinted static CSS, X-Frame-Options and HSTS; both serve
`app.549ea0e7ad7e.css`. Both regenerated nginx configurations retain
`client_max_body_size 25m;`, and recent app logs contain clean Gunicorn startup
only.

The host briefly refused additional SSH connections after several parallel
read-only Jober checks. Corvinum's first stream failed before data was received
and changed no state; both public health endpoints stayed available. After a
short pause, the restricted Dokku connection recovered and the complete stream,
release and verification succeeded sequentially.

No seed, purge, SMS, Telegram, SMTP send, payslip send, provider configuration,
runtime-secret change or production action ran. Both databases remain
fictional staging data. The prior shared image
`jober-platform:demo-6c413b0` remains the immediate rollback target.

## 2026-08-03 - Five merged PRs deployed to both staging clients

Merged **#157, #158, #159, #160 and #161** and deployed the exact merge
**`6c413b0`** to `jober-staging` and `corvinum-staging` as the shared image
`jober-platform:demo-6c413b0` (source image digest
`sha256:4cc2cc737a72809e4c3d09f5e3b1e3939974e5018da9209651ca2e994e8fdbe9`).

The release carries: job-offer emails for Jober with a platform-wide recipient
allowlist for both clients (#157), the mobile nav toggle moved out from under
the notification bell (#158), the reporting-period picker's missing spacing
(#159), payslips brought inside the office boundary (#160), and the legal,
retention and Secure Document Vault documents (#161, no runtime effect).

Every GitHub Actions run was green before its merge. Merged `main` was then
verified locally before any deploy: Ruff, Ruff format and the dependency
direction tripwire clean; `manage.py check` and `makemigrations --check` green
under both settings modules; **1008 passed / 15 skipped** in Jober, **614
passed / 21 skipped / 257 deselected** in CorvinumEU, and **65/65** browser
tests. `check_no_node_artifacts` and `verify_vendor_assets` both passed.

**Migrations.** `people.0008_person_email_opt_out` applied to both databases.
`messaging.0003_joboffer_emailbatch_outboundemail_offeremailtemplate` applied to
Jober only, because CorvinumEU does not install `features.messaging` - the
expected asymmetry, not a partial run. Both apps then reported no pending
migrations and `manage.py check --deploy` found no issues on either, so the
`mail.W001` allowlist warning is not firing: `EMAIL_ALLOWED_RECIPIENTS` is set
on both apps.

Both public HTTPS smoke suites passed health, login/CSRF, fingerprinted static
CSS, X-Frame-Options and HSTS. The deployed stylesheet fingerprint is
`app.565fda8125c7.css`, and its public contents expose both corrections from
this release - `.period-filter{gap:var(--space-3);display:grid}` and
`.app-header>.icon-button.mobile-only{...position:absolute;left:50%...}`.
Client isolation was re-checked at the routing layer: `/en/offers/` answers 302
on `jober-staging` and **404** on `corvinum-staging`, so the offer-email feature
is mounted for exactly one client.

Because `git:load-image` releases on load, there was a short window on each app
where the new code ran against the previous schema. Both migrations are
additive, the window was seconds, and `migrate` ran immediately afterwards.
Worth noting rather than repeating: a pre-release migration step would remove it.

No seed, purge, SMS, Telegram, SMTP send, payslip-send, runtime-configuration
or production action ran. Both staging databases remain fictional. The previous
shared image `jober-platform:demo-60b730d` remains the immediate rollback
target.

Deployed entirely through the command-restricted `syncmetric-prime-dokku` key;
the administrative `syncmetric-prime` key is passphrase-protected and its agent
refused to sign, which the deploy key exists to survive.

## 2026-08-02 - Help card icon correction deployed to both staging clients

Merged PR **#155** and deployed exact merge **`60b730d`** to `jober-staging`
and `corvinum-staging` as the shared image `jober-platform:demo-60b730d`
(source image digest
`sha256:59187f93ed59e4b39dedf017718602d3946edd5d00c116ff44978d24dcb00752`).
This corrects Jober's oversized Help-card SVGs by defining the missing shared
`icon-lg` size as 24×24 inside the existing 44×44 tile. CorvinumEU's Material
Symbols retain the same intended dimensions.

GitHub Actions run `30741349514` was green before merge: the complete browser
job passed in 2m56s and the two-client quality/unit job passed in 12m04s. Both
replacement containers passed Dokku's uptime and port-listening checks. Both
databases reported no pending migrations, and the read-only certificate-policy
scan found zero disallowed records with files in either app. Final process
reports show one running web process per app, and both active nginx
configurations still expose `client_max_body_size 25m;`.

Both public HTTPS smoke suites passed health, login/CSRF, fingerprinted static
CSS, X-Frame-Options and HSTS. The deployed stylesheet fingerprint is
`app.e91e6f987234.css`; its public contents expose the exact
`.icon-lg{width:1.5rem;height:1.5rem;font-size:1.5rem}` rule from both client
hosts. The Hungarian Help route on each host still redirects unauthenticated
requests to that client's Hungarian login page.

No seed, purge, SMS, Telegram, SMTP, payslip-send, runtime-configuration, or
production action ran. Both staging databases remain fictional. The previous
shared image `jober-platform:demo-c78e962` remains the immediate rollback
target for both apps.

## 2026-08-02 - Complete Help area deployed to both staging clients

Merged PR **#153** and deployed exact merge **`c78e962`** to `jober-staging`
and `corvinum-staging` as the shared image `jober-platform:demo-c78e962`
(source image digest
`sha256:e527c80ddaad93ea69c33935d8e90620a623c04110cbc68b3717ba83880d03ce`).
The image was built locally from the clean merge, passed the Node-artifact,
vendor-integrity and production-runtime checks, and was streamed through
Dokku `git:load-image`; the VPS did not build the source tree or receive
build-time secrets.

GitHub Actions run `30706522432` was green before merge: the complete browser
job passed in 3m11s and the two-client quality/unit job passed in 12m06s. Both
staging databases then reported no pending migrations. The read-only
certificate-policy scan found zero disallowed records with files on each app.
Both replacement containers passed Dokku uptime and port checks plus the full
HTTPS smoke suite: health, login/CSRF, fingerprinted CSS, X-Frame-Options and
HSTS. The active nginx configuration still exposes
`client_max_body_size 25m;` on both apps.

The authenticated staging acceptance check proved exactly 12 cards and 12
openable articles for each client, the shared purpose/permission/workflow/
boundary/example structure, translated HTML callouts, three unsupported
client topics returning 404, and the former Logistics URL redirecting to
Equipment. All 24 Jober WebPs and all 24 Corvinum WebPs are discoverable by
the deployed application and served successfully over public HTTPS. Jober
uses its Slovak/Jober namespace and CorvinumEU its Hungarian/Corvinum
namespace, with no cross-client image reference.

No seed, purge, SMS, Telegram, SMTP, payslip-send, runtime configuration, or
production action ran. Both staging databases remain fictional. The previous
shared image `jober-platform:demo-1458ff7` remains the immediate rollback
target for both apps.

## 2026-08-01 - Jober staging accepted all three occupational file forms

The owner completed the positive certificate-upload matrix against fictional
Jober staging records after the nginx request ceiling was corrected. A
forklift card saved with its front image; the normal **Edit certificate** flow
then corrected the issuer and dates and added the missing back image while
preserving the front. Both private file links appeared. A crane certificate
saved as a single PDF, and a welding certificate saved as a single image. All
three records rendered their expected category, issuer, dates and Valid state.

This proves the ordinary UI accepts the allowlisted front/back, PDF-only and
single-image forms on the deployed build. It does not yet claim the remaining
acceptance steps: cross-role/private-link authorization, Audit inspection,
archive/renewal, manager purge, or the optional fictional mislabel probe. No
real worker document, provider call, deployment, migration or production data
was involved.

## 2026-08-01 - Dokku upload ceiling corrected on both staging apps

A manual Jober avatar upload returned nginx's raw **413 Request Entity Too
Large** page. The nginx error log showed that the rejected request was roughly
1.9 MB, while the active configuration for both `jober-staging` and
`corvinum-staging` still had Dokku's 1 MB default. This failure was entirely at
the reverse-proxy layer: Django never received the request and therefore could
not show its existing friendly upload-validation message.

The owner set `client-max-body-size` to `25m` for both apps. On this host's
Dokku 0.38.25, `nginx:set` changed the computed report but did not immediately
rewrite the active nginx file. The required completion step was:

```bash
sudo dokku proxy:build-config jober-staging
sudo dokku proxy:build-config corvinum-staging
```

Both generated configurations then passed `nginx:validate-config` and
`nginx:show-config` reported `client_max_body_size 25m;`. After reload, all four
large generated PNG originals used in the manual Jober pass uploaded and
rendered in the person detail, People list, and bottom-right quick-access
worker panel.

A subsequent read-only inspection of the mounted media found exactly four
database-referenced avatar files and no orphans. Each had a UUID `.webp` name,
decoded as WebP at 512×512, and carried no EXIF. The four uploaded PNGs totalled
7,770,049 bytes; their stored WebPs totalled 77,042 bytes, approximately 99.0%
less (about 101× smaller). No source PNG remained in the avatar tree. Both
staging apps remain on the existing application image; no code deployment,
migration, seed, provider call, or real personal data was involved.

The 25 MB proxy ceiling deliberately sits above the application limits rather
than replacing them: Django continues to enforce 5 MB per avatar and 10 MB per
certificate file. The extra room permits a two-sided certificate request plus
multipart overhead to reach Django and fail there gracefully when an
individual file is invalid or oversized. The staging runbook now makes this a
required per-app setting and records that a reload alone does not regenerate a
stale Dokku nginx configuration. Requests above the 25 MB outer guard can still
receive nginx's generic 413 page; a branded proxy response or browser-side
preflight remains future UX hardening, not part of this operational correction.

## 2026-08-01 - Restricted certificates release deployed to both staging clients

Deployed merge **`1458ff7`** to `jober-staging` and `corvinum-staging` as the
shared image `jober-platform:demo-1458ff7` (local image digest
`sha256:6fee292fe2822b45331ceef88e44f68b5f8bb56a3f07e500e9d05e0500fcdac1`).
The image was built locally from the clean merged checkout, passed the runtime-
artifact check, and was streamed through Dokku `git:load-image`; neither VPS
app built the source tree or received build-time secrets.

Release gates were green on the exact merge: Application CI run `30693027596`
passed the full Jober/Corvinum quality lane and the two-client browser lane.
The preceding red `main` run was a July-fixture/current-month test defect; PR
#149 pinned the two office-scope requests to July and the exact-merge rerun
passed.

`jober-staging` applied only
`compliance.0003_occupational_certificate_files`. The read-only
`enforce_certificate_storage_policy` report found **0** disallowed certificate
records with files. The process stayed running and the HTTPS smoke passed
health, login+CSRF, fingerprinted static CSS, X-Frame-Options and HSTS.

`corvinum-staging` had not received the later shared migrations, so this release
applied `people.0006`/`0007`, `audit.0002`, `compliance.0003`,
`logistics.0010`/`0011` and `projects.0007`. The required idempotent
`backfill_audit_persons` command attributed **29 of 62** previously
unattributed events; the remaining 33 target no person (29 target nothing and
4 target equipment catalogue items). Its certificate-policy report also found
**0** disallowed records with files. The process and the same HTTPS smoke suite
passed.

No seed, SMS, Telegram, SMTP or purge command ran. Both databases remain
fictional staging data. Production and the real-data gate were not touched.
Dokku 0.38.25 still reports the known default-bridge deprecation and the apps
still rely on Dokku's port/uptime checks because no `app.json` healthcheck is
defined; both checks succeeded for each app.

## 2026-07-28 - SMS templates deployed and the picker verified rendering

Deployed **`631dd1c`** to `jober-staging` as `jober-platform:demo-631dd1c` -
the seeded SMS templates (#146) and the status-rail race fix that came with
them. No migrations. `seed_messaging` run on staging: 3 created.

**Verified the picker actually renders**, not just that rows exist. The panel
hides its `<select name="template">` behind
`{% if panel.message_templates %}`, which is exactly why an empty table looked
like a missing feature - so a row count proves nothing and the page had to be
loaded:

| check | result |
|---|---|
| templates on staging | 3, all active |
| coordinator opens a person with a phone (Olha) | HTTP 200 |
| `<select name="template">` present | **yes** |
| all three names appear as options | yes |

The runbook's "pick a template" step now has something to pick.

**Unchanged and still true:** the body is sent verbatim in whatever language it
was written in. These are Slovak. Backlog item 17.

## 2026-07-28 - Project management and the finance entry panel deployed

Deployed **`e0f833b`** to `jober-staging` as `jober-platform:demo-e0f833b`,
carrying project management (#144), the finance manual-entry panel (#143), J6's
returns retirement (#142), the finance-workbook answers (#141) and the deploy
record (#140). No migrations.

**Verified by creating a real project through the UI, not by reading code:**

| check | result |
|---|---|
| `manazer@` creates a project | HTTP 200, filed to Velký Meder |
| audited | `project.created` recorded |
| `manazer.gyor@` sees it in the list | **no** |
| `manazer.gyor@` opens its edit form | **403** |
| `manazer.gyor@` deactivates it | **403**, and it stayed active |
| `manazer@` opens its edit form | 200 |
| finance record panel renders | yes |

Done with two managers in different offices rather than one, and the write
attempt matters as much as the read: filtering a list has never been the same
thing as refusing a POST, which is how the cross-office deduction write got
through earlier this week. The verification project was deleted afterwards - it
had no assignments or finance months, so nothing PROTECTed it.

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
