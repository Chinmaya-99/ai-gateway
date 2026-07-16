from app.services.auth.auth_service import AuthService

authservice = AuthService()
class log_service: 
    def __init__(self):
        self.authservice = authservice
        self.user_db = self.authservice.user_db

    def login_user(self, username: str, password: str):
        """Handles the user authentication workflow."""
        print("\n--- User Login ---")
        user_db = self.user_db


        if username in user_db:
            print(f"\nWelcome back,'{user_db[username]['role']}' {username}!")
            hashed_pwd = user_db[username].get('hashed_pwd')
            verification_result = self.authservice.verify_password(password, hashed_pwd)
            if verification_result:
                print("Password verification successful!,log in successful.")
            else:
                print("Password verification failed.")
                raise ValueError("Invalid password.")    
        else:
            raise ValueError("Invalid username.")
        

        return self.authservice.create_token(username,role=user_db[username].get('role'))