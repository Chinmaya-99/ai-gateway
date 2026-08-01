from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def create_embedding():
    return {"message": "embedding route placeholder"}
