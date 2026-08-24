from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def traces_info():
    return {
        "message": "Trace system is initialized."
    }