#!/usr/bin/env bash
#
# Backup + restore drill (deployment-plan.md: monthly, documented in
# deployment_journal.md). Dumps a Postgres database, restores it into a
# scratch database on the same server, and proves the restore by comparing
# per-table row counts. Works against the local demo DB containers today and
# a `dokku postgres:*` service via DRILL_EXEC later.
#
#   scripts/backup_restore_drill.sh                    # jober demo DB
#   DB_CONTAINER=corvinum-dev-db DB_NAME=corvinum DB_USER=corvinum \
#     scripts/backup_restore_drill.sh                  # corvinum demo DB
#
# The dump file is kept under backups/ (gitignored) with a timestamped name —
# copy it off-site per the deployment plan.
set -euo pipefail

DB_CONTAINER="${DB_CONTAINER:-jober-dev-db}"
DB_NAME="${DB_NAME:-jober}"
DB_USER="${DB_USER:-$(docker exec "$DB_CONTAINER" printenv POSTGRES_USER)}"
SCRATCH="${DB_NAME}_restore_drill"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="backups"
DUMP="$OUT_DIR/${DB_NAME}-${STAMP}.dump"

mkdir -p "$OUT_DIR"

echo "1/4 Dumping $DB_NAME from $DB_CONTAINER ..."
docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" -Fc "$DB_NAME" > "$DUMP"
[ -s "$DUMP" ] || { echo "FAIL: dump is empty" >&2; exit 1; }
echo "  dump: $DUMP ($(du -h "$DUMP" | cut -f1))"

echo "2/4 Restoring into scratch database $SCRATCH ..."
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -q -c "DROP DATABASE IF EXISTS ${SCRATCH}"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -q -c "CREATE DATABASE ${SCRATCH}"
docker exec -i "$DB_CONTAINER" pg_restore -U "$DB_USER" -d "$SCRATCH" --no-owner < "$DUMP"

echo "3/4 Comparing per-table row counts ..."
counts() {
  docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$1" -At -c \
    "SELECT relname || '=' || n_live_tup FROM pg_stat_user_tables ORDER BY relname"
}
# n_live_tup is an estimate; count precisely via a generated query instead.
precise_counts() {
  docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$1" -At -c \
    "SELECT string_agg(format('SELECT %L || ''='' || count(*) FROM %I', tablename, tablename), ' UNION ALL ' ORDER BY tablename) FROM pg_tables WHERE schemaname='public'" |
  { read -r q; docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$1" -At -c "$q"; } | sort
}
orig="$(precise_counts "$DB_NAME")"
rest="$(precise_counts "$SCRATCH")"
if [ "$orig" != "$rest" ]; then
  echo "FAIL: restored row counts differ from the source:" >&2
  diff <(echo "$orig") <(echo "$rest") >&2 || true
  exit 1
fi
tables="$(echo "$orig" | grep -c '=' || true)"
rows="$(echo "$orig" | awk -F= '{s+=$2} END {print s}')"
echo "  identical: $tables tables, $rows total rows"

echo "4/4 Dropping scratch database ..."
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -q -c "DROP DATABASE ${SCRATCH}"

echo "Backup/restore drill PASSED — record this run in deployment_journal.md"
echo "  dump kept at: $DUMP (copy off-site per deployment-plan.md)"
