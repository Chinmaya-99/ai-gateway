import hashlib
import uuid
from datetime import datetime

from ai_gateway.app.services.cache.exact_cache import ExactCache
from ai_gateway.app.services.embeddings.embedding_service import EmbeddingModel
from ai_gateway.app.services.cache.semantic_cache import SemanticCache
from ai_gateway.app.services.llm.router import ModelsInit
from ai_gateway.app.db.response_store import ResponseStore
from ai_gateway.app.models.response_models import LLMResponse
from ai_gateway.app.db.chroma_client import VectorStore


SIMILARITY_THRESHOLD = 0.85


class CacheManager:

    def __init__(self):
        # All async services are None until initialize() is called
        self.embedding_model: EmbeddingModel | None = None
        self.semantic_cache: SemanticCache | None = None
        self.exact_cache: ExactCache | None = None
        self.response_store: ResponseStore | None = None
        self.llm: ModelsInit | None = None
        self.vector_store: VectorStore | None = None

    @classmethod
    async def create(cls) -> "CacheManager":
        instance = cls()
        await instance._initialize()
        return instance

    async def _initialize(self):
        # Sync inits (no IO)
        self.embedding_model = EmbeddingModel()
        self.exact_cache = ExactCache()
        self.llm = ModelsInit()

        # Async inits (IO — DB connections, chroma client)
        self.semantic_cache = await SemanticCache.create()
        self.response_store = await ResponseStore.create()
        self.vector_store = await VectorStore.create()

    async def handle(self, query: str) -> dict:
        # ── L1: Exact cache (SHA-256) ──────────────────────────────────
        exact_hit = await self._check_exact_cache(query)
        if exact_hit:
            return {
                "answer": exact_hit,
                "cache_hit": True,
                "cache_tier": "L1_exact",
                "provider": "cache",
                "tokens": None,
            }

        # ── L2: Semantic cache (vector similarity) ─────────────────────
        cache_id = str(uuid.uuid4())  # unique ID linking query embedding ↔ response

        embedding_data = await self.embedding_model.embed_text(query, cache_id=cache_id)
        query_embedding = embedding_data.embedding

        semantic_hit = await self.semantic_cache.search_similar(query_embedding)

        if semantic_hit and semantic_hit["similarity"] >= SIMILARITY_THRESHOLD:
            result = await self.response_store.get_response(semantic_hit["cache_id"])
            print("Semantic Cache Hit:", semantic_hit)
            return {
                "answer": result["answer"],
                "cache_hit": True,
                "cache_tier": "L2_semantic",
                "provider": "cache",
                "prompt": result["prompt_tokens"],
                "completion": result["completion_tokens"],
                "total": result["total_tokens"],
            }

        # ── L3: LLM processing ─────────────────────────────────────────
        raw_response = await self.llm.get_response_llm(context="", query=query)

        response = LLMResponse(
            cache_id=cache_id,
            provider=raw_response.response_metadata["model_provider"],
            model=raw_response.response_metadata["model_name"],
            answer=raw_response.content,
            prompt_tokens=raw_response.response_metadata["token_usage"]["prompt_tokens"],
            completion_tokens=raw_response.response_metadata["token_usage"]["completion_tokens"],
            total_tokens=raw_response.response_metadata["token_usage"]["total_tokens"],
            created_at=datetime.utcnow(),
        )

        await self.vector_store.add_documents(embedding_data)
        await self.response_store.add_response(response)

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

    async def _check_exact_cache(self, query: str) -> str | None:
        """L1: SHA-256 hash lookup. Returns None until Redis is wired up."""
        key = hashlib.sha256(query.strip().lower().encode()).hexdigest()
        return await self.exact_cache.lookup(key)

    async def close(self):
        """Clean shutdown — call from FastAPI lifespan."""
        if self.response_store:
            await self.response_store.close()
