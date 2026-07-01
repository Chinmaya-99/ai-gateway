from pydantic import BaseModel
from datetime import datetime

class register_request(BaseModel):
    username: str
    password: str

class login_request(BaseModel):
    username: str
    password: str