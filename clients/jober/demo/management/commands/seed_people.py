from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.accounts.models import User
from core.offices.models import Office
from core.people.models import LifecycleStatus, Person
from core.projects.models import Project
from core.projects.services import activate_on_project, schedule_trial

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
PROJECTS = [
    {"name": "DHL Bratislava", "code": "DHLBA", "office_code": "VM", "partner": "DHL"},
    {"name": "WEBASTO", "code": "WEB", "office_code": "GYR", "partner": "Webasto"},
    {"name": "CARGO", "code": "CARGO", "office_code": "DS", "partner": "Cargo"},
]

# (first, last, status, has_disability, office_code) — office_code spreads
# people across all three offices (not all-VM) so office scoping (ADR 0026
# Phase B) is visibly demonstrated in the demo, matching the same principle
# already applied to project/staff office assignment above. Farrukh's office
# matches his pending trial at WEBASTO (Győr), not his eventual home office.
PEOPLE = [
    ("Olha", "Kovalenko", LifecycleStatus.WORKING, False, "VM"),
    ("Farrukh", "Tashkentov", LifecycleStatus.AVAILABLE, False, "GYR"),
    ("Tran", "Van Minh", LifecycleStatus.AVAILABLE, False, "DS"),
    ("Diana", "Horvathova", LifecycleStatus.AVAILABLE, True, "VM"),
    ("Bohdan", "Melnyk", LifecycleStatus.INACTIVE, False, "DS"),
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
        manager = User.objects.filter(email=f"manazer@{DEMO_DOMAIN}").first()

        projects = {}
        for spec in PROJECTS:
            office_code = spec["office_code"]
            defaults = {k: v for k, v in spec.items() if k != "office_code"}
            defaults["office"] = Office.objects.filter(code=office_code).first()
            project, _ = Project.objects.update_or_create(
                code=spec["code"], defaults=defaults
            )
            if coordinator:
                project.responsible_coordinators.add(coordinator)
            projects[spec["code"]] = project
        self.stdout.write(f"Projects: {len(projects)}")

        # Give the demo staff membership in exactly one office (ADR 0026 Phase
        # A) — deliberately NOT all three, so the demo actually shows the
        # restriction working (a manager's Finance page differs visibly from
        # the Observer's all-offices executive view, rather than looking
        # identical because every demo account happened to span every office).
        velky_meder = Office.objects.filter(code="VM").first()
        if recruiter and velky_meder:
            recruiter.offices.set([velky_meder])
        if coordinator and velky_meder:
            coordinator.offices.set([velky_meder])
        if manager and velky_meder:
            manager.offices.set([velky_meder])
        # Observer intentionally gets no office membership — cross-office
        # visibility is a role bypass (user_office_scope), not a membership.

        for first, last, status, disabled, office_code in PEOPLE:
            office = Office.objects.filter(code=office_code).first()
            person, created = Person.objects.get_or_create(
                first_name=first,
                last_name=last,
                defaults={
                    "owning_recruiter": recruiter,
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
