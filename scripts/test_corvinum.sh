#!/usr/bin/env bash
#
# Corvinum-flags test lane (Stage D: "the suite passes under EACH client's
# flag set"). Runs the shared/portable unit tests under
# clients.corvinum_eu.settings against a dedicated `corvinum` database on the
# dev Postgres. Jober-specific tests carry @pytest.mark.jober_only and are
# excluded here; feature-not-installed modules skip themselves at import.
#
# Usage: scripts/test_corvinum.sh   (dev DB must be up: scripts/dev_db.sh up
#        or the dev_app stack — password is read from the container env)
set -euo pipefail

NET=jober-dev-net
DB=jober-dev-db
IMAGE="${TEST_IMAGE:-jober-test:phase4}"

DB_PASSWORD="$(docker exec "$DB" printenv POSTGRES_PASSWORD)"

docker run --rm --network "$NET" \
  -e DB_HOST="$DB" -e DB_NAME=corvinum -e DB_USER="$(docker exec "$DB" printenv POSTGRES_USER)" \
  -e DB_PASSWORD="$DB_PASSWORD" \
  -e HOME=/tmp -e DJANGO_DEBUG=1 \
  -v "$PWD":/app -w /app --user "$(id -u):$(id -g)" \
  "$IMAGE" python -m pytest -q -p no:cacheprovider --ignore=tests/e2e \
  --ds=clients.corvinum_eu.settings -m "not jober_only" "$@"
