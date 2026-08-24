from fastapi import APIRouter

from app.schemas.query import QueryRequest
from app.schemas.response import QueryResponse
from app.services.query_service import QueryService


router = APIRouter()

query_service = QueryService()


@router.get("/")
async def query_info():
    return {
        "message": (
            "Submit a POST request with a remote sensing query "
            "and optional image file paths."
        )
    }


@router.post("/", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
):
    return query_service.process(request)