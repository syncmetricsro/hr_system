from __future__ import annotations

from django.db import migrations

# Neutral placeholder categories (plan §11.14). Kept deliberately minimal to avoid
# special-category data; the real list is pending Jober/lawyer confirmation.
PLACEHOLDERS = [
    "Fraud / dishonesty",
    "Safety violation",
    "Repeated no-show",
    "Serious misconduct",
    "Other",
]


def seed(apps, schema_editor):
    BlacklistCategory = apps.get_model("blacklist", "BlacklistCategory")
    for order, label in enumerate(PLACEHOLDERS):
        BlacklistCategory.objects.get_or_create(label=label, defaults={"order": order})


def unseed(apps, schema_editor):
    BlacklistCategory = apps.get_model("blacklist", "BlacklistCategory")
    BlacklistCategory.objects.filter(label__in=PLACEHOLDERS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("blacklist", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
