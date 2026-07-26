"""Structural checks for the deployment operations scripts.

The backup pair (`offsite_backup.sh` / `backup_health.sh`) is no longer
Corvinum-specific: one invocation backs up one Dokku app, so the same scripts
cover jober-staging too. These assertions guard the properties that are easy to
lose in a refactor and expensive to lose in production - encryption before
transfer, never exporting Dokku config (it carries Doppler secrets), and a
retention pass scoped to its own archive prefix.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def script(name: str) -> str:
    return (ROOT / "scripts" / name).read_text(encoding="utf-8")


def test_offsite_backup_is_encrypted_and_does_not_export_dokku_config() -> None:
    source = script("offsite_backup.sh")

    assert "set -euo pipefail" in source
    assert "dokku postgres:export" in source
    assert "--encrypt" in source
    assert "BACKUP_GPG_RECIPIENT" in source
    assert "dokku config:export" not in source
    assert 'prune "$backup_dir/daily" 35' in source
    assert 'prune "$backup_dir/monthly" 12' in source


def test_offsite_backup_prunes_only_its_own_prefix() -> None:
    """Two apps may share a backup directory. The retention pass must glob on
    the run's own prefix — a bare wildcard would delete the other app's
    history, and would look like a harmless generalisation in review."""
    source = script("offsite_backup.sh")

    assert '-name "$prefix-*.tar.gpg"' in source
    assert "'corvinum-*.tar.gpg'" not in source
    # The prefix reaches the remote shell as a positional argument rather than
    # by interpolation into the heredoc body, so its value cannot rewrite the
    # remote script itself.
    assert 'prefix="$4"' in source
    # And it is constrained to characters that cannot change what the glob matches.
    assert '"$BACKUP_PREFIX" =~ ^[A-Za-z0-9._-]+$' in source


def test_backup_health_matches_the_same_prefix() -> None:
    """A health check globbing a different prefix than the backup writes would
    report "no backup" for a healthy app — a false alarm that teaches people to
    ignore the alert."""
    source = script("backup_health.sh")

    assert "BACKUP_PREFIX" in source
    assert "'corvinum-*.tar.gpg'" not in source


def test_backup_health_enforces_age_and_capacity_thresholds() -> None:
    source = script("backup_health.sh")

    assert "BACKUP_MAX_AGE_HOURS:-26" in source
    assert "BACKUP_MAX_USAGE_PERCENT:-60" in source
    assert "StrictHostKeyChecking=yes" in source


def test_staging_script_is_explicitly_on_demand() -> None:
    source = script("corvinum_staging.sh")

    assert 'action="${1:-status}"' in source
    assert "start|stop|status" in source
    assert "dokku ps:start" in source
    assert "dokku ps:stop" in source
