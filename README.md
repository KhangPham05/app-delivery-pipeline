# App Delivery Pipeline

FastAPI service backed by PostgreSQL (SQLAlchemy).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then set DATABASE_URL
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

## TODO

- [ ] Document URL shortener endpoints as they're added
- [ ] Add testing instructions
- [ ] Add deployment notes
