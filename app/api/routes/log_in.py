from app.services.auth.auth_service import AuthService
from app.models.user_log_req_model import register_request, login_request
from fastapi import APIRouter, Request
from fastapi import FastAPI
from fastapi import HTTPException


auth_services = AuthService()
router = APIRouter()
@router.post("/register")
async def register(data: register_request):
    auth_services.register_user(
        data.username,
        data.password
    )
    return {"message": "Registration successful"}
    
@router.post("/login")
async def login(data: login_request):

    success = auth_services.login_user(
        data.username,
        data.password
    )

    if not success:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    return {"message": "Login successful"}