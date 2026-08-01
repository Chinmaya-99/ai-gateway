import numpy as np
from dataclasses import dataclass, field
from app.services.embeddings.embedding_service import EmbeddingModel
from app.models.EmbeddingPacket import EmbeddingPacket


class SharedEmbeddingService:
    async def share_embed(self, embeddings) -> EmbeddingPacket:
        """Convert an EmbeddingModelData-like object into an EmbeddingPacket.

        Expects `embeddings` to have attributes `text` and `embedding`.
        """
        return EmbeddingPacket(
            query=embeddings.text,
            vector=embeddings.embedding,
        )