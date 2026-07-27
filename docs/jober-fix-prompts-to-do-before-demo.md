# Jober fix prompts — interview + demo, July 2026

Derived from the recorded demo walkthrough with the Jober manager. Each block below is a
self-contained prompt to paste into Claude Code against the `hr_system` repo. They are ordered
roughly by client urgency, not by size.

Repo conventions every prompt assumes (do not restate them in the prompt if the agent already
has AGENTS.md): business logic in `services.py`, RBAC via `require_action` / `{% can %}`,
per-client feature flags, i18n SK/HU/UK compiled, unit tests extended, `BUILD_JOURNAL.md`
entry appended.

> **Corrected 2026-07-27:** this previously said "Django apps under `apps/`". That layout no
> longer exists — the repo is `core/` + `features/` + `clients/` (ADR 0021/0022). An agent given
> the old text goes looking for directories that are not there.

---

## 0. Scope split — which of these also apply to CorvinumEU

| Fix | Jober | CorvinumEU | Note |
|---|---|---|---|
| J1 Audit person filter | yes | yes | Corvinum audit + person history share the surface |
| J2 Recruiter/coordinator activity stats | yes | yes | Corvinum design doc already lists "candidates by recruiter", "workers by coordinator" |
| J3 Accommodation cost report | yes | **no** | Corvinum excludes accommodation entirely |
| J4 Finance manual entry + chart | yes | **no** | Corvinum excludes economic/P&L dashboards |
| J5 Goods-receipt log | yes | **no** | Corvinum uses per-person custody + ledger, not warehouse stock |
| J6 Remove equipment returns | yes | **no — must stay flag-scoped** | Corvinum keeps return-to-stock and the recovery review |
| J7 Warehouse year/multi-month filter | yes | partial | Same filter widget is reusable on Corvinum reports |
| J8 Persistent status rail | yes | yes | Corvinum's vocabulary is pipeline status, not working/not-working |
| J9 In-app help | yes | yes | Shared shell |
| J10 HU translation sweep | yes | yes | Shared catalogs |
| J11 Clean tenant for client trial | yes | yes | Same bootstrap path, separate DB |

The common core both clients confirmed they want — recruiting/onboarding, transport management,
SMS+e-mail notification, admin → recruiter → worker hierarchy plus read-only observer, blacklist
on returning banned people, modern web UI, central DB, backups — is unaffected by this list. Note
that transport was **removed from Jober** on 2026-07-20 per the previous interview; if the shared
requirement list is now authoritative again, that is a scope reversal to confirm before building.

---

## 1. Confirmed working — no action

The client explicitly approved these during the call. Do not touch them:

- per-office separation of the data model; observer sees all offices, managers are scoped to their own;
- worker avatar upload and its display on person cards;
- blacklist indicator on the person card;
- the reworked Reports surface;
- the QR feedback links, generated link page, and PDF download (he intends to staple the QR to payslips);
- warehouse stock correction / manual adjustment.

---

## 2. Prompts

### J1 — Audit log person filter is broken

```
The audit log's person/worker filter returns no rows. Reproduce: open Audit as a manager,
type a seeded worker's name (e.g. "Diana") into the person filter, submit — the result set is
empty even though that person has audit events.

Strong hypothesis: the per-office scoping introduced in the office-separation slice added a
join or a filter that eliminates rows when the person filter is also applied (e.g. scoping on
the actor's office while the person predicate resolves against a different relation, or an
inner join against an office FK that is null on older audit rows).

Required behaviour:
- The person filter matches on a partial, case-insensitive, diacritic-insensitive substring of
  the person's name. "Diana", "diana", "horvat" and "Horváth" must all match Diana Horváth.
  Reuse the existing name normalization used by the People search and the blacklist fingerprint
  normalizer — do not write a third normalizer.
- Office scoping and the person filter must compose: a manager sees matching events for people
  in their own office(s); an observer sees matching events across all offices. Audit rows with
  no office attribution must not silently disappear — attribute them or include them for
  observers, but decide explicitly and document the choice.
- The actor filter (filter by the e-mail of the user who performed the action) must work the
  same way and compose with both of the above.

Deliver: the fix, a regression test per composition case (manager+person, observer+person,
diacritics, partial match, null-office row), and a note in BUILD_JOURNAL.md naming the root
cause. Check whether the same scoping bug affects any other filtered list added in the same
slice.
```

### J2 — Staff activity statistics, separate from the audit log

