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

```bash
uvicorn src.main:app --reload
```

## Endpoints

- `GET /healthz` - liveness check
- `GET /readyz` - readiness check (verifies DB connection)

## TODO

- [ ] Document URL shortener endpoints as they're added
- [ ] Add testing instructions
- [ ] Add deployment notes
