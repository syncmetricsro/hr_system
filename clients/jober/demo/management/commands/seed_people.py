from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.accounts.models import Role, User
from core.offices.models import Office
from core.people.models import LifecycleStatus, Person
from core.projects.models import Project
from core.projects.services import activate_on_project, schedule_trial
from clients.jober.demo.management.commands.seed_demo import DEMO_USERS

# Fictional data only — no real worker PII before the legal gate.
DEMO_DOMAIN = "demo.jober.test"

# The three offices Jober licensed from SyncMetric s.r.o. (ADR 0026 Phase
# A). Seeded here — a Jober-only management command — rather than in a
# core/offices migration: core.offices is installed by every client (it's
# a generic mechanism, like Project.office was before this), but these
# specific office names are Jober business data, not something CorvinumEU
# or any future client should get seeded into its own database just
# because it shares the same core app.
OFFICES = [
    {"name": "Velký Meder", "code": "VM", "country": "SK"},
    {"name": "Győr", "code": "GYR", "country": "HU"},
    {"name": "Dunajská Streda", "code": "DS", "country": "SK"},
]

# office_code refers to the OFFICES rows created below — assignment is an
# arbitrary but sensible demo spread across the three licensed offices,
# not a claim about where these fictional clients actually operate.
# Two projects per office, so the finance "Profit/loss by office" roll-up is a
# real sum rather than a restatement of a single project. Names follow the
# vocabulary of Jober's own workbook (Jober_Finance_Specs.md §2) so the demo
# reads as familiar to them; the figures behind them are fictional.
PROJECTS = [
    {"name": "DHL Bratislava", "code": "DHLBA", "office_code": "VM", "partner": "DHL"},
    {"name": "Minit", "code": "MINIT", "office_code": "VM", "partner": "Minit"},
    {"name": "WEBASTO", "code": "WEB", "office_code": "GYR", "partner": "Webasto"},
    {"name": "Mevis 080", "code": "MEVIS", "office_code": "GYR", "partner": "Mevis"},
    {"name": "CARGO", "code": "CARGO", "office_code": "DS", "partner": "Cargo"},
    {"name": "RLS 067", "code": "RLS", "office_code": "DS", "partner": "RLS"},
]

# (first, last, status, has_disability, office_code) — office_code spreads
# people across all three offices (not all-VM) so office scoping (ADR 0026
# Phase B) is visibly demonstrated in the demo, matching the same principle
# already applied to project/staff office assignment above. Farrukh's office
# matches his pending trial at WEBASTO (Győr), not his eventual home office.
# Bohdan (the only INACTIVE demo person) stays in VM deliberately, alongside
# Olha/Diana/Mira: the seeded staff accounts (manazer/naborar/koordinator)
# are all VM-scoped, so VM needs its own representative of every interesting
# lifecycle state - Tran (DS) and Farrukh (GYR) alone are enough to prove
# cross-office data is hidden from those accounts without also hiding VM's
# own inactive-reason/disability/underage demo scenarios from them.
PEOPLE = [
    ("Olha", "Kovalenko", LifecycleStatus.WORKING, False, "VM"),
    ("Farrukh", "Tashkentov", LifecycleStatus.AVAILABLE, False, "GYR"),
    ("Tran", "Van Minh", LifecycleStatus.AVAILABLE, False, "DS"),
    ("Diana", "Horvathova", LifecycleStatus.AVAILABLE, True, "VM"),
    ("Bohdan", "Melnyk", LifecycleStatus.INACTIVE, False, "VM"),
    ("Mira", "Novakova", LifecycleStatus.AVAILABLE, False, "VM"),
]


