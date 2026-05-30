from pydantic import BaseModel
from datetime import datetime

class LLMResponse(BaseModel):
    cache_id: str
    provider: str
    model: str
    answer: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    created_at: datetime
