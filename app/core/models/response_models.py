from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class LLMResponse(BaseModel):
    cache_id: UUID
    provider: str
    model: str
    answer: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    created_at: datetime
