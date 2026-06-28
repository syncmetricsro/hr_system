#!/usr/bin/env bash
set -euo pipefail

PLAYWRIGHT_VERSION="${PLAYWRIGHT_VERSION:-1.60.0}"
PLAYWRIGHT_BASE_IMAGE="${PLAYWRIGHT_BASE_IMAGE:-mcr.microsoft.com/playwright/python:v1.60.0-noble@sha256:8ff591d613b01c884cc488339ed4318b4513eaf0c57a164a878ba49e70e3f384}"
PLAYWRIGHT_TEST_IMAGE="${PLAYWRIGHT_TEST_IMAGE:-jober-platform-playwright:phase0}"
APP_IMAGE="${APP_IMAGE:-jober-platform:phase0}"
POSTGRES_IMAGE="${POSTGRES_IMAGE:-postgres@sha256:2203e6282d9e7de7c24d7da234e2a744fb325df366a3fd8ed940e8abbee39527}"
NET="${NET:-jober-phase0-pw-net}"
DB="${DB:-jober-phase0-pw-db}"
APP="${APP:-jober-phase0-app}"

cleanup() {
  docker rm -f "$APP" >/dev/null 2>&1 || true
  docker rm -f "$DB" >/dev/null 2>&1 || true
  docker network rm "$NET" >/dev/null 2>&1 || true
}
trap cleanup EXIT

cleanup
if ! grep -Eq "^playwright==${PLAYWRIGHT_VERSION}[[:space:]]" requirements/test.lock; then
  echo "requirements/test.lock must pin playwright==${PLAYWRIGHT_VERSION} to match ${PLAYWRIGHT_BASE_IMAGE}" >&2
  exit 1
fi

docker network create --internal "$NET" >/dev/null
network_internal="$(docker network inspect "$NET" --format '{{.Internal}}')"
if [[ "$network_internal" != "true" ]]; then
  echo "Expected $NET to be an internal Docker network, got Internal=$network_internal" >&2
  exit 1
fi

docker build \
  --build-arg "BUILDKIT_INLINE_CACHE=0" \
  -f Dockerfile.playwright-python \
  -t "$PLAYWRIGHT_TEST_IMAGE" \
  . >/tmp/jober-playwright-build.log

docker run -d --name "$DB" --network "$NET" \
  -e POSTGRES_DB=jober \
  -e POSTGRES_USER=jober \
  -e POSTGRES_PASSWORD=jober-pass \
  "$POSTGRES_IMAGE" >/dev/null

for i in $(seq 1 30); do
  if docker exec "$DB" pg_isready -U jober -d jober >/dev/null 2>&1; then
    break
  fi
  sleep 1
  if [[ "$i" = "30" ]]; then
    docker logs "$DB"
    exit 1
  fi
done

docker run --rm --network "$NET" \
  -e DJANGO_SECRET_KEY=phase0-test-secret \
  -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,testserver,"$APP" \
  -e DB_NAME=jober \
  -e DB_USER=jober \
  -e DB_PASSWORD=jober-pass \
  -e DB_HOST="$DB" \
  -e DB_PORT=5432 \
  "$APP_IMAGE" python manage.py migrate --noinput

docker run --rm --network "$NET" \
  -e DJANGO_SECRET_KEY=phase0-test-secret \
  -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,testserver,"$APP" \
  -e DB_NAME=jober \
  -e DB_USER=jober \
  -e DB_PASSWORD=jober-pass \
  -e DB_HOST="$DB" \
  -e DB_PORT=5432 \
  "$APP_IMAGE" python manage.py seed_demo

docker run -d --name "$APP" --network "$NET" \
  -e DJANGO_SECRET_KEY=phase0-test-secret \
  -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,testserver,"$APP" \
  -e DJANGO_SECURE_SSL_REDIRECT=0 \
  -e DJANGO_SESSION_COOKIE_SECURE=0 \
  -e DJANGO_CSRF_COOKIE_SECURE=0 \
  -e DB_NAME=jober \
  -e DB_USER=jober \
  -e DB_PASSWORD=jober-pass \
  -e DB_HOST="$DB" \
  -e DB_PORT=5432 \
  "$APP_IMAGE" >/dev/null

for i in $(seq 1 30); do
  if docker run --rm --network "$NET" "$PLAYWRIGHT_TEST_IMAGE" python - <<PY >/dev/null 2>&1
import urllib.request
with urllib.request.urlopen("http://$APP:8000/healthz/", timeout=2) as response:
    body = response.read().decode()
    raise SystemExit(0 if response.status == 200 and body == "ok" else 1)
PY
  then
    break
  fi
  sleep 1
  if [[ "$i" = "30" ]]; then
    docker logs "$APP"
    exit 1
  fi
done

docker run --rm --network "$NET" \
  -e BASE_URL="http://$APP:8000" \
  "$PLAYWRIGHT_TEST_IMAGE" sh -eu -c '
    for binary in node npm pnpm yarn; do
      if command -v "$binary" >/dev/null 2>&1; then
        echo "Forbidden test image binary present on PATH: $binary" >&2
        exit 1
      fi
    done
    test "${PLAYWRIGHT_BROWSERS_PATH:-}" = "/ms-playwright"
    pytest -c tests/e2e/pytest.ini tests/e2e/test_shell_smoke.py --browser chromium
  '
