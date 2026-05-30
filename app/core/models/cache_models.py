from pydantic import BaseModel, Field

class EmbeddingModelData(BaseModel):
    cache_id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    embedding: list[float]
