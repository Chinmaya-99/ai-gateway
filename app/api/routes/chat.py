from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def chat():
    return {"message": "chat route placeholder"}
