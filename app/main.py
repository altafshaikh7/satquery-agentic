from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.query import router as query_router
from app.api.routes.traces import router as traces_router


app = FastAPI(
    title="SatQuery AI",
    description="Agentic Vision-Language Assistant for Remote Sensing",
    version="1.0.0",
)


# ==========================================
# CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# API ROUTES
# ==========================================

app.include_router(
    health_router,
    prefix="/health",
    tags=["Health"],
)

app.include_router(
    query_router,
    prefix="/query",
    tags=["Query"],
)

app.include_router(
    traces_router,
    prefix="/traces",
    tags=["Traces"],
)


# ==========================================
# ROOT ENDPOINT
# ==========================================

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "SatQuery AI Backend is running",
        "status": "success",
    }