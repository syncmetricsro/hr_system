# Phase 3/4 — Open Questions for Jober

Created: 2026-06-29

These block the remaining Phase 3 modules (accommodation pricing, equipment
deductions, blacklist) and the start of Phase 4 (finance). Each has a safe
default we'll use if no answer arrives — except the blacklist, which can't be
built for real use without the legal answer. Record the answer + date on each.

## 1. Accommodation cost
How should housing cost be tracked? Is there a **fixed monthly rate per room**,
or **per bed / per person**? Do different accommodations/rooms have different
rates, and are there **per-worker overrides** (someone pays a different amount)?
Is the cost just **recorded for reporting**, or **charged/deducted** from the
worker?
- Why it matters: shapes the rate model + occupancy-cost reporting.
- Safe default: monthly rate **per room**, recorded for reporting only (no
  auto-deduction), with an optional per-assignment override.
- **Answer:**

## 2. Unreturned equipment (deduction review)
When a worker does **not return** issued gear, what should happen? Is the
item's **value deducted** from their pay? **Who reviews/approves** the
deduction, and is there a waive/appeal step?
- Why it matters: shapes the returns → deduction workflow (the valuation itself
  is already built: latest manual unit price).
- Safe default: flag unreturned items at their unit price for a **manager to
  review/approve**; **no** automatic payroll deduction.
- **Answer:**

## 3. Blacklist (legal)
Do you keep a list of workers who must **not be rehired/placed**, and what is
the **legal basis (GDPR)** for it? What data identifies a person on it (name +
ID number?), **who may see the reason** (managers only?), and how long is it
kept (5 years was mentioned)? Should matching use a **hashed ID** so we never
store the raw ID number?
- Why it matters: lawyer item — **blocks building the blacklist module for real
  use** (DPA / blacklist legality).
- Safe default: none — needs the legal answer first. (We can build inert
  mechanics, but the legal answer may reshape them.)
- **Answer:** _Interim (2026-06-29): candidate legal basis identified — workers
  sign an annual paper (a temporary contract) that includes GDPR / personnel-data
  clauses. Awaiting a sample to check whether it actually covers a do-not-rehire
  list. Owner not reachable yet; still needs lawyer confirmation before build.
  Verify in the sample: (1) purpose — does it name rehire-screening / not-rehire
  use, not just general HR processing; (2) basis type — consent (fragile,
  withdrawable) vs legitimate interest (usually sounder for a blacklist);
  (3) retention period (5y?) stated + justified; (4) identifier retention for
  post-exit matching (supports our hashed-ID approach); (5) transparency — worker
  told data may be used against future engagement + who sees it; (6) blacklist
  reason categories may edge into special-category data (stricter rules)._

## 4. Finance sign convention (Phase 4)
In your monthly finance sheet, are **costs entered as negative numbers**, or are
costs **positive** and the system computes **revenue − cost**? Could you share
**one filled-in month** so we match it exactly (and avoid the two summing bugs
in the current spreadsheet)?
- Why it matters: determines how "net" is computed across the finance module;
  **Phase 4 blocker**.
- Safe default: `net = revenue − cost` (current assumption), to confirm.
- **Answer (CONFIRMED 2026-06-29): positive convention.** Costs and revenues are
  entered as **positive** numbers; the system computes **net = revenue − cost**.
  This matches how the finance module was already built (amounts stored positive,
  sign derived from the category kind), so the confirmation **validates** the
  existing implementation rather than unblocking new work. Hardened accordingly:
  the write path (`finance.services.positive_amount`, `logistics._non_negative`)
  and model validators now **reject negative** amounts across finance line items,
  monthly revenue/cost, room rates, equipment unit prices, and unreturned-item
  charges. Equipment charge = `unit_price × quantity` (positive arithmetic).
  Still helpful: a real filled month to reconcile the seeded category labels.

## 5. Inactive reasons (minor)
What are the allowed reasons for marking a person **Inactive** (e.g. sick, left,
suspended, military service)?
- Why it matters: catalog values for the lifecycle.
- Safe default: build a configurable list; seed a few placeholders.
- **Answer:**

---

## Magyar — kérdések Jobernek

A fenti kérdések magyarul, továbbküldéshez.

**1. Szállásköltség**
A szállás díja fix **havi díj szobánként**, vagy **ágyanként / személyenként**?
Eltérő díjak vannak-e a különböző szállásoknál/szobáknál, és vannak-e
**munkavállalónkénti eltérések** (valaki más összeget fizet)? A költséget csak
**nyilvántartjuk** (riportokhoz), vagy **levonjuk/felszámítjuk** a
munkavállalónak?

**2. Vissza nem adott felszerelés**
Ha egy munkavállaló **nem adja vissza** a kiadott felszerelést, **levonjuk-e az
értékét** a béréből? **Ki hagyja jóvá** a levonást, és van-e elengedési/
fellebbezési lépés? (Az értéket már számoljuk a kézi egységárból — ez csak a
folyamat.)

**3. Feketelista (jogi)**
Vezetnek-e listát azokról, akiket **nem szabad újra felvenni/kihelyezni**, és mi
ennek a **jogalapja (GDPR)**? Milyen adat azonosítja a személyt (név +
igazolványszám?), **ki láthatja az indokot** (csak vezetők?), meddig őrzik (5
év?), és az egyezést **hashelt azonosítóval** végezzük-e, hogy soha ne tároljuk
a nyers számot?

**4. Pénzügyi előjel-konvenció (Phase 4)**
A havi pénzügyi táblázatban a költségeket **negatív számként** viszik be, vagy
**pozitívan**, és a rendszer számolja a **bevétel − költség** értéket? Meg
tudnának osztani **egy kitöltött hónapot**, hogy pontosan egyezzünk?

**5. Inaktív okok (kisebb)**
Milyen okok engedélyezettek a munkavállaló **Inaktívra** állításához (beteg,
kilépett, felfüggesztve, sorkatonai szolgálat, …)?
