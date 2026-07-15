#!/usr/bin/env bash
#
# Encrypted off-site backup for the CorvinumERP production Dokku host.
#
# This script intentionally exports only the PostgreSQL service, an optional
# future media directory, and a non-secret deployment manifest.  It never
# exports Dokku config: that output can contain Doppler-synchronised secrets.
#
# Required environment (normally supplied by a root-owned file outside git):
#   BACKUP_REMOTE=corvinum-backup@backup.example
#   BACKUP_REMOTE_DIR=/srv/corvinum-backups
#   BACKUP_GPG_RECIPIENT=<public key fingerprint or recipient>
# Optional:
#   DOKKU_APP=corvinum                 POSTGRES_SERVICE=pg-corvinum
#   BACKUP_SSH_KEY=/root/.ssh/corvinum-backup_ed25519
#   MEDIA_SOURCE_DIR=/var/lib/dokku/data/storage/corvinum/media
#   BACKUP_WORK_DIR=/var/lib/corvinum-backups
#
# The recipient must be a public encryption key.  Keep its private recovery
# key outside both VPS providers and do not place it on either server.
set -euo pipefail
umask 077

DOKKU_APP="${DOKKU_APP:-corvinum}"
POSTGRES_SERVICE="${POSTGRES_SERVICE:-pg-corvinum}"
BACKUP_REMOTE="${BACKUP_REMOTE:?Set BACKUP_REMOTE (user@backup-host)}"
BACKUP_REMOTE_DIR="${BACKUP_REMOTE_DIR:?Set BACKUP_REMOTE_DIR (absolute remote path)}"
BACKUP_GPG_RECIPIENT="${BACKUP_GPG_RECIPIENT:?Set BACKUP_GPG_RECIPIENT}"
BACKUP_SSH_KEY="${BACKUP_SSH_KEY:-}"
MEDIA_SOURCE_DIR="${MEDIA_SOURCE_DIR:-}"
BACKUP_WORK_DIR="${BACKUP_WORK_DIR:-/var/lib/corvinum-backups}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
ARCHIVE_NAME="corvinum-${STAMP}.tar"
ENCRYPTED_NAME="${ARCHIVE_NAME}.gpg"
WORK_DIR="${BACKUP_WORK_DIR}/work-${STAMP}-$$"

die() { echo "backup failed: $*" >&2; exit 1; }
for command in dokku gpg ssh scp sha256sum tar; do
  command -v "$command" >/dev/null 2>&1 || die "required command missing: $command"
done
[[ "$BACKUP_REMOTE_DIR" =~ ^/[A-Za-z0-9._/-]+$ ]] && [[ "$BACKUP_REMOTE_DIR" != *".."* ]] \
  || die "BACKUP_REMOTE_DIR must be an absolute, traversal-free path"
gpg --batch --list-keys "$BACKUP_GPG_RECIPIENT" >/dev/null 2>&1 \
  || die "the backup recipient public key is not available locally"

ssh_args=(-o BatchMode=yes -o StrictHostKeyChecking=yes)
if [ -n "$BACKUP_SSH_KEY" ]; then
  [ -r "$BACKUP_SSH_KEY" ] || die "BACKUP_SSH_KEY is not readable"
  ssh_args+=(-i "$BACKUP_SSH_KEY")
fi

mkdir -p "$BACKUP_WORK_DIR"
mkdir -p "$WORK_DIR"
trap 'rm -rf "$WORK_DIR"' EXIT

echo "Exporting PostgreSQL service ${POSTGRES_SERVICE}..."
dokku postgres:export "$POSTGRES_SERVICE" > "$WORK_DIR/postgres.dump"
[ -s "$WORK_DIR/postgres.dump" ] || die "PostgreSQL export is empty"

# These reports identify the release without disclosing config values.
dokku git:report "$DOKKU_APP" > "$WORK_DIR/release-manifest.txt"
dokku domains:report "$DOKKU_APP" >> "$WORK_DIR/release-manifest.txt"
printf 'created_at_utc=%s\napp=%s\npostgres_service=%s\n' \
  "$STAMP" "$DOKKU_APP" "$POSTGRES_SERVICE" >> "$WORK_DIR/release-manifest.txt"

if [ -n "$MEDIA_SOURCE_DIR" ]; then
  [ -d "$MEDIA_SOURCE_DIR" ] || die "MEDIA_SOURCE_DIR does not exist: $MEDIA_SOURCE_DIR"
  echo "Including configured media volume..."
  tar -C "$MEDIA_SOURCE_DIR" -cf "$WORK_DIR/media.tar" .
fi

tar -C "$WORK_DIR" -cf "$WORK_DIR/$ARCHIVE_NAME" . \
  --exclude="$ARCHIVE_NAME" --exclude="$ENCRYPTED_NAME"
gpg --batch --yes --trust-model always --recipient "$BACKUP_GPG_RECIPIENT" \
  --output "$WORK_DIR/$ENCRYPTED_NAME" --encrypt "$WORK_DIR/$ARCHIVE_NAME"
sha256sum "$WORK_DIR/$ENCRYPTED_NAME" > "$WORK_DIR/${ENCRYPTED_NAME}.sha256"

echo "Uploading encrypted archive..."
ssh "${ssh_args[@]}" "$BACKUP_REMOTE" \
  "mkdir -p '$BACKUP_REMOTE_DIR/daily' '$BACKUP_REMOTE_DIR/monthly'"
scp "${ssh_args[@]}" "$WORK_DIR/$ENCRYPTED_NAME" \
  "$BACKUP_REMOTE:$BACKUP_REMOTE_DIR/daily/${ENCRYPTED_NAME}.partial"
scp "${ssh_args[@]}" "$WORK_DIR/${ENCRYPTED_NAME}.sha256" \
  "$BACKUP_REMOTE:$BACKUP_REMOTE_DIR/daily/${ENCRYPTED_NAME}.sha256.partial"
ssh "${ssh_args[@]}" "$BACKUP_REMOTE" \
  "bash -s -- '$BACKUP_REMOTE_DIR' '$ENCRYPTED_NAME' '${STAMP:6:2}'" <<'REMOTE'
set -eu
backup_dir="$1"
archive="$2"
day_of_month="$3"

cd "$backup_dir/daily"
mv "$archive.partial" "$archive"
mv "$archive.sha256.partial" "$archive.sha256"
sha256sum -c "$archive.sha256"
if [ "$day_of_month" = '01' ]; then
  ln -f "$archive" "../monthly/$archive"
  ln -f "$archive.sha256" "../monthly/$archive.sha256"
fi
prune() {
  directory="$1"
  keep="$2"
  find "$directory" -maxdepth 1 -type f -name 'corvinum-*.tar.gpg' -printf '%T@ %f\n' \
    | sort -n | head -n "-$keep" | cut -d' ' -f2- \
    | while IFS= read -r old; do
        [ -z "$old" ] || rm -f -- "$directory/$old" "$directory/$old.sha256"
      done
}
prune "$backup_dir/daily" 35
prune "$backup_dir/monthly" 12
REMOTE

echo "Encrypted off-site backup completed: ${ENCRYPTED_NAME}"
