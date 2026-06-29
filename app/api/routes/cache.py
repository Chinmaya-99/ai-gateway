from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def cache_status():
    return {"message": "cache route placeholder"}
