# ADR 0032: A payroll run recovers what is outstanding, not just its own window

Status: **Accepted — 2026-08-05.**
Date drafted: 2026-08-05

## Context

Reported by the owner: **an advance given in July is never deducted from the
August salary.** Investigation found it was worse than a display problem — the
money was never recovered at all.

`include_cycle(year, month)` swept only entries inside its own 21st-to-20th
window:

```python
entry_date__gte=start, entry_date__lte=end
```

The windows are disjoint. An entry that missed its run — dated before the
window, or recorded after that window had been closed — was therefore never
picked up by *any* later run. It stayed `OPEN` for ever: reported as owed,
collected never.

Two things in the code already disagreed with that, which is the strongest
evidence it was a defect rather than a decision:

- `open_balance()` counts **every** unsettled entry regardless of date, and its
  docstring calls the result *"what the person currently owes against future
  pay"*. The office was already told the money was owed.
- `cycle_for()` correctly places a 25 July advance in the **August** run, while
  `ledger_deduction_series` grouped the pay overview by the entry's **calendar
  month**. So the ledger said August and the overview said July.

That grouping was chosen on 2026-08-04, in this repository, on the reasoning
that all four columns of the overview should describe one period. The reasoning
was tidy and wrong: an advance handed over on the 25th is recovered from the
next month's pay, so showing it against the current month describes a payslip
that has already been paid.

## Decision

### 1 · A run collects what is outstanding at its cutoff

`include_cycle` now sweeps every `OPEN` entry dated on or before the window end,
with no lower bound. Anything still outstanding when a run happens is recovered
by that run. An advance that missed August is collected in September; nothing
can fall through.

The first run after this change performs a genuine catch-up over existing data.
That is intended and was decided explicitly: those entries were already counted
as owed by `open_balance`, so nothing changes about *what* is owed — only about
when it is finally collected.

### 2 · The report answers "did" or "will", whichever applies

`cycle_report` shows entries already carrying that cycle key — what the run
actually collected — and, only while the cycle has not been run, adds every open
entry dated on or before its cutoff. A closed run therefore keeps reporting
exactly what it took, however the sweep rules change afterwards, while an unrun
cycle forecasts what it is about to take. Both the ledger page and the
accountant CSV export read this, so both agree with the sweep.

### 3 · The overview shows the run that collects the money

`settling_cycle_key(entry)` returns the stored cycle key when the entry has been
assigned one, and otherwise walks forward from `cycle_for(entry_date)` past any
already-closed run. The pay overview groups deductions by that, so a 25 July
advance appears in the August row beside the August gross wage.

### 4 · The settled-cycle refusal is withdrawn

Added earlier the same day to stop a backdated entry being orphaned, it was
wrong twice over:

- it blocked ordinary present-day work. Equipment charges reach the ledger
  through `equipment_charge_to_ledger` with **no date at all**, so they default
  to today; once the current run was closed, issuing chargeable equipment
  stopped entirely on staging.
- it solved a problem carry-forward removes. A late entry now has somewhere to
  go, so there is nothing to reject.

Refusing to record something that really happened was the wrong shape of answer.
The money exists whether or not the bookkeeping is ready for it.

## Consequences

**The 21st-to-20th boundary is unchanged.** C-Q3 stands. What changed is what a
run collects, not when a run covers.

**An entry's recovery month is no longer a pure function of its date.** Until it
is included, which run collects it depends on which runs have already gone out.
That is the price of never losing money, and it is why `settling_cycle_key`
prefers the stored key: once collected, history is fixed.

**The first deploy sweeps historical strays.** On any database with outstanding
entries, the next `include_cycle` will collect all of them at once. Check what a
run will take before making it — `cycle_report` forecasts exactly that.

**Existing entry dates are not rewritten.** Their dates are what happened;
carry-forward changes which run collects them, not when they occurred.

## Open

- C-Q5 sign-off still pending: corrections after inclusion remain reversal-only,
  and there is still no way to reopen a run closed by mistake. Raised with the
  owner on 2026-08-04 and not built.
