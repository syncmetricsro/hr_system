# Build Journal

## 2026-08-05 - nine checkboxes, nine explanations

The activation checklist hung one tooltip on all nine boxes: "records that you
completed this item, with your name and the time". True, and useless — it
explains ticking, not the check. Noticed in Hungarian, where nine identical
bubbles down a list are unmistakable.

That list is the one place in the product where the office asserts that
real-world verification happened: a document was seen, a training attended, a
duplicate search actually run. So each item now says what its tick claims, with
the item's own name as the tooltip heading.

Help text is **data, not code**: a `help_text` field on `ChecklistItemTemplate`,
seeded in canonical English beside the label, registered in the client's
`catalog_i18n.py`, rendered through `db_trans` — the pattern every other seeded
catalog string already uses. A lookup map would have avoided the migration and
put one client's nine strings inside a shared feature, where an operator-added
item could never have help of its own.

The trap worth remembering: `get_or_create(defaults=…)` **creates**. Every demo
and staging database already holds all nine rows, so the help text would have
reached none of them. The seed now repairs existing rows, and the local stack
proved it by showing Hungarian help on a database seeded weeks ago.

Not marked as real-world action buttons (ADR 0034): a tick asserts that
something happened rather than causing it, and nine amber rows would flatten a
marker that is one day old.

Wording is ours, not the client's — C-Q22 asks them to correct any of the nine
at the demo, and the runbook now says to hover a few before ticking.

Jober 1110, CorvinumEU 711, browser 70 (not re-run).

## 2026-08-05 - Corvinum localhost uses password-only demo login

The fictional-data Corvinum client at `localhost:8001` no longer asks testers
to enroll or enter TOTP. A dedicated `clients.corvinum_eu.local` settings layer
turns off the shared authentication switch, and the committed local runner is
the only entry point that selects it. The bypass covers both forced manager
enrollment and users who already have a confirmed device in the disposable
demo database; setup and verification routes also stop operating while the
switch is off.

This does not relax a public environment. Corvinum staging, the browser
acceptance lane, and production continue to select
`clients.corvinum_eu.production`, where TOTP is enabled and managers are still
required to use it. The ADR, permission/security notes, environment guidance,
presenter runbook, and historical verification record now state that boundary.

No dependency or migration. Jober 1108 passed / 16 skipped; CorvinumEU 706
passed / 23 skipped / 262 deselected. Browser lane not run because it remains
production-settings coverage and this slice changes only the local runner.

## 2026-08-05 - the buttons that reach outside the application

Owner request: some clicks pay a person, send a real message, hand over gear, or
put someone on a bus, and the product gave them the same quiet grey button as
"recalculate this table". The only thing separating *Mark cycle settled* from a
filter was the label text.

Sixteen buttons across four families now carry a marker of three parts: an amber
**striped** button, the fixed tooltip heading **Real-world action**, and a
visible caption saying the physical fact - *Money is actually paid out*, *A real
phone buzzes*, *Gear physically changes hands*. Where the action already
confirmed, the dialog leads with a band saying it reaches outside the
application. Verified in both themes, at 1280 and 390, and by opening a physical
confirmation and then an ordinary one to see the band clear.

The stripe is the part worth defending. Colour alone fails greyscale and colour
vision deficiency - this stylesheet already reasons that way about its chart
tokens - so the marker had to be a shape too. It is drawn in CSS rather than set
as an icon because the CorvinumEU Material subset is fixed and a missing
ligature renders as the literal word.

Deliberately **not** marked: the generic ledger *Record* button. It records
something that already happened, and the same control also takes fuel additions
and equipment charges; the loudest styling in the product on its most routine
button is how a warning becomes wallpaper. Blacklist decisions stay unmarked too
- serious, but not physical.

`.button-physical` is read by `app.js`, so the class is an interface, not a
style. ADR 0034, and a test that holds the three parts together and names each
of the sixteen buttons.

Two stale ledger tooltips went with it: *Include open entries* still promised
reversal-only corrections and no backdating, both untrue since ADR 0032/0033.

Jober 1105, CorvinumEU 703, browser 70 (not re-run; e2e is opt-in).

## 2026-08-05 - C-Q5 answered: an entry is deletable until the money is paid

The open question said "no hard deletes; reversal-only after inclusion". The
owner rejected it outright - **these should be deletable and cannot be made
immutable** - and then drew a better line than the one I offered: deletable
right up until the money is paid, immutable after. Included is not paid; it
means queued for a run. So everything before payday is a record of an intention
and may be corrected freely, and `DEDUCTED` is where the ledger becomes the
thing an accountant argues from.

`delete_entry` removes the row and writes `ledger.entry_deleted` carrying
person, amount, currency, category, type, date, the status it held and its cycle
key. The ledger gets clean; the record does not disappear. An entry that already
carries a reversal is refused rather than cascaded - removing a row the operator
did not select is the worse surprise.

Delete and reverse both stay, because they say different things. Delete: this
should never have existed. Reverse: this happened and is being given back, with
both sides visible and linked. The owner was asked directly and kept both.

**Reopening a cycle** was the second half. A run closed by mistake was
unrecoverable, which cost a reversal per entry. `reopen_cycle` returns the
entries to open while the cycle's own 21st-to-20th window is still running, and
refuses once anything in it has been paid. After the window ends it refuses too
- and the refusal **names the next run and the dates it covers**, which was the
owner's actual requirement: do not just say no, say when the money gets
collected instead. Under carry-forward (ADR 0032) that sentence is always true.

ADR 0033; C-Q5 closed; the demo runbook now walks the correction paths instead
of asking the client to invent them, and its stale "would be refused" note is
gone with the guard it described.

Jober 1083, CorvinumEU 681, browser 70 (not re-run).

## 2026-08-05 - The ledger offered a reversal it would then refuse

Reported: pressing Sztornó on an already-reversed entry answered "this entry is
already reversed", and the original was still sitting in the list looking
untouched.

Both halves were the interface, not the rule. `reverse_entry` has always allowed
one reversal per entry (C-Q5), but `ledger_activity.html` showed the button
whenever an entry was locked, without asking whether a reversal already existed
- so the page offered an action it would then refuse. And nothing marked either
side of the pair, so the correction the operator was looking for was already two
rows away with no sign of it.

`LedgerEntry.is_reversed` answers it, `cycle_report` select_relates
`reversed_by` so the list does not cost a query per row to ask, and the rows now
carry **Reversed** and **This is a reversal**. The original stays listed, which
is the point: reversal never deletes.

Jober 1083, CorvinumEU 673, browser 70.


## 2026-08-05 - A medical you could never record, and flashes nobody could read

**The compliance alert that could not be cleared.** A worker showed "Medical —
missing" with no way to fix it. Their readiness said `medical_state = complete`
and `entry_medical_date = None`: activation checks the pillar *state*, the
compliance alert reads the *date*, and nothing ever required the two to agree.
Not stale data - the person was created on 2026-07-20 by the walkthrough
checker, well after the medical features existed.

Two holes, and the second is the one everybody reaches:

* a worker could be activated with Medical ticked and no date, straight into an
  alert. `update_readiness` now refuses to mark Medical complete without one.
* readiness is only editable on the way *in* - the form disappears once someone
  is Working - so no screen anywhere set this field for an activated worker.
  `MEDICAL_VALIDITY_MONTHS` is 12, so **every** worker eventually needs a
  renewal recorded and nobody could record one. A working person's profile now
  carries a medical panel: `record_entry_medical` touches the date and nothing
  else, audited, manager-gated, and deliberately not a back door into the
  activation workflow.

Requiring the date made the demo seed and three test files fail, which is the
rule working: each was creating exactly the inconsistency that produced the live
alert.

**Flash messages.** Three seconds for a two-line message, so they were gone
before they could be read. Now ten seconds, with a dismiss button, and the timer
holds while the pointer or keyboard focus is on the message - reading it should
not race it. The markup was duplicated in both client shells, identical and free
to drift, so it moved to `templates/partials/flash_messages.html` and the shell
test now checks the include on each side and the behaviour once, where it lives.

Jober 1076, CorvinumEU 671, browser 70.


## 2026-08-05 - A payroll run now collects what is outstanding

Reported by the owner: an advance given in July was never deducted from the
August salary. It was worse than a display bug - the money was never recovered
at all. `include_cycle` swept only its own 21st-to-20th window, and the windows
are disjoint, so an entry that missed its run was never picked up by any later
one. It stayed OPEN for ever: reported as owed, collected never.

Two things in the code already disagreed with that, which is what made it a
defect rather than a decision. `open_balance` counts every unsettled entry and
calls the result "what the person currently owes against future pay" - the
office was already being told the money was owed. And `cycle_for` correctly put
a 25 July advance in the **August** run while the pay overview showed it under
**July**, because I grouped that column by calendar month on 2026-08-04 and
wrote a test asserting it was deliberate. The reasoning was tidy and wrong: an
advance handed over on the 25th is recovered from the next month's pay, so
showing it against the current month describes a payslip already paid.

A run now sweeps every open entry dated on or before its cutoff. `cycle_report`
answers "did" or "will" depending on whether the run has happened, so a closed
run keeps reporting exactly what it took while an unrun one forecasts what it is
about to take - both the ledger page and the accountant CSV read it.
`settling_cycle_key` gives the overview the run that collects an entry, walking
forward past runs that have already gone out.

**The settled-cycle refusal is withdrawn, not narrowed again.** Added yesterday
to stop an orphaned backdated entry, it was wrong twice: it blocked ordinary
present-day work, because equipment charges reach the ledger with no date at all
and default to today, and it solved a problem carry-forward removes. Refusing to
record something that really happened was the wrong shape of answer - the money
exists whether or not the bookkeeping is ready for it. ADR 0032 records all of
it.

Checked what the first run would collect on staging before shipping, because
this sweeps historical strays by design: four entries, all dated 2026-08-04, all
pay additions - the reversals created while testing Sztornó. Nothing historical,
no surprise deduction.

Jober 1076, CorvinumEU 665, browser 70.


## 2026-08-04 - A slow upload could be submitted twice

Reported against certificate upload: the Save button stayed live while the file
POST was in flight, so it could be pressed again. `Certificate` carries **no
uniqueness constraint**, so the second press genuinely created a second row -
confirmed by counting requests, not by reading code: without the guard the
interface sent **2 create requests**, with it **1**.

The guard is generic rather than bolted onto that one page, because the ledger
entry, payslip and wage forms create rows exactly the same way and are exposed
to exactly the same double-click. It is deliberately narrow about what it
touches: GET forms are search and filter controls where re-submitting is
harmless, htmx owns its own submissions, and a submission another listener
already prevented (the confirm dialog) is left alone - the real submit arrives
afterwards and is guarded then.

Two implementation details that were not optional:

* **The submitter's `name`/`value` is carried as a hidden input before the
  button is disabled.** A disabled submitter contributes nothing to the form
  data, so without this an approval would post with no `decision=approve` in it.
* **The busy state is applied synchronously, not on a `setTimeout(0)`.** The
  first version used a timer to avoid that same name/value problem, and the
  timer never ran: once a form starts navigating the browser may drop queued
  timeouts - which is precisely the window the second press lands in. That
  version passed nothing and looked correct.

Visible feedback beyond the disable, since a silent wait is what makes people
press again: the button shows a spinner and swaps to its `data-busy-label`, and
the certificate form reveals a bordered notice saying an upload is running and
not to close the page. Both respect `prefers-reduced-motion`.

**Not fixed, and worth stating: this is a client-side guard.** It stops the
reported cause - an impatient double-click - but not a re-POST from the back
button or a retried request. The durable fix is server-side, either an
idempotency token on the form or a uniqueness constraint on the certificate.
That is a schema and workflow decision rather than a UI one, so it is not
bundled here.

Jober 1076, CorvinumEU 658, browser 70.


## 2026-08-04 - The worker rail was reserving 320px on a phone

The reported mobile symptom - a ledger heading wrapping one character per line -
turned out to have nothing to do with the ledger, or with the card layout fixed
earlier today. Four rounds of measurement from the reporter's own browser found
`.cv-main` computing **`padding: 24px 320px 48px 16px`** at a 375px viewport: a
39px content box, so every block on every page collapsed to min-content.

The 320px is the worker status rail's reserved gutter. It *was* released below
1100px, on paper:

```css
body:has(.worker-rail:not([data-collapsed="true"])) .cv-main { padding-right: 20rem; }
@media (max-width: 1100px) { body:has(.worker-rail) .cv-main { padding-right: 0; } }
```

`:has()` carries the specificity of its argument, and a media query adds none of
its own, so `:has(.worker-rail:not([data-collapsed="true"]))` outscores
`:has(.worker-rail)` and the gutter survived the override. The rule now sits
inside `@media (min-width: 1101px)` instead, which removes the specificity
contest rather than trying to win it - and matches the intent, since below that
width the rail is a floating panel in the bottom-right corner with nothing
beside it to make room for.

**It only appears while the rail is expanded**, which is why nothing caught it:
the rail ships collapsed, every existing responsive test left it collapsed, and
the reporter had opened it. The new test expands it first, and was confirmed to
fail without the fix with the reporter's exact numbers - `padding-right: 320px`,
content box 39px - and to pass with it at 16px and 343px.

Worth recording as a pattern, because this is the third instance today: a test
that never puts the UI in the state the bug needs will pass forever. The other
two were the activation queue measured on a page with no cards, and the ledger
measured as a role that cannot see the entry form.

Jober 1076, CorvinumEU 658, browser 68.


## 2026-08-04 - Decision cards stop squeezing their own form

Reported with two screenshots of CorvinumEU's activation queue: a reason input
about 70px wide on a desktop browser, and a card running off a phone screen with
the intro paragraph crushed beside it.

**The desktop symptom reproduced exactly and was measured before anything
changed: 99px at 1280px.** `.field-card` is a two-column grid, and *seven*
templates give it three children - the third wraps into column one, which the
details list has already squeezed. Not three templates, as the screenshots
suggested: `accommodation_detail`, `equipment_catalog`, `offer_list` and
`trials_queue` have the same shape with a link or a div as the third child, so
one rule (`:nth-child(n+3) { grid-column: 1 / -1 }`) repairs all seven.

Two more structural weaknesses fixed alongside it: the details list had a fixed
`10rem` right-aligned value track, which a longer value overflows *leftward*
across its own label, and nothing set `min-width: 0`, so an unbreakable token
like an email address can force a card wider than the viewport. The
`· your own request` marker added earlier today lengthened exactly that value.

Decision cards - the three with a form - now stack at every width behind a
`field-card-decision` class, so the actions get the whole card and the detail
pairs flow as a wrapping row. An explicit class rather than `:has(form)`: it is
greppable, assertable, and does not silently restyle some other card the day
someone adds a form to it. The four non-form three-child cards keep their
two-column look and are fixed by the shared rule alone.

**The mobile symptom did not reproduce**, and that is worth saying plainly
rather than quietly claiming a fix. With the seeded demo data the Corvinum card
measures 359px inside a 375px viewport with zero page overflow, before and
after. The structural causes that would produce it are fixed, but the exact
screenshot is not reproduced - most likely because the reported view had three
cards and a longer Hungarian requester string than the seed generates. If it
persists, the viewport width it was taken at would pin it down.

Measured, not eyeballed: **inputWidth 99px -> 320px** at 1280px, page overflow 0
at both widths, no value rendering left of its label.

Two test-infrastructure notes. The browser stacks seed **no** pending activation
approval, so a naive test on that page asserts nothing while passing - the new
test builds the request through the UI and asserts a card exists before
measuring anything. And `test_z_certificate_uploads` and the new layout test
both drive the same 2FA-enforced manager, where only the first login is ever
shown the enrolment secret; they now share `tests/e2e/corvinum_auth.py`, which
caches it, so neither depends on running before the other.

Jober 1076, CorvinumEU 658, browser 67; ruff check and format clean.


## 2026-08-04 - CorvinumEU pre-demo batch: the subtraction they could not show

Ten requested items before a customer demo. Two were bigger than they looked,
one was not the bug it appeared to be, and one turned out to be a template
condition.

**"I was unable to demonstrate the subtracted payslip from the Brutto salary"
was not a defect — the product refused to do it by design.** Gross wage and net
payslip were two independent source values (C-Q17) and nothing joined them; the
panel said as much in its own caption. The fix shows what the office actually
controls: a **Ledger deductions** column from `features/advances` and a derived
**After deductions** column. The join has to happen in core, because a feature
may not import another feature, so `register_person_finance_series` gained a
`role` (`gross` / `deduction` / `source`) and core relates two columns without
knowing which feature supplies either. C-Q17 narrows rather than reverses: the
remaining gap to the payslip is statutory, and naming that gap out loud is now
step 5 of the runbook rather than an awkward silence.

**The ledger form had no date field at all.** Every entry landed on today, so a
July deduction could not be entered in August — which is precisely why the demo
could not be given. `record_entry()` already accepted `entry_date`; only the
form and view never passed it. Adding it exposed a real hazard: `include_cycle`
sweeps its window **once**, and the windows are disjoint, so an entry backdated
into a swept window would be created OPEN and never picked up again — sitting
forever in a period whose payroll had already gone out. `record_entry` now
refuses that and names the cycle. Reversals are exempt, or the sanctioned
correction path for a settled cycle would have no way to run.

**Office separation needed no client branching.** `apply_office_scope` already
set the queryset to `Office.objects.all()`, empty on CorvinumEU — so the picker
rendered as an empty dropdown asking for something the client does not have. It
now drops the field when **no Office rows exist at all**: keyed on data, never
on client identity, so seeding one office brings it straight back. One change
covered all five call sites. The header badge already handled this correctly.

**Audit and Staff activity are Observer-only on CorvinumEU.** Done at the policy
layer rather than by hiding links, so a manager loses the tab *and* gets 403 on
a typed URL. The staff-activity icon moved from `trending_up` to `badge`; the
first choice, `supervisor_account`, was caught by a test proving it is not in
the self-hosted font subset and would have rendered as raw ligature text.

**Dates are bounded, both clients.** A native date input always submits ISO, so
the format was never the problem — the year was. Unbounded, `12345-06-07` parses
as a valid date and lands in the database looking plausible. `core/ui/forms.py`
now defines the bounds once; every form widget and all 14 raw template inputs
use them, and a sweep test fails when the next unbounded one is added.

**Tooltips and help were written as one job, and that caught a mistake.** The
extractor reported near-duplicate msgids differing only by an em dash — proof
that the "same sentence in both places" claim in the `_f` docstring was already
false. Unified before translating, which also removed 7 strings from the batch.

The safe extractor from #164 did its job twice: it refused the run outright
until the two genuinely obsolete labels were acknowledged with
`--accept-obsolete`, and it surfaced the duplicates. 54 new msgids, translated
by hand into SK/HU/UK, zero fuzzy.

Suites: **Jober 1076 / CorvinumEU 658**, ruff and dependency direction clean.
E2E deliberately not run, per the workflow agreed earlier today — it touches
many templates, so it is a fair one to ask for before deploying.


## 2026-08-04 - No more pull requests, and the browser suite becomes opt-in

Two process changes, both asked for, both about cost rather than code. Recorded
here with the reasoning because a future session reading only the diff would see
rules getting *looser* and reasonably try to put them back.

**Pull requests are gone.** They were ceremony for a repo with one maintainer:
nobody reviewed them, and waiting on CI before merging cost ~9 minutes a slice.
Work still gets its own branch — that part was never the problem — but it is
merged locally with `git merge --no-ff` and pushed. `AGENTS.md` §1 item 8 is the
binding statement and had to change first; `CLAUDE.md`'s workflow now spells out
the four steps and the `git` commands.

The honest consequence, written into both files: **CI stops being a gate and
becomes a report.** It still runs on every push to `main`, but after the fact,
and `main` has no branch protection — so a red local run reaches `main`
unopposed. That makes step 2 (ruff + both unit lanes, ~1640 tests) the only
thing standing in front of `main`, which is worth knowing before skipping it.

**The browser suite is opt-in.** It had grown to the point where running it per
slice was not worth it, and CI was running it on *every* push to `main` as well.
The `browser` job moved out of `application-ci.yml` into its own
`browser-e2e.yml` with `workflow_dispatch` and nothing else, so it is one
command away (`gh workflow run browser-e2e.yml --ref <sha>`) and never runs
itself. `application-ci.yml` also loses its `pull_request` trigger and the now
dead `github.event.pull_request.base.sha` half of `CI_BASE_SHA`.

`scripts/ci_quality.sh` needed no change: its format check already falls back to
`git merge-base HEAD main` when `CI_BASE_SHA` is not a valid sha, so losing PR
events does not affect it.

The one place e2e is now *required* is a staging deploy, so
`docs/deployment/deployment-plan.md` gains it as rollout step 0 — a deploy is
the moment the accumulated UI risk is worth 45 minutes.

Not done: the three merged branches (`feat/activation-without-trial`,
`feat/profitability-workbook`, `fix/i18n-extraction-safety`) still exist on the
remote, since without PRs nothing deletes them automatically. All three carry
zero commits that are not in `main`; deleting the pointers was raised and left
for the owner to decide.

## 2026-08-04 - Translation extraction now fails safe

The catalog incident on the activation branch had two genuine tooling bugs and
one misleading symptom. Raw Django extraction scanned
`tests/test_compile_po.py`, so its context/plural compiler fixtures became
product msgids. GNU msgmerge also guessed fuzzy translations, including pairing
"trial waived" with the translation of "Trial failed". Those are now prevented
at source: the shared `safe_makemessages` command adds
`--no-fuzzy-matching`, and the workflow excludes `tests`.

The apparent deletion was different. Extraction moved 122 no-longer-referenced
active entries into recoverable `#~` obsolete history; it did not erase their
PO blocks. Of those, 111 referenced only the deleted, pre-redesign Help
templates. The workflow now reports additions, removals and revivals
semantically, snapshots all catalogs before extraction, and restores them if an
active-to-obsolete transition was not explicitly approved.

Compilation is deliberately separate. A standard-library parser understands
wrapped entries, contexts, plurals, fuzzy flags and obsolete blocks; it rejects
fuzzy, untranslated, incomplete or language-divergent active catalogs before
writing deterministic MO files. `--check` compares those bytes without
writing. No dependency or runtime behavior changed.

Failure-path verification: ordinary extraction reported 1542 active / 1542
translated / 0 fuzzy and 165 obsolete per language, listed all 122 transitions,
returned failure, and restored SK/HU/UK byte-for-byte. Review classified 111 as
references only to deleted Help files; the remaining 11 are ten superseded Help
labels/titles and PR 163's removed self-approval error. The explicit refresh
retained all 165 obsolete translations, compiled the 1542 reviewed active
entries, and a later second extraction was byte-identical. Creation timestamps
are preserved deliberately so time alone cannot dirty a catalog.

## 2026-08-04 - Activation stops assuming two people and a trial day

Two client complaints, one root cause: an office may have exactly one
administrator, and the activation workflow was built assuming at least two
people and always a trial day. ADR 0031 records both fixes; they apply to Jober
and CorvinumEU, and both live in `core/`, so each is written once.

**Reading the code first shrank half the job to a template condition.** Nothing
in the activation chain ever required a trial — `get_or_create_readiness`,
`update_readiness`, `_assert_ready`, `request_activation` and
`activate_on_project` never reference `Trial`, `readiness_update` and
`activate_person` accept any project pk, and *both* clients already permitted
`AVAILABLE -> WORKING` (Jober's entry even carries the comment
`# CARGO manager override / direct activation`). The requirement lived entirely
in `person_detail`'s `in_readiness` flag, which demanded `TRIAL_DAY` plus a
passed trial, and in the template reading its project from
`passed_trial.project.pk`. A presentation constraint that read like a business
rule.

So: a manager-only `activation.waive_trial`, a `ReadinessRecord.trial_waived`
flag, and `waive_trial()` opening readiness on an Available person for a chosen
project. The person **stays Available** until the decision — moving them to
Trial-day would make the lifecycle claim a trial that never happened. The four
pillars are untouched, which is the entire point: the trial is waivable, the
entry medical certificate is not. `exit_person` clears the flag, or a recycled
worker would land back in readiness on a record describing finished work.

**The self-approval 403 was a control that made the product unusable.** One
manager on CorvinumEU staging, two pending approvals both raised by that
manager, neither ever decidable. `SelfApprovalError` is gone; `decide_activation`
now computes `self_approved` and puts it in the audit event **only when true**,
so the ordinary decision stays quiet and searching for self-approvals returns
exactly them. The queue row says "your own request". Separation of duties became
visibility rather than prevention — a deliberate reduction, on the reasoning
that a control which blocks the job gets worked around, and being worked around
leaves no record while this does.

