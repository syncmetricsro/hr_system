# Jober Per-Project Profitability Specification

> **Changelog, 2026-07-20:** Replaces the blank-template uncertainty with facts
> verified from the filled Jober workbook `HV 202510.xlsx`. Costs are negative,
> revenues positive, regional roll-ups are required, and Jober profitability is
> unblocked at specification level. The current positive-only implementation is
> not changed by this documentation update and requires later reconciliation.

> **Status: SPECIFICATION AUTHORITY, NOT AN IMPLEMENTATION CLAIM.** This document
> specifies Jober's target `features/profitability` capability. CorvinumEU keeps
> profitability OFF. Application changes require a separate build prompt.

## 1. Source and provenance

The source was supplied as `HV 202510.xlsx` and referred to as
`HV_202510.xlsx` in interview notes.

| Property | Verified value |
|---|---|
| Client/purpose | Jober monthly per-project P&L |
| SHA-256 | `2e293b79dc237072c08e0ea16a36eaf8a60eed8b2bf3d1298b74e6a93f5743f6` |
| Worksheet | `November 2025` |
| Filename period token | `202510` (normally October 2025; mismatch is open) |
| Regions | Megyer, DS (Dunajska Streda) |
| Projects | 9 |
| Source sign convention | Costs negative; revenues positive; P/L is their sum |

This workbook is not `radonak.xlsx`. `radonak.xlsx` is the deferred CorvinumEU
per-worker wage sheet. It neither specifies nor blocks Jober profitability.
The earlier blank `HV_202305_blank.xlsx` established a preliminary shape; this
filled workbook supersedes it where values, signs, regions, formulas, or project
layout differ.

## 2. Product boundary and module placement

Jober's monthly project P&L is a full profitability/economic dashboard. It is
explicitly in scope for Jober and explicitly out of scope for CorvinumEU. It is
separate from accommodation/equipment operational cost reporting and does not
authorize payroll calculation or automatic wage deductions.

Target placement is `features/profitability`, selected ON by Jober and OFF by
CorvinumEU. The current repository still implements this capability under
`features/finance` and stores non-negative magnitudes with cost/revenue kind
providing the sign. The verified workbook uses signed cells. A later build must
choose and migrate/validate the persistence convention while preserving the
source's signed behavior at entry, calculation, and export boundaries. This
document changes no current model or validator.

## 3. Workbook shape

One period presents projects as columns and line-item categories as rows. The
verified project grouping is:

| Region | Projects |
|---|---|
| Megyer | RLS 067; Minit; Mevis 080; DHL Gan 63/2; DHL Bratislava 063 |
| DS | Pivovar Hurbanovo; Mediashop; Europack; Delticom |

Project and region sets are data, never fixed code or fixed spreadsheet ranges.
Each project has a costs block, a revenues block, and computed P/L. Projects
roll up to region totals, and regions roll up to a grand total.

## 4. Category seed list

Labels below reproduce the source workbook. Stable internal keys and translated
EN/SK/HU/UK labels are implementation work; source wording must remain traceable.

### Costs (`NAKLADY`)

| Source label | English meaning | Proposed group | Later source |
|---|---|---|---|
| `hrubá výplata bez zrážok` | Gross wage before deductions | Labour | Manual; no Jober wage engine |
| `SZCO` | Sole trader/subcontractors | Labour | Manual; settlement feature deferred |
| `odvody` | Levies/contributions | Labour | Manual |
| `vodič` | Driver | Transport cost | Manual; transport feature OFF |
| `škoda` | Damage | Damage | Manual |
| `VZV oktatas` | Forklift training | Compliance | Manual |
| `VZV jogsi` | Forklift licence | Compliance | Manual |
| `Ubytovanie` | Accommodation | Accommodation | Later accommodation contribution |
| `Poistenie` | Insurance | Compliance | Manual |
| `Lekarske` | Medical | Compliance | Manual |
| `Koordinatorok` | Coordinators | Overhead | Manual |
| `Leasingek` | Leasing | Transport cost | Manual; transport feature OFF |
| `Benzin` | Fuel | Transport cost | Manual; transport feature OFF |
| `Myto` | Toll | Transport cost | Manual; transport feature OFF |
| `Faktoring` | Factoring | Overhead | Manual |
| `Iroda` | Office | Overhead | Manual |
| `Toborzas` | Recruitment | Overhead | Manual |
| `HR` | HR | Overhead | Manual |
| `Oblecenie` | Clothing/equipment | Equipment | Later equipment contribution |
| `Iné náklady mimoriadne` | Other extraordinary costs | Other | Manual |

### Revenues (`VYNOSY`)

