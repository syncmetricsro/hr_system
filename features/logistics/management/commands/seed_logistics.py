from __future__ import annotations

from django.core.management.base import BaseCommand

from core.accounts.models import User
from features.logistics.models import Accommodation, EquipmentItem, Room
from features.logistics.services import assign_room
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

        self.stdout.write(self.style.SUCCESS("Logistics demo data seeded."))