**Catalog extraction is unsafe, and it is not this slice's bug.** Running the
old `compile_messages.sh --extract` moved 122 no-longer-referenced strings from
the active set into recoverable obsolete history, including 111 tied only to
deleted Help templates. That cleanup was legitimate but silent. The real bugs
were pulling fixture strings from `tests/test_compile_po.py` and proposing
five wrong fuzzy translations ("trial waived" -> the translation of "Trial
failed", "Skip the trial and start readiness" -> "Review the trial details and
try again"). The changes were reverted and nine reviewed entries appended by
hand: 1664/1664 translated in SK, HU and UK, zero fuzzy. Extraction safety
belongs in its own slice.
## 2026-08-04 - Profitability: the client's own workbook, three ways

Jober accept the implementation when it looks and totals like `HV 202510.xlsx`.
Reading that file before writing anything changed the job twice.

**The rows already matched.** All 25 categories line up one-for-one with the
sheet, because `Jober_Finance_Specs` §2 was derived from this workbook in July
and `seed_finance` seeds from §2. Nothing to build there. The columns are
projects, which is data.

**Signed storage was cancelled after being approved.** The spec lists the
storage convention as an open question (§10 q4) and it is not: the code answered
it. `normalize_source_amount` already requires costs typed negative and rejects
a positive cost, `signed_amount` already renders signed, the CSV already exports
signed, and two test modules already lock both in. Migrating storage would have
rewritten tested design and every staging row for no visible change. The spec
was stale, not open.

What was actually missing was layout, a year view, and a way in from the file.

The module moved to `features/profitability`, the placement §2 names and the
name the flag always used. The Django app *label* stays `finance` on purpose —
letting it follow would rename every table and rewrite migration history on
databases holding data, for something no reader sees. `makemigrations --check`
reports no changes, which is the evidence. One reference no grep for the module
path could catch: `config/urls.py` gated the whole finance block on
`_feature_on("finance", …)`, which prefixes `features.` internally, so moving
the module silently unmounted every route and took 174 tests with it.

Two read surfaces now draw the workbook's shape — one period with projects
across and offices subtotalled, and one project across twelve months. Both
compute from the active category set rather than a coordinate range, which is
not a stylistic preference: see below. Rows carry values pre-aligned to columns,
because Django templates cannot index a dict by a variable key and a filter to
do it would move grid arithmetic into the one place it cannot be tested.

`import_hv_workbook` reads the `.xlsx` with `zipfile` and some XML, so no
spreadsheet library enters the lockfile and AGENTS.md §3.1 never applies. It is
a command, not an upload: the file is never stored and the document-storage
boundary stays out of it. It refuses to guess which column is which project,
because the file cannot say — columns B and J carry a headcount in the header
row and no project name anywhere, and column G holds headcounts among the
figures. Unmapped column, hard error.

**Their workbook is wrong in three separate ways, and only one was known.**
§7 recorded that Minit's `C24=SUM(C3:C22)` stops a row short. Parsing the file
found the cached value matches *neither* the short sum nor the correct one, so
that cell is stale as well as mis-ranged; that column B is wrong too and §7
never mentioned it; and that `B3` holds a headcount inside the range its own
`SUM` starts at. Two projects' profit has been reported incorrectly. The
importer reports each disagreement and imports the cells — the discrepancy is
the client's and they should see it. §7 is expanded and the demo runbook now
tells the presenter how to raise it without it sounding like an accusation.

One bug worth keeping. Grid cells were assigned through a dict keyed by project
id but indexed by month id — separate sequences that coincide only on a freshly
created database. It passed alone and failed seven tests in a shared run. Every
figure would have landed in the wrong column. The added test burns project ids
first so the mix-up fails deterministically rather than by luck.

After the extraction-safety work landed, this branch was rebased and refreshed
with that workflow. Extraction reported 14 genuinely new active messages,
including "Workbook", with zero fuzzy guesses, newly obsolete entries or
revivals. All 14 were translated manually in SK, HU and UK; each catalog now
has 1556 active / 1556 translated / 0 fuzzy entries, the committed MO files
pass the read-only synchronization check, and a second extraction was
byte-identical.

CI then exposed a local-only test dependency: all importer tests read the
gitignored client workbook, so a clean checkout had no fixture and 16 tests
failed before exercising the importer. The private file remains excluded. A
small standard-library OOXML builder now recreates only the structural facts
the tests need — unnamed and non-project columns, duplicate damage labels,
float noise, a short formula and stale totals — with no client data in Git.

## 2026-08-03 - The Secure Document Vault gets an architecture

Asked to capture a decision to exclude government IDs, birth certificates and
medical papers from the product and offer a paid vault instead. Checking first
turned the task from "write it all" into "write the one part that is missing".

The decision was already made and already enforced.
`document-storage-boundary.md` adopted it on **2026-07-31**, and
`FILE_ALLOWED_CATEGORIES` limits uploads to forklift, crane and welding in code
rather than in policy. The module was already named and already framed as
"separately scoped and priced", referenced from eight places, and already put to
the client as **C-Q18**. The accompanying legal analysis existed too, and
`accountant-data-handoff.md` is more complete than the version we were working
from - it covers Hungary as well as Slovakia and lists the primary sources it
checked.

What was missing was architecture. The vault section was an eight-bullet
requirements list with no design, no data model, no phasing, and nothing a
client could be quoted from. Two documents now fill that: an engineering design
and a client-facing offer. The boundary doc keeps the requirements and points at
the design for the rest.

**Encrypted identifier storage went into the vault rather than the base
platform**, reversing the shape of the source material. The base stores no raw
identifier at all today - blacklist matching keeps `identifier_type`, an HMAC
and a key version, and the value never reaches the database. Putting encrypted
identifiers in the base would surrender that property for every client including
the ones who never asked for a vault, so `PersonIdentifier` sits behind the paid
module and the base keeps a claim worth having: we do not hold your ID number.

The proposal leads on three gaps verified in the code rather than on security
adjectives. `core/media_views.py` has no `record_event`, so a certificate read is
correctly *authorised* - `assert_person_in_scope` plus `can_view_sensitive` - and
then not recorded; who looked at a file is not written down. Files are plain
`FileField`s on the media volume with no application-managed key, which the
boundary doc already admits and `production-readiness.md` already tracks as
blocking real scans. And nothing anywhere asks a user to re-authenticate before
a sensitive view or export.

The design deliberately does **not** re-specify what the base already provides -
secret isolation, hash-locked dependencies, encrypted off-site backups whose
restore drill compares per-table row counts, server-side RBAC, append-only
audit. Listing those as vault features would invite a client to pay twice for
things they already have.

## 2026-08-03 - Written the material the client is being asked to approve

Every remaining item on the worker-email work was blocked on the client rather
than on code, and none of it could move because nobody had written what the
client is being asked to approve. There was no LIA draft anywhere in the repo,
no retention policy, and no statement of what a processor agreement must cover;
`docs/security/` held two files.

Five documents now exist: draft LIAs for job-offer emails and for the blacklist,
a retention proposal, a per-processor DPA checklist, and one page consolidating
every outstanding decision by who has to answer it. Both LIAs carry an unsigned
DRAFT banner and a sign-off block, and cite safeguards from the code by name
rather than promising them - the point is that a DPO edits rather than starts
blank, and that the technical description is accurate because they cannot check
it themselves.

Two findings came out of writing them rather than out of the brief.

**The retention framework exists and almost nothing uses it.** `register_retention`
is called by exactly two features, feedback and blacklist. Six other stores of
personal data - SMS records, payslips, audit events, certificate files, person
records, wage and advance rows - have no purge path at all, so setting a period
for them is a code change and not only a decision. `run_retention` is also not
scheduled anywhere, and there is no Art. 17 erasure path: `archive` hides a
person, it does not delete one.

**On the blacklist, the free-text reason outlives the hash.** `purge_expired`
deletes fingerprints past `expires_at`, but `BlacklistCase` rows carry no expiry
- so the stigmatising artefact persists indefinitely while the privacy-protecting
one ages out. That looks like an oversight rather than a decision and is written
up as row 3 of the proposal.

Also corrected an error of my own. I had reported the i18n catalogs as stale on
`main` and written that into the offer-email design doc's status section.
`msgfmt --statistics` says 1576 translated, 0 untranslated, 0 fuzzy in all three
languages. The figures I quoted came from `grep -c '^msgstr ""$'`, which counts
the wrapped form where `msgstr ""` is followed by continuation lines - a
translated long string, not an empty one. Running the extract would produce ~44
genuine fuzzy matches to review and fix nothing. The claim is removed.

## 2026-08-03 - The reporting-period picker had no CSS at all

Reported as buttons sitting too close to panels, with a note that not every
instance had been found. Measuring rather than eyeballing turned up one cause
and exactly three instances: `.period-filter` had **no stylesheet rule
whatsoever**, so the shared reporting-period picker rendered as raw block flow
and its Filter button touched the caption beneath it at a measured **0px** on
the warehouse stock, goods-receipt and staff-activity pages.

The picker is now a grid with `--space-3` gaps and a button that keeps its
natural width. Grid rather than a flex row deliberately: the controls stay
stacked and full-width exactly as the clients have already seen them, so this
adds the missing rhythm without relaying out a control mid-engagement. The
"Showing: …" caption sits outside the form, so the grid gap cannot reach it and
it carries its own `--space-4` margin.

One trap worth recording: `.period-group` must not be given a `display` value.
`app.js` hides non-matching granularities with `group.hidden = …`, which works
through the UA stylesheet's `[hidden] { display: none }`, and any author rule
would override it and render every granularity at once.

**A second suspected cause turned out not to be one.** The vertical-rhythm rule
matches only `section|aside|article`, so a top-level `<p>` breaks the chain and
the following panel inherits nothing from it — which reads like a bug and was
planned as one. Measured, those pairs sit at **14px**, because the paragraph's
own bottom margin already covers it, against the 16px the rule would give. Two
pixels is not worth a selector change that moves spacing on every page of both
clients, so the rule is left alone and the reasoning recorded here instead of
being rediscovered later.

Also confirmed while looking: yearly inventory periods are **already built**.
`core/reporting/periods.py` has offered day, week, month, several months and
year since J7, both stock pages resolve through it, and the picker renders every
granularity — the screenshots simply had Month selected. No change, and nothing
to raise with the client.

## 2026-08-03 - The mobile nav toggle was unreachable, not just hidden

Reported as the alert widget overlapping the hamburger on a phone. It was worse
than an overlap: `.notification-center` is `position: fixed` in the top-right
corner below 640px with `z-index: 55`, while `.app-header` is sticky at
`z-index: 10`. The header put the nav toggle in that same corner, so the bell
sat on top of it and swallowed the tap - the mobile menu could not be opened at
all. Measured at 375px, the bell spanned 289-363px and the toggle 318-359px,
i.e. the toggle was entirely underneath it.

The toggle now anchors to the header's centre. The first attempt used
`margin-inline: auto`, which centres it in whatever space the brand leaves over
- fine at 375px, but that space shrinks with the viewport and at 320px it put
the toggle back under the bell with one pixel to spare. Anchoring to the centre
with `left: 50%` and a translate is independent of brand width, and taking the
control out of flow also keeps it clear of the account row that wraps beneath.
`.app-header` is already `position: sticky`, so it is the containing block.

Clearance is now 81px at 375 and 54px at 320, and the header reads the way its
layout always implied: brand left, one control centred, account row below.

## 2026-08-03 - Payslips join the office boundary

Recorded as a known gap during the recipient-allowlist work and left open on
the grounds that it was not exploitable: CorvinumEU creates no `Office` rows so
`user_office_scope` returns its unrestricted sentinel, and Jober has payslips
switched off. Both halves of that argument are configuration, and configuration
changes - so it is closed now rather than left as a note.

Looking properly found **three** leaks where the note recorded one.
`payslip_send` took a pk with no guard, so a manager could email another
office's worker their payslip; that POST also mints a one-time password and
displays it, so it leaked a credential as well as the document. `payslip_list`
showed every office's net pay, which is restricted data - `PAYSLIP_VIEW` sits
in the sensitive-reads group of the `Action` enum, so a cross-office row is a
disclosure even though nothing is written. And the record form's person
dropdown offered every worker in the company, which is how an out-of-scope
payslip could be created in the first place.

`Payslip` has no office of its own, so all three scope through the worker:
`assert_person_in_scope` on the object view, and `scope_people(...,
prefix="person__")` on the list, matching the precedent already used by
logistics, checklists and audit. `PayslipForm` now takes `user` and scopes its
person queryset, which doubles as the validation - a hand-crafted POST naming
an out-of-scope person fails `is_valid()` instead of silently creating a row.
The argument is passed in rather than read from a global so the boundary stays
visible in the view, where the request is.

The guard sits before `send_payslip`, so nothing is generated for a refused
request; a test monkeypatches the PDF builder to explode and proves it.

## 2026-08-03 - Two placeholders that were being read as configuration

The recipient allowlist landed earlier the same day. Checking whether it was
safe to deploy turned out to be the more useful exercise: it found two bugs in
`email_configured()`, and neither would ever have been caught by the test suite,
because both were about environments rather than code.

They are the same defect twice. `email_configured()` asked only whether a value
was truthy, so an **empty** `EMAIL_BACKEND` fell through the non-SMTP branch and
reported *configured* - Django cannot import `""`, so every send raises
ImportError - and `EMAIL_HOST == "localhost"` did the same, despite being the
literal `os.getenv` fallback in `config/settings/base.py`, i.e. the value that
means nobody set it. In both cases the offer panel and the payslip list rendered
a Send button that could only fail. That is precisely the state the honest
disabled control exists to prevent, so the guard was lying in exactly the place
it was supposed to tell the truth.

Both were found by tracing real deployments rather than by testing.
`stg_jober-staging` has `DJANGO_EMAIL_BACKEND` set to an empty string sitting
beside live SMTP credentials. And `scripts/dev_app.sh` forwards no
`DJANGO_EMAIL_*` at all while the image bakes production settings, so the Jober
demo falls straight through to the localhost default - which is the state Jober
is in by decision, since no `noreply@` address has been supplied yet. An
environment genuinely relaying through a local MTA names it explicitly
(`127.0.0.1` or a hostname) and is unaffected.

The first real-SMTP run also happened here, against CorvinumEU payslips with a
disposable relay address allowlisted. Both directions were exercised, which is
the only thing that makes it evidence: a non-allowlisted recipient was refused
*with live credentials loaded*, and the allowlisted one arrived and decrypted.

Getting there exposed a trap in the demo runbook. The local Doppler CLI scope
was unset, so the documented bare `doppler run --` falls back to `doppler.yaml`
and selects the Jober `dev` config - which carries working SMTP and **no**
allowlist - while `corvinum_app.sh` forwards all seven `DJANGO_EMAIL_*`
variables. Following the runbook literally would have started the Corvinum demo
sending unrestricted from the wrong account: the exact failure this feature
exists to prevent, one step before the step that prevents it. Every rehearsal
command now names `--project` and `--config` in full.

The staging runbook had two gaps of its own. Its per-app config list never
mentioned `EMAIL_ALLOWED_RECIPIENTS`, so a bring-up that followed it produced
real SMTP, fictional records and no allowlist. It also never said that Doppler
does not reach syncmetric-prime - values are read locally and pasted into
`dokku config:set`, so setting a secret in Doppler alone changes nothing on
staging. Both are now stated, along with the note that a scoped service token
(ask D4) is the answer if direct sync is ever wanted, not an interactive login
binding app secrets to one person's session.

One correction worth keeping, since this journal is the durable record: while
reporting the above I described the Jober `dev` Doppler config as a live
exposure for the Jober demo. It is not - `dev_app.sh` forwards no email
variables, so those credentials are inert there. The real risk was the
cross-config trap described above, where `corvinum_app.sh` picks them up.

## 2026-08-03 - The email recipient allowlist becomes a platform control

The allowlist shipped a day earlier inside `features/messaging`, guarding job
offers. It guarded the wrong client. CorvinumEU installs `features.payslips` and
not `features.messaging`, and CorvinumEU is the deployment about to be pointed at
a live mail server (`noreply@corvinum.eu`). `send_payslip` emailed
`payslip.sent_to or person.email` unconditionally; the only thing between a demo
and a real inbox was the runbook telling the presenter to use a controlled
mailbox. That is exactly the control `tests/test_sms_safety.py` rejects — a
fictional record with a real address typed into it is indistinguishable from any
other, so "the data is fake" is not a control.

The deploy check had the same shape of bug and was worse, because it looked like
protection: `messaging.W001` was gated on `FEATURE_FLAGS["offer_emails"]`, which
is False on CorvinumEU, so the warning could never fire for the client that
needed it.

`core/mail.py` now owns the question of whether and where this environment may
send mail — `assert_recipient_allowed`, `email_configured`, and the list of flags
whose features can email a worker. It has to be core rather than shared between
features: the two senders ship to different clients and neither can import the
other, since importing a non-installed app's services pulls in its models. Same
reasoning that put the upload pipeline in `core/media.py`. The check moved to
`core/checks.py` as `mail.W001`, registered from `core.ui`, and now fires for
payslips as well as offers.

In `send_payslip` the guard sits before the password and the PDF, not merely
before the send. The one-time password exists only in the caller's flash message,
so minting one for a refused send would have a presenter read out a password for
an email nobody received. A refusal raises `PayslipError`, which the existing
view already turns into an error message, leaves `sent_at` untouched so a blocked
attempt never reads as a delivery, and writes a new `payslip.send_blocked` audit
event — previously only successes were audited.

The payslip list also gained the honest disabled state the offer panel has: when
email is unusable the Send button is disabled with a reason, rather than offering
a control that fails at the mail server. `scripts/corvinum_app.sh` forwards
`EMAIL_ALLOWED_RECIPIENTS` and warns when real SMTP is configured without it —
deliberately a warning, not a hard requirement, because empty means unrestricted
and that is correct in production.

Recorded, not fixed: `payslip_send` fetches by pk with no office guard. Not
exploitable today — CorvinumEU creates no `Office` rows so the scope helper
returns its unrestricted sentinel, and Jober has the feature off — but it is real
the moment either changes.

## 2026-08-02 - Job offers reach workers by email, in their own language

Jober could reach a worker by SMS only. `features/messaging` was Twilio-shaped
end to end - `OutboundMessage` stores a phone number, there is no subject, and
`MessageTemplate.body` is sent verbatim, so `Person.preferred_language` was
never consulted. That left no channel for the one message that genuinely needs
long-form text and the recipient's own language, and recruiters were sending
job offers out of band, which put both the content and the fact of the send
outside the system.

The transport stays inside `features/messaging` per the messaging spec's
boundary rule, with its own records rather than a widened `OutboundMessage`:
`JobOffer` (title, project, office, wage, start date, terms), `OfferEmailTemplate`
keyed `(kind, language)`, `OutboundEmail`, and `EmailBatch` so a campaign is one
auditable object. Delivery uses Django's own mail backend - no new dependency,
the same reasoning ADR 0019 applied to Twilio.

Templates are per-language rows, not gettext, because the bodies are
operator-authored; the send picks the row matching the worker's preferred
language and falls back to the site default, then to any active row for that
kind. A wrong-language offer is recoverable, silence is not. This is the first
transport to close the gap `seed_messaging`'s docstring recorded. Substitution
is `string.Template.safe_substitute`, so a typo'd `$token` survives into the
preview instead of raising mid-batch.

Three guards run in order before anything leaves: the worker's own state
(opt-out, blacklisted, no address), then the `EMAIL_ALLOWED_RECIPIENTS`
environment allowlist, then delivery. The first is new relative to SMS, which
consults neither flag - an operational text to someone on shift is a different
act from marketing a job to someone who asked us to stop. `BLOCKED` stays
distinct from `FAILED` for the reason `OutboundMessage` already draws that line.
`Person.email_opt_out` is the Art. 21 objection mechanism and is deliberately
ignored by payslip delivery, which has a different basis.

Two surfaces: a person-card panel (recruiter/coordinator/manager, with SMS's
coordinator narrowing) that renders even when nothing can be sent, with the
control disabled and the reason shown; and a manager-only bulk page that
previews the scoped recipient list, the excluded rows with their reasons, and
the rendered body, then requires a confirmation box. Preview and execution use
the same scoped query - a page that scoped only its preview would show ten names
and email four hundred. Unlike `sms.manage_templates`, `offer_template.manage`
is enforced by a real view rather than left to Django admin.

`EMAIL_ALLOWED_RECIPIENTS` is the execution gate. It cannot be made mandatory
because empty means unrestricted in production, so `manage.py check` raises
`messaging.W001` when outreach is on with a real SMTP backend and no allowlist.
`OutboundEmail` is registered with `core.retention`; the period is unapproved
and the purge is a deliberate no-op until it is set. CorvinumEU gets neither the
flag, the routes, nor the permissions - its design rejects automated worker
notification, and `features.messaging` is not installed there at all.

Two things surfaced while building. The e2e stack turned out to have a
**fourth** copy of the seed order that omitted `seed_messaging` entirely, so the
browser suite had been exercising an empty SMS panel; both seeds are wired in
now. And a seeded offer with no office is visible to Observer alone - unlike a
Person, a non-Person record has no owning-recruiter fallback - which is how the
first e2e run failed and is now pinned by a test.

Not done, and recorded rather than hidden: sends are synchronous like `send_sms`,
so a capped batch of 100 holds the request for 100 SMTP round-trips; there is no
retry, no bounce handling, and no self-service unsubscribe link.

## 2026-08-02 - Help card icons share a complete size vocabulary

The shared icon stylesheet now defines the previously missing `lg` size as a
24×24 glyph. Help cards already requested that size inside their 44×44 icon
tiles, but Jober's SVG backend fell back to the browser's intrinsic 300×150 SVG
dimensions because only `sm` and `md` existed. The oversized glyphs escaped
their tiles and obscured card text. CorvinumEU's Material Symbols happened to
remain 24px through its client font rule and did not exhibit the defect.

The correction is representation-neutral and lives in the existing shared
size vocabulary; it does not branch on client identity or alter either icon
backend. Browser coverage now measures every visible Help-card glyph for both
clients, requires the intended 24px dimensions, and proves each glyph remains
inside its 44px tile. No schema, dependency, translation, or Help content
changed.

## 2026-08-01 - Help becomes a complete two-client workflow guide

The former nine broad Help pages are replaced by a feature-aware registry and
one consistent instructional article template. Jober and CorvinumEU each see
exactly 12 focused cards; unsupported workflows disappear from the index and
return 404 directly. The old Logistics URL remains as an unlisted permanent
redirect to Equipment. Every authenticated role may read Help, while actual
workflow actions retain their existing server-side authorization.

Every card now has an existing client-native semantic icon, a 16:9
client-specific thumbnail, and a one-sentence summary. Articles have purpose,
anchors, permission notes, numbered steps, security boundaries, annotated
screenshots, and filtered related topics. Generic capability checks split
Jober's stock/receipt guidance from Corvinum's return guidance and add the
appropriate readiness and financial material without any client-name branch
inside core.

The committed fictional asset set contains 24 WebP screens and 24 thumbnails,
captured in Slovak for Jober and Hungarian for CorvinumEU. They were generated
through the committed 1440×900 Playwright/Pillow path, reviewed as contact
sheets, and verified for exact dimensions and absent EXIF. No Audit rows, TOTP
screen, payslip password, provider credential, log, or real record is pictured.
All 210 Help msgids have reviewed SK/HU/UK entries, with a dedicated Hungarian
terminology pass. A standard-library PO compiler regenerates the committed MO
files without installing gettext or another dependency. No schema or runtime
dependency changed.

## 2026-08-01 - Dynamic UI labels no longer leak English

The SK/HU/UK page audit found three real localization gaps: occupational-
certificate badge tooltips inserted their canonical English database name into
an otherwise translated sentence; the People filter rendered seeded inactive
reasons without the existing `db_trans` filter; and three Staff activity help
texts had empty translations in every shipped catalog.

Certificate badge rendering now translates the stored canonical name at the
last possible moment. A compliance catalog registers Forklift/Crane/Welding
licence as translatable system labels, while unregistered operator-entered
names still pass through unchanged. The inactive-reason filter now follows the
same runtime-translation convention already used elsewhere. The missing
Slovak, Hungarian and Ukrainian Staff activity translations were supplied and
all three compiled catalogs regenerated. A template guard now rejects new
literal tooltip, placeholder, title and accessible-label attributes unless
they are translated or supplied dynamically. No dependency, schema or stored
data changed.

## 2026-08-01 - Manual upload fixtures now survive a fresh checkout

A curated 15 MB fictional pack now lives under
`tests/fixtures/manual_uploads/`: six avatar inputs spanning JPEG/PNG/WebP and
square/landscape/portrait shapes, two harmless avatar rejection files, and the
essential allowed forklift/crane/welding plus prohibited birth/ID/medical
certificate cases. `SHA256SUMS`, provenance, and a pack README make the binary
set auditable and usable without this workstation's gitignored artifacts.

The large generation originals, processed previews, contact sheet, duplicate
document forms, and ZIP archives remain under gitignored `test-artifacts/`.
This avoids committing roughly 30 MB of duplicate working directories plus 30
MB of duplicate archives while preserving every manual acceptance path. A new
shared avatar runbook covers positive/rejection UI checks, the 25 MB Dokku
prerequisite, detail/list/quick-access rendering, audit/permission checks, and
read-only verification that the server retained only UUID-named 512×512 WebPs
without EXIF or orphans. Certificate and client runbooks now point to the
tracked curated directory. No runtime behavior or dependency changed.

The sixth avatar is an age-appropriate portrait for fictional Mira Novakova,
whose seeded 2009 birth date deliberately exercises the under-18 warning. It
was generated without an input photograph or real-person reference. The source
is a 1254×1254 PNG with no EXIF; the real processor produced a 512×512,
28,256-byte WebP with no EXIF. The acceptance runbook requires confirming that
uploading it does not alter or hide Mira's under-18 warning.

## 2026-08-01 - Dokku proxy ceiling now matches the upload workflow

The shared staging runbook now requires a 25 MB nginx request ceiling for each
client app. This lets Django receive a request containing two certificate files
of up to 10 MB each plus multipart overhead while preserving the stricter
application limits of 5 MB per avatar and 10 MB per certificate file.

The operational detail matters on syncmetric-prime's Dokku 0.38.25:
`nginx:set` changed the computed value but the active file stayed at 1 MB until
`proxy:build-config` regenerated it. The runbook therefore includes rebuild,
validation and active-config inspection, plus a raw-413 diagnostic. After the
correction, all four large generated PNGs used in the manual Jober pass
uploaded and rendered in person detail, the People list and the quick-access
worker panel. Server inspection proved they were stored only as four referenced
512×512 WebPs without EXIF: 77,042 bytes instead of 7,770,049 source bytes,
about 101× smaller, with no originals or orphaned avatar files. Requests above
the 25 MB outer ceiling can still receive nginx's generic 413 page; branded
proxy handling or browser-side preflight remains future UX work. No runtime
code or dependency changed.

## 2026-08-01 - Certificate rehearsal distinguishes translation from recognition

The Jober, CorvinumEU and shared staging runbooks now use one fictional
certificate-upload acceptance matrix. It covers a front/back forklift card, a
single crane PDF, a welding scan, private delivery, audit evidence, the
manager-only purge, and explicit cleanup after an internal wrong-document
probe. The full generated Testovia working pack stays under gitignored
`test-artifacts/`; the curated inputs required by the runbook are now tracked
under `tests/fixtures/manual_uploads/`, so a fresh checkout never needs a real
document or an out-of-band local pack.

The language boundary is now stated precisely. Jober's manual category UI
renders EN/SK/HU/UK and CorvinumEU renders SK/HU, but the uploaded scan is
opaque image/PDF content. There is no OCR, language detection, translation,
field extraction, issuer validation, or automatic category inference. A
foreign-language occupational scan can be stored when a human selects the
right category; a high-risk scan mislabeled as Forklift is not discovered from
its pixels and must be purged. No runtime behavior or dependency changed.

## 2026-08-01 - Goods-receipt scope tests stop depending on today's month

The first post-merge CI run after midnight on 1 August exposed two tests whose
fixtures were fixed in July but whose page request silently used the current
month. The goods-receipt view correctly defaulted to August and returned no
July rows, so the office-scope assertions failed even though the scoping code
had not changed.

Both tests now request July 2026 explicitly. Their subject is office visibility,
not the default-period behavior, which already has dedicated coverage in the
reporting-period suite. This keeps the acceptance fixtures stable across month
and year boundaries without changing application behavior.

## 2026-07-31 - Hungary joins accountant handoff as a separate rulebook

The product-owner follow-up supersedes the Slovakia-only boundary recorded
below: future accountant handoffs may support **Slovakia and Hungary**, but as
two versioned country schedules, never one blended export. Each employment must
resolve to an approved employing entity and explicit `SK` or `HU` jurisdiction;
an office label, nationality, address, or UI language cannot choose it.

The Hungarian baseline now records NAV's current `08E` structured identity and
employment fields and the 2026 family-tax-allowance advance-tax declaration.
The normal family-tax input is the declaration and required dependant/
co-claimant facts, not a standing birth-certificate archive. Hungarian medical
fitness remains outside ordinary payroll: the employer gets the conclusion and
necessary restrictions, while the reason for unsuitability is not disclosed to
the employer without written consent.

Mixed, posted, unresolved cross-border, third-country, and uncertain cases
still fail closed to a human legal/payroll process. No export, jurisdiction
model, family-benefit model, or real-data path was implemented in this
documentation slice.

## 2026-07-31 - Accountant handoff is facts, conditional evidence, not a worker-file export

The platform now has a researched Slovak baseline for what may flow to an
external payroll accountant. Recurring payroll is an allowlist of structured
facts. A child's birth certificate is relevant only when the worker makes the
particular tax claim, with the signed declaration and only the evidence that
claim requires. An identity document may be used to verify identifiers, but
its image is not a routine payroll input. Medical examination details stop at
the clinician; the employer's restricted fitness conclusion is not part of the
ordinary accountant export.

This closes an important potential loophole in the document-storage decision:
“the accountant needs it” does not permit Jober or CorvinumEU to upload and
relay excluded scans. Required source evidence stays in a separately approved
employer/accountant custody and secure-transfer process; PeopleOps may retain
only approved verification metadata. No export or family-benefit data model was
built in this documentation slice.

The product owner subsequently fixed the jurisdiction boundary at **Slovakia
only**. Jober's Győr label remains an operational office, not permission to run
Hungarian payroll rules. Non-Slovak, posted, cross-border, and uncertain cases
must be refused rather than approximated. C-Q19 and Jober's decision register
still require the client, payroll owner, and legal/privacy reviewer to confirm
the employing entity, recipient role/DPA, exact Slovak forms and fields,
evidence custody, transfer, and retention before real data or implementation.

## 2026-07-31 - Telegram is a channel broadcast, not imaginary per-worker delivery

The Jober Telegram direction is now one coherent design. A client-owned bot may
post human-approved Ukrainian text to one configured private Ukrainian-worker
channel. It extends `features/messaging`; it is not a separate Telegram module,
worker portal, chat-ID registry, inbound feedback bot, or SMS fallback engine.
The earlier “manual channel, no bot” answer and still older per-worker bot design
are explicitly historical rather than competing implementation instructions.

Telegram and SMS keep honest domain semantics. SMS remains person-addressed and
Coordinator-project-scoped. Telegram records one channel post and never claims
subscriber, person-level delivery, read, project, or opt-in evidence. Because a
common channel crosses those person/project boundaries, the new
`telegram.broadcast` action is designed as Jober Manager/Admin-only.

The v1 boundary is outbound text with exact preview/confirm, low-sensitivity
general announcements, human-approved Ukrainian, minimum bot rights, separate
test/production bot+channel, Doppler-injected token, audit, and no webhook. The
design handles the dangerous timeout case explicitly: Telegram has no
application idempotency key, so an uncertain result becomes `unknown` and is
never retried automatically.

Implementation remains blocked on the client confirming a private single
channel, Manager-only posting, content/retention and DPA treatment, Ukrainian
approval, bot ownership/recovery, test+production access, token rotation, and
the comments/discussion policy. No runtime behavior changed in this
documentation slice.

## 2026-07-31 - Occupational certificates, without becoming a document vault

The shared Jober/CorvinumEU compliance feature now stores files only for three
occupational qualifications: forklift, crane and welding. The narrower boundary
is deliberate. Identity cards, passports, birth/residence papers, financial
records, medical reports and health-certificate scans remain metadata-only or
outside the base platform; if a client insists on those files, the answer is a
separately scoped Secure Document Vault with its own threat model, legal basis,
key management, retention, backups and operating budget.

The production trust boundary is explicit too: the base platform does not
encrypt each certificate with an application-managed key. Django protects the
web delivery path, but root on the active VPS can read the mounted media volume;
provider/full-volume encryption does not change that while it is mounted. Real
certificate scans remain blocked until volume encryption and key ownership,
privileged-host access, per-client isolation, encrypted off-site media backups,
a restore drill, and acceptance of that residual root-access risk are reviewed
and recorded. A requirement to hide files from the application-host
administrator belongs in an application-level key-isolation or Secure Document
Vault project.

The workflow accepts one sanitized PDF, one image, or ordered front/back images.
New records need a file and either an expiry date or “does not expire.” Renewal
creates a new active row and supersedes the old one; archive preserves history
and files. There is no ordinary hard delete. A new manager-only emergency purge
requires a reason, permanently removes bad/wrong-person files, archives the row
and preserves its audit metadata.

The allowlist is enforced in the form, service and model, not merely taught in
the UI. Images are decode-verified/re-encoded without EXIF. PDFs are capped at
four pages, must be unencrypted and non-interactive, and are rebuilt from their
pages. File delivery retains the office plus per-person sensitive-data check;
the row can be a broad operational read while its scan remains restricted.
Mutations audit before/after values and file presence.

Migration `compliance.0003` preserves the original primary file by renaming its
field, adds front/back and renewal/history fields, and maps legacy undated rows
to “does not expire.” `enforce_certificate_storage_policy` is dry-run by
default; its purge mode has an explicit fictional-data confirmation because the
real-data gate is still closed.

Two deliberate omissions are worth stating. There is no verification queue:
an added occupational certificate is immediately active. Expiry alerts remain
advisory and do not block trial, assignment or activation. Both can change only
after an explicit business decision, not by accident in a migration.

The browser lane uploads and reopens both sides of a fictional card in both
clients. Its Corvinum path uses HR Admin and completes the client-mandated TOTP
setup before exercising the shared workflow.

Suites: 908 Jober passed (8 skipped), 538 CorvinumEU passed (15 skipped), and
52 browser tests passed.

## 2026-07-28 - The status rail's fetch was racing the tooltip

An unrelated e2e tooltip assertion failed in CI while passing locally, twice
over. The mechanism is mine: `app.js` hides any open tooltip on
`htmx:beforeSwap`, and the worker status rail fetched its contents on htmx's
`revealed` trigger. `revealed` fires unpredictably for an element that starts
hidden, so on a slower machine the rail's swap could land mid-hover and dismiss
the tooltip the test was asserting on.

Fixed by making the fetch explicit: the toggle dispatches a `workerRailOpened`
event the first time the rail is opened, and `hx-trigger` listens for that
instead. Deterministic, fetches nothing until the rail is actually used, and
removes the race rather than retrying past it.

Worth recording because the tempting response to a green-locally/red-in-CI test
is to re-run it. Re-running would have worked most times, and the flake would
have stayed.

## 2026-07-28 - SMS templates seeded, and the language gap that exposed

Item 16 read as "templates cannot be managed in the product". The larger half
was simpler than that: **none were seeded**, and the SMS panel hides its picker
behind `{% if panel.message_templates %}`. So the control never appeared at
all, and the demo runbook's "pick a template" step had nothing to pick. It
looked like a missing feature; it was missing data.

Three templates now seed via `seed_messaging`, added to `dev_app.sh` and both
staging seed lists. Idempotent on `name`, so a reseed repairs an edited body
rather than accumulating near-copies - seeds re-run on every staging deploy.

Written as messages a coordinator would actually send. A template nobody would
send teaches a demo audience nothing.

**Seeding them surfaced a real gap, recorded as backlog item 17.**
`features/messaging/views.py` sends `template.body` verbatim, and messaging
never reads `Person.preferred_language` - which exists and is populated. The
workforce is Ukrainian, Hungarian, Slovak and Vietnamese, so a single-language
template reaches people who cannot read it. The seeded bodies are Slovak, the
company's operating language and the app default: the least wrong single
choice, not a solution. Fixing it properly needs the client to say which
languages he actually sends in, so it is a question rather than a task.

Management stays in Django admin, so `Action.SMS_MANAGE_TEMPLATES` remains
unenforced and item 16 is only partly closed.

Suites: 901 Jober, 529 CorvinumEU.

## 2026-07-28 - Project management (production-readiness item 15)

A manager could not create a project. `Action.PROJECT_MANAGE` was granted to
Manager in both clients and implemented nowhere; the only ways in were the demo
seed, a shell, or Django admin - which needs a superuser no client role has,
bypasses the service layer, writes no audit event and honours no office
boundary. The client intends to enter a whole project on his trial instance, so
he would have hit this in his first ten minutes.

Create, edit and deactivate/reactivate, mirroring the accommodation pattern -
same shape, so `apply_office_scope()` and the existing
`_assert_project_in_scope()` were reused rather than reinvented.

**The backlog entry was half wrong, and the truth is worse.** Item 15 described
a misleading "Manage projects" button linking to the read-only list. That
button lives in `templates/pages/dashboard.html`, which **no view renders** -
the `dashboard` URL delegates to `reports()`. So it was not misleading, it was
invisible, and `reports.html`, the page a manager actually lands on, had no
project entry point at all. The create link now sits there and on the project
list.

Two decisions worth recording:

- **Deactivate, never delete.** `ProjectAssignment`, `TrialAssignment`,
  `FinancialMonth` and `TransportWeek` all `PROTECT` their project, so a used
  one cannot be removed and offering deletion would only fail at the database.
- **The coordinator picker is restricted to the chosen office**, in the
  queryset *and* in `clean()`. The demo seed had exactly this bug until
  2026-07-26 - a coordinator formally responsible for projects they get a 403
  on. A hand-built form is the obvious place to reintroduce it.

The office field is validated by its queryset, not just narrowed for display:
posting another office's pk is a field error, and a test posts one to prove it.

Suites: 897 Jober, 529 CorvinumEU. Form captured and reviewed - fully
translated, office pre-selected, and only the selected office's coordinator
offered. Two cosmetic items noted, neither introduced here: the page-head
Cancel button sits under the fixed notification bell (true of every page with a
right-aligned head button), and the finance checkbox row is cramped.

## 2026-07-28 - J6: Jober stops taking equipment back

The client was unambiguous - "what we issue, stays out" - and the owner
confirmed it. Returns are now per-client.

Done the way the transport removal was, and for the same reason: **the route is
not registered** for a client whose `equipment_returns` flag is off, rather
than registered and 403'd. A route that 403s is still a route to maintain, and
a URL that does not exist cannot be reached by guessing. Models and migrations
are untouched, so previously returned items still read correctly - nothing is
deleted, only the path forward is closed.

CorvinumEU keeps returns, the recovery review and the linked ledger deduction.
That is asserted positively rather than inferred from a green lane: the
CorvinumEU suite gained a test that the route *does* resolve there, and its
count moved 518 -> 519 while Jober skips it. A global removal would have
satisfied every Jober assertion while silently breaking the other client.

`tests/test_view_gating.py` lost its `return_equipment` row. Parametrizing a
route that is not registered fails at `reverse()` rather than testing a gate;
the RBAC coverage moved to the new file, where it runs for whichever clients
still have the route.

**Two things deliberately not done, both flagged rather than guessed:**

- **The manager recovery review queue stays.** The fix list said to flag it
  rather than remove it unilaterally, and nobody has said it should go.
  Flagging an item unreturned and charging or waiving it is a distinct action
  from taking equipment back, so it still functions. If the client agrees
  nothing is ever expected back, it is the obvious next thing to retire -
  recorded in runbook §7 as a question to ask him during that section.
- **The "receipt-total tile" was not removed.** The fix list says to remove the
  "20 units / 730 EUR" figure, but question 1 of the open-questions doc records
  him *confirming he wants* the item list plus the current total value - which
  is what the warehouse page's two tiles show. Removing the wrong one deletes
  something he asked for. He needs to point at it.

Suites: 879 Jober, 519 CorvinumEU, 50 e2e.

## 2026-07-28 - Finance manual entry gets its own panel

The month-recording form sat at the bottom of the "Financial months" list, so
the way you *create* a month was appended to the list of ones that already
exist - findable only by scrolling past them. It is now its own panel directly
under the page head, with a line saying plainly that every figure is typed by
hand and only the totals are calculated.

That sentence is worth having on the page rather than only in the runbook. The
client's stated reason for wanting manual entry is that he does not trust a
system to invent numbers; the screen should say what it does rather than leave
him to infer it.

**The screenshot pipeline caught the new strings shipping in English.** The
existing field labels rendered as PROJEKT / ROK / MESIAC because they were
already translated; my three new ones - the eyebrow, the heading and the
explanatory line - rendered as English inside a Slovak page. That is the exact
failure this area had before, and it was invisible to 875 passing tests. Caught
by capturing the panel and looking at it, fixed, and re-captured to confirm.

Suites: 875 Jober, 519 CorvinumEU, 50 e2e.


## 2026-07-28 - Seeded people belong to their own office's recruiter

Verifying J2 on staging showed the staff-activity table listing one recruiter
with all seven people and two with none. The zero rows were correct and are
deliberately kept - but the report exists to reveal *a gap between two working
recruiters*, and seed data where only one recruiter has ever done anything
cannot demonstrate that.

Every seeded person was attributed to the Velký Meder recruiter regardless of
their office. This is the same defect corrected for project coordinators on
2026-07-26, which left the Velký Meder coordinator formally responsible for
four projects they get a 403 on; the reasoning transfers directly and the fix
mirrors it.

The correction also **repairs existing databases** rather than only new ones.
`get_or_create(defaults=...)` applies on creation alone, so without an explicit
repair pass every demo instance already in existence - staging included - would
keep the old attribution however often it was reseeded. The seed already had
exactly this pattern for `office`; this follows it.

Two tests guard demo properties rather than code paths, because nothing else
would notice either: that seeded people span more than one recruiter, and that
re-running the seed fixes a database whose attribution was collapsed onto one.

Suites: 875 Jober, 517 CorvinumEU.

## 2026-07-28 - J9 second slice: the Help screenshot pipeline, and what it caught

The Help area's one existing "visual" is a hand-built HTML mock of the
navigation. The plan's core argument is that a mock drifts from the product
while a screenshot cannot - and the very first capture proved the point
immediately.

**The first screenshot found a defect in the worker status rail merged an hour
earlier.** Collapsed, the rail was an 18rem fixed box anchored below the
notification bell - directly on top of the People page's Search button, which
could therefore not be clicked. 851 unit tests and 50 browser tests were green
throughout, because none of them looks at whether one element covers another.
The rail is now anchored bottom-right, the one corner no page competes for, and
collapses to its own width instead of reserving space for content it is not
showing.

The pipeline itself:

- **`scripts/capture_help_screens.sh`** reuses the e2e harness rather than
  duplicating it - `playwright_e2e.sh` gained an `E2E_PYTEST_ARGS` hook, so the
  capture job runs against the same built apps and seeded databases the test
  suite drives. Regeneration is one command, which is the only way screenshots
  stay true.
- **Captured in Slovak**, the default and the language most users see. The
  app's chrome is therefore in one language; the numbered callouts beside each
  figure carry the explanation in the reader's language, which is exactly why
  the illustrations that accompany them must stay textless.
- **`COPY static/help /app/static/help` in the Dockerfile.** Static
  subdirectories are copied individually, so a missing line means files that
  exist in git and 404 in production - which has already happened once, to the
  avatars. A test asserts the line is present.
- **Tests guard the properties that failed last time**: every referenced asset
  resolves through `staticfiles.find()` rather than merely producing a URL;
  every `<img>` carries translatable alt text; no illustration is
  per-language, because a label baked into a raster can never be translated.
  They are written to pass with zero images so the scaffolding lands before the
  assets.

**Still needed from the owner:** the textless illustrations. The generation
prompts are in the plan; I can capture screens but not draw rasters.

Suites: e2e 50 green after the rail fix.

## 2026-07-28 - J8: the persistent worker status rail

An always-visible list of workers and their current state, with the
notification centre in the same rail region, as the client asked.

Three constraints in the brief drove the shape, and each of them turned out to
have an existing answer in the codebase rather than needing a new mechanism:

- **"Must not become an N+1 query on every page render. Cache or defer-load
  it."** The notification centre already defers its contents through `hx-get`
  and re-fetches on an event; the rail does the same. An ordinary page ships
  the rail's shell and none of its data, and the fragment costs a constant
  number of queries. The test asserts *that*, not a magic number: resolving the
  office scope is its own query and a legitimate constant, so what is pinned is
  that twenty workers cost what one does.
- **"Corvinum's status vocabulary is the candidate pipeline, not
  working/not-working. Drive the labels from the client's lifecycle
  configuration."** Both clients in fact share `LifecycleStatus` - CorvinumEU
  simply enables `TRIAL_DAY` - so rendering from its choices through the same
  `status_pill` the People list uses satisfies this by construction. The brief
  implied Corvinum needed a separate vocabulary; in the code it does not, which
  made this simpler than written.
- **"Scoped exactly like the People list."** `scope_people`, which also covers
  the coordinator case the brief calls out. The status counts above the list are
  scoped too - a summary over a scoped list that is not itself scoped is the
  precise bug that shipped three times this week, so it has its own test.

Capped at 60 most-recently-updated with an explicit "open People" link rather
than paginating: the rail is a glance, not a directory, and an uncapped list
would degrade quietly as the workforce grows.

**The rail is collapsed by default, which is a deliberate deviation from
"always-visible", and e2e is what forced the question.** The first version was
a fixed overlay; it covered page content and intercepted a click, failing a
CorvinumEU test. Reserving a 20rem gutter fixed that and then failed a second
test that pins CorvinumEU's content width - correctly, because the gutter
narrows every page by 320px. CorvinumEU centres a 1280px column beside a 280px
sidebar, so at a 1650px viewport there is simply no width to give away, and
imposing that on a client who never asked for the rail is a worse outcome than
one click. Expanded, it still reserves the gutter rather than floating over
content; collapsed, it costs nothing and does not even fetch (`hx-trigger`
is `revealed`). The state is remembered per browser.

Worth raising with the client: he asked for always-visible, and this is
one-click-away instead. The brief invited the trade ("pick one and justify it
against the existing sidebar layout"), but the justification is a real
constraint rather than a preference.

**The person-card icons the brief also mentions were deliberately not guessed
at.** The current indicators are written up as question 4 of
`docs/product/jober-open-questions-july-2026.md` for the client to choose from -
including the fact that the blacklist indicator he listed as confirmed-working
is a banner on the person *detail* page, not an icon in the people list.

Suites: 851 Jober, 510 CorvinumEU.

## 2026-07-28 - J9 first slice: Help articles now match the client's feature set

The visual-aids plan for J9 flagged this as production-readiness item 10, and
it turns out to be a defect rather than a nicety: `HELP_GROUPS` shipped every
article to every client, so a CorvinumEU user was offered - and could open -
articles explaining Feedback, Finance reports and accommodation, none of which
that client's app has.

Documentation for a feature you cannot reach is worse than no documentation. It
reads as something broken or missing rather than absent by design, and it is
the kind of thing a client finds in the first ten minutes of a trial.

- Articles declare the flags they depend on and appear when **any** is on,
  because an article can legitimately span features: Logistics covers
  accommodation, equipment and transport, and CorvinumEU has only the middle
  one - the article is still worth reading there.
- **The gate is a boundary, not decoration**: a hidden article 404s by URL as
  well as vanishing from the index. A URL survives in a bookmark or a chat
  message long after the index stops linking it.
- **Still not role-gated.** The design doc is explicit that every role gets
  documentation, and a test pins that so the flag gate cannot quietly become a
  permission gate.
- This also removes the need for client-conditional screenshots in three of the
  nine articles, which is why the plan put it first.

Two things worth recording about how this was built:

**Mutating `settings.FEATURE_FLAGS` in a test rebuilds the URLconf.**
`config/urls.py` registers routes per flag at import time, so a test that
flipped a flag to check a Help article silently unregistered unrelated URLs and
failed somewhere else entirely. The tests patch the flag *lookup* instead, and
the fixture says why.

**The CorvinumEU lane caught what the Jober lane could not.** Three existing
tests asserted that every article renders; under CorvinumEU they now correctly
404. Jober has every feature, so its lane was green throughout - the whole
argument for running both.

Suites: 850 Jober, 510 CorvinumEU.

**Still outstanding for J9:** the screenshots and illustrations themselves. The
plan at `~/.claude/plans/` has the generation prompts; capture needs a
`scripts/capture_help_screens.sh`, a `COPY static/help` line in the Dockerfile
(subdirectories are copied individually), and a staticfiles-discoverability
test mirroring `test_default_avatar_file_is_actually_discoverable_by_staticfiles`.


## 2026-07-28 - J2: staff activity statistics, and two field checks I got wrong

The client accepted that the audit log is traceability rather than reporting,
then asked for the reporting separately. This is its own page - `Staff
activity`, beside Audit in the nav in both shells - rather than another filter
on the log.

**I twice reported a field as missing that was already there.** Checking
`EquipmentIssue` with a line-range window that stopped at 300 hid `issued_by` at
304; checking `RoomAssignment` the same way hid `assigned_by` and `created_at`.
On the strength of the first error I asked the owner to choose between adding a
field with a backfill and reporting off the audit log, and they picked the
field - a decision that was never needed. Both facts were already recorded on
the domain models, so **J2 needed no migration at all** and the fix list's
"models untouched if possible" was achievable as written. Reading the whole
class, not a line window, is the fix.

That the data lives on the models rather than only in the audit log matters for
a reason beyond convenience: `core.retention` will eventually purge audit rows
for GDPR, and statistics built on the log alone would quietly empty themselves.

- **Recruiter productivity** comes from `core.people`, so it lives in core.
  Every recruiter is listed **including those who registered nobody** - the
  stated purpose is spotting a large gap between two recruiters, and a table
  that drops its zero rows cannot show a gap.
- **Equipment issuance and accommodation transfers** come from a feature's own
  records, so they arrive through a new
  `register_staff_activity_panel` registry slot rather than core importing
  logistics. The period reaches them on `request.reporting_period`, because the
  registry calls every contribution with `(request)` alone and growing that
  signature per consumer would be worse.
- **A first placement is not a transfer.** Only a move between accommodations
  counts, and the previous accommodation is read from the worker's earlier
  assignment rather than stored - no denormalised trail.
- Office-scoped throughout, including the headline counts, and gapped periods
  are respected: January+March does not count February.
- RBAC: new `staff_activity.view`, manager and observer only, mirrored in both
  clients' permission matrices.

Suites: 828 Jober, 503 CorvinumEU.

## 2026-07-28 - J5: the goods-receipt log, which needed no new model

The client demonstrated the gap live: after receiving 3 helmets and 2 boots he
could see the new totals but could not answer "what did I take in today?".

The fix list said to check whether the receipt header is persisted before
adding a model. It is - `receive_stock()` has been writing
`EquipmentStockReceipt` and its lines since the warehouse slice, and nothing
ever read them back. So this is a read view over existing records: **no model,
no migration.**

- **List and detail**, newest first, with supplier, reference, office and who
  recorded it. Totals are summed from the lines rather than stored, like every
  other money figure here, so a receipt can never disagree with what it
  contains.
- **Period filtering reuses J7's control** rather than a fourth month picker,
  which is the whole reason J7 came first.
- **Office-scoped from the first commit, list *and* detail.** A receipt names a
  supplier, a reference and a value belonging to one office. After three leaks
  of exactly this shape in one week, the `_assert_receipt_in_scope` guard went
  in with the feature rather than after it, with a companion test asserting a
  manager can still open their *own* office's receipt - a blanket 403 would
  satisfy the leak test while breaking the feature.
- **The seed now spreads receipts across two months.** Every seeded receipt
  previously carried the same date, four days before the current month starts,
  so the default current-month view showed nothing and only a year selection
  revealed anything. That reads as missing data rather than as an empty period.
  A second, smaller top-up receipt two months earlier makes both the log and
  the period filter demonstrable.

Suites: 818 Jober, 493 CorvinumEU.


## 2026-07-28 - The audit backfill only reached 8 of 900 events

Deploying J1 and checking it against the real staging database, rather than
against a freshly seeded test one, showed the fix had not actually fixed the
client's complaint. Searching the audit log for a worker still returned **zero
rows** for every account.

The migration attributed **8 of 900** events. Its own docstring said why - a
data migration works with historical models that carry no relations, and `core`
must not import `features` to learn that an `EquipmentIssue` has a `.person` -
but the consequence was underestimated when it was written. `equipment.issued`,
`room.assigned`, `blacklist.proposed`, `trial.scheduled`, `sms.sent`: none were
attributed, and those are exactly the events a manager means by "what happened
to this worker?". Only `person.lifecycle_changed`, where the target *is* the
person, came through.

A management command has what a migration lacks: real models. Resolving
`target_type` through the app registry needs no core-to-feature import, and the
resolution rule is the same one `record_event` applies to new events, so
history ends up attributed the way the future already is.

Verified against the real staging data before writing it, as a dry run: **25
further events** would be attributed, all of them worker actions. What stays
unattributed is correctly impersonal - 738 finance line items, 108 financial
months, receipts, rooms, cost periods - plus two `ActivationApproval` rows
whose target no longer exists, because a consumed approval was deleted during
last week's verification. A person deleted since the event was written also
stays unattributed rather than pointing at a recycled primary key.

**This is a deploy-step change, not just code:** the command has to be run after
migrating any database that carries history. Recorded in the deployment runbook.

The general lesson is the one this week keeps repeating: the local test passed
because it created its events through `record_event`, which resolves
attribution correctly. Only pre-existing rows were broken, and only a real
database has those.

Suites: 814 Jober, 493 CorvinumEU.


## 2026-07-28 - J7: one reporting-period control, and what J10 actually was

The client could not ask for "the whole of 2026" - selecting a year collapsed
back into a month picker - and could not report several months together. The
fix list is explicit that this must not be built three times, because J5
(goods-receipt log) and J2 (staff activity) need the same granularities.

- **`core/reporting/periods.py` resolves a period, and nothing else.** No
  database, no model knowledge: `filter_q(field_name)` hands the caller a `Q`
  for whichever date column they store, so the same period can filter stock
  movements, receipts, person registrations or room assignments. Bad input
  falls back to the current month rather than raising - these values come from
  a query string a user can edit, and a report that 500s on a typo is worse
  than one showing this month.
- **Several months means several months.** Owner decision: a selection of
  January and March resolves to two disjoint ranges, never
  January-through-March. Silently widening a gapped selection is the same class
  of surprise as the bug being fixed. Adjacent months are merged, so the common
  contiguous run still costs one range and one `BETWEEN`, and `is_contiguous`
  stays honest for any caller doing span-based arithmetic.
- **Opening and closing balances are gone** from the warehouse report, on the
  owner's call. They were also the figures with no clear meaning across a
  gapped selection. The two tests that asserted them were rewritten rather than
  deleted - both were really asserting that history is immutable, which is a
  property of `equipment_stock_balance(as_of=...)` and is still covered.

**J10 was not a translation problem.** I reported it earlier as substantially
done because the catalog is correct - `Issue` is `Kiadás`, `Receipt` is
`Bevételezés`. That assessment was wrong. The warehouse template rendered
`{{ kind }}`, the **raw enum key**, so the page printed a literal lowercase
"receipt" and "issue" in every language while the correct labels sat unused in
the catalog. Translating it again would have fixed nothing. The report now
carries `label`, and a test loads the page in Hungarian and asserts
"Bevételezés" is present and the raw key is not.

Also caught by an existing repo rule rather than by me: my first draft used
multiline `{# ... #}` comments, which Django renders as **visible page text**.
`tests/test_shell.py` failed on it. Rewritten as `{% comment %}` blocks.

Suites: 805 Jober, 493 CorvinumEU.

## 2026-07-28 - Sweeping the aggregates for the ADR 0026 blind spot

Three office-scoping leaks had shipped and every one was found while doing
something else - a dashboard tile summing every office's rooms, the audit log,
and the accommodation cost report two days ago. That is a pattern, not three
coincidences, so this slice went looking on purpose rather than waiting for the
fourth.

The blind spot is structural. Scoping has two enforcement points: a filter on
every list, and an `_assert_..._in_scope` guard on every view taking an object
pk. An aggregate falls between them - it opens no single record, so no guard
fires, and it does not look like a "list", so the filter gets forgotten.

Found and fixed:

- **The equipment deduction review queue was unscoped, and it is a write.**
  This is the serious one. `pending_deduction_reviews()` returned every
  office's flagged issues, so a Velky Meder manager saw Gyor workers' names and
  charge amounts - and `review_deduction_view` had no scope guard at all, so
  posting another office's issue pk **approved a money charge against a worker
  in an office they cannot otherwise see**. Verified before fixing: the probe
  posted the pk and the review status changed. Both the queue and the decision
  are now scoped, the latter with `_assert_person_in_scope`.
- **The queue total, the nav badge count and the notification** all read the
  same unscoped queryset, so each leaked a cross-office figure on its own.
- **The `Equipment value` dashboard tile** summed every office's issued
  equipment. Reachable only when the stock ledger is off, which is not Jober's
  configuration today - but it is one setting away.
- **Finance would 500 on a tenant with no offices.** `user_office_scope`
  returns `None` both for an unrestricted caller *and* when no `Office` rows
  exist at all; `finance_summary` handled only the first reading and passed the
  sentinel into `office__in=`, which raises. Not hypothetical: an office-less
  instance is exactly the empty one the client asked to be handed for their
  trial (J11), so a manager opening Finance before creating an office got an
  error page. Two call sites, both now guarded like `finance_year` already was.

Deliberately not changed: `accommodation_cost_report()` (the legacy room-rate
report) is also unscoped, but it has **no callers** - dead code retained "for
historical records and other clients". Deleting it is a separate decision, and
scoping a function nobody calls would only make it look maintained.

Services that aggregate now take `user` as a **required** argument rather than
an optional one. An optional scope is a leak waiting for the next author, and
that is precisely how these accumulated.

Suites: 752 Jober, 449 CorvinumEU.

## 2026-07-28 - J3: the accommodation cost report, five figures and a leak

The client gave a worked example on the handover call - capacity 18 at 180
EUR/head, three workers, one of them alone in a two-bed room paying 230 - and
the fix list carried his diagnosis with it: "occupied beds renders 15, i.e.
capacity minus occupied; the counter is inverted." Building his fixture against
the current code first, as the list itself asked, showed the diagnosis was
wrong and one of the other figures was wrong instead.

- **There is no inverted counter.** The page showed `occupied_days`, correctly
  labelled *Occupied bed-days*, and three workers across a month is 93. The
  client read a bed-day count as a bed count. Both 18-3 and a partial-month
  bed-day sum can land on 15, which is why the hypothesis looked sound. The fix
  is a head count (`occupied_beds`), not a sign flip.
- **Empty-bed loss was genuinely wrong**, and nobody had reported it: it read
  `standing - occupied_cost` and never subtracted worker payments, overstating
  the loss by exactly what the workers pay. His fixture makes it 2700 where it
  should be 2370.
- **The zero floor stays, deliberately.** Taken literally the client's formula
  goes negative whenever a house is full - standing cost then equals occupied
  cost, leaving `-payments` - and a figure labelled "loss" must not read -150
  for a fully occupied hostel. Floored at zero, with a test that pins it.
- **Occupancy counts people, not beds withdrawn from circulation.** The worker
  who pays 230 to keep a twin room to himself counts as one, and the bed he
  funds reads as empty. That is the client's own stated definition; it is left
  as a TODO in the service and an open question for him, because a
  paid-for-but-empty bed arguably belongs in a different report.
- **Margin and the internal occupied-cost term are off the card**, on request.
  Occupied cost stays in the returned data so the arithmetic is testable and so
  the runbook can explain the formula; it is simply not rendered.
- **The report had no office scoping at all** (ADR 0026). It opened no single
  record, so the `_assert_..._in_scope` guards beside it never fired - yet it
  listed every office's residences and summed them into one company-wide bar. A
  Velky Meder manager could read Gyor's and Dunajska Streda's capacities, costs
  and worker payments. This is precisely the aggregate leak the convention
  warns about, and the second one this week. The service now takes `user` as a
  **required** argument rather than an optional one, so the next aggregate
  cannot omit it by default.

Suites: 744 Jober, 449 CorvinumEU, e2e green. Runbook section 5 rewritten - it
described margin, which no longer exists.

## 2026-07-27 - J1: the audit person filter, and the office scoping it never had

The client reported the audit person filter as "returns no rows". The fix list
hypothesised that office scoping had introduced a join that eliminated them.
Reproducing it first showed something different and larger.

- **The filter matched `target_type="Person"`**, so it found only events whose
  *target row* was the person. A certificate upload targets the Certificate; an
  equipment issue targets the EquipmentIssue; a blacklist proposal targets the
  case. All are events *about* a worker and none were findable. A manager
  asking "what happened to Diana?" got a fraction of the answer and reasonably
  concluded the filter was broken. Verified by recording two events about one
  person and watching the filter return one of them.
- **`AuditEvent.person` now attributes each event to the worker it concerns**,
  resolved in `record_event` from the target being a Person, the target hanging
  off one (`.person`), or an explicit `person=` kwarg that several call sites
  already passed. Attribution is best-effort and returns `None` rather than
  raising: audit writes sit inside business transactions, and recording history
  must never be the thing that fails an operation.
- **The data migration backfills historical rows**, because without it the fix
  works only for events recorded after deployment - which on any real database
  looks exactly like not having fixed it. Verified on legacy-shaped rows: a
  person filter that found 0 finds 2 afterwards, and genuinely unattributable
  rows are left alone rather than guessed at.
- **Diacritics were a second, independent bug.** `search_name` stored
  "horváthová" verbatim, so typing "horvat" matched nothing. Slovak and
  Hungarian names carry accents that people routinely omit at the keyboard.
  Fixed with a folded `Person.search_fold` column, and **People search now uses
  it too** - the two surfaces disagreeing about what a name is would be its own
  bug.
- **The normalizer was moved, not rewritten.** The blacklist already had one,
  but `core` may not import `features` (ADR 0021), so it moved to
  `core/people/naming.py::fold_name`. It feeds HMAC fingerprints: changing what
  it returns silently invalidates every stored fingerprint and **fails open** -
  a barred person stops matching and is quietly admitted. Moved byte-identically
  and confirmed against the existing blacklist suite before going further.
- **The audit log had no office scoping at all** - the fix list only guessed at
  this. A Velky Meder manager could read every action taken on Gyor and
  Dunajska Streda workers. That is the fourth surface in this class after
  messaging, compliance and feedback. Attributed events are now scoped;
  unattributed ones stay visible to everyone, because they are configuration
  and system actions carrying no worker's data and hiding them would blind a
  manager to their own app's history for no privacy gain. The decision is
  asserted in a test rather than left implicit, per J1's instruction to decide
  explicitly.

## 2026-07-27 - Finance manual workflow documented; J4's premise corrected

The July interview fix list (`docs/jober-fix-prompts-to-do-before-demo.md`)
carries J4: "the Finance page derives its figures from system data (headcount,
inventory, accommodation) - remove every automatic derivation". Checked before
building it, and **there is nothing to remove**: `set_line_item()` stores a
hand-typed amount, `recompute_month()` only sums line items, and
`features/profitability/` imports nothing from people, logistics or accommodation.

- The likeliest explanation for what the client saw is the **seeded demo data**
  - 54 pre-filled months that look auto-populated but were written by
  `seed_finance`. On the clean trial instance he asked for (J11) the pages
  start empty, which may resolve the complaint on its own.
- Marked J4 in the fix list as premise-wrong rather than deleting it, listing
  what genuinely survives: the workbook inputs-vs-computed question, the
  "one chart" request against several currently on the page, and the
  `202510`-versus-`November 2025` discrepancy.
- **Documented the manual workflow as runbook §6a**, because a hands-on tester
  needs the operating instructions and the demo script only covers what to
  point at. The section leads on the one genuine trap: **saving line items
  recomputes the month from those items and replaces the headline revenue and
  cost typed when the month was created.** Somebody entering a total and then
  its breakdown will watch their number change, and without that sentence it
  reads as data loss rather than as the mechanism that makes the spreadsheet's
  off-by-one impossible.
- Also documented that costs must be typed **negative** exactly as the workbook
  has them, and that the rejection of a positive cost is deliberate - it is the
  only thing preventing a cost being booked silently as revenue.
- **Corrected the fix list's own conventions preamble**, which told agents that
  Django apps live under `apps/`. That layout has not existed since ADR
  0021/0022; anyone pasting those prompts verbatim would send an agent hunting
  directories that are not there.

## 2026-07-27 - Activation now needs two people (readiness item 14)

Activating a worker is the moment Jober commits - the person is on a client
site, accommodation is booked, equipment is issued, billing starts. The design
specified a manager approval on that step and both permission matrices promised
it; it was never implemented. Demonstrated before starting: one coordinator
went Available -> trial -> readiness -> **WORKING** with nobody else involved,
because `activate_person` was gated by `project.assign` and the Activate button
by `readiness.complete`, both of which coordinators hold.

- Built as the **full `ActivationApproval` record** the design describes rather
  than a bare gate: pending/approved/rejected, a pillar snapshot, a decision
  reason, requester and decider. A coordinator requests; a manager of that
  office decides from an Activations queue modelled on the blacklist one.
- **Separation of duties is enforced by identity, not only by role.** Managers
  hold both actions, so the role gate alone would still permit self-approval.
  The check started life in the view and was moved into `decide_activation`
  before shipping - a management command or future API calling the service
  would otherwise have bypassed the entire control, which makes it a
  view-shaped bug in business logic rather than a style point.
- **Readiness is re-checked at decision time**, because it stays editable after
  a request is raised. Approving a worker whose medical lapsed in the meantime
  would defeat the very gate the approval exists to double-check.
- **The snapshot is not decoration.** Without it a manager approves whatever
  the readiness record says when they open the queue, not what the coordinator
  submitted.
- Rejection requires a reason, and the reason surfaces on the person page so
  the coordinator knows what to fix rather than guessing.
- **Applied to CorvinumEU as well**, on the owner's call. Their coordinators
  lose a capability they had - a client-facing behaviour change - but their own
  matrix already said they did not have it, so the code now matches the
  document rather than the document being quietly wrong.
- Two incidental fixes the suite caught: `how_to_reg` is not in CorvinumEU's
  self-hosted icon subset and would have rendered as a blank box, and the
  audit-page test's page-wide substring check for raw reason codes tripped on
  the new `/activations/` URL. The latter was tightened to assert on rendered
  content rather than loosened - verified by rendering `event.reason` raw and
  confirming it still fails.

## 2026-07-27 - Fixed the Help visual aids, and how they reached main unreviewed

The Getting Started page gained navigation, role, office-boundary, status and
tooltip diagrams. They shipped broken, and they shipped inside **PR #123**,
whose title was "Staff every office, and give each project its own office's
coordinator" - because that commit was staged with `git add -A` and swept up
another session's in-flight work. 302 lines of CSS and 165 lines of template
merged under a misleading title, unreviewed, and deployed to staging.

The diagrams described a system that does not exist:

- a **"Field" navigation tab** that is not in the shell (People, Projects,
  Compliance, Accommodation, Reports, Help), and a callout describing "active
  field assignments";
- **Bratislava** as the office-scope badge and **Office A (e.g. Bratislava) /
  Office B (e.g. Kosice)** as the boundary example - for a client whose
  offices are Velky Meder, Gyor and Dunajska Streda;
- a hardcoded **`JOBER`** wordmark in a template CorvinumEU also renders;
- the office-boundary diagram rendering unconditionally, explaining a
  boundary a single-site client does not have.

**39 of 59 strings had no translation.** Wrapping a string in `{% trans %}`
makes it *extractable*, not *translated*; the catalog cycle was never run, so
the live Slovak page showed 14 English fragments. Two more untranslated
strings turned out to be **mine** from yesterday's SMS work - the `BLOCKED`
status label and the disabled-SMS notice - so the same omission, in the same
week, in my own slice. All 46 are now translated in SK/HU/UK with zero fuzzy
and zero empty entries remaining.

- The office diagram is now gated on a new `OFFICES_IN_USE` context flag,
  reusing the data-driven test the shell badge already makes rather than
  branching on client.
- **That flag caused a regression I only caught by running the lanes.**
  Computing `Office.objects.exists()` at the top of the context processor
  added a query to *every* response, including the anonymous login page which
  otherwise touches no database - four tests that render pages without a
  database started failing. Now a `SimpleLazyObject`, so the query happens
  only if a template actually reads the flag.
- `tests/test_help_visual_aids.py` pins the claims a diagram makes but prose
  does not have to: which tabs exist, which cities are not offices, that the
  wordmark comes from `BRAND_NAME`, that the boundary picture hides on a
  single-site install, and that the strings render translated in all three
  languages. Verified against the original template: four of the seven fail.

## 2026-07-27 - Four granted-but-unimplemented actions recorded; one is a control gap

The owner asked whether project creation existed. It does not - and sweeping
all 37 `Action` members against the views and templates that reference them
found that three others are in the same state. They accumulated over months
because nothing ever checked, and the permission matrix's Phase 1 caveat
("most action rows do not yet have a backing business view") had never been
revisited to say *which* rows were still aspirational.

- **`approval.activate` is the serious one, and it is a contradiction rather
  than an absence.** Three documents promise manager approval on activation -
  the permission matrix, `Jober_Product_Design.md`, and
  `jober-open-decisions.md` - and the action is checked nowhere.
  `activate_person` is gated by `project.assign`, which coordinators hold, and
  the Activate button sits inside the readiness block behind
  `readiness.complete`, also a coordinator action. So a coordinator **sees the
  button and can use it**; this is the normal UI path, not a crafted request.
  The matrix stated flatly that coordinators "Cannot approve Working". That was
  untrue, and is now corrected.
- **`project.manage`** is referenced by exactly one file - the dashboard -
  whose "Manage projects" button links to the read-only project list. No
  create/edit/archive routes exist. The feature matrix called this "Partial
  project management", which understates it enough to mislead.
- **`sms.manage_templates`** and **`user.manage`** are dormant outright. The
  first explains something noticed during yesterday's demo prep: no templates
  are seeded *and* none can be created, so the SMS template picker never
  renders at all.
- **It affects CorvinumEU too, which the sweep only revealed on verification.**
  Grepping `approval.activate` across `docs/` to confirm every mention was
  marked turned up `corvinum-permission-matrix.md` making the same promise -
  and CorvinumEU grants the same three actions and mounts the same shared
  `activate_person` route. A single-client fix would have left the second
  client's matrix lying. Both are now marked; the code fix lands for both at
  once.
- **Marked specified-not-enforced rather than reversing the design.** This is a
  different situation from the 2026-07-26 corrections, where documents made
  false claims about built behaviour ("Office never gates visibility"). Here the
  design is right and the implementation is missing, and the owner confirmed
  manager-only approval is still wanted - so the design docs keep their content
  and gain a marker pointing at readiness item 14.
- **The sweep's own criterion needed correcting mid-write.** The first pass
  counted "referenced by no view *and* no template", which returns 3 - it
  quietly excuses `project.manage`, whose button exists while nothing enforces
  it. The criterion that matters is **no server-side enforcement**, which
  returns 4. A `{% can %}` only hides a button. Both documents now state the
  criterion and the exact command, so a re-run reproduces the number instead of
  producing a different one and casting doubt on the list. A guard test asserting this was proposed and
  declined for now; the backlog entries carry the information instead.

## 2026-07-26 - Every office gets its own staff; projects get their own coordinator

The demo's headline is office separation, and it could only be shown in one
direction. All three working accounts belonged to Velky Meder, so "the VM
manager cannot see Gyor" was demonstrable and "the Gyor manager cannot see VM"
was not. One direction reads as a filter; both read as a boundary.

- Seeded a manager, recruiter and coordinator for **Gyor** and **Dunajska
  Streda** as well - nine staff accounts across three offices, plus the
  Observer. `DEMO_USERS` now carries the office code, and `seed_people`
  assigns membership from that single table, so an account and its office
  cannot drift apart.
- **Found and fixed an incoherence while doing it.** Every one of the six
  projects listed the Velky Meder coordinator as responsible - including the
  four in other offices, which that coordinator gets a 403 on. Formally
  responsible for work they cannot open. Each project is now run by a
  coordinator of its own office, so "who runs the Gyor contracts?" has an
  answer that survives being clicked on.
- `offices.set()` rather than `add()` throughout, and a test for it: `add()`
  would accumulate across reseeds until every account spanned every office and
  the demo silently stopped demonstrating anything. That failure is invisible -
  every page still renders, it just stops proving the point.
- The Observer deliberately keeps **zero** memberships. Granting it all three
  offices would produce identical screens by a different mechanism and would
  survive a regression in `user_office_scope` unnoticed, so a test pins the
  bypass as the mechanism.
- Runbook §1 now spends its time on the reciprocal check rather than the
  one-way one.

## 2026-07-26 - Backups deferred to the CorvinumEU build (with a hard trigger)

Owner decision: install scheduled backups once CorvinumEU accepts the offer,
expected shortly after the Jober demo.

- **The deferral is coherent, not drift.** The missing piece is an off-site
  host on a *different* provider, and `corvinum-basic-production.md` already
  plans one - a Contabo Storage VPS 10 in the EU, with its DPA part of that
  build. Installing Jober's backups first would mean buying a second
  destination.
- **What it costs today is small and measurable:** both databases hold
  fictional data only, so losing one costs a reseed - about ten minutes, done
  twice already today.
- **Recorded a trigger that is not only CorvinumEU.** Backups must exist
  before *either* CorvinumEU acceptance **or** the real-data gate opening for
  any client, whichever comes first. Tying the deadline solely to a commercial
  event would leave a path where real worker data lands first and the
  deferral quietly becomes negligence: at that point a lost database is lost
  personal data and a GDPR availability failure, not an inconvenience.
- Item 4 is marked deferred rather than downgraded, and the recommended-order
  note now says plainly that it remains the largest *risk* while no longer
  being the largest *actionable* item.

## 2026-07-26 - One backup script for every app, not just CorvinumEU

Scheduled database backups (production-readiness item 4) are the largest
remaining risk, and the plan for them was wrong in a way worth recording.

- **The documented command does not do what the runbook claimed.** Phase 6 said
  to run `dokku postgres:backup-schedule <service> <cron> <off-site-or-local>`.
  That command is **S3-only** - `postgres:backup-auth` takes AWS keys and the
  third argument is a bucket name. There is no local-target variant, so the
  placeholder was unimplementable as written. It also backs up only the
  database: not the media volume, which now holds real uploads, and not a
  release manifest.
- **A working script already existed, one client too narrow.** CorvinumEU had
  an encrypted, checksum-verified, retention-managed off-site backup;
  `DOKKU_APP` and `POSTGRES_SERVICE` were already env-overridable. Only the
  archive prefix, the work directory and the remote retention glob were
  hardcoded. Generalised to `scripts/offsite_backup.sh` +
  `scripts/backup_health.sh`, so one invocation backs up one app and Jober is
  covered by the same reviewed code rather than a second implementation.
- **The retention glob is the dangerous part.** Two apps may share a
  `BACKUP_REMOTE_DIR`, and the prune previously matched `corvinum-*.tar.gpg`.
  Widening that to `*` would have looked like a tidy generalisation in review
  while silently deleting the other app's history. The prefix is now passed to
  the remote shell as a positional argument, constrained to
  `[A-Za-z0-9._-]+`, and asserted in tests. Verified by simulation: with 40
  Jober and 5 CorvinumEU archives in one directory, a Jober run trimmed Jober
  to 35 and left CorvinumEU untouched.
- The health check globs the same prefix, because a mismatch reports "no
  backup" for an app that is backing up fine - a false alarm that teaches
  people to ignore the alert.
- **Still blocked on the owner**, and specifically: an off-site host on a
  different provider (D6), a GPG public key whose private half lives on
  neither server, and root shell on the Dokku host - the agent's SSH key is
  restricted to `dokku` commands and cannot install cron entries. Manual
  `postgres:export` dumps were taken for both services as an interim, which is
  a point-in-time safety net and not a backup system.
- Item 4 is written to stay open **even once a schedule runs**, until a restore
  drill has been performed and logged. A backup nobody has restored is a
  hypothesis.

## 2026-07-26 - Replaced uploads stop leaving orphans; bombs refused before decoding

Two production-readiness findings (6 and 8), plus the record correction that
goes with the whole media slice.

- **Every replacement was leaking a file.** `FieldFile.save()` mints a new
  name from `upload_to` and never touches the predecessor, so replacing an
  avatar or a certificate left the old file on disk with **no row pointing at
  it** - unreachable, un-auditable, and still holding a photo or a scan of
  someone's documents. Only an explicit *remove* deleted anything.
  `core.media.save_replacing` now stores and cleans up in one call, used by
  all three call sites.
- The delete runs in `transaction.on_commit`, not inline: if the surrounding
  transaction rolls back, the row still references the old file, and an eager
  delete would have destroyed the live copy. That detail is also why the tests
  need `django_capture_on_commit_callbacks` - without it they would pass
  vacuously, since pytest-django rolls every test back and the callback would
  simply never run.
- **The decompression-bomb check ran after the bomb was decoded.** Both
  handlers called `image.load()` and only then compared dimensions, so the
  image had already been expanded in memory by the time it was refused. The
  check now reads `.size` from the header in the probe block. `MAX_IMAGE_PIXELS`
  is capped as well, because a dimension limit alone still admits 7999 x 7999
  - roughly 64M pixels, well inside both caps.
- **Corrected the record rather than only the code.** Production-readiness
  item 2 asserted "Neither Dokku app has a storage mount"; both apps have one,
  and `MEDIA_ROOT` resolves to `/app/media`. Uploads always survived
  redeploys. The demo runbook's "uploads vanish on redeploy" warning inherited
  that error and is gone; uploading is now something the demo can show,
  including the certificate-visibility boundary.

## 2026-07-26 - SMS cannot reach a real number from staging any more

The runbook was mitigating live Twilio credentials on a public-URL staging app
with a sentence telling the presenter not to press Send. Two changes make that
sentence unnecessary.

- **A recipient allowlist outside production** (`SMS_ALLOWED_RECIPIENTS`,
  comma-separated, **empty = unrestricted** so production is unaffected).
  The risk it closes is specific: staging holds fictional worker data *and*
  real provider credentials, and a fictional person record with a real phone
  number typed into it is indistinguishable from any other - so "the data is
  fake" was never a control. The check runs before the provider call, and the
  test asserts the provider is never reached by monkeypatching it to raise.
- Numbers are compared digits-only, so `+421 900 000 000` and
  `+421-900-000-000` are the same handset. An allowlist that matched only one
  spelling would be worse than none: the entry looks correct, the send is
  blocked, and nothing explains why.
- **A blocked send is `BLOCKED`, not `FAILED`.** FAILED means Twilio saw the
  message and refused it; BLOCKED means we never asked. Collapsing them would
  make a safety net read as an outage in the message history.
- **"Just unset the credentials" is now actually safe.** It was not: with
  Twilio unset, `send_sms` recorded FAILED, so an unconfigured environment
  looked *broken* rather than unavailable - which is precisely why the runbook
  fell back to "don't press it". The panel now renders with the control
  disabled and a plain reason. The disabled attribute is cosmetic honesty; the
  allowlist and the fail-closed provider call are the actual controls.

## 2026-07-26 - Uploaded media is served, and only to people entitled to it

Uploads have been silently half-broken: the Dokku volumes *are* mounted and
`MEDIA_ROOT` resolves to `/app/media`, so files persist - but `/media/` was
routed only under `DEBUG` and no nginx alias exists, so every uploaded avatar
rendered as a broken image and every "View document" link 404'd. The runbook's
warning that uploads "vanish on redeploy" was wrong on the durability half.

- **The planned fix was the dangerous one.** Both design docs specified an
  nginx alias for `/media/`. That serves every certificate scan to anyone
  holding the URL - a UUID filename is obscurity, not authorization - which is
  what production-readiness item 3 flagged before it was built. Reversed both
  docs rather than leaving a sketch that a future reader would implement.
- Files now go through `core/media_views.py`, which re-runs the checks of the
  page they appear on: the office boundary for person avatars, plain
  authentication for staff headshots (colleagues appear in shared queues, and
  a headshot is not office data), and the office boundary **plus**
  `can_view_sensitive` for certificate documents.
- **The certificate rule is deliberately tighter than the office boundary.**
  Whether a certificate *exists* is an ordinary broad read; a scan of
  someone's medical or licence document is not. It reuses the rule already
  settled for DOB and identifiers, so an unconnected recruiter in the same
  office sees the row and gets a 403 on the file.
- **Removed the DEBUG-only `/media/` alias too.** It meant local development
  served uploads with no permission check while production served none, so a
  bypass was one settings flag away and would never show up locally. There is
  now no `/media/` route in any environment, and a test asserts it.
- A missing file 404s instead of 500ing. That is a real case, not defensive
  padding: a database restored from a dump taken without the media volume
  would otherwise crash every page embedding an avatar.

## 2026-07-26 - Object-level office guards for messaging, compliance, feedback, intake

ADR 0026 Phase B scoped the *list* queries across the app but left several
per-object views fetching by pk. Found while planning the media work, by
counting `get_object_or_404` calls against scope guards per file: `people`
7/11 and `logistics` 21/20, against **`compliance` 4/0, `messaging` 3/0,
`feedback` 3/0**. Filtering a list never stops someone typing a URL - which is
exactly what `CLAUDE.md`'s RBAC rule now requires and what these views skipped.

What was reachable before this slice, as a Velky Meder manager:

- **Send an SMS to a Gyor worker** by POSTing their pk. This is the one that
  matters most - it reaches a real phone, and the runbook was mitigating live
  Twilio credentials with "don't press send" while the send path itself was
  unbounded.
- **Create, edit or delete a Gyor worker's certificates**, including deleting
  the stored document.
- **Download another office's feedback flyer**, and see every office's
  feedback submissions and links in the inbox, and create a link against
  another office's project.

- `assert_person_in_scope` and a new `assert_office_in_scope` were promoted
  into `core/offices/scoping.py`. The people-views copy was private, which is
  precisely why three other modules shipped without it; there is now one
  public guard to reach for.
- **Intake needed a real rule, not an annotation.** `RecruitmentIntake` has no
  office FK, so the plan assumed it had no office dimension - but it carries a
  `recruiter` and a nullable `person`. The rule now mirrors the office-less
  Person case: before completion the owning recruiter, afterwards the created
  person's office. It is deliberately strict (a colleague in the same office
  cannot open a half-finished intake) and says so, so widening it is a
  decision rather than a drift.
