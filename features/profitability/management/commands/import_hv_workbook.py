"""Import one month of Jober's HV workbook into stored line items.

A management command rather than an upload form on purpose: the file is never
stored, nothing is exposed to the web, and the operator has to mean it. It also
keeps the whole document-storage boundary out of the conversation.

**Column mapping is required and is never guessed.** The source workbook cannot
name two of its own nine projects — columns B and J carry a headcount in their
header row and no project name anywhere. `Jober_Finance_Specs` §3 resolves them
from interview notes, not from the file. Guessing here would file an entire
month of costs against the wrong project and look completely normal afterwards,
so a populated column with no mapping is a hard error.

**Cached totals are read but never trusted.** The workbook's own row-24 and
row-32 sums disagree with its cells in more than one column:

* `C24` is `SUM(C3:C22)`, stopping a row short of the cost block (§7);
* the cached values in columns B and C match neither `SUM(:22)` nor `SUM(:23)`,
  so they are stale as well as mis-ranged;
* `B3` holds a headcount *inside* the summed cost block.

Every total is recomputed from the cells. Where the recomputed figure disagrees
with the workbook's, the command reports it rather than silently overriding: the
discrepancy is the client's, and they should see it.
"""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.projects.models import Project
from features.profitability.models import (
    FinanceCategory,
    FinanceCategoryKind,
    FinancialMonth,
)
from features.profitability.services import (
    FinanceError,
    normalize_source_amount,
    set_line_item,
)
from features.profitability.workbook import (
    WorkbookError,
    column_index,
    quantize,
    read_sheet,
)

#: Source label (lower-cased) -> `FinanceCategory.key`. The labels reproduce the
#: workbook exactly; the mapping to English categories is `Jober_Finance_Specs`
#: §4. Both label columns are consulted because neither is complete on its own:
#: the left block has no label for the gross-wage row, the right block does.
SOURCE_LABELS = {
    "hrubá výplata bez zrážok": "gross_wage",
    "szco": "szco",
    "odvody": "levies",
    "vodič": "driver",
    "skoda": "damage_cost",
    "škoda": "damage_cost",
    "vzv oktatas": "forklift_training",
    "vzv jogsi": "forklift_licence",
    "ubytovanie": "accommodation_cost",
    "poistenie": "insurance",
    "lekarske": "medical",
    "koordinatorok": "coordinators",
    "leasingek": "leasing",
    "benzin": "fuel",
    "myto": "toll",
    "faktoring": "factoring",
    "iroda": "office",
    "toborzas": "recruitment",
    "hr": "hr",
    "oblecenie": "clothing",
    "iné náklady mimoriadne": "other_extraordinary",
    "faktúry": "invoices",
    "zrážky prijaté od zam": "worker_deductions",
    "obed": "meals",
    "ubytovňa": "accommodation_revenue",
}

#: Rows whose label is a total the workbook computed. Never imported.
TOTAL_LABELS = {"celkové náklady", "celkové výnosy", "summ ds", "summ spolu"}

#: `škoda` appears twice — once as a cost and once as recovered revenue. The
#: revenue block starts after the cost total, so the row number disambiguates.
LABEL_COLUMNS = ("A", "I")


