from pydantic import BaseModel, Field
from uuid import UUID

class EmbeddingModelData(BaseModel):
    cache_id: UUID
    text: str = Field(..., min_length=1)
    embedding: list[float]
