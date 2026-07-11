#!/usr/bin/env bash
#
# Full-feature browser e2e: builds the current app + Playwright images, seeds
# both client demos, serves both apps, and runs the whole tests/e2e suite.
#
# Mirrors scripts/playwright_smoke.sh but targets the CURRENT code (not phase0)
# and seeds enough data for the finance/accommodation/equipment/reports pages.
set -euo pipefail

PLAYWRIGHT_VERSION="${PLAYWRIGHT_VERSION:-1.60.0}"
PLAYWRIGHT_BASE_IMAGE="${PLAYWRIGHT_BASE_IMAGE:-mcr.microsoft.com/playwright/python:v1.60.0-noble@sha256:8ff591d613b01c884cc488339ed4318b4513eaf0c57a164a878ba49e70e3f384}"
PLAYWRIGHT_TEST_IMAGE="${PLAYWRIGHT_TEST_IMAGE:-jober-platform-playwright:e2e}"
APP_IMAGE="${APP_IMAGE:-jober-platform:e2e}"
POSTGRES_IMAGE="${POSTGRES_IMAGE:-postgres@sha256:2203e6282d9e7de7c24d7da234e2a744fb325df366a3fd8ed940e8abbee39527}"
NET="${NET:-jober-e2e-net}"
DB="${DB:-jober-e2e-db}"
APP="${APP:-jober-e2e-app}"
CORVINUM_DB="${CORVINUM_DB:-corvinum-e2e-db}"
CORVINUM_APP="${CORVINUM_APP:-corvinum-e2e-app}"

cleanup() {
  docker rm -f "$APP" >/dev/null 2>&1 || true
  docker rm -f "$DB" >/dev/null 2>&1 || true
  docker rm -f "$CORVINUM_APP" >/dev/null 2>&1 || true
  docker rm -f "$CORVINUM_DB" >/dev/null 2>&1 || true
  docker network rm "$NET" >/dev/null 2>&1 || true
}
trap cleanup EXIT

cleanup
if ! grep -Eq "^playwright==${PLAYWRIGHT_VERSION}[[:space:]]" requirements/test.lock; then
  echo "requirements/test.lock must pin playwright==${PLAYWRIGHT_VERSION} to match ${PLAYWRIGHT_BASE_IMAGE}" >&2
  exit 1
fi

echo "Building current app image ($APP_IMAGE) ..."
docker build -t "$APP_IMAGE" . >/tmp/jober-e2e-app-build.log 2>&1 || { tail -30 /tmp/jober-e2e-app-build.log; exit 1; }

echo "Building Playwright test image ($PLAYWRIGHT_TEST_IMAGE) ..."
docker build -f Dockerfile.playwright-python -t "$PLAYWRIGHT_TEST_IMAGE" . >/tmp/jober-e2e-pw-build.log 2>&1 || { tail -30 /tmp/jober-e2e-pw-build.log; exit 1; }

docker network create --internal "$NET" >/dev/null
if [[ "$(docker network inspect "$NET" --format '{{.Internal}}')" != "true" ]]; then
  echo "Expected $NET to be an internal Docker network." >&2
  exit 1
fi

docker run -d --name "$DB" --network "$NET" \
  -e POSTGRES_DB=jober -e POSTGRES_USER=jober -e POSTGRES_PASSWORD=jober-pass \
  "$POSTGRES_IMAGE" >/dev/null
docker run -d --name "$CORVINUM_DB" --network "$NET" \
  -e POSTGRES_DB=corvinum -e POSTGRES_USER=corvinum -e POSTGRES_PASSWORD=corvinum-pass \
  "$POSTGRES_IMAGE" >/dev/null

for i in $(seq 1 30); do
  if docker exec "$DB" pg_isready -U jober -d jober >/dev/null 2>&1 \
    && docker exec "$CORVINUM_DB" pg_isready -U corvinum -d corvinum >/dev/null 2>&1; then break; fi
  sleep 1
  [[ "$i" = "30" ]] && { docker logs "$DB"; exit 1; }
