# App Delivery Pipeline

FastAPI service backed by PostgreSQL (SQLAlchemy).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then set DATABASE_URL
```

## Database

This project expects a local PostgreSQL server (installed via Homebrew, e.g. `brew install postgresql@16`).

```bash
# Start Postgres (runs in the background, survives reboots)
brew services start postgresql@16

# Check it's running
brew services list | grep postgresql   # should show "started"
pg_isready                             # should print "accepting connections"

# Stop it
brew services stop postgresql@16
```

Create the database once (name must match `DATABASE_URL` in `.env`):

```bash
createdb app_delivery_pipeline
```

## Run

Three equivalent ways to start the server, all from the project root:

```bash
# 1. Plain python — runs src/main.py's __main__ block, which calls uvicorn.run() internally
python -m src.main

# 2. FastAPI CLI — wraps uvicorn, adds auto-reload and a dev landing page
fastapi dev src/main.py

# 3. Uvicorn CLI directly — most explicit, used in production
uvicorn src.main:app --reload
```

All three end up running the same `app` object on `http://localhost:8000`. Use `python -m src.main`
for quick manual checks, `fastapi dev` for day-to-day local development, and the bare `uvicorn`
command (without `--reload`) for production.

## Endpoints

- `GET /healthz` - liveness check
- `GET /readyz` - readiness check (verifies DB connection)
- `GET /urls` - list all shortened URLs
- `POST /urls` - create a shortened URL from `{"original_url": "..."}`, returns the new `short_code`
- `GET /{short_code}` - redirect to the original URL and record a click
- `GET /urls/{short_code}/stats` - total click count and recent click timestamps

## Testing

```bash
pip install -r requirements-dev.txt
createdb app_delivery_pipeline_test   # first time only
pytest -v
```

Tests run against a real Postgres database (`app_delivery_pipeline_test`),
isolated from your dev data — no mocking. `pytest` uses `TestClient` to call
the app directly in-process, so no server needs to be running first.

## Fixed Issues

- **Table creation race with Postgres startup in Kubernetes** — fixed via an
  `initContainers` step in the Helm chart that waits for Postgres before the
  app starts.

## TODO
- [ ] Add deployment notes