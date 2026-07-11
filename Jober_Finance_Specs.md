# Finance Module Spec — from the manager's Excel (`HV_202305_blank.xlsx`)

Reverse-engineered from Jober's actual monthly profitability workbook. This is the authoritative input for the **finance module (Phase 4)** and resolves the round-3/4 "send your Excel" blocker. Hand to GPT with the v3 plan and `jober_answers_round4.md`.

> The file is a **blank template** (no figures), so the *structure and formulas* are authoritative; actual values/sign conventions need one filled month to confirm (see "Confirm with the manager").

---

## 1. Shape of the model

- **One sheet = one month** (the file's sheet is "Június (2)"; filename suggests a YYYYMM convention, `HV_202305`).
- **Projects are columns.** This month's columns were: RLS 067, Europack, Mediashop, Minit, Mevis 080, DHL Gáň 63/2, DHL Bratislava 063, Pivovar Hurbanovo, Delticom.
  - ⚠️ These differ from the round-4 current project list (DHL BA, DHL Gáň, DHL Nitra, WEBASTO, MEVIS, MINIT, C2I, CARGO). **Projects change month to month**, so the module must treat the project set as **data entered per period**, never as fixed columns.
- **Rows = line items**, split into a **costs** block and a **revenues** block, then per-project **profit/loss**, then a **company total**.

---

## 2. Line items (the catalog)

These become the configurable finance-category catalog. Labels below are the originals (mixed Slovak/Hungarian) with an English gloss and a suggested **group** (the grouping is what powers the manager's "transport vs accommodation vs company" breakdowns). HU/SK/UA UI wording comes through i18n with team-confirmed terms.

### Costs (náklady)

| Original label | English gloss | Group |
|---|---|---|
| hrubá výplata bez zrážok | Gross wage (before deductions) | Labour |
| SZCO | Sole-trader (SZČO) payments | Labour |
| odvody | Payroll levies/contributions | Labour |
| vodič | Driver | Transport |
| skoda | Damage (cost) | Damage |
| VZV oktatas | Forklift training | Compliance |
| VZV jogsi | Forklift licence | Compliance |
| Ubytovanie | Accommodation | Accommodation |
| Poistenie | Insurance | Compliance |
| Lekarske | Medical | Compliance |
| Koordinatorok | Coordinators | Overhead |
| Leasingek | Leasing | Transport |
| Benzin | Fuel | Transport |
| Myto | Toll | Transport |
| Faktoring | Factoring | Overhead |
| Iroda | Office | Overhead |
| Toborzas | Recruitment | Overhead |
| HR | HR | Overhead |
| Oblecenie | Clothing/equipment | Equipment |
| Iné náklady mimoriadne | Other extraordinary costs | Other |

### Revenues (výnosy)

| Original label | English gloss | Group |
|---|---|---|
| faktúry | Client invoices | Revenue |
| zrážky prijaté od zam | Deductions received from employees | Revenue |
| obed | Meals | Accommodation/Welfare |
| ubytovňa | Accommodation charged | Accommodation |
| škoda | Damage recovered | Damage |

---

## 3. Calculations

- **Total costs** per project = sum of all cost lines.
- **Total revenues** per project = sum of all revenue lines.
- **Profit/loss** per project = total revenues + total costs. *(In the Excel `profit = totalCosts + totalRevenues`, which implies costs are entered as negative numbers — confirm; the module should store sign explicitly and compute `revenues − costs`.)*
- **Company total** = sum of profit/loss across **all** projects.
- **Group breakdowns** (the manager's headline want): aggregate by the Group column across all projects, e.g.
  - **Accommodation result** = `ubytovňa` revenue − `Ubytovanie` cost.
  - **Transport result** = transport revenues (none today) − (driver + leasing + fuel + toll).
  - …and per-project and whole-company. So **each line item carries a group tag** to make these one-click.

---

## 4. Two real bugs in the current template — do NOT reproduce

These are exactly why a system beats the spreadsheet; the module's dynamic sums must avoid them:

1. **Minit's total-cost formula is off-by-one.** `E23 = SUM(E2:E21)` while every other project sums `…:22` — so Minit **silently excludes "Iné náklady mimoriadne"** (the last cost row). One project's costs are understated.
2. **The company total omits two projects.** `K33 = SUM(B33:H33)` — it stops at column H, so **Pivovar Hurbanovo and Delticom are left out** of the company-wide profit/loss.

The module must total **dynamically over the actual set of projects and the full set of line items**, so neither error is possible.

---

## 5. Behaviour requirements (from the manager's interview)

- **Manual entry** per project per line item (he wants to re-check figures himself; ~20 numbers/project, most stable month to month). Source numbers arrive as a PDF from the bookkeeper; he types them in.
- **A "calculate" action** that totals everything on demand — he may fill in mid-month and recompute, not only at month-end.
- **Monthly history + yearly rollup**, **archived and reproducible**: from June he can open January and see how it looked. Lock a closed month; reopening requires a reason + audit (per `AGENTS.md`).
- **Decimal money, EUR.** Never floats.
- **Observer (and the manager's boss) can view** closed months — it's the reporting layer that "convinces the boss and the bookkeeper."
- **No Pohoda integration** — manual entry is deliberate. (A later PDF import is explicitly not worth it for ~20 numbers; out of scope.)

---

## 6. Confirm with the manager

- **Sign convention:** are costs entered as negatives (so `profit = costs + revenues`), or should the module compute `revenues − costs` from positive inputs? (Needs one *filled* month to see.)
- **"SZCO" cost line** exists even though workers are "employees, not contractors" — keep, rename, or drop?
- **Better labels:** he asked for cleaner naming — the cleaned template (`HV_finance_template_clean.xlsx`) is the proposal for him to confirm or correct before the catalog is fixed in code.
- **Group tags:** confirm the Group column above matches how he wants transport/accommodation/overhead split.