done

run_manage() {
  docker run --rm --network "$NET" \
    -e DJANGO_SECRET_KEY=e2e-test-secret \
    -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,testserver,"$APP" \
    -e DB_NAME=jober -e DB_USER=jober -e DB_PASSWORD=jober-pass -e DB_HOST="$DB" -e DB_PORT=5432 \
    "$APP_IMAGE" python manage.py "$@"
}

run_manage_corvinum() {
  docker run --rm --network "$NET" \
    -e DJANGO_SETTINGS_MODULE=clients.corvinum_eu.production \
    -e DJANGO_SECRET_KEY=e2e-test-secret \
    -e DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend \
    -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,testserver,"$CORVINUM_APP" \
    -e DB_NAME=corvinum -e DB_USER=corvinum -e DB_PASSWORD=corvinum-pass \
    -e DB_HOST="$CORVINUM_DB" -e DB_PORT=5432 \
    "$APP_IMAGE" python manage.py "$@"
}

echo "Migrating + seeding ..."
run_manage migrate --noinput
run_manage seed_demo
run_manage seed_people
run_manage seed_logistics
run_manage seed_questionnaire
run_manage seed_finance
run_manage_corvinum migrate --noinput
run_manage_corvinum seed_corvinum_demo

docker run -d --name "$APP" --network "$NET" \
  -e DJANGO_SECRET_KEY=e2e-test-secret \
  -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,testserver,"$APP" \
  -e DJANGO_SECURE_SSL_REDIRECT=0 \
  -e DJANGO_SESSION_COOKIE_SECURE=0 \
  -e DJANGO_CSRF_COOKIE_SECURE=0 \
  -e DB_NAME=jober -e DB_USER=jober -e DB_PASSWORD=jober-pass -e DB_HOST="$DB" -e DB_PORT=5432 \
  "$APP_IMAGE" >/dev/null

docker run -d --name "$CORVINUM_APP" --network "$NET" \
  -e DJANGO_SETTINGS_MODULE=clients.corvinum_eu.production \
  -e DJANGO_SECRET_KEY=e2e-test-secret \
  -e DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend \
  -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,testserver,"$CORVINUM_APP" \
  -e DJANGO_SECURE_SSL_REDIRECT=0 \
  -e DJANGO_SESSION_COOKIE_SECURE=0 \
  -e DJANGO_CSRF_COOKIE_SECURE=0 \
  -e DB_NAME=corvinum -e DB_USER=corvinum -e DB_PASSWORD=corvinum-pass \
  -e DB_HOST="$CORVINUM_DB" -e DB_PORT=5432 \
  "$APP_IMAGE" >/dev/null

for i in $(seq 1 30); do
  if docker run --rm -i --network "$NET" "$PLAYWRIGHT_TEST_IMAGE" python - <<PY >/dev/null 2>&1
import urllib.request
for url in ("http://$APP:8000/healthz/", "http://$CORVINUM_APP:8000/healthz/"):
    with urllib.request.urlopen(url, timeout=2) as r:
        if r.status != 200 or r.read().decode() != "ok":
            raise SystemExit(1)
PY
  then break; fi
  sleep 1
  [[ "$i" = "30" ]] && { docker logs "$APP"; docker logs "$CORVINUM_APP"; exit 1; }
done

docker run --rm --network "$NET" \
  -e BASE_URL="http://$APP:8000" \
  -e CORVINUM_BASE_URL="http://$CORVINUM_APP:8000" \
  "$PLAYWRIGHT_TEST_IMAGE" sh -eu -c '
    for binary in node npm pnpm yarn; do
      if command -v "$binary" >/dev/null 2>&1; then
        echo "Forbidden test image binary present on PATH: $binary" >&2
        exit 1
      fi
    done
    test "${PLAYWRIGHT_BROWSERS_PATH:-}" = "/ms-playwright"
    pytest -c tests/e2e/pytest.ini tests/e2e --browser chromium
  '
