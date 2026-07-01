import asyncio
from functools import partial

from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

from app.models.cache_models import EmbeddingModelData

load_dotenv()


class EmbeddingModel:

    def __init__(self):
        # Model loading is CPU-bound and done once at startup — stays sync
        self.model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        self._loop = asyncio.get_event_loop()

    async def embed_text(self, text: str, cache_id: str) -> EmbeddingModelData:
        # embed_query is CPU-bound (torch inference) — offload to thread pool
        # so it doesn't block the event loop
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None, partial(self.model.embed_query, text)
        )

        return EmbeddingModelData(
            cache_id=cache_id,
            text=text,
            embedding=embedding,
        )
