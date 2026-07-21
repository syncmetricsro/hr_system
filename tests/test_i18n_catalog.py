from __future__ import annotations

import pytest
from django.utils import translation
from django.utils.translation import gettext

# Regression coverage for the hu/django.po fuzzy-match cleanup: these msgids
# previously carried #, fuzzy translations paired with unrelated old strings
# by an automated msgmerge run (see CLAUDE.md's "msgmerge fuzzy matches" note).
# Shared logistics/people catalog content — not Jober- or Corvinum-specific.
MUST_FIX_HU = {
    "Date of birth cannot be in the future.": "A születési dátum nem lehet jövőbeli.",
    "Approaching age 18": "Hamarosan 18 éves",
    "occurred on": "mozgás dátuma",
    "receipt line": "bevételezési sor",
    "Only %(available)s units are available in stock.": (
        "Csak %(available)s egység érhető el a készleten."
    ),
    "Stock receipt recorded.": "A készletbevételezés rögzítve.",
    "Stock adjustment recorded.": "A készletkorrekció rögzítve.",
    "Review the stock adjustment and try again.": (
        "Ellenőrizze a készletkorrekció adatait, majd próbálja újra."
    ),
    "Invalid equipment issue.": "Érvénytelen felszerelés-kiadás.",
    "No cost period recorded.": "Nincs rögzített költségidőszak.",
    "Units available": "Elérhető egységek",
    "Damaged or retired": "Sérült vagy selejtezett",
}


@pytest.mark.parametrize("msgid,expected", sorted(MUST_FIX_HU.items()))
def test_hu_catalog_corrected_translation(msgid, expected):
    with translation.override("hu"):
        assert gettext(msgid) == expected


def test_hu_equipment_stock_lot_sibling_fields_are_distinguishable():
    """initial/remaining quantity and value previously collapsed to the same
    generic Hungarian word, making sibling fields on EquipmentStockLot
    indistinguishable in the UI."""
    with translation.override("hu"):
        assert gettext("initial quantity") != gettext("remaining quantity")
        assert gettext("initial value") != gettext("remaining value")


def test_hu_panel_help_text_strings_are_translated():
    with translation.override("hu"):
        assert gettext(
            "Items marked critical must all be ticked before this person can be activated."
        )
        assert gettext(
            "Cash advances and deductions against this person's pay, settled through the "
            "weekly ledger cycle."
        )
