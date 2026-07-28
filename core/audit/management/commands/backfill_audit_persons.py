"""Attribute historical audit events to the worker they concern.

The migration that added `AuditEvent.person` could only attribute two cases:
the target *was* a Person, or a caller had passed `person=` in metadata. It
could not follow a target to its owner, because a data migration works with
historical models that carry no relations, and because `core` must not import
`features` to learn that an `EquipmentIssue` has a `.person`.

That limit was documented but its consequence was underestimated. On the demo
database it attributed **8 of 900** events: every `equipment.issued`,
`room.assigned`, `blacklist.proposed` and `trial.scheduled` row stayed
unattributed, and those are precisely the events a manager means when they ask
"what happened to this worker?". The person filter still returned nothing for
anybody with real history - the original complaint, unfixed.

A management command has what a migration lacks: real models. Resolving the
target through the app registry needs no import from core into features, and
`getattr(obj, "person", None)` is the same rule `record_event` applies to new
events - so history ends up attributed exactly as the future will be.

Idempotent: only rows with no person are considered, so it is safe to re-run
and safe to run on a database where it has already been applied.
"""

from __future__ import annotations

from collections import defaultdict

from django.apps import apps as django_apps
from django.core.management.base import BaseCommand
from django.db import transaction

from core.audit.models import AuditEvent
from core.people.models import Person

BATCH = 500


def _models_named(name: str) -> list:
    """Every installed model whose class name matches, since `target_type`
    stores a bare class name and two apps may legitimately share one."""
    return [m for m in django_apps.get_models() if m.__name__ == name]


def _person_id_for(target_type: str, target_id: str, metadata: dict) -> int | None:
    """The same three sources `record_event._person_for` uses, resolved from
    stored identifiers rather than a live object."""
    if target_type == "Person" and (target_id or "").isdigit():
        return int(target_id)

    if (target_id or "").isdigit():
        for model in _models_named(target_type):
            if not any(f.name == "person" for f in model._meta.get_fields()):
                continue
            person_id = (
                model.objects.filter(pk=int(target_id))
                .values_list("person_id", flat=True)
                .first()
            )
            if person_id:
                return person_id

    raw = (metadata or {}).get("person")
    if isinstance(raw, int) or (isinstance(raw, str) and str(raw).isdigit()):
        return int(raw)
    return None


class Command(BaseCommand):
    help = "Attribute historical audit events to the person they concern."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be attributed without writing anything.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        known = set(Person.objects.values_list("pk", flat=True))

        pending = AuditEvent.objects.filter(person__isnull=True).only(
            "pk", "target_type", "target_id", "metadata", "action"
        )
        total = pending.count()

        updates = []
        by_action: dict[str, int] = defaultdict(int)
        unresolved: dict[str, int] = defaultdict(int)

        for event in pending.iterator(chunk_size=BATCH):
            person_id = _person_id_for(
                event.target_type, event.target_id, event.metadata
            )
            # A person deleted since the event was written stays unattributed
            # rather than pointing at a recycled primary key.
            if person_id in known:
                event.person_id = person_id
                updates.append(event)
                by_action[event.action] += 1
            else:
                unresolved[event.target_type or "(none)"] += 1

        if updates and not dry_run:
            with transaction.atomic():
                AuditEvent.objects.bulk_update(updates, ["person"], batch_size=BATCH)

        verb = "would attribute" if dry_run else "attributed"
        self.stdout.write(f"{verb} {len(updates)} of {total} unattributed events")
        for action, count in sorted(by_action.items(), key=lambda kv: -kv[1]):
            self.stdout.write(f"  {action}: {count}")
        if unresolved:
            self.stdout.write("still unattributed, by target type:")
            for target_type, count in sorted(unresolved.items(), key=lambda kv: -kv[1])[
                :10
            ]:
                self.stdout.write(f"  {target_type}: {count}")
