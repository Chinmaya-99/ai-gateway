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
from ai_gateway.app.models.response_models import LLMResponse

load_dotenv()


class models_init:
    def __init__(self):
        self.gemini = ChatGoogleGenerativeAI(
            model="gemini-3.1-flash-lite-preview", temperature=0.0
        )
        self.lamma = ChatGroq(
            model="llama-3.1-8b-instant", temperature=0.0
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
        self.final_chain = self.prompt | self.lamma.with_fallbacks([self.gemini])
    

    async def get_response_llm(self, context: str, query: str):
        """Async invoke — uses LangChain's ainvoke so the event loop stays free."""
        return await self.final_chain.ainvoke(
            {"context": context, "query": query}
        )