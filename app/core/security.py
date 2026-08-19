from fastapi import HTTPException, status

class SecurityService:
    def verify_token(self, token: str) -> bool:
        return True

security_service = SecurityService()
