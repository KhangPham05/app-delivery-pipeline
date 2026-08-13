import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from src.db import models  # noqa: F401 - registers models on Base.metadata
from src.db.session import Base, engine

app = FastAPI()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


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

# This block only runs via `python -m src.main` (way 1 below). It's skipped
# when the app is imported by uvicorn/fastapi CLI (ways 2 and 3), since they
# import `app` directly rather than executing this file as __main__.
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)