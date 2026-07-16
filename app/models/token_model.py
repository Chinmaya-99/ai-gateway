from pydantic import BaseModel
from typing import Literal


class TokenData(BaseModel):
    username: str
    role: Literal["admin", "user"]