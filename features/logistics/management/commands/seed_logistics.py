from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.accounts.models import User
from features.logistics.models import Accommodation, EquipmentItem, Room
from features.logistics.services import assign_room, record_transport_week
from core.projects.models import Project
from core.people.models import LifecycleStatus, Person

DEMO_DOMAIN = "demo.jober.test"


class Command(BaseCommand):
    help = "Seed fictional accommodation, rooms (with rates), and the equipment catalog."

    def handle(self, *args, **options):
        coordinator = User.objects.filter(email=f"koordinator@{DEMO_DOMAIN}").first()

        accommodation, _ = Accommodation.objects.get_or_create(
            name="Ubytovňa Nitra", defaults={"address": "Nitra 1", "is_active": True}
        )
        room, _ = Room.objects.get_or_create(
            accommodation=accommodation, label="101",
            defaults={"capacity": 2, "monthly_rate": "180.00"},
        )
        Room.objects.get_or_create(
            accommodation=accommodation, label="102",
            defaults={"capacity": 2, "monthly_rate": "180.00"},
        )
        working = Person.objects.filter(lifecycle_status=LifecycleStatus.WORKING).first()
        if working and not working.room_assignments.exists():
            assign_room(working, room, actor=coordinator)

        for name, size, price in [
            ("Work boots", "42", "45.00"),  # canonical English; rendered via db_trans
            ("High-visibility vest", "L", "8.50"),
            ("Safety helmet", "", "15.00"),
        ]:
            EquipmentItem.objects.get_or_create(name=name, size=size, defaults={"unit_price": price})

        # Populate several project weeks so Transport is a useful trend rather
        # than an empty state in a fresh fictional demo.
        today = timezone.localdate()
        monday = today - timedelta(days=today.weekday())
        projects = list(Project.objects.filter(is_active=True).order_by("code")[:3])
        for project_index, project in enumerate(projects):
            for weeks_ago in range(4, -1, -1):
                week_start = monday - timedelta(weeks=weeks_ago)
                record_transport_week(
                    project, week_start, 5 + project_index * 3 + (4 - weeks_ago),
                    actor=coordinator, note="Fictional demo transport",
                )

        self.stdout.write(self.style.SUCCESS("Logistics demo data seeded."))
