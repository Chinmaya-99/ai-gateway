from pydantic import BaseModel, Field

class EmbeddingModelData(BaseModel):
    cache_id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    embedding: list[float]

class ChromaModel(BaseModel):
    cache_id: str = Field(..., min_length=1)
    embedding: list[float]

    
class redisData(BaseModel):
    cache_id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)