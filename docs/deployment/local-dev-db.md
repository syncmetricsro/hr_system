# Local Development PostgreSQL

Last updated: 2026-06-17

Use `scripts/dev_db.sh` for workstation PostgreSQL. It does not install PostgreSQL on the host.

## Properties

- Image: `postgres@sha256:2203e6282d9e7de7c24d7da234e2a744fb325df366a3fd8ed940e8abbee39527`.
- Container: `jober-dev-db`.
- Network: `jober-dev-net`, created with `--internal`.
- Volume: `jober-dev-db-data`.
- Host DB port: none. The database is reachable only from containers on `jober-dev-net`.
- Credentials file: `.env.dev-db`, generated locally, mode `0600`, gitignored by `.env.*`.

## Commands

```bash
scripts/dev_db.sh up
scripts/dev_db.sh status
scripts/dev_db.sh url
scripts/dev_db.sh psql
scripts/dev_db.sh down
scripts/dev_db.sh reset --yes
```

`down` removes the container but preserves the Docker volume. `reset --yes` deletes the container and volume and starts with a fresh database.

App containers should join `jober-dev-net` and use:

```text
DB_HOST=jober-dev-db
DB_PORT=5432
```

For local database inspection, use `scripts/dev_db.sh psql`; it starts a temporary digest-pinned PostgreSQL client container on the same internal network.
