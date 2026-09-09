import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from src.api.urls import router as urls_router
from src.db import models  # noqa: F401 - registers models on Base.metadata
from src.db.session import Base, engine

app = FastAPI()
logger = logging.getLogger(__name__)


@app.on_event("startup")
def on_startup():
    # Don't crash the process if the DB isn't reachable yet (e.g. Postgres
    # Pod not up when this container starts) - /readyz is the source of
    # truth on DB health, and Kubernetes uses it to gate traffic instead of
    # restarting this container.
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError:
        logger.warning("Database unavailable at startup; skipping table creation")


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/healthz")
async def read_health():
    return {"status": "healthy"}

@app.get("/readyz")
async def read_ready():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        return JSONResponse(status_code=503, content={"status": "not ready"})
    return {"status": "ready"}

# Auto-instruments request count/latency/status codes for every route, and
# exposes them at GET /metrics for Prometheus to scrape. Registered here,
# before include_router, for the same reason as / , /healthz, /readyz above:
# urls_router's GET /{short_code} is a catch-all that would otherwise shadow
# /metrics (confirmed by testing: it did, returning 422 since "metrics" is
# 7 characters and fails the short_code length check).
Instrumentator().instrument(app).expose(app)

# Included last: urls_router's GET /{short_code} is a catch-all for any
# single path segment, so it must be registered after the literal routes
# above or it would shadow them (e.g. /healthz would be treated as a short
# code and 404).
app.include_router(urls_router)

# This block only runs via `python -m src.main` (way 1 below). It's skipped
# when the app is imported by uvicorn/fastapi CLI (ways 2 and 3), since they
# import `app` directly rather than executing this file as __main__.
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)