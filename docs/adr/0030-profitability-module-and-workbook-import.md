# ADR 0030: Profitability module placement, sign reconciliation, and workbook import

Status: **Accepted — 2026-08-04.**
Date drafted: 2026-08-04

> **Status note — 2026-08-06:** the project-year grid described below as
> read-only became the existing bulk-entry surface on 2026-08-05. It still
> writes through to the same monthly records and stores no annual total. The
> cross-project monthly and annual workbooks remain read-only reports.

## Context

`Jober_Finance_Specs.md` has carried three structural questions since
2026-07-20, all deferred to "a later build":

- §2 names `features/profitability` as the target placement while the code lived
  in `features/finance`.
- §5 and §10 question 4 left open whether persistence should adopt the source
  workbook's signed values or keep non-negative magnitudes with `kind` supplying
  the sign.
- §3 and §7 describe the source workbook `HV 202510.xlsx` but nothing read it.

Jober will accept the implementation when it looks and totals like that
workbook. Answering the three questions is what this ADR records.

## Decision

### 1 · The module moves; the Django app label does not

`features/finance` is now `features/profitability`, the placement §2 names and
the name the `profitability` feature flag has always used.

The app label stays `finance`. Django derives a label from the module's last
component, and letting it follow would rename every table (`finance_*`),
invalidate the `to='finance.…'` references inside this app's own migrations,
and require rewriting `django_migrations.app` and `django_content_type.app_label`
on every database holding data — staging included. That is real risk on a live
database for something no reader can see: the label is an internal key, the
module path is what the spec and the flag care about. `makemigrations --check`
reports no changes, which is the evidence.

Renaming the label remains possible as its own slice with its own restore drill.
It is deliberately not bundled with a feature change. The reasoning lives in
`ProfitabilityConfig`'s docstring so it is found by whoever next wonders why the
two disagree.

### 2 · §10 question 4 is answered: signed at the boundary, magnitude in storage

Not by choosing, but by observing that the build already chose. Verified in
code on 2026-08-03:

- `normalize_source_amount(kind, value)` requires costs to be entered negative
  and rejects a positive cost — the rejection §5 demands;
- `signed_amount(kind, amount)` renders every displayed amount signed;
- `finance_month_detail` uses both, so a manager types `-18676.90` and reads
  `-18676.90` back;
- `finance_csv` exports signed;
- `tests/test_finance_workbook.py` and `tests/test_positive_convention.py` lock
  both conventions in.

Migrating storage to signed values would rewrite tested design and every
existing row for **no user-visible change**. The question was open in the spec
and closed in the code; the spec was stale.

### 3 · Two workbook-shaped read surfaces

`finance_workbook` renders one period as the source draws it — projects across,
categories down, a subtotal per office, a grand total. `finance_project_year`
renders one project across twelve months. Both are read-only:
`finance_month_detail` stays the single write path.

Both compute from the **active category set**, never a coordinate range, and
both are office-scoped through `user_office_scope`. The workbook has no concept
of an office boundary; the product does, so a Velký Meder manager sees Velký
Meder columns.

### 4 · Import by management command, with mandatory column mapping

`import_hv_workbook` reads the `.xlsx` with `zipfile` and a little XML parsing.
No spreadsheet library enters the lockfile, so AGENTS.md §3.1 — ADR, release
cooldown, hash-pinned lock update — never applies. `features/profitability/workbook.py`
is deliberately minimal: values and formulas from the first sheet, nothing else.
Needing more is a reason to revisit the dependency decision, not to grow it into
a spreadsheet library.

A command rather than an upload form: the file is never stored, nothing is
exposed to the web, and the document-storage boundary stays out of the
conversation entirely.

**Mapping is required and never inferred.** Columns are matched to projects only
by explicit `--map COLUMN=CODE`; a populated column with no mapping is a hard
error, and a column that holds figures without being a project needs an explicit
`--ignore`. See the consequences below for why.

`FinanceCategory` gains the stable `key` §5 asked for. The bookkeeper CSV now
carries the full §8 column set, with `project_name` and `category_key` separate
from their codes, every row written at one width.

## Consequences

**The source workbook is wrong in three distinct ways, and now we can say so
precisely.** Reading the file directly found more than §7 records:

| Column | Workbook total | Its own cells sum to |
|---|---|---|
| B | `-18996.90` | `-19096.90` |
| C (Minit) | `-15087.17` | `-15187.17` |
| D, E, F | — | match exactly |

§7 attributes Minit's error to `C24=SUM(C3:C22)` stopping a row short. That is
incomplete: the cached value matches **neither** the short sum nor the correct
one, so the cell is stale as well as mis-ranged. Column B is wrong too and §7
does not mention it. And `B3` holds a headcount *inside* the range its own `SUM`
starts at — a third failure mode, and the reason summing categories rather than
coordinates is not a stylistic preference.

The importer reports each disagreement and imports the cells. The discrepancy is
the client's, and they should see it rather than have it quietly corrected.

**Two of nine projects cannot be named from the file.** Columns B and J carry a
headcount in their header row and no project name anywhere; §3 resolves them
from interview notes. A positional guess would file a whole month of costs
against the wrong project and look entirely normal afterwards. Hence the
mandatory mapping — the cost is a longer command line, and it is worth it.

**The period is still ambiguous.** The filename says `202510`, the worksheet says
`November 2025`, and §10 has carried that since 2026-07-20. `--period` is
required so the operator states which, rather than the importer picking.

**Not yet done.** No live accounting integration, no PDF or OCR path, and no
scheduled import — each run is a deliberate act. The grids are read surfaces;
bulk entry through the grid was considered and left out so there stays one write
path.

## Open, and still for Jober

- October or November 2025? (§10)
- Profitability ON globally or per project? `Project.financial_reporting_eligible`
  exists and is currently the per-project answer.
