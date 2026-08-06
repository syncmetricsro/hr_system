# ADR 0036: XlsxWriter for chart-bearing finance exports

Status: **Accepted — 2026-08-06.** Explicitly approved by the project owner;
implementation may proceed within the dependency and security boundary below.

Date drafted: 2026-08-06

## Context

Jober's finance module now has a monthly cross-project workbook and a yearly
cross-project workbook. Both are read-only views over the authoritative
`FinanceLineItem` records entered through the project-year grid. Jober also
needs a downloadable Excel workbook with the same yearly figures, a monthly
revenue/cost/net summary, and live Excel charts.

The export must contain two worksheets:

- **Year:** categories down, projects across, per-office subtotal rows and a
  grand total; costs are negative; header row and category column are frozen.
- **Months:** revenue, cost and net for each month, with a column chart of those
  three series and a bar chart of net by project.

The file is an export, not a second accounting system. All values are computed
by the Django application from the same office-scoped service used by the HTML
workbook. The spreadsheet contains **no formulas** and does not recalculate
business results.

Python's standard library can create the ZIP/XML parts of an XLSX file, but it
does not implement the Office Open XML workbook model. Hand-building a
chart-bearing workbook would require maintaining worksheet, drawing, chart,
relationship, content-type, style and shared-string XML as one internally
consistent package. A workbook can appear to generate successfully yet be
repaired or rejected by Excel because one relationship or range is wrong.
That is too fragile for a customer-facing financial export.

## Proposed decision

Adopt **XlsxWriter 3.2.9** as a narrowly scoped runtime dependency for the
Jober profitability export. Version 3.2.9 is the current stable release listed
on PyPI as of 2026-08-06; it was published on 2025-09-16 and is well beyond the
AGENTS.md approximately three-day cooldown window.

The package will be used only in `features/profitability/exports.py` to write
new `.xlsx` files. It will not read or modify uploaded workbooks, replace the
existing standard-library workbook importer, or enter `core/`.

The project owner explicitly approved this decision on 2026-08-06.

## AGENTS.md §3.1 approval-gate review

- **Why not standard library or Django:** neither provides an XLSX object
  model or native Excel chart generation. Implementing the required OOXML
  relationships and chart parts by hand would create a substantial,
  security-sensitive file-format maintenance burden for one export.
- **Maintainer and maturity:** XlsxWriter is maintained by John McNamara. The
  project has released continuously since 2013 and PyPI classifies it as
  Production/Stable. Its scope is deliberately focused on writing Excel 2007+
  XLSX files.
- **Transitive weight:** the project declares that it uses Python's standard
  libraries only. Version 3.2.9 has no required runtime dependencies, so the
  expected lockfile change is one pure-Python package and no transitive tree.
- **License:** BSD-2-Clause, compatible with use as an unmodified dependency.
- **Python/build compatibility:** Python 3.8+ is declared. PyPI publishes a
  universal `py3-none-any` wheel, so the production image should not need a
  compiler or an additional OS package.
- **Cooldown:** 3.2.9 was released on 2025-09-16, over ten months before this
  decision. It is not in the high-risk newly-published window.
- **Sources reviewed:** the
  [PyPI project page](https://pypi.org/project/XlsxWriter/), the
  [official documentation](https://xlsxwriter.readthedocs.io/), and the
  [official chart documentation](https://xlsxwriter.readthedocs.io/working_with_charts.html).

After approval, `xlsxwriter==3.2.9` will be added to both
`requirements/runtime.in` and `requirements/test.in`. Hash-pinned lockfiles
will be regenerated only through the repository's committed, digest-pinned
container workflow (`scripts/write_requirements_lock.py`). The lock diff must
contain XlsxWriter and no unexplained dependency drift, and installation must
continue to use hash enforcement.

## Security and data-handling boundary

XlsxWriter can emit formulas, hyperlinks, external references, macros and
embedded objects, but this feature will not use those capabilities.

- Construct a new workbook in memory and return it as a download; never accept
  a path or workbook content from the request.
- Set `strings_to_formulas=False` and `strings_to_urls=False` so project,
  office and category labels remain plain text even if they begin with `=` or
  resemble a URL.
- Do not call formula, macro, external-link, image or embedded-object APIs.
- Write app-computed monetary values as spreadsheet numbers with explicit
  currency formats. The authoritative values remain Django `Decimal` data;
  the export is a presentation artifact, not a persistence or calculation
  surface.
- Reuse the existing `Action.EXPORT_APPROVED` authorization and
  `user_office_scope` restrictions. A primary-key scope mismatch must fail
  with 403 where applicable.
- Use fixed, translated worksheet names and a server-generated filename. No
  user value controls a filesystem path or response header.
- Apply reasonable row/column bounds and keep generation synchronous only
  while the current, bounded finance dataset remains within the established
  request limits. Revisit background generation through a separate decision
  if real usage outgrows that boundary.

## Alternatives considered

### Hand-written OOXML with `zipfile` and `xml.etree.ElementTree`

Rejected. It avoids a dependency but makes this repository responsible for a
large, interdependent subset of the OOXML specification, especially chart and
drawing relationships. The existing importer only reads a tightly constrained
subset and does not make robust chart-bearing generation cheap or safe.

### openpyxl

Rejected for this write-only use case. It has a broader read/write object model
and a required dependency, while XlsxWriter has no runtime dependencies and a
focused, mature chart-writing API. Nothing in the requested export requires
editing an existing workbook.

### CSV only

Rejected as the sole export. The existing CSV remains useful, but CSV cannot
represent two worksheets, formatting, frozen panes or live charts.

### Server-rendered PDF

Rejected. A PDF is not the editable, spreadsheet-native deliverable Jober
requested and cannot provide live Excel charts.

## Consequences

- Runtime and test dependency manifests gained exactly `xlsxwriter==3.2.9`.
  Both hash-pinned lockfiles were regenerated in the digest-pinned Python
  image; their package diff adds only XlsxWriter. Already-vetted `cffi==2.1.0`
  and `packaging==26.2` were made explicit input pins after the first resolver
  pass attempted unrelated upgrades.
- The profitability feature gains one office-scoped, permission-gated XLSX
  response and focused unit/browser coverage. CorvinumEU remains unchanged
  because profitability routes are feature-gated off there.
- Generated workbooks can be opened in Excel/LibreOffice with two worksheets,
  formatting, frozen panes and native charts while remaining a formula-free
  snapshot of application data.
- The package becomes part of the runtime supply chain and must be reviewed and
  deliberately upgraded like every other pinned dependency.
- No migration, database model, import behavior, API or deployment change is
  introduced by the dependency decision itself.

## Approval record

Approved by the project owner on 2026-08-06 before any dependency manifest,
lockfile or application-code change was made.
