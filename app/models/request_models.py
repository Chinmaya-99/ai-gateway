from pydantic import BaseModel, Field, PrivateAttr
from typing import Optional
from uuid import UUID

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    context: str = Field(..., min_length=0)
    _cache_id: UUID | None = PrivateAttr(default=None)

