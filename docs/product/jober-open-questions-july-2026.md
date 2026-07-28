# Jober — open questions from the July 2026 handover call

Questions the demo walkthrough raised but did not settle. Four of them **block or
reshape work already on the list**, so they are worth asking before the next
build slice rather than after it.

Status as of 2026-07-28. Answers belong in this file, dated.

**Answered so far:** question 2a and 2b (finance workbook — see below).
Question 6 is the one that blocks build work.

---

## 1. Warehouse opening and closing value — which is it?

He said both of these in the same conversation:

> "at year end there's a closing value, that's the one there"

> "the opening/closing, I don't need that either"

**Confirmed wanted:** the item list plus the current total value.
**Unclear:** the period valuation (opening balance / closing balance per period).

**Why it matters:** the goods-receipt log (J5) and the warehouse period filter
(J7) are both cheaper without period valuation. If it is wanted, it should be
designed in from the start rather than bolted on.

---

## 2. Finance workbook — ✅ **ANSWERED 2026-07-28** (2a, 2b); 2c still open

**2a. Inputs vs. computed — answered by the workbook itself.**

`docs/examples/HV 202510.xlsx` was read directly. **Nothing is derived from
another category.** The sheet is projects-as-columns, categories-as-rows, in two
office blocks (*Megyer* = Veľký Meder, and *DS*).

| His rows | Count | Kind |
|---|---|---|
| `hrubá výplata bez zrážok` … `Iné náklady mimoriadne` | 20 | **typed input** (cost) |
| `celkové náklady` | 1 | formula `SUM(B3:B23)` |
| `faktúry` … `škoda` | 5 | **typed input** (revenue) |
| `celkové výnosy` | 1 | formula `SUM(B26:B31)` |
| `zisk/strata` | 1 | formula `B24+B32` |
| `Summ Megyer`, `Summ DS`, `Summ Spolu` | 3 | formulas over the above |

**25 inputs, 8 totals, and every total is a plain sum.** So he types all 25 by
hand and nothing else — which is exactly what the app already does.
`set_line_item()` stores a hand-typed amount, `recompute_month()` only sums, and
no total is ever stored or asked for. **The app's 25 seeded `FinanceCategory`
rows already match his 25 rows one-to-one, in his order**, so the entry screen
mirrors his workbook.

Nothing to change. He wanted manual entry with computed totals; that is what
exists.

> **⚠️ Practical warning — tell him before he enters November 2025.** His own
> total for the **Minit** column is wrong. Every other column sums its costs
> with `SUM(…:…23)`; Minit uses `SUM(C3:C22)` and **omits row 23**, so the €200
> of `Iné náklady mimoriadne` is missing. His sheet says **−15 087,17**; the
> twenty rows actually total **−15 287,17**, and Minit's profit is overstated by
> €200.
>
> This matters operationally, not rhetorically: when he types those numbers in,
> the app will show −15 287,17 and he will reasonably conclude the app is
> broken. It is his SUM range, not our arithmetic. Say so first.

**Two more observations from the file:**

- **Győr is absent.** Only two office blocks. Either it postdates this period
  or it is tracked elsewhere — worth confirming, since the app has three.
- **His signs are inverted relative to ours.** He stores costs negative and
  computes profit as `cost + revenue`; the app stores everything positive
  (validators enforce it) and computes `revenue − cost`. Same result. But
  anyone transcribing must **not** carry his minus signs across, or they will
  be double-negated.

**2b. The period discrepancy — answered.** It is **November 2025**. The
workbook contains exactly one sheet, named `November 2025`; the `202510`
filename is simply mislabelled (owner-confirmed 2026-07-28).

**2c. How many charts?** He asked for *one* — monthly result across the year.
The pages currently carry four: a monthly trend, a margin gauge, a by-group
breakdown, and an all-offices executive view. **The extra three were built to
his earlier brief, so please confirm before we remove any.**

---

## 3. Accommodation occupancy — does a paid-for empty bed count?

Occupancy is currently defined as **"a worker is assigned here"** — a head
count of people, not of beds withdrawn from circulation.

Concretely, using his own example: the worker alone in a two-bed room who pays
230 EUR to keep it to himself counts as **one** occupied bed. The second bed —
which he is paying for and nobody can use — reads as **empty**, and therefore
contributes to empty-bed loss.

That is what he specified, and it is what now ships. The question is whether it
is what he *wants* in every report, or whether a "beds unavailable" figure
belongs somewhere alongside it.

**Why it matters:** it changes the meaning of empty-bed loss, which is the
headline number on that page.

---

## 4. Person-card icons — which ones does he want added?

He asked for "a couple more icons" without saying which. Here is what a person
row carries **today**, so he can point at gaps rather than guess:

| Indicator | Where | What it shows |
|---|---|---|
| **Avatar** | list + detail | uploaded photo, or a default |
| **Status dot** | list + detail | lifecycle status, by colour |
| **Status text** | list | the same status, spelled out |
| **Certificate badges** | list + detail | one icon per certificate category held |
| **Blacklist banner** | **detail only** | an open blacklist case, full-width |

The certificate badges are: **health/medical, forklift, crane, welding, other** —
one per category the worker holds, coloured by expiry (valid / expiring within
30 days / expired), with the certificate name and expiry date on hover.

> **Worth checking with him:** he listed "blacklist indicator on the person
> card" as confirmed-working. Today that is a **banner on the person detail
> page**, not an icon in the people list. If he expects to spot a blacklisted
> worker while scanning the list, that does not exist yet.

---

## 5. Transport — is it in scope again?

Transport was **removed from Jober on 2026-07-20** following the previous
interview, and is currently flag-off (`"transport": False`).

But transport management appears in the shared requirement list for both
clients. Either that list is stale, or this is a **scope reversal** to plan for.

**Why it matters:** the code and migrations were preserved rather than deleted,
so reinstating is a flag flip plus UI review — cheap. But it is not free, and it
is not currently in any estimate.

---

## 6. Equipment recovery review — does it survive?

J6 removes equipment returns for Jober entirely ("what we issue, stays out").

With returns gone, the manager's **equipment recovery review queue** — where an
unreturned item is approved as a deduction or waived — may have nothing left to
do. It was demoed previously and he has not asked for its removal, so we have
not touched it.

**This blocks J6.** Building the returns removal against a queue we then delete
is wasted work, so this answer should come first.

---

## Not a question — something to tell him

While fixing the audit filter we found that the **equipment deduction review
queue was not office-scoped**, and neither was the decision it leads to. A
manager in one office could approve a charge against a worker in another. It is
fixed, tested, and shipping in the same batch.

He does not need the technical detail, but if he is going to hand this to staff
across three offices, he should know the boundary was audited and tightened
rather than assumed.
