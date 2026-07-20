from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from uuid import NAMESPACE_URL, uuid5

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.accounts.models import User
from features.logistics.models import Accommodation, EquipmentItem, Room
from features.logistics.services import (
    assign_room, receive_stock, set_accommodation_cost_period,
)
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
            assignment = assign_room(
                working, room, actor=coordinator, worker_payment_monthly=Decimal("125.00")
            )
            assignment.start_date = timezone.localdate().replace(day=15)
            assignment.save(update_fields=["start_date"])

        month_start = timezone.localdate().replace(day=1)
        set_accommodation_cost_period(
            accommodation, effective_month=month_start, capacity=4,
            per_head_cost=Decimal("180.00"), actor=coordinator,
        )

        items = []
        for name, size, price in [
            ("Work boots", "42", "45.00"),  # canonical English; rendered via db_trans
            ("High-visibility vest", "L", "8.50"),
            ("Safety helmet", "", "15.00"),
        ]:
            item, _ = EquipmentItem.objects.get_or_create(
                name=name, size=size, defaults={"unit_price": price}
            )
            items.append(item)

        receive_stock(
            received_on=month_start - timedelta(days=4),
            operation_key=uuid5(NAMESPACE_URL, "jober-demo-stock-opening-v1"),
            reference="DEMO-DAC-001", supplier="Fictional Safety Supply",
            lines=[
                {"item": items[0], "quantity": 10, "total_value": Decimal("410.00")},
                {"item": items[1], "quantity": 20, "total_value": Decimal("150.00")},
                {"item": items[2], "quantity": 8, "total_value": Decimal("112.00")},
            ],
            actor=coordinator,
        )

        self.stdout.write(self.style.SUCCESS("Logistics demo data seeded."))
