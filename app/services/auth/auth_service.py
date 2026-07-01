import hashlib
import os
import getpass


file_path = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(file_path, "user_credentials.txt")


class AuthService:
    def __init__(self):
        self.data_file =DATA_FILE
        self.user_db = self.load_database()

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()


    def load_database(self) -> dict:
        """Reads stored credentials and parses them into a dictionary."""
        user_db = {}
        if not os.path.exists(self.data_file):
            return user_db

        with open(self.data_file, "r") as file:
            for line in file:
                line = line.strip()
                if line and ":" in line:
                    username, hashed_pwd = line.split(":", 1)
                    user_db[username] = hashed_pwd
        return user_db


    def save_user(self, username: str, hashed_pwd: str):
        """Appends a new user record to the credentials file."""
        with open(self.data_file, "a") as file:
            file.write(f"{username}:{hashed_pwd}\n")


    def register_user(self,username: str, password: str):
        """Handles the user registration workflow."""
        print("\n--- Account Registration ---")
        user_db = self.user_db

        if not username:
            print("Error: Username cannot be blank.")
            return

        if username in user_db:
            print("Error: Username already exists. Please pick another.")
            return


        if password != password:
            print("Error: Passwords do not match.")
            return

        if len(password) < 6:
            print("Error: Password must be at least 6 characters long.")
            return

        hashed_pwd = self.hash_password(password)
        self.save_user(username, hashed_pwd)
        self.user_db[username] = hashed_pwd
        print(f"Success: Account created successfully for '{username}'!")


    def login_user(self, username: str, password: str):
        """Handles the user authentication workflow."""
        print("\n--- User Login ---")
        user_db = self.user_db

        hashed_pwd = self.hash_password(password)

        # Secure validation step
        if username in user_db and user_db[username] == hashed_pwd:
            print(f"\nWelcome back, {username}! Login successful.")
            return True
        else:
            print("\nError: Invalid username or password.")
            return False
