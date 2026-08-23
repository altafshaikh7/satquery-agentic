from fastapi import APIRouter

from app.core.config import settings


router = APIRouter()


@router.get("/")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "llm_provider": settings.llm_provider,
    }