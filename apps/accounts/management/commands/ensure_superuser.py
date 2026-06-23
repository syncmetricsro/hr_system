from __future__ import annotations

import os

from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import Role, User
from apps.audit.services import record_event


class Command(BaseCommand):
    help = (
        "Idempotently ensure a Manager/Administrator superuser exists, from "
        "DJANGO_SUPERUSER_EMAIL / DJANGO_SUPERUSER_PASSWORD. Safe to run on "
        "every (non-interactive) deploy."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-if-unset",
            action="store_true",
            help="Exit 0 without error if the env vars are not set (for optional release steps).",
        )

    def handle(self, *args, **options):
        email = (os.environ.get("DJANGO_SUPERUSER_EMAIL") or "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD") or ""

        if not email or not password:
            message = "DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD must be set."
            if options["skip_if_unset"]:
                self.stdout.write(self.style.WARNING(f"Skipped: {message}"))
                return
            raise CommandError(message)

        email = User.objects.normalize_email(email)
        user = User.objects.filter(email=email).first()

        if user is None:
            user = User.objects.create_superuser(email=email, password=password, role=Role.MANAGER)
            record_event(user, "accounts.superuser_created", target=user)
            self.stdout.write(self.style.SUCCESS(f"Superuser created: {email}"))
            return

        # Already present: ensure it really is an active manager-superuser.
        # Password is left untouched so a redeploy never silently resets it.
        changed = []
        if not user.is_superuser:
            user.is_superuser = True
            changed.append("is_superuser")
        if not user.is_staff:
            user.is_staff = True
            changed.append("is_staff")
        if not user.is_active:
            user.is_active = True
            changed.append("is_active")
        if user.role != Role.MANAGER:
            user.role = Role.MANAGER
            changed.append("role")

        if changed:
            user.save(update_fields=changed)
            record_event(user, "accounts.superuser_ensured", target=user, fields=changed)
            self.stdout.write(self.style.SUCCESS(f"Superuser updated: {email} ({', '.join(changed)})"))
        else:
            self.stdout.write(f"Superuser already present and correct: {email}")
