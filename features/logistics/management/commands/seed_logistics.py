from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from uuid import NAMESPACE_URL, uuid5

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.accounts.models import User
from core.offices.models import Office
from features.logistics.models import Accommodation, EquipmentItem, Room
from features.logistics.services import (
    assign_room,
    receive_stock,
    set_accommodation_cost_period,
)
from core.people.models import LifecycleStatus, Person

DEMO_DOMAIN = "demo.jober.test"


class Command(BaseCommand):
    help = (
        "Seed fictional accommodation, rooms (with rates), and the equipment catalog."
    )

    def handle(self, *args, **options):
        coordinator = User.objects.filter(email=f"koordinator@{DEMO_DOMAIN}").first()

        # Matches the office of the worker housed here (Olha, on DHLBA/VM) —
        # None on any install with no Office rows (e.g. CorvinumEU), which is
        # the correct/safe default there.
        velky_meder = Office.objects.filter(code="VM").first()
        accommodation, _ = Accommodation.objects.get_or_create(
            name="Ubytovňa Nitra",
            defaults={"address": "Nitra 1", "is_active": True, "office": velky_meder},
        )
        if accommodation.office_id != (velky_meder.id if velky_meder else None):
            accommodation.office = velky_meder
            accommodation.save(update_fields=["office"])
        room, _ = Room.objects.get_or_create(
            accommodation=accommodation,
            label="101",
            defaults={"capacity": 2, "monthly_rate": "180.00"},
        )
        Room.objects.get_or_create(
            accommodation=accommodation,
            label="102",
            defaults={"capacity": 2, "monthly_rate": "180.00"},
        )
        working = Person.objects.filter(
            lifecycle_status=LifecycleStatus.WORKING
        ).first()
        if working and not working.room_assignments.exists():
            assignment = assign_room(
                working,
                room,
                actor=coordinator,
                worker_payment_monthly=Decimal("125.00"),
            )
            assignment.start_date = timezone.localdate().replace(day=15)
            assignment.save(update_fields=["start_date"])

        month_start = timezone.localdate().replace(day=1)
        set_accommodation_cost_period(
            accommodation,
            effective_month=month_start,
            capacity=4,
            per_head_cost=Decimal("180.00"),
            actor=coordinator,
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

        # One opening receipt per office rather than a single pooled one, so
        # the demo actually exercises per-office FIFO isolation (ADR 0026
        # Phase B) instead of just carrying an office column nobody can see.
        # Quantities differ per office deliberately: a VM-scoped manager and
        # the Observer see visibly different warehouse totals.
        # Note the cross-file dependency: seed_people.py assigns each demo
        # person an office, and issue_equipment draws only from that person's
        # office - every office holding a worker needs stock here.
        offices = list(Office.objects.order_by("code")) or [None]
        per_office_quantities = {
            "VM": (10, 20, 8),
            "GYR": (6, 12, 5),
            "DS": (4, 8, 3),
        }
        for office in offices:
            code = office.code if office else "POOLED"
            boots, vests, helmets = per_office_quantities.get(code, (4, 8, 3))
            receive_stock(
                received_on=month_start - timedelta(days=4),
                operation_key=uuid5(
                    NAMESPACE_URL, f"jober-demo-stock-opening-v2-{code}"
                ),
                reference=f"DEMO-DAC-{code}",
                supplier="Fictional Safety Supply",
                lines=[
                    {
                        "item": items[0],
                        "quantity": boots,
                        "total_value": Decimal("41.00") * boots,
                    },
                    {
                        "item": items[1],
                        "quantity": vests,
                        "total_value": Decimal("7.50") * vests,
                    },
                    {
                        "item": items[2],
                        "quantity": helmets,
                        "total_value": Decimal("14.00") * helmets,
                    },
                ],
                actor=coordinator,
                office=office,
            )

        self.stdout.write(self.style.SUCCESS("Logistics demo data seeded."))