class Command(BaseCommand):
    help = (
        "Create fictional projects, people, and one assignment for local/staging demos."
    )

    def handle(self, *args, **options):
        for spec in OFFICES:
            Office.objects.get_or_create(code=spec["code"], defaults=spec)
        self.stdout.write(
            f"Offices: {Office.objects.filter(code__in=[o['code'] for o in OFFICES]).count()}"
        )

        recruiter = User.objects.filter(email=f"naborar@{DEMO_DOMAIN}").first()
        coordinator = User.objects.filter(email=f"koordinator@{DEMO_DOMAIN}").first()

        # Office membership for every seeded account, driven by the single
        # DEMO_USERS table so accounts and their offices cannot drift apart.
        # Done before projects, because responsible-coordinator assignment
        # below needs to know which coordinator belongs to which office.
        coordinators_by_office: dict[str, User] = {}
        recruiters_by_office: dict[str, User] = {}
        for local_part, role, _first, _last, office_code in DEMO_USERS:
            user = User.objects.filter(email=f"{local_part}@{DEMO_DOMAIN}").first()
            if user is None:
                continue
            if office_code is None:
                # Observer: cross-office access is a role bypass, never a
                # membership, so it must hold no office rows at all.
                user.offices.clear()
                continue
            office = Office.objects.filter(code=office_code).first()
            if office is None:
                continue
            user.offices.set([office])
            if role == Role.COORDINATOR:
                coordinators_by_office[office_code] = user
            if role == Role.RECRUITER:
                recruiters_by_office[office_code] = user

        projects = {}
        for spec in PROJECTS:
            office_code = spec["office_code"]
            defaults = {k: v for k, v in spec.items() if k != "office_code"}
            defaults["office"] = Office.objects.filter(code=office_code).first()
            project, _ = Project.objects.update_or_create(
                code=spec["code"], defaults=defaults
            )
            # Each project is run by a coordinator of its OWN office. Assigning
            # every project to the Velký Meder coordinator - as this did until
            # 2026-07-26 - left them formally responsible for four projects
            # they get a 403 on, which reads as broken data the moment anyone
            # asks who runs the Győr contracts.
            office_coordinator = coordinators_by_office.get(office_code)
            if office_coordinator:
                project.responsible_coordinators.set([office_coordinator])
            projects[spec["code"]] = project
        self.stdout.write(f"Projects: {len(projects)}")

        for first, last, status, disabled, office_code in PEOPLE:
            office = Office.objects.filter(code=office_code).first()
            person, created = Person.objects.get_or_create(
                first_name=first,
                last_name=last,
                defaults={
                    # Owned by their OWN office's recruiter, the same
                    # correction made for project coordinators on 2026-07-26.
                    # Attributing all seven to the Velký Meder recruiter left
                    # the staff-activity report showing one recruiter with
                    # everything and two with nothing - which demonstrates the
                    # zero rows but not the gap between two working recruiters
                    # the report exists to reveal.
                    "owning_recruiter": recruiters_by_office.get(
                        office_code, recruiter
                    ),
                    "has_disability": disabled,
                    "disability_type": "reduced mobility" if disabled else "",
                    # WORKING is reached via an assignment below, not directly.
                    "lifecycle_status": status
                    if status != LifecycleStatus.WORKING
                    else LifecycleStatus.AVAILABLE,
                    "office": office,
                },
            )
            if not created and person.office_id != (office.id if office else None):
                person.office = office
                person.save(update_fields=["office", "updated_at"])
            # Repair databases seeded before recruiters were per-office. Without
            # this the correction only reaches a database created from scratch,
            # and every existing demo instance keeps showing one recruiter with
            # everything.
            owner = recruiters_by_office.get(office_code, recruiter)
            if not created and owner and person.owning_recruiter_id != owner.id:
                person.owning_recruiter = owner
                person.save(update_fields=["owning_recruiter", "updated_at"])
            if created and status == LifecycleStatus.WORKING:
                activate_on_project(
                    person, projects["DHLBA"], actor=coordinator, reason="demo seed"
                )

        underage = Person.objects.filter(
            first_name="Mira", last_name="Novakova"
        ).first()
        if underage:
            underage.date_of_birth = timezone.localdate().replace(
                year=timezone.localdate().year - 17
            )
            underage.save(update_fields=["date_of_birth", "updated_at"])

        # A lifecycle label alone does not populate the operational queue. Keep
        # one real pending TrialAssignment so the demo exercises the same UI and
        # service path staff use.
        farrukh = Person.objects.filter(
            first_name="Farrukh", last_name="Tashkentov"
        ).first()
        if farrukh and not farrukh.trials.exists():
            if farrukh.lifecycle_status == LifecycleStatus.TRIAL_DAY:
                # Repair databases created by the older incomplete seed.
                farrukh.lifecycle_status = LifecycleStatus.AVAILABLE
                farrukh.save(update_fields=["lifecycle_status", "updated_at"])
            schedule_trial(
                farrukh,
                projects["WEB"],
                actor=coordinator,
                scheduled_for=timezone.now() + timedelta(days=2),
                note="Demo arrival at the main gate",
            )

        self.stdout.write(
            self.style.SUCCESS(f"People seeded: {Person.objects.count()} total")
        )
