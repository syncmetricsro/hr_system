#!/usr/bin/env bash
set -euo pipefail

APP_IMAGE="${APP_IMAGE:-jober-platform:ci}"
TEST_IMAGE="${TEST_IMAGE:-jober-platform-test:ci}"
POSTGRES_IMAGE="${POSTGRES_IMAGE:-postgres@sha256:2203e6282d9e7de7c24d7da234e2a744fb325df366a3fd8ed940e8abbee39527}"
NET="${NET:-jober-ci-net}"
JOBER_DB="${JOBER_DB:-jober-ci-db}"
CORVINUM_DB="${CORVINUM_DB:-corvinum-ci-db}"

cleanup() {
  docker rm -f "$JOBER_DB" "$CORVINUM_DB" >/dev/null 2>&1 || true
  docker network rm "$NET" >/dev/null 2>&1 || true
}
trap cleanup EXIT

cleanup

python3 scripts/check_no_node_artifacts.py
python3 scripts/verify_vendor_assets.py

echo "Building production image..."
if [[ "${CI_SKIP_BUILD:-0}" = "1" ]]; then
  docker image inspect "$APP_IMAGE" "$TEST_IMAGE" >/dev/null
else
  docker build --no-cache -t "$APP_IMAGE" .
fi
scripts/check_production_image.sh "$APP_IMAGE"

if [[ "${CI_SKIP_BUILD:-0}" != "1" ]]; then
  echo "Building pinned Python test image..."
  docker build --no-cache -f Dockerfile.playwright-python -t "$TEST_IMAGE" .
fi

docker network create --internal "$NET" >/dev/null
if [[ "$(docker network inspect "$NET" --format '{{.Internal}}')" != "true" ]]; then
  echo "Expected $NET to be an internal Docker network." >&2
  exit 1
fi

docker run -d --name "$JOBER_DB" --network "$NET" \
  -e POSTGRES_DB=jober \
  -e POSTGRES_USER=jober \
  -e POSTGRES_PASSWORD=jober-pass \
  "$POSTGRES_IMAGE" >/dev/null
docker run -d --name "$CORVINUM_DB" --network "$NET" \
  -e POSTGRES_DB=corvinum \
  -e POSTGRES_USER=corvinum \
  -e POSTGRES_PASSWORD=corvinum-pass \
  "$POSTGRES_IMAGE" >/dev/null

for attempt in $(seq 1 30); do
  if docker exec "$JOBER_DB" pg_isready -U jober -d jober >/dev/null 2>&1 \
    && docker exec "$CORVINUM_DB" pg_isready -U corvinum -d corvinum >/dev/null 2>&1; then
    break
  fi
  if [[ "$attempt" = "30" ]]; then
    docker logs "$JOBER_DB" >&2 || true
    docker logs "$CORVINUM_DB" >&2 || true
    echo "PostgreSQL did not become ready." >&2
    exit 1
  fi
  sleep 1
done

run_test_image() {
  docker run --rm \
    -e HOME=/tmp \
    -v "$PWD:/app" \
    -w /app \
    "$TEST_IMAGE" \
    "$@"
}

run_jober() {
  docker run --rm --network "$NET" \
    -e DB_HOST="$JOBER_DB" \
    -e DB_NAME=jober \
    -e DB_USER=jober \
    -e DB_PASSWORD=jober-pass \
    -e HOME=/tmp \
    -e DJANGO_DEBUG=1 \
    --tmpfs /app/media:rw,noexec,nosuid,nodev,mode=1777 \
    -v "$PWD:/app" \
    -w /app \
    "$TEST_IMAGE" \
    "$@"
}

run_corvinum() {
  docker run --rm --network "$NET" \
    -e DB_HOST="$CORVINUM_DB" \
    -e DB_NAME=corvinum \
    -e DB_USER=corvinum \
    -e DB_PASSWORD=corvinum-pass \
    -e HOME=/tmp \
    -e DJANGO_DEBUG=1 \
    -e DJANGO_SETTINGS_MODULE=clients.corvinum_eu.settings \
    --tmpfs /app/media:rw,noexec,nosuid,nodev,mode=1777 \
    -v "$PWD:/app" \
    -w /app \
    "$TEST_IMAGE" \
    "$@"
}

echo "Running Ruff..."
run_test_image ruff check --no-cache core features clients config tests

format_base="${CI_BASE_SHA:-}"
if [[ ! "$format_base" =~ ^[0-9a-f]{40}$ ]] || ! git cat-file -e "$format_base^{commit}" 2>/dev/null; then
  format_base="$(git merge-base HEAD main 2>/dev/null || true)"
fi
if [[ -n "$format_base" ]]; then
  mapfile -t changed_python < <(
    git diff --name-only --diff-filter=ACMR "$format_base" \
      | grep -E '^(core|features|clients|config|tests|scripts)/.*\.py$' \
      || true
  )
  if ((${#changed_python[@]})); then
    run_test_image ruff format --no-cache --check "${changed_python[@]}"
  else
    echo "No changed Python files require a Ruff format check."
  fi
else
  echo "No base revision available; the full Ruff lint gate still ran."
fi

echo "Checking Django and migrations under both clients..."
run_jober python manage.py check
run_jober python manage.py makemigrations --check --dry-run
run_corvinum python manage.py check
run_corvinum python manage.py makemigrations --check --dry-run

echo "Running Jober unit tests..."
run_jober python -m pytest -q -p no:cacheprovider --ignore=tests/e2e

echo "Running CorvinumEU unit tests..."
run_corvinum python -m pytest -q -p no:cacheprovider --ignore=tests/e2e \
  --ds=clients.corvinum_eu.settings -m "not jober_only"

echo "Quality and unit gate passed."
