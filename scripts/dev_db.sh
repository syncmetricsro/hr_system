#!/usr/bin/env bash
set -euo pipefail

POSTGRES_IMAGE="${POSTGRES_IMAGE:-postgres@sha256:2203e6282d9e7de7c24d7da234e2a744fb325df366a3fd8ed940e8abbee39527}"
NET="${DEV_DB_NET:-jober-dev-net}"
DB_CONTAINER="${DEV_DB_CONTAINER:-jober-dev-db}"
DB_VOLUME="${DEV_DB_VOLUME:-jober-dev-db-data}"
ENV_FILE="${DEV_DB_ENV_FILE:-.env.dev-db}"

usage() {
  cat <<EOF
Usage: scripts/dev_db.sh <command>

Commands:
  up          Start digest-pinned local PostgreSQL.
  down        Stop the DB container, preserving the Docker volume.
  reset --yes Delete the DB container and volume, then start fresh.
  status      Show container/network/volume status.
  logs        Follow DB logs.
  url         Print app-container connection settings.
  psql        Open psql inside a temporary digest-pinned Postgres container.

Environment overrides:
  POSTGRES_IMAGE   Default: ${POSTGRES_IMAGE}
  DEV_DB_ENV_FILE  Default: ${ENV_FILE}
EOF
}

ensure_env_file() {
  if [[ -f "$ENV_FILE" ]]; then
    return
  fi

  password="$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(32))
PY
)"
  umask 077
  cat >"$ENV_FILE" <<EOF
POSTGRES_DB=jober
POSTGRES_USER=jober
POSTGRES_PASSWORD=${password}
EOF
  echo "Created ${ENV_FILE}. It is gitignored and contains local-only credentials."
}

load_env() {
  ensure_env_file
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
}

ensure_network() {
  if ! docker network inspect "$NET" >/dev/null 2>&1; then
    docker network create --internal "$NET" >/dev/null
  fi
  internal="$(docker network inspect "$NET" --format '{{.Internal}}')"
  if [[ "$internal" != "true" ]]; then
    echo "Docker network ${NET} exists but is not internal. Refusing to use it." >&2
    exit 1
  fi
}

wait_for_db() {
  for i in $(seq 1 30); do
    if docker exec "$DB_CONTAINER" pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" >/dev/null 2>&1; then
      return
    fi
    sleep 1
    if [[ "$i" = "30" ]]; then
      docker logs "$DB_CONTAINER" >&2 || true
      echo "PostgreSQL did not become ready." >&2
      exit 1
    fi
  done
}

up() {
  load_env
  ensure_network

  if docker inspect "$DB_CONTAINER" >/dev/null 2>&1; then
    if [[ "$(docker inspect -f '{{.State.Running}}' "$DB_CONTAINER")" != "true" ]]; then
      docker start "$DB_CONTAINER" >/dev/null
    fi
  else
    docker volume create "$DB_VOLUME" >/dev/null
    docker run -d \
      --name "$DB_CONTAINER" \
      --network "$NET" \
      --env-file "$ENV_FILE" \
      -v "${DB_VOLUME}:/var/lib/postgresql/data" \
      "$POSTGRES_IMAGE" >/dev/null
  fi

  wait_for_db
  echo "PostgreSQL is ready."
  url
}

down() {
  docker rm -f "$DB_CONTAINER" >/dev/null 2>&1 || true
  echo "Stopped ${DB_CONTAINER}. Volume ${DB_VOLUME} is preserved."
}

reset() {
  if [[ "${1:-}" != "--yes" ]]; then
    echo "Refusing destructive reset without --yes." >&2
    echo "Run: scripts/dev_db.sh reset --yes" >&2
    exit 1
  fi
  docker rm -f "$DB_CONTAINER" >/dev/null 2>&1 || true
  docker volume rm "$DB_VOLUME" >/dev/null 2>&1 || true
  up
}

status() {
  printf 'Container: '
  if docker inspect "$DB_CONTAINER" >/dev/null 2>&1; then
    docker inspect "$DB_CONTAINER" --format '{{.Name}} running={{.State.Running}} image={{.Config.Image}}'
  else
    echo "not-created"
  fi
  printf 'Network:   '
  if docker network inspect "$NET" >/dev/null 2>&1; then
    docker network inspect "$NET" --format '{{.Name}} internal={{.Internal}}'
  else
    echo "not-created"
  fi
  printf 'Volume:    '
  if docker volume inspect "$DB_VOLUME" >/dev/null 2>&1; then
    docker volume inspect "$DB_VOLUME" --format '{{.Name}}'
  else
    echo "not-created"
  fi
  printf 'Env file:  %s\n' "$ENV_FILE"
}

logs() {
  docker logs -f "$DB_CONTAINER"
}

url() {
  load_env
  cat <<EOF
App containers on ${NET}:
  DB_HOST=${DB_CONTAINER}
  DB_PORT=5432
  DB_NAME=${POSTGRES_DB}
  DB_USER=${POSTGRES_USER}

Use --env-file ${ENV_FILE} plus the DB_HOST/DB_PORT values above for app containers.
Use "scripts/dev_db.sh psql" for an interactive local psql session without installing PostgreSQL on the host.
EOF
}

psql_shell() {
  load_env
  ensure_network
  tty_args=(-i)
  if [[ -t 0 && -t 1 ]]; then
    tty_args=(-it)
  fi
  docker run --rm "${tty_args[@]}" \
    --network "$NET" \
    -e PGPASSWORD="$POSTGRES_PASSWORD" \
    "$POSTGRES_IMAGE" \
    psql -h "$DB_CONTAINER" -U "$POSTGRES_USER" "$POSTGRES_DB"
}

case "${1:-}" in
  up) up ;;
  down) down ;;
  reset) shift; reset "${1:-}" ;;
  status) status ;;
  logs) logs ;;
  url) url ;;
  psql) psql_shell ;;
  -h|--help|help|"") usage ;;
  *)
    usage >&2
    exit 1
    ;;
esac