| Source label | English meaning | Proposed group | Later source |
|---|---|---|---|
| `faktúry` | Invoices | Revenue | Manual |
| `zrážky prijaté od zam` | Deductions received from workers | Recovery | Later approved recovery/advance contribution |
| `obed` | Lunch | Welfare | Manual |
| `ubytovňa` | Accommodation charged | Accommodation | Later accommodation contribution |
| `škoda` | Damage recovered | Damage | Manual or later approved recovery contribution |

## 5. Logical data model

- `Project.region`: region roll-up key. The implementation should use a
  configurable relation/catalog if regions are confirmed to grow.
- `FinancePeriod`: project, year, month, state, note, created/updated actor and
  timestamps, lock metadata, and reopen reason; unique by project and month.
- `FinanceCategory`: stable key, source label, cost/revenue kind, reporting
  group, order, active state, and manual/operational source policy.
- `FinanceLine`: period, category, logical signed `Decimal` amount, actor, and
  timestamps; unique by period/category.

Logical signs are invariant: costs are negative, revenues positive, and zero is
valid for either category. Whether the database stores the logical signed value
or a non-negative magnitude plus category kind remains an implementation
reconciliation decision. In either case, API/form/export behavior must reject a
cost with revenue effect or a revenue with cost effect rather than silently
changing business meaning.

Totals are derived and never persisted as editable line items. Decimal EUR is
mandatory; floats are forbidden.

## 6. Calculations

For every project-period:

- Total costs = sum of every active cost-category line; result is zero or
  negative.
- Total revenues = sum of every active revenue-category line; result is zero or
  positive.
- Profit/loss = total costs + total revenues.
- Region P/L = sum of all included project P/L values in that region.
- Grand total = sum of all included region/project P/L values.
- Group result = signed sum of all lines assigned to the group for the selected
  project, region, period, or year.

Calculations always query the actual project/category sets. No project-specific
column range or category-specific row range is allowed.

## 7. Verified spreadsheet defect

The filled workbook demonstrates one concrete formula defect:

- Minit is column C. `C24` uses `SUM(C3:C22)` while the complete cost block ends
  at row 23.
- The omitted `C23` extraordinary-cost value is `-200` EUR.
- Cached Minit P/L is therefore `279.09` EUR instead of `79.09` EUR.
- Megyer's regional result and the grand total are also overstated by `200` EUR.

The application must compute every project over the same complete category set,
making this class of silent omission impossible. The older blank workbook also
showed a company-total range omission; dynamic project and region queries avoid
both defects without encoding workbook coordinates.

## 8. MVP behavior

- Managers manually enter each project/month/category value and may recalculate
  before month end.
- The UI shows cost, revenue, and P/L by project, region, and grand total using
  one consistent calculation path.
- Filters support month, year, region, project, category, and reporting group.
- Monthly history is reproducible. Closing locks a period; reopening requires a
  non-empty reason and append-only audit with actor and old/new values.
- Observers may view closed periods and exports but cannot edit or reopen them.
- A per-project feature policy can exclude a project if the outstanding toggle
  question confirms that requirement; global Jober enablement remains ON.
- No Pohoda or other live accounting integration, PDF import, or OCR is in MVP.

### CSV export

The bookkeeper export is detailed, stable, and machine-readable. One row contains
`period`, `region`, `project_code`, `project_name`, `category_key`,
`category_label`, `kind`, `group`, and signed `amount_eur`. Derived project,
region, and grand totals use clearly identified summary rows or a separate
summary export; they are never copied from editable stored totals. UTF-8 and a
documented delimiter/decimal convention are required in the build acceptance
criteria.

## 9. Later operational contributions

Later automation may prepopulate selected lines through a core registry or
client composition layer; features must not import each other.

- Accommodation cost and revenue: `features/accommodation`.
- Deductions received: approved Jober recovery/advance capability.
- Clothing/equipment: `features/equipment`.
- SZCO/subcontractor settlement: deferred and remains manual until approved.
- Driver, leasing, fuel, and toll: remain manual because Jober transport and
  vehicle management are OFF.
- Coordinators, factoring, office, recruitment, HR, insurance, and other
  overhead remain manual.

Operational proposals require manager review before becoming locked finance
lines. Recalculation must be idempotent and must not duplicate contributed
amounts.

## 10. Open questions

- Is the period October 2025, as `202510` suggests, or November 2025, as the
  worksheet states?
- Are Megyer and DS the complete fixed region list, or must regions be managed
  as growing data?
- Is profitability switched on globally for Jober or individually per project?
- Should persistence adopt signed values or retain positive magnitudes by kind
  while exposing the workbook's signed convention?
- Confirm final translated category labels and whether `SZCO` remains active.

The finance Excel gate for Jober is lifted: the structure, categories, signs,
roll-ups, and export source shape are captured. These open configuration and
reconciliation questions do not reclassify `radonak.xlsx` or unblock any
deferred CorvinumEU wage work.