The client accepted that the audit log is a traceability tool, not a reporting tool — but he wants
the reporting separately.

```
Add a manager-facing "Staff activity" reporting section, distinct from the audit log. The audit
log stays exactly as it is (traceability: what happened, who did it, when, and the filters that
support asking someone to explain an action).

Scope for the first slice, in priority order:
1. Recruiter productivity: for a selected period, how many people each recruiter registered.
   Recruiters must be comparable side by side in one table — the stated purpose is spotting a
   large gap between two recruiters.
2. Coordinator equipment issuance: for a selected period, how many equipment items each
   coordinator issued, broken down by item.
3. Lower priority, build only if cheap: accommodation transfers — who moved which worker from
   which accommodation to which, in the period.

Period selection: day, week, month, and full year. The client asked for exactly these
granularities. Reuse the filter widget from J7 if that lands first.

Constraints:
- Read-only aggregation over existing data (person creation events, equipment issue records,
  room assignment history). Do not add denormalized counters.
- Manager and observer only; observer read-only, and unscoped across offices. Managers see
  their own office(s).
- Every figure must be computed dynamically over the full set — no hardcoded periods or
  recruiter lists.
- Place it under its own nav entry, or directly beneath Audit in the nav. The client said either
  is fine; pick the one that fits the existing nav grouping and say which you chose.

Deliver: models untouched if possible, a service with unit tests covering each granularity and
the empty-period case, the page, RBAC tests, SK/HU/UK strings, BUILD_JOURNAL entry.
```

### J3 — Accommodation cost report: wrong figures and too many of them

This is the fix with the most precise client specification. The worked example below came
directly from the call — use it as the acceptance fixture.

```
The accommodation cost report shows the wrong occupancy figure and shows more metrics than
the client wants. Rework it.

Display exactly five figures, per accommodation and again as a summary across all
accommodations. Nothing else on the card:
1. Capacity
2. Occupied beds
3. Standing cost  = capacity × per-head monthly rate
4. Worker payments = sum of what the placed workers actually pay
5. Empty-bed loss  = standing cost − worker payments − occupied cost

Where occupied cost = occupied beds × per-head monthly rate. Occupied cost is an internal term
in the formula only — the client explicitly said it should not be displayed, though he is
indifferent if keeping it visible makes the arithmetic easier to follow. Prefer hiding it.

Remove from the display entirely: margin ("ár"/price), and any figure not in the list of five.
The summary bar at the top must sum the same five across every accommodation.

Acceptance fixture — build this as a test:
  Accommodation: capacity 18, per-head monthly rate 180 EUR.
  Three workers placed: two share Apartment 1 paying 50 EUR each; one worker is alone in a
  two-bed room and pays 230 EUR (he covers the second bed himself).
  Expected:
    Capacity        = 18
    Occupied beds   = 3      <-- currently renders 15, i.e. capacity minus occupied; the
                                 counter is inverted. The bed the third worker pays extra for
                                 is NOT counted as occupied.
    Standing cost   = 3240   (18 × 180) — already correct today
    Occupied cost   = 540    (3 × 180) — internal
    Worker payments = 330    (50 + 50 + 230)
    Empty-bed loss  = 2370   (3240 − 330 − 540)

Fix the occupancy counter (verify the inversion hypothesis before assuming it) and align the
loss formula to the above. Keep the existing daily proration for mid-month arrivals; the client
did not object to it. Keep the "reporting only — creates no wage, deduction or payroll entry"
note.

Open question to leave in the code as a TODO and in the journal: occupancy is defined here as
"active room assignments", not "beds unavailable to others". Confirm with the client whether a
bed paid for but empty should ever count toward occupancy in a different report.

Deliver: service fix, the fixture above as a unit test, summary-aggregation test, updated
template, updated jober-demo-runbook.md section 4 (the current text describes margin, which is
being removed), BUILD_JOURNAL entry.
```

### J4 — Finance page: manual entry, not derived data

