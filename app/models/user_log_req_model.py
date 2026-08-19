from pydantic import BaseModel
from datetime import datetime
from typing import Literal

class register_request(BaseModel):
    username: str
    password: str
    confirm_password: str
    role:  Literal["admin","user"]= "user"  

class login_request(BaseModel):
    username: str
    password: str