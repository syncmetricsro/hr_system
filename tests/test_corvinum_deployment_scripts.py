"""Structural checks for the Corvinum cost-first deployment operations."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def script(name: str) -> str:
    return (ROOT / "scripts" / name).read_text(encoding="utf-8")


def test_offsite_backup_is_encrypted_and_does_not_export_dokku_config() -> None:
    source = script("corvinum_offsite_backup.sh")

    assert "set -euo pipefail" in source
    assert "dokku postgres:export" in source
    assert "--encrypt" in source
    assert "BACKUP_GPG_RECIPIENT" in source
    assert "dokku config:export" not in source
    assert 'prune "$backup_dir/daily" 35' in source
    assert 'prune "$backup_dir/monthly" 12' in source


def test_backup_health_enforces_age_and_capacity_thresholds() -> None:
    source = script("corvinum_backup_health.sh")

    assert "BACKUP_MAX_AGE_HOURS:-26" in source
    assert "BACKUP_MAX_USAGE_PERCENT:-60" in source
    assert "corvinum-*.tar.gpg" in source
    assert "StrictHostKeyChecking=yes" in source


def test_staging_script_is_explicitly_on_demand() -> None:
    source = script("corvinum_staging.sh")

    assert 'action="${1:-status}"' in source
    assert "start|stop|status" in source
    assert "dokku ps:start" in source
    assert "dokku ps:stop" in source