> **⚠️ The premise is wrong — verified against the code 2026-07-27. Do not build this as
> written.** Finance is *already* entirely manual. `set_line_item()` stores a hand-typed
> amount; `recompute_month()` only sums line items; and `features/finance/` imports nothing
> from `core.people`, `features.logistics` or accommodation. There is no derivation to remove.
>
> What the client saw was most likely the **seeded demo data** — 54 pre-filled financial months
> — which looks auto-populated but was written by `seed_finance`. On the clean trial instance
> (J11) the pages start empty.
>
> **What genuinely remains of J4:**
> 1. Confirm with the client which workbook columns are inputs and which are computed. Every
>    category is currently an input; if some should be derived, that changes the entry screen.
> 2. He asked for *one* chart (monthly result across the year). The pages currently carry
>    several — a monthly trend, a margin gauge, a by-group breakdown, and an all-offices
>    executive view. Confirm before removing any; the extra ones were built to his earlier
>    brief.
> 3. Resolve `202510`-filename versus `November 2025` sheet label.
>
> The manual workflow is now documented in `jober-demo-runbook.md` §6a, including the one
> genuine trap: **saving line items recomputes the month total and replaces the headline
> revenue/cost typed when the month was created.**

Original prompt, retained for the record:

```
The Finance page currently derives its figures from system data (headcount, inventory,
accommodation). The client explicitly does not want this. He said: "I will enter every number
here by hand, from the spreadsheet I sent you. Do not pull data in here."

Rework the Finance section to:
- Present a manual entry form per month, whose fields mirror the client's supplied workbook
  (HV 202510.xlsx / the filled example he sent). The existing configurable FinanceCategory
  catalog is the right shape — keep it; what changes is that nothing is auto-populated.
- Remove every automatic derivation from people, inventory, accommodation and any other module
  into finance figures. If a category previously auto-filled, it becomes an empty input.
- Keep the existing month/year navigation, the signed display convention, the lock/reopen with
  audited reason, and CSV export. The client did not ask to remove any of those.
- Add one chart: monthly result across the selected year, so January vs February vs March is
  visible at a glance. One chart is sufficient — he said so explicitly. Use the existing
  dependency-free CSS bar-chart approach already used for transport trends; do not add a JS
  charting library.

Do not delete the existing aggregation services in the same commit — mark them unused and
remove them in a follow-up once the client has confirmed the manual page on the trial instance.

Deliver: the reworked page, tests that no module writes into finance figures, chart rendering
test, SK/HU/UK strings, BUILD_JOURNAL entry, updated runbook section 5.

Blocking question for the client before you finish: which of the workbook's columns are inputs
and which are computed? The call did not resolve this, and the 202510-filename-vs-November-2025
sheet-label discrepancy is still open.
```

### J5 — Warehouse goods-receipt log

```
Warehouse stock can be received but there is no way to see what was booked in, and when. The
client demonstrated the gap live: after receiving 3 helmets and 2 boots he could see the new
totals but could not answer "what did I take in today?".

Add a goods-receipt list:
- A list of receipts, newest first, each row showing date received, supplier, reference (the
  order code), and the receipt total value.
- Drilling into a receipt shows its lines: item, size, quantity, unit or total value.
- Filterable by period using the same widget as J7 (day / month / multiple months / full year).

This is a read view over the immutable receipt and movement records already stored by the
warehouse slice — no new write path, no new model unless the receipt header genuinely is not
persisted today. Check first.

Deliver: list view + detail view, tests, SK/HU/UK strings including a proper Hungarian label
for "receipt" (see J10), BUILD_JOURNAL entry.
```

### J6 — Remove equipment returns for Jober

```
Jober never returns issued equipment to stock. The client was unambiguous: "what we issue,
stays out". The current UI offers "Reusable — return to stock" / "Damaged or retired", plus an
outstanding-items and owed-value display that only makes sense if returns exist.

For the Jober client configuration only:
- Remove the return-to-stock path from the UI and from navigation.
- Remove the unreturned-items / amount-owed display from the warehouse surface.
- Remove the receipt-total tile the client pointed at (the "20 units / 730 EUR" figure) — he
  said it is not information he needs.
- Issuing an item decrements stock permanently. Stock correction (J-approved, keep) remains the
  only way to put quantity back.

CorvinumEU must be unaffected: it keeps return-to-stock, the manager equipment recovery review,
and the linked ledger deduction. Do this with the existing per-client feature flag mechanism,
not by deleting shared code. Preserve historical models and migrations exactly as the transport
removal did on 2026-07-20.

Also check the manager equipment recovery review: with returns gone, does that queue still have
a purpose for Jober? If not, flag it rather than removing it unilaterally — it was demoed
previously and the client has not asked for its removal.

Deliver: flag-scoped changes, tests asserting Jober cannot reach the return route (403/404) and
Corvinum still can, updated jober-demo-runbook.md section 3, BUILD_JOURNAL entry.
```

### J7 — Warehouse period filter: full year and multiple months

