"""Jober's activation checklist: the gate, and the seed that has to survive it.

Turning the feature on for Jober is one flag, and the flag is not the risk. The
risk is that `seed_people` **activates** the seeded working people, and
`activate_on_project` runs every registered activation check — so the moment a
template with critical items exists, the seed refuses its own activation with
`Activation blocked by open checklist items`. CorvinumEU never met this because
its seed activates nobody.

That failure has no partial form: seeding stops, and what a demo shows the next
morning is an empty database. So it is tested from the seed inward rather than
from the service outward.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from django.core.management import call_command, get_commands
from django.utils import translation

from core.people.models import LifecycleStatus, Person
from core.projects.models import Project
from core.projects.services import WorkflowError, activate_on_project
from features.checklists.models import ChecklistItemTemplate, ChecklistTemplate
from features.checklists.services import ensure_person_checklist, set_item_state


REPO = Path(__file__).resolve().parent.parent
SEED = REPO / "clients/jober/demo/checklist.py"
CATALOG = REPO / "clients/jober/catalog_i18n.py"

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]

FLAGS_ON = {"checklists": True}


def _assigned_literal(path: Path, name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == name:
            return node.value
    raise AssertionError(f"{name} is no longer assigned in {path.name}")


def _seed_items():
    return ast.literal_eval(_assigned_literal(SEED, "ACTIVATION_ITEMS"))


def _catalog_strings(name):
    return [
        ast.literal_eval(element.args[0])
        for element in _assigned_literal(CATALOG, name).elts
    ]


# --- the seed against its own gate -----------------------------------------


@pytest.mark.skipif(
    "seed_people" not in get_commands(), reason="the Jober demo app is not installed"
)
def test_the_demo_seed_survives_the_activation_gate(settings):
    """The whole feature, from the angle that can empty a demo database."""
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, **FLAGS_ON}

    call_command("seed_demo")
    call_command("seed_people")

    assert ChecklistItemTemplate.objects.filter(critical=True).count() == 8
    working = Person.objects.filter(lifecycle_status=LifecycleStatus.WORKING)
    assert working.exists(), "the seed activated nobody, so the gate is untested"
    for person in working:
        open_critical = [
            item
            for item in ensure_person_checklist(person)
            if item.item_template.critical and not item.done
        ]
        assert not open_critical, f"{person} was activated with items still open"


@pytest.mark.skipif(
    "seed_people" not in get_commands(), reason="the Jober demo app is not installed"
)
def test_the_seeded_ticks_carry_who_did_them(settings):
    """Ticked through the service, not flipped in the database: the demo has to
    show a real approval identity beside each item."""
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, **FLAGS_ON}

    call_command("seed_demo")
    call_command("seed_people")

    person = Person.objects.filter(lifecycle_status=LifecycleStatus.WORKING).first()
    done = [i for i in ensure_person_checklist(person) if i.done]
    assert done and all(i.done_by is not None and i.done_at for i in done)


# --- the gate itself, in the Jober lane ------------------------------------


def test_an_open_critical_item_blocks_activation_and_names_it(settings):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, **FLAGS_ON}
    template = ChecklistTemplate.objects.create(name="Global activation")
    ChecklistItemTemplate.objects.create(
        template=template, label="Contract signed", critical=True, order=1
    )
    person = Person.objects.create(first_name="Fictional", last_name="Candidate")
    project = Project.objects.create(name="DHL", code="DHLJC", is_active=True)

    with (
        translation.override("en"),
        pytest.raises(WorkflowError, match="Contract signed"),
    ):
        activate_on_project(person, project)

    person.refresh_from_db()
    assert person.lifecycle_status != LifecycleStatus.WORKING


def test_a_non_critical_item_does_not_block(settings):
    """Welcome call made is deliberately not critical; it must warn, not stop."""
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, **FLAGS_ON}
    template = ChecklistTemplate.objects.create(name="Global activation")
    ChecklistItemTemplate.objects.create(
        template=template, label="Welcome call made", critical=False, order=1
    )
    person = Person.objects.create(first_name="Fictional", last_name="Candidate")
    project = Project.objects.create(name="DHL", code="DHLJC", is_active=True)

    activate_on_project(person, project)

    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.WORKING


def test_ticking_every_critical_item_clears_the_gate(settings):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, **FLAGS_ON}
    template = ChecklistTemplate.objects.create(name="Global activation")
    ChecklistItemTemplate.objects.create(
        template=template, label="Contract signed", critical=True, order=1
    )
    person = Person.objects.create(first_name="Fictional", last_name="Candidate")
    project = Project.objects.create(name="DHL", code="DHLJC", is_active=True)
    for item in ensure_person_checklist(person):
        set_item_state(item, done=True)

    activate_on_project(person, project)

    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.WORKING


# --- the seed and the msgid registry ---------------------------------------


def test_every_seeded_label_and_help_string_is_registered_for_translation():
    items = _seed_items()
    labels = _catalog_strings("SEEDED_CHECKLIST_LABELS")
    helps = _catalog_strings("SEEDED_CHECKLIST_HELP")

    assert len(items) == len(labels) == len(helps)
    for (label, _critical, help_text), registered_label, registered_help in zip(
        items, labels, helps
    ):
        assert label == registered_label
        # Verbatim: db_trans is a dictionary lookup, not a fuzzy match.
        assert help_text == registered_help, f"help text drifted for {label!r}"


def test_every_item_says_something_of_its_own():
    helps = [help_text for _label, _critical, help_text in _seed_items()]

    assert all(helps), "a seeded item was left without help text"
    assert len(set(helps)) == len(helps), "two seeded items share the same help text"


def test_jober_and_corvinum_still_share_their_wording():
    """Not a rule, a tripwire.

    The two lists are separate so either office can reword its own without
    touching the other. Today they are identical, which is why this slice needed
    no new translations at all. When they do diverge, this test is the reminder
    that the changed strings are new msgids and need sk, hu and uk before they
    ship - not a reason to revert the change.
    """
    corvinum = (
        REPO / "clients/corvinum_eu/demo/management/commands/seed_corvinum_demo.py"
    )
    theirs = ast.literal_eval(_assigned_literal(corvinum, "ACTIVATION_ITEMS"))

    assert _seed_items() == theirs, (
        "Jober and CorvinumEU checklists have diverged - translate the changed "
        "strings into sk/hu/uk, then update this test to allow the difference"
    )
