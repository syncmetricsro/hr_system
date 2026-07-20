from __future__ import annotations

from datetime import date

import pytest
from django.urls import reverse

from core.accounts.permissions import Action, can
from features.blacklist.models import (
    BlacklistCaseStatus,
    BlacklistCategory,
    IdentifierType,
    MatchFingerprint,
)
from features.blacklist.services import (
    BlacklistError,
    _normalize,
    check_match,
    check_matches,
    compute_composite_identifier,
    compute_fingerprint,
    decide_case,
    has_open_case,
    propose_case,
    purge_expired,
    remove_case,
)
from core.people.models import LifecycleStatus, Person
from core.projects.models import Project
from core.projects.services import WorkflowError, activate_on_project

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


def test_normalize_folds_diacritics_and_keeps_ascii_stable():
    # Diacritics transliterate instead of being deleted ("Kováč" must not
    # collapse to "KOV"); NFKD-resistant letters go through the fold table.
    assert _normalize("Kováč") == "KOVAC"
    assert _normalize("Łukasz") == "LUKASZ"
    assert _normalize("Groß") == "GROSS"
    assert _normalize("Kováčová-Nagy") == "KOVACOVANAGY"
    # ASCII-alphanumeric identifiers are untouched, so existing stored ID
    # fingerprints keep matching across the normalizer change.
    assert _normalize("SK-12345") == "SK12345"
    assert _normalize("sk 12345") == "SK12345"
    # Non-Latin scripts strip to empty rather than hashing garbage.
    assert _normalize("Олена") == ""


def test_composite_identifier_canonical_and_order_insensitive():
    dob = date(1990, 1, 15)
    canonical = compute_composite_identifier("Anna", "Kováčová", dob, "Nováková")
    assert canonical == "v1|ANNA|KOVACOVA|1990-01-15|NOVAKOVA"
    # First/last swapped and diacritic-free spellings yield the same string.
    assert compute_composite_identifier("Kovacova", "Anna", dob, "Novakova") == canonical
    # Missing or non-normalizable components mean no composite at all.
    assert compute_composite_identifier("", "", dob, "Nováková") is None
    assert compute_composite_identifier("Anna", "Kováčová", None, "Nováková") is None
    assert compute_composite_identifier("Anna", "Kováčová", dob, "") is None
    assert compute_composite_identifier("Олена", "Ковач", dob, "Новак") is None


def test_check_matches_requires_type_and_hash(setup, settings):
    settings.BLACKLIST_MATCHING_ENABLED = True
    manager, _c, person = setup
    composite = compute_composite_identifier("A", "B", date(1991, 2, 3), "C")
    case = propose_case(person, identifier="ID-9", composite_identifier=composite, actor=manager)
    decide_case(case, "approve", actor=manager)
    matches = check_matches({IdentifierType.NAME_DOB_MMN: composite})
    assert set(matches.values_list("identifier_type", flat=True)) == {IdentifierType.NAME_DOB_MMN}
    # The right hash under the wrong type does not match.
    assert not check_matches({IdentifierType.PASSPORT: composite}).exists()
    both = check_matches({"national_id": "ID-9", IdentifierType.NAME_DOB_MMN: composite})
    assert set(both.values_list("identifier_type", flat=True)) == {
        "national_id", IdentifierType.NAME_DOB_MMN,
    }
    settings.BLACKLIST_MATCHING_ENABLED = False
    assert not check_matches({"national_id": "ID-9"}).exists()


def test_propose_stores_composite_fingerprint_inactive_until_approved(setup):
    manager, _c, person = setup
    composite = compute_composite_identifier("Anna", "Kováčová", date(1990, 1, 15), "Nováková")
    case = propose_case(person, identifier="ID-7", composite_identifier=composite, actor=manager)
    assert case.fingerprints.count() == 2
    fp = case.fingerprints.get(identifier_type=IdentifierType.NAME_DOB_MMN)
    assert not fp.is_active
    # Neither the canonical string nor the raw maiden name is stored anywhere.
    for row in case.fingerprints.all():
        for value in vars(row).values():
            assert "NOVAKOVA" not in str(value) and "Nováková" not in str(value)
    decide_case(case, "approve", actor=manager)
    assert case.fingerprints.filter(identifier_type=IdentifierType.NAME_DOB_MMN, is_active=True).exists()


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


def test_archiving_a_blacklisted_person_preserves_reentry_protection(setup):
    manager, _c, person = setup
    case = decide_case(
        propose_case(person, identifier="CE-DEMO-BL-2026-001", actor=manager),
        "approve",
        actor=manager,
    )

    person.archive(actor=manager, reason="fictional demo archive")

    person.refresh_from_db()
    assert person.is_archived
    assert case.fingerprints.filter(is_active=True).exists()
    assert check_match("CE-DEMO-BL-2026-001").exists()


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


