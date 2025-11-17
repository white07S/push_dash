Backend
=======

Database backends
-----------------

The backend now supports two database backends behind the same `Database` API:

- PostgreSQL (preferred)
- SQLite via APSW (fallback)

On startup the backend will:

1. Try to connect to PostgreSQL.
2. If that fails (driver missing or database unreachable), it will fall back to the local SQLite file `dashboard.db`.

PostgreSQL configuration
------------------------

PostgreSQL is the default when available. Configure it primarily via `backend/config.yaml`:

```yaml
database:
  backend: "postgres"  # or "sqlite"
  path: "dashboard.db"
  postgres:
    host: "localhost"
    port: 5432
    user: "preetam"
    password: "preetam123"
    db: "main"
    connect_timeout: 5
```

On a successful Postgres connection the backend will:

- Ensure the schema `analytics` exists.
- Set `search_path` to `analytics, public`.
- Create all required tables and indexes in the `analytics` schema if they do not already exist.

Environment variables can still override individual settings if needed:

- `DB_BACKEND` (overrides `database.backend`)
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`,
  `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_CONNECT_TIMEOUT`

No separate migration scripts are required; the schema is created programmatically on startup.

For example, when running with Docker:

```bash
docker run \
  -e POSTGRES_USER=preetam \
  -e POSTGRES_PASSWORD=preetam123 \
  -e POSTGRES_DB=main \
  postgres:16
```

Then start the backend container with the same environment variables.

Forcing SQLite
--------------

If you want to force the backend to use SQLite (and skip Postgres attempts), set:

```bash
export DB_BACKEND=sqlite
```

In all cases, the rest of the code continues to use the existing `db.get_db()` helper and does not need to change when switching between backends.