class Command(BaseCommand):
    help = "Import one month of an HV workbook. Requires an explicit column map."

    def add_arguments(self, parser):
        parser.add_argument("path", help="Path to the .xlsx workbook")
        parser.add_argument(
            "--period",
            required=True,
            help="YYYY-MM this sheet covers. Required because the source "
            "filename and its worksheet name disagree (spec §10).",
        )
        parser.add_argument(
            "--map",
            action="append",
            default=[],
            metavar="COLUMN=PROJECT_CODE",
            help="Spreadsheet column to project code, e.g. --map C=MINIT. "
            "Every populated column needs one; the workbook does not name "
            "all of its own projects.",
        )
        parser.add_argument(
            "--ignore",
            action="append",
            default=[],
            metavar="COLUMN",
            help="A column that holds figures but is not a project, e.g. "
            "--ignore G. The source keeps headcounts in cells that sit inside "
            "category rows, so they look like data. Ignoring is a decision the "
            "operator states, not something the importer infers.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse, recompute and report without writing anything.",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.exists():
            raise CommandError(f"{path} does not exist.")

        year, month = self._period(options["period"])
        try:
            cells = read_sheet(path)
        except WorkbookError as exc:
            raise CommandError(str(exc)) from exc

        rows = self._category_rows(cells)
        if not rows:
            raise CommandError(
                "No recognisable category labels found. Is this an HV workbook?"
            )

        mapping = self._mapping(options["map"])
        ignored = {c.strip().upper() for c in options["ignore"]}
        overlap = ignored & set(mapping)
        if overlap:
            raise CommandError(
                f"Column(s) both mapped and ignored: {', '.join(sorted(overlap))}."
            )
        populated = self._populated_columns(cells, rows) - ignored
        unmapped = sorted(populated - set(mapping), key=column_index)
        if unmapped:
            raise CommandError(
                "These columns hold figures but have no --map entry: "
                f"{', '.join(unmapped)}. The workbook does not name every "
                "project it contains, so the mapping cannot be guessed — see "
                "Jober_Finance_Specs §3. If a column is not a project (the "
                "source keeps headcounts among the figures), pass --ignore."
            )

        projects = self._projects(mapping)
        categories = {c.key: c for c in FinanceCategory.objects.exclude(key="")}
        missing = sorted(set(rows.values()) - set(categories))
        if missing:
            raise CommandError(
                f"No FinanceCategory for keys: {', '.join(missing)}. "
                "Run `seed_finance` first."
            )

        written, discrepancies = self._import(
            cells,
            rows,
            mapping,
            projects,
            categories,
            year,
            month,
            dry_run=options["dry_run"],
        )

        verb = "Would import" if options["dry_run"] else "Imported"
        self.stdout.write(
            self.style.SUCCESS(
                f"{verb} {written} line item(s) for {year}-{month:02d} "
                f"across {len(mapping)} project(s)."
            )
        )
        for line in discrepancies:
            self.stdout.write(self.style.WARNING(line))

    # -- parsing ------------------------------------------------------------

    def _period(self, raw: str) -> tuple[int, int]:
        match = re.fullmatch(r"(\d{4})-(\d{1,2})", raw.strip())
        if not match:
            raise CommandError("--period must look like YYYY-MM.")
        year, month = int(match.group(1)), int(match.group(2))
        if not 1 <= month <= 12:
            raise CommandError("--period month must be 1-12.")
        return year, month

    def _mapping(self, entries) -> dict[str, str]:
        mapping = {}
        for entry in entries:
            if "=" not in entry:
                raise CommandError(f"--map expects COLUMN=PROJECT_CODE, got {entry!r}.")
            column, code = entry.split("=", 1)
            column = column.strip().upper()
            if not re.fullmatch(r"[A-Z]+", column):
                raise CommandError(f"{column!r} is not a spreadsheet column.")
            mapping[column] = code.strip()
        return mapping

    def _category_rows(self, cells) -> dict[int, str]:
        """Row number -> category key, read from whichever label column has it."""
        rows: dict[int, str] = {}
        for (column, row), cell in cells.items():
            if column not in LABEL_COLUMNS or not cell.text:
                continue
            label = cell.text.strip().lower()
            if label in TOTAL_LABELS:
                continue
            key = SOURCE_LABELS.get(label)
            if key:
                rows[row] = key
        # `škoda` is both a cost and a revenue row. Anything after the cost
        # total belongs to the revenue block, so re-point the later one.
        cost_total_row = self._total_row(cells, "celkové náklady")
        if cost_total_row is not None:
            for row, key in list(rows.items()):
                if row > cost_total_row and key == "damage_cost":
                    rows[row] = "damage_recovered"
        return rows

    def _total_row(self, cells, label: str) -> int | None:
        for (column, row), cell in cells.items():
            if column in LABEL_COLUMNS and cell.text.strip().lower() == label:
                return row
        return None

    def _populated_columns(self, cells, rows) -> set[str]:
        return {
            column
            for (column, row), cell in cells.items()
            if row in rows and column not in LABEL_COLUMNS and cell.number is not None
        }

    def _projects(self, mapping) -> dict[str, Project]:
        by_code = {p.code: p for p in Project.objects.filter(code__in=mapping.values())}
        unknown = sorted(set(mapping.values()) - set(by_code))
        if unknown:
            raise CommandError(f"No project with code: {', '.join(unknown)}.")
        return {column: by_code[code] for column, code in mapping.items()}

    # -- writing ------------------------------------------------------------

    def _import(
        self, cells, rows, mapping, projects, categories, year, month, *, dry_run
    ):
        written, discrepancies = 0, []
        for column in sorted(mapping, key=column_index):
            project = projects[column]
            recomputed_cost = Decimal("0")
            recomputed_revenue = Decimal("0")
            values = []
            for row, key in sorted(rows.items()):
                cell = cells.get((column, row))
                if cell is None or cell.number is None:
                    continue
                category = categories[key]
                signed = quantize(cell.number)
                # The workbook's own convention is the input convention: costs
                # negative, revenues positive. `normalize_source_amount` both
                # validates that and returns the storage magnitude, so a source
                # cell with the wrong sign fails the import instead of silently
                # inverting a project's result.
                try:
                    magnitude = normalize_source_amount(category.kind, signed)
                except FinanceError as exc:
                    raise CommandError(
                        f"column {column} row {row} ({category.key}): {exc}"
                    ) from exc
                values.append((category, magnitude))
                if category.kind == FinanceCategoryKind.COST:
                    recomputed_cost += signed
                else:
                    recomputed_revenue += signed

            discrepancies.extend(
                self._compare(cells, column, recomputed_cost, recomputed_revenue)
            )

            if dry_run:
                written += len(values)
                continue

            with transaction.atomic():
                financial_month, _created = FinancialMonth.objects.get_or_create(
                    project=project, year=year, month=month
                )
                if financial_month.is_locked:
                    raise CommandError(
                        f"{project.code} {year}-{month:02d} is locked. "
                        "Reopen it deliberately before re-importing."
                    )
                for category, magnitude in values:
                    try:
                        set_line_item(financial_month, category, magnitude)
                    except FinanceError as exc:
                        raise CommandError(
                            f"{project.code} {category.key}: {exc}"
                        ) from exc
                    written += 1
        return written, discrepancies

    def _compare(self, cells, column, cost, revenue):
        """Report where the workbook's own totals disagree with its cells."""
        notes = []
        for label, recomputed, total_label in (
            ("costs", cost, "celkové náklady"),
            ("revenues", revenue, "celkové výnosy"),
        ):
            row = self._total_row(cells, total_label)
            if row is None:
                continue
            cached = cells.get((column, row))
            if cached is None or cached.number is None:
                continue
            if quantize(cached.number) != quantize(recomputed):
                notes.append(
                    f"  column {column}: workbook {label} total "
                    f"{quantize(cached.number)} but its own cells sum to "
                    f"{quantize(recomputed)}. Imported the cells."
                )
        return notes
