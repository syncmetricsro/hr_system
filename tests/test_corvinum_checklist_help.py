"""The nine activation checklist items and the help text that defines them.

Two things can silently break here, and both have the same symptom — the office
sees English, or sees nothing:

1. **The seed and the msgid registry drift.** `scripts/compile_messages.sh`
   ignores `demo` paths, so the seed's own strings are never extracted; they are
   registered by hand in `clients/corvinum_eu/catalog_i18n.py`. `db_trans` looks
   the string up verbatim, so one edited comma in one of the two places falls
   through to English with nothing failing.
2. **The seed creates but does not repair.** Every demo and staging database
   already holds all nine rows, so `get_or_create(defaults=…)` would never
   deliver help text to any of them.

The first test reads both files as source text rather than importing them: the
seed module imports the whole CorvinumEU pay stack, which Jober does not
install, and this check is worth running in both lanes.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest
from django.conf import settings
from django.core.management import call_command, get_commands
from django.utils import translation


REPO = Path(__file__).resolve().parent.parent
SEED = REPO / "clients/corvinum_eu/demo/management/commands/seed_corvinum_demo.py"
CATALOG = REPO / "clients/corvinum_eu/catalog_i18n.py"


def _assigned_literal(path: Path, name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == name:
            return node.value
    raise AssertionError(f"{name} is no longer assigned in {path.name}")


def _seed_items():
    return ast.literal_eval(_assigned_literal(SEED, "ACTIVATION_ITEMS"))


def _catalog_strings(name):
    # Each entry is `_("…")`; take the single argument of every call.
    return [
        ast.literal_eval(element.args[0])
        for element in _assigned_literal(CATALOG, name).elts
    ]


def test_every_seeded_label_and_help_string_is_registered_for_translation():
    items = _seed_items()
    labels = _catalog_strings("SEEDED_CHECKLIST_LABELS")
    helps = _catalog_strings("SEEDED_CHECKLIST_HELP")

    assert len(items) == len(labels) == len(helps), (
        "the seed and the msgid registry have different lengths: "
        f"{len(items)} items, {len(labels)} labels, {len(helps)} help strings"
    )
    for (label, _critical, help_text), registered_label, registered_help in zip(
        items, labels, helps
    ):
        assert label == registered_label
        # Verbatim: db_trans is a dictionary lookup, not a fuzzy match.
        assert help_text == registered_help, f"help text drifted for {label!r}"


def test_every_checklist_item_says_something_of_its_own():
    """Nine identical sentences is the bug this feature exists to fix."""
    helps = [help_text for _label, _critical, help_text in _seed_items()]

    assert all(helps), "a seeded item was left without help text"
    assert len(set(helps)) == len(helps), "two seeded items share the same help text"


@pytest.mark.skipif(
    "seed_corvinum_demo" not in get_commands(),
    reason="the CorvinumEU demo app is not installed for this client",
)
@pytest.mark.django_db
def test_reseeding_fills_in_help_text_on_rows_that_already_exist():
    """The staging case: the rows are there, only the help text is missing."""
    from features.checklists.models import ChecklistItemTemplate, ChecklistTemplate

    template = ChecklistTemplate.objects.create(name="Global activation")
    stale = ChecklistItemTemplate.objects.create(
        template=template, label="Contract signed", critical=True, order=6
    )
    assert stale.help_text == ""

    call_command("seed_corvinum_demo")

    stale.refresh_from_db()
    assert stale.help_text, "an already-seeded item never received its help text"
    assert not ChecklistItemTemplate.objects.filter(
        template=template, help_text=""
    ).exists()


# --- what the office actually reads on hover -------------------------------
#
# These render the panel, which reverses the toggle URL. That route is only
# mounted for a client with the checklists flag on, so they belong here rather
# than in the shared module, where they passed or failed depending on which
# test had last reloaded the URLConf.

pytestmark_reason = "the checklists feature is off for this client"


@pytest.fixture
def documented_template(db):
    from features.checklists.models import ChecklistItemTemplate, ChecklistTemplate

    template = ChecklistTemplate.objects.create(name="Global activation")
    ChecklistItemTemplate.objects.create(
        template=template,
        label="Identity document verified",
        help_text="You have seen the ID card or passport yourself.",
        critical=True,
        order=1,
    )
    ChecklistItemTemplate.objects.create(
        template=template,
        label="Welcome call made",
        help_text="Somebody has called to confirm the start date.",
        critical=False,
        order=2,
    )
    return template


def _rendered_panel(user, person):
    """Render the panel partial directly.

    Going through the view would drag in the context processors, which want a
    session the RequestFactory does not build. The panel provider is the thing
    under test either way.
    """
    from django.template.loader import render_to_string
    from django.test import RequestFactory

    from features.checklists.panels import checklist_panel

    request = RequestFactory().get(f"/people/{person.pk}/")
    request.user = user
    return render_to_string(
        "panels/checklists_items.html", {"panel": checklist_panel(request, person)}
    )


@pytest.fixture
def _people(django_user_model):
    from core.people.models import Person

    manager = django_user_model.objects.create_user(
        email="cl-help-manager@demo.corvinum.test", password="x", role="manager"
    )
    person = Person.objects.create(first_name="Fictional", last_name="Candidate")
    return manager, person


@pytest.mark.skipif(
    not settings.FEATURE_FLAGS.get("checklists"), reason=pytestmark_reason
)
@pytest.mark.django_db
def test_each_checklist_item_offers_its_own_tooltip(documented_template, _people):
    """Nine identical bubbles down a list is the same as no help at all."""
    manager, person = _people

    with translation.override("en"):
        body = _rendered_panel(manager, person)

    assert "You have seen the ID card or passport yourself." in body
    assert "Somebody has called to confirm the start date." in body

    tooltips = re.findall(r'data-tooltip="([^"]+)"', body)
    assert len(tooltips) >= 2
    assert len(set(tooltips)) == len(tooltips), tooltips

    headings = re.findall(r'data-tooltip-heading="([^"]+)"', body)
    assert "Identity document verified" in headings
    assert "Welcome call made" in headings


@pytest.mark.skipif(
    not settings.FEATURE_FLAGS.get("checklists"), reason=pytestmark_reason
)
@pytest.mark.django_db
def test_an_item_without_help_text_still_explains_the_tick(_people):
    """An operator-added item has no seeded help; it must not hover blank."""
    from features.checklists.models import ChecklistItemTemplate, ChecklistTemplate

    manager, person = _people
    template = ChecklistTemplate.objects.create(name="Global activation")
    ChecklistItemTemplate.objects.create(
        template=template, label="Something the office added", critical=False, order=1
    )

    with translation.override("en"):
        body = _rendered_panel(manager, person)

    assert "Records that you completed this item" in body
    assert 'data-tooltip=""' not in body
