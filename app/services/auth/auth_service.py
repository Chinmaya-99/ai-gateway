import os
import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from app.models.token_model import TokenData


file_path = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(file_path, "user_credentials.txt")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 1

class AuthError(Exception):
    def __init__(self, error, status_code=status.HTTP_401_UNAUTHORIZED):
        self.error = error
        self.status_code = status_code

class AuthService:
    def __init__(self):
        self.data_file =DATA_FILE
        self.user_db = self.load_database()
        
    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes a password with bcrypt (includes salt automatically)."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password: str, stored_hashed: str) -> bool:
        """Constant-time comparison to prevent timing attacks."""
        return bcrypt.checkpw(password.encode(), stored_hashed.encode())


    @staticmethod
    def create_token(username: str,role:str) -> str:
        """Returns a signed JWT valid for TOKEN_EXPIRE_HOURS hours."""
        expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
        payload = {"sub": username, "exp": expire, "role": role}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
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
        

    def load_database(self) -> dict:
        """Reads stored credentials and parses them into a dictionary."""
        user_db = {}
        if not os.path.exists(self.data_file):
            return user_db

        with open(self.data_file, "r") as file:
            for line in file:
                line = line.strip()
                if line and ":" in line:
                    username, hashed_pwd, role = line.split(":", 2)
                    user_db[username] = {"hashed_pwd": hashed_pwd, "role": role}
        return user_db


    def save_user(self, username: str, hashed_pwd: str,role: str):
        """Appends a new user record to the credentials file."""
        with open(self.data_file, "a") as file:
            file.write(f"{username}:{hashed_pwd}:{role}\n")

    def require_admin(self, token: str):
        """Checks if the provided token belongs to an admin user."""
        try:
            token_data = self.decode_token(token)
            username, role = token_data.username, token_data.role
            if role != "admin":
                raise AuthError("Admin privileges required.", status.HTTP_403_FORBIDDEN)
            return username
        except AuthError as e:
            raise HTTPException(status_code=e.status_code, detail=str(e))