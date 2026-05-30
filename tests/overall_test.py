import sys
from pathlib import Path

sys.path.append(
        str(Path(__file__).resolve().parent.parent)
)

from app.services.embeddings.embedding_service import EmbeddingModel
from app.db.chroma_client import VectorStore
from app.services.cache.semantic_cache import SemanticCache
from app.core.models.cache_models import EmbeddingModelData
from app.core.models.response_models import LLMResponse
from app.core.models.request_models import QueryRequest, EmbeddingRequest
from app.services.llm.router import models_init
from app.db.response_store import ResponseStore
from datetime import datetime
import uuid

VectorStore=VectorStore()
text="what is api?"
cache_id=str(uuid.uuid4())
embaddings=EmbeddingModel().embed_text(text, cache_id=cache_id)

print("\n\n======================embeddings========================\n\n")
print(embaddings)

print("\n\n======================store embedding in vector store========================\n\n")
vectore_result=VectorStore.add_documents(embaddings)

print(vectore_result)

print(
    "VectorStore Count:",
    VectorStore.collection.count()
)
llm=models_init()
raw_response=llm.get_response(context="", query=text)
print("\n\n======================response from llm========================\n\n")


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


print(response)


print("\n\n======================store response in response store========================\n\n")
response_store=ResponseStore()
responsedb=response_store.add_response(response)
print(responsedb)

print("\n\n======================search similar embedding in semantic cache========================\n\n")
cache = SemanticCache()
query_embedding = embaddings.embedding

result = cache.search_similar(
    query_embedding
)

print(
    "SemanticCache Count:",
    cache.collection.count()
)
print(result)
