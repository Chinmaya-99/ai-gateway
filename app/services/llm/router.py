import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_openrouter import ChatOpenRouter
from langchain_groq import ChatGroq
from app.models.response_models import normalizedResponse
from llm.complexcity.complexcity_features import ComplexityFeatures
from app.models.EmbeddingPacket import EmbeddingPacket


load_dotenv()


class models_init:
    def __init__(self): 
        self.complexity_features= ComplexityFeatures()
        self.gemini = ChatGoogleGenerativeAI(
            model="gemini-3.1-flash-lite-preview", temperature=0.0
        )
        self.minimax = ChatGroq(
            model="minimaxai/minimax-m2.7", temperature=0.0

            )
        self.nvidia = ChatOpenRouter(
            model="nvidia/nemotron-3.5-lightning:free", temperature=0.0
        )
        self.prompt = ChatPromptTemplate.from_messages(
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
                ]
            )
        self.simple_llm = self.prompt | self.nvidia
        self.complex_llm=self.prompt| self.gemini
    

    async def get_response_llm(self, context: str, query: str, packet: EmbeddingPacket) :
        """Routes to simple or complex chain based on complexity score."""

        complexity = await self.complexity_features.score(packet)

        if complexity.tier == "High":
            chain = self.complex_llm
        else:
            # Low and Medium both use simple chain
            chain = self.simple_llm
        return await chain.ainvoke(
            {"context": context, "query": query})


    async def normalize_llm_response(self, response) -> normalizedResponse:
            """
            Convert a LangChain AIMessage/provider response
            into the Gateway's unified response format.
            """
            content = getattr(response, "content", "") or ""
            usage = getattr(response, "usage_metadata", {}) or {}
    
            prompt_tokens = usage.get("input_tokens", 0)
            completion_tokens = usage.get("output_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
    
            metadata = getattr(response, "response_metadata", {}) or {}
    
            provider=metadata.get("model_provider", "unknown"),
            model = metadata.get("model_name", "unknown")
    
            return normalizedResponse(
                provider=str(provider),
                model=model,
                answer=content,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            )


    