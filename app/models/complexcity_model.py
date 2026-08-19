from pydantic import BaseModel

class ComplexityResult(BaseModel):
    score: float
    tier: str
    token_score: float
    instruction_score: float
    domain_score: float
    code_score: float
    question_score: float
    semantic_score: float