- **Blacklist stays company-wide and is now asserted.** ADR 0026 point 3 makes
  it the deliberate exception: someone barred in one office must be caught in
  all of them. An *absence* of scoping cannot be reviewed, so
  `tests/test_blacklist_stays_company_wide.py` asserts a Velky Meder manager
  still sees and can decide a Gyor case. A later "scope everything for
  consistency" sweep now fails loudly instead of quietly disabling fraud
  protection.
- CorvinumEU is unaffected by data - single site, no `Office` rows, so every
  guard returns its unrestricted sentinel.

## 2026-07-26 - Re-seeding can no longer republish a rotated demo password

The owner rotated `jober-staging`'s four demo accounts off `demo-jober-2026`,
the value this public repo publishes. Verified by confirming the old password
no longer authenticates on any of the four - and that the command's
`<your-password>` placeholder had not been pasted through literally, which is
the failure mode a "rotated" success message would have hidden.

That left a trap. `seed_demo` called `set_password(DEMO_PASSWORD)` on **every**
run, created or not, so the next routine reseed would have silently restored
the published value with nothing reporting it. The rotation had no in-app
undo either, since no route in the product can change a password
(production-readiness 11).

- `seed_demo` now sets the built-in password **only on accounts it creates**.
  Existing accounts keep whatever they have, and the command says so:
  "Kept the existing password on N account(s)."
- `--reset-passwords` restores the old force-everything behaviour for the
  cases that actually want it.
- Everything else the seed repairs still gets repaired - role, names,
  `is_active` - so this is not a step toward the seed becoming a no-op on an
  existing database. A test asserts exactly that, because "preserve the
  password" is one plausible edit away from "skip existing users entirely".
- `CLAUDE.md` now marks the published password local-only and points at the
  owner for staging.

Left deliberately: the value is still hardcoded in `seed_demo.py` and six e2e
tests, so env-driving it is the durable fix and a larger change than the day
before a client demo warrants.

## 2026-07-26 - User and credential management recorded as the largest functional gap

Rotating the staging demo password needed a shell command against the Dokku
host. That is worth stating plainly: **no route in the product can change any
password.** `core/accounts/` has no `urls.py` or `forms.py`, and the only
account routes are login, logout, the two 2FA views, and avatar
upload/remove. `Action.USER_MANAGE` is granted to Manager in both clients'
policies and has no view behind it. Django admin is not a fallback for a
client - it needs a superuser, and no Jober role is one.

- **The authority model was already right.** Section 3a of
  `jober-multi-office-scoping.md` had specified exactly the rule the owner
  restated - Observer acts in every office, a manager only in their own -
  including the tiered detail that a *principal* manager may invite peer
  managers while a regular member manager may not. Nothing needed deciding;
  it needed building.
