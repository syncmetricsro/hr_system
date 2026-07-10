"""GDPR retention registry (Stage B4, ADR 0021; CorvinumEU design §5.12).

Features register their purge callables from ``AppConfig.ready()``; the single
``run_retention`` command executes them all. Generalizes the pattern the
feedback and blacklist purges established — those commands keep working and
now also run through here.
"""

from __future__ import annotations

_jobs: list[tuple[str, object]] = []


def register_retention(name: str, purge_fn) -> None:
    entry = (name, purge_fn)
    if entry not in _jobs:
        _jobs.append(entry)


def run_all() -> dict[str, object]:
    """Run every registered purge; returns {name: result} for reporting."""
    return {name: purge_fn() for name, purge_fn in _jobs}


def registered() -> list[str]:
    return [name for name, _ in _jobs]
