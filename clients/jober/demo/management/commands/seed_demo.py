from __future__ import annotations

from django.core.management.base import BaseCommand

from core.accounts.models import Role, User

# Obviously-fictional accounts only. No real worker PII may enter the system
# before the legal/security real-data gate (Handoff.md / AGENTS.md).
DEMO_PASSWORD = "demo-jober-2026"
DEMO_DOMAIN = "demo.jober.test"

DEMO_USERS = [
    ("naborar", Role.RECRUITER, "Náborár", "Demo"),
    ("koordinator", Role.COORDINATOR, "Koordinátor", "Demo"),
    ("manazer", Role.MANAGER, "Manažér", "Demo"),
    ("pozorovatel", Role.OBSERVER, "Pozorovateľ", "Demo"),
]


def is_fictional(email: str) -> bool:
    return email.endswith(f"@{DEMO_DOMAIN}")


class Command(BaseCommand):
    help = "Create one fictional user per role for local/staging demos (no real PII)."

    def handle(self, *args, **options):
        created, updated = 0, 0
        for local_part, role, first, last in DEMO_USERS:
            email = f"{local_part}@{DEMO_DOMAIN}"
            assert is_fictional(email), "Seed accounts must use the fictional demo domain."
            user, was_created = User.objects.get_or_create(
                email=email,
                defaults={"first_name": first, "last_name": last, "role": role},
            )
            user.first_name = first
            user.last_name = last
            user.role = role
            user.is_active = True
            user.set_password(DEMO_PASSWORD)
            user.save()
            created += int(was_created)
            updated += int(not was_created)
            self.stdout.write(f"  {email} -> {role.label}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {created} created, {updated} updated. "
                f"Password for all: {DEMO_PASSWORD}"
            )
        )
