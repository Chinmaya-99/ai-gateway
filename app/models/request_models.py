from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    context: str = Field(..., min_length=1)
    cache_id: Optional[UUID] = None

class EmbeddingRequest(BaseModel):
    text: str = Field(..., min_length=1)
    cache_id: UUID
