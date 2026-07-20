from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.accounts.models import User
from core.people.models import LifecycleStatus, Person
from core.projects.models import Project
from core.projects.services import activate_on_project, schedule_trial

# Fictional data only — no real worker PII before the legal gate.
DEMO_DOMAIN = "demo.jober.test"

PROJECTS = [
    {"name": "DHL Bratislava", "code": "DHLBA", "office": "Bratislava", "partner": "DHL", "region": "Megyer"},
    {"name": "WEBASTO", "code": "WEB", "office": "Nitra", "partner": "Webasto", "region": "DS"},
    {"name": "CARGO", "code": "CARGO", "office": "Bratislava", "partner": "Cargo", "region": "Megyer"},
]

# (first, last, status, has_disability)
PEOPLE = [
    ("Olha", "Kovalenko", LifecycleStatus.WORKING, False),
    ("Farrukh", "Tashkentov", LifecycleStatus.AVAILABLE, False),
    ("Tran", "Van Minh", LifecycleStatus.AVAILABLE, False),
    ("Diana", "Horvathova", LifecycleStatus.AVAILABLE, True),
    ("Bohdan", "Melnyk", LifecycleStatus.INACTIVE, False),
    ("Mira", "Novakova", LifecycleStatus.AVAILABLE, False),
]


class Command(BaseCommand):
    help = "Create fictional projects, people, and one assignment for local/staging demos."

    def handle(self, *args, **options):
        recruiter = User.objects.filter(email=f"naborar@{DEMO_DOMAIN}").first()
        coordinator = User.objects.filter(email=f"koordinator@{DEMO_DOMAIN}").first()

        projects = {}
        for spec in PROJECTS:
            project, _ = Project.objects.update_or_create(code=spec["code"], defaults=spec)
            if coordinator:
                project.responsible_coordinators.add(coordinator)
            projects[spec["code"]] = project
        self.stdout.write(f"Projects: {len(projects)}")

        for first, last, status, disabled in PEOPLE:
            person, created = Person.objects.get_or_create(
                first_name=first,
                last_name=last,
                defaults={
                    "owning_recruiter": recruiter,
                    "has_disability": disabled,
                    "disability_type": "reduced mobility" if disabled else "",
                    # WORKING is reached via an assignment below, not directly.
                    "lifecycle_status": status if status != LifecycleStatus.WORKING else LifecycleStatus.AVAILABLE,
                },
            )
            if created and status == LifecycleStatus.WORKING:
                activate_on_project(
                    person, projects["DHLBA"], actor=coordinator, reason="demo seed"
                )

        underage = Person.objects.filter(first_name="Mira", last_name="Novakova").first()
        if underage:
            underage.date_of_birth = timezone.localdate().replace(
                year=timezone.localdate().year - 17
            )
            underage.save(update_fields=["date_of_birth", "updated_at"])

        # A lifecycle label alone does not populate the operational queue. Keep
        # one real pending TrialAssignment so the demo exercises the same UI and
        # service path staff use.
        farrukh = Person.objects.filter(first_name="Farrukh", last_name="Tashkentov").first()
        if farrukh and not farrukh.trials.exists():
            if farrukh.lifecycle_status == LifecycleStatus.TRIAL_DAY:
                # Repair databases created by the older incomplete seed.
                farrukh.lifecycle_status = LifecycleStatus.AVAILABLE
                farrukh.save(update_fields=["lifecycle_status", "updated_at"])
            schedule_trial(
                farrukh, projects["WEB"], actor=coordinator,
                scheduled_for=timezone.now() + timedelta(days=2),
                note="Demo arrival at the main gate",
            )

        self.stdout.write(self.style.SUCCESS(f"People seeded: {Person.objects.count()} total"))
