from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def cache_status():
    return {"message": "cache route placeholder"}
