from fastapi import APIRouter

router = APIRouter()

@router.post("/embed")
def create_embedding():
    return {"message": "embedding route placeholder"}
