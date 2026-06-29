from fastapi import APIRouter

router = APIRouter()

@router.post("/embed")
async def create_embedding():
    return {"message": "embedding route placeholder"}
