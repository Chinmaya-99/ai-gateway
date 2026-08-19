import re
import numpy as np
from app.models.EmbeddingPacket import EmbeddingPacket
from app.models.complexcity_model import ComplexityResult



# ── Signal Definitions ────────────────────────────────────────────────────────
 
SIMPLE_VERBS = {
    "what", "who", "when", "where", "list", "define",
    "name", "show", "tell", "give", "is", "are", "was"
}
 
COMPLEX_VERBS = {
    "explain", "compare", "analyze", "design", "implement",
    "optimize", "evaluate", "justify", "debug", "architect",
    "differentiate", "summarize", "critique", "prove", "derive"
}
 
TECHNICAL_DOMAINS = {
    "programming": ["function", "class", "api", "database", "algorithm", "code", "bug", "error"],
    "ml_ai":       ["model", "training", "embedding", "transformer", "gradient", "inference", "vector"],
    "networking":  ["tcp", "http", "dns", "latency", "bandwidth", "protocol", "socket"],
    "math":        ["equation", "proof", "integral", "derivative", "matrix", "theorem"],
    "devops":      ["docker", "kubernetes", "ci/cd", "deployment", "pipeline", "container"],
}
 
CODE_PATTERNS = [
    r"```",                        # code blocks
    r"\bdef\b|\bclass\b",          # python
    r"\bSELECT\b|\bFROM\b",        # SQL
    r"\bconst\b|\blet\b|\bvar\b",  # javascript
    r"\{.*\}",                     # JSON/dict-like
    r"import\s+\w+",               # imports
    r"<\w+>.*</\w+>",              # XML/HTML tags
]
 
# Phase 1 weights — linguistic-heavy until semantic history builds up
WEIGHTS = {
    "token":       0.15,
    "instruction": 0.25,
    "domain":      0.20,
    "code":        0.15,
    "question":    0.10,
    "semantic":    0.15,   # increase this in Phase 2
}
#_________________complexity_features_____________________

class ComplexityFeatures:
    async def score(self,packet:EmbeddingPacket):
            query = packet.query
            tokens = query.lower().split()
    
            token_score       = await self._token_score(tokens)
            instruction_score = await self._instruction_score(tokens)
            domain_score      = await self._domain_score(tokens)
            code_score        = await self._code_score(query)
            question_score    = await self._question_score(query)
            semantic_score    = await self._semantic_score(packet)
            final_score =(
                 
                WEIGHTS["token"] * token_score +
                WEIGHTS["instruction"] * instruction_score +
                WEIGHTS["domain"] * domain_score +
                WEIGHTS["code"] * code_score +
                WEIGHTS["question"] * question_score +
                WEIGHTS["semantic"] * semantic_score
            )
            return ComplexityResult( 
                            score=final_score,
                            tier=await self._tier(final_score),
                            token_score=token_score,
                            instruction_score=instruction_score,
                            domain_score=domain_score,
                            code_score=code_score,
                            question_score=question_score,
                            semantic_score=semantic_score
                        )


    async def _token_score(self, tokens):
            token_len=len(tokens)
            if token_len < 10:
                return 1.0
            if token_len < 20:
                return 2.0
            if token_len < 30:
                return 3.0
            if token_len < 40:
                return 4.0
            if token_len < 50:
                return 5.0
            if token_len < 60:
                return 6.0
            if token_len < 70:
                return 7.0
            if token_len < 80:
                return 8.0
            if token_len < 90:
                return 9.0
            return 10.0

    async def _instruction_score(self, tokens)->float:
        token_set = set(tokens)
        complex_hits = len(token_set & COMPLEX_VERBS)
        simple_hits  = len(token_set & SIMPLE_VERBS)
 
        if complex_hits >= 3: return 10.0
        if complex_hits == 2: return 8.0
        if complex_hits == 1: return 6.0
        if simple_hits >= 1:  return 2.0
        return 4.0

    async def _domain_score(self, tokens)->float:
        token_set = set(tokens)
        technical_keywords = {keyword for keywords in TECHNICAL_DOMAINS.values() for keyword in keywords}
        technical_hits = len(token_set & technical_keywords)

 
        if technical_hits >= 3: return 10.0
        if technical_hits == 2: return 8.0
        if technical_hits == 1: return 6.0
        if technical_hits >= 1:  return 2.0
        return 4.0
    
    async def _code_score(self, query)->float:
        for pattern in CODE_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return 10.0
        return 0.0
         
    async def _question_score(self, query)->float:
        query_count = query.count("?")
        if query_count == 0: return 2.0
        if query_count == 1: return 4.0
        if query_count == 2: return 7.0
        return 10.0
    
    async def _semantic_score(self, packet: EmbeddingPacket) -> float:
        magnitude = packet.magnitude
        normalized = np.clip((magnitude - 0.02) / (0.08 - 0.02), 0.0, 1.0)
        return round(float(normalized * 10), 2)


    async def _tier(self, score: float) -> str:
        if score < 3.0:
            return "Low"
        elif score < 6.0:
            return "Medium"
        else:
            return "High"