```
The warehouse report filter is month-based. Selecting a year collapses back into months, so the
client cannot ask for "the whole of 2026". He also wants to select several months at once.

Required:
- Selecting a year shows the full year as a single period, without re-expanding into a month
  picker.
- Multiple months can be selected together and are reported as one combined period.
- Single-month selection keeps working exactly as now.

Build this as a reusable period-filter component — J2 and J5 both need the same granularities
(day / week / month / multi-month / year). Do not implement it three times.

Deliver: the component, the warehouse report wired to it, tests for year, multi-month, single
month and empty period, SK/HU/UK strings, BUILD_JOURNAL entry.
```

### J8 — Persistent worker status rail

```
Add an always-visible status panel to the app shell, pinned to the left or right edge (pick one
and justify it against the existing sidebar layout — the client is indifferent).

Contents:
- A scrollable list of workers with their current working / not-working state, live as the user
  navigates.
- Notifications alongside it, in the same rail.

Constraints:
- Scoped exactly like the People list: coordinators see their own people, managers their own
  office(s), observers everything read-only.
- Must not become an N+1 query on every page render. Cache or defer-load it.
- Must collapse on narrow viewports and not fight the existing collapsible sidebar.
- Shared shell, so CorvinumEU inherits it — but Corvinum's status vocabulary is the candidate
  pipeline, not working/not-working. Drive the labels from the client's lifecycle configuration
  rather than hardcoding two states.

Separately: the client asked for "a couple more icons" on the person cards without specifying
which. Do not guess — list the current card indicators in the journal and send him the list to
choose from.
```

### J9 — Finish the in-app help section

```
The help/guide section renders text only and is incomplete. Finish it:
- Cover every section currently in the navigation, explaining what it is for and how to use it.
- Add illustrations — annotated screenshots of the actual screens, not stock imagery.
- Keep it text-first so it degrades gracefully; images are enhancement, not the content.
- SK/HU/UK. Hungarian matters most here: the client reads the system in Hungarian.

Screenshots must come from the fictional-data demo instance only. Never from a real-data
environment.
```

### J10 — Hungarian translation sweep

```
The warehouse surface shows untranslated English strings in the Hungarian interface — the
client pointed at "issue" and "receipt" specifically, which is doubly bad because "issue" reads
as a defect rather than a stock movement.

Sweep the HU catalog for untranslated and mistranslated strings across the whole application,
not just warehouse. Pay attention to domain terms where a literal translation is wrong:
issue / receipt / adjustment / standing cost / occupancy. Recompile catalogs. Re-check SK and
UK for the same terms while you are in there.
```

### J11 — Clean instance for the client trial

The client's closing request, and the one with the most risk attached.

```
Prepare a clean Jober instance for the client's own hands-on trial and send him the link.

- Completely empty: no synthetic seed data at all. He was explicit — "when you hand it over,
  let it be empty".
- All the fixes above applied first. He intends to enter roughly 20 people, an accommodation,
  and a whole project, and then show it internally.

RISK — raise this with the client and internally before sending the link. He also said he will
load "our entire actual current warehouse" into it. That is real operational data, and he is
likely to enter real worker records alongside it. The real-data gate is currently closed
pending the Art. 28 processor DPA and the processors/retention list. Either:
  (a) the DPA and retention list are completed before the link is sent, or
  (b) the instance is handed over with an explicit written condition that it is fictional-data
      only, and a technical control if one is cheap.
Do not send the link on the assumption this will be sorted out afterwards.
```

---

## 3. Send back to the client

Questions the call raised but did not answer:

1. **Warehouse opening/closing value** — he said both "at year end there's a closing value, that's
   the one there" and later "the opening/closing, I don't need that either". Which is it? The
   list of items plus the current total value is confirmed wanted; the period valuation is not.
2. **Finance workbook** — which columns are manual inputs and which are computed from the others?
   Also still open: is the period October 2025 or November 2025 (`202510` filename vs the
   "November 2025" sheet label)?
3. **Accommodation occupancy** — should a bed that a worker pays for but does not occupy ever
   count as occupied in any report? Current spec says no.
4. **Person-card icons** — which additional indicators does he want? Send the current list.
5. **Transport** — it was removed from Jober after the previous interview, but transport
   management appears in the shared requirement list for both clients. Reinstate for Jober, or
   is the shared list stale?
6. **Equipment recovery review** — with returns removed, does the manager review queue still
   serve a purpose for Jober?