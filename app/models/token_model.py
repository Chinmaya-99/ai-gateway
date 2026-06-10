from pydantic import BaseModel
from datetime import datetime

class Tokenmodel(BaseModel):
    token: str
    accesse_token: str