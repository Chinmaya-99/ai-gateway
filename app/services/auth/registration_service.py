from app.services.auth.auth_service import AuthService
from app.models.user_log_req_model import register_request
import os
from fastapi import HTTPException, status   



class RegistrationService(AuthService):
    def __init__(self):
        self.data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_credentials.txt")   
        self.user_db = self.load_database()
        self.auth_service = AuthService()  # Initialize AuthService for password hashing and saving

        
    def register_user(self,login_req: register_request):
        """Handles the user registration workflow."""
        print("\n--- Account Registration ---")
        user_db = self.user_db
        username = login_req.username.strip()
        password = login_req.password
        confirm_password = login_req.confirm_password
        role = login_req.role if hasattr(login_req, 'role') else "user"

        if not username:
            print("Error: Username cannot be blank.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username cannot be blank."
            )

        if username in user_db:
            print(f"Error: Username '{username}' already exists.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists. Please pick another."
            )

        if len(password) < 6:
            print("Error: Password must be at least 6 characters long.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long."
            )
        if password != confirm_password:
            print("Error: Passwords do not match.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match."
            )

        hashed_pwd = self.hash_password(password)
        self.auth_service.save_user(username, hashed_pwd,role)
        self.user_db[username] = hashed_pwd
        print(f"Success: Account created successfully for '{username}''{role}'!")
