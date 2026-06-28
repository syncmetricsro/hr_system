# Running the Jober web app locally (testing & customer demos)

A one-command way to start the real web app on your machine so human testers can
click through it and you can show it to the customer. It runs the production
Docker image plus PostgreSQL and publishes the app at **http://localhost:8000**.

> Local demo only. The helper serves the production image over plain HTTP, so it
> turns off HTTPS redirect and secure cookies. Never use those settings on a real
> deployment. The data is fictional and reset each time you start fresh.

## Prerequisites

- Docker installed and running (`docker --version`).
- Run commands from the repository root (`/home/disane/Development/HR_System`).

## Start

```bash
scripts/dev_app.sh up
```

This builds the image if needed, starts PostgreSQL, applies migrations, seeds
fictional demo users, and starts the app. When it finishes it prints the URL and
the logins. Open **http://localhost:8000**.

## Log in

All demo accounts use the password **`demo-jober-2026`**:

| Role | Email |
|---|---|
| Manager / Administrator | `manazer@demo.jober.test` |
| Recruiter | `naborar@demo.jober.test` |
| Coordinator | `koordinator@demo.jober.test` |
| Observer | `pozorovatel@demo.jober.test` |

Tip for demos: the **Manager** account sees the most (e.g. the "Spravovať
projekty" action); the **Observer** account is read-only — a good before/after to
show role-based access.

## Other commands

```bash
scripts/dev_app.sh status    # is it running? what URL?
scripts/dev_app.sh logs      # follow the app log (Ctrl+C to stop watching)
scripts/dev_app.sh rebuild   # rebuild the image after code changes, then restart
```

## Stop

```bash
scripts/dev_app.sh down
```

Removes the app, the database, and the Docker network. Because the database is
not persisted, the next `up` starts clean and re-seeds the demo users.

## Notes

- Default port is 8000. To use another: `PORT=9000 scripts/dev_app.sh up`.
- To demo a specific built image: `APP_IMAGE=jober-platform:phase1 scripts/dev_app.sh up`.
- Languages: the SK/HU/UK switch changes the URL prefix; non-Slovak text falls
  back to Slovak until translation catalogs are compiled (see the production
  readiness journal).
