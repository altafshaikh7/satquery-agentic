from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def query_info():
    return {
        "message": "SatQuery query API is ready",
    }