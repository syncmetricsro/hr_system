from __future__ import annotations

import pytest
from django.urls import reverse

from apps.accounts.permissions import Action, can
from apps.blacklist.models import (
    BlacklistCaseStatus,
    BlacklistCategory,
    MatchFingerprint,
)
from apps.blacklist.services import (
    BlacklistError,
    check_match,
    compute_fingerprint,
    decide_case,
    has_open_case,
    propose_case,
    purge_expired,
    remove_case,
)
from apps.people.models import LifecycleStatus, Person
from apps.projects.models import Project
from apps.projects.services import WorkflowError, activate_on_project

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup(django_user_model):
    manager = django_user_model.objects.create_user(email="m@demo.jober.test", password="x", role="manager")
    coord = django_user_model.objects.create_user(email="c@demo.jober.test", password="x", role="coordinator")
    person = Person.objects.create(first_name="A", last_name="B")
    return manager, coord, person


# --- hashing / matching --------------------------------------------------------

def test_fingerprint_is_deterministic_and_keyed(settings):
    settings.BLACKLIST_HMAC_KEYS = ["key-one"]
    h1, v1 = compute_fingerprint("SK-12345")
    h2, _ = compute_fingerprint("sk 12345")  # normalization: case/format-insensitive
    assert h1 == h2 and v1 == 0
    settings.BLACKLIST_HMAC_KEYS = ["key-two"]
    h3, _ = compute_fingerprint("SK-12345")
    assert h3 != h1  # different key -> different hash


def test_raw_identifier_is_never_stored(setup):
    _m, _c, person = setup
    propose_case(person, identifier="RAW-999", actor=None)
    fp = MatchFingerprint.objects.get()
    assert fp.hmac != "RAW999" and "RAW" not in fp.hmac
    # No field on the row holds the raw value.
    for value in vars(fp).values():
        assert "RAW-999" not in str(value)


def test_check_match_active_and_company_wide(setup, settings):
    settings.BLACKLIST_MATCHING_ENABLED = True
    manager, _c, person = setup
    case = propose_case(person, identifier="ID-1", actor=manager)
    assert not check_match("ID-1").exists()          # inactive until approved
    decide_case(case, "approve", actor=manager)
    assert check_match("ID-1").exists()              # active after approval
    assert not check_match("OTHER").exists()


def test_matching_disabled_returns_empty(setup, settings):
    manager, _c, person = setup
    decide_case(propose_case(person, identifier="ID-1", actor=manager), "approve", actor=manager)
    settings.BLACKLIST_MATCHING_ENABLED = False
    assert not check_match("ID-1").exists()


# --- decision lifecycle --------------------------------------------------------

def test_approve_blacklists_and_activates_fingerprint(setup):
    manager, _c, person = setup
    case = propose_case(person, reason="fraud", identifier="ID-1", actor=manager)
    assert person.lifecycle_status != LifecycleStatus.BLACKLISTED  # proposed != blacklisted
    decide_case(case, "approve", actor=manager)
    person.refresh_from_db()
    case.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.BLACKLISTED
    assert case.status == BlacklistCaseStatus.APPROVED
    assert case.fingerprints.filter(is_active=True).exists()


def test_reject_leaves_lifecycle_unchanged(setup):
    manager, _c, person = setup
    case = propose_case(person, actor=manager)
    decide_case(case, "reject", actor=manager)
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.AVAILABLE
    assert not has_open_case(person)


def test_remove_reverts_to_available_and_revokes(setup):
    manager, _c, person = setup
    case = decide_case(propose_case(person, identifier="ID-1", actor=manager), "approve", actor=manager)
    remove_case(case, actor=manager, reason="appeal upheld")
    person.refresh_from_db()
    case.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.AVAILABLE
    assert case.status == BlacklistCaseStatus.REMOVED
    assert not case.fingerprints.filter(is_active=True).exists()


def test_decide_requires_proposed(setup):
    manager, _c, person = setup
    case = decide_case(propose_case(person, actor=manager), "approve", actor=manager)
    with pytest.raises(BlacklistError):
        decide_case(case, "reject", actor=manager)  # already approved


# --- hard gate -----------------------------------------------------------------

def test_open_case_blocks_activation(setup):
    manager, coord, person = setup
    project = Project.objects.create(name="DHL", code="DHLBA")
    propose_case(person, actor=manager)  # open (proposed)
    with pytest.raises(WorkflowError):
        activate_on_project(person, project, actor=coord)


# --- intake matching via the create view --------------------------------------

def test_person_create_flags_match_without_blocking(client, setup, settings):
    settings.BLACKLIST_MATCHING_ENABLED = True
    manager, _c, existing = setup
    decide_case(propose_case(existing, identifier="MATCH-1", actor=manager), "approve", actor=manager)
    recruiter = client
    from django.contrib.auth import get_user_model
    rec = get_user_model().objects.create_user(email="r@demo.jober.test", password="x", role="recruiter")
    recruiter.force_login(rec)
    resp = recruiter.post(reverse("person_create"), {
        "first_name": "New", "last_name": "Person", "identifier": "MATCH-1",
        "identifier_type": "national_id",
    })
    assert resp.status_code == 302
    new = Person.objects.get(first_name="New")            # created, not blocked
    assert has_open_case(new)                              # proposed case for review


# --- RBAC ----------------------------------------------------------------------

def test_rbac(setup, django_user_model):
    manager, coord, _p = setup
    recruiter = django_user_model.objects.create_user(email="r2@demo.jober.test", password="x", role="recruiter")
    assert can(manager, Action.BLACKLIST_DECIDE) and not can(coord, Action.BLACKLIST_DECIDE)
    assert can(coord, Action.BLACKLIST_PROPOSE) and can(manager, Action.BLACKLIST_PROPOSE)
    assert not can(recruiter, Action.BLACKLIST_PROPOSE)
    # Reason visible to coordinator + manager, not recruiter.
    assert can(coord, Action.BLACKLIST_VIEW_REASON) and can(manager, Action.BLACKLIST_VIEW_REASON)
    assert not can(recruiter, Action.BLACKLIST_VIEW_REASON)


def test_queue_view_gated(client, setup):
    manager, coord, _p = setup
    url = reverse("blacklist_queue")
    client.force_login(coord)
    assert client.get(url).status_code == 403
    client.force_login(manager)
    assert client.get(url).status_code == 200


# --- retention + seed ----------------------------------------------------------

def test_purge_expired_drops_expired(setup):
    manager, _c, person = setup
    case = propose_case(person, identifier="ID-1", actor=manager)
    fp = case.fingerprints.get()
    from datetime import date
    fp.expires_at = date(2000, 1, 1)
    fp.save(update_fields=["expires_at"])
    assert purge_expired() == 1
    assert not MatchFingerprint.objects.filter(pk=fp.pk).exists()


def test_seed_categories_present():
    assert BlacklistCategory.objects.filter(label="Fraud / dishonesty").exists()
    assert BlacklistCategory.objects.count() >= 5
