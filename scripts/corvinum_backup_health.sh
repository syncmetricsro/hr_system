#!/usr/bin/env bash
# Verify that the encrypted Corvinum off-site backup is current and that the
# Contabo target remains below its 60% planning threshold.  It does not read
# archive contents and does not need a decryption key.
set -euo pipefail

BACKUP_REMOTE="${BACKUP_REMOTE:?Set BACKUP_REMOTE (user@backup-host)}"
BACKUP_REMOTE_DIR="${BACKUP_REMOTE_DIR:?Set BACKUP_REMOTE_DIR (absolute remote path)}"
BACKUP_SSH_KEY="${BACKUP_SSH_KEY:-}"
BACKUP_MAX_AGE_HOURS="${BACKUP_MAX_AGE_HOURS:-26}"
BACKUP_MAX_USAGE_PERCENT="${BACKUP_MAX_USAGE_PERCENT:-60}"

die() { echo "backup health check failed: $*" >&2; exit 1; }
command -v ssh >/dev/null 2>&1 || die "required command missing: ssh"
[[ "$BACKUP_REMOTE_DIR" =~ ^/[A-Za-z0-9._/-]+$ ]] && [[ "$BACKUP_REMOTE_DIR" != *".."* ]] \
  || die "BACKUP_REMOTE_DIR must be an absolute, traversal-free path"
[[ "$BACKUP_MAX_AGE_HOURS" =~ ^[0-9]+$ ]] || die "BACKUP_MAX_AGE_HOURS must be an integer"
[[ "$BACKUP_MAX_USAGE_PERCENT" =~ ^[0-9]+$ ]] || die "BACKUP_MAX_USAGE_PERCENT must be an integer"

ssh_args=(-o BatchMode=yes -o StrictHostKeyChecking=yes)
if [ -n "$BACKUP_SSH_KEY" ]; then
  [ -r "$BACKUP_SSH_KEY" ] || die "BACKUP_SSH_KEY is not readable"
  ssh_args+=(-i "$BACKUP_SSH_KEY")
fi

result="$(ssh "${ssh_args[@]}" "$BACKUP_REMOTE" "
  set -eu
  latest=\$(find '$BACKUP_REMOTE_DIR/daily' -maxdepth 1 -type f -name 'corvinum-*.tar.gpg' -printf '%T@\\n' | sort -nr | head -n 1)
  [ -n \"\$latest\" ] || exit 42
  now=\$(date +%s)
  age=\$((now - \${latest%.*}))
  usage=\$(df -P '$BACKUP_REMOTE_DIR' | awk 'NR == 2 {gsub(/%/, \"\", \$5); print \$5}')
  printf '%s %s\\n' \"\$age\" \"\$usage\"
")" || die "cannot read the remote backup status"
read -r age_seconds usage_percent <<< "$result"
[ -n "${age_seconds:-}" ] && [ -n "${usage_percent:-}" ] || die "remote status was incomplete"
max_age_seconds=$((BACKUP_MAX_AGE_HOURS * 3600))
[ "$age_seconds" -le "$max_age_seconds" ] || die "newest successful backup is older than ${BACKUP_MAX_AGE_HOURS} hours"
[ "$usage_percent" -lt "$BACKUP_MAX_USAGE_PERCENT" ] || die "backup target is ${usage_percent}% full (threshold: ${BACKUP_MAX_USAGE_PERCENT}%)"
echo "Backup health OK: newest archive is $((age_seconds / 3600))h old; target usage ${usage_percent}%"
