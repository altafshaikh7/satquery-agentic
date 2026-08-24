from fastapi import FastAPI

from app.api.routes import health, query, traces
from app.core.config import settings
from app.core.logging import setup_logging


setup_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Agentic Vision-Language Assistant for Remote Sensing",
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to SatQuery AI",
        "status": "running",
        "version": settings.app_version,
    }


app.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
)

app.include_router(
    query.router,
    prefix="/query",
    tags=["Query"],
)

app.include_router(
    traces.router,
    prefix="/traces",
    tags=["Traces"],
)