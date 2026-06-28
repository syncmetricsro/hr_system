from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.finance.services import record_financial_month
from apps.logistics.models import Accommodation, EquipmentItem, Room
from apps.logistics.services import assign_room
from apps.people.models import LifecycleStatus, Person
from apps.projects.models import Project
from apps.projects.services import activate_on_project

# Fictional data only — no real worker PII before the legal gate.
DEMO_DOMAIN = "demo.jober.test"

PROJECTS = [
    {"name": "DHL Bratislava", "code": "DHLBA", "office": "Bratislava", "partner": "DHL"},
    {"name": "WEBASTO", "code": "WEB", "office": "Nitra", "partner": "Webasto"},
    {"name": "CARGO", "code": "CARGO", "office": "Bratislava", "partner": "Cargo"},
]

# (first, last, status, has_disability)
PEOPLE = [
    ("Olha", "Kovalenko", LifecycleStatus.WORKING, False),
    ("Farrukh", "Tashkentov", LifecycleStatus.TRIAL_DAY, False),
    ("Tran", "Van Minh", LifecycleStatus.AVAILABLE, False),
    ("Diana", "Horvathova", LifecycleStatus.AVAILABLE, True),
    ("Bohdan", "Melnyk", LifecycleStatus.INACTIVE, False),
]


class Command(BaseCommand):
    help = "Create fictional projects, people, and one assignment for local/staging demos."

    def handle(self, *args, **options):
        recruiter = User.objects.filter(email=f"naborar@{DEMO_DOMAIN}").first()
        coordinator = User.objects.filter(email=f"koordinator@{DEMO_DOMAIN}").first()

        projects = {}
        for spec in PROJECTS:
            project, _ = Project.objects.get_or_create(code=spec["code"], defaults=spec)
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

        # Minimal accommodation with rooms; house the first Working person.
        accommodation, _ = Accommodation.objects.get_or_create(
            name="Ubytovňa Nitra", defaults={"address": "Nitra 1", "is_active": True}
        )
        room, _ = Room.objects.get_or_create(accommodation=accommodation, label="101", defaults={"capacity": 2})
        Room.objects.get_or_create(accommodation=accommodation, label="102", defaults={"capacity": 2})
        working = Person.objects.filter(lifecycle_status=LifecycleStatus.WORKING).first()
        if working and not working.room_assignments.exists():
            assign_room(working, room, actor=coordinator)

        # Minimal equipment catalog.
        for name, size in [("Pracovná obuv", "42"), ("Reflexná vesta", "L"), ("Prilba", "")]:
            EquipmentItem.objects.get_or_create(name=name, size=size)

        # Minimal financial months (sign convention: net = revenue - cost, to confirm).
        for code, month, rev, cost in [("DHLBA", 5, "18000", "12000"), ("WEB", 5, "9000", "7000")]:
            record_financial_month(projects[code], 2026, month, rev, cost, actor=coordinator)

        self.stdout.write(self.style.SUCCESS(f"People seeded: {Person.objects.count()} total"))
