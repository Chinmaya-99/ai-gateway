from fastapi import APIRouter
from fastapi import FastAPI
from ai_gateway.app.services.cache.cache_manager import CacheManager
from ai_gateway.app.models.request_models import QueryRequest
from fastapi import HTTPException


router = APIRouter()


cache_manager=None
def get_cache_manager()->CacheManager:
    global cache_manager
    if cache_manager is None:
        cache_manager = CacheManager()
    return cache_manager



@router.post("/")
def chat(request: QueryRequest):
    print("Received request:", request)

    # # Extract the last user message (standard pattern for chat APIs)
    # user_messages = [m for m in request.messages if m.role == "user"]
 
    # if not user_messages:
    #     raise HTTPException(status_code=400, detail="No user message found in request.")
 
    # query = user_messages[-1].content.strip()
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="User message is empty.")
    manager = get_cache_manager()
    result = manager.handle(query=query)
    return result
