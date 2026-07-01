from fastapi import APIRouter, Request
from fastapi import FastAPI
from app.models.request_models import QueryRequest
from app.services.cache.cache_manager import CacheManager
from fastapi import HTTPException


router = APIRouter()

def get_cache_manager(request: Request) -> CacheManager:
    return request.app.state.cache_manager


@router.post("/")
async def chat(request: Request, body: QueryRequest):
    query = body.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="User message is empty.")

    manager = get_cache_manager(request)
    result = await manager.handle(query=query)
    return result