- **What genuinely was not specified is what happens to an account after it
  exists**, now written as section 3b: self-service password change,
  administrator-initiated reset (with the real choice between setting a
  temporary password and issuing a single-use link that means an
  administrator never learns someone's password), optional
  forgotten-password self-service and the rate-limiting/enumeration
  obligations it brings, deactivation via the `User.is_active` flag that
  already exists and that nothing sets, and clearing a lost 2FA enrolment -
  which matters because CorvinumEU turns 2FA on for managers.
- **Flagged a contradiction rather than encoding it silently.** Sections 3a
  and 3b give Observer authority over accounts in every office, while the
  permission matrix describes Observer as read-only with no writes. That is
  not yet a contradiction because none of it is built, but whichever slice
  lands first has to change that cell. Recorded the intent beside it:
  Observer is read-only over *operations* and authoritative over *staffing*.
  The CEO hires and removes people; the CEO does not record trial outcomes.
- Two production-readiness findings added (11: no user/credential
  management; 12: no superuser on staging after the reset) and one **false
  claim corrected** - the "Initial admin user" row asserted that
  `ensure_superuser` is wired into the Dokku release steps. It is not: the
  `Procfile` declares only `web:`, there is no `app.json`, and the superuser
  env vars are in neither app's config. It has only ever been run by hand,
  which is why a database reset silently leaves the app with no superuser.

## 2026-07-26 - Runbook rehearsed against staging; two claims were wrong

Walked the demo runbook end to end against the live staging app, checking each
claim rather than re-reading the script. Nine of eleven checks matched exactly.
Two did not, and both would have been discovered in front of the client.

- **The CEO's own table had two wrong numbers.** The per-office net column read
  ~EUR 20 060 for Gyor and ~EUR 11 270 for Dunajska Streda; the seeded values
  are **24 690** and **18 180**. Revenue was right for all three offices, which
  is what made it plausible - the net column had been written before the final
  cost splits landed and never re-derived. Replaced with exact figures and the
  company total (EUR 88 970 net on EUR 368 180), and dropped the "~" so the
  presenter reads them off the screen instead of approximating.
- **An undemonstrable step.** Section 5 told the presenter to open another
  office's accommodation location by URL and get a 403. The seed creates
  exactly **one** location (Ubytovna Nitra, Velky Meder), so there is no other
  office's location to try. The instruction now says so and points at Section 1,
  where the same boundary is already shown with a project and a person.
- Verified and left alone: office separation (badges, 5-of-7 people, 2-of-6
  projects, 403 vs 200), warehouse figures to the cent (36 + 23 + 14 = 73 units,
  EUR 623.50 + 406.00 + 252.00 = 1 281.50), the 2025 tail (EUR 90 890, ~45k per
  month against 2026's ~52.6k), DHL Bratislava 2026-05, manager finance showing
  Velky Meder only, and the blacklist step (Ivan approved, Diana proposed - both
  cases carrying no office, which is exactly the company-wide design Section 8
  claims).
- Transport is genuinely absent: the only "transport" left in a rendered page is
  a dead `<symbol>` in the inlined icon sprite, and the nav tab is gated on
  `has_transport`, which Jober sets false. No change needed.
- Mira Novakova's under-18 warning cannot drift: the seed sets her birth date to
  today minus 17 years, so the critical warning holds whenever the demo runs.

## 2026-07-26 - Help articles describe office scoping; 104 untranslated strings found and fixed

Started as "mention office scoping in two Help articles". The i18n cycle that
the change required then turned up something much larger.

- **The demo language was showing English.** `Profit/loss by office` and
  `Monthly trend by office` - two headings on the finance page a CEO is shown
  - rendered untranslated on the live Slovak staging app. Confirmed by
  requesting the real page as the real demo accounts, not by reading the
  catalog. In total **104 strings per catalog** were fuzzy or empty across
  SK/HU/UK: the whole equipment-stock ledger, accommodation cost periods,
  certificates, avatars, the trial/activation tooltips, and the office and
  executive-dashboard vocabulary itself.
- Fuzzy entries are excluded by `msgfmt`, so every one of them was rendering
  in English too. The catalog's stored guesses show why that exclusion is
  merciful: `msgmerge` had paired "Avatar updated." with "Skusobny den bol
  aktualizovany." (*Trial day was updated*) and "Profit/loss by office" with
  "Zisk/strata podla regionu" - the legacy *region* wording this programme
  had just finished removing from the docs.
- All 104 were translated in all three languages, following the terminology
  already established in the catalogs rather than inventing new words:
  office = `pobocka` / `iroda` / office, warehouse = `sklad` / `raktar` /
  `sklad`, and the lifecycle statuses exactly as the UI already renders them.
  Zero fuzzy and zero empty entries now remain in any catalog.
- The applier only ever *fills a gap*: an entry already translated and not
  fuzzy is a human decision and is never overwritten from a table. That guard
  is what kept Hungarian's 46 existing stock/accommodation translations
  intact - the run reports them as "not found" precisely because it refused
  to touch them.
- One deliberate overwrite, made separately: Slovak translated the `office`
  field label as `kancelaria` (a clerical office) while every other string
  says `pobocka` (a branch). That label is on the person form.
- **A real template bug surfaced from the extraction.** `person_detail.html`
  used `{% trans 'Change this person\'s avatar' %}`; the escaped apostrophe
  truncated the extracted msgid to `Change this person\\`, so the tooltip
  could never be translated in any language. Switched to double quotes.
- Verified structurally, not by eye: placeholder sets compared between every
  msgid and msgstr (0 mismatches), `python-format` flags confirmed present
  wherever placeholders exist, and the added/removed msgid sets diffed
  against `main` so the +4 net change is fully accounted for.

## 2026-07-26 - Legacy "region" vocabulary swept; feature matrix reconciled

Closes production-readiness item 9. The repo still described offices as
"regions" in the two documents a reader would treat as authoritative for
finance, and the cross-client feature matrix was wrong about three shipped
features.

- **The matrix was reconciled by re-checking each claim in the code, not by
  reading the last journal entry.** It listed warehouse stock as
  unimplemented (it ships, and is per-office), the under-18 warning as
  unimplemented (`core/people/services.py::age_warning` ships - critical
  under 18, advisory within 30 days, informational rather than blocking),
  and Jober transport as an ON/OFF mismatch that `clients/jober/settings.py`
  had already resolved to `False`. Added an office-scoped-RBAC row and gave
  People/Accommodation/Profitability the office dimension.
- **The "region" documents are kept, not rewritten.** `Jober_Finance_Specs.md`
  and `jober-requirements-supplement.md` are the provenance record for the
  workbook's sign convention and category structure - that is precisely why
  they are worth keeping readable as spoken. Each now opens with a banner
  saying regions became `Office` in ADR 0026 and that `Project.region` was
  removed; only the forward-looking instructional lines (the data-model
  sketches, the "can the region list grow?" open questions) were corrected,
  struck through with the answer beside them.
- `security-review-2026-06-29.md` keeps its dated text - it records what was
  true at review time - with an inline note that ADR 0026 superseded
  "offices are filters, not access boundaries". ADR 0008 gained a
  forward-pointer: its broad read was always broad *within* the viewer's
  offices.
- Two of this file's own gates were stale and were verified against the live
  app rather than the journal: Dokku staging deploy (both apps live) and
  HTTPS/secure cookies - confirmed by reading the actual response headers
  (HSTS with preload, `X-Frame-Options: DENY`) and the CSRF cookie's
  `Secure; HttpOnly; SameSite=Lax`. That also surfaced a small real finding:
  nginx emits a second, shorter HSTS header alongside Django's.
- Left deliberately: the last "region" naming is in code, not docs -
  `regional_results`/`regional_chart_data` in `features/profitability/views.py`
  and two templates. The data is already per-office; only the names are
  stale. A rename needs both unit lanes plus e2e, which is not a sensible
  thing to run the day before the CEO demo for a change no user can see.

## 2026-07-25 - Documentation caught up with office scoping (behaviour truth)

Seven PRs of office scoping shipped while the documents kept describing the
system as it was before. Several statements were not merely stale but
actively false.

- **`CLAUDE.md`'s RBAC convention is the important one.** It said nothing
  about office scoping, so the next agent adding a list view would have
  silently reintroduced the leaks this programme spent seven PRs closing. It
  now spells out five concrete requirements: filter through
  `user_office_scope` treating `None` as unrestricted (never "all offices" -
  an all-offices queryset still drops rows whose office is unset); use
  `core/offices/scoping.py` for `Person` rather than a bare `office__in`;
  403-guard any view taking an object pk, because filtering a list does not
  stop someone typing another office's URL; remember aggregates count (a
  dashboard tile summing every office's rooms shipped once); and keep
  blacklist company-wide.
- Also refreshed `CLAUDE.md`'s state-of-project block, its badly stale test
  baseline (276+22 -> ~654/~425/50), and a note that only `pozorovatel@` sees
  all three offices, since agents use those accounts to verify and would
  otherwise read scoped results as missing data.
- `Jober_Product_Design.md` carried the single most misleading line in the
  repo - *"Office never gates visibility in the MVP"* - in the file CLAUDE.md
  designates as product truth. Reversed, along with "no office-level data
  isolation", the "not yet implemented" banner, the ADR "Status: Proposed"
  paragraph, and the User model's "optional home office".
- `docs/permissions/jober-permission-matrix.md`: office boundary stated once
  above the per-role notes rather than repeated; Manager explicitly no longer
  company-wide; Observer named as the only cross-office role; the office-less
  person rule recorded; stale `apps.people` path fixed. CorvinumEU's matrix
  gains one clause explaining that ADR 0026 is a no-op there because it never
  creates `Office` rows.
- `notification-center.md` (managers were documented as company-wide; the
  provider contract's "object scope" now names office scope) and
  `operations-data-entry.md` (trials/transport/accommodation were all
  office-blind).

## 2026-07-25 - Richer demo finance data for the CEO walkthrough

The executive dashboard had 21 months across three single-project offices,
each month carrying ~6 line items. For a CEO demo that reads as a toy.

- **Six projects, two per office** (`DHLBA`+`MINIT` / `WEB`+`MEVIS` /
  `CARGO`+`RLS`), which is what makes "Profit/loss by office" a real roll-up
  instead of a restatement of one project. Each has its own revenue curve -
  steady grower, summer-peaking, dips-and-recovers, flat, fast ramp, slow
  decline - so the trend chart shows six differently-shaped contracts behind
  three office lines.
- **Per-project cost and revenue splits** replacing the shared five-category
  template. All ten finance groups are now populated, and accommodation and
  damage carry *both* sides (accommodation costs EUR 35.6k against 20k
  recharged; damage 3.2k against 5.4k recovered) - so the group breakdown is
  a story rather than a row of cost bars.
- **Nov-Dec 2025 backfilled for all six projects**, replacing a two-project
  single-month stub that made the year view read as "EUR 24 400 for all of
  2025" next to 2026's 368k. Both years now run through one shared
  `_apply_splits()` helper reading the same tables, so they cannot drift
  apart in category depth again - which is exactly how the old stub got thin.
- Result: 54 months, 738 line items, all six projects and all three offices
  present in both years. 2025 (~EUR 45k/month) into 2026 (~52.6k/month)
  reads as growth.
- The runbook's finance step now carries the per-office figures and states
  plainly that 2025's smaller total is two months, not a bad year.

## 2026-07-25 - Office-less people belong to their owning recruiter

A decision the office-scoping work forced into the open. Intake only infers
an office when the recruiter belongs to exactly one, so a multi-office
recruiter creates people with `office=None` - and a plain `office__in`
filter hid those from *everyone* except Observer, including the recruiter
who had just created them. Owner chose ownership as the middle ground over
"visible to all" (too loose) and "keep hidden" (orphans records).

- New `core/offices/scoping.py` states the rule once - `may_see_person` for
  403 guards, `scope_people`/`people_scope_q` for querysets (the `prefix=`
  argument handles querysets rooted elsewhere, e.g. `person__` for checklist
  items). Eight call sites now share it instead of re-deriving the predicate,
  and the duplicated `_assert_person_in_scope` in two modules collapsed into
  it.
- The notification feed had been deliberately fail-open for office-less
  records ("convenience list, not the boundary"). That is now a *second,
  looser* definition of the same rule, so it was tightened to match - one
  definition beats two.
- **Found while verifying, not while coding**: the seeded blacklist demo
  person (Ivan) had no office, so the re-entry walkthrough 403'd for the
  manager it is presented as. Fixing the create path alone would only have
  helped fresh databases, because that seed block is create-only - an
  existing demo or staging database would have kept failing. Added a repair
  path following `seed_people.py`'s existing precedent and verified it
  against the database that was actually broken: 403 -> 200.
- That is the same shape as slice 5's legacy office-less stock: changing what
  new seeds *create* does not fix databases that already exist. Worth
  carrying into the runbook as reseed-vs-repair guidance.
- Verified: 639 Jober unit / 7 skipped, 425 CorvinumEU / 10 skipped / 157
  deselected, 50 Playwright e2e, ruff check + format clean.

## 2026-07-25 - Office-scope badge, a leak found by sweeping, and the i18n slice-5 missed

Office scoping was fully enforced after slice 5 but completely **invisible**:
a scoped manager just saw fewer rows, which reads identically to an empty
database. For a demo whose whole purpose is to show separation exists, the
strongest available evidence was a 403 page. This adds the missing signal,
and a completion sweep turned up a real gap.

- `core/offices/context_processors.py::office_scope` feeds the shared shell a
  label: the office name for a single-office user, `"<first> +N"` for
  multi-office, `"All offices"` for Observer/superuser, `"No office"` for
  someone who belongs to none while offices exist (previously an unexplained
  empty screen). Renders **nothing at all** where no offices are populated,
  so CorvinumEU's shell is untouched - a data difference, not branching.
- Badge added to both client shells; `.account-office` shares the role pill's
  shape with an accent tint, and the unrestricted variant is deliberately
  neutral (absence of a restriction shouldn't shout).
- The `office` icon reuses assets both clients already ship - Jober's existing
  location-pin symbol and `location_on`, already in CorvinumEU's font subset.
  `core/ui/icons.py`'s docstring warns that expanding that subset is a new
  build dependency needing AGENTS.md §3.1 approval, so this deliberately adds
  neither a sprite symbol nor a font-subsetting step.
- **Leak found by a completion sweep, not by a failing test**: asked "is item
  #5 actually done?" and grepped every view/service for model queries lacking
  a nearby scope guard. `features/logistics/panels.py::occupancy_tile` summed
  capacity over *every* room company-wide and counted every active
  assignment - a Velký Meder manager's dashboard was reporting Győr's and
  Dunajská Streda's beds. An aggregate rather than row-level data, but still a
  read of another office's accommodation, which is exactly what the ADR's
  acceptance test forbids. The file had scope references elsewhere, so a
  file-level check called it "scoped"; only a per-query sweep caught it.
- Also hardened `_trial_queue_context`'s read-only project dropdown, which was
  correct only by coincidence: today just Observer lacks
  `INTAKE_ASSIGN_TRIAL` (and is unrestricted), but a client policy change
  would have silently produced an unscoped list. Now scoped by construction,
  matching what `_transport_context` already did.
- **Process miss owned and fixed**: slice 5 shipped five user-facing strings
  with no translations at all - the office-named stock error, "Receiving
  office", both warehouse help texts, and the "set this person's office
  first" rejection. `msgmerge` had since fuzzy-matched them to nonsense (the
  Slovak stock error had become "Only available candidates can be
  scheduled"). All five now translated in SK/HU/UK with the `python-format`
  flag preserved so `msgfmt` still validates the `%(available)s`/`%(office)s`
  placeholders. Extract-and-translate needs to be part of every slice
  touching user-facing text, not a step remembered ad hoc.
- A repo invariant caught a real bug in this work too: the CorvinumEU layout
  got a multiline `{# ... #}` comment, which Django renders as visible text.
  `test_production_templates_do_not_use_multiline_short_comments` failed
  exactly as designed.
- Verified: 626 Jober unit tests / 7 skipped, 417 CorvinumEU / 10 skipped /
  152 deselected, 50 Playwright e2e, ruff check + format clean.

## 2026-07-25 - Office-scoped RBAC Phase B, Slice 5: equipment stock split into per-office warehouses

Slice 5 of 7, and the largest piece of Phase B: the equipment stock ledger
was one pooled, company-wide FIFO inventory with no site dimension at all.
Splitting it is a valuation/allocation change, not a query filter.

- Schema (`features/logistics/migrations/0011`): nullable `office` FK on
  `EquipmentStockReceipt` (the source of truth - stock is received into one
  physical warehouse), plus denormalized copies on `EquipmentStockLot`,
  `EquipmentStockAllocation`, and `EquipmentStockMovement`.
  **The movement column is one addition beyond the design doc's literal
  field list**, taken deliberately: `equipment_stock_balance` aggregates over
  movements in a single `.values().annotate()`, and inbound rows reach their
  office via `stock_lot` while outbound rows reach it via `allocations__lot`
  - two different join paths that don't combine into one clean filter. A flat
  column keeps that aggregate a single-table `office__in=`, matching
  finance's shape.
- `_consume_fifo` now takes `office=` and, when given, only considers that
  office's lots. An office short on stock **raises** rather than reaching
  into another warehouse (ADR decision point 6: independent ledgers, no
  transfer flow), and the error names the office so the operator knows whose
  stock is short. `receive_stock`/`adjust_stock` thread it through;
  `issue_equipment` resolves it from `person.office` and refuses to issue
  stock-tracked gear to a person with no office set.
- `equipment_stock_balance`/`equipment_month_report` gained `offices=None`
  (the established "unfiltered" convention). The stock page, the person
  card's availability numbers, and the warehouse-value report tile all pass
  the caller's scope - showing a company-wide availability figure next to an
  issue button that would reject it would be worse than not showing one.
- `return_equipment` restocks into the person's *current* office. No office
  snapshot is kept on `EquipmentIssue` (matching the design doc's field
  list), so a person who changed office mid-issue restocks into the new one
  - accepted as low-probability rather than adding schema.
- Refactor taken along the way: the office-picker scoping was about to be
  copy-pasted into a third and fourth form, so it moved into
  `core/offices/forms.py::apply_office_scope`, and `PersonForm`/
  `AccommodationForm` were switched over to it (covered by their existing
  slice-1 tests).
- Demo seed now creates one opening receipt **per office** with different
  quantities, so the split is visibly demonstrable rather than a column
  nobody can see. Verified against real seeded data, not just green tests:
  Velký Meder 38 units/€672, Győr 23/€406, Dunajská Streda 15/€266; the
  VM-scoped demo manager's stock page shows exactly VM's 38 while the
  Observer sees everything.
- **Legacy office-less stock, observed and left alone deliberately**: a
  database seeded before this slice keeps its old pooled receipt with
  `office=None`. Those rows stay invisible to every scoped manager and
  visible to the Observer - which is the documented `offices=None` ("no
  filter", not "all offices") semantics working correctly, and exactly what
  the finance Phase A tests already pin down. No backfill migration: only
  fictional data exists (the real-data gate has not opened), so reseeding a
  fresh database is the cheaper answer, and `EquipmentStockMovement`'s
  deliberate per-instance immutability guards make retro-assignment
  something a data migration would have to bypass rather than a natural fix.
- Verified: 614 Jober unit tests / 7 skipped, 407 CorvinumEU / 10 skipped /
  150 deselected, 50 Playwright e2e (a fresh image build reseeded both demo
  clients with the new per-office receipts), `makemigrations --check` clean,
  ruff check + format clean. Every pre-existing equipment/stock test passes
  unmodified - the `office=None` default preserves the pooled path exactly.

## 2026-07-25 - Office-scoped RBAC Phase B, Slice 4: Logistics (accommodation + transport) scoped

Slice 4 of 7. Accommodation and transport are the last two read surfaces
before the equipment-stock ledger (slice 5, the big one).

- `features/logistics/views.py::accommodation_list` and
  `_transport_context` (both the chart-data `rows` queryset and the
  `records` table) filtered by office. Transport was a one-hop
  `project__office__in=scope`, identical in shape to finance's Phase A
  pattern, since `TransportWeek.project` already existed.
- `features/logistics/forms.py::transport_projects()` gained the office
  filter on top of its existing coordinator filter.
- New `_assert_accommodation_in_scope` / `_assert_person_in_scope` guards
  give the same hard-403 treatment slice 2 gave People/Projects, across
  every accommodation-and-room surface that takes a pk directly:
  `accommodation_detail`, `accommodation_edit`, `room_create`,
  `room_edit`, `accommodation_cost_period`, `set_room_rate_view`,
  `set_assignment_rate_view`, `set_assignment_payment_view`,
  `assign_room_view` (both the person *and* the room's accommodation, as
  either can be an independent cross-office guess), `release_room_view`.
- **Caught the same class of bug slice 2's e2e run surfaced, this time by
  looking for it rather than waiting to be bitten**:
  `features/logistics/forms.py::assignable_rooms()` built the room
  `<select>` on the person card from every active room company-wide, with
  no user argument at all. A cross-office room would have been offered in
  a dropdown that `assign_room_view` now correctly 403s. Gained a `user=`
  parameter scoped via `accommodation__office__in`; its single caller
  (`features/logistics/panels.py::room_panel`) now passes `request.user`.
- Verified: 605 Jober unit tests / 6 skipped, 397 CorvinumEU / 10 skipped
  / 150 deselected, 50 Playwright e2e, ruff check + format clean.
- Note on the verification: the host OS crashed mid-run on the first
  attempt, taking out all containers and the scratchpad. Every lane was
  re-run from scratch afterwards (fresh test databases, fresh image
  builds) rather than trusting the partial pre-crash results - the Jober
  count reproduced exactly.

## 2026-07-25 - Office-scoped RBAC Phase B, Slice 3: Compliance, Checklists, Notifications scoped

Slice 3 of 7. Extends office scoping to the three surfaces that surface
per-person alerts/updates: `features/compliance/services.py::compliance_alerts`
(now a trivial `Person.office__in=scope` filter, no longer needing the
fragile "current assignment" chain the pre-Slice-1 design would have
required), `features/checklists/notifications.py` (CorvinumEU-only
feature — Jober has `checklists` off entirely, so this is the first real
exercise of Slice 1's CorvinumEU-safety fix under this program), and
`core/notifications/services.py`'s `_viewer_may_see_update`/`_core_alerts`.

- `_viewer_may_see_update` now ANDs an office check onto the existing
  role logic: resolves a record's office from `project.office_id` first,
  falling back to `person.office_id`; a record with neither (legacy/
  unassigned data) stays visible - this feed is a convenience list, the
  real access boundary is the linked detail view (already 403-guarded in
  Slice 2).
- `_core_alerts`'s `TrialAssignment`/`ReadinessRecord` queries gained the
  uniform non-observer office filter, on top of the existing
  Coordinator-only filter (kept as an additional AND).
- **A calling-convention subtlety caught before it broke `tests/test_
  compliance.py`**: `compliance_alerts(viewer=None)` is a real, pre-
  existing "no filter" convention used by several tests and
  `test_demo_scenario.py` - naively delegating to `user_office_scope(None)`
  would silently scope those calls to nothing, since `user_office_scope`
  treats `user=None` as an anonymous *web* request (fails closed). Fixed
  by only calling `user_office_scope` when a real viewer is passed.
- New tests carry no `jober_only` marker and were verified to actually
  exercise the CorvinumEU-only checklist path: run once under default
  (Jober) settings, where it correctly skips (`flag_enabled("checklists")`
  is `False` there); run again explicitly under `--ds=clients.corvinum_
  eu.settings`, where it executes for real and passes.
- Verified: 593 Jober unit tests / 6 skipped (the checklist test skips
  under Jober), 391 CorvinumEU / 10 skipped / 144 deselected, 50
  Playwright e2e, ruff check + format clean.

## 2026-07-25 - Office-scoped RBAC Phase B, Slice 2: People, Projects, Reports, Exports scoped + detail-view 403s

Slice 2 of 7. Applies the schema from Slice 1 as a real access boundary,
not just a filter: `.filter(office__in=scope)` on every list/aggregate
query, plus a hard 403 (mirroring finance's `_assert_month_in_scope`) on
direct/URL-guessed access to another office's `Person`/`Project` detail
or mutation views.

- `core/people/views.py`: `people_list` filtered; a new
  `_assert_person_in_scope` guards `person_detail`, `person_edit`,
  `archive_person`, `recycle_person`, `person_avatar_upload/remove` — not
  just the read view, every mutation that takes a `person_pk` directly.
- `core/projects/views.py`: `project_list` filtered; `_assert_project_in_scope`
  guards `project_detail`, `trial_outcome`; `_assert_person_in_scope` +
  `_assert_project_in_scope` together guard `assign_trial`,
  `readiness_update`, `exit_view`, `activate_person` (both the person and
  the project argument, since either can be an independent cross-office
  guess). `_trial_queue_context`'s pending-trials queue is now
  office-filtered for every non-Observer role, not just Coordinator.
- `core/projects/forms.py::operable_projects()` gained the office filter
  on top of its existing coordinator filter — this also newly restricts
  Manager (previously unrestricted there) to their own office(s),
  matching the ADR's "if role is not observer" rule.
- `core/ui/views.py::reports()` and `core/ui/exports.py` (`people_csv`,
  `projects_csv`) scoped — the CSV export gap the ADR flagged as
  pre-existing (zero recruiter/coordinator scoping, independent of
  multi-office) is now closed. `core/people/services.py::inactive_by_reason`
  gained an `offices=None` kwarg mirroring finance's convention.
- **Fixed two real behavior changes surfaced by e2e, not test-only
  workarounds**: `person_detail`'s trial-assignment project dropdown
  (`active_projects` context var) was still `Project.objects.filter(is_
  active=True)` unfiltered — switched to the now-scoped
  `operable_projects()`, since offering a cross-office project in a
  `<select>` that the backend will now correctly 403 is a real UX bug, not
  just a test fixture problem. Also moved the demo's one INACTIVE person
  (Bohdan) from Dunajská Streda to Velký Meder in `seed_people.py`: the
  seeded staff accounts are all VM-scoped, so VM needs its own
  representative of every interesting lifecycle state for demo
  walkthroughs to keep working — Tran (DS) and Farrukh (GYR) alone already
  prove cross-office data is correctly hidden.
- `docs/permissions/jober-permission-matrix.md`'s stale "Offices are
  filters, not access boundaries" line rewritten to describe the real
  ADR 0026 boundary.
- Verified: 583 Jober unit tests / 5 skipped, 380 CorvinumEU / 10 skipped
  / 144 deselected (new office-scoping tests carry no `jober_only` marker
  and run for real there), 50 Playwright e2e (caught and fixed the two
  real issues above), ruff check + format clean.

## 2026-07-25 - Office-scoped RBAC Phase B, Slice 1: `Person.office`/`Accommodation.office` schema + a critical CorvinumEU-safety fix

Production-readiness review item #5: office scoping (ADR 0026) only
protected Finance ("Phase A"). This is Slice 1 of a 7-slice program
completing Phase B (People, Projects, Reports, Compliance, Logistics,
Notifications, exports, the equipment-stock ledger, and the office-
principal/staff-invitation subsystem — all confirmed in scope, not
deferred, per the user's explicit "complete solution" call).

- **Found and fixed a real bug before it could ship**, not called out in
  the original review: `user_office_scope()` (`core/accounts/
  permissions.py`) returned `user.offices.all()` for any non-Observer —
  for CorvinumEU (which never populates `Office`/`User.offices` at all)
  that's always an *empty* queryset, not `None`. Every `.filter(office__
  in=scope)` call the later slices add would have silently returned zero
  rows for every CorvinumEU Manager/Coordinator/Recruiter, everywhere.
  Fixed with a data-driven (not client-branching) check: `if not Office.
  objects.exists(): return None` before the membership return — safe for
  Jober (always has 3 seeded offices) and correct for CorvinumEU. This is
  the load-bearing prerequisite every later slice depends on.
- `Person.office` and `Accommodation.office` — new nullable FKs
  (`core/people/models.py`, `features/logistics/models.py`), migrations
  `core/people/migrations/0006_person_office.py` and `features/logistics/
  migrations/0010_accommodation_office.py`. `Room` inherits its
  accommodation's office transitively, no separate field.
- `PersonForm`/`AccommodationForm` gained a scoped `office` field (new
  `user=` kwarg): offered choices are the acting user's own offices
  (all offices for Observer/superuser or installs with none at all),
  defaulted when the user belongs to exactly one. `person_create`/
  `person_edit`/`accommodation_create`/`accommodation_edit` thread
  `user=request.user` through.
- `features/intake/services.py::complete_intake` infers a new person's
  office from the recruiter's own office membership when unambiguous
  (exactly one office); left unset otherwise, correctable later via
  `person_edit` — chosen over adding an intake questionnaire field, since
  that would couple the static `SELECT` catalog to `Office.code` strings
  for no real benefit (offices are permanently capped at 3).
- Demo seed data updated: `seed_people.py` spreads the six seeded people
  across all three offices (not all-VM) so office scoping is visibly
  demonstrated, not just schema nobody can see; `seed_logistics.py`'s
  single accommodation matches its housed worker's office.
- New tests: `tests/test_office_scope_helper.py` (the CorvinumEU-safety
  regression guard, no client marker), `tests/test_person_office.py`,
  `tests/test_accommodation_office.py` — form scoping/defaults, intake
  inference, and an explicit CorvinumEU-lane case per file proving the
  office field stays optional and empty there, not broken.
- Verified: 554 Jober unit tests / 5 skipped, 351 CorvinumEU / 10 skipped
  / 144 deselected, 50 Playwright e2e (both demo apps rebuilt and reseeded
  cleanly with the new office logic), `manage.py makemigrations --check`
  clean, ruff check + format clean on every touched file.

## 2026-07-25 - Audit `reason` translation gap closed for fixed-vocabulary literals

`docs/i18n-workflow.md` had documented `reason` as a full "accepted
limitation" — free text, not translatable, same tradeoff as any changelog.
On re-check that turned out to be only mostly true: `core/audit/models.py`'s
`reason` field is genuinely free text at most call sites, but several
(`core/people/services.py`, `core/projects/services.py`,
`features/logistics/services.py`, `features/blacklist/services.py`) pass a
fixed English literal as a default (`reason or "activation"`,
`reason="superseded"`, etc.) — a real closed vocabulary hiding inside a free
`TextField`.

- Added `AUDIT_REASON_LABELS` + `audit_reason_label()` to
  `core/audit/presentation.py`, mirroring the existing
  `AUDIT_ACTION_LABELS`/`audit_action_label()` pattern exactly: translate at
  **display time** based on the viewer's active locale, not at write time
  (which would incorrectly bake in the *actor's* language into the stored
  event). Unmatched reasons — the genuine free text — pass through
  unchanged.
- `core/audit/views.py`'s `audit_log` view now resolves
  `event.reason_label` per paginated row, same as `event.action_label`;
  `templates/pages/audit_log.html` renders `reason_label` instead of the
  raw `reason`.
- Also found and fixed 12 action codes that had never been added to
  `AUDIT_ACTION_LABELS` (accommodation.cost_period_set/created/updated/
  worker_payment_set, equipment.stock_adjusted/received, room.created/
  updated, transport.week_created/updated, trial.updated, wage.recorded) —
  these were falling back to the auto-generated readable label instead of
  a real translation.
- Extraction picked up 25/24/25 (SK/HU/UK) new-or-changed fuzzy matches —
  most were the new audit strings fuzzy-pairing to unrelated existing
  msgids (e.g. `"Trial no-show"` matched against `"Trials"`,
  `"Added to blacklist"` matched against its near-opposite
  `"Removed from blacklist"`); a few were incidental to prior unrelated
  template wording changes (`equipment_stock.html`, `payslips.html`,
  `logistics_equipment.html`) that had never been re-extracted. Reviewed
  and hand-translated every one per the CLAUDE.md fuzzy-match caution
  rather than trusting `msgmerge`'s guess.
- `docs/i18n-workflow.md`'s audit section rewritten from "`reason`
  deliberately is not [translated]" to "`reason` is partially translated" —
  the accepted-limitation framing was accurate for the free-text majority
  but wrong for this fixed-literal minority.
- Verified: 543 Jober unit tests + 5 skipped, 340 CorvinumEU tests + 10
  skipped/144 deselected, full Playwright e2e — all green; `ruff check` and
  `ruff format --check` clean.

## 2026-07-25 - Illustrated default avatar art landed (avatar-design.md §1)

Closes the one deliberate exception left open from the avatar feature: the
illustrated per-role default art. The user generated all five (worker +
4 admin roles) via their own image-generation tool, then chroma-keyed and
color-normalized them, and handed over 1024×1024 RGBA PNGs.

- Verified independently before integrating, not just trusted "validated":
  exact dimensions, true alpha transparency at the corners, and the circle/
  silhouette fills checked pixel-for-pixel against §1's palette
  (`#4A6FA5`/`#2F9E8F`/`#C9922B`/`#6B4E9E`/`#6B7280` circles, `#F5F5F0`
  silhouette) - all five were exact hex matches, not just visually close.
- Processed with Pillow (resize to 256×256, re-encode WebP) and shipped as
  `static/avatars/default_{role}.webp`.
- **Real gap caught before shipping, not after**: this doc's own §1
  originally specified `core/static/core/avatars/` as the destination -
  never actually checked against `STATICFILES_DIRS`
  (`config/settings/base.py`), which only scans the top-level `static/`
  directory and each client's own `static/` directory, not `core/static/`.
  `{% static %}` happily built a URL string for the wrong path anyway (it
  doesn't verify the file exists), so the first version of the test suite
  passed cleanly while the feature would have silently 404'd every default
  avatar in production. Caught by asking "would this actually survive a
  real Docker build," not by re-reading the code - moved the files to
  `static/avatars/`, and confirmed the fix by inspecting the actual built
  image's filesystem (`docker exec` into a freshly rebuilt `jober-dev-app`,
  not a bind-mounted dev container) rather than trusting the passing test.
  Also needed its own new `Dockerfile` `COPY static/avatars
  /app/static/avatars` line - the Dockerfile copies `static/` subdirectories
  individually, the exact same class of gap the DejaVu font vendoring hit
  earlier this session for `vendor/fonts/`.
- `core/ui/templatetags/avatars.py`'s placeholder branch (a plain gray
  circle, `.avatar-placeholder`) is gone entirely - the no-photo case now
  always renders an `<img>` at the role-appropriate default, same code path
  as an uploaded photo. `Person` always gets the worker default (no `.role`
  field); `User` gets the default matching their own role.
- Verified live on both clients: the worker default renders correctly on
  every worker-list row on both Jober and CorvinumEU (same shared
  template/tag, no client-specific branching needed), and each of the four
  admin roles' navbar avatar shows its own distinct color when logged in
  as that role.

## 2026-07-25 - GitHub application CI gate

- Added `.github/workflows/application-ci.yml` for pull requests and pushes to
  `main`, with read-only repository permission, exact-revision checkout, run
  cancellation, explicit timeouts, and no third-party GitHub Actions.
- Added `scripts/ci_quality.sh`, which builds from the committed digest/hash
  pins, verifies vendored assets and the npm-free boundary, checks Ruff
  lint across the codebase and formatting on changed Python files, checks
  Django and migration consistency under both client settings, runs both unit
  test lanes against isolated PostgreSQL containers, and verifies the
  production image excludes test/browser/Node tooling.
- Kept the full existing `scripts/playwright_e2e.sh` as a separate required
  browser check. Neither CI job receives Doppler or provider credentials.

## 2026-07-24 - In-app Help area (help-area-design.md)

Sixth and final planned backlog item this session (multi-office Phase B
remains, explicitly out of scope — its own large platform change per ADR
0026). Asked whether to scope down to a 4-article starter set or build the
full 8-module set the design doc lists; the user chose the full set.

- New `core/ui/help.py` (article registry, no DB model — hand-authored
  templates was already decided against Markdown to avoid a new PyPI
  dependency) plus `help_index`/`help_article` views
  (`core/ui/views.py`), mounted unconditionally in `config/urls.py` — no
  `Action` or `flag_on` gate, per the design doc's explicit "every role
  needs documentation" call.
- New nav tab, right after Reports, in both shells: a new `nav-icon-help`
  SVG symbol for Jober; CorvinumEU reuses its already-subsetted `info`
  Material Symbol rather than triggering another font-subset regeneration
  for one icon (the pill-system-design.md §2 pipeline from earlier this
  session).
- 9 article templates (`templates/help/*.html`) extending a shared
  `templates/help/_base.html` wrapper, plus a grouped `help_index.html`
  landing page (`.grid-2`, auto-wrapping — not `.two-column`, which is a
  fixed 2-panel layout unsuited to 9 groups).
- **Real translation volume, done properly**: 72 new msgids (39 headings/
  titles, 33 paragraphs) hand-translated into SK/HU/UK, not machine-
  translated, as one combined authoring+translation pass per the design
  doc's own "a partially-translated Help section would be worse than not
  having one" guidance. `scripts/compile_messages.sh --extract`'s
  `msgmerge` step fuzzy-matched several new strings against unrelated
  existing ones (e.g. "Getting started" initially inherited the Slovak
  translation of an unrelated pre-existing "started" msgid) — caught and
  fixed per CLAUDE.md's documented fuzzy-match caution, not accepted
  blind. Applied via `polib` (installed transiently for this one-off
  authoring task, not an app dependency) rather than hand-editing ~250
  `.po` entries across 3 files, which would have been impractical to do
  reliably by hand given gettext's line-wrapping conventions.
- **Real cross-client nuance caught during live verification, documented
  as a follow-up rather than silently shipped**: every Help article is
  visible on every client regardless of that client's feature flags —
  CorvinumEU sees the Feedback article even though it has no Feedback tab
  at all (`feedback: False`). The content is accurate, just not relevant
  to that reader. Per-client article filtering wasn't in the original
  design doc's scope; noted there as a real, separable follow-up.
- **Real test-isolation lesson applied preemptively**: given the pills
  feature's registry-pollution bug earlier this session, the Help
  registry (`core/ui/help.py`) was deliberately built as static, immutable
  module-level data (not a mutable registration API tests could leave
  polluted) — nothing to monkeypatch, nothing to leak between tests.
- Verified live on both clients with real Playwright screenshots: the
  English index and a full article page, plus a complete Ukrainian
  article page (Jober-only language) rendering correctly end to end, and
  the CorvinumEU sidebar's Slovak-translated Help entry with the reused
  `info` icon.

## 2026-07-24 - Certificate-validity icons — pill system Phase 2 (pill-system-design.md §2)

Fifth backlog item this session, closing out `pill-system-design.md` fully.
Two real pieces of new engineering beyond straightforward feature wiring:

- **New generic registry slot**: `register_person_badges`/`person_badges`
  (`core/ui/registry.py`) plus a `{% person_badges person as badges %}`
  template tag (`core/ui/templatetags/avatars.py`) — the "extra content in
  a worker-list row" extension point that didn't exist when §1/§3 shipped.
  Used identically on the worker list (dot-sized icons,
  `core/people/views.py::people_list`, now `.prefetch_related("certificates")`)
  and the person-detail header (larger icons) - one slot, two render sites,
  matching how `{% avatar %}`/`{% status_pill %}` already work.
  `features/compliance/panels.py::certificate_badges` groups certificates
  by category and picks the most relevant row per category via new
  `features/compliance/services.py::most_relevant_certificate` (soonest-
  expiring valid row, else most-expired - a no-expiry certificate counts as
  valid but never "wins" over a genuinely soon-expiring one).
- **Real font-engineering detour**: CorvinumEU's Material Symbols webfont
  is a hand-picked 44-glyph subset with nothing medical/forklift/welding-
  adjacent. Asked whether to reuse an imperfect existing glyph or properly
  expand the subset, the user chose the latter. New
  `scripts/subset_corvinum_icons.py` downloads the official Google variable
  font, pins it to the shipped "24pt Regular" instance (FILL=0, GRAD=0,
  opsz=24, `wght` stays variable - matches the currently-shipped file's
  `fvar` exactly), and - the actual finding - prunes the GSUB
  `LigatureSubst` table at the Python data-structure level *before*
  subsetting. A plain `fonttools subset --text=medical_services` pull, on
  this font, retains the entire same-first-letter ligature group (66
  glyphs for one word; the full 49-name target list ballooned to 3335
  glyphs) because `LigatureSubst` groups every ligature sharing a first
  input glyph into one `LigatureSet`, and fonttools' text-driven closure
  can't prune within it. Manually filtering `ligatures[first_glyph]` down
  to only the target words first, then re-subsetting, reproduced the
  shipped file exactly for its existing 44 icons (70 glyphs, byte-for-byte
  glyph-count match) before adding the 5 new ones (75 total). New mapping:
  `medical_services` and `forklift` are genuine exact-name matches in
  Material Symbols; `construction`/`factory` are the closest available
  stand-ins for crane/welding (no dedicated icons exist for either -
  acceptable since every icon carries a tooltip naming the actual
  certificate). New `vendor/fonts`-style provenance entry in
  `vendor/MANIFEST.md` (Apache-2.0, source URL, regeneration script, hash)
  even though this asset lives under `clients/corvinum_eu/static/` rather
  than `vendor/` - it's the first properly hash-pinned entry for a font
  that previously had none (BUILD_JOURNAL 2026-07-15: "copied from the
  prototype").
- **New regression guard**: `test_icons_dict_material_names_are_all_in_the_corvinum_subset`
  (`tests/test_corvinum_client.py`) - the pre-existing icon-subset test only
  checked hardcoded `base.html` usages, not the generic `{% icon %}` tag's
  `ICONS` dict (`core/ui/icons.py`), which is exactly what this feature's
  5 new entries are. A future icon added to `ICONS` without a matching
  font-subset entry now fails a test instead of silently rendering raw
  ligature text on CorvinumEU.
- New `.badge-danger` CSS class (this doc's own open item) plus
  `.cert-badges`/`.cert-badge-expired`/`.cert-badge-expiring` for icon
  tinting - no class needed for valid/no-expiry, which inherits ambient
  ink color.
- Demo data: a second certificate (Mira Novakova, expired Health check)
  added to `seed_demo_scenario.py` so the demo shows two different
  category icons in two different severity tints.
- **Real test-isolation bug caught by the new suite, not a fluke**: an
  early version of the new registry test called `register_person_badges`
  with a throwaway lambda and no cleanup, permanently polluting the
  module-level `_person_badges` list for the rest of the pytest session -
  every person on every subsequent test's rendered page picked up a phantom
  badge. Fixed with `monkeypatch.setattr` to scope the registration to the
  single test, verified by re-running the full file (order-dependent
  failure gone).
- Verified live on both clients with real Playwright screenshots against
  freshly rebuilt (not bind-mounted) images: zoomed crops confirmed the
  status-pill/cert-icon colors are genuinely distinguishable at real size,
  and - the meaningful check - a temporary CorvinumEU certificate row
  rendered both new icons correctly shaped and correctly tinted through the
  regenerated font subset in an actual browser, not just a glyph-count
  sanity check.

## 2026-07-24 - Downloadable feedback PDF+QR flyer (feedback-flyer-design.md, ADR 0028)

Fourth backlog item this session. The design doc's original plan was a
dependency-free hand-rolled PDF (extending `_simple_pdf()`'s technique),
explicitly flagging that approach can't support Cyrillic text. Given that
tradeoff, the user chose real font embedding over a Latin-only flyer —
which turned into a real supply-chain decision, not just a code change.

- **New dependency, ADR 0028**: `fpdf2==2.8.7` plus its two genuinely-new
  runtime deps `fonttools==4.63.0` and `defusedxml==0.7.1` (its third dep,
  Pillow, was already pinned via ADR 0027 — no version bump needed).
  Confirmed via the PyPI JSON metadata (not just search-result summaries)
  that fpdf2's `uharfbuzz` dependency some sources mention is test-only
  upstream, not a runtime requirement. All three cooldown-clear (fpdf2
  ~5 months, fonttools ~2 months, defusedxml since 2021). Downloading
  against the existing pinned `.in` files confirmed **zero** unrelated
  transitive drift this time (unlike Pillow's addition) - both lock diffs
  are purely additive. `jober-test:phase4` rebuilt so the pinned test image
  actually has the new imports.
- **New vendored asset**: DejaVu Sans 2.37 (Regular + Bold TTF,
  `vendor/fonts/`) for fpdf2 to embed - broad Unicode coverage including
  Cyrillic, stable since 2016 (no ongoing release-churn supply-chain
  exposure for a pinned asset). Downloaded archive's MD5 verified against
  the officially published value *before* extracting; SHA-256 values in
  `vendor/MANIFEST.md`/`scripts/verify_vendor_assets.py` computed directly
  from the extracted files. AGENTS.md §3.2 names htmx/Alpine specifically
  but the same discipline was applied here since the font is needed at
  request time (unlike the Tailwind CLI, which is build-only and
  deliberately not committed).
- **Real gap caught before it shipped**: the production `Dockerfile`
  copies specific directories into the runtime image (`core`, `features`,
  `clients`, `config`, `locale`, `templates`, `static/vendor`,
  `static/src/js`) - no wildcard `COPY .`. The new `vendor/fonts/` wasn't
  in that list. Unit/CorvinumEU-lane tests never would have caught this
  (they bind-mount the whole repo into the test container), so this was
  only found by explicitly testing against the *actual built* runtime
  image (`scripts/dev_app.sh rebuild`, then `docker exec` calling
  `qr_pdf()` directly inside the container with no bind mount) - confirmed
  missing, added the `COPY vendor/fonts /app/vendor/fonts` line, rebuilt,
  reconfirmed working.
- `core/ui/qr.py` gains `qr_pdf(data, *, label="")` alongside the existing
  `qr_svg()` - same segno matrix, walked into `fpdf2` `rect()` fills
  (much simpler than the original no-dependency plan's raw `re f` content-
  stream operators, now that a real PDF library is in play) plus label/URL
  text set in the vendored DejaVu font.
- New `features/feedback/views.py::feedback_link_pdf`, gated
  `@require_action(Action.FEEDBACK_VIEW)` (same as `feedback_inbox`),
  returning `Content-Disposition: attachment; filename="feedback-<token>.pdf"`
  - uses the link's token, not its free-text label, for the filename (a
  small, deliberate deviation from the design doc's literal suggestion,
  since a label could contain characters unsafe for a filename/header).
  "Download PDF" button added to `feedback_inbox.html` next to each link's
  existing on-screen QR toggle, using `{% icon "export" %}`.
- Verified live end-to-end via a Playwright download (not just unit
  assertions): logged in, clicked the real button, downloaded the actual
  PDF from the running app, rendered it to PNG with `pdftoppm` and visually
  confirmed the QR code and label; separately extracted embedded Cyrillic
  text back out with `pypdf` and confirmed it round-trips as real glyphs,
  not placeholder boxes.

## 2026-07-24 - Status pills + nav attention badges (pill-system-design.md §1/§3)

Third backlog item this session. Scoped down from the full three-part
`pill-system-design.md` to §1 (worker status pill) + §3 (Compliance/Reviews
nav badges) — §2 (certificate-validity icons) needs a new list-row registry
slot that doesn't exist yet and was cut to its own deferred Phase 2, same
phasing precedent as the avatar feature's deferred illustrated-art Phase 2.

- New `--info`/`--info-soft` CSS tokens (`static/src/css/app.css`, both
  themes) for the `AVAILABLE` status — reused the already dataviz-validated
  `--chart-office-1` blue (`#2a78d6` light / `#3987e5` dark) rather than
  deriving a new color; confirmed via the dataviz skill's validator that it
  doesn't introduce any new CVD/lightness failure against either client's
  existing (and already slightly-imperfect, pre-existing, out-of-scope)
  success/warning/danger trio, light and dark, both clients' actual hex
  values.
- New `{% status_pill person size="dot"/"label" %}` tag
  (`core/ui/templatetags/avatars.py`, same module as `{% avatar %}`) plus
  `.avatar-stack`/`.status-pill*` CSS — a colored dot on the worker-list
  thumbnail, a labeled pill on the person-detail header, overlapping the
  avatar's bottom edge. Never rendered for a `User`'s own avatar (navbar) -
  `lifecycle_status` is a `Person` concept only, matching the design doc.
- New generic nav-badge registry slot (`register_nav_badge`/`nav_badge`,
  `core/ui/registry.py`) so `core/ui/templatetags/nav.py` never imports
  `features.*` directly — features register their own count provider from
  `apps.py` instead, same pattern as `register_report_tile`/
  `register_person_panel`. Compliance (`compliance_badge`) and Logistics
  (`reviews_badge`) both register into it; wired into both clients' nav
  (`.folder-tab`/Jober, `.sb-item`/CorvinumEU sidebar including rail mode)
  inside the exact same `{% if %}` gates the tabs themselves already use, so
  the badge never queries for a role/client that wouldn't see the tab.
- **Real bug caught by the existing unit suite, not the new tests**: both
  `layouts/base.html` files render the nav (and therefore call the badge
  tag) even on the anonymous login page. The first cut of `compliance_badge`
  had no auth guard, which broke three unrelated, non-`django_db`-marked
  tests (`test_theme.py`, `test_tooltips.py`) that render the login page
  without a DB fixture — and would have run a real `compliance_alerts()`
  query against `AnonymousUser` on every login-page load in production.
  Fixed with an `is_authenticated` guard at the top of `compliance_badge`
  (mirroring how `can()` already short-circuits for `reviews_badge`).
- One new `.notification-count-warning` CSS variant (amber, reusing the
  existing `--warning` token) alongside the pre-existing `-alert`/`-update`
  pills — Reviews is always this tone, Compliance uses it when no alert is
  `expired`/`missing`.
- Verified live against the running dev app with Playwright screenshots
  (not just unit assertions): status-pill tone correctly distinguishes
  `info` (blue, Available) from `success` (green, Working) at actual
  worker-list dot size, in both light and dark theme; nav badge renders and
  is correctly positioned on both Jober's folder-tab and CorvinumEU's
  sidebar (including confirming it's correctly *absent* when CorvinumEU's
  demo data has zero alerts, then correctly present after inserting one).

## 2026-07-24 - Certificate document uploads implemented (certificate-upload-design.md)

Second backlog item built end-to-end this session, unblocked by the avatar
slice landing first (shares `MEDIA_ROOT`/Pillow/ADR 0027 — no new dependency
approval needed here; `pypdf`, used for the PDF half, already shipped for
payslips). Matches `docs/product/certificate-upload-design.md` exactly, plus
pulls in `pill-system-design.md`'s `Certificate.category` field in the same
migration since the upload form needed a category selector anyway.

- `features/compliance/models.py`: `CertificateCategory` (`HEALTH`/
  `FORKLIFT`/`CRANE`/`WELDING`/`OTHER`, default `OTHER`) and
  `Certificate.document` (`FileField`) added in one migration
  (`0002_certificate_category_certificate_document`). Docstring corrected —
  no longer "metadata only, no file storage".
- New certificate-specific functions in `core/media.py`, alongside (not
  replacing) the avatar ones: `certificate_upload_path` and
  `process_certificate_document`. Deliberately different from avatar
  processing in two ways the design doc called out — no center-crop (a
  legal document must stay legible, so only aspect-ratio-preserving
  downscale above a 2000px cap) and dual format support (JPEG/PNG/WebP via
  the same Pillow decode-verify-strip-EXIF-by-reencode pipeline as avatars,
  or PDF via `pypdf.PdfReader(...).pages`, stored unmodified once
  validated — pypdf has no drawing/re-encode API, so PDFs aren't
  re-processed the way images are).
- RBAC: new `Action.CERTIFICATE_MANAGE`, granted to
  `{RECRUITER, COORDINATOR, MANAGER}` in both `clients/jober/policies.py`
  and `clients/corvinum_eu/policies.py` (mirrors `INTAKE_ASSIGN_TRIAL`/
  `PERSON_RECYCLE_AVAILABLE`'s exact grant set, per the design doc's
  precedent-matching rationale) — both permission matrix docs updated in
  the same commit.
- New `features/compliance/forms.py` (`CertificateForm`: category/name/
  dates only — the file input is handled outside the `ModelForm`, same
  pattern as avatar uploads) and `features/compliance/services.py`
  additions (`save_certificate`, `delete_certificate`, both audited via
  `record_event`: `certificate.uploaded`/`replaced`/`updated`/`deleted`,
  all four labels added to `core/audit/presentation.py`'s translated map).
- Surfaced as a new person-detail panel
  (`templates/panels/compliance_certificates.html`), registered via
  `register_person_panel` in `features/compliance/apps.py` — not a template
  hand-edit, uses the existing `person_panels` slot (ADR 0021 Stage B).
  Full-page create/edit form (`templates/pages/certificate_form.html`,
  multipart) mirrors `equipment_form.html`'s established pattern.
- Demo seed (`seed_demo_scenario.py`) updated to tag Olha's existing
  "Forklift licence" row with `category=FORKLIFT` — a fresh environment
  will show it correctly; the long-lived local dev DB kept its
  pre-migration row at the default `OTHER` since the seed step is
  idempotent and the row already existed (expected, not a bug).

## 2026-07-24 - Avatar system implemented (ADR 0027 + avatar-design.md)

The first backlog item actually built from planning, not just designed —
matches `docs/product/avatar-design.md` with one deliberate exception:
the illustrated per-role default art was never delivered, so the
no-photo fallback is a plain placeholder circle, not the illustrated art
originally specified; the user chose to wait for real art rather than
build a stand-in design now, and the placeholder is structured so
swapping in real art later only touches
`core/ui/templatetags/avatars.py`'s one placeholder branch.

- **New dependency, approved and added properly**: `docs/adr/0027-
  pillow-avatar-images.md` — Pillow 12.3.0 (released 2026-07-01, clear of
  the 3-day cooldown). Adding it re-resolved three unrelated transitive
  packages (`asgiref`, `typing_extensions`, and `charset-normalizer` in
  `test.lock` only) to newer point releases; all three pinned back to
  their vetted versions in both `.in` files so the actual lock diffs are
  Pillow-only, matching ADR 0016's exact precedent for this situation.
  Rebuilt `jober-test:phase4` (built from `Dockerfile.playwright-python`)
  so the pinned test image actually has Pillow importable, not just the
  lock file listing it.
- New `core/media.py` (shared by `Person.avatar` and `User.avatar`, not
  duplicated per app): `avatar_upload_path` (UUID filenames, always
  `.webp`) and `process_avatar_upload` — decode-and-verify, reject
  anything not JPEG/PNG/WebP (SVG included), cap input size/dimensions,
  center-crop, resize to 512px, re-encode as WebP. EXIF is dropped by
  construction (re-encoding from decoded pixels, not copied source
  bytes) rather than a separate strip step.
- `MEDIA_ROOT`/`MEDIA_URL` added to `config/settings/base.py` (never
  existed before); both clients' `production.py` accept a `MEDIA_ROOT`
  env override for the eventual Dokku volume mount without a code
  change. Local/dev serves `/media/` via Django's own `DEBUG`-gated
  static serve in `config/urls.py`.
- RBAC exactly as designed: own avatar is self-service
  (`request.user.pk == target.pk`, no `Action`); worker avatar reuses the
  existing `Action.INTAKE_CREATE_EDIT` rather than a new fine-grained
  action.
- New shared `{% avatar obj size="sm/md/lg" %}` tag
  (`core/ui/templatetags/avatars.py`) wired into the navbar (own avatar,
  both clients — CorvinumEU's sidebar already had an initials-based
  `.sb-avatar` fallback, deliberately preserved as CorvinumEU's own
  fallback rather than overridden with the generic placeholder), the
  worker list, and the person-detail header.
- Every add/replace/remove audited via `core.audit.services.record_event`
  with new, already-translated action labels
  (`core/audit/presentation.py`).
- **Real bug caught by the e2e suite, not guessed at**: the mobile phone-
  viewport test failed after the navbar changes — `.header-account` had
  `flex-shrink: 0` in its base rule with no override in the mobile media
  query, so it refused to shrink to the viewport and the Sign-out button
  overflowed 30px past the edge. Fixed with a targeted mobile-only
  `flex-shrink: 1; max-width: 100%` override, confirmed with a live
  Playwright diagnostic script (not just re-running the suite blind)
  before treating it as fixed.
- 15 new tests (`tests/test_avatars.py`): upload validation (valid image
  re-encodes to 512×512 WebP, non-image/SVG/oversized all rejected, real
  embedded EXIF confirmed stripped), own-avatar self-service including
  anonymous rejection and audit-event sequencing (added → replaced),
  worker-avatar RBAC (recruiter/manager can, coordinator can't - 403),
  and the template tag's two render branches.

## 2026-07-24 - Richer finance demo data (Jan-Jul 2026); three new design docs

- `features/profitability/management/commands/seed_finance.py`: expanded from 2
  `FinancialMonth` rows total (Nov 2025 only, missing CARGO entirely) to a
  full Jan-Jul 2026 year-to-date series across all three projects/offices
  — 21 new rows, plus the original Nov 2025 pair kept for year-over-year
  contrast. Each project gets a distinct growth curve (DHLBA/Velký Meder:
  steady ~3%/month growth; WEB/Győr: a mid-year dip and recovery;
  CARGO/Dunajská Streda: a fast ramp-up, reflecting a newer project) so
  the executive dashboard's multi-series office-trend chart (built
  earlier this session) actually shows three differently-shaped lines
  instead of parallel copies. Each month also gets a small line-item
  breakdown (a fixed cost-category split per project, reused across all 7
  months) so the Group-breakdown chart and month-detail drill-in are
  populated too, not just top-line totals.
- Three new planning-only design docs, matching the avatar/pill/
  certificate-upload pattern (nothing built beyond the demo data above):
  - `docs/product/feedback-flyer-design.md` — a downloadable PDF+QR flyer
    for feedback links. Key finding: needs **no new dependency** — segno's
    QR matrix can be walked to emit PDF vector-rectangle fill operators
    directly into a hand-written PDF (the same technique
    `features/payslips/services.py::_simple_pdf()` already uses), so
    `pypdf` isn't even needed for drawing, only (if ever) for features
    payslips already uses it for (encryption). Flags a real constraint
    plainly instead of glossing over it: PDF's standard base fonts don't
    cover Cyrillic, so a Ukrainian-language flyer isn't achievable without
    embedding a real font resource — a materially bigger, separate
    decision.
  - `docs/product/help-area-design.md` — a new in-app Help section.
    Confirmed with the user: hand-authored Django templates (no Markdown
    dependency, avoids an AGENTS.md §3.1 ADR), and full SK/HU/UK
    translation from day one — flagged explicitly as a real translation
    workload given the existing `.po` catalogs are already ~4800-4900
    lines each of short labels, and help prose is a different scale of
    content entirely.
  - Audit `reason` i18n: turned out to already be half-solved on
    investigation — `action` labels are fully translated today via
    `AUDIT_ACTION_LABELS` (`core/audit/presentation.py`); `reason` is
    genuinely free text (user-typed or interpolated) with no closed
    vocabulary `gettext` can address. User chose to document this as an
    accepted limitation rather than build anything — added a short
    section to `docs/i18n-workflow.md` rather than a new design doc, so
    the distinction isn't re-litigated as if it were still open.

## 2026-07-24 - Correction: office seed data was leaking into CorvinumEU's database

User asked "hopefully these changes were only applied to the jober thin
client" about the previous slice — a fair challenge that caught a real
issue. The *behavioral* changes (office-scoped finance queries, the
executive dashboard, the 403 guard) genuinely are Jober-only in effect,
since they all live in `features/profitability/`, which CorvinumEU doesn't
install. But `core/offices/migrations/0002_seed_offices.py` seeded the
three real office names (Velký Meder, Győr, Dunajská Streda) via a Django
migration — and `core.offices` was added to every client's
`INSTALLED_APPS` (correctly, as a generic mechanism, same as
`core.people`). Migrations have no per-client conditional, so that
migration would have inserted Jober's specific office names into
CorvinumEU's database too, just because it shares the app — Jober
business data leaking into an unrelated client's schema, even though
nothing in CorvinumEU's UI would ever display or use it.

- Deleted `core/offices/migrations/0002_seed_offices.py`.
- Moved the office seeding into `clients/jober/demo/management/commands/
  seed_people.py` (already Jober-only) — `Office.objects.get_or_create(...)`
  for the three offices, run before projects are assigned to them.
- Updated `tests/test_office_scoping.py`'s fixture to create its own
  `Office` rows directly (the migration-seeded ones it previously relied
  on no longer exist).
- Updated ADR 0026's execution note to state the mechanism explicitly:
  `core/offices` stays empty by default for every client; only Jober's own
  seed command ever populates it.
- **Verified with an actual query, not just re-running tests**: migrated a
  fresh scratch database under `clients.corvinum_eu.settings` and queried
  `offices_office` directly — 0 rows, confirming the fix, not just
  inferring it from green test output.

## 2026-07-24 - Office-scoped finance RBAC + executive dashboard (ADR 0026 Phase A)

Actual implementation of ADR 0026's finance-relevant slice, on the user's
explicit request for the full platform change (phased — see the ADR's
execution note for what's Phase A vs still-pending Phase B).

- New `core/offices` app: `Office(name, code, country)`, seeded via a data
  migration with Jober's three licensed offices (Velký Meder/VM/SK, Győr/
  GYR/HU, Dunajská Streda/DS/SK). Registered in every client's
  `INSTALLED_APPS` that fully replaces the base list (`corvinum_eu`,
  `_smoke`) — a core app, not Jober-only code, mirroring `core.people`/
  `core.projects`.
- `Project.office` is now a real FK (was free-text `office`/`region`
  `CharField`s). Migrated as an explicit `RemoveField`+`AddField`, not
  Django's auto-generated `AlterField` — there's no sensible cast from
  arbitrary strings to a FK, so this is a deliberate drop-and-recreate.
  Demo seed data reassigned to real offices (DHLBA→Velký Meder, WEBASTO→
  Győr, CARGO→Dunajská Streda) since the old "Bratislava"/"Nitra" strings
  were fictional placeholders with no real-office correspondence.
- `User.offices` M2M (not a single FK — staff can work at multiple
  offices, per the earlier session's amendment). Demo staff (recruiter/
  coordinator/manager) seeded to Velký Meder only, deliberately not all
  three, so the demo actually shows the restriction working.
- `core.accounts.permissions.user_office_scope(user)`: returns `None` for
  Observer — a genuine "unrestricted" sentinel, not an all-offices
  queryset (which would incorrectly exclude any record with no office
  assigned yet). Every finance service function
  (`company_totals`/`monthly_totals`/`yearly_totals`/`project_totals`/
  `group_breakdown`/the renamed `office_totals`, plus new
  `office_monthly_totals`) takes `offices=None` with the same meaning.
- `finance_summary` view branches by role at the same URL: Observer gets a
  new executive dashboard (`templates/pages/finance_executive.html` —
  company totals, per-office breakdown, a new multi-series monthly-trend
  chart); every other `finance.view_summary` role gets the existing page,
  now scoped to their own office(s) only.
- Closed a real bypass: `finance_month_detail`/`_save`/`_lock`/`_reopen`
  and `finance_record` now 403 a non-Observer acting on another office's
  month/project, even via a guessed PK or crafted POST — not just hidden
  from the UI dropdown.
- New Chart.js builder (`office-trend`, `static/src/js/charts.js`) — a
  generic N-series line chart (one line per office), unlike the existing
  `trend` builder which is hardcoded to exactly Revenue/Cost/Net. Colors
  come from a new fixed categorical palette (`--chart-office-1/2/3`)
  picked and validated with the project's `dataviz` skill for this exact
  3-series all-pairs case, in both themes — light mode carries a
  contrast WARN on one slot, satisfied by the chart's own legend +
  accompanying office-breakdown table (the skill's required "relief").
- Fixed test fixtures across `test_finance_charts.py`,
  `test_finance_lineitems.py`, `test_finance_workbook.py`, and
  `test_nav_active.py` that created bare `Project`/manager fixtures with
  no office — the new scope guard correctly rejected them, so each was
  given a real office and matching user membership rather than the guard
  being loosened.
- Updated `docs/adr/0026-office-scoped-rbac.md` (Status: Partially
  Accepted, execution note added) and
  `docs/product/jober-multi-office-scoping.md` to reflect exactly what's
  built (Phase A) vs still pending (Phase B: Person/Accommodation office
  fields, equipment-stock split, the principal/invitation subsystem, and
  the remaining ~13 ad hoc RBAC call sites outside finance).

## 2026-07-24 - Move regional finance chart from Reports to Finance; correct §8.1

- The "office financial chart" on Reports/Overview turned out to be
  `features/profitability/panels.py::company_totals_panel` (registered onto the
  Reports page via `register_report_panel`) — a linked card showing a
  margin gauge and a profit/loss-by-region diverging chart. Region is the
  closest existing concept to "office" today (`Project.region`); the real
  `Office` model is still just a design doc (`docs/product/jober-multi-
  office-scoping.md`, ADR 0026 — not implemented).
- Moved the regional diverging chart into the existing "Regional roll-up"
  section of `templates/pages/finance_summary.html` (which already had
  the same `regional_totals()` data as a chartless table) — added
  `regional_chart_data` to `finance_summary`'s view context
  (`features/profitability/views.py`), mirroring the existing `group_chart_data`
  pattern exactly.
- Deleted the now-dead `features/profitability/panels.py` and
  `templates/panels/finance_company_totals.html`, and removed
  `FinanceConfig.ready()`'s report-panel registration entirely — per the
  user's choice, Reports/Overview shows **no** finance content at all now,
  for any role including Observer, not even a lightweight tile.
- Corrected `Jober_Product_Design.md` §8.1 ("Visibility principle"), which
  literally said "offices are filters and reporting fields, not access
  boundaries" — the opposite of the office-isolation principle now wanted,
  and in direct contradiction with ADR 0026. The old wording is kept
  underneath as the accurate *current* behavior (ADR 0026 is still
  Proposed, not activated) so the doc doesn't overclaim a design that
  isn't built yet.
- `AGENTS.md` has similar stale RBAC wording but was deliberately left
  untouched this pass — it's binding scope/security/supply-chain
  authority and warrants its own deliberate correction.

## 2026-07-24 - Shared icon system + expanded tooltip coverage

- New `{% icon "name" %}` template tag (`core/ui/templatetags/icons.py`,
  vocabulary in `core/ui/icons.py`) resolves one icon concept to each
  client's own existing mechanism — Jober's inline SVG sprite
  (`templates/partials/jober_nav_icons.html`) or CorvinumEU's Material
  Symbols web font — via a new per-client `ICON_BACKEND` setting. Icons
  had been confined entirely to the two nav shells until now; this is the
  first time page-body buttons get icons at all, in either client.
- Vocabulary checked against CorvinumEU's existing font subset
  (`icon-names.txt`) before adding anything, specifically to avoid a
  silent new build-time dependency (font re-subsetting would need its own
  AGENTS.md §3.1 approval). `search`/`filter`/`back`/`sign-out` were
  deliberately excluded — no matching glyph exists in the current subset,
  and those buttons stay text-only rather than getting a mismatched icon.
- Added 15 new SVG symbols to Jober's sprite (`add`, `edit`, `delete`,
  `archive`, `recycle`, `approve`, `reject`, `export`, `issue`, `receive`,
  `adjust`, `save`, `invite`, `promote`, `warehouse`) and a matching
  `.icon`/`.icon-sm`/`.icon-md` CSS family; fixed `nav-icon-reviews` being
  reused for both the Reviews and Warehouse nav tabs (Warehouse now has
  its own symbol).
- Rolled icons + targeted tooltips out across all remaining page/panel
  templates (people, projects, compliance, logistics/equipment,
  accommodation, transport, finance, ledger, payslips, feedback,
  blacklist). Tooltip coverage follows the existing documented minimalism
  rule (`docs/product/contextual-tooltips.md`) — icon-only and
  consequential/state-changing actions get one, plain labeled Save/Cancel/
  Back buttons don't. Icons themselves went broad by design, independent
  of that rule.
- Fixed a real pre-existing gap found along the way: `person_detail.html`'s
  "Recycle to Available" button had no `data-confirm`, unlike its sibling
  exit-action buttons which already had one (and thus an implicit
  tooltip) — added the missing confirm text and the `recycle` icon.
- This also completes a documentation arc from the same session: design
  docs for avatars, worker status/certificate pills, certificate uploads,
  and Jober's multi-office RBAC (with a follow-up amendment for
  multi-office staff + office principals) were written as planning-only
  deliverables (`docs/product/avatar-design.md`,
  `docs/product/pill-system-design.md`,
  `docs/product/certificate-upload-design.md`,
  `docs/product/jober-multi-office-scoping.md`, `docs/adr/0026-...md`) —
  none of those are implemented yet; only this icon/tooltip slice touched
  code.

## 2026-07-23 - Hungarian payslip terminology

- Standardized CorvinumEU's payslip workflow on `Bérlap`: navigation,
  recording form, optional issue-date label, recorded table, audit labels,
  email copy, and wage-versus-payslip overview.
- Kept the separate advances/deductions ledger named `Előlegek és levonások`
  so users no longer have to distinguish two finance workflows both labelled
  with variants of `bérjegyzék`.
- Added catalog-level regression coverage for the four primary workflow
  labels. This is translation-only and does not alter payroll calculations,
  period uniqueness, PDF content, or ledger behavior.

## 2026-07-23 - Finance + Reports: charts (backlog slice 8/9, expanded scope)

User explicitly asked for this slice to be "big, sophisticated, and usable"
rather than the plan's original minimal sketch — scope was re-planned from
scratch with 3 research agents + 1 design-review agent, then every claim
independently re-verified (services.py, `reports()`, `vendor/MANIFEST.md`,
`verify_vendor_assets.py`, theme.js, app.css, `docs/adr/`, CorvinumEU's
`INSTALLED_APPS`) before writing code. Full design/governance rationale is
in `docs/adr/0025-chartjs-visualizations.md`; highlights below.

- **New capability, not just visualization**: `monthly_totals(year=None)`
  in `features/profitability/services.py` — the only company-wide monthly
  (not yearly) revenue/cost/net time series that existed anywhere.
  Ascending order (a trend), deliberately not matching `yearly_totals()`'s
  newest-first convention. `all_locked` flag per bucket for a future
  filled-vs-hollow point treatment.
- **Vendored Chart.js 4.5.1** (MIT) per AGENTS.md §3.2 — live-fetched
  (read-only) the actual jsdelivr UMD bundle and GitHub LICENSE to pin a
  real version/hash rather than a placeholder; stripped a trailing
  `//# sourceMappingURL=...` comment (the map itself isn't vendored,
  matching htmx/alpine shipping no map) — **this one required a real
  fix**: leaving it in made `collectstatic` fail the Docker build outright
  (whitenoise refuses to publish a JS file whose referenced map is
  missing). `docs/adr/0025-...md` records the alternatives rejected (D3,
  ECharts, uPlot) and why.
- **Ran the project's own `dataviz` skill's validator** against this
  product's actual color tokens before writing any chart code — found
  that `--success`/`--danger` (already used everywhere for signed money
  in text) **fail** the six-checks validator in dark mode specifically
  (CVD separation 5.4, below the legal floor; lightness out of band) even
  though they pass in light mode. Rather than replicate a known-bad pair
  into a new surface, added 3 new chart-only tokens (`--chart-positive`,
  `--chart-negative`, `--chart-net`) — light mode aliases the existing
  tokens (already pass), dark mode gets bespoke validated values found by
  iterating the actual validator script, not by eyeballing hex codes.
  `--success`/`--danger` themselves are untouched — fixing them globally
  is a much bigger, separate piece of work, out of scope here.
- **Chart placement** (additive everywhere, tables/dl's kept): monthly
  trend line + margin half-doughnut gauge + group-breakdown diverging bar
  on `finance_summary.html`; monthly trend + per-project diverging bar on
  `finance_year.html`; group-breakdown diverging bar on
  `finance_month_detail.html` (zero new backend — reuses the `groups`
  context already there); a new "Projects and assigned personnel"
  section directly in `core/ui/views.py::reports()` (core-owned data, not
  the feature-panel registry) with a headcount-per-project bar plus a
  real per-project people list; the existing `finance_company_totals`
  Reports panel extended in place (not duplicated) with a compact gauge +
  regional bar, since `features.profitability` isn't even installed for
  CorvinumEU so the extension carries zero client-branching risk.
- **`static/src/js/charts.js`** (new): reads chart colors from CSS custom
  properties at build time, destroys+rebuilds tracked charts on the
  existing `themechange` event (Chart.js doesn't self-repaint on a CSS
  change). A custom inline value-label plugin (no `chartjs-plugin-
  datalabels` — staying to exactly one new vendored file) draws bar-tip
  and line-end labels per the dataviz skill's mark spec. **Found and
  fixed during its own first render**: labels for a bar/point near the
  auto-scaled axis extreme overlapped the y-axis category labels or
  clipped at the canvas edge — fixed with a `paddedRange()` helper that
  adds proportional headroom to the numeric scale (not just a fixed pixel
  canvas pad), confirmed by re-screenshotting before/after.
- **`core/ui/chart_data.py`** (new, core not feature — `core/ui/views.py`
  needs the same `{labels, net}` shaping as finance's views, and core
  can't import features): `net_bar_payload()`, the one payload shape
  reused across group/project/region (~5 call sites); other shapes
  (trend, gauge, magnitude) are each used once or twice and stay inlined
  per view rather than being abstracted.
- Data hand-off via Django's `json_script` filter (auto-serializes
  `Decimal` as a JSON string, no manual coercion) — never hand-rolled
  inline `<script>` JSON interpolation.
- New `{% block scripts %}` added to **both** `templates/layouts/base.html`
  and `clients/corvinum_eu/templates/layouts/base.html` (confirmed
  CorvinumEU has its own separate base template) so Chart.js loads only
  on the pages that actually render a canvas — never globally alongside
  htmx/Alpine/app.js.
- **Found and fixed via a real corvinum-lane test run, not by inspection**:
  a new Reports test hardcoded `translation.override("en")`, but
  CorvinumEU's `LANGUAGES` only configures sk/hu — no "en" — which 404'd
  under that lane. Fixed by reusing the exact fallback pattern already
  established two tests above it in the same file
  (`"en" if "en" in dict(settings.LANGUAGES) else "sk"`), rather than
  inventing a new one.

## 2026-07-23 - Apartments: base cost + capacity at creation (backlog slice 7/9)

- Design pass (with user 2026-07-23) rejected the plan's original
  assumption of auto-generating N placeholder `Room` rows for "number of
  rooms (beds)". Found that base cost and bed count already live together
  on one existing record, `AccommodationCostPeriod` (`capacity` ×
  `per_head_cost`, `features/logistics/models.py:44-70`) — previously only
  enterable *after* creation via a second form on the detail page. Reused
  that record wholesale instead of inventing new Room-generation behavior.
- `AccommodationForm` (`features/logistics/forms.py`) gained two optional,
  non-model fields — `capacity` and `per_head_cost` — dropped from the
  form entirely when editing (`__init__` deletes them if `instance.pk` is
  set), so the edit form is untouched: no bare inputs that would silently
  do nothing. Added a `clean()` check requiring both-or-neither so a
  half-filled pair fails loudly instead of quietly creating nothing.
- `accommodation_create` (`features/logistics/views.py`) calls the
  existing `set_accommodation_cost_period()` service (idempotent
  `update_or_create` keyed on accommodation+month) when both fields are
  present, defaulting `effective_month` to the current month — no new
  service code, no template change (`accommodation_form.html` already
  iterates `{% for field in form %}` generically).
- Verified functionally against the dev app, not just unit tests: created
  with both fields filled (cost period recorded, visible on the detail
  page), with only one filled (form re-renders with the validation error,
  nothing created), and confirmed the edit form shows neither field.
- New labels ("Capacity (beds)", "Per-head monthly cost (EUR)") both
  fuzzy-matched on extraction (paired with unrelated prior "capacity"/
  "Capacity"/"per-head monthly cost" strings in all three catalogs) — the
  same failure mode as every other slice this session; corrected and
  cleared the fuzzy flags rather than accepting the guess.
- Added `test_accommodation_create_with_capacity_and_cost_records_a_cost_period`
  and `test_accommodation_create_rejects_only_one_of_capacity_or_cost` to
  `tests/test_operations_workspaces.py`. Note for future editors: my first
  attempt at this edit mis-split the existing
  `test_manager_creates_location_and_room_but_coordinator_cannot` test
  (inserted before its actual last line, which I hadn't seen because an
  earlier `Read` call was window-truncated) — caught by the test run
  itself (a `Room.DoesNotExist` in the wrong test), fixed before commit.

## 2026-07-23 - Warehouse equipment issuing runbook scenario (backlog slice 6/9)

- Docs-only. Added `### 6. Equipment issuing and deduction review` to
  `docs/deployment/jober-demo-runbook.md`'s headline sequence, following
  the existing numbered-section presenter-script format (sections 1-5):
  issue an item as Coordinator → flag unreturned → switch to Manager →
  approve or waive in Equipment reviews, calling out the slice-5 badge
  colors (neutral/warning/success) as the demo's actual point.
- Chose a runbook entry over a new Playwright test because e2e coverage
  of the issue/return/flag actions is already thin (only the review
  *queue* page has e2e coverage — `tests/e2e/test_feature_pages.py:79-82,
  133-136`) and this is explicitly a "show it to the client" ask, i.e. a
  human presenter walkthrough, not a regression check.
- Removed "equipment recovery review" from the `## Supporting flow`
  fallback list since it's now a full headline section rather than an
  if-time-allows extra — avoids the same flow being listed twice.
- Verified every button/page label referenced in the new section
  (Flag unreturned, Equipment reviews, Approve charge, Waive) against the
  actual template strings — all match verbatim, so the script won't send
  a presenter looking for a button that reads differently.

## 2026-07-23 - Warehouse: better visual for "Issue" (backlog slice 5/9)

- `templates/panels/logistics_equipment.html`'s issued-items list
  (person-detail page) previously only badged the deduction-review state
  (`review_status != 'none'`, plain `<span class="badge">`) — a currently
  issued item with no review was bare text, indistinguishable at a glance
  from the deduction-review states.
- Every issued row now gets a status badge: neutral "Issued" (no review),
  the existing warning badge for "Pending review"/"Charge approved", and a
  new success-colored badge for "Waived". Added `.badge-neutral` and
  `.badge-success` variants (`static/src/css/app.css`) reusing the
  existing `--n100/--n300/--n700` and `--success/--success-soft` tokens
  already defined for both themes — no new colors invented. Added
  `.equipment-issue-row` (flex, space-between, wraps) to lay out item name
  + badge on one line without a new template-wide layout change.
- The "Issued" label needed no new translation — it already existed as
  the `EquipmentIssueStatus.ISSUED` model choice label, so `{% trans
  "Issued" %}` reuses the existing sk/hu/uk catalog entries verbatim
  (confirmed via extraction diff: no new msgid, no fuzzy).
- Verified visually (not just markup review): seeded three issued rows on
  one person covering all three states (none/pending/waived — waived
  required a raw ORM tweak since stock-tracked issuance blocked a second
  real `issue_equipment()` call without prior stock receipt) and took a
  full-page Playwright screenshot logged in as manager. All three badges
  render with distinct colors and correct labels/charge amounts; the
  return/flag-unreturned actions still only show for the un-reviewed row.

## 2026-07-23 - Audit log: filter by target worker (backlog slice 4/9)

- `core/audit/views.py::audit_log` gained a `worker` GET filter: resolves
  the entered text against `Person.search_name__contains` (same pattern
  as `core/people/views.py::people_list`'s existing name search, reusing
  the precomputed indexed field rather than a fresh `icontains` on two
  columns), then narrows `AuditEvent` to `target_type="Person"` with
  `target_id` in the matched people's pks.
- Confirmed this covers every action the user asked for ("edited,
  recruited, fired, blacklisted a worker") without needing to also match
  on `metadata`: `person.created`/`person.updated`/`person.archived`/
  `person.recycled` all audit with `target=person` directly, and
  blacklisting goes through `Person.set_status()` which independently
  audits `person.lifecycle_changed` with `target=self` — so even though
  `features/blacklist/services.py`'s own `blacklist.decided` event targets
  the case (not the person), the person-targeted lifecycle event already
  captures "this worker was blacklisted" for the new filter.
- Added the input to `templates/pages/audit_log.html` next to the existing
  actor/action/date filters, and threaded `worker` through both
  pagination links (previously missing `worker` broke the query string on
  page 2+ for any active filter, not just this new one — same in-line
  pattern the actor/action/target/date filters already used).
- New label "Worker (name contains)" — extraction fuzzy-matched it against
  unrelated prior strings in all three catalogs (sk→"Workers", hu→"Worker
  payments", uk→"Workers"), the exact failure mode the repo's i18n gotchas
  section warns about. Hand-corrected all three and cleared the fuzzy
  flags rather than accepting the guess.
- Added `tests/test_audit_log_page.py::test_filters_by_target_worker`:
  two people, one event each, asserts the filter narrows to the matching
  person only in both directions.

## 2026-07-23 - Fixed pre-existing CorvinumEU ledger e2e failure

- Root-caused the e2e failure flagged in the slice-1 entry below:
  `test_corvinum_shell.py::test_corvinum_ledger_groups_controls_and_keeps_tables_aligned`
  asserts `.ledger-summary-table` and `.ledger-entries` both render inside
  `.ledger-activity-panel` (`templates/partials/ledger_activity.html`).
  Both are conditionally rendered (`{% if summary.entries %}` /
  `{% if cycle.entries %}`), and the Thursday-summary half went missing.
- Cause: `clients/corvinum_eu/demo/management/commands/seed_corvinum_demo.py`
  seeds an illustrative open cash advance with `created_at` = real
  wall-clock time at seed. `features/advances/services.py:thursday_summary`
  only shows cash advances created up to *this week's* Thursday 14:00
  (Europe/Bratislava, C-Q2) — anything created later rolls to next week
  and never retro-inserts. The demo images got rebuilt/reseeded on a
  Thursday afternoon (past the 14:00 cutoff), so the seeded advance rolled
  out of the current week and the summary table simply didn't render —
  not just an e2e artifact, a real person spinning up the demo on a
  Thursday afternoon would see "No open advances" instead of the intended
  example.
- Fix: after creating the cash-advance entry, if its `created_at` lands
  after `week_cutoff(today)`, pin it one hour earlier via a direct
  queryset `.update()` (bypasses `auto_now_add`) so it's always inside the
  current week's window regardless of what day/time the demo is seeded.
- Verified live: inspected the seeded `LedgerEntry` rows and the rendered
  `/hu/ledger/?year=2026&month=8` HTML directly (via `corvinum_app.sh`)
  before and after the fix — summary table now present both times seeding
  ran after the cutoff.

## 2026-07-23 - Feedback form language picker + desktop layout/copy (backlog slices 2-3/9)

- **Slice 2 (language picker)**: `templates/pages/feedback_form.html` (public,
  unauthenticated, outside `i18n_patterns`) now embeds the same
  `language-switch` form pattern already used in `layouts/base.html`'s
  header, posting to the existing `set_language` view
  (`core/ui/views.py`, name `set_language`) with `next` pointed back at
  `request.path`. No new view code: `LocaleMiddleware` already honors the
  session/cookie language on unprefixed routes (URL-prefix detection is
  just the first check, not the only one), and the custom `set_language`
  wrapper's URL-prefix-translation step is a no-op here since
  `/feedback/<token>/`'s first path segment ("feedback") never matches a
  language code. Verified end-to-end with a real POST + cookie jar against
  the dev app: switching to `hu` persists across the next request and
  renders `<html lang="hu">` with translated copy.
- **Slice 3 (desktop layout + copy)**: added a `.feedback-panel` class
  (`static/src/css/app.css`) so the page uses `clamp(440px, 60vw, 760px)`
  instead of the shared `.login-panel`'s fixed 440px — addresses "looks
  small on desktop" while leaving `.login-panel` itself (real login page)
  untouched. Rewrote the form copy: an anonymous-and-goes-to-your-manager
  intro line, a rating question with a 1=poor/5=excellent hint, and a
  message prompt with example placeholder text. Added `label small {
  font-weight: 400 }` so hint text doesn't inherit the bold label style.
  Checked visually with Playwright screenshots at 1440px and 390px
  viewports (both clean, no overflow) before extracting/translating copy.
- New copy ("Go", the anonymous-answers line, the rating question + hint,
  the message question + placeholder) extracted and translated sk/hu/uk;
  diff confirmed no fuzzy flags on the new strings (an unrelated
  pre-existing fuzzy entry on `equipment_stock_receive.html`'s "Record
  receipt" was left alone — out of scope).

## 2026-07-23 - Feedback invitation QR code (backlog slice 1/9)

- First slice of a 9-item manual-QA backlog filed by the user (feedback,
  finance, warehouse, equipment, audit, reports, apartments, messaging —
  broken into a sliced plan, one branch per item).
- Feedback invitation links (`FeedbackLink`, `features/feedback/views.py`)
  now render an inline SVG QR code of the public form URL alongside the
  existing raw-URL text, behind a `<details>`/`<summary>` disclosure per
  link on `feedback_inbox.html` so the list stays scannable with many links.
- Lifted the existing 2FA QR helper (`core/accounts/views.py:_qr_svg`,
  ADR 0024/segno, previously private to that view) into a shared
  `core/ui/qr.py:qr_svg()` — both 2FA enrollment and feedback invitations
  now call the same helper instead of duplicating the segno call.
- New copy ("Show QR code") extracted/translated (sk/hu/uk) via
  `scripts/compile_messages.sh --extract`; diff confirmed no fuzzy flag,
  only the one new msgid plus source-line churn.
- **Found, not fixed (out of scope for this slice)**: the full Playwright
  e2e suite has one consistent failure —
  `test_corvinum_shell.py::test_corvinum_ledger_groups_controls_and_keeps_tables_aligned`
  (`summaryAndEntriesMerged` assertion) — reproduced twice on this branch
  and confirmed present on a clean `main` worktree with none of this
  slice's changes, so it predates this work. Flagging for a separate fix;
  not addressed here.

## 2026-07-21 - Hungarian catalog fuzzy-match cleanup + panel help text

- Root-caused a user report of "mislabeled" CorvinumEU panels: the Corvinum
  ledger/checklist/advances panels were already fully and correctly
  translated. The actual defect was 47 entries in
  `locale/hu/LC_MESSAGES/django.po` left `#, fuzzy` from a prior `msgmerge`
  run that paired new English msgids with unrelated stale Hungarian text —
  the exact failure mode this file's own Gotchas section warns about.
  Concentrated in `features/logistics` (equipment/accommodation, reused by
  CorvinumEU) and 2 in `core/people`. About a third were substantively wrong
  (e.g. a stock-count message read as a candidate-scheduling message and
  dropped its `%(available)s` placeholder; a date field read as "currency";
  `EquipmentStockLot`'s `initial_quantity`/`remaining_quantity` and
  `initial_value`/`remaining_value` all collapsed to the same generic
  Hungarian word). Hand-corrected and cleared every fuzzy flag; none were
  bulk-stripped.
- Added missing help text under the checklist and advances panel titles
  (`templates/panels/checklists_items.html`, `templates/panels/
  advances_ledger.html`), matching the explanatory-paragraph pattern already
  used in `templates/partials/ledger_activity.html`. Considered renaming
  "Thursday summary" for clarity but kept it — it's the established product
  term for this exact weekly cash-advance process, referenced throughout
  `docs/platform/corvinumeu-peopleops-design.md` and the demo script.
- Re-extracted all three catalogs (`scripts/compile_messages.sh --extract`)
  for the 2 new help-text msgids and recompiled `.mo`; translated the new
  strings in hu/sk/uk. Verified via diff that extraction touched no other
  msgid content (0 removed, only the 2 additions), just `#:` source-comment
  reordering.
- **AI-drafted translations**: per `docs/i18n-seeded-data.md`,
  native-speaker review of Hungarian (and the SK/UK spot-checks) remains the
  standing pre-demo task — not claimed as final sign-off here.
- **Deferred**: `locale/sk` and `locale/uk` each independently carry the
  same 47 fuzzy msgids (identical upstream `msgmerge` run). Not fixed in
  this slice — flagged as a follow-up of the same bug class.

## 2026-07-21 - Corvinum ledger panel-order correction

- Corrected the first compact-ledger composition after staging review: the
  smaller Cycle card now occupies the desktop column beside Record entry, and
  the larger Thursday summary + Entries card spans the full row below.
- Kept document order aligned with visual and keyboard order by extracting the
  cycle and activity cards into template partials rather than applying CSS-only
  reordering. Tablet/mobile order is Record entry, Cycle, then activity.
- No ledger data, calculations, permissions, exports, or actions changed.

## 2026-07-21 - Corvinum ledger workspace compaction

- Reworked the Corvinum ledger into a desktop workspace: the entry form uses a
  compact two-column field grid beside one activity panel, while tablet/mobile
  layouts retain a single-column workflow.
- Merged the Thursday cash-distribution summary and selected-cycle Entries into
  that activity panel. Cycle totals, filters, CSV, inclusion, and settlement
  actions remain in their own shorter full-width panel below.
- Kept all ledger services, calculations, permissions, exports, confirmation
  flows, and settlement behavior unchanged. Wide entry tables still scroll
  inside their panel rather than widening the page.

## 2026-07-21 - Corvinum payslip issue date

- Added a server-owned issue date to payslip records. Managers may enter it
  when recording a payslip or leave it blank to use the Europe/Bratislava
  creation date; it is intentionally independent of the payroll month.
- Existing rows are backfilled from their localized creation timestamp. The
  resolved date is included in structured audit metadata and shown to Manager
  and Observer users in the responsive Recorded payslips table.
- Kept the encrypted PDF, email naming/content, and person wage-versus-payslip
  overview unchanged. Jober receives only the compatible schema migration;
  its payslip feature remains disabled.
- Added deterministic fictional issue dates to the Corvinum seed and updated
  the presenter route to explain period versus issue date.

## 2026-07-20 - Corvinum wage and payslip source overview

- Reconciled the safe wage-ledger slice from the preserved branch onto current
  main without importing its unsupported computed-net formula. Corvinum now
  records one positive Decimal gross-wage source per person/calendar month and
  displays it beside the independently recorded net payslip on the person card.
- The UI explicitly states that taxes, levies, and statutory payroll are not
  calculated. Gross-versus-net differences are not labelled mismatches. The
  operational advance/deduction ledger retains its separate 21st-to-20th cycle.
- Added Manager write and Manager/Observer read policy, Corvinum-only routing,
  deterministic fictional June/July fixtures, responsive tables, and an
  expanded 14-section presenter/checker sequence with exact numeric checkpoints.
- The numeric checkpoint belongs to fictional candidate Eszter Varga, not
  Marek Skladník. This isolates deterministic source values from Marek's
  persistent encrypted-delivery rehearsal history.

## 2026-07-20 - Shared responsive audit table

- Ported the isolated audit-table layout fix from the parked wage-ledger branch
  without merging any wage-ledger code. The audit template now uses the shared
  responsive data-table primitive, semantic column headers, and an
  audit-specific timestamp class.
- Wide audit data scrolls inside its panel instead of widening the page.
  Timestamps and record references remain on one line, while the reason column
  absorbs flexible width. Because the fix lives in shared CSS and the shared
  template, both Jober and Corvinum receive the same behavior.

## 2026-07-20 - Corvinum full-feature presenter walkthrough

- Expanded the Corvinum manual runbook into a 13-section, 40-45 minute route
  with 20-minute and 10-minute cuts. The route now covers client isolation,
  Reports, projects/exports, intake v4, trials, readiness/checklist activation
  gates, notifications, compliance, equipment recovery, ledger controls,
  encrypted payslips, person/global audit, and Observer RBAC.
- Separated disposable-local and persistent-staging instructions, including
  TOTP setup versus verification, unique fictional records, payslip
  create-versus-resend behavior, recovery paths, and the deployed feature
  boundary. At that checkpoint the parked wage-ledger branch was explicitly
  not presented; the later reconciliation entry above supersedes that boundary.
- Added a companion 13-section HTTP checker. It discovers rendered IDs instead
  of assuming database primary keys, verifies activation and role boundaries,
  avoids fixed payslip-period collisions, and keeps provider-backed email off
  unless explicitly approved.
- Added a sanitized verification summary for the prior manual/automated run.
  TOTP secrets, provider credentials, recipient details, and one-time PDF
  passwords are not retained in the repository.

## 2026-07-20 — Jober second-interview headline demo

- Removed Jober transport from flags, routes, navigation, seeds, project UI,
  and readiness enforcement while preserving historical models and migrations.
- Added server-owned under-18/near-18 warnings to person intake, edit, detail,
  and an authenticated htmx fragment with full-submit fallback.
- Added Jober warehouse stock receipts, immutable movements, FIFO lots and
  allocations, transactional issue/return/adjustment services, idempotency
  keys, current balance, and monthly movement reporting. CorvinumEU keeps the
  legacy issue-without-stock policy.
- Added effective accommodation cost periods, separate worker payments, and a
  daily-prorated monthly capacity/cost/loss/margin report with no payroll side
  effects. Legacy room-rate fields and reports remain compatible.
- Added project regions and workbook-facing signed finance entry/display/CSV,
  regional roll-ups, project opt-out, and dynamic inclusion of extraordinary
  categories while preserving positive internal magnitudes.
- Refreshed fictional Jober seeds and the demo runbook for the five headline
  amendments. Telegram, DAC attachments, feedback replies, consolidated debt,
  actor-complete person history, and project CRUD remain deferred.

## 2026-07-17 — Secondary blacklist fingerprint (name + DOB + mother's maiden name)

- Added a second re-entry fingerprint type alongside the optional ID code: a
  canonical composite of the person's name tokens (sorted, so first/last entry
  order is irrelevant), ISO date of birth, and the mother's maiden name. The
  maiden name is a new transient input — hashed into the keyed fingerprint at
  intake or manual proposal, never stored as a person field, intake answer, or
  audit value.
- Fixed the fingerprint normalizer to transliterate diacritics (NFKD plus a
  small fold table for ß/đ/ø/ł/æ/œ) instead of deleting accented letters;
  "Kováč" now normalizes to KOVAC rather than KOV. ASCII identifiers are
  unchanged, so existing stored ID fingerprints keep matching without any
  re-hash or data migration.
- Matching stays "warning, not silent merge": a composite hit auto-proposes a
  case for manager decision and never blocks person creation. New
  `check_matches` requires type+hash agreement so hashes never cross
  fingerprint types; the manager queue now shows a "Matched via" row and the
  intake warning names the matched fingerprint types.
- Seeded Recruiter intake v4 with the transient mother's-maiden-name question;
  manual proposal gains an optional equivalent input. New identifier-type
  label, form strings, and warning localized into SK/HU/UK (plus five
  pre-existing untranslated notification model labels).
- Granted `person.archive` to Jober managers (`clients/jober/policies.py` and
  the Jober permission matrix): the action existed in core and Corvinum but was
  unmapped for Jober, which failed the RBAC completeness test.

## 2026-07-16 — Consolidated session handoff

- Added `docs/session-summary-2026-07-16.md`, consolidating the completed Jober
  and CorvinumEU product work, demo workflows, provider boundaries, public
  staging state, verification evidence, and remaining real-data/production
  gates. It contains no credentials, phone numbers, recipient addresses, or
  worker PII.
- Indexed the handoff from `docs/README.md`. This documentation-only addition
  does not require an application rebuild or staging deployment.

## 2026-07-16 — Checklist toggles preserve workflow position

- Changed CorvinumEU activation-checklist toggles to refresh only the checklist
  panel through htmx. The critical-item count, completion mark, and staff
  attribution update together without a full-page navigation or jump to the
  top of the person record.
- Preserved the ordinary CSRF-protected POST and person-detail redirect as the
  no-JavaScript/full-page fallback. Stable button IDs allow focus restoration
  after the panel swap, and the existing notification trigger continues to
  refresh actionable alerts after the mutation.
- Added focused fragment/fallback coverage and a browser regression asserting
  that the URL and scroll position remain unchanged after a toggle.

## 2026-07-15 — CorvinumEU public staging release

- Built the committed Corvinum demo release `12d0735` locally without runtime
  credentials and deployed that image to the isolated `corvinum-staging` Dokku
  app on syncmetric-prime with Dokku's image-streaming deployment path.
- The public staging app uses the Corvinum production settings layer and its
  own PostgreSQL service, but seeds only fictional demo data. SMTP delivery is
  intentionally a separately pending runtime configuration step; Doppler is
  never included in the image or build stage.

## 2026-07-15 — Safe payslip resend and SMTP failures

- Payslip resend now uses the last successful recipient address, rather than a
  subsequently changed person email. SMTP/network failure is converted to a
  translated safe error, leaves delivery metadata unchanged, and cannot return
  a raw 500 page.

## 2026-07-15 — Manager equipment catalogue

- Added a manager-only Equipment catalogue to the shared logistics feature:
  search, create, edit, and deactivate items with EUR unit prices. Catalogue
  changes are audited; coordinators retain issue/return actions only.

## 2026-07-15 — Optional intake email for CorvinumEU

- Published questionnaire v3 adds an optional, server-validated Email input on
  the Contact panel and maps it to the existing person email field. This makes
  later encrypted-payslip delivery possible without making email a condition
  of recruitment or activation.

## 2026-07-15 — CorvinumEU trial-day workflow enabled

- Enabled the existing shared trial workflow through Corvinum’s feature flag
  and client policy. No model, migration, dependency, or client branch was
  added: the client layer selects the shared routes and role grants.

## 2026-07-15 — Corvinum blacklist archive and re-entry workflow

- Added a manager-only operational archive action and the Corvinum intake’s
  transient blacklist ID/type inputs. Archive is intentionally distinct from
  erasure: it preserves an approved case and its active HMAC fingerprint.
- Guided intake passes the transient identifier into the existing feature hook
  only after the person is created; it never persists the raw identifier in an
  intake answer, person field, or audit payload. A match creates a proposed
  case and preserves manager review as the decision point.

## 2026-07-15 — Corvinum Basic production backup operations

- Added dependency-free, deployment-host-only scripts for encrypted off-site
  PostgreSQL/release-manifest backups, backup health enforcement, and explicit
  on-demand Corvinum staging control. They use existing Dokku, OpenPGP, and
  OpenSSH tooling; no runtime dependency, migration, model, endpoint, or
  client code was added.
- The backup workflow has a hard boundary against `dokku config:export` so
  Doppler-synchronised secrets cannot enter a backup archive. Future ERP media
  is opt-in through an explicit absolute directory.

## 2026-07-15 — Isolated Corvinum demo SMTP runtime

- Updated `scripts/corvinum_app.sh` to accept a complete Django SMTP
  configuration injected by Doppler while retaining console email as its
  secret-free default.
- SMTP configuration is validated fail-closed and forwarded only to the web
  container. Migration and seed containers remain on console email and never
  receive the SMTP password.
- Documented the dedicated `hr_system/dev_corvinum_demo` configuration and the
  deliverable, non-personal test-recipient requirement.

## 2026-07-15 — Strict client identity on authentication screens

- Removed the hard-coded Jober heading from the shared login template and all
  remaining hard-coded Jober browser titles from shared pages. Titles and
  visible identity now come from the active client's `BRAND_NAME` setting.
- Added a shared authentication lockup to login, TOTP enrollment, and TOTP
  verification. Corvinum now supplies its client-owned logo through
  `BRAND_LOGO`; Jober continues to supply its own SVG.
- Added source, rendered-template, and browser boundaries that fail if a shared
  page hard-codes either client or if Corvinum authentication renders Jober
  identity. No dependency, migration, endpoint, or external asset was added.

## 2026-07-15 — Corvinum personnel-intake demo bootstrap

- Corvinum's clean local bootstrap now seeds the published, versioned intake
  questionnaire before its fictional client scenario. **Add person** therefore
  opens the three-step guided intake after every disposable-database reset.
- The staging seed order and client walkthrough now match the executable
  bootstrap. The walkthrough includes a fictional `Olena Demo` intake act and
  carries that record into checklist and notification demonstrations.
- No dependency, migration, endpoint, external asset, or real PII was added.

## 2026-07-14 — Operations data-entry workspaces

- Trials now supports lookup, central scheduling from Available candidates, and
  audited pending-trial edits. Coordinator writes are scoped to responsible
  projects; existing recruiter and manager scheduling access is preserved.
- Transport now combines filtered records, create/edit panels, and trend charts.
  Central duplicate project/week creation fails clearly, while project quick
  entry remains idempotent.
- Managers can create/edit/deactivate accommodation locations and rooms.
  Coordinators retain assignment-only access. Occupancy protects capacity and
  deactivation; inactive/full rooms are excluded from new assignments.
- Added the `Room.is_active` field and per-location unique room-label constraint.
  No dependency, external asset, or frontend toolchain change was introduced.

## 2026-07-14 — Consistent Jober panel clearance

- Added shell-level vertical rhythm between adjacent operational sections in
  Jober, matching the established CorvinumEU behavior. This closes the
  grid-to-feature-panel seam on person details and prevents independently
  contributed panels from visually touching.
- Existing grid gaps, page-header spacing, responsive stacking, and both theme
  palettes remain unchanged. No dependency, model, migration, or asset added.

## 2026-07-14 — Action-oriented dashboard tooltips

- Replaced generic dashboard “Details” help with a localized action heading
  and a concise destination/filter description. Structured content is assigned
  as text nodes, while existing single-message navigation, confirmation, and
  notification tooltips remain backward compatible.
- Made linked report-tile providers supply their own meaningful tooltip copy;
  missing heading/body data now fails closed during report composition.
- Aligned dashboard promises with their drill-downs: Active projects opens an
  active-only project list, lifecycle rows retain their status filters, and
  inactive-reason rows filter People by the selected reason or “No reason”.
- Improved keyboard behavior found during Firefox verification: focused
  tooltips survive focus-induced scrolling and reposition instead of being
  immediately dismissed. Pointer-only tooltips still dismiss on scroll.
- Added EN/SK/HU/UK copy and kept the feature dependency-free, client-neutral,
  and free of models, migrations, cookies, endpoints, or external assets.

## 2026-07-13 — Reliable language-prefix switching

- Replaced Django's stock language endpoint with a thin shared wrapper that
  preserves its CSRF, cookie, language-validation, and safe-redirect behavior.
- When the active language cookie disagrees with the current URL prefix, the
  wrapper now translates from the prefix explicitly. Selecting a language can
  no longer write the new cookie while redirecting back to the old-language
  page.
- Added Jober EN/SK/HU/UK and CorvinumEU SK/HU regressions, including query
  strings, client-specific cookies, hostile redirect rejection, and a real
  browser interaction.

## 2026-07-13 — Shared contextual tooltips

- Added one delegated, dependency-free tooltip controller shared by Jober and
  CorvinumEU. It supports delayed mouse hover, immediate keyboard focus,
  Escape dismissal, hover persistence, viewport-aware placement, restored
  `aria-describedby`, htmx-swapped content, and touch-focus suppression.
- Added contextual coverage to both navigation systems, notification icon
  controls, linked metrics/cards/rows, and confirmation-backed actions. Visible
  routine buttons remain uncluttered; existing localized confirmation text is
  reused instead of duplicated.
- Added client- and mode-specific semantic tooltip tokens, reduced-motion
  handling, and a 22rem responsive maximum width. No dependency, endpoint,
  model, cookie, service, or external asset was introduced.

## 2026-07-13 — Theme-aware Jober logo

- Added a dark-mode-only color treatment to the supplied SVG. Hue, saturation,
  and brightness move the blue artwork toward the night palette's periwinkle
  accent while preserving the white inset; Light mode and the source vector are
  unchanged, so no duplicate brand asset is required.

## 2026-07-13 — Jober night palette revision

- Replaced the blue-heavy midnight palette with a warmer “after-hours control
  room” treatment: graphite/aubergine surfaces, periwinkle interaction color,
  amber attention states, and mint success signals.

## 2026-07-13 — Jober navigation iconography

- Added a first-party set of fourteen restrained outline SVG symbols for the
  Jober folder tabs. Icons cover people, projects, field work, compliance,
  accommodation, transport, reports, audit, reviews, blacklist, finance,
  ledger, payslips, and feedback.
- Kept labels as the accessible link names and marked the icons decorative.
  The strokes inherit light/dark, hover, focus, and active-state colors without
  a font, package, external asset, CDN request, or cross-client dependency.

## 2026-07-13 — Client light, dark and system themes

- Gotcha: do not compile Django catalogs with the host `pybabel` command. Its
  default domain is `messages`, not `django`; the mistaken invocation generated
  an Ubuntu Apport crash report for a missing file. Use the repository's
  containerized Django catalog workflow.
- Added a shared first-paint-safe Light/Dark/System controller with browser-local,
  client-specific persistence and live operating-system preference updates.
- Jober keeps its calm industrial light mode and gains a navy “midnight
  operations” palette. Its supplied SVG replaces the temporary text badge.
- Corvinum keeps its dark-default glass treatment and gains the light palette
  from its PeopleOps reference; its sidebar remains dark in both modes.
- Theme selection is available before and after authentication and adds no
  endpoint, cookie, model, dependency, or background request.

## 2026-07-13 — Floating session notification center

- Added the client-neutral `core.notifications` domain and a dismissal migration
  that stores only user/key/version state, never copied notification content.
- Added role-scoped routine updates from the audit log and current actionable
  alerts for trials, readiness, compliance, equipment review, blacklist,
  feedback, and enabled checklists.
- Added the shared top-right bell/popover to Jober and CorvinumEU with deep links,
  manual refresh/dismissal, responsive controls, and htmx refresh events.
- Kept delivery interaction-driven. True idle-browser realtime delivery remains
  deferred pending an ASGI/SSE or WebSocket ADR.
- Added EN/SK/HU/UK interface strings and feature-alert wording.

## 2026-07-13 — Corvinum selector, personnel email and interactive Reports

CorvinumEU now uses a client-specific language cookie, so the Jober demo on
the same localhost host cannot overwrite its SK/HU preference. The shared
person form includes the worker email (needed for payslips). Corvinum inherits
the consolidated Reports overview: its metric/status cards are drill-down
links, the old Overview navigation item is gone, and the Reports title uses
the active client brand.

## 2026-07-12 — Specific activation-blocker messages

The activation gate now explains the concrete incomplete requirement(s), rather
than returning a generic readiness failure. The message and each blocker use
the active EN/SK/HU/UK locale, and incomplete legacy N/A records are blocked
until they include their required reason.

## 2026-07-12 — Readiness form attention states

The four-pillar readiness form now surfaces an attention summary and highlights
incomplete requirements, missing N/A reasons, and an already-stored future
medical date. N/A reason fields appear only when relevant and are required in
that state. Future medical dates are rejected on save.

## 2026-07-12 — Audit action localization

Audit action codes remain stable in storage and query strings, but the audit
screen now renders human-readable labels for every current action in EN/SK/HU/
UK. This covers the filter options as well as event rows, with a readable
fallback for any future unknown code.

## 2026-07-12 — One operational Reports surface with actionable metrics

- Overview and Reports are now one reporting surface: the legacy overview URL
  renders the same page, while navigation and brand links expose only Reports.
  This removes duplicate navigation without breaking existing bookmarks.
- Summary and status metrics drill into the corresponding projects, people,
  trials, compliance, accommodation, equipment-review, or finance workflow.
  Restricted operational targets stay inert for roles that cannot open them.
- Monetary values on accommodation, equipment-review, logistics, and finance
  reporting surfaces explicitly state **EUR**.

## 2026-07-12 — Trial appointments and scheduling authority

- A trial now records a timezone-aware arrival appointment (`scheduled_for`)
  alongside its legacy date. The person card and field queue clearly show the
  trial destination (project and office) and arrival time.
- Recruiters, Coordinators, and Managers can schedule trials. The permission
  matrix is kept in sync.
- Trial results are deliberately all neutral secondary buttons until an
  operator chooses an outcome, avoiding a misleading preselected blue action.

## 2026-07-12 — Equipment clarity, localized history and safer person forms

- Equipment cards now state both their aggregate value and every catalog item's
  unit price explicitly in **EUR**, including the amount under a deduction
  review. The issue selector also shows the unit price before an operator
  issues an item.
- Person timeline events translate canonical lifecycle values and seeded
  equipment names at render time, while preserving unknown historic values as
  a safe fallback.
- The disability-type input follows the disability checkbox locally and is
  visibly disabled when irrelevant. The form also clears that sensitive detail
  server-side whenever the checkbox is not selected.
- Shared flash messages are fixed, readable bottom-center toasts, automatically
  dismissing after three seconds. Corvinum centers them in its usable main area
  rather than across the sidebar.

## 2026-07-12 — Deploy smoke + backup/restore drill scripts (§2 complete)

`scripts/deploy_smoke.sh` (post-deploy gate, fails closed) and
`scripts/backup_restore_drill.sh` (dump → scratch restore → exact row-count
proof) — both verified live against both stacks; wired into
deployment-plan.md's release step and backup section. With error logging,
the audit page, and the corvinum test lane, every §2 production-readiness
item that needed no external input is done. Staging now waits only on owner
asks D1–D4.


## 2026-07-12 — Corvinum-flags test lane (closes the last audit finding)

Stage D says the suite passes under **each** client's flag set; until now only
Jober's lane ran. New `scripts/test_corvinum.sh` runs the shared/portable unit
tests under `clients.corvinum_eu.settings` against a dedicated `corvinum` DB:
**143 passed** (100 Jober-specific tests deselected via the new
`@pytest.mark.jober_only` marker — URLs/policies/languages that are Jober by
design; 7 modules importing not-installed feature models self-skip at
collection). Triage found **zero cross-client bugs** — every failure was a
legitimate client difference — plus one real test-hygiene bug: the active
language is thread-local and leaked across tests depending on execution
order; a global autouse fixture now pins each test to the settings default
(`tests/conftest.py`). Jober lane unchanged (283) and e2e 21 green. The lane
joins the per-slice workflow (CLAUDE.md).


## 2026-07-12 — Observability: error logging + audit-log page (production readiness §2)

- **Error visibility**: explicit `LOGGING` in base — `django.request` ERRORs
  and `django.security` warnings stream to stdout/stderr (formatted with
  timestamp/level/logger), root at `DJANGO_LOG_LEVEL` (default WARNING).
  Production 500s now show tracebacks in `dokku logs`/`docker logs` — the
  silent-500 class that slowed Stage C4 debugging is closed.
- **Who-did-what UI**: new `/audit/` page (core/audit/views.audit_log) over
  the existing append-only `AuditEvent` stream — filters for actor, action,
  record type, and date range; paginated 50/page; distinct-value dropdowns.
  Gated by `audit.view`, which now includes **observers** in both clients
  (owner request; matrices updated). Nav: folder tab (Jober) + sidebar item
  (CorvinumEU, `verified_user` icon). 18 msgids translated SK/HU/UK
  (715/715 clean after de-fuzzing the usual msgmerge mispair).
- Live-verified on both stacks: observer accounts render the page (SK and HU),
  demo data shows real event rows; LOGGING active in the running container.


## 2026-07-12 — Session longevity: cookie collision fixed + 30-day rolling sessions

Owner: "I need to log in too often." Two causes, both fixed:

- **Cookie collision** (the real culprit during dual-demo testing): browsers
  scope cookies by host and ignore ports, so Jober (:8000) and CorvinumEU
  (:8001) both writing Django's default `sessionid` evicted each other's
  login on every switch. Cookie names are now client policy:
  `jober_sessionid`/`jober_csrftoken` and `corvinum_sessionid`/
  `corvinum_csrftoken` — verified live: one cookie jar holds all four,
  both sessions authenticated simultaneously.
- **Session policy** (owner decision): **30-day rolling** sessions —
  `SESSION_COOKIE_AGE` env-overridable (`DJANGO_SESSION_COOKIE_AGE`),
  `SESSION_SAVE_EVERY_REQUEST=True` so activity refreshes expiry and only
  inactivity logs out. Costs one session-row write per request (fine at this
  scale). Everyone logs in once more after this deploys (cookie renamed).
- Stack resets (`down && up`) still wipe sessions — inherent, documented.


## 2026-07-11 — Corvinum shell brand fit + centered content

Adjusted the Corvinum-only theme without changing the shared Jober shell. The
full `CorvinumEU PeopleOps` brand now fits inside the existing 280px sidebar;
the main column is centered in the viewport space remaining beside the full
sidebar or 72px collapsed rail, and returns to full-width at the mobile
breakpoint. No horizontal overflow at 375px.

The official Playwright workflow now boots and seeds both Jober and CorvinumEU
on the same internal E2E network. New Corvinum browser coverage measures brand
containment and main-column centering at 1650px, repeats centering with the
collapsed rail, and checks the 375px viewport. While extending the runner, its
health probe was fixed to pass the inline Python program through stdin; before
this, `docker run ... python -` received no program and could report success
without probing the app.

Verification: **19/19 e2e green**; live screenshot reviewed; desktop geometry
sidebar `0–280`, main `325–1605`, shared center `965`; rail and mobile checks
green. No dependency, model, migration, permission, or business-rule change.

Follow-up visual review added a Corvinum-only 16px vertical rhythm between
adjacent top-level content sections. The page header keeps its existing spacing
and top-level workflow-panel margins are normalized to avoid a doubled gap.
Playwright measures the project-detail overview→logistics separation at exactly
16px. Updated browser baseline: **20/20 e2e green**.

Checklist control investigation: a manually opened/stale form after a local
rebuild produced Django's expected CSRF rejection. The live, rendered form
already carries `{% csrf_token %}` and posts correctly; no protection was
weakened. Added a Corvinum coordinator browser regression that checks the token
and cookie then performs a real checklist toggle. Updated browser baseline:
**21/21 e2e green**.

Corvinum ledger layout pass: added labelled compact cycle controls, grouped
cycle actions, bounded summary output, and aligned ledger columns/actions. The
shared ledger template receives semantic classes only; all visual treatment is
Corvinum-only. Phone layouts keep the page viewport-width while the cycle
summary and detailed entries tables independently scroll when dense. A new
browser regression measures the desktop controls/tables and confirms zero
page-level overflow at 375px. Updated browser baseline: **22/22 e2e green**.

## 2026-07-11 — Controlled build/test artifact policy

Owner-approved clarification to `AGENTS.md` §7: agents may run committed,
isolated build and E2E workflows that fetch repository-pinned artifacts when
integrity is verified before execution and restricted tooling stays out of the
runtime image. This resolves the conflict between the former blanket
binary-fetch prohibition and the required Tailwind/Playwright Docker workflows.
Ad-hoc or unverified downloads, host-package installation, and agent retrieval
of media/fonts/images/credentials remain prohibited.

The same owner decision clarifies secret-bearing tests: human sessions or
automated integration checks that exercise external providers must be launched
through Doppler (or the approved production equivalent) and inject credentials
only into the runtime/test process. Standard unit and Playwright suites remain
secret-free and deterministic.

## 2026-07-11 — Destructive-action confirmation dialog

Completed the owner-requested confirmation layer for high-impact workflow
actions. A shared, dependency-free native `<dialog>` is included by both the
Jober and CorvinumEU shells; forms or individual submit buttons opt in with a
translated `data-confirm` description. Sixteen controls/forms now describe
the consequence before worker exit, blacklist decisions/removal, equipment
charge review, finance lock/reopen, and ledger inclusion/settlement/correction.

The delegated JavaScript preserves native form validation and the exact
clicked submitter, defaults focus to Cancel, clears pending state on
Cancel/Escape/close, and uses `window.confirm` as a fail-safe where native
dialog support is unavailable. The confirmation action has danger semantics,
44px targets, and phone-width stacking. This is a UI safety layer only: all
existing server-side RBAC, service validation, audit, and idempotency behavior
is unchanged. No dependency, model, migration, permission, or workflow-rule
change.

Manual review caught internal notes rendering on both shells: first the shared
dialog note, then CorvinumEU's font-preload note. Django's `{# ... #}` comment
form does not span lines. Both now use `{% comment %}...{% endcomment %}`; a
repository-wide template scan rejects any future multiline short comment, and
the shared-shell response test rejects leaked dialog prose.

Verification: 276 unit + 18 e2e green; ruff, dependency-direction, no-Node,
vendor checksum, migration-consistency, and diff checks green. SK/HU/UK
translations and compiled catalogs are included.

## 2026-07-11 — Jober seeded catalogs localized + the pattern documented

Same db_trans treatment for Jober (owner request): **inactive reasons**
(person page + reports), **finance categories** (month detail), **intake
questionnaire** (panel titles + question labels), and the **equipment seeds
converted to canonical English** ("Work boots", "High-visibility vest",
"Safety helmet" — scenario lookups updated; SK renders the old Slovak names
via translation, HU/UK now localize too). New `catalog_i18n.py` registries in
core/people, features/{finance,intake,logistics}. 31 msgids translated
SK/HU/UK — catalogs **680/680** per msgfmt. The whole pattern is now written
down in **`docs/i18n-seeded-data.md`** (canonical-English seeds → db_trans →
catalog_i18n → extract/translate/verify → reseed via down&&up), linked from
CLAUDE.md conventions and the docs index.


## 2026-07-11 — i18n sweep: seeded catalog data now localizes (db_trans)

Owner-reported gaps (HU UI showing English checklist items, blacklist
categories, equipment names) were **DB content, not msgids** — gettext never
touches rows. New pattern: seeds store the **canonical English string**;
rendering passes it through a `db_trans` template filter (`core/ui`
templatetags — runtime gettext; operator-entered text falls through
unchanged); the strings are registered as msgids in dedicated
`catalog_i18n.py` files (`features/blacklist`, `clients/corvinum_eu`) because
applied migrations must not be edited and makemessages ignores `demo` paths.
Applied to: blacklist category labels (panel + queue), checklist item labels
(panel + the activation-blocked error), equipment item names (panel + issue
rows), the equipment-charge ledger note (now created via gettext in the
actor's locale), and the feedback form's hardcoded "Jober" → BRAND_NAME.
15 new msgids translated SK/HU/UK — catalogs **649/649** per msgfmt.
Template-literal audit found no other untranslated text nodes. Bonus PR #60
earlier: font preloads kill the icon-ligature flash (all assets self-hosted —
verified zero external URLs in page + CSS).


## 2026-07-11 — Stage C8: the real CorvinumEU shell (peopleops prototype port)

Owner escalation: the :8001 client was the **Jober shell in corvinum colors**
— C4 had only lifted tokens, never the prototype's design. Fixed by porting
the peopleops prototype (corvinumeu repo, Addendum A2) properly:

- **Client template layer**: corvinum settings prepend
  `clients/corvinum_eu/templates` to TEMPLATES dirs; a client
  `layouts/base.html` override replaces the shell — **left slide-out
  sidebar** (desktop collapse-to-rail persisted, mobile off-canvas + scrim),
  grouped nav (Workforce/Operations/System) with Material Symbols icons,
  user card + language + sign-out in the sidebar foot, hamburger topbar.
  Same blocks, URLs, `{% flag_on %}`/`{% can %}` gating as the shared shell —
  every page renders unchanged inside it; anonymous pages (login/2FA) get a
  centered no-sidebar layout.
- **Vendored assets (§3.2)**: Hanken Grotesk / Inter / JetBrains Mono +
  Material Symbols subset woff2 + brand logo copied from the prototype
  (provenance chain corvinum.eu site → prototype → here) with SHA-256s in
  `clients/corvinum_eu/static/corvinum/VENDOR-MANIFEST.md`. `shell.js` +
  `theme.css` are first-party ports (no new third-party code).
- **theme.css** rewritten to the prototype's exact dark palette
  (#050b14 bg, #0a1526 sidebar, cobalt #005bbf / #1a73e8) + full shell CSS;
  dark-only pending C-Q8. Sidebar nav msgids translated (SK/HU/UK); catalogs
  verified **634/634 translated** per language via msgfmt --statistics.
- Jober untouched: shared base.html unchanged; 273 unit + 16 e2e green.
  Live drive on :8001: sidebar + icons + gating (recruiter sees no
  Payslips/Ledger), anon login centered, fonts served fingerprinted.


## 2026-07-11 — Docs separated per client + docs index

Extends the runbook convention repo-wide: **unprefixed = platform-shared**,
client docs carry `jober-`/`corvinum-` prefixes. Renamed (git mv): root specs
→ `Jober_{Product_Design,Finance_Specs,Messaging_Specs}.md`; deployment
`{local-demo,twilio-setup,dokku-staging}` → `jober-*`; all eight Jober-era
product docs → `jober-*`; `blacklist-legal-basis` → `jober-*`;
`permission-matrix` → `jober-permission-matrix` **plus a new
`corvinum-permission-matrix.md`** mirroring `clients/corvinum_eu/policies.py`
(deny-by-default note for unmounted Jober actions; trial-less lifecycle).
ADRs stay one chronological log. New **`docs/README.md`** index maps every
doc → owner → purpose. All living references updated (AGENTS, CLAUDE, ADRs,
code docstrings); journal history intentionally untouched.


## 2026-07-11 — Runbook naming: one per thin client

`docs/deployment/demo-runbook.md` → **`jober-demo-runbook.md`** (git mv);
**`corvinum-demo-runbook.md`** refreshed to post-C7 reality (2FA act now scans
the QR; payslip act names the flash message; reset tip for re-rehearsing
first-login enrollment). Both runbooks open with a pairing note naming the
other client + port. Cross-references updated (local-demo.md, CLAUDE.md).
Jober runbook also picked up the seed-chain correction from the earlier docs
audit (`seed_logistics` was missing from the listed chain).


## 2026-07-11 — Stage C7: 2FA QR codes (ADR 0024) + dark-theme flash messages

Owner demo-testing findings on :8001. (1) **QR enrollment**: `segno==1.6.6`
(pure Python, zero deps, BSD; cooldown satisfied by >1 year) renders the
otpauth URI as **inline SVG** server-side — no external request, no JS; shown
on a white `.qr-plate` so scanners work on dark themes; manual secret + URI
stay as fallback. ADR 0024 records the decision (hand-rolled Reed–Solomon and
vendored-JS alternatives rejected). (2) **Flash messages were unreadable** on
the corvinum theme (near-white `--ink` over the shell's hardcoded light
pastel `--*-soft` backgrounds — the payslip one-time-password message among
them): the corvinum theme now overrides the `-soft` tokens with translucent
dark tints and brightens `--success/--warning/--danger`. Setup-page msgid
updated + translated (SK/HU/UK). Both demo stacks rebuilt; live drive:
login → 2FA setup shows the QR, wrong code renders a readable error flash.


## 2026-07-11 — Stage C6: conformance fixes + dual demo stacks

Closes the 2026-07-11 conformance audit findings (owner-directed):

- **i18n (finding 1):** full extraction pass; **332 msgids** (Stage C strings
  + a long-standing backlog of model verbose names) translated in **SK/HU/UK**
  and all 132 msgmerge fuzzies reviewed/replaced (the known wrong-pairing
  behavior). Catalogs compile clean. Translations are AI-drafted — the
  **native-review ask stands** and now covers both products.
- **Payslip audit (finding 2):** creation moved into
  `features/payslips/services.record_payslip` — atomic, `full_clean`, and a
  `payslip.recorded` audit event; a pay amount can no longer appear without a
  trail.
- **CLAUDE.md (finding 3):** the stale "gated, do not build" platform line
  replaced with the executed-stages reality + pointers to both demo runbooks.
- **Dual demos (owner request):** `scripts/corvinum_app.sh` runs the CorvinumEU
  thin client on **:8001** (own DB/network, console email backend so payslip
  sends are visible in logs) side-by-side with Jober on :8000 — same image,
  different `DJANGO_SETTINGS_MODULE`, which is itself the platform pitch.
  New `clients/corvinum_eu/production.py` (whitenoise hardening layer) +
  `docs/deployment/corvinum-demo-runbook.md` (~30-min script, TOTP act,
  human-prep list). Base gains env-driven EMAIL settings (ADR 0023 delivery).
- **Fix found by the demo boot:** collectstatic ran under one client's settings
  but the artifact serves every client (§12.4) — a client theme missing from
  the manifest 500'd the page. Base now globs `clients/*/static`.

Not addressed (recorded): finding 4 — full pytest under corvinum flags in the
standard gate, and corvinum e2e coverage. Candidate next slice.


## 2026-07-11 — Stage C5: payslips — encrypted PDF pay statements (ADR 0023)

Client-requested **scope change recorded**: CorvinumEU now stores net pay
amounts and emails each worker an **AES-256 (PDF 2.0 R6) encrypted payslip**.
Design: SSN-as-password rejected; per-send **12-char truly random password**
(`secrets`, no-lookalike alphabet, shown `XXXX-XXXX-XXXX`, ~70 bits — PDFs are
offline-brute-forceable, so length is the security). The password is shown
**once** to the office user for phone/Messenger delivery — never stored,
never logged, never emailed; the PDF itself isn't stored either (regenerated
per send, fresh password on resend). PDF content built by a minimal stdlib
writer; **first new PyPI deps since the npm purge**, owner-approved per
AGENTS §3.1: pypdf 6.14.2 + cryptography 49.0.0 (+cffi/pycparser), cooldown
verified, wheels hash-pinned into both locks. `core/people.Person` gains an
optional contact `email`. New `payslip.manage` action (manager), Payslips
page + nav tab, flag off for Jober. Open questions: C-Q15 (password delivery
channel), C-Q16 (pay-data retention); C-Q6 boundary note updated.


## 2026-07-11 — Stage C4: corvinum.eu theme + validation — STAGE C COMPLETE

Theme: `CLIENT_THEME_CSS` hook in the shared shell (context processor + one
line in `base.html`); `clients/corvinum_eu/static/corvinum/theme.css` layers
the corvinum.eu tokens (dark glass surfaces, cobalt #005bbf, font stacks with
system fallbacks — no vendored font binaries) per §7.0/Addendum A2.

The C4 live drive caught a real flag bug: the shared nav/dashboard hardcoded
`trials_queue`/`compliance_list`/`accommodation_list`/`transport_trends`
links, so any client without those flags 500'd. Fix: `{% flag_on %}` template
tag; every feature tab now gates on **flag AND permission**, and the Ledger
tab joins the nav for advances-enabled clients. Jober's rendered nav is
unchanged (all its flags on).

Validation (Stage D bar, three flag sets): dep-direction clean · 265 unit +
16 e2e under Jober flags, assertions unchanged · smoke client boots · live
CorvinumEU drive on a real DB: migrate → `seed_corvinum_demo` → 2FA detour
enforced for managers → dashboard/people/person/ledger/blacklist/equipment/
compliance all 200 and themed → checklist on the person card → ledger balance
arithmetic verified (100 advance + 35 equipment charge − 30 travel = 105) →
Jober-only URLs absent. **ADR 0022 EXECUTED** — staging/production deployment
remains gated on CorvinumEU server/domain/DB names (C-Q14).


## 2026-07-11 — Stage C3: equipment charge → ledger link + CorvinumEU demo seeds

The §5.8↔§5.10 join: `features/logistics` gains a `deduction_approved_hooks`
registry (fired once per issue by `review_deduction`'s PENDING guard);
`features/advances` registers a handler (only when logistics is installed)
that turns an approved equipment charge into a linked, positive-magnitude
`PAY_DEDUCTION` (flag-guarded — Jober unchanged). New
`clients/corvinum_eu/demo` app with an idempotent `seed_corvinum_demo`:
4 fictional users @demo.corvinum.test (HR Admin = manager, C-Q9), two partner
companies, the §5.5 global activation checklist, equipment issue → flag →
approve → ledger deduction, an open Thursday advance, and travel money.


## 2026-07-11 — Stage C2: features/advances (advance & deduction ledger, §5.10)

CorvinumEU's anchor feature. Explicit-field `LedgerEntry` — positive
`Decimal` amounts only; meaning lives in `entry_type` (cash_advance /
pay_deduction / pay_addition), `pay_effect` (deduct/add/none, mapping
enforced), `settlement_status` (open → included → deducted, or cancelled).
Money rules per the recorded C-Q2..C-Q5 defaults: Europe/Bratislava
**Thursday 14:00** cut-off with late entries rolling forward (never
retro-inserted), **20th-to-20th** cycle keyed by end month (correct across
Dec→Jan), no hard deletes (admin delete disabled), cancel only while OPEN,
locked entries corrected via linked reversal entries with the opposite pay
effect. Ledger page (record/summary/cycle/actions), person-card panel with
open balance, Thursday + cycle CSV exports (proposed column layout). New
`ledger.enter`/`ledger.view` actions in both client policies + matrix.
Flag off for Jober — zero behavior change.


## 2026-07-11 — Stage C1: features/checklists (approval checklists, §5.5)

New feature app (installed for both clients, **flag off for Jober** — zero
behavior change): `ChecklistTemplate`/`ChecklistItemTemplate`/
`PersonChecklistItem` (who approved what, when), idempotent per-person
instantiation, audited ticking, and an **activation hard-stop** on open
critical items registered through the Stage B `register_activation_check`
hook — the mechanism ADR 0021 predicted would carry CorvinumEU's checklist
gates. Person-card panel via the surface registry; toggle endpoint mounted
only where the `checklists` flag is on (corvinum_eu). New `checklist.tick`
action granted in both client policy modules, mirrored in the permission
matrix.


## 2026-07-11 — Stage C0: CorvinumEU thin-client scaffold (ADR 0022)

Stage C activated by the owner (2026-07-11). ADR 0022 records the scope
mapping — reuse `features/{logistics(equipment),blacklist,compliance,intake}`;
build `features/checklists` + `features/advances`; `fuel_costs` NOT built
(design-doc A1: unconfirmed, secondhand); deployment deferred (no server
names). `clients/corvinum_eu/` lands: explicit INSTALLED_APPS (no finance/
messaging/feedback apps), CorvinumEU flag set, SK/HU, 2FA required for
managers, CE branding, trial-less lifecycle + grants in `policies.py`.
Unconfirmed client decisions build against recorded defaults —
`docs/product/corvinum-open-questions.md` (C-Q1…C-Q14).

Ops: the host lost `/var/lib/docker` (external deletion while the daemon ran)
— all images/volumes destroyed; daemon reset, test image rebuilt from the
hash-pinned `requirements/test.lock` on the digest-pinned Python base, dev DB
recreated. The accounting-project Postgres volume was unrecoverable (dead
before salvage was possible); Jober data was all re-seedable.


## 2026-07-09 — STAGE B COMPLETE: shared core + thin-client architecture

ADR 0021 executed end-to-end (PRs #36–#45), assertions unchanged throughout.

- **B-1/B0**: governance (owner waiver recorded), `pre-stage-b` tag,
  FEATURE_FLAGS + CLIENT_POLICIES, dependency tripwire (debt enumerated: 10).
- **B1 (a–c)**: decoupling — activation/exit hooks, the surface registry
  (person panels/banners/form-extensions/exit-relevance, report tiles/panels),
  per-feature exports and seeds, `clients/jober/demo`. **Debt 10 → 0.**
- **B2**: `git mv` reshape to `core/{accounts,audit,people,projects,ui,retention}`
  + `features/{7 apps}`; basenames kept ⇒ labels/tables/FKs untouched;
  `migrate --check` clean against a live-DB dump.
- **B3**: client policy layer — grants/lifecycle/sensitive-visibility moved
  verbatim to `clients/jober/policies.py`, neutral deny-by-default core
  fallbacks, flag-gated URLconf, brand context, `clients/_smoke` proves the
  core boots with zero features/client.
- **B4**: `core/retention` (registry + `run_retention`) and **stdlib TOTP 2FA**
  (RFC 6238 vectors tested; `TWO_FACTOR_REQUIRED_ROLES=[]` for Jober ⇒ zero
  behavior change). Demo seeds moved fully into `clients/jober/demo`.
- **B5**: Stage D sweep green — dep direction clean, `core/` free of client
  conditionals, smoke client passes checks, **242 unit + 16 e2e**, demo stack
  rebuilt on the extracted architecture with the scenario intact.

Stage C (CorvinumEU thin client) now starts from `clients/corvinum_eu/` +
feature flags + the design prototype — configuration and theming, not a rebuild.


## 2026-07-08 — PROGRESS REPORT (owner-requested snapshot)

**Where we are in one sentence:** the Jober product is feature-complete and
demo-ready; all five client questions are answered and implemented; the
platform extraction (Stage B) is activated and ~40% executed, with the
dependency debt already down from 10 edges to 6.

### Jober product (Phases 0–5)
- **Phases 0–4: DONE** — foundation/supply-chain, auth/RBAC/i18n/audit, the
  full workforce core (people, intake, trials, readiness, dashboards, SMS),
  logistics (rooms+pricing Q1, equipment+deduction review Q2, transport),
  compliance alerts, feedback, exit/recycle+inactive reasons Q5, the blacklist
  with HMAC matching Q3 (execution gated on the pending LIA/written text), and
  finance with the confirmed positive convention Q4 (line items, lock/reopen,
  rollups).
- **Quality layer:** full UI redesign ("calm industrial"), nav active-state
  fix, i18n gap audit (no user-facing gaps), internal security review (no
  high/medium findings), 16-test browser e2e suite, demo scenario seed +
  presenter runbook (SMS live; Telegram re-ask scripted).
- **Phase 5 (pilot): NOT STARTED, by design** — gated on the customer demo →
  acceptance → real-data/legal gate. External items outstanding: blacklist
  LIA + written contract text, one filled finance month (label reconciliation),
  Dokku staging names, Twilio account upgrade, native translation review.

### Platform (core + thin clients, ADR 0021)
- **ADR 0021 ACTIVATED 2026-07-07** (owner waiver of the demo-acceptance
  trigger recorded). Safety: tag `pre-stage-b` pushed; the running demo
  container stays on its pre-extraction image until B5.
- Slice progress:
  - **B-1 governance** — merged (PR #36).
  - **B0 flags + tripwire** — merged (PR #37): FEATURE_FLAGS, CLIENT_POLICIES,
    dependency-direction check with the debt enumerated (10 edges).
  - **B1a hooks** — merged (PR #38): activation/exit registries; projects no
    longer imports blacklist/logistics (debt 10 → 8).
  - **B1b surface registry** — merged (PR #39): person card composed by
    feature registration (panels/banners/form-extensions/exit-relevance);
    people no longer imports blacklist/messaging (debt 8 → 6).
  - **B1c (in progress):** reports tiles/panels via registry, finance export
    moved home, seed untangling, `clients/jober/demo` app — target debt 0.
  - **B2–B5 pending:** repo reshape (git mv, labels preserved), client policy
    layer + smoke client, retention + stdlib TOTP 2FA, final validation.
- Throughout: **test assertions unchanged** (Stage D bar); suite currently
  231 unit + 16 e2e, green at every merged slice.

### CorvinumEU (Stage C inputs, ready and waiting)
- Design doc v0.6 + Addendum A1 (fuel money, pending confirmation) + A2.
- Clickable 12-page design prototype (left slide-out sidebar, corvinum.eu
  design language, dark/light) on the `peopleops-prototype` branch of the
  corvinumeu repo (unpushed).

### Risks / notes
- Stage B is mid-flight: main is stable and green at every slice, but the demo
  should run from the running container or the `pre-stage-b` tag until B5
  re-validates.
- 39 PRs merged to date; the ~2–3 week Stage B estimate still holds (the
  hardest 40% — decoupling — is nearly done).


## 2026-06-29 — Phase 3 (6/n): inventory valuation

The unblocked part of inventory (round-4 confirmed valuation method: latest manual price, no weighted-average). Deduction review for missing items stays deferred (open decision).

- `EquipmentItem.unit_price` (manual latest price). `issued_equipment_value(person=None)` sums active issues × price (DB aggregate), company-wide or per person.
- Surfaced on the person card equipment panel (per-person value) and the Reports page (company "Equipment value" card). Admin shows/edits price; `seed_people` sets demo prices. i18n SK/HU/UK.

Verification: ruff clean; **166 unit tests pass** (3 new: qty×price sum company/per-person, returns excluded, zero when none).

## 2026-06-29 — Phase 3 (5/n): operational reports

- `core.views.reports`: read-only cross-module summary (plan §3) — active projects, total people, pending trials, compliance-alert count, accommodation occupancy, people-by-status, and a finance block gated by `finance.view_summary` (managers/observers). Reuses existing services; no new models.
- Reports nav tab + `/reports/`. i18n SK/HU/UK.

Verification: ruff clean; **163 unit tests pass** (4 new: login required, counts render, finance section hidden from recruiter / shown to observer).

## 2026-06-29 — Phase 3 (4/n): QR feedback + manager inbox

Worker-facing feedback (plan §10.1 `/feedback/<token>`, §11.11).

- `apps/feedback`: `FeedbackLink` (tokenized public entry point the QR encodes; optional project) and `FeedbackSubmission` (message + optional rating; **no account/PII**).
- Public **no-login** form at `/feedback/<token>/` (standalone template, not the app shell) → records a submission, shows a thank-you. Inactive/unknown token → 404.
- **Manager-only inbox** (`feedback.view`) listing submissions + active links with their public URLs + a create-link form. Gated nav tab.
- **Retention**: `purge_feedback` management command deletes submissions older than `FEEDBACK_RETENTION_DAYS` (≈1 month). i18n SK/HU/UK.

Verification: ruff clean; **159 unit tests pass** (5 new: public submit, message required, inactive/unknown 404, inbox manager-only, retention purge); image builds.

## 2026-06-28 — Phase 3 (3/n): transport trends

- `logistics.views.transport_trends`: last-12-weeks transport headcount per project + company total per week (plan §11.10), rendered as **dependency-free CSS bar charts** (no JS library).
- New Transport nav tab + `/transport/`. i18n SK/HU/UK.

Verification: ruff clean; **151 unit tests pass** (2 new: login required; company total = sum across projects).

## 2026-06-28 — Phase 3 (2/n): exit reconciliation & recycling

- `projects.services.exit_person`: atomic exit reconciliation (plan §11.13) — ends the active project assignment, releases the room, returns all issued equipment, then recycles the person to **Available** (default) or **Inactive**; audited. Orchestrates the existing lifecycle + logistics services. Missing-returnable-item **deductions remain an open decision** and are not modelled.
- Exit panel on the person card (gated `exit.reconcile` — coordinator + manager) with Exit-to-Available / Exit-to-Inactive; shown when there's something to reconcile (Working, active room, or issued equipment).
- i18n SK/HU/UK. No new migrations (reuses existing models).

Verification: ruff clean; **149 unit tests pass** (4 new: full reconcile + recycle, exit-to-inactive, view RBAC deny/allow).

## 2026-06-28 — Phase 3 (1/n): compliance alerts

Fulfils the manager's earlier explicit ask (alerts for missing/expiring papers); plan §3 / §11.9.

- `apps/compliance`: `Certificate` (metadata only — dates, no file storage, matching the demo decision).
- `services.compliance_alerts(viewer)`: surfaces **missing / expiring / expired** papers across workers — medical derived from the latest readiness **entry-medical date** + `MEDICAL_VALIDITY_MONTHS`; certificates by `expiry_date`; window = `COMPLIANCE_ALERT_DAYS` (the ~11/23-month pattern = ~1 month before a 12/24-month validity). Coordinator-scoped (own active-project people); managers/observers see all. `add_months` helper (no external dep).
- Compliance page on a new nav tab; certificate admin; settings `MEDICAL_VALIDITY_MONTHS` / `COMPLIANCE_ALERT_DAYS` (env-overridable). i18n SK/HU/UK.

Verification: ruff clean; **145 unit tests pass** (8 new: add_months clamping, missing medical, expired/expiring/far-future certs, valid recent medical, login required, coordinator scoping).

## 2026-06-28 — Phase 2 (6/6): approved SMS messaging (Phase 2 complete)

Twilio SMS over the **standard library** — no SDK, no new dependency (ADR 0019).

- `apps/messaging`: `MessageTemplate` (manager-managed), `OutboundMessage`, `InboundMessage`.
- `services.py`: `_twilio_send` (urllib Basic-auth POST to Twilio `Messages.json`; creds from env, `SmsNotConfigured` when unset → recorded `failed`, never faked); `send_sms` (records + audits); `verify_twilio_signature` (base64 HMAC-SHA1, `compare_digest`).
- Inbound webhook (`/webhooks/twilio/inbound/`): `csrf_exempt`, unauthenticated, **signature-verified, fails closed (403)**; stores inbound messages.
- Send gated by `sms.send`; **coordinator-scoped** (a coordinator may only message people on their own projects). Templates manager-managed. No Telegram.
- UI: a Send-SMS panel on the person card (template select or free text + recent messages). Settings: `TWILIO_ACCOUNT_SID/AUTH_TOKEN/FROM_NUMBER` from env. i18n SK/HU/UK.

Live sending requires the operator to set the Twilio env vars and expose the webhook publicly; tests mock the network call.

Verification: ruff clean; **137 unit tests pass** (9 new: sent on provider OK, fail-closed when unconfigured, signature accept/reject, webhook 403/200, RBAC, coordinator scope allow/deny); production image builds with all apps.

**Phase 2 build items complete** (person card/history/search, dashboards, project/coordinator routing, complete trials/full readiness, exports, approved SMS).

## 2026-06-28 — Phase 2 (5/n): full readiness (N/A reasons + entry-medical date)

- `ReadinessRecord`: added `accommodation_na_reason` / `transport_na_reason`.
- `update_readiness`: accommodation/transport now **require an explicit reason when marked N/A** (plan §11.6); accepts and stores the **entry-medical date**.
- Readiness panel: per-pillar N/A reason inputs + an entry-medical date field.
- i18n SK/HU/UK.

Verification: ruff clean; **128 unit tests pass** (N/A-requires-reason, entry-medical-date saved; existing readiness tests updated to supply reasons).

## 2026-06-28 — Phase 2 (4/n): project/coordinator routing

- The Trials queue and the dashboard's pending-trials list are now **scoped to a coordinator's own projects** (via `project.responsible_coordinators`); managers, observers, and recruiters still see all (broad read).

Verification: ruff clean; **126 unit tests pass** (2 new: coordinator sees only their projects' trials; manager sees all).

## 2026-06-28 — Phase 2 (3/n): permission-controlled CSV exports

- `apps/core/exports.py`: `people_csv`, `projects_csv` (gated `export.approved` — manager + observer) and `finance_csv` (gated `finance.view_summary`). Clean non-prefixed download URLs.
- Exports deliberately **exclude bulk sensitive fields** (DOB, disability, identifiers); those stay on the per-person card behind `can_view_sensitive`.
- Gated **Export** buttons on the People, Projects, and Finance pages. i18n SK/HU/UK.

Verification: ruff clean; **124 unit tests pass** (6 new: CSV content + content-type for manager/observer, 403 for recruiter, anonymous redirect).

## 2026-06-28 — Phase 2 (2/n): real dashboard

Replaced the Phase 0 mock dashboard (hardcoded 8/14/6 + mock field panel) with live aggregates.

- `apps/core/views.dashboard`: real counts — active projects, available, working, trials awaiting outcome — plus a list of pending trials.
- `dashboard.html`: clickable metric cards (link to the filtered People list / Projects / Trials) and a real pending-trials panel.
- Retired the mock `field_queue` view/route/partial and `PROJECT_CARDS`; updated the e2e smoke (it asserted the old mock) to check the real metric cards.
- i18n: "Awaiting outcome" (SK/HU/UK).

Verification: ruff clean; **118 unit tests pass** (1 new: dashboard shows real metrics + pending trial); **Playwright smoke 5 pass**; dashboard screenshot reviewed (live counts + pending trial).

## 2026-06-28 — Phase 2 (1/n): person card history + search filter

First Phase 2 slice (full person card / history / search).

- `apps/people/services.py` `person_history(person)`: a newest-first unified timeline assembled from trials (scheduled + outcome), project assignments, room assignments, equipment issues, readiness submissions, intake completion, and the append-only audit log's lifecycle changes.
- Person card: a **History** panel rendering that timeline.
- People list: a **lifecycle-status filter** alongside the existing name search.
- i18n SK/HU/UK for the new strings.

Verification: ruff clean; **117 unit tests pass** (2 new: history is newest-first and covers the key event types; the status filter narrows the list). Browser-reviewed the card history + filtered list.

## 2026-06-28 (later) — Hard-gated intake engine (Phase 1 complete)

Replaces intake-lite with the real questionnaire engine (§11.3 / §12.1). This was the last open Phase 1 build item.

- `apps/intake`: versioned questionnaire (`IntakeQuestionnaireVersion → IntakePanel → IntakeQuestion`) and `RecruitmentIntake → IntakeAnswer`.
- Engine (`services.py`): `start_intake`, `save_panel`, `complete_intake`.
  - **Sequential, server-driven panels** — `save_panel` always acts on `intake.current_panel_order`, so panels can't be bypassed by URL/forged POST.
  - **Required** answers enforced server-side; **typed-negative** questions reject a blank field (no checkbox bypass) and recognise accepted "no/none" words (normalized); **conditional** questions are required only when their parent answer is positive.
  - Completion maps stable_keys → Person fields and creates an `AVAILABLE` Person owned by the recruiter; audited.
- Seed `seed_questionnaire` (published "Recruiter intake" v1: Identity / Contact / Compliance with a typed-negative disability question + conditional disability type). `dev_app.sh up` seeds it.
- UI: `intake_start` → sequential `intake_panel` wizard (step X/Y, prefilled, per-field errors); "Add person" now starts the real intake. Admin for questionnaire authoring. i18n SK/HU/UK.

Verification: ruff clean; **93 unit tests pass** (6 new: required blocks advance, typed-negative can't be blank, accepted-negative skips the conditional + completes, positive requires the conditional, full completion creates an Available person, completed intake rejects further panels). Browser walkthrough of the wizard reviewed.

Phase 1 status: **all build items complete.** (Questionnaire *content* + per-language typed-negative phrases remain configurable/Tier-2; the manager-approval→coordinator-activation change is ADR 0018.)

## 2026-06-28 (later) — Minimal financial month (Phase 1)

Completes the deferred peripheral modules. Sign convention flagged as an
assumption (Phase 4 blocker).

- `apps/finance`: `FinancialMonth` (project/year/month, revenue, cost, lock; unique per project-month). `net = revenue - cost` documented as an **assumption** to confirm from one filled month (open-decisions). `company_totals` sums **dynamically** over all projects/months — never hardcoded — to avoid the manager's spreadsheet bugs.
- Services `record_financial_month` (update_or_create; rejects edits to a locked month) and `company_totals`.
- UI: a Finance summary page (totals + months + record form), gated `finance.view_summary` (manager + observer); the nav tab and record form are role-gated; `finance.manage` for writes. Admin; `seed_people` seeds two months. i18n SK/HU/UK.

Verification: ruff clean; **87 unit tests pass** (5 new: net, dynamic totals, idempotent month, locked-month rejection, RBAC).

## 2026-06-28 (later) — Weekly transport reporting (Phase 1)

- `apps/logistics`: `TransportWeek` (project + week_start + headcount; unique per project/week).
- Service `record_transport_week` (update_or_create, audited).
- UI: a Weekly transport panel on the project detail — recent weeks + a record form, gated by `transport.record`. Admin. i18n SK/HU/UK.

Verification: ruff clean; **82 unit tests pass** (3 new: create, idempotent per week, RBAC).

## 2026-06-28 (later) — Minimal inventory / equipment (Phase 1)

- `apps/logistics`: `EquipmentItem` catalog (name/size; no valuation — Phase 3) and `EquipmentIssue` (quantity, issued/returned).
- Services `issue_equipment` / `return_equipment` (audited).
- UI: an Equipment panel on the person hub — issue (item + quantity) and return, gated by `equipment.issue_return` (coordinator + manager).
- Admin; `seed_people` seeds a small catalog. i18n SK/HU/UK.

Verification: ruff clean; **79 unit tests pass** (3 new: issue, return, RBAC).

## 2026-06-28 (later) — Minimal accommodation (Phase 1)

First of the deferred peripheral modules. Minimal per Phase 1 (no rates/valuation; those are Phase 3, open-decisions).

- `apps/logistics`: `Accommodation`, `Room` (capacity + occupancy/is_full), `RoomAssignment` with a DB one-active-room-per-person constraint.
- Services `assign_room` (capacity-enforced, closes prior active room, audited) / `release_room`.
- UI: Accommodation list/detail (occupancy) on a new nav tab; an assign/release-room panel on the person hub, gated by `room.assign` (coordinator + manager).
- Admin for all three; `seed_people` now also creates an accommodation with rooms and houses the Working seed person.
- i18n: logistics strings translated SK/HU/UK and compiled.

Verification: ruff clean; **76 unit tests pass** (5 new: occupancy, capacity enforcement, one-active-room reassignment, release, RBAC).

## 2026-06-28 (later) — Core Phase 1 workflow (demo cut)

Made the intake → trial → readiness → activation vertical clickable end-to-end
for tomorrow's customer demo. Deferred the peripheral minimal modules (room,
inventory, transport, finance).

What changed:
- **Trials** (`apps/projects`): `TrialAssignment` (§11.5, append-preserving) + `schedule_trial` (handoff, requires Available → Trial day) and `record_trial_outcome` (pass keeps Trial day; fail/no-show recycles to Available, §12.3).
- **Readiness + activation**: `ReadinessRecord` (four pillars; medical+gear required, accommodation/transport may be N/A; `is_ready`); `update_readiness` (rejects medical/gear N/A) and `activate_from_readiness` — the **system-enforced** coordinator activation (ADR 0018); CARGO/manager override still possible via direct `activate_on_project`.
- **Intake-lite**: recruiter `PersonForm` + `person_create` (gated `intake.create_edit`), "Add person" on the People list.
- **UI**: the person detail is now a **state-driven workflow hub** (assign-trial → record-outcome → readiness pillars → activate), a coordinator **Trials** queue wired to the Field nav, and a shell messages region. All actions gated with `require_action` + `{% can %}`.
- i18n: translated all new workflow/readiness/intake strings (SK/HU/UK) and recompiled.
- `scripts/dev_app.sh up` now also runs `seed_people` so the demo stack is populated.

Verification: ruff clean; **71 unit tests pass** (11 new workflow tests incl. the full path to Working); **Playwright drove the entire demo path** (add person → trial → fail/recycle → re-trial → pass → readiness → activate → Working) and screenshots were reviewed — all in Slovak.

Demo path: log in (manager does everything) → People → Add person → Schedule trial → Fail (recycles) → Schedule trial → Pass → Four-pillar readiness → Activate → Working on project.

## 2026-06-28 (later) — Project UI

Read-only Project list + detail, mirroring the People pattern.

What changed:
- `apps/projects/views.py`: `project_list` and `project_detail` (login-gated). Detail shows code/partner/office/responsible coordinators/financial-reporting eligibility plus the active **Workers** on the project, each linked to their person page.
- Templates `pages/project_list.html` + `pages/project_detail.html`; wired the **Projects** nav tab to the route and added `/projects/`, `/projects/<id>/`. Small `.plain-list` CSS.
- i18n: translated the new project UI strings (SK/HU/UK) and recompiled.
- Verified live (manager): list shows the three seeded projects with active status; DHL Bratislava detail lists the assigned worker linked back to People.

Verification: ruff clean; **60 unit tests pass** (3 new project view tests); screenshots reviewed.

## 2026-06-28 (later) — People UI

Surfaced the Person spine in the app (read-only), the lowest-hanging next slice.

What changed:
- `apps/people/views.py`: `people_list` (login-gated broad read, name search) and `person_detail`, which renders sensitive fields (DOB, place of birth, disability) only when `can_view_sensitive` allows (Q4); otherwise a restricted note.
- Templates `pages/people_list.html` + `pages/person_detail.html` reusing the existing panel/field-card CSS; added a **People** nav tab and `/people/`, `/people/<id>/` routes.
- Small CSS: `.people-search`, `.person-row`, `.detail-grid`.
- i18n: translated the new operational UI strings (lifecycle status labels + People page) in SK/HU/UK and recompiled; admin-only model field labels fall back to English for now.
- Verified live (manager): list shows seeded people with translated statuses; detail shows the restricted panel with disability for a permitted viewer.

Verification: ruff clean; **57 unit tests pass** (5 new view tests incl. sensitive masking); screenshots of list + detail reviewed.

Next step:
- Recruiter intake (hard-gated) or trials + the readiness gate (which activates ADR 0018 enforcement).

## 2026-07-05

Stage B platform extraction — planning completed (docs only, build gated).

What changed (no production code touched; ADR 0001 still governs):
- `docs/platform/extraction-matrix.md`: DRAFT → **completed against the real
  repo** (2026-07-05 sweep: 11 apps, 26 models, 26 RBAC actions, 22 page
  templates, 9 commands). Per-artifact rows for every app; explicit all-26
  RBAC-actions table; dependency baseline table. All four open flags **resolved
  with repo evidence** (advances↔finance: no overlap; equipment: shared; auth:
  compatible + 2FA to add; core→feature coupling: three call sites + dashboard).
- `docs/platform/extraction-plan.md` (new): staged execution B0–B5 — safety
  net/flags → decouple (hook + registry designs for the four coupling sites) →
  in-place `git mv` reshape with **AppConfig.label pinning so no data migration**
  → `clients/jober/` policy layer → core additions CorvinumEU needs (2FA,
  retention, tasks) → validation. Risks + per-slice done-criteria; ~2–3 weeks
  (§12.5 estimate holds given the localized coupling).
- `docs/adr/0021-stage-b-extraction.md` (new): **Proposed** — activation trigger
  is Jober demo acceptance + owner go-ahead; on activation it supersedes ADR 0001
  and the plan's slices may land. Not in force while Proposed.
- Source register: both new docs registered as non-authoritative until activation.

Verification: docs-only diff; completeness check script confirms every model,
command, and action appears in the matrix; matrix ↔ plan ↔ ADR cross-references
consistent.

## 2026-07-04 (later)

Customer demo tooling — full-scenario seed + presenter runbook.

What changed:
- `apps/core/management/commands/seed_demo_scenario.py` — idempotent, fictional
  orchestration (via the real services) that fills every module screen for the
  demo: finance line items on DHLBA 2026-05 (+ recompute), two equipment items
  issued to Olha with one **flagged unreturned** (Reviews queue), Bohdan's
  **inactive reason**, an expiring **certificate**, a **blacklisted** person
  ("Ivan Zablokovaný", hashed ID `SK-DEMO-BL-001`) for the live re-entry moment,
  a **proposed** blacklist case on Diana to decide live, and a phone for Olha.
  Wired into `scripts/dev_app.sh up` after the other seeds.
- `docs/deployment/demo-runbook.md` — the ~60-min presenter script (Slovak +
  a Hungarian switch): prep/go-no-go, logins, cast, 11 acts mapped to the pains
  and the five answered questions, caveats, and the closing ask. Linked from
  `docs/deployment/local-demo.md`.

Verification: **226 unit tests pass** (was 224) — `tests/test_demo_scenario.py`
asserts every module screen is populated (finance net = revenue − cost = 6900,
pending equipment review, "Sick" inactive bucket, blacklisted person + active
fingerprint, `check_match("SK-DEMO-BL-001")` hits, a compliance alert, Olha's
phone) and that re-running the seed is idempotent. ruff clean.

## 2026-07-04

Blacklist & HMAC matching module (Q3 unblocked) — `apps/blacklist/`.

Jober confirmed the legal basis: **legitimate interest** (fraud prevention /
security vetting / hiring decisions). The last hard-blocked module is now built,
on the authoritative Jober spec (`Product_Design.md` §11.14 / §12.13). The written
contract text + a documented LIA are still pending, so **real-data execution stays
gated** (`BLACKLIST_MATCHING_ENABLED`); fictional data only until sign-off.

What changed:
- New `apps/blacklist/`: `BlacklistCategory` (configurable, seeded neutral
  placeholders), `BlacklistCase` (proposed/approved/rejected/removed), and
  `MatchFingerprint` (keyed **HMAC-SHA256** of a transiently-entered ID —
  **raw identifier never stored**; `key_version` allows key rotation). Migrations
  0001 + 0002 (seed).
- Services: `compute_fingerprint` (normalized, keyed), `check_match` (company-wide,
  active/non-expired, honours the enable gate), `propose_case` (no lifecycle
  change), `decide_case` (approve → BLACKLISTED + activate fingerprint; reject),
  `remove_case` (→ Available + revoke), `has_open_case`, `purge_expired` + a
  `purge_blacklist` command.
- Warning flow (§12.13): optional non-persisted ID on the intake form
  (`PersonForm`) → on a match, create the person, auto-propose a case, and warn —
  **no block, no silent merge**. `activate_on_project` now **hard-gates** on an
  unresolved case.
- RBAC: new **`blacklist.propose`** (coordinator + manager); **widened
  `blacklist.view_reason`** to coordinator + manager (client's visibility rule:
  flag = recruiter + coordinator + manager; reason = coordinator + manager);
  `blacklist.decide` stays manager-only. Matrix updated.
- UI: person-detail blacklist panel (flag to all; reason gated; propose/decide/
  remove), a warning banner, a manager review queue, a manager-only **Blacklist**
  nav tab. Admin + i18n SK/HU/UK. Settings: `BLACKLIST_HMAC_KEYS`,
  `BLACKLIST_MATCHING_ENABLED`, `BLACKLIST_RETENTION_DAYS`.
- Legal: `docs/security/blacklist-legal-basis.md` (legitimate-interest grounds +
  LIA placeholder + data-handling); Q3 in the open-questions doc marked BUILT.

Verification: ruff clean; **224 unit tests pass** (was 202) + **16 e2e** (blacklist
queue renders; manager sees the tab; coordinator 403). Covered: keyed/deterministic
hash, **raw id never persisted**, active/company-wide matching, propose→approve→
BLACKLISTED + fingerprint active, remove→Available + revoke, reject no-op,
open-case blocks activation, intake match warns without blocking, RBAC, retention
purge. Migrations build under pytest.

Next step:
- On the written text + LIA: confirm retention period + reason-category list, then
  lift the real-data gate. Q3 is the last blocker; everything else is merged.

## 2026-06-30

Finance sign convention CONFIRMED (Q4) — positive convention + hardening.

Jober confirmed (2026-06-29): costs and revenues are entered as **positive**
numbers; the system computes `net = revenue − cost`. This is exactly how the
finance module was already built (PRs #16–#17: amounts stored positive, sign
from the category kind), so the confirmation **validates** the existing build
rather than unblocking new work. This slice enforces the convention so it can't
be violated, and flips the docs from "assumption" to "confirmed".

What changed:
- `apps/finance/services.py`: `positive_amount()` guard — `set_line_item` and
  `record_financial_month` now **reject negative** amounts (raise FinanceError,
  surfaced by the existing view try/except).
- `apps/logistics/services.py`: `_non_negative()` guard on `set_room_rate` /
  `set_assignment_rate` (raise ValueError; the rate views now catch it and show
  a message instead of 500ing).
- Model validators (`MinValueValidator(0)`) on every money field for admin/form
  defence: finance line-item amount, monthly revenue/cost; room monthly_rate +
  rate_override, equipment unit_price, unreturned-item charge_amount. Migrations
  `finance/0003` + `logistics/0007` (validator-only; no data change).
- Docstrings + `docs/product/phase3-4-open-questions.md` Q4 +
  `docs/product/open-decisions.md`: assumption → **confirmed 2026-06-29**.

Point-by-point vs the request: (1) all cost fields accept/process positives —
yes, and negatives are now rejected; (2) ledger entries align — the Jober
finance model is project-month P&L (FinancialMonth + line items), not a
per-worker cash ledger (that's the CorvinumEU design); it computes
`net = revenue − cost` on positive inputs; (3) equipment charge =
`unit_price × quantity`, positive arithmetic, prices/charges validated
non-negative; (4) no ambiguous calc found — net is unambiguous under positives.

Verification: ruff clean; **207 unit tests pass** (was 202) — positive net =
revenue − cost, and negatives rejected for line items, monthly cost, room rate,
and assignment override. Migrations build under pytest.

Next step:
- Still useful (not blocking): a real filled month to reconcile the seeded
  category labels. Otherwise finance is done; remaining blocker is Q3 blacklist.

## 2026-06-29 (later 5)

Reports polish — inactive-by-reason breakdown.

What changed:
- `apps/people/services.py`: `inactive_by_reason(include_archived=False)` —
  counts Inactive people grouped by their structured reason (Q5), most-common
  first, with a "No reason" bucket for nulls; non-archived by default to match
  the reports page's workforce counts.
- Reports view/template gained an "Inactive by reason" panel next to "People by
  status". i18n SK/HU/UK.

Verification: ruff clean; **202 unit tests pass** (was 198) — grouping/ordering,
null bucket, archived excluded by default (and included on request), empty case.
(Read-only reporting; no model change, no migration.)

## 2026-06-29 (later 4)

Inactive-reasons catalog + exit recycling (Q5 + lifecycle polish).

What changed:
- `apps/people/models.py`: `InactiveReason` catalog (label, is_active, order —
  configurable in admin) and `Person.inactive_reason` FK + `Person.inactive_since`.
  Migration `0002`; data migration `0003` seeds the Q5 placeholders (Sick,
  Quit / left, Suspended, Military service, Other).
- `apps/projects/services.py`: `exit_person` now takes `inactive_reason` and,
  when exiting to Inactive, records the structured reason + since-date on the
  person (replacing the free-text-only exit).
- `apps/people/services.py`: `recycle_to_available` — returns an **Inactive**
  person to the **Available** pool (INACTIVE→AVAILABLE is already an allowed
  transition), clears the reason/since, audited `person.recycled`. Guarded to
  Inactive-only.
- views/urls: exit form captures the reason; `recycle_person` (POST) wires the
  previously-defined-but-**unused** `person.recycle_available` action
  (recruiter + coordinator + manager). Templates: reason `<select>` on the
  Exit-to-Inactive form, plus an Inactive panel showing the reason/since and a
  Recycle-to-Available button. Admin for `InactiveReason` + reason column on
  Person. i18n SK/HU/UK.

Verification: ruff clean; **198 unit tests pass** (was 192) — the `0003`
migration seeds the placeholders, exit-to-inactive records reason + since,
recycle clears them and returns Available, recycle is guarded to Inactive-only,
RBAC (recruiter/coordinator/manager yes, observer no), and the recycle view is
403 for observer / 302 + Available for coordinator.

Next step:
- Remaining work is blocked on Jober (blacklist legal Q3; the charge/deduct
  behaviours behind Q1/Q2/Q4). This clears the last safe-default-buildable slice.

## 2026-06-29 (later 3)

Phase 3 unreturned-equipment deduction review queue (Q2 safe default).

What changed:
- `apps/logistics/models.py`: `DeductionReviewStatus` (NONE/PENDING/APPROVED/
  WAIVED) + `review_status`, `charge_amount`, `reviewed_by/at`, `review_note` on
  `EquipmentIssue`. Migration `0006`. The charge review is **separate from the
  physical status** — a flagged item is still ISSUED (not returned) but its
  *charge* is under manager review. **No payroll deduction is ever executed**;
  APPROVED only records the manager's decision to recover (Q2 safe default).
- `apps/logistics/services.py`: `flag_unreturned` (snapshots
  `quantity × item.unit_price`, guarded to issued + un-reviewed), `review_deduction`
  (approve/waive, guarded to pending, audited), `pending_deduction_reviews`
  (queue + dynamic outstanding total). `exit_person` now **skips already-flagged
  items** when auto-returning (leaves them for the queue), replacing the old
  "deductions not modelled yet" note.
- RBAC: new **manager-only** `equipment.review_deduction` (queue + approve/waive);
  flagging uses the existing coordinator+manager `equipment.issue_return`.
  permission-matrix.md updated.
- views/urls: `flag_unreturned`, `equipment_reviews` (queue), `review_deduction`.
  Templates: per-item "Flag unreturned" + status badges on the person card; a
  manager review-queue page (approve/waive + note, outstanding total, "no
  automatic deduction" note); a manager-only **Reviews** nav tab. Admin + i18n
  SK/HU/UK.

Verification: ruff clean; **192 unit tests pass** (was 184) — flag snapshots the
charge at unit price, can't flag returned/double-flag, approve/waive records the
reviewer + note, review requires pending + a valid decision, the queue total is
dynamic, **exit leaves flagged items for review** while auto-returning the rest,
manager-only RBAC, and the queue view is 403 for coordinator / 200 for manager.
Migration `0006` builds under pytest.

Next step:
- Inactive-reasons catalog + exit recycling (small lifecycle slice), or wait on
  the blocked items (blacklist legal; the finance/accommodation/equipment answers).

## 2026-06-29 (later 2)

Phase 3 accommodation pricing + occupancy-cost reporting (Q1 safe default).

What changed:
- `apps/logistics/models.py`: `Room.monthly_rate` (per-room monthly EUR) and
  `RoomAssignment.rate_override` (optional per-assignment override) + an
  `effective_rate` property (override if set, else the room rate). Migration
  `0005`. This is the Q1 **safe default** — a per-room rate **recorded for
  reporting only, no payroll deduction** — and the room-rate-plus-override shape
  stays robust whether Jober's answer is per-room, per-bed, or per-person, so
  the slice is **not blocked** on the answer.
- `apps/logistics/services.py`: `set_room_rate`, `set_assignment_rate` (blank
  clears the override), and `accommodation_cost_report()` — per-accommodation
  occupancy plus two dynamic figures: `room_cost` (Σ room rates, standing) and
  `assigned_cost` (Σ effective rate over **active** assignments) + a company
  total. Reporting only; no deduction is created.
- `apps/logistics/views.py` + `config/urls.py`: `accommodation_costs` report,
  `set_room_rate_view`, `set_assignment_rate_view` — all gated **manager-only**
  (`accommodation.manage`, previously defined but unused). Coordinators still
  assign/release rooms; only managers see/set cost data.
- Templates: accommodation detail shows + edits room rates (manager); a cost
  report page (occupancy + room/assigned cost, with a "reporting only" note);
  person detail shows the effective rate and a manager override form; list links
  to the report. Admin + `seed_people` rates (€180/room). i18n SK/HU/UK.

Verification: ruff clean; **184 unit tests pass** (was 177) — rate set,
effective-rate override-then-room fallback, cost report room/assigned totals,
released assignments excluded from occupancy/assigned cost (standing room cost
remains), manager-only RBAC, and the cost view returns 403 to recruiter +
coordinator, 200 to manager. Migration `0005` builds under pytest.

Next step:
- Equipment unreturned → manager review queue (Q2 safe default), or the
  inactive-reasons catalog + exit recycling slice.

## 2026-06-29 (later)

Phase 4 finance — month lock/reopen and yearly/per-project rollups.

What changed:
- `apps/finance/services.py`: `lock_month` (close a month, audited `finance.locked`) and `reopen_month` (**reason mandatory**, recorded in the audit `reason` field as `finance.reopened` — Finance_Specs §5). Added read-only aggregations `project_totals(year=None)` and `yearly_totals()`; `company_totals` now takes an optional `year`. All dynamic — every project/month included.
- `apps/finance/views.py` + `config/urls.py`: `finance_month_lock` / `finance_month_reopen` (POST, FINANCE_MANAGE) and a `finance_year` page (per-project results + group breakdown + month list for one year). The month-detail form is now read-only when the month is locked (`editable = can_manage and not is_locked`), with manager-only lock / reopen-with-reason controls. The summary page gained per-project results and a yearly list linking into `finance_year`.
- No model changes (reuses `FinancialMonth.is_locked`), so no new migration.

Verification: ruff clean; **177 unit tests pass** (was 173) — lock blocks edits + reopen needs a reason, reopen reason is audited, the save view no-ops on a locked month, and project/yearly/company aggregations (incl. year filter + empty-year zero) are correct. Catalogs recompiled SK/HU/UK (fixed two fuzzy mis-matches: "Lock month"/"Reopen month").

Next step:
- Per-project line-item *columns* per `Finance_Specs.md`, or move to the accommodation pricing slice (Q1 safe-default).

## 2026-06-29

Phase 4 finance — configurable line-item catalog + per-month entry, recalc and group breakdowns.

What changed:
- `apps/finance/models.py`: `FinanceCategory` (configurable catalog: label, `kind` cost/revenue, `group`, active, order) and `FinanceLineItem` (one positive amount per category per `FinancialMonth`, unique together). Amounts are stored **positive**; the sign comes from `kind`, so `net = revenues − costs` holds regardless of which sign convention the source spreadsheet used (the open Phase-4 confirmation does not block this design).
- `apps/finance/services.py`: `set_line_item` (locked-month guarded, audited), `recompute_month` (rolls line items into `revenue`/`cost` by `kind` — summed **dynamically over the full set**, so it cannot reproduce the spreadsheet's off-by-one cost bug), and `group_breakdown` (per-group revenue−cost across one/all months for the manager's transport/accommodation/overhead view).
- `apps/finance/views.py` + `config/urls.py`: `finance_month_detail` (line-item entry form, gated FINANCE_VIEW_SUMMARY) and `finance_month_save` (FINANCE_MANAGE, POST → set items → recalc). `finance_summary` now shows the company group breakdown and links each month to its detail page.
- `seed_finance` management command seeds the 25-category catalog from `Finance_Specs.md §2` (idempotent); wired into `scripts/dev_app.sh up`. Admin registered for category + line item.
- i18n: new finance strings + group labels translated SK/HU/UK; fixed a reused-but-wrong "Overhead" (was "Prehľad"/overview → "Réžia") and "No line items yet." string.

Assumption recorded (still to confirm with Jober, one filled month): `net = revenue − cost`. The positive-amount + sign-by-kind model makes this robust either way.

Verification: ruff clean; **173 unit tests pass** (was 166) — recompute sums by kind, dynamic totals cover every cost row, locked-month blocks edits, group breakdown nets revenue−cost, save view persists + recomputes, detail view gated from recruiters. Migration `0002` builds cleanly under pytest; catalogs compiled. (Run `scripts/dev_app.sh rebuild` to pick up the new code in the local demo.)

Next step:
- Month lock/reopen UI (reason + audit) and the yearly rollup view; then per-project line-item columns per `Finance_Specs.md`.

## 2026-06-28

Phase 1 business spine — Person + lifecycle + project administration.

What changed:
- Added `apps/people`: `Person` with the canonical 5-state lifecycle (`AVAILABLE / TRIAL_DAY / WORKING / INACTIVE / BLACKLISTED`, plan §9.1), validated transition helper `set_status` (audited), search-normalized name, archive, **disability as a flag only** (no documents, Q1), and `owning_recruiter`.
- Added `apps/projects`: `Project` (project↔coordinator many-to-many) and `ProjectAssignment` with a DB-level **one-active-assignment-per-person** constraint (§11.4); placement service `activate_on_project` / `end_assignment` (atomic, audited, history-preserving).
- **Sensitive-field visibility** (`apps/people/permissions.can_view_sensitive`, Q4): DOB/place-of-birth/disability visible to managers, observers, owning recruiter, and responsible coordinator(s); hidden from unconnected recruiters/coordinators.
- RBAC: added `project.assign` (coordinator + manager, Q2); updated `permission-matrix.md`.
- Admin for Person/Project/ProjectAssignment; fictional `seed_people` (3 projects, 5 people, one Working via assignment; no real PII).
- ADR 0018: coordinator-activated, **system-enforced** readiness gate replaces the §11.6/§12.4 manager-approval step (CARGO override retained). Readiness-gate enforcement + alert layer attach with `ReadinessRecord` (next slice).

Decisions baked in: phase1-open-questions Q1–Q4 + the activation-gate answer.

Verification: ruff clean; **52 unit tests pass** (lifecycle transitions, one-active-assignment + history, sensitive visibility, placement RBAC); migrate + seed_demo + seed_people run clean on pinned PostgreSQL.

Next step:
- Recruiter intake (hard-gated, typed-negative) and the Person card/list UI; then trials and the readiness gate + manager alerts.

## 2026-06-21

Phase 1 — foundation slice: authentication, four-role RBAC, localization, append-only audit.

What changed:
- Added `apps/accounts` with a custom `User` (email login, custom manager, removed `username`) carrying a single fixed `role` field (`Role`: recruiter/coordinator/manager/observer). Set `AUTH_USER_MODEL = "accounts.User"` before any business migration.
- Added action-gated RBAC in `apps/accounts/permissions.py`: an `Action` enum, an `ACTION_ROLES` map derived literally from plan §8.2–8.5 (with the inverse `ROLE_ACTIONS`), `can()`, a `require_action()` view decorator (redirect anonymous, 403 authenticated-but-denied), and a `{% can %}` template tag so hidden buttons are backed by real server checks.
- Kept reads broad by default behind a single `BROAD_INTERNAL_READS` switch (env `JOBER_BROAD_INTERNAL_READS`) so the still-open GDPR recruiter/coordinator read-scope decision is not hardcoded (open-decisions.md).
- Added `apps/audit`: append-only `AuditEvent` (immutable `save()` on update, `delete()` raises) and `record_event()` as the single write path; wired into login/logout. Read-only admin.
- Replaced the static login view with real email/password auth (`apps/accounts/views.py`), gated `dashboard`/`field_queue` with `login_required`, added a logout button and a language switcher to the base template.
- Wrapped app routes in `i18n_patterns` and added the `set_language` route; `healthz/` stays unprefixed.
- Added `seed_demo`/`reset_demo` management commands creating one fictional user per role on the `demo.jober.test` domain (no real PII; asserted).
- Added `docs/permissions/permission-matrix.md` (mirrors `ACTION_ROLES`) and ADR 0015 (custom user model).
- Generated `accounts`/`audit` initial migrations inside the digest-pinned image.
- Made `SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE` env-overridable (secure by default) so the HTTP-only internal smoke network can exercise authenticated flows; `playwright_smoke.sh` now seeds demo users and the smoke suite logs in.

Decisions made:
- Custom user model introduced now while the DB held only contrib migrations — the last cheap moment (ADR 0015).
- No business modules (Person, intake, trials) in this slice; the permission matrix is authored ahead so future views adopt the correct gate from day one.

Deferred:
- Translation catalogs (`.po`/`.mo`) are not generated/compiled in this slice: `msgfmt`/`xgettext` are absent on the host and gettext is not in the hardened image, and all source UI strings are already Slovak (the default locale), so non-default languages fall back to Slovak msgids. The i18n machinery (prefixes, `set_language`, switcher) is fully wired and tested. Generating + compiling catalogs is a follow-up once gettext tooling is approved in the toolchain.

Follow-up (2026-06-21) — static serving fix:
- Manual browser testing surfaced an unstyled shell: the production image (gunicorn) served no static files, so CSS/htmx/Alpine/app.js all returned the HTML 404 page (`text/html`, blocked by nosniff). Phase 0 smoke never requested an asset, so it was hidden.
- Adopted WhiteNoise 6.12.0 (ADR 0016): `whitenoise.middleware.WhiteNoiseMiddleware` after SecurityMiddleware + `CompressedManifestStaticFilesStorage`, enabled in production settings only (local runserver/tests don't need it). Hash-pinned in `runtime.lock` and `test.lock`; pinned `certifi`/`greenlet` back to vetted versions so the lock diff is WhiteNoise-only (no cooldown-window pulls).
- Made `SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE` env-overridable (secure by default) so the HTTP-only smoke network can run authenticated flows.
- Added a Playwright regression (`test_static_css_is_served`) asserting the stylesheet serves `200 text/css`. Verified the live image serves `app.css` fingerprinted as `200 text/css`.

Follow-up (2026-06-21) — production admin path:
- Added `manage.py ensure_superuser`: idempotent, env-driven (`DJANGO_SUPERUSER_EMAIL`/`DJANGO_SUPERUSER_PASSWORD`) Manager/Administrator superuser for non-interactive Dokku deploys; audited; `--skip-if-unset` for optional release steps. Created if absent, flags repaired if demoted, password left untouched on redeploy.
- Wired into the Dokku release steps (`docs/deployment/dokku-staging.md`); marked the admin gate Ready in the production-readiness journal. `seed_demo` stays fictional/staging only.
- Verified all paths (create / idempotent / repair / skip) in the production image.

Follow-up (2026-06-23) — internationalization:
- Switched the codebase base language to **English** while keeping **Slovak as the visible default** (`LANGUAGE_CODE=sk`, ADR 0017). Rewrote all template/Python `gettext` source strings (and CLI/exception/dev messages) from Slovak to English.
- Added English to the switcher (now EN/SK/HU/UK). Authored full **SK/HU/UK** catalogs (`locale/<lang>/LC_MESSAGES/django.po`) and compiled `.mo`; the SK catalog reproduces the previous Slovak text exactly, so the default rendering and existing tests are unchanged. HU/UK + revised SK are AI-authored, pending fluent-speaker review.
- gettext is not in the runtime/test images; `scripts/compile_messages.sh` runs the app image with gettext apt-installed to extract/compile. Runtime image now `COPY`s `locale/`.
- Regenerated the `accounts`/`audit` initial migrations (verbose-name/choice-label changes). Added `tests/test_i18n.py` (renders EN/SK/HU/UK + default redirect). Verified all four languages live on the login page.

Next step:
- Phase 1 business spine: project administration and the Person model + lifecycle-status state machine, then hard-gated intake.

What changed:
- Removed tracked Node/PNPM/JavaScript Playwright artifacts from the production tree: `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `Dockerfile.playwright`, `playwright.config.js`, and the old JS Playwright spec.
- Added an npm-free Django skeleton: `manage.py`, `config/`, `apps/core/`, templates, static source files, and a health endpoint.
- Added a Jober-only server-rendered shell with folder-tab navigation, Slovak UI strings, local asset references, and a mobile coordinator htmx interaction that also works as a normal full-page request.
- Vendored htmx `2.0.4` and Alpine `3.15.12` as local static assets with licenses and SHA-256 checksums.
- Added supply-chain scripts:
  - `scripts/check_no_node_artifacts.py`
  - `scripts/verify_vendor_assets.py`
  - `scripts/build_tailwind.sh`
- Added the Tailwind standalone CLI v4.3.0 provenance manifest and local convenience request.
- Added Phase 0 product docs: source register, open decisions, demo inventory, removed-feature inventory, demo-to-Django map, risk/blocker list, and Dokku staging skeleton.
- Added the required Phase 0 ADR set for scope, architecture, htmx/Alpine, Tailwind, npm exclusion, Python Playwright, RBAC, demo reuse, project assignment, and Pohoda exclusion.

Decisions made:
- The old static demo stays in the repo as a design reference, but the new production skeleton does not import Corvinum, shared-client structure, shifts, sick leave, worker portal, or Pohoda.
- Docker is intentionally not completed in this slice because base-image digests must come from trusted/human-approved sources before execution or commit.
- Python dependencies were not installed on the host. The hash-pinned lock remains a Phase 0 blocker until generated in an approved container/CI workflow.

Next step:
- Resolve base-image digests and the Python dependency lock, then add the Docker/CI path and run the Django shell against PostgreSQL.

Follow-up:
- Verified the local Tailwind standalone CLI at `/home/disane/.local/bin/tailwindcss`.
- Confirmed it reports v4.3.0 and observed SHA-256 `73f0e5459054e5cfaa8ab6f3b940f3fbe0f13cc7fd83bc24e7c655033c203400`.
- Ran `scripts/build_tailwind.sh`; it built `static/dist/css/app.css` successfully.
- Updated the base template to load the compiled CSS output.

Infrastructure follow-up:
- Resolved Python base image digest: `python@sha256:d764629ce0ddd8c71fd371e9901efb324a95789d2315a47db7e4d27e78f1b0e9`.
- Resolved PostgreSQL test image digest: `postgres@sha256:2203e6282d9e7de7c24d7da234e2a744fb325df366a3fd8ed940e8abbee39527`.
- Added `requirements/runtime.in`, `requirements/test.in`, and generated hash-pinned `requirements/runtime.lock` / `requirements/test.lock` inside the digest-pinned Python container.
- Added `Dockerfile`, `Procfile`, and `pytest.ini`.
- Built `jober-platform:phase0` successfully; Docker build installs runtime dependencies from hash-pinned wheels and runs `collectstatic`.
- Verified Django migrations against a temporary digest-pinned PostgreSQL 17 container and checked `/healthz/` from the running image.
- Added Django smoke tests in `tests/test_shell.py`.
- Tried Playwright-Python browser smoke; package install and Chromium download worked, but browser launch failed in the slim Python image because `libglib-2.0.so.0` is missing. Documented the decision in `docs/product/playwright-test-environment-note.md`.
- Resolved the browser-test blocker by pinning the official Playwright Python test image:
  `mcr.microsoft.com/playwright/python:v1.60.0-noble@sha256:8ff591d613b01c884cc488339ed4318b4513eaf0c57a164a878ba49e70e3f384`.
- Confirmed the image has no `node`, `npm`, `pnpm`, or `yarn` on `PATH`.
- Added `scripts/playwright_smoke.sh` and wired it into `scripts/ci_phase0.sh`.
- Added `Dockerfile.playwright-python` to build a test-only runner image that installs `requirements/test.lock` with hash enforcement and runs as a non-root user.
- Playwright browser smoke now runs app, PostgreSQL, and test runner on an internal-only Docker network. The browser reaches the app at `http://jober-phase0-app:8000`.
- Playwright browser smoke passed against a temporary digest-pinned PostgreSQL 17 container and the built production app image.

Local development database follow-up:
- Added `scripts/dev_db.sh` for workstation PostgreSQL without host installation.
- The script uses digest-pinned PostgreSQL 17, an internal Docker network, a named Docker volume, a containerized `psql` helper, and a generated gitignored `.env.dev-db`.
- Verification showed a loopback DB port is not reachable from the host when this Docker daemon attaches the container only to an internal network, so the helper intentionally keeps PostgreSQL off the host network.
- Added `docs/deployment/local-dev-db.md`.
- Updated the open-decision register to keep recruiter/coordinator read scopes configurable until Jober answers the GDPR visibility question.

Tailwind provenance follow-up:
- Confirmed the exact workstation version is `tailwindcss v4.3.0`.
- Confirmed official Tailwind Labs release `https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.3.0` exists.
- Pulled the official release `sha256sums.txt` and found the Linux x64 line:
  `73f0e5459054e5cfaa8ab6f3b940f3fbe0f13cc7fd83bc24e7c655033c203400  ./tailwindcss-linux-x64`.
- Confirmed the existing local binary matches the official checksum.
- Added `vendor/tailwind/tailwindcss-v4.3.0-linux-x64.sha256`.
- Added `scripts/fetch_tailwind.py`, `scripts/check_production_image.sh`, and `scripts/ci_phase0.sh`.
- Updated the Dockerfile so the `tailwind` build stage fetches the pinned official binary, verifies the official checksum before execution, builds CSS, and excludes the binary from the final runtime image.
- Added ADR 0013 documenting why the expected checksum comes from the vendor's `sha256sums.txt`, not from a self-derived local hash.

## 2026-06-13

Built the v1 static HR operations demo inside `demo/`.

What changed:
- Added `demo/index.html`, `demo/styles.css`, and `demo/app.js`.
- Implemented the CorvinumEU default theme and live Jober theme switch with CSS custom properties.
- Implemented the global top bar, role switch, client switch, sidebar, guided manifest rail, and decision capture panel.
- Implemented the full guided sequence: sign in, dashboard, staffing decision, blacklist risk check, work test approval, shift and transport decision, fake SMS, second shift, sick leave, certificate hard-stop, mobile manager view, and Jober module reveal.
- Added Jober-only Accommodation, Equipment, and Pohoda dashboard screens.
- Kept all demo state in plain in-memory JavaScript. No persistence APIs, backend, dependencies, remote scripts, remote styles, or media assets were added.

Design decisions:
- Followed the local `demo/frontend-design/SKILL.md` direction by grounding the interface in workforce logistics: manifests, rosters, risk gates, shifts, buses, and document stops.
- Used the manifest rail as the single aesthetic risk. It works as both guided stepper and operational route strip, so the memorable visual device carries product meaning instead of decoration.
- Used the approved token palettes from the plan for CorvinumEU and Jober.
- Used Option A typography: system stacks that prefer Michroma, Noto Sans, and JetBrains Mono only when already present on the machine.
- Self-critique outcome: removed the narrow-layout promotion of the manifest rail after screenshot review because it hid the active screen on mobile. The mobile layout now places the active screen first.

Deferred:
- No real media assets or font files. Option B self-hosted fonts can be added only if the human delivers the files and licenses.
- No real SMS, authentication, database, or Pohoda connection.

Next step:
- Review the demo in a normal browser window before the meeting and tune copy or screen density if the presenter wants a different walkthrough rhythm.

## 2026-06-13

Responsive retrofit and spec filename fix.

What changed:
- Renamed `demo/demo_prototype_build_specs.md` to the canonical `demo/demo_prototype_build_spec.md` so the file on disk matches `AGENTS.md` / `CLAUDE.md` references.
- Retrofitted the shell for tablet and phone without rebuilding the demo: desktop keeps the three-column layout above 1024px.
- Added a hamburger drawer for tablet/phone navigation and moved mobile Client / Role controls into that drawer.
- Converted the right Live manifest rail into a collapsible top progress strip below 1024px, with all 12 stops reachable.
- Restacked dense tables into labelled cards at phone width.
- Made decision cards stack vertically on phone.
- Made the manager field view read as a phone-native screen at phone width rather than a desktop page containing a heavy phone mockup.
- Added spacing and tap-target CSS tokens so controls have more consistent gaps and phone buttons are easier to hit.
- Added isolated Playwright test tooling at the repo root, outside `demo/`, using the pinned Docker workflow.

Decisions made:
- Used a hamburger drawer instead of bottom tabs because Jober adds too many nav items for a reliable thumb tab bar.
- Used 1024px as the shell breakpoint and 640px as the phone/card breakpoint.
- Kept the manifest as the signature element by adapting it to a mobile progress strip instead of hiding it.
- Used Playwright, not Puppeteer, because repo policy defines a specific Playwright-in-Docker workflow.

Deferred:
- No new media, fonts, framework, runtime dependency, backend, or production scaffold.

Next step:
- Review the responsive demo manually on the actual presentation phone and laptop for meeting-specific pacing and density.

## 2026-06-13

Desktop spacing and tap-target cleanup.

What changed:
- Tightened the shared spacing system in `demo/styles.css` with reusable control, action-row, and stack-gap tokens.
- Increased shared buttons and segmented switch buttons to a 44px minimum hit target.
- Added consistent separation after form grids, status badges, alert/callout blocks, message boxes, and action rows so buttons no longer sit flush against nearby content.
- Increased decision-card padding/gaps and form-field gutters to keep dense screens readable without changing the desktop shell.
- Added a Playwright regression check that verifies visible button height and control spacing across the desktop walkthrough screens.

Decisions made:
- Fixed the issue at the component spacing layer instead of tuning each screen separately, because the cramped controls came from repeated action-row and callout patterns.
- Kept the existing desktop information architecture and responsive breakpoints intact.

Next step:
- Review the updated pages on the presentation laptop to confirm the spacing matches the desired meeting-room density.

## 2026-06-13

Split the demo into internal, CorvinumEU-only, and Jober-only builds.

What changed:
- Moved the existing combined demo unchanged into `demo/internal/`.
- Created `demo/corvinum/` as a CorvinumEU-only static build with its own `index.html`, `styles.css`, and `app.js`.
- Created `demo/jober/` as a Jober-only static build with its own `index.html`, `styles.css`, and `app.js`.
- Removed the client switch from both client-facing builds.
- Removed all Jober-only strings/modules/data from the CorvinumEU build source.
- Removed all CorvinumEU references from the Jober build source.
- Gave Jober a different primary IA: folder-style tabs for Operations, People, Compliance, Logistics, Accounting, and Reports; nested sections live under each folder.
- Replaced Jober's right-side manifest rail with a slim numbered step bar under the folder tabs.
- Made Accommodation, Equipment, and Pohoda normal Jober tabs rather than licensed extras.
- Updated `AGENTS.md`, `demo/demo_prototype_build_spec.md`, `deployment_journal.md`, and the Playwright suite for the three-build structure.

Decisions made:
- Kept CorvinumEU close to the original operational rail/sidebar layout because that is the requested client-facing shape.
- Treated Demand as an Operations sub-section in Jober because the guided story needs the staffing decision before dispatch planning.
- Kept the internal build as the only place where the platform/resale client switch is visible.

Verification:
- `grep -ri jober demo/corvinum/` returned no output.
- `grep -ri corvinum demo/jober/` returned no output.
- The pinned Docker Playwright suite passed with 8 tests across phone, tablet, and desktop.
- Visual screenshots were reviewed for CorvinumEU and Jober at desktop and 375px.

Next step:
- Open the two client builds on the actual meeting laptop/phone and decide whether Jober's Demand sub-section should stay under Operations or move elsewhere.

## 2026-06-13

Added English, Slovak, and Hungarian language switching to all demo builds.

What changed:
- Added an in-memory EN / SK / HU language switch to `demo/internal/`, `demo/corvinum/`, and `demo/jober/`.
- Wired the switch through primary navigation, role labels, guided controls, decision labels, page headings, table headers, and status badges.
- Kept the language choice intentionally non-persistent; it resets on reload like the other demo state.
- Kept the Jober folder-tab grouping data-driven while translating labels at render time.
- Updated `AGENTS.md`, `demo/demo_prototype_build_spec.md`, and the Playwright suite to cover language switching.

Decisions made:
- Mock names, company names, phone numbers, dates, and most audit/demo data remain fixed source data for now; the language layer focuses on the UI and presentation surface.
- CorvinumEU keeps the language switch inside the mobile drawer, alongside Role. Jober shows Role and Language directly in the mobile top area because it has no drawer.

Verification:
- `grep -ri jober demo/corvinum/` returned no output.
- `grep -ri corvinum demo/jober/` returned no output.
- The pinned Docker Playwright suite passed with 9 tests, including language switching in all three builds.

Next step:
- Review Slovak and Hungarian wording with a fluent speaker before client presentation if exact business terminology matters.

## 2026-06-13

Expanded Slovak and Hungarian coverage for the client demos.

What changed:
- Added the missing Slovak/Hungarian strings for the CorvinumEU-only and Jober-only builds across story callouts, audit rows, mobile card labels, table values, document states, and action labels.
- Added a small render-time localization pass in both client builds so existing literal panels and `data-label` values localize without refactoring every template.
- Localized Jober-only Logistics and Accounting surfaces, including Accommodation, Equipment, sizes, and Pohoda metrics.
- Updated the language spec to require client-facing callout prose, audit lines, mobile labels, and module labels to translate.
- Added a Playwright regression that checks deeper translated screens, not only the dashboard heading.

Decisions made:
- Names, company names, phone numbers, and fixed dates remain unchanged mock data.
- The internal combined demo was left as-is for this pass because the request targeted the two client-facing demos.

Verification:
- `grep -ri jober demo/corvinum/` returned no output.
- `grep -ri corvinum demo/jober/` returned no output.
- The pinned Docker Playwright suite passed with 10 tests, including the deeper Slovak/Hungarian coverage check.

Next step:
- Have a Slovak/Hungarian speaker review business terminology before presenting if exact wording matters.

## 2026-06-14

Coordinator role and answered product decisions.

What changed:
- Added the distinct Coordinator role to `demo/internal/`, `demo/corvinum/`, and `demo/jober/`.
- Enforced Coordinator as a real logistics-only permission boundary: CorvinumEU exposes only transport logistics; Jober exposes transport, accommodation, and equipment logistics.
- Filtered Coordinator navigation and guided steps so HR-only screens are not reachable.
- Removed HR/approval data from Coordinator-rendered DOM, including hire status, blacklist status, documents/certificates, work-test/approval content, and audit history.
- Updated the shift flow to be shifts-first: once Hired, a worker is directly shift-eligible, with no contract/signing step.
- Changed transport capacity from an open A/B decision to an answered client decision: vehicle-specific capacity is enforced and full vehicles block future assignments.
- Changed certificate storage from an open A/B decision to metadata only: type, issue date, expiry date, and valid/invalid status; no file upload or retention.
- Kept Demand model as the only open interactive A/B gate.
- Tightened the internal top bar so the added Coordinator role does not cause desktop overflow after switching the internal build to Jober.
- Updated `AGENTS.md`, `demo/demo_prototype_build_spec.md`, and the Playwright suite.

Decisions made:
- Treated Coordinator as not having dashboard access because the current dashboards contain HR/approval metrics. Coordinator defaults to the logistics shift/dispatch view instead.
- Kept Jober Coordinator Logistics access data-driven through the existing folder/tab configuration.
- Applied the pasted clarification because `shared_hr_platform_architecture.md` is referenced by the task/spec but is not present on disk.

Verification:
- `grep -ri jober demo/corvinum/` returned no output.
- `grep -ri corvinum demo/jober/` returned no output.
- The pinned Docker Playwright suite passed with 11 tests, including a Coordinator DOM-absence test across internal, CorvinumEU, and Jober at 375px and desktop.
- Coordinator screenshots were generated for internal, CorvinumEU, and Jober at phone and desktop widths.

Next step:
- Confirm with the clients whether Coordinator should remain dashboard-free or receive a separate logistics-only dashboard later.

## 2026-06-14

Decision drawer regression added.

What changed:
- Added an explicit Playwright regression that opens the decision drawer in internal, CorvinumEU, and Jober and verifies:
  - Demand model is still unanswered.
  - Transport capacity is answered as `A - Enforce capacity`.
  - Certificate storage is answered as `B - Dates only`.

Verification:
- The pinned Docker Playwright suite passed with 12 tests.
