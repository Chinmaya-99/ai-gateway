from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class EmbeddingModelData(BaseModel):

    cache_id: UUID
    text: str = Field(
        ...,
        min_length=1
    )

    embedding: list[float]


class LLMResponse(BaseModel):

    cache_id: UUID

    provider: str

    model: str

    answer: str

    prompt_tokens: int

    completion_tokens: int

    total_tokens: int

    created_at: datetime
