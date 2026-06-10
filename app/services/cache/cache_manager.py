import hashlib
import uuid
from datetime import datetime
from ai_gateway.app.services.cache.exact_cache import ExactCache
from app.services.embeddings.embedding_service import EmbeddingModel
from app.services.cache.semantic_cache import SemanticCache
#from app.services.cache.exact_cache import ExactCache
from app.services.llm.router import models_init
from app.db.response_store import ResponseStore
from app.models.response_models import LLMResponse




SIMILARITY_THRESHOLD = 0.85

class CacheManager:
 
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.semantic_cache = SemanticCache()
        self.exact_cache = ExactCache()
        self.response_store = ResponseStore()
        self.llm = models_init()

    def handle(self,query:str):
       # ── L1: Exact cache (SHA-256) ──────────────────────────────────
        exact_hit = self._check_exact_cache(query)
        if exact_hit:
            return {
                "answer": exact_hit,
                "cache_hit": True,
                "cache_tier": "L1_exact",
                "provider": "cache",
                "tokens": None,
            }
         # ── L2: Semantic cache (vector similarity) ──────────────────

        cache_id = str(uuid.uuid4())
        embedding_data = self.embedding_model.embed_text(query, cache_id=cache_id)
        query_embedding = embedding_data.embedding

    
        semanntic_hit = self.semantic_cache.search_similar(query_embedding)
        if semanntic_hit and semanntic_hit.similarity >= SIMILARITY_THRESHOLD:
            return {
                "answer": semanntic_hit.answer,
                "cache_hit": True,
                "cache_tier": "L2_semantic",
                "provider": "cache",
                "tokens": None,
            }
         # ── L3: LLM processing ─────────────────────────────────────────
        raw_response = self.llm.get_response(context="", query=query)

        response = LLMResponse(
        cache_id=cache_id,

        provider=raw_response.response_metadata[
            "model_provider"
        ],

        model=raw_response.response_metadata[
            "model_name"
        ],

        answer=raw_response.content,

        prompt_tokens=raw_response.response_metadata[
            "token_usage"
        ]["prompt_tokens"],

        completion_tokens=raw_response.response_metadata[
            "token_usage"
        ]["completion_tokens"],

        total_tokens=raw_response.response_metadata[
            "token_usage"
        ]["total_tokens"],

        created_at=datetime.utcnow()
    )
        self.add_document(embedding_data)
        self.add_response(response)
        return {
            "answer": response.answer,
            "cache_hit": False,
            "cache_tier": "L3_llm",
            "provider": response.provider,
            "tokens": {
                "prompt": response.prompt_tokens,
                "completion": response.completion_tokens,
                "total": response.total_tokens,
            },
        }
    def _check_exact_cache(self, query: str):
        """
        L1: SHA-256 hash lookup.
        ExactCache.lookup() returns None until Redis is wired up.
        """
        key = hashlib.sha256(query.strip().lower().encode()).hexdigest()
        return self.exact_cache.lookup(key)
 