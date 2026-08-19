from app.models.EmbeddingPacket import EmbeddingPacket
from app.models.cache_models import ChromaModel

class SharedEmbeddingService:
    async def share_embed(self, embeddings) -> EmbeddingPacket:
        """Convert an EmbeddingModelData-like object into an EmbeddingPacket.

        Expects `embeddings` to have attributes `text` and `embedding`.
        """
        return EmbeddingPacket(
            query=embeddings.text,
            vector=embeddings.embedding,
        )

class chromaDB_Service:
    async def convert(self,Embadding=list,cache_id=str)-> ChromaModel:
        """convert the data into ChromaModel like object
        
        Expect embaddings and cache_id as input"""

        return ChromaModel(
            cache_id=cache_id,
            embedding=Embadding
        )