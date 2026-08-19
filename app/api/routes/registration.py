from app.services.auth.auth_service import AuthService, AuthError
from app.models.user_log_req_model import register_request
from fastapi import APIRouter, Depends
from fastapi import FastAPI
from fastapi import HTTPException, status
from app.services.auth.registration_service import RegistrationService
from app.services.auth.log_service import log_service

auth_services = AuthService()
registration_service = RegistrationService()
log_service = log_service()
router = APIRouter()


require_admin = auth_services.require_admin

@router.post("/",status_code=status.HTTP_201_CREATED) 

async def registration(data: register_request):
    
    try:
     registration_service.register_user(
            login_req=data,
        )
        
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"message": f"Account created successfully for '{data.username}''{data.role}'!"}

