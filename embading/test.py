import sys
from pathlib import Path
sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)
from embading import EmbeddingModel
from vector_store import VectorStore
from grp_llm import models  
from pydantic_datatypes import LLMResponse
from uuid import  uuid4
from datetime import datetime
from uuid import uuid4

cache_id = uuid4()


VectorStore=VectorStore()
text="what is langchain?"
context=""
embading_result=EmbeddingModel().embed_text(text, cache_id)
print("\n========== llm response ==========\n")

engine = models.models_init()
raw_response = engine.get_edits(
        query= text,
        context=context)

formatting_response=LLMResponse(
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


vector_store_result=VectorStore.add_documents(data=embading_result)


print(formatting_response.answer)
print(formatting_response.cache_id)
print(embading_result.cache_id)
print(vector_store_result)