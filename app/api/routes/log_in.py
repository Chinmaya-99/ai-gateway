from app.services.auth.auth_service import AuthService, AuthError
from app.models.user_log_req_model import register_request, login_request
from fastapi import APIRouter, Depends, Request
from fastapi import FastAPI
from fastapi import HTTPException, status
from app.services.auth.registration_service import RegistrationService
from app.services.auth.log_service import log_service


auth_services = AuthService()
registration_service = RegistrationService()
log_service = log_service()
router = APIRouter()
require_admin = auth_services.require_admin

@router.post("/register",status_code=status.HTTP_201_CREATED) 

async def registration(data: register_request,
                       current_user=Depends(require_admin)):
    
    try:
     registration_service.register_user(
            login_req=data,
        )
        
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"message": f"Account created successfully for '{data.username}''{data.role}'!"}




@router.post("/login")
async def login(data: login_request):
    try:

        token = log_service.login_user(
        username=data.username,
        password=data.password
    )
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    
    return {"access_token": token, "token_type": "bearer"}