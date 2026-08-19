import os
from jose import jwt, JWTError
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from ai_gateway.app.models.token_model import TokenData


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 1

class AuthError(Exception):
    def __init__(self, error, status_code=status.HTTP_401_UNAUTHORIZED):
        self.error = error
        self.status_code = status_code
        


def hash_password(password: str) -> str:
        """Hashes a password with bcrypt (includes salt automatically)."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

stored_username1 = "om"
stored_hashed_password = "$2b$12$pznNrY7uD2GAPs7yuw/0z.k5gLLcZYlYHiJmLDFb62wb5fvcOmiY6"
stored_role="admin"
username1="om"
password="omom@123"
role="user"

user_db ={stored_username1:{"password":stored_hashed_password,"role":stored_role}}


def verify_password(password: str, hashed: str) -> bool:
        """Constant-time comparison to prevent timing attacks."""
        return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(username: str,role:str) -> str:
        """Returns a signed JWT valid for TOKEN_EXPIRE_HOURS hours."""
        expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
        payload = {"sub": username, "exp": expire, "role": role}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> TokenData:
        """Decodes a JWT and returns the username and role, or raises AuthError."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            role: str = payload.get("role")
            if username is None or role is None:
                raise AuthError("Token payload missing subject.")
            return TokenData(username=username, role=role)
        except JWTError as e:
            raise AuthError(f"Invalid or expired token: {e}")
        




print("log in")
# verification_result=verify_password(password, stored_hashed_password)

# if verification_result==True:
#     print("Password verification successful!,log in successful.")
# else:
#     print("Password verification failed.")


if username1 in user_db:
    print(f"\nWelcome back,'{user_db[username1]['role']}' {username1}!")
    hashed_pwd = user_db[username1].get('password')
    verification_result =verify_password(password, hashed_pwd)
    if verification_result:
        print("Password verification successful!,log in successful.")
    else:
        print("Password verification failed.")
        raise ValueError("Invalid password.")    
else:
    print("Invalid username.")
    raise ValueError("Invalid username.")


jwt_token = create_token(username1,role)
print(f"Generated JWT: {jwt_token}")