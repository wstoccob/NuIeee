# NU IEEE Backend

Backend for the **Nazarbayev University IEEE Student Branch** website.
FastAPI + PostgreSQL + MinIO. The frontend lives in
[nuieee-client](https://github.com/wstoccob/nuieee-client) and deploys on Vercel.

## Stack

| | |
|---|---|
| Python | 3.13 |
| Framework | FastAPI |
| Database | PostgreSQL 16 via SQLAlchemy 2 (async) + asyncpg |
| Migrations | Alembic |
| Auth | JWT (PyJWT) with Argon2 password hashing |
| Object storage | MinIO, presigned uploads |
| Tooling | uv, ruff, pytest |

## Layout

```
src/
  main.py          app entrypoint and middleware
  core/            config, database session, errors, security (jwt, passwords)
  models/          SQLAlchemy tables
  schemas/         Pydantic request and response models
  services/        business logic as plain async functions
  api/             dependencies and routers
alembic/           migrations
scripts/           one-off operational scripts
tests/             pytest suite
```

Services are modules of functions rather than classes: there is no per-request state
worth holding, so a class would only add indirection.

## Running locally

```bash
uv sync --group dev
cp .env.example .env          # then edit
docker compose up -d db minio # or point DATABASE_URL at your own Postgres
uv run alembic upgrade head
uv run uvicorn main:app --app-dir src --reload
```

API docs at http://localhost:8000/docs

The whole stack (API included) runs with `docker compose up -d`.

## Checks

```bash
uv run ruff check src tests scripts alembic
uv run ruff format --check src tests scripts alembic
uv run pytest -q
```

## API

Roles are hierarchical: `superadmin` satisfies anything `admin` can do.

| Method | Path | Access |
|---|---|---|
| POST | `/api/auth/login` | public |
| GET | `/api/auth/me` | authenticated |
| GET | `/api/events` (`?limit=N`) | public |
| GET | `/api/events/{id}` | public |
| POST | `/api/events` | admin |
| PUT | `/api/events/{id}` | admin |
| DELETE | `/api/events/{id}` | admin |
| POST | `/api/storage/upload-url?filename=` | admin |
| DELETE | `/api/storage/objects?key=` | admin |
| GET | `/api/users`, `/api/users/{id}` | superadmin |
| POST | `/api/users` | superadmin |
| DELETE | `/api/users/{id}` | superadmin |
| GET | `/health` | public |

There is no public registration endpoint. Accounts are created by a superadmin.

Photo uploads are two-step: ask `/api/storage/upload-url` for a presigned URL, PUT the
file straight to MinIO, then send the returned `publicUrl` as part of the event payload.

## Deployment

Pushing to `main` runs lint and tests, builds an image tagged with the commit SHA, pushes
it to GHCR, syncs the VPS from git, runs migrations as a one-shot container, then starts
the API and polls `/health`, rolling back automatically if it does not come up.

Never edit `docker-compose.prod.yml` on the server: the deploy resets the checkout to
`origin/main` and your change would be lost.

Secrets live in `.env` on the VPS and are not in this repository.
