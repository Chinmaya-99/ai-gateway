from pydantic import BaseModel
from datetime import datetime

class UserLogRequest(BaseModel):
    username: str
    password: str
    timestamp: datetime