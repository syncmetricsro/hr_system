from __future__ import annotations

from django.db import migrations

# Q5 safe default: seed a few placeholder Inactive reasons (configurable in admin).
PLACEHOLDERS = [
    "Sick",
    "Quit / left",
    "Suspended",
    "Military service",
    "Other",
]


def seed(apps, schema_editor):
    InactiveReason = apps.get_model("people", "InactiveReason")
    for order, label in enumerate(PLACEHOLDERS):
        InactiveReason.objects.get_or_create(label=label, defaults={"order": order})


def unseed(apps, schema_editor):
    InactiveReason = apps.get_model("people", "InactiveReason")
    InactiveReason.objects.filter(label__in=PLACEHOLDERS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0002_inactivereason_person_inactive_since_and_more"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
