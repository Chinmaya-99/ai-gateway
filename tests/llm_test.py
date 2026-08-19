import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)
from uuid import uuid4
from datetime import datetime
from langchain_openrouter import ChatOpenRouter
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from app.models.response_models import LLMResponse
load_dotenv()
def llm(
    context: str,
    query: str,
)-> LLMResponse:
    load_nvidia = ChatOpenRouter(
        model="nvidia/nemotron-3.5-lightning:free", temperature=0.0
    )

    prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """you are an answering model. you must give proper response to the user based on the context
                        query given below.""",
                    ),
                    (
                        "human",
                        "Context: {context}\n\nQuery: {query}"
                    ),
                ])

    chain= prompt | load_nvidia
    response = chain.invoke({"context": context, "query": query})
    return response

query = "What is the capital of France?"

first_raw_response = llm(context="Geography", query=query)

#=================normalization of response===================


def normalize_llm_response(response) -> LLMResponse:

    """
    Convert a LangChain AIMessage/provider response
    into the Gateway's unified response format.
    """
    content = getattr(response, "content", "") or ""
    cache_id=str(uuid4())
    usage = getattr(response, "usage_metadata", {}) or {}

    prompt_tokens = usage.get("input_tokens", 0)
    completion_tokens = usage.get("output_tokens", 0)
    total_tokens = usage.get("total_tokens", 0)

    metadata = getattr(response, "response_metadata", {}) or {}

    provider=metadata.get("model_provider", "unknown"),
    model = metadata.get("model_name", "unknown")
    time=datetime.utcnow().isoformat()

    return LLMResponse(
        provider=str(provider),
        model=model,
        answer=content,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        cache_id=cache_id,
        created_at=time,
    )

response = normalize_llm_response(first_raw_response) 


print("LLM Response:", response)

print(response)
print("==============content=================")
print(response.answer)

print("==============metadata=================")
print(response.provider)
print(response.model)
print(response.prompt_tokens)
print(response.completion_tokens)
print(response.total_tokens)