def test_person_create_flags_composite_match_without_id(client, setup, settings):
    settings.BLACKLIST_MATCHING_ENABLED = True
    manager, _c, existing = setup
    existing.date_of_birth = date(1990, 1, 15)
    existing.save(update_fields=["date_of_birth"])
    composite = compute_composite_identifier("Olena", "Kováčová", date(1990, 1, 15), "Nováková")
    decide_case(
        propose_case(existing, composite_identifier=composite, actor=manager),
        "approve", actor=manager,
    )
    from django.contrib.auth import get_user_model
    rec = get_user_model().objects.create_user(email="r3@demo.jober.test", password="x", role="recruiter")
    client.force_login(rec)
    # Re-entry with no ID code, an ASCII spelling, and swapped name order.
    resp = client.post(reverse("person_create"), {
        "first_name": "Kovacova", "last_name": "Olena",
        "date_of_birth": "1990-01-15", "mothers_maiden_name": "Novakova",
    })
    assert resp.status_code == 302
    new = Person.objects.get(first_name="Kovacova")       # created, not blocked
    assert has_open_case(new)
    case = new.blacklist_cases.get()
    assert IdentifierType.NAME_DOB_MMN in case.restricted_reason
    # The new proposal carries its own composite fingerprint for the decision.
    assert case.fingerprints.filter(identifier_type=IdentifierType.NAME_DOB_MMN).exists()


def test_person_create_reason_names_all_matched_types(client, setup, settings):
    settings.BLACKLIST_MATCHING_ENABLED = True
    manager, _c, existing = setup
    composite = compute_composite_identifier("New", "Person", date(1988, 6, 1), "Horváthová")
    decide_case(
        propose_case(existing, identifier="MATCH-2", composite_identifier=composite, actor=manager),
        "approve", actor=manager,
    )
    from django.contrib.auth import get_user_model
    rec = get_user_model().objects.create_user(email="r4@demo.jober.test", password="x", role="recruiter")
    client.force_login(rec)
    resp = client.post(reverse("person_create"), {
        "first_name": "New", "last_name": "Person", "date_of_birth": "1988-06-01",
        "identifier": "MATCH-2", "identifier_type": "national_id",
        "mothers_maiden_name": "Horvathova",
    })
    assert resp.status_code == 302
    case = Person.objects.get(first_name="New").blacklist_cases.get()
    assert "national_id" in case.restricted_reason
    assert IdentifierType.NAME_DOB_MMN in case.restricted_reason


def test_queue_shows_matched_fingerprint_types(client, setup):
    manager, _c, person = setup
    composite = compute_composite_identifier("A", "B", date(1992, 3, 4), "C")
    propose_case(person, identifier="ID-5", composite_identifier=composite, actor=manager)
    client.force_login(manager)
    resp = client.get(reverse("blacklist_queue"))
    html = resp.content.decode()
    # Compare against the response's own locale (clients ship different
    # LANGUAGES; corvinum has no "en" URL prefix).
    from django.utils import translation
    from django.utils.html import escape
    from django.utils.translation import gettext
    with translation.override(resp.headers.get("Content-Language", "sk")):
        assert escape(gettext("Matched via")) in html
        assert escape(str(IdentifierType.NATIONAL_ID.label)) in html
        assert escape(str(IdentifierType.NAME_DOB_MMN.label)) in html


def test_manual_propose_accepts_optional_maiden_name(client, setup):
    manager, _c, person = setup
    person.date_of_birth = date(1993, 5, 6)
    person.save(update_fields=["date_of_birth"])
    client.force_login(manager)
    resp = client.post(reverse("blacklist_propose", args=[person.pk]), {
        "reason": "fictional", "identifier": "ID-8", "mothers_maiden_name": "Szabó",
    })
    assert resp.status_code == 302
    case = person.blacklist_cases.get()
    assert set(case.fingerprints.values_list("identifier_type", flat=True)) == {
        "national_id", IdentifierType.NAME_DOB_MMN,
    }
    # Without the maiden name (or DOB) only the ID fingerprint is stored.
    other = Person.objects.create(first_name="No", last_name="Maiden")
    resp = client.post(reverse("blacklist_propose", args=[other.pk]), {
        "reason": "fictional", "identifier": "ID-10",
    })
    assert resp.status_code == 302
    assert set(other.blacklist_cases.get().fingerprints.values_list("identifier_type", flat=True)) == {
        "national_id",
    }


# --- RBAC ----------------------------------------------------------------------

@pytest.mark.jober_only  # Jober grants/lifecycle/features
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
