# ADR 0033: Ledger entries are deletable until the money is paid

Status: **Accepted — 2026-08-05.**
Date drafted: 2026-08-05

## Context

C-Q5 had stood unanswered since the ledger was built, with a recorded default of
*"no hard deletes; post-inclusion only reversal entries"*. The owner rejected it
directly: entries **should be deletable and cannot be made immutable**.

The default was defensible on paper and awkward in practice. A mistyped advance
that had been swept into a cycle could only be corrected by recording an
opposite entry, so a keystroke error became two permanent rows that net to zero.
For a small office reading its own ledger, that is noise standing in for
rigour — and it accumulates.

A second gap surfaced at the same time: a cycle closed by mistake was
unrecoverable. `include_cycle` locked its entries and nothing put them back, so
a misclick cost a reversal per entry.

## Decision

### 1 · The line is where the money leaves

- `OPEN` and `INCLUDED_IN_CYCLE` entries can be **deleted**.
- `DEDUCTED` entries cannot. The money has been paid; the ledger is what the
  accountant export and any later pay dispute are argued from.

The owner chose this line over "anything is deletable" when the consequence was
put to them. Included means *queued for a run*, not *paid* — so everything
before payday is a record of an intention and may be corrected freely.

### 2 · The row goes; the fact that it existed does not

Every deletion writes `ledger.entry_deleted` carrying person, amount, currency,
category, entry type, entry date, the status it held and its cycle key. The
ledger stays clean without a paid-adjacent figure being able to evaporate
silently. This was not optional: it is the difference between a tidy ledger and
an unauditable one.

### 3 · Delete and reverse both stay, because they mean different things

**Delete** says *this never should have existed* — a typo, the wrong person.
**Reverse** says *this happened and is being given back*, and leaves both sides
visible and linked. An accountant reading the ledger can tell them apart; only
reversal preserves the relationship. Keeping both costs nothing, since reversal
already worked.

`reversal_of` is `PROTECT`, so deleting an entry that already carries a reversal
is refused with an instruction to delete the reversal first. Refusing beats
cascading: removing a row the operator did not select is the worse surprise.

### 4 · A cycle reopens while its own window is still running

`reopen_cycle(year, month)` returns included entries to `OPEN` and clears their
cycle key, allowed **while `today <= ` the cycle's own end date** — there is
still time to collect them properly. Refused once anything in it has been paid.

Refused after the window ends too, and **the refusal says what happens instead**:
it names the next run and the dates it covers. A refusal that only says no
leaves the office stuck; this one tells them where the entries will be
collected, which under carry-forward (ADR 0032) is always true.

## Consequences

**C-Q5 is answered and closed.** The `no hard deletes` line in the ledger
services docstring, which described the old default, is corrected.

**Deletion is a manager action** — it rides on `ledger.enter`, which is
Manager-only on CorvinumEU. Nothing below that role can remove a money record.

**Audit volume grows slightly**, which is the intended trade: a deleted entry
leaves one event carrying everything the row held.

**The reopen window is deliberately narrow.** It recovers a misclick made during
the cycle it belongs to, and nothing else. It is not a way to revisit a finished
period, which is what reversal is for.

## Open

- Whether a *deleted* entry should be visible anywhere in the product, rather
  than only in the audit log. Nobody has asked; the audit log answers it today.
