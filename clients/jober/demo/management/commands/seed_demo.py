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

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-passwords",
            action="store_true",
            help=(
                "Also reset existing accounts back to the built-in demo password. "
                "Off by default so re-seeding never silently undoes a rotation."
            ),
        )

    def handle(self, *args, **options):
        # Only *new* accounts get the built-in password. This command is run
        # against staging, whose demo password has been rotated away from the
        # value published in this public repo - resetting it on every run would
        # quietly republish it. Rotations therefore survive a reseed unless
        # --reset-passwords says otherwise.
        reset_passwords = options["reset_passwords"]
        created, updated, kept = 0, 0, 0
        for local_part, role, first, last in DEMO_USERS:
            email = f"{local_part}@{DEMO_DOMAIN}"
            assert is_fictional(email), (
                "Seed accounts must use the fictional demo domain."
            )
            user, was_created = User.objects.get_or_create(
                email=email,
                defaults={"first_name": first, "last_name": last, "role": role},
            )
            user.first_name = first
            user.last_name = last
            user.role = role
            user.is_active = True
            if was_created or reset_passwords:
                user.set_password(DEMO_PASSWORD)
            else:
                kept += 1
            user.save()
            created += int(was_created)
            updated += int(not was_created)
            self.stdout.write(f"  {email} -> {role.label}")

        summary = f"Seed complete: {created} created, {updated} updated."
        if created or reset_passwords:
            summary += f" Password for new/reset accounts: {DEMO_PASSWORD}"
        self.stdout.write(self.style.SUCCESS(summary))
        if kept:
            self.stdout.write(
                self.style.WARNING(
                    f"Kept the existing password on {kept} account(s). Pass "
                    f"--reset-passwords to force them back to the built-in demo value."
                )
            )
