import uuid
from datetime import datetime

from app.services.cache.exact_cache import ExactCache
from app.services.embeddings.embedding_service import EmbeddingModel
from app.services.cache.semantic_cache import SemanticCache
from app.services.llm.router import models_init as ModelsInit
from app.db.response_store import ResponseStore
from app.db.chroma_client import VectorStore
from app.services.embeddings.shared_embadding import SharedEmbeddingService,chromaDB_Service
from app.models.response_models import LLMResponse

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
        self.shared_embedding:SharedEmbeddingService | None=None
        self.chromaDB_Service:chromaDB_Service | None=None

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
        self.shared_embedding =SharedEmbeddingService()
        self.chromaDB_Service =chromaDB_Service()
        

        # Async inits (IO — DB connections, chroma client)
        self.semantic_cache = await SemanticCache.create()
        self.response_store = await ResponseStore.create()
        self.vector_store = await VectorStore.create()

    

    async def handle(self, query: str) -> dict:
        # ── L1: Exact cache (SHA-256) ──────────────────────────────────
        exact_hit = await self._check_exact_cache(query)
        if exact_hit:
            result = await self.response_store.get_response(cache_id=exact_hit)
            if result:
             return {
                 "answer": result["answer"],
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
            hit_id = semantic_hit["cache_id"]
            print("Semantic hit:", semantic_hit)
            print("Cache ID:", hit_id)

            result = await self.response_store.get_response(cache_id=hit_id)

            print("Response Store Result:", result)
            print("Semantic Cache Hit:", semantic_hit)
            if result is None:
             print("No response found, falling through to L3.")
            else:

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
        shared_embedding=await self.shared_embedding.share_embed(embedding_data)
        raw_response = await self.llm.get_response_llm(context="", query=query,packet=shared_embedding)
        normalized_response = await self.llm.normalize_llm_response(raw_response)    
        print("LLM Response:", normalized_response)

        response=LLMResponse(
            answer=normalized_response.answer,
            provider=normalized_response.provider,
            prompt_tokens=normalized_response.prompt_tokens,
            completion_tokens=normalized_response.completion_tokens,
            total_tokens=normalized_response.total_tokens,
            created_at=datetime.utcnow(),
            model=normalized_response.model,
            cache_id=cache_id

        )


        chromadata = await self.chromaDB_Service.convert(query_embedding, cache_id) 


        await self.vector_store.add_documents(chromadata)
        await self.response_store.add_response(response)
        await self.exact_cache.store(query,cache_id=cache_id)
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

        return await self.exact_cache.lookup(query)

    async def close(self):
        """Clean shutdown — call from FastAPI lifespan."""
        if self.response_store:
            await self.response_store